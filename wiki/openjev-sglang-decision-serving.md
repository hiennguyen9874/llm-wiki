---
type: Concept
title: OpenJev-SGLang Decision Serving
description: SGLang-backed Jev-compatible decision server on Qwen3.6-35B-A3B with N+1 one-token readout, Modal B200 recipe, and 64-option letter-combination labels.
tags: [open-weights, decision-models, jev, sglang, serving]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T00:00:00Z }
sources:
  - id: openjev-sglang-2026
    resource: ../raw/openjev-sglang.md
    kind: documentation
    title: openjev-sglang
---

# OpenJev-SGLang Decision Serving

Synthesis: openjev-sglang is an early Jev-API reproduction that serves typed `noul` / `choice` / `score` decisions from Qwen3.6-35B-A3B on SGLang with a prefill plus first-token readout (N+1 one-token calls for N questions); the document itself says SGLang now ships a native decisions endpoint the same way and new users should prefer that API[^openjev-sglang-2026].

## Identity and freshness

- Early experiment reproducing Jev after release, not affiliated with TypeSafe; no requests go to TypeSafe and SGLang generation/admin routes stay on localhost[^openjev-sglang-2026].
- Backend model is Qwen3.6-35B-A3B served through SGLang 0.5.19 Rust frontend with radix caching and breakable prefill CUDA graphs, one B200 per container; public model ID `Qwen/Qwen3.6-35B-A3B` with NVIDIA's repository as the internal weight source[^openjev-sglang-2026].
- Freshness limit — **reported** in the source NOTE: SGLang now ships a native decisions endpoint implemented the same way, so treat this server as superseded guidance and verify against current SGLang decision-model docs before building[^openjev-sglang-2026].
- No author, date, revision, or license is stated in the single-file bundle; upstream locators are TypeSafe Jev API docs, SGLang decision-model docs, Modal Server docs, and one SGLang mixed-logprob issue link[^openjev-sglang-2026].

## Inference mechanism (**reported**)

- Pipeline: validate schema, answer count, body size, context length, and total token budget; render the native chat template once with thinking disabled; split a common prefix and independently tokenize each question suffix[^openjev-sglang-2026].
- Cache warmup: send the common prefix to `/generate` with `max_new_tokens=1`, await completion, and discard the sampled token to warm SGLang radix cache[^openjev-sglang-2026].
- Branch scoring: concurrently send `prefix + question suffix + assistant header + "Answer:\n"` per question, each with `max_new_tokens=1`; request `token_ids_logprob` for every answer label with `logprob_start_len=-1` so prompt logprobs are not recomputed; the sampled token is ignored[^openjev-sglang-2026].
- Normalization: stable-softmax the requested label logprobs; `noul` returns `P(yes)`, `choice` returns argmax plus full distribution, `score` returns zero-based `sum(level_index * probability)` with a legend; `OPENJEV_TEMPERATURE` (default 1.0) applies during normalization[^openjev-sglang-2026].
- Labels: options render as `A: description`, `B: description`, without JSON wrappers; because Qwen tokenizes `10` and `64` as multiple tokens, labels are `A`–`Z` then verified single-token letter combinations (`AA`, `AB`, …), all 64 checked against the actual tokenizer at startup, preserving original option names in the returned distribution[^openjev-sglang-2026].
- Choice keys identify response fields and are hidden from the model, except when a description is `null`: then the option key supplies its meaning, matching Jev's nullable description schema[^openjev-sglang-2026].
- No chain of thought and no autoregressive continuation after the first token; speculative decoding is not enabled[^openjev-sglang-2026].
- Cache behavior is opportunistic, not a pinned per-request KV session: hybrid Qwen recurrent state, page boundaries, pressure, and concurrency can reduce hits; backend uses `--mamba-radix-cache-strategy extra_buffer`[^openjev-sglang-2026].
- Observability: `x-openjev-prefix-tokens` exposes requested common-prefix size; `x-openjev-cached-tokens` sums branch cache hits when SGLang reports counts, but SGLang 0.5.19 Rust frontend omits them (header absent, smoke reports `null`); `Server-Timing` separates prompt preparation, shared prefill, and branch inference[^openjev-sglang-2026].
- Usage accounting: `usage.input_tokens` sums full SGLang prompt counts across warmup plus all branches including cached tokens; `usage.output_tokens` is N+1; these are backend counts, not billing estimates or unique computed tokens[^openjev-sglang-2026].

