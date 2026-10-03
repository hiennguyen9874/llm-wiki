#!/usr/bin/env python3
"""The frozen helper (shim.py, sha 81a22f1b…) served over an MLX model on this Mac instead of vLLM: every prompt, option layout, letter readout,
temperature and yes/no calibration line is the helper's own code, untouched. Only `shim.client` is replaced by a stand-in that answers the ONE call
the helper makes in TARGETED mode (chat.completions.create with logprob_token_ids) from the MLX model's logits at the first output position.
Chat rendering uses the checkpoint's own chat template through transformers (the same template vLLM applies), thinking off, generation prompt on.
Run: TOKENIZER=<mlx dir> SHIM_MODEL=<mlx dir> READOUT_T=0.85 READOUT_NOUL_T=1.829074 READOUT_NOUL_BIAS=0 READOUT_TARGETED=1 READOUT_INSTR_STYLE=pyrepr \
     SHIM_STAGGER=1 SHIM_TOKEN=... python shim_mlx.py --helper release/openjev_merged_draft/helper/shim.py --model <mlx dir> --port 3000
Selfcheck: python shim_mlx.py --helper ... --model <mlx dir> --selfcheck   (renders + scores one fixed question; prints letter logprobs)."""
import argparse, hashlib, importlib.util, math, os, sys, threading, types

ap = argparse.ArgumentParser(); ap.add_argument("--helper", required=True); ap.add_argument("--model", required=True); ap.add_argument("--port", type=int, default=3000)
ap.add_argument("--host", default="127.0.0.1"); ap.add_argument("--selfcheck", action="store_true"); a = ap.parse_args()
assert os.environ.get("READOUT_TARGETED") == "1", "the MLX stand-in implements only the TARGETED readout (READOUT_TARGETED=1)"
os.environ.setdefault("TOKENIZER", a.model); os.environ.setdefault("SHIM_MODEL", a.model)
HELPER_SHA = hashlib.sha256(open(a.helper, "rb").read()).hexdigest(); assert HELPER_SHA.startswith("81a22f1b"), f"helper is {HELPER_SHA[:16]}, not the frozen 81a22f1b"

import mlx.core as mx
from mlx_lm import load
from transformers import AutoTokenizer
MLX_MODEL, _ = load(a.model); tok = AutoTokenizer.from_pretrained(a.model)   # module-level name distinct from create()'s `model` argument (the helper passes model="qwen")
LOCK = threading.Lock(); STATS = {"calls": 0, "prompt_tokens": 0}

class _Obj(types.SimpleNamespace): pass

def create(model=None, max_tokens=1, temperature=0, logprobs=False, messages=None, extra_body=None, **kw):
    """The helper's TARGETED call: messages = [{"role": "user", "content": <str>}], extra_body.logprob_token_ids = the candidate letter ids.
    Returns logprobs for exactly those ids (log-softmax over the full vocabulary at the first output position) as `token_id:<id>` entries."""
    eb = extra_body or {}; want = eb.get("logprob_token_ids") or eb.get("allowed_token_ids")
    assert want and messages and isinstance(messages[0]["content"], str), "MLX stand-in: text-only prompts with logprob_token_ids"
    assert (eb.get("chat_template_kwargs") or {}).get("enable_thinking") is False
    ids = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, enable_thinking=False)
    if hasattr(ids, "input_ids"): ids = ids["input_ids"]
    with LOCK:
        logits = MLX_MODEL(mx.array(ids)[None])[0, -1].astype(mx.float32); lp = logits - mx.logsumexp(logits, axis=-1); vals = [float(lp[i]) for i in want]; mx.eval(logits)   # log-softmax over the full vocabulary
        STATS["calls"] += 1; STATS["prompt_tokens"] += len(ids)
    top = [_Obj(token=f"token_id:{i}", logprob=v) for i, v in zip(want, vals)]
    return _Obj(choices=[_Obj(logprobs=_Obj(content=[_Obj(top_logprobs=top)]))], usage=_Obj(prompt_tokens=len(ids)))

spec = importlib.util.spec_from_file_location("shim", a.helper); shim = importlib.util.module_from_spec(spec); spec.loader.exec_module(shim)
shim.client = _Obj(chat=_Obj(completions=_Obj(create=create)), base_url=f"mlx://{os.path.basename(a.model.rstrip('/'))}")
assert shim.TARGETED and shim.PERMS == 1, "helper must run TARGETED with PERMS=1 here"

if a.selfcheck:
    st = shim.with_image({"text": "I was charged twice for my order and nobody replied."})
    ans, n = shim.answer_choice(st, {"type": "choice", "instructions": "Which team should handle this?", "criteria": {"billing": None, "shipping": None, "technical": None}})
    print("selfcheck:", ans, "prompt_tokens", n); ans2, n2 = shim.answer_noul(st, {"type": "noul", "instructions": "Is the customer angry?"}); print("selfcheck noul:", ans2, n2)
    print("helper", HELPER_SHA[:16], "version", shim.VERSION["model_dir"], shim.VERSION["T"], shim.VERSION["noul_t"], shim.VERSION["flags"]); sys.exit(0)

print(f"MLX helper on :{a.port}; model {a.model}; helper {HELPER_SHA[:16]}; version {shim.MODEL_STRING}", flush=True)
shim.ThreadingHTTPServer.request_queue_size = 256; shim.ThreadingHTTPServer.daemon_threads = True
shim.ThreadingHTTPServer((a.host, a.port), shim.H).serve_forever()
