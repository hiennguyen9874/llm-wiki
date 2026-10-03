---
type: Concept
title: OpenJev Diffusion Decision Server (razorback16)
description: Jev-compatible decision server that reads typed answers from a DiffusionGemma diffusion canvas plus routed Laya, Verdict, CLM, and JevK5 models, with extensions, backends, and reported latency figures.
tags: [open-weights, decision-models, jev, diffusion, serving]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:45:00Z }
sources:
  - id: razorback16-openjev-2026
    resource: ../raw/razorback16-openjev.md
    kind: documentation
    title: OpenJev
---

# OpenJev Diffusion Decision Server (razorback16)

Synthesis: OpenJev (razorback16) is an open-source Jev-wire-compatible "System One" decision server whose primary model reads typed `noul` / `choice` / `score` answers as probability distributions from one masked token slot each in a DiffusionGemma 26B-A4B diffusion canvas, with no text parsing and therefore no off-schema answers; the same server also routes to Laya, Verdict, CLM, and JevK5 models, adds `images` / `steps` / `samples` / `think` / `sequential` extensions, and ships vLLM (NVIDIA) and MLX (Apple silicon) backends plus a hosted Codiv endpoint[^razorback16-openjev-2026].

## Identity, license, and models

- Independent project by razorback16, not affiliated with or endorsed by TypeSafe AI; reuses TypeSafe's Jev wire API so TypeSafe SDKs work unchanged; hosted for free on Codiv (`https://api.codiv.ai/v1/systemone`, 100M input tokens on signup)[^razorback16-openjev-2026].
- All weights named are **reported** Apache-2.0; upstream repo `https://github.com/razorback16/openjev`; Docker image `razorback16/openjev` (tag `0.5.0` in the doc); source license of this doc page is Apache-2.0 per its License section[^razorback16-openjev-2026].
- Model table (**reported** in "Models" section)[^razorback16-openjev-2026]:

| Model id | Base | Size | Input | Choices | Runs on |
|---|---|---|---:|---|---|
| `openjev-latest` (`openjev-0.1`) | DiffusionGemma 26B-A4B (NVIDIA/Google), read as diffusion canvas | 26B total, 4B active | text and images | up to 255 | vLLM (NVIDIA GPU) or MLX (Apple silicon) |
| `laya-1.0` | Laya by Nandakishor M / Convai Innovations | 421M | text, 1,024 tokens | up to 255 | PyTorch, GPU or CPU |
| `verdict-1.4` | Verdict by Heman10x | 151M | text, 512 tokens | up to 24 | PyTorch, GPU or CPU |
| `clm-v0.1` | CLM by Contrastive-LM (contrastive heads over Qwen3-8B) | 8B + 2 x 9.4M | text, 2,048 tokens | up to 255 | vLLM (NVIDIA GPU) |
| `jevk5-0.2` | JevK5 by Alibi Serikbay (Qwen3.5-4B with distilled LoRA, answer-letter readout) | 4B | text, 16,384 tokens | up to 255 | vLLM (NVIDIA GPU) |

- `diffusiongemma-26b` is the same DiffusionGemma weights exposed for text generation; Laya, Verdict, CLM, and JevK5 are other people's models served behind the same API with credit to their authors[^razorback16-openjev-2026].

## Wire API (Jev-compatible)

- Routes: `POST /v1/systemone` (`{state, model, questions}` to `{model, answers, usage}`); `POST /v1/chat/completions` OpenAI-style generation with model `diffusiongemma-26b`; `GET /v1/models` lists `openjev-0.1`, alias `openjev-latest`, `diffusiongemma-26b`, and routed small-encoder models when running; `jev-latest` and `jev-preview` are accepted as aliases so TypeSafe SDK defaults work[^razorback16-openjev-2026].
- Question types (**reported** in "API" section)[^razorback16-openjev-2026]:
  - `noul` (yes/no) with optional `criteria: {true, false}` returns `{noul: P(yes)}`.
  - `choice` with `criteria: {name: description}` returns `{choice, probabilities, confidence}`.
  - `score` with `criteria: [level0, level1, ...]` (1-10 levels; one level answered directly) returns `{score: sum i*p_i, legend, probabilities, confidence}`.
