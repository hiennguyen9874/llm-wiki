"""HTTP gateway that speaks OpenRouter's Decisions API in front of an openjev checkpoint served by SGLang (serve_sglang.sh).

    POST /api/alpha/decisions     (also POST /api/v1/systemone: same request/response schema)
    GET  /health                  200 once SGLang answers, 503 before

Env: SGLANG_URL (http://127.0.0.1:30000), API_KEY (Bearer token; unset = no auth, local use only), SERVED_MODEL
(name echoed in the response), PRICE_PER_MTOK (USD per 1M input tokens for usage.cost, default 0), MAX_INFLIGHT (429 above), CLASSIFY_BS.

    uvicorn decisions_server:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import asyncio
import hmac
import json
import os
import random
import string
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from decisions_api import ApiError, assemble, build_plan, softmax_ent
from prompt_templates import STYLES, build_prompt_plan, finish_answers
from image_inputs import image_input, image_premise

SGLANG_URL = os.environ.get("SGLANG_URL", "http://127.0.0.1:30000").rstrip("/")
API_KEY = os.environ.get("API_KEY", "")
SERVED_MODEL = os.environ.get("SERVED_MODEL", "openjev/qwen3.5-4b-nli-v5")
PRICE_PER_MTOK = float(os.environ.get("PRICE_PER_MTOK", "0"))
MAX_INFLIGHT = int(os.environ.get("MAX_INFLIGHT", "64"))
CLASSIFY_BS = int(os.environ.get("CLASSIFY_BS", "32"))  # pairs per /classify call; the calls of one request run concurrently
PROMPT_STYLE = os.environ.get("OPENJEV_PROMPT_STYLE", "trained")
if PROMPT_STYLE not in STYLES:
    raise ValueError(f"Unknown OPENJEV_PROMPT_STYLE: {PROMPT_STYLE}")
TEMPLATE = "Premise: {premise}\nHypothesis: {hypothesis}"  # must match train.py / modeling_openjev.py

app = FastAPI(title="openjev decisions", docs_url=None, redoc_url=None, openapi_url=None)
_client: httpx.AsyncClient | None = None
_inflight = 0


def client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=httpx.Timeout(600.0), limits=httpx.Limits(max_connections=256))
    return _client


def err(code: int, message: str) -> JSONResponse:
    return JSONResponse(ApiError(code, message).body(), status_code=code)


async def classify(pairs: list, image=None) -> tuple:
    """-> (P(entailment) per pair, prompt tokens). One request per CLASSIFY_BS pairs, all in flight together."""
    texts = [TEMPLATE.format(premise=image_premise(p.strip()) if image else p.strip(), hypothesis=h.strip())
             for p, h in pairs]

    async def one(chunk):
        payload = {"text": chunk}
        if image:
            payload["image_data"] = [image] * len(chunk)
        r = await client().post(f"{SGLANG_URL}/classify", json=payload)
        r.raise_for_status()
        out = r.json()
        return out if isinstance(out, list) else [out]

    if image:
        # Keep repeated image bytes bounded and vision prefill memory predictable.
        image_bs = max(1, min(4, CLASSIFY_BS, (8 * 1024 * 1024) // len(image)))
        outs = [await one(texts[i:i + image_bs]) for i in range(0, len(texts), image_bs)]
    else:
        outs = await asyncio.gather(*[one(texts[i:i + CLASSIFY_BS]) for i in range(0, len(texts), CLASSIFY_BS)])
    flat = [o for chunk in outs for o in chunk]
    if len(flat) != len(texts):
        raise RuntimeError(f"/classify returned {len(flat)} results for {len(texts)} inputs")
    tokens = sum((o.get("meta_info") or {}).get("prompt_tokens") or 0 for o in flat)
    if not tokens:  # older servers do not report it; ~4 chars per token is close enough for billing display
        tokens = sum(len(t) for t in texts) // 4
    return softmax_ent([o["embedding"] for o in flat]), tokens


def authorized(request: Request) -> bool:
    if not API_KEY:
        return True
    got = request.headers.get("authorization", "")
    return got.lower().startswith("bearer ") and hmac.compare_digest(got[7:].strip(), API_KEY)


@app.get("/health")
async def health():
    try:
        r = await client().get(f"{SGLANG_URL}/health", timeout=3.0)
        if r.status_code == 200:
            return {"status": "ok", "model": SERVED_MODEL}
    except httpx.HTTPError:
        pass
    return JSONResponse({"status": "loading"}, status_code=503)


async def decisions(request: Request):
    global _inflight
    if not authorized(request):
        return err(401, "Missing or invalid Authorization header (expected 'Bearer <key>')")
    try:
        raw = bytearray()
        async for chunk in request.stream():
            raw.extend(chunk)
            if len(raw) > 8 * 1024 * 1024:
                return err(413, "Request exceeds 8 MiB")
        body = json.loads(raw)
    except ValueError:
        return err(400, "request body is not valid JSON")
    try:
        plan = build_prompt_plan(body, PROMPT_STYLE)
        image = image_input(body)
        if image:
            for premise, _ in plan.pairs:
                image_premise(premise)
    except ApiError as e:
        return err(e.code, e.message)
    if _inflight >= MAX_INFLIGHT:
        return err(429, "Too many concurrent requests")
    _inflight += 1
    try:
        ent, tokens = await classify(plan.pairs, image=image)
        answers = finish_answers(plan, ent)
    except (httpx.HTTPError, RuntimeError, KeyError, ValueError) as e:
        return err(502, f"upstream model server failed: {type(e).__name__}: {str(e)[:200]}")
    finally:
        _inflight -= 1
    rid = "gen-dec-%d-%s" % (time.time(), "".join(random.choices(string.ascii_letters + string.digits, k=20)))
    return {"id": rid, "model": SERVED_MODEL, "provider": "openjev", "answers": answers,
            "probability_method": "normalized_entailment_v1",
            "usage": {"input_tokens": int(tokens), "output_tokens": 0, "cost": tokens * PRICE_PER_MTOK / 1e6}}


app.add_api_route("/api/alpha/decisions", decisions, methods=["POST"])
app.add_api_route("/api/v1/systemone", decisions, methods=["POST"])
app.add_api_route("/v1/systemone", decisions, methods=["POST"])