## State rendering (**reported**)

- `state`, `instructions`, and criteria descriptions accept strings, JSON objects, or arrays; criteria descriptions may be `null`; structured criteria serialize as compact JSON[^openjev-sglang-2026].
- A list-of-messages state, or exactly `{"messages": [...]}`, renders with the model native chat template; original roles and message objects are retained and the classification question becomes an additional user turn even after another user turn[^openjev-sglang-2026].
- Other structured state serializes intact into a user message; objects containing `messages` plus extra fields stay intact so metadata is not discarded; chat state supports text, not image/audio/video content[^openjev-sglang-2026].

## Routes (**reported**)

| route | purpose |
|---|---|
| `POST /v1/systemone` | Noul, Choice, and Score evaluation |
| `GET /v1/models` | Model catalogue with TypeSafe and OpenAI-style fields |
| `GET /v1/limits` | Admission limits |
| `GET /health` | Readiness, including SGLang health and startup duration |
| `GET /health/live` | API process liveness |
| `GET /` | Scalar API reference with editable example and request client |
| `GET /docs` | Built-in Swagger UI |
| `GET /openapi.json` | Generated API schema |

- `jev-latest` is a compatibility alias for the configured Qwen model; override the public ID with `OPENJEV_SERVED_MODEL_NAME` or `openjev serve --served-model-name`, also passed to SGLang as `--served-model-name`[^openjev-sglang-2026].

## Limits and configuration (**reported**)

- Defaults: 64 questions, 2–64 answers per Choice/Score, 2 MiB JSON, 32,768 tokens per branch including output, 262,144 total submitted input tokens, 16 simultaneous evaluations, 64 simultaneous backend calls[^openjev-sglang-2026].
- Errors: invalid requests return 422 before inference; oversized bodies 413; overload 529 with `Retry-After`; backend timeouts 504; failed or cancelled evaluations cancel siblings and attempt SGLang aborts[^openjev-sglang-2026].
- Common settings all overridable as `OPENJEV_*` (see `src/openjev/config.py` in the project): `OPENJEV_MODEL` (`nvidia/Qwen3.6-35B-A3B-NVFP4`), `OPENJEV_SERVED_MODEL_NAME`, pinned `OPENJEV_REVISION`, `OPENJEV_FRONTEND` (`rust`, `python` explicit fallback), `OPENJEV_MAX_INPUT_TOKENS` (32768), `OPENJEV_MAX_TOTAL_INPUT_TOKENS` (262144), `OPENJEV_MAX_CONCURRENT_REQUESTS` (16), `OPENJEV_MAX_CONCURRENT_BRANCHES` (64), `OPENJEV_REQUEST_TIMEOUT` (120 s), `OPENJEV_TEMPERATURE` (1.0), optional `OPENJEV_API_KEY` and separate `OPENJEV_BACKEND_API_KEY`[^openjev-sglang-2026].
- Confidence follows `confidence = 1 - H(probabilities) / log(number_of_options)`, clamped to [0, 1]: zero for uniform, one for point mass; conditioned on supplied options and prompt/label ordering, not a calibrated correctness estimate[^openjev-sglang-2026].

## Deployment and operations (**reported**)