- `confidence` is `1 - H(p)/ln K` (1 certain, 0 uniform); `usage.input_tokens` counts prompt tokens including image tokens; `usage.output_tokens` is 0 unless `think` is set[^razorback16-openjev-2026].
- `Server-Timing` header reports `model;dur`, `server;dur`, `total;dur`; model time is summed over reads and can exceed total when reads run in parallel[^razorback16-openjev-2026].
- Errors mirror Jev shapes checked against the live API: `422` FastAPI validation list for wrong-shaped fields; `400` plain-text for unaskable questions (no options, too many options/score levels); `400 api_usage_error` for unknown model/type; `{"detail": {"error_type", "message"}}` for auth (`401`/`403`); `429` rate limits; `529` overload[^razorback16-openjev-2026].
- Differences from Jev (**reported**): model names are OpenJev's own with `jev-latest`/`jev-preview` aliases; a pinned Jev version such as `jev-1.13.0` gets `400` Unknown model; many questions are read in chunks of about 12 per read, run in parallel[^razorback16-openjev-2026].

## Extensions (OpenJev additions; absent fields behave exactly like Jev)

| Field | Values | Effect | Cost |
|---|---|---|---|
| `images` | up to 8, `data:image/...;base64,` URL or `{content_type, base64}`; JPEG/PNG/WebP/GIF, 5 MB each; placed before state | questions can ask about images | ~280 input tokens per image |
| `steps` | 1-8, default 1 | denoise steps per read; more steps let answers settle | same tokens, more GPU time |
| `samples` | 1-32 | N noisy reads averaged; replaces automatic re-reads; `1` is one read, fastest | N x input tokens |
| `think` | 0-4096 tokens hard cap | model writes a thought, then reads answers after it; give multi-step problems 512+ | input tokens twice plus thought as output tokens |
| `sequential` | `true` | long lists read chunks in order, each seeing prior answers | one read per chunk, serial |

- `think` and `sequential` need a text state; combining them with `images` gets a 400[^razorback16-openjev-2026].
- Text generation ignores sampling fields (`temperature`, `seed`, penalties) because vLLM refuses them for diffusion models; `max_tokens` defaults 1024, cap 8192; at most 8 generations run at once so reads keep room; MLX ignores `tools`/`logprobs` and returns no thought[^razorback16-openjev-2026].

## Mechanism (**reported** in "How it works")

- DiffusionGemma is a discrete diffusion model denoising a full token canvas per forward pass; OpenJev builds a canvas with only answer slots masked, one token per question, and reads the label-token distribution in one read-only pass — that distribution is the answer[^razorback16-openjev-2026].
- One token per label: `yes`/`no` for `noul`, `A`/`B`/`C` for choice, `0`/`1`/`2` for score; the model never writes the slots, so only label tokens are scored and answers cannot go off-schema; confidence comes from the distribution itself, not a self-reported number[^razorback16-openjev-2026].
- Uncertain slots (entropy > 0.1) trigger three more fresh-noise reads averaged over four; one uncertain question re-reads all questions in the request; extra reads add no `usage` tokens; `samples: 1` disables to one read; question ids never reach the model (it sees `q1`, `q2`, ...)[^razorback16-openjev-2026].
- vLLM support is upstream PR vllm-project/vllm#57250, merged 2026-09-22 (seeded canvases, read-only steps, step caps, pinned canvas positions); `openjev/engine.py` adapts that PR's `structured_server.py` example with async I/O, bounded concurrency, and backpressure[^razorback16-openjev-2026].

## Backends and reported latency

- Backend choice by hardware: vLLM default on NVIDIA GPU with 24 GB+ (tested RTX PRO 6000 Blackwell sm_120) via Docker image (CUDA 13), up to 64 reads in flight; MLX via `pip install -e '.[mlx]'` with `OPENJEV_BACKEND=mlx` on Apple silicon (~16 GB free to load), one read at a time, local use only[^razorback16-openjev-2026].
- NVIDIA vLLM setup: `git clone https://github.com/razorback16/openjev && docker compose up -d` (API on 127.0.0.1:8080 when loaded) or `docker run` with `~/.cache/huggingface` mount (~18 GB first download); `OPENJEV_UPSTREAM` points at an existing vLLM server; without Docker, pin vLLM commit `1b3b88ec2b7457aa030db4d0e7d8aaf04f6d0fb8`, raise `MAX_LOGPROB_TOKEN_IDS` 128 to 512 for >128-option choices, apply `docker/patches/vision_prefix_lm.py` for bidirectional image attention, and serve with the doc's `vllm serve` flags (canvas 64, `--max-logprobs 32`, prefix caching, async scheduling, TRITON_ATTN, image limit 8)[^razorback16-openjev-2026].
- **Reported** RTX PRO 6000 at 38% GPU, 3 questions/request, cache-busted states: 1 concurrency 10.7 req/s p50 94 ms; 16 conc. 43.3 req/s p50 367 ms p95 369 ms; 32 conc. 51.7 req/s p50 545 ms p95 618 ms; 64 conc. 57.4 req/s p50 760 ms p95 1109 ms; single-request `samples: 1`: 1 question p50 27 ms, 3 questions p50 31 ms[^razorback16-openjev-2026].
- Apple silicon: same prompts/canvases/seeds as vLLM; supports `images`, `samples`, `sequential`, `steps`, `think`, automatic re-reads with identical billing; steps after the first reuse one prompt prefill (GPU time, not tokens); re-reads/`samples` share one vision pass; 3-question request ~0.2-0.4 s on M3 Ultra, ~0.39 s on M4 Max (4-bit), ~4 req/s at 16 concurrency[^razorback16-openjev-2026].
- MLX memory: 4-bit load ~16 GB; MLX pools freed GPU buffers up to peak working set (one M4 Pro 48 GB workload 16.6 to 36.2 GB); `OPENJEV_MLX_CACHE_LIMIT_GB=4` held it at 23.5 GB with same answers/speed; off by default since 8-bit/bf16 reads can exceed 4 GB — set above working set; `OPENJEV_MLX_PROMPT_CACHE` default 12 cached prefills[^razorback16-openjev-2026].

