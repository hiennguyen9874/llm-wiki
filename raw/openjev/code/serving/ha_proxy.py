"""Local SGLang gateway: prefix affinity, bounded concurrency and replica failover."""
import asyncio
from contextlib import asynccontextmanager
import hashlib
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from service_notify import notify

BACKENDS = os.environ.get("OPENJEV_BACKENDS", "http://127.0.0.1:31010,http://127.0.0.1:31012").split(",")
MAX_INFLIGHT = int(os.environ.get("OPENJEV_MAX_INFLIGHT", "64"))
MAX_BODY = 16 * 1024 * 1024
READY_DIR = os.environ.get("OPENJEV_READY_DIR")
healthy = {url: False for url in BACKENDS}
cooldown = {url: 0.0 for url in BACKENDS}
inflight = 0
client = None


def affinity(body):
    # Different hypotheses for the same long premise prefer the same replica.
    value = body.get("input_ids", body.get("text", ""))
    if isinstance(value, list) and value and isinstance(value[0], (list, str)):
        value = value[0]
    value = value[:128] if isinstance(value, list) else str(value).split("\nHypothesis:", 1)[0][:512]
    return json.dumps(value, ensure_ascii=False).encode()


def ordered_backends(body):
    key = affinity(body)
    return sorted(BACKENDS, key=lambda url: hashlib.sha256(key + url.encode()).digest(), reverse=True)


async def check_backends():
    async def check(url):
        if READY_DIR and not (Path(READY_DIR) / f"{urlsplit(url).port}.ready").is_file():
            healthy[url] = False
            return
        if cooldown[url] > time.monotonic():
            healthy[url] = False
            return
        try:
            # health_generate tests scheduler progress, unlike plain HTTP liveness.
            response = await client.get(url + "/health_generate", timeout=5)
            healthy[url] = response.status_code == 200
        except httpx.HTTPError:
            healthy[url] = False

    await asyncio.gather(*(check(url) for url in BACKENDS))


async def monitor():
    while True:
        await check_backends()
        notify("WATCHDOG=1\nSTATUS=" + str(sum(healthy.values())) + "/" + str(len(BACKENDS)) + " replicas healthy")
        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(_):
    global client
    async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=3),
                                limits=httpx.Limits(max_connections=128)) as client:
        # Socket activation queues new connections during this initial check.
        await check_backends()
        task = asyncio.create_task(monitor())
        notify("READY=1")
        try:
            yield
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/health")
@app.get("/health_generate")
async def health():
    count = sum(healthy.values())
    return JSONResponse(dict(status="ok" if count else "unavailable", ready_replicas=count,
                             replicas=healthy), status_code=200 if count else 503)


async def post_checked(url, raw):
    task = asyncio.create_task(client.post(url + "/classify", content=raw,
                                          headers={"Content-Type": "application/json"}))
    try:
        while True:
            done, _ = await asyncio.wait({task}, timeout=1)
            if done:
                return await task
            if not healthy[url]:
                raise httpx.ConnectError("Replica failed its concurrent health probe")
    finally:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


@app.post("/classify")
async def classify(request: Request):
    global inflight
    if inflight >= MAX_INFLIGHT:
        return JSONResponse({"error": "Too many in-flight requests"}, status_code=429)
    inflight += 1
    try:
        raw = bytearray()
        async for chunk in request.stream():
            raw.extend(chunk)
            if len(raw) > MAX_BODY:
                return JSONResponse({"error": "Request too large"}, status_code=413)
        try:
            body = json.loads(raw)
            if not isinstance(body, dict):
                raise ValueError("Expected an object")
        except (ValueError, UnicodeDecodeError):
            return JSONResponse({"error": "Invalid JSON object"}, status_code=400)
        for url in ordered_backends(body):
            if not healthy[url]:
                continue
            try:
                response = await post_checked(url, bytes(raw))
                if response.status_code >= 500 or response.status_code == 429:
                    if response.status_code >= 500:
                        healthy[url] = False
                        cooldown[url] = time.monotonic() + 10
                    continue
                return Response(response.content, status_code=response.status_code,
                                media_type="application/json", headers={"X-OpenJev-Backend": url})
            except httpx.HTTPError:
                healthy[url] = False
                cooldown[url] = time.monotonic() + 10
        return JSONResponse({"error": "No healthy replica completed the request"}, status_code=503)
    finally:
        inflight -= 1


# Preserve the existing typed Decisions API through the same resilient backend.
from decisions_server import app as decisions_app
app.mount("/", decisions_app)