- Stack: separate Python FastAPI API process (uvloop, Rust-backed HF tokenizer, pooled async HTTP to SGLang on localhost) plus SGLang container holding CUDA dependencies; `uv sync` on a laptop installs only API, deployment tools, and tests[^openjev-sglang-2026].
- Modal: `uv run modal run modal_app.py` for a temporary checked server, `uv run modal deploy modal_app.py` for a stable public endpoint printing a `https://...us-west.modal.direct` URL; unauthenticated Modal Server with `routing_region="us-west"`, `compute_region=["us-west", "us-central", "us"]`, unbounded autoscaling to zero after five idle minutes, `min_containers=1` to keep a B200 warm[^openjev-sglang-2026].
- Supervision: if SGLang exits the API exits too; the Modal launcher watches the API and exits the container so Modal replaces it rather than leaving a live HTTP process with a dead backend; normal shutdown disarms both watchers[^openjev-sglang-2026].
- Persistence and startup: first build imports a large SGLang image; first GPU start downloads weights and compiles/captures kernels; weights persist in the `openjev-huggingface` Modal Volume with SGLang tuning and Triton caches; later starts reuse files but CUDA graph capture still runs; Rust frontend gets an explicit local tokenizer directory to avoid remote-name lookup on revision-pinned snapshots; scaled-to-zero servers return 503 while starting[^openjev-sglang-2026].
- Compatibility workaround: cache warmups request one unused token probability to avoid SGLang's mixed-logprob batch crash (linked issue), keeping warmups and scoring batch-compatible without patching SGLang[^openjev-sglang-2026].
- Smoke test: `uv run openjev smoke https://YOUR-SERVER.us-west.modal.direct` covers all three answer types, a 64-answer question, semantic sanity, 65-answer rejection, startup wait, latency, and cache usage; `modal run` saves `smoke-result.json`[^openjev-sglang-2026].
- Local use: `uv run pytest` (offline unit plus API), `pytest -m integration` (real tokenizer, small HF download, no GPU), `ruff check`, `openjev schema` with no GPU/download; `openjev serve --connect http://127.0.0.1:30000` needs matching model/tokenizer revision, selected-token logprobs, radix cache, and context length; `--sglang-python` targets a B200 host with SGLang 0.5.19 in another environment[^openjev-sglang-2026].
- Remote customization: launcher forwards `OPENJEV_PROFILE`, `OPENJEV_FRONTEND`, `OPENJEV_SERVED_MODEL_NAME`; other settings go in `image.env(...)` or a Modal Secret; the default Modal endpoint intentionally has no auth[^openjev-sglang-2026].

## Relationships

- Contrasts with [OpenJev Open-Weights Typed Decision Model](openjev-decision-model.md): different base model (Qwen3.6-35B-A3B here vs Qwen3.8-27B there) and backend (SGLang N+1 readout here vs vLLM plus helper there); do not merge accuracy, latency, or limit figures.
- Uses [Jev API Patterns](jev-api-patterns.md) `choice` / `noul` / `score` shapes over `POST /v1/systemone`.
- Informs [Classifier Selection](classifier-selection.md) as a Modal B200 self-host recipe distinct from the H100 vLLM recipe.
- Requires [Classifier Calibration](classifier-calibration.md) for interpreting its softmax probabilities and normalized-entropy confidence.

## Coverage limits

- Inspected by static read of `../raw/openjev-sglang.md` only; no project code, `src/openjev/config.py`, `modal_app.py`, `examples/request.json`, container image, or live Modal/SGLang deployment was inspected, and no command or smoke test was executed[^openjev-sglang-2026].
- All mechanism, limit, default, latency-adjacent, and cache-hit figures are **reported** documentation values; scheduler-log cache hits and B200 behavior were not reproduced here[^openjev-sglang-2026].
- External links (TypeSafe API, SGLang decision-model docs, Modal Server docs, SGLang issue 34719, imgur demo gif) were not resolved beyond the prose[^openjev-sglang-2026].
- Supersession is one-directional and **reported**: the source recommends SGLang's native decisions endpoint instead; the native endpoint itself was not inspected here[^openjev-sglang-2026].

[^openjev-sglang-2026]: openjev-sglang project, "openjev-sglang," canonical local entry `../raw/openjev-sglang.md`. Locators in file: top NOTE (early experiment, native SGLang endpoint recommendation); intro (Qwen3.6-35B-A3B, SGLang 0.5.19 Rust frontend, B200, FastAPI/uvloop/tokenizer/pooled HTTP); "Run on Modal" (uv/modal commands, unauthenticated Server, regions, autoscale/min_containers, watchers, warmup mixed-logprob workaround, volumes, tokenizer dir, 503, smoke command); "Request" (curl example, state/criteria rendering rules, route table, jev-latest alias, served-model override, localhost-only SGLang); "How inference works" (validation, template once, prefix/suffix, N+1 calls, max_new_tokens=1, token_ids_logprob/logprob_start_len, softmax, noul/choice/score math, A–Z/AA labels and startup check, radix/mamba strategy, headers, usage, Server-Timing, no-CoT/no-speculative); "Limits and configuration" (defaults, 422/413/529/504 codes, OPENJEV_* table, Modal forwarding, confidence formula); "Local development / existing SGLang" (pytest/ruff/schema/serve commands).
