"""CPU regression checks for image forwarding, probabilities and input errors."""
import base64
import io
import json
import unittest

import httpx
from PIL import Image

import decisions_server as server
from decisions_api import ApiError, assemble, build_plan
from image_inputs import image_input
from image_jevbench import OpenJevImageAdapter


def picture():
    b = io.BytesIO()
    Image.new("RGB", (32, 32), "red").save(b, format="PNG")
    return b.getvalue()


class Images(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.calls = []
        def upstream(req):
            body = json.loads(req.content)
            self.calls.append(body)
            return httpx.Response(200, json=[{"embedding": [0, 2, -1], "meta_info": {"prompt_tokens": 80}}
                                            for _ in body["text"]])
        server._client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        self.api = httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app), base_url="http://test")
        server.API_KEY = ""
        self.body = {"model": "test", "state": "Image: <<IMG>>", "image_data": base64.b64encode(picture()).decode(),
                     "questions": {"q": {"type": "choice", "instructions": "Which color?",
                                         "criteria": {"a": "red", "b": "blue"}}}}

    async def asyncTearDown(self):
        await self.api.aclose()
        await server._client.aclose()
        server._client = None

    async def test_pixels_forwarded_per_option(self):
        r = await self.api.post("/v1/systemone", json=self.body)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["answers"]["q"]["probabilities"], {"a": .5, "b": .5})
        self.assertEqual(len(self.calls), 1)
        for c in self.calls:
            self.assertEqual(c["image_data"], [self.body["image_data"]] * 2)
            self.assertEqual(c["text"][0].count("<|image_pad|>"), 1)
            self.assertNotIn("<<IMG>>", c["text"][0])

    async def test_text_request_still_batched(self):
        del self.body["image_data"]
        self.body["state"] = "A red box."
        r = await self.api.post("/v1/systemone", json=self.body)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(self.calls), 1)
        self.assertNotIn("image_data", self.calls[0])

    async def test_bad_image_does_not_reach_worker(self):
        for data in ("/etc/passwd", "https://example.com/image.png", "not-base64", [], ""):
            self.body["image_data"] = data
            r = await self.api.post("/v1/systemone", json=self.body)
            self.assertEqual(r.status_code, 400, r.text)
        self.assertEqual(self.calls, [])

    async def test_duplicate_marker_rejected(self):
        self.body["state"] = "<<IMG>> <<IMG>>"
        r = await self.api.post("/v1/systemone", json=self.body)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.calls, [])

    def test_data_uri_and_zero_entailment(self):
        self.assertEqual(image_input({"image_data": "data:image/png;base64," + self.body["image_data"]}), self.body["image_data"])
        p = assemble(build_plan(self.body), [0, 0])["q"]["probabilities"]
        self.assertEqual(p, {"a": .5, "b": .5})
        with self.assertRaises(ValueError):
            assemble(build_plan(self.body), [float("nan"), 1])

    def test_benchmark_does_not_send_gold_or_alt(self):
        a = OpenJevImageAdapter("http://test", "test")
        try:
            body = a.build_request({"question": "Q", "options": [{"label": "a", "text": "red"}],
                                    "correctLabel": "SECRET_GOLD", "alt": "SECRET_DESCRIPTION"}, picture())
            self.assertNotIn("SECRET", json.dumps(body))
        finally:
            a.close()


if __name__ == "__main__":
    unittest.main()
