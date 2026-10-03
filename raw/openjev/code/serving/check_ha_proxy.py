"""CPU checks for replica failover and request errors before live fault injection."""
import asyncio
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

import httpx

import ha_proxy as proxy


class ProxyChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        proxy.inflight = 0
        proxy.healthy.update({url: True for url in proxy.BACKENDS})
        proxy.cooldown.update({url: 0 for url in proxy.BACKENDS})
        self.body = {"text": "Premise: same state\nHypothesis: first"}
        self.order = proxy.ordered_backends(self.body)
        self.calls = []
        self.status = {}

        def upstream(request):
            url = str(request.url).removesuffix("/classify")
            self.calls.append(url)
            result = self.status.get(url, 200)
            if isinstance(result, Exception):
                raise result
            return httpx.Response(result, json={"embedding": [0, 1, 0]})

        proxy.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        self.api = httpx.AsyncClient(transport=httpx.ASGITransport(app=proxy.app), base_url="http://test")

    async def asyncTearDown(self):
        await self.api.aclose()
        await proxy.client.aclose()

    async def test_fallback_on_failure(self):
        self.status[self.order[0]] = 500
        response = await self.api.post("/classify", json=self.body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.calls, self.order)
        self.assertFalse(proxy.healthy[self.order[0]])

    async def test_connection_failure_falls_back(self):
        self.status[self.order[0]] = httpx.ConnectError("worker disappeared")
        response = await self.api.post("/classify", json=self.body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.calls, self.order)

    async def test_bad_input_is_not_retried(self):
        self.status[self.order[0]] = 400
        response = await self.api.post("/classify", json=self.body)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.calls, self.order[:1])

    async def test_overload_tries_other_worker(self):
        self.status[self.order[0]] = 429
        response = await self.api.post("/classify", json=self.body)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(proxy.healthy[self.order[0]])

    async def test_no_workers_returns_503(self):
        proxy.healthy.update({url: False for url in proxy.BACKENDS})
        response = await self.api.post("/classify", json=self.body)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.calls, [])

    async def test_inflight_hang_fails_over_after_health_loss(self):
        await proxy.client.aclose()

        async def upstream(request):
            url = str(request.url).removesuffix("/classify")
            if url == self.order[0]:
                proxy.healthy[url] = False
                await asyncio.sleep(10)
            return httpx.Response(200, json={"embedding": [0, 1, 0]})

        proxy.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        response = await asyncio.wait_for(self.api.post("/classify", json=self.body), timeout=3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-OpenJev-Backend"], self.order[1])

    async def test_bad_json_and_backpressure_release_counter(self):
        response = await self.api.post("/classify", content="{")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(proxy.inflight, 0)
        proxy.inflight = proxy.MAX_INFLIGHT
        response = await self.api.post("/classify", json=self.body)
        self.assertEqual(response.status_code, 429)

    def test_shared_premise_affinity(self):
        other = {"text": "Premise: same state\nHypothesis: second"}
        self.assertEqual(proxy.ordered_backends(other), self.order)

    async def test_warming_backend_not_routed_until_ready(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(proxy, "READY_DIR", directory):
            await proxy.check_backends()
            self.assertFalse(any(proxy.healthy.values()))
            self.assertEqual(self.calls, [])
            port = urlsplit(proxy.BACKENDS[0]).port
            (Path(directory) / f"{port}.ready").write_text("123\n")
            await proxy.check_backends()
            self.assertTrue(proxy.healthy[proxy.BACKENDS[0]])
            self.assertEqual(sum(proxy.healthy.values()), 1)


if __name__ == "__main__":
    unittest.main()