## Routed models: serving notes and limits (**reported**)

- Small encoders run in their own containers (`OPENJEV_BACKEND=laya` or `verdict`); `docker compose up -d` starts both beside vLLM on one GPU with `OPENJEV_MODEL_ROUTES` forwarding from `:8080`; `/v1/models` lists a routed model even when stopped (then 503); together ~3.7 GB bf16 on GPU — reserve via `OPENJEV_GPU_UTIL`[^razorback16-openjev-2026].
- Laya `laya-1.0` (ModernBERT-large `laya-typed-decisions` checkpoint): 1,024-token state limit options-included, up to 255 options but options share 256 tokens so use ~20 or split; Verdict `verdict-1.4` (ModernBERT-base GLiClass head, v1.4 engine): 512-token limit, up to 24 options[^razorback16-openjev-2026].
- **Reported** RTX PRO 6000, 16 questions/request: Laya 2.5 GB, 10 ms short state / 109 ms full 16x1024; Verdict 1.2 GB, 7 ms short / 21 ms full 16x512; FlashAttention 2 no gain (same memory, within 6%, short slower)[^razorback16-openjev-2026].
- Encoder differences from DiffusionGemma: text only (`images`, `steps` > 1, `samples` > 1, `think`, `sequential` get 400); over-limit states truncated silently with `usage.input_tokens` counting what was read, each question billed separately; Verdict's "insufficient evidence" option removed with remaining probabilities renormalized, Verdict ignores noul `criteria`; Laya rounds to 4 decimals; GPU weights bf16 (36-answer check: no top-option change, drift <= 0.021 Laya / 0.007 Verdict); Verdict prompt/temperatures from its v1.4 engine[^razorback16-openjev-2026].
- CLM `clm-v0.1` (Contrastive-LM, frozen Qwen3-8B + 2x9.4M state/action heads, 512-dim cosine softmax): `docker/Dockerfile.clm` runs vLLM pooling runner plus heads in one container on the same pinned vLLM commit without its changes; layout/heads/scoring from `contrastive-lm` 0.1.0; compose `--profile clm` with `clm-v0.1=http://clm:8080` in routes; shares GPU via `OPENJEV_CLM_GPU_UTIL` default 0.12 (lower `openjev` share); default FP8 Qwen3-8B weights (7.7 GB vs 14.1 GB bf16); **reported** 581 four-way SQuAD FP8/bf16 agree 98.5% top, cosine 0.9992, 89.7% to 88.8%; Ampere note (Marlin weight-only FP8, RedHatAI dynamic FP8 fails to start, `OPENJEV_MODEL=Qwen/Qwen3-8B` for bf16)[^razorback16-openjev-2026].
- **Reported** CLM on one RTX 3090 at `OPENJEV_GPU_UTIL=0.85`, unique SQuAD-paragraph states with 3 questions (~550 tokens): 99 ms (FP8) / 130 ms (bf16) single; 18 req/s, ~9.6-9.8k prompt tokens/s at 64 concurrency; GPU-bound prefill, FP8 buys latency/cache (2.4x prefix cache: 78k vs 33k tokens), `--max-num-batched-tokens 8192` no gain[^razorback16-openjev-2026].
- CLM differences: text only; over-2,048-token states lose the start (question survives), unlike upstream cutting the end (CLM PR #6); recent-text embedding/projection caches (`OPENJEV_CLM_EMBED_CACHE`, `OPENJEV_CLM_CACHE`) with `usage` counting only fresh embeds (repeat request 0); score-question warning — upstream one level can win regardless of state (CLM issue #3), doc's check scored a thankful customer "annoyed": evaluate score questions on own data; choice/noul follow state[^razorback16-openjev-2026].
- JevK5 `jevk5-0.2` (Alibi Serikbay, Qwen3.5-4B + distilled LoRA merged, SemIf readout): per-question JSON lettered A-P, softmax over letter logits at calibration temperature 1.532 from `jevk5_config.json`; >16 options take combined multi-passes; `docker/Dockerfile.jevk5` runs bf16 on same pinned vLLM without changes; prompts/combining from `jevk5` 0.2.2; vLLM batches questions across requests (upstream reads one at a time); compose `--profile jevk5` with `jevk5-0.2=http://jevk5:8080`; `OPENJEV_JEVK5_GPU_UTIL` default 0.12[^razorback16-openjev-2026].
- JevK5 parity and speed (**reported**): 231 JevBench public items, OpenJev vs JevK5's own v0.2 run agree on all 231 top answers and token counts (identical prompts), probabilities differ 0.0012 median / 0.055 max (kernel nondeterminism), both 86.6%; RTX 3090 same SQuAD-style load (7.9 GB weights, 284k KV): 3-question ~700-token request 116 ms single / 8-11 req/s at 32-64 conc (~8k tokens/s), 10-way choice 75 ms single / 20 req/s; GPU at 100% (350 W cap); Qwen3.5 linear-attention 528-token cache blocks mean short-state questions do not share prefill[^razorback16-openjev-2026].
- JevK5 differences: text only; reads over 16,384 tokens get 400, never cut; `usage.input_tokens` counts every pass (state re-read per question, as JevK5 does); image sets `VLLM_USE_FLASHINFER_SAMPLER=0` (one greedy token + logprobs only, no CUDA compiler for FlashInfer sampler)[^razorback16-openjev-2026].

## Settings and caveats

- Selected env vars (**reported** in "Settings"; defaults in doc)[^razorback16-openjev-2026]: `OPENJEV_BACKEND` (`vllm` default; `mlx`/`laya`/`verdict`/`clm`/`jevk5`); `OPENJEV_MODEL_ROUTES`, `OPENJEV_FORWARD_TIMEOUT=300`; `OPENJEV_MODEL` (built-in vLLM weights; `Qwen/Qwen3-8B-FP8` for CLM, `alibiserikbay/JevK5` for JevK5); `OPENJEV_GPU_UTIL=0.9` (0.85 for CLM/JevK5), `OPENJEV_MAX_NUM_SEQS=64`, `OPENJEV_MAX_MODEL_LEN=65536` (2048 CLM, 16384 JevK5); `OPENJEV_CANVAS=64`, `OPENJEV_MAX_INFLIGHT=64`, `OPENJEV_MAX_QUEUE=512` (529 beyond), `OPENJEV_MAX_QUESTIONS=256`, `OPENJEV_MAX_BODY_BYTES=64MiB`; `OPENJEV_API_KEY` / `OPENJEV_ORIGIN_SECRET` auth; `OPENJEV_MAX_IMAGES=8`, `OPENJEV_MAX_IMAGE_BYTES=5MiB`; generation `OPENJEV_GEN_MAX_INFLIGHT=8`, `OPENJEV_GEN_MAX_QUEUE=32`, `OPENJEV_GEN_MAX_TOKENS=8192`; `OPENJEV_WARMUP=1`.
- Image pin caveat: build fails if either of two pinned-vLLM changes no longer applies — exact-label-id cap raised 128 to 512 (up to 255 options), and `docker/patches/vision_prefix_lm.py` giving image tokens bidirectional attention per checkpoint config (upstream does it for Gemma4, not yet DiffusionGemma); `clm`/`jevk5` images pin the same commit with neither change[^razorback16-openjev-2026].
- Quality caveat (**reported**): answer quality is DiffusionGemma 26B-A4B quality in this mode — evaluate on own tasks before relying[^razorback16-openjev-2026].
- Live checks: `pip install -e '.[test]' && pytest`; end-to-end `OPENJEV_LIVE_URL=http://127.0.0.1:8080 pytest tests/test_live.py`; MLX `OPENJEV_MLX_TEST_MODEL=path/to/weights pytest tests/test_mlx_model.py`; run live checks after image builds and before cutover[^razorback16-openjev-2026].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) `choice` / `noul` / `score` shapes with `POST /v1/systemone` plus OpenJev-only `images` / `steps` / `samples` / `think` / `sequential` fields.
- Informs [System One Models](system-one-models.md) as the full diffusion-canvas mechanism behind the brief DiffusionGemma-Jev availability note.
- Informs [Classifier Selection](classifier-selection.md) self-hostable diffusion plus small-model routing option versus hosted Jev.
- Uses [Laya Decision Models](laya-decision-models.md) `laya-typed-decisions` checkpoint as routed model `laya-1.0` with the 1,024-token / shared-256-option-token limits above.
- Uses [Contrastive Language Models](contrastive-language-models.md) CLM-v0.1-8B heads as routed model `clm-v0.1` with the FP8/bf16, truncation-from-start, cache-billing, and score-question caveats above.
- Contrasts with [OpenJev Open-Weights Typed Decision Model](openjev-decision-model.md): same "OpenJev" name, different project and mechanism (razorback16 diffusion-canvas server here versus `openjev/openjev` Qwen3.8-27B letter readout there); do not merge accuracy or serving figures.
- Contrasts with [SemIf Open Decisions](semif-open-decisions.md): same former "OpenJev" name, different mechanism (JevK5 letter readout routed here versus no-training direct-logit baseline there); the JevK5 readout used here is SemIf's.
- Contrasts with [OpenJev-SGLang Decision Serving](openjev-sglang-decision-serving.md): different backbone and stack (DiffusionGemma on vLLM/MLX here versus Qwen3.6-35B-A3B on SGLang N+1 readout there).
- Contrasts with [OpenJev NLI Cross-Encoder (AlexWortega)](openjev-nli-cross-encoder.md): same `openjev` name, different project and mechanism (diffusion/encoder routing here versus Qwen3.5 NLI entailment scoring there).

