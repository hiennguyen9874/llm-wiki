# Serving OpenJev

Three steps: download the weights, serve them with vLLM, run the helper in front of it.
Every number in the model card was measured with exactly the flags and settings below. Change one and the numbers no longer apply.

## Locked versions

| package | version |
|---|---|
| vllm | 0.29.0 |
| torch | 2.13.0 (the measured build is 2.13.0+cu130) |
| transformers | 5.17.0 |
| peft | 0.21.0 |
| openai (helper's client library) | 3.16.2 |
| httpx | 0.28.1 |

Measured on one H100 with online FP8 quantization. The shipped-helper results in the model card were measured with openai 3.16.2 and httpx 0.28.1. The public serving machine runs openai 3.15.0; the helper file does not pin a client version itself, so install the versions above to reproduce.

## 1. Download

```bash
hf download openjev/openjev --local-dir openjev
```

The repository root is the complete model (config, processor files and bfloat16 safetensors). There is nothing to merge. `<model dir>` below is that `openjev` folder.

## 2. vLLM

```bash
vllm serve <model dir> --host 127.0.0.1 --served-model-name qwen --port 8000 --enable-prefix-caching --max-model-len 16384 --gpu-memory-utilization 0.90 --limit-mm-per-prompt '{"image":1}' --trust-remote-code --max-num-seqs 256 --max-logprobs 64 --gdn-prefill-backend triton --quantization fp8
```

`--host 127.0.0.1` is a safety default, not a performance flag; every other flag is exactly as measured. Without `--host`, vLLM listens on all network interfaces, and this command sets no API key, so anyone who can reach port 8000 could use the model directly. Keep the backend on loopback or behind a firewall.

Three of the remaining flags are load-bearing for the helper, not tuning:
- `--served-model-name qwen`: the helper calls the model by that name.
- `--max-logprobs 64`: the helper asks for the exact score of every option letter (up to 52) in one request.
- `--max-model-len 16384` and `--limit-mm-per-prompt '{"image":1}'`: the request limits in the model card (prompts up to 16,384 tokens, one image).

## 3. Helper

```bash
VLLM=http://localhost:8000/v1 \
TOKENIZER=<model dir> \
READOUT_T=0.85 \
READOUT_NOUL_T=1.829074 \
READOUT_NOUL_BIAS=0 \
READOUT_TARGETED=1 \
READOUT_INSTR_STYLE=pyrepr \
SHIM_STAGGER=1 \
python helper/shim.py --host 127.0.0.1 --port 3000
```

This binds the helper to loopback: only processes on the same machine can call it. Every variable is written as an assignment in front of the command, which puts it into the helper process's environment whether or not it is exported in your shell. Setting the same variables on separate lines without `export` would leave the helper running on its file defaults. `helper/shim.py` is shipped unmodified (sha256 `81a22f1b1b8912a465059207ef9f60b7c6c16b4de6372305d867efbe38a1987a`). It needs the `openai` and `transformers` Python packages. Without `--host` / `--port` it binds `127.0.0.1:8765`.

### Environment knobs

| variable | value used here | default in the file | what it does |
|---|---|---|---|
| `VLLM` | `http://localhost:8000/v1` | same | OpenAI-compatible base URL of the vLLM server. |
| `TOKENIZER` | `<model dir>` | `Qwen/Qwen3.8-27B` | Tokenizer used to look up the token id of each option letter. Its directory name is also reported as the served model. |
| `READOUT_T` | `0.85` | `1.1` | Temperature for choice and score: each option's log-probability is divided by it before the softmax. |
| `READOUT_NOUL_T` | `1.829074` | `3.0` | Yes/no calibration slope: `p = sigmoid(logit(p_yes) / READOUT_NOUL_T + READOUT_NOUL_BIAS)`. |
| `READOUT_NOUL_BIAS` | `0` | `-0.4` | Bias term of the same formula. |
| `READOUT_TARGETED` | `1` | off | Reads the exact score of exactly the candidate letter tokens, matched by token id. When off, a letter that falls outside the raw top-K gets a floor value instead of its real score. The temperature and the yes/no slope above were fitted with this ON, so keep the three together. If any candidate score comes back missing, the request fails rather than being floored. |
| `READOUT_INSTR_STYLE` | `pyrepr` | JSON | How `instructions` that are an object or array are written into the prompt: Python literal text (the wording the model was trained on) instead of JSON. Plain string instructions are unaffected. |
| `SHIM_STAGGER` | `1` | off | For a long state (at least `SHIM_STAGGER_MIN_CHARS` characters, default 16000, roughly 4k tokens) the first question runs alone so the page is cached before the remaining questions run in parallel. |

Leave the rest at their defaults; none was set for the measured numbers: `READOUT_PERMS` (1), `SHIM_POOL` (16 questions in flight), `SHIM_STAGGER_MIN_CHARS` (16000), `SHIM_COMPACT`, `SHIM_COMPACT_CAP`, `SHIM_LAYOUT`, `SHIM_PAD`, `SHIM_LOOP_BREAK` (all off), `SHIM_MODEL`.

`SHIM_TOKEN`: see the next section. It is unset in the loopback setup above.

### Exposing the helper to other machines (separate, optional step; REQUIRES `SHIM_TOKEN`)

Do this only when callers run on other machines. It is the loopback command with two changes: the token on the first line and `--host 0.0.0.0`.

```bash
SHIM_TOKEN="${SHIM_TOKEN:?set SHIM_TOKEN to a long random secret before exposing the helper}" \
VLLM=http://localhost:8000/v1 \
TOKENIZER=<model dir> \
READOUT_T=0.85 \
READOUT_NOUL_T=1.829074 \
READOUT_NOUL_BIAS=0 \
READOUT_TARGETED=1 \
READOUT_INSTR_STYLE=pyrepr \
SHIM_STAGGER=1 \
python helper/shim.py --host 0.0.0.0 --port 3000
```

The first line does two jobs. It stops the command before Python starts when `SHIM_TOKEN` is unset or empty, and it hands the token to the helper process itself. A separate guard line is not enough: a token that is set in your shell but not exported passes such a guard, while the helper sees no token and serves unauthenticated. Tested with a stub in bash and zsh: unset or empty token, Python never starts; token set but not exported, the helper process receives it.

Confirm it on the running process, from another terminal, with no token: `curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3000/v1/version` must print `401`. If it prints `200`, the helper is serving unauthenticated: stop it.

What the helper actually does with the token, read from the code:
- It reads `SHIM_TOKEN` from the environment once, at start-up. Changing it means restarting the helper. Pass it through the environment or a secret store; never write it into a file in this package.
- When it is set, every route, `POST` and `GET` alike (`/v1/systemone`, `/v1/prewarm`, `/v1/chat/completions`, `/v1/version`), requires the exact header `Authorization: Bearer <token>`; anything else gets `401`.
- **When it is empty or unset there is no check at all.** The helper does not refuse to start on `0.0.0.0` without a token: it starts normally and serves every request from anyone who can reach the port, including the chat pass-through, which is open access to the model. The requirement is yours to enforce; that is what the first line of the command above is for.
- The helper speaks plain HTTP, so the token and every state you send travel unencrypted. Across a network you do not control, put a TLS-terminating proxy in front of it. The check is a plain string comparison with no rate limiting: treat the token as a gate, not as hardened authentication.

**An authenticated helper does not protect an externally reachable backend.** The token guards the helper's port only. The vLLM backend on port 8000 has no authentication in this setup, so if that port is reachable from outside, anyone can bypass the helper and its token entirely. Keep the backend on `127.0.0.1` as in step 2, or behind a firewall, and expose the helper's port only.

## POST /v1/systemone

One request = one state plus a map of questions. Each question is answered independently and comes back typed.

Request fields:
- `model`: string. This helper ignores it (one model is served); send it anyway, a stricter front end may require it.
- `state`: string or object, required. An object may carry one image as `screenshot` or `image` (a `data:image/...` URL, or raw base64 PNG/JPEG); the rest of the object is the text state.
- `questions`: non-empty map of `<your key>` to a question:
  - `type`: `"choice"`, `"noul"` (yes/no) or `"score"`.
  - `instructions`: required for every question. String, object or array.
  - `criteria`: for `choice`, a non-empty map of option name to description (or `null`); for `score`, an ordered array of at least two levels, lowest first; for `noul`, optional `{"true": ..., "false": ...}` descriptions.

```bash
curl -s http://localhost:3000/v1/systemone \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "openjev",
    "state": "Customer message: I was charged twice for my order last week and nobody has replied.",
    "questions": {
      "route": {
        "type": "choice",
        "instructions": "Which team should handle this message?",
        "criteria": {
          "billing": "charges, refunds, invoices",
          "shipping": "delivery and tracking",
          "technical": "bugs and login problems"
        }
      },
      "angry": {
        "type": "noul",
        "instructions": "Is the customer angry?"
      },
      "urgency": {
        "type": "score",
        "instructions": "How urgent is this message?",
        "criteria": ["can wait", "should be handled today", "needs an immediate reply"]
      }
    }
  }'
```

Add `-H "Authorization: Bearer $SHIM_TOKEN"` when a token is set.

Response shape (values shown as placeholders; nothing here is a measured number). The request's `model` field is a free label that the helper ignores (`"openjev"` above is illustrative); the response's `model` string is built by the helper from the directory name of the merged model you serve, its calibration settings, its flags and its own hash, exactly in this form:

```
{
  "id": "shim-<unix milliseconds>",
  "model": "<model dir name> T=0.85 noul=1.829074,0.0 flags={...} shim=shim.py@81a22f1b1b89",
  "answers": {
    "route":   {"type": "choice", "choice": "<winning option name>",
                "probabilities": {"billing": <p>, "shipping": <p>, "technical": <p>}, "confidence": <0 to 1>},
    "angry":   {"type": "noul", "noul": <calibrated probability of yes>},
    "urgency": {"type": "score", "score": <expected level index, 0-based>,
                "legend": {"0": "can wait", "1": "should be handled today", "2": "needs an immediate reply"},
                "probabilities": {"0": <p>, "1": <p>, "2": <p>}, "confidence": <0 to 1>}
  },
  "usage": {"input_tokens": <prompt tokens summed over all passes>, "output_tokens": 0}
}
```

`choice` is picked before rounding; probabilities are rounded to 4 decimals. `confidence` for a choice is `(max p - 1/N) / (1 - 1/N)`; for a score it is one minus the expected distance from the most likely level, relative to a uniform answer.

Errors: `401` (bad or missing token) and `422` (missing `state` / `questions`, unknown `type`, bad `criteria`, missing `instructions`) return `{"error": {"code": <int>, "message": "<text>"}}`.

Other routes: `GET /v1/version` (served model directory, calibration constants, flags, the helper's own sha256; use it to pin what you measured), `POST /v1/prewarm` with `{"state": ...}` (reads the page once so following questions hit the cache), `POST /v1/chat/completions` (passes a chat request through to vLLM with thinking switched off).

## Known helper behaviour (unchanged on purpose: this is the file the numbers were measured with)

- More than 52 options: the options are split into near-equal chunks of at most 52, each chunk is one pass, one more pass ranks the chunk winners, and the results are composed into one distribution over all options. Several passes, approximate, and less stable between runs than a single pass.
- Rounded probabilities can miss a sum of exactly 1 by a rounding remainder, most visibly with very many options. With a near-tie, check `probabilities[choice]` against the maximum with a tolerance instead of assuming the first maximum is the choice.
- Malformed JSON, a body that is not a JSON object, `noul` criteria sent as a list, or a failure of the model server closes the connection without a JSON error body. Treat a dropped connection as a failed request.
- No caps are enforced on option count or score levels; the limits in the model card are what was measured, not what is rejected.
- A screenshot sent together with a page / elements style state uses a prompt layout that the image training stage did not see in that shape; run your own matched check before relying on it.