## Coverage limits

- Inspected by static read of the single documentation file `../raw/razorback16-openjev.md` only; no code was executed and no serving run was reproduced — all latency, accuracy/parity, memory, and agreement figures are **reported** project measurements under the stated hardware and flags[^razorback16-openjev-2026].
- Excluded as uninspected: upstream repo code (`openjev/engine.py`, encoders, Dockerfiles, `docker/patches/vision_prefix_lm.py`), linked Hugging Face checkpoints and GitHub repos (DiffusionGemma, Laya, Verdict, CLM, JevK5, SemIf), Codiv hosting, vLLM PR #57250 diff, and CLM PR #6 / issue #3 threads beyond the doc's description[^razorback16-openjev-2026].
- Single-file scope holds no immutable weight revision or capture date; model ids (`openjev-0.1`, `laya-1.0`, `verdict-1.4`, `clm-v0.1`, `jevk5-0.2`), Docker tag `0.5.0`, vLLM commit `1b3b88e`, and the 2026-09-22 merge date are the snapshot anchors — verify flags and limits against the live repo before building[^razorback16-openjev-2026].
- No live credentials, private keys, tokens, or PII were found; the only key-like text is the `sk-codiv-...` / `YOUR_API_KEY`-style placeholder in client examples[^razorback16-openjev-2026].

[^razorback16-openjev-2026]: razorback16, "OpenJev," project documentation, canonical local entry `../raw/razorback16-openjev.md`, upstream `https://github.com/razorback16/openjev`, Docker `razorback16/openjev:0.5.0`. Locators in file: "Models" table; "Try it" SDK/curl; "API" routes, question types, confidence/usage/Server-Timing, errors, Jev differences; "Extensions" fields table plus images curl; "Text generation"; "How it works" canvas diagram, label tokens, entropy-0.1 re-reads, vLLM PR #57250 merged 2026-09-22; "Run your own" backend table; "NVIDIA GPU" compose/run/build, no-Docker vLLM commit `1b3b88e` plus `MAX_LOGPROB_TOKEN_IDS` sed and `vllm serve` flags, RTX PRO 6000 latency tables; "Apple silicon" install/run plus M3 Ultra/M4 Max figures; "MLX memory" pool figures plus `OPENJEV_MLX_CACHE_LIMIT_GB`/`OPENJEV_MLX_PROMPT_CACHE`; "Small encoder models" compose/routes/503/memory table, RTX PRO 6000 encoder table, per-model differences; "CLM" image/compose/GPU-share/FP8-vs-bf16/RTX 3090 table/differences with PR #6 and issue #3; "JevK5" image/compose/GPU-share/JevBench-231 parity/RTX 3090 table/differences; "Settings" env table; "Caveats" two pinned-vLLM changes plus quality warning; "Development" pytest commands; "License" Apache-2.0.
