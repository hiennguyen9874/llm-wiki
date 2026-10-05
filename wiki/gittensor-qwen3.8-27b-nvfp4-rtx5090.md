---
type: Concept
title: Gittensor Qwen3.8-27B NVFP4 RTX 5090
description: Blackwell-optimized NVFP4 checkpoint of Qwen3.8-27B with NVFP4 lm_head, removed MTP head, DSpark v2 drafting, and RTX 5090 serving recipes and benchmarks.
tags: [qwen3.8, nvfp4, quantization, blackwell, rtx-5090, sglang, vllm, sparkinfer, speculative-decoding, dspark]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T14:00:00Z }
stale_after: 2027-04-05
sources:
  - id: qwen38-nvfp4-rtx5090
    resource: ../raw/Qwen3.8-27B-NVFP4-RTX5090.md
    title: RTX5090 Blackwell GPU Optimized Qwen-3.8-27B-NVFP4
---

Gittensor's RTX 5090 build is a Blackwell-specific NVFP4 checkpoint of `Qwen/Qwen3.8-27B` (17.92 GB, 2 shards) that quantizes `lm_head` to NVFP4 and deletes the unused MTP head, serving the full 262,144-token window on 32 GB across SparkInfer, SGLang, and vLLM, with a co-trained DSpark v2 drafter reaching 264.8 tok/s overall (up to 420 on code) in SparkInfer's bench harness and 161.7 tok/s on SGLang's server[^qwen38-nvfp4-rtx5090].

## Checkpoint identity and recipe

- Checkpoint `gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090`; base `Qwen/Qwen3.8-27B`; Apache 2.0; quantized with NVIDIA Model Optimizer at git `c4129b6` (`quant_method: modelopt`)[^qwen38-nvfp4-rtx5090].
- Final build: 17.92 GB in 2 shards (was 18.77 GB / 3 shards); `lm_head` in NVFP4 (0.71 GB vs 2.54 GB BF16); MTP head (~0.85 GB) removed from the weights[^qwen38-nvfp4-rtx5090].
- Precision placement: NVFP4 W4A4 group-size 16 on MLP, `lm_head`, and remaining Linear layers; deliberately BF16 on vision tower, embeddings, and Gated-DeltaNet `conv1d` / `in_proj_a` / `in_proj_b`; FP8 KV cache (`fp8_cast` at PTQ, serve with `--kv-cache-dtype fp8`); calibration on 128 image-text samples (`--calib_with_images`)[^qwen38-nvfp4-rtx5090].
- Tooling note: excluded modules must be listed in two places — `hf_quant_config.json` (`exclude_modules`) and `config.json` (`quantization_config.ignore`) — or loading fails with `Parameter lm_head.input_scale not found`[^qwen38-nvfp4-rtx5090].
- Hardware scope: Blackwell tensor cores only (`sm_120`); Hopper can load the files but cannot run NVFP4[^qwen38-nvfp4-rtx5090].
- Previous builds survive on branches `pre-final` (NVFP4 `lm_head`, MTP still present) and `pre-lmhead4` (BF16 `lm_head`); the standalone `-No-MTP` and `-LMHead4` variants are superseded — this repo now is both[^qwen38-nvfp4-rtx5090].

## Why `lm_head` is NVFP4 and MTP is gone

- At concurrency 1 the model is **Reported** as weight-bandwidth bound, not compute bound: an earlier build streamed 18.80 GiB of weights per token at 81.6 tok/s — a 1.65 TB/s read rate against the RTX 5090's 1.79 TB/s spec (~92% of peak) — so removed bytes convert almost linearly into tokens per second[^qwen38-nvfp4-rtx5090].
- `lm_head` is a full-vocabulary (248,320 × 5,120) GEMM evaluated on every token; embeddings are the same size but a gather (~10 KB/token), so quantizing them saves capacity, not speed[^qwen38-nvfp4-rtx5090].
- The bandwidth model predicted 89.7 tok/s for the NVFP4-`lm_head` build; measured 88.45 — within 1.4%[^qwen38-nvfp4-rtx5090].
- The MTP head was dead weight once the DSpark drafter is in play: the drafter beats MTP by 31.7% on a quarter of the memory (see speculation table), so removing it shrinks download and load-time footprint without touching a computed value[^qwen38-nvfp4-rtx5090].
- Leaving NVFP4 for the next instruction tier costs 1.5–2.1× on these GEMM shapes, so precision spent elsewhere is expensive on this card[^qwen38-nvfp4-rtx5090].

## Cross-engine performance (same weights, RTX 5090)

24 prompts across chat/code/math/JSON, 256 max tokens, `temperature=0`, thinking off, sequential, through each engine's OpenAI API, every row at `--ctx 262144`; SGLang 0.5.18 with FP8 KV, SparkInfer v0.5.5 with default int8 KV[^qwen38-nvfp4-rtx5090].

| Stack | Decode | Max context on 32 GB |
| --- | --- | --- |
| SparkInfer (no speculation) | 92.9 tok/s | 360,000 tokens — 1.37× native window |
| SGLang (no speculation) | 85.8 tok/s | 320,960 tokens — full window with 59K spare |
| SGLang + DSpark v2 | 161.7 tok/s | 165,169 tokens |

- SparkInfer is both faster without speculation and holds more context: 262,144 tokens costs it 27.9 GB; it still answers at `--ctx 360000` (31.2 GB) with decode falling to ~74 tok/s at that extreme[^qwen38-nvfp4-rtx5090].
- Speculation accelerates decode only, never prefill — cold TTFT at 250K is ~121 s either way — so on one 32 GB card you can have the full 262K window or ~1.9× decode[^qwen38-nvfp4-rtx5090].

## Against the other NVFP4 builds (same GPU, same harness)

Three published NVFP4 checkpoints of Qwen3.8-27B on one RTX 5090 — same engine (vLLM), same session, same sampling (model `generation_config`: temp 1.0, top_k 20, top_p 0.95), same 32,768-token budget[^qwen38-nvfp4-rtx5090].

| | This build | QUASAR | NVIDIA |
| --- | ---: | ---: | ---: |
| GPQA Diamond (198) | 76.3% | 78.8% | 76.8% |
| AIME 2025 (30) | 76.7% | 76.7% | 76.7% |
| MMLU-Pro (100) | 85.0% | 84.0% | 83.0% |
| Overall (328) | 79.0% | 80.2% | 78.7% |
| 95% CI | [74.2–83.0] | [75.5–84.1] | [73.9–82.7] |
| AA-LCR (100 q @ ~95K tok) | 55 | 55 | 55 |
| Decode | 86.8 tok/s | 78.5 | 69.5 |
| KV @ 131,072 ctx | 300,009 | 249,036 | 209,715 |
| Checkpoint | 17.92 GB | 19.7 GB | 21.0 GB |

- Quality is a tie (all confidence intervals overlap; truncation 41/45/42 comparable); the difference is what the weights leave room for: 24.9% faster with 43% more context than NVIDIA's official checkpoint[^qwen38-nvfp4-rtx5090].
- Allocation, not luck: NVIDIA keeps self-attention and Gated-DeltaNet at FP8 (22% of linear weight), costing decode bandwidth and KV headroom on this card — their target is GB300, where FP8 sits closer to FP4 in relative cost; QUASAR keeps `lm_head` in BF16[^qwen38-nvfp4-rtx5090].
- Caveats preserved: published BF16 references disagree across harnesses (NVIDIA 88.92 vs QUASAR 91.41 on GPQA Diamond for the same weights), so only these same-harness numbers compare with each other, never against a leaderboard; AA-LCR here uses a deterministic salient-token proxy applied identically to all three, not Artificial Analysis' LLM judge[^qwen38-nvfp4-rtx5090].

## Against the other NVFP4 builds on the same GPU (serving view)

This build vs RadixArk DSpark vs Unsloth NVFP4; this build and RadixArk measured back to back on identical SGLang flags (FP8 KV, `--mm-feature-transport cpu`, 2 running requests) at `--ctx 262144`; Unsloth figures are an earlier vLLM measurement on the same GPU — a different engine, included for scale[^qwen38-nvfp4-rtx5090].

| | This build | RadixArk DSpark | Unsloth NVFP4 |
| --- | --- | --- | --- |
| Max context, SGLang | 320,960 | 225,600 | 77,184 (vLLM) |
| Max context, SparkInfer | 360,000 | does not load | not tested |
| Full native window | yes | no | no |
| Decode, no speculation | 85.8 SGLang · 92.9 SparkInfer | 73.7 tok/s | 42.4 tok/s |
| Decode + own drafter | 161.7 tok/s | 148.0 tok/s | — |
| Max context with speculation | 165,169 | 37,900 | — |

- RadixArk's drafter is BF16 (3.5 GB vs 1.41 GB) with its draft KV pool sized to the full target context, so speculation costs it most of its window; RadixArk does not load on SparkInfer at all — its Gated-DeltaNet projections (`linear_attn.in_proj_qkv`, `in_proj_z`, `out_proj`) are rejected by the compressed-tensors loader as malformed FP8 — while this checkpoint runs on all three engines unmodified[^qwen38-nvfp4-rtx5090].

## Concurrency and prefix reuse

- Single-stream figures above; under concurrent load SparkInfer v0.5.5 decodes the whole batch in one packed forward (earlier versions time-sliced one sequence at a time, flat ~77 tok/s)[^qwen38-nvfp4-rtx5090].

| Concurrent requests | 1 | 2 | 4 | 8 | 16 | 32 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Aggregate tok/s | 88.9 | 162.1 | 249.6 | 344.3 | 345.1 | 318.2 |
| Per request | 88.9 | 81.1 | 63.0 | 43.7 | 22.0 | 13.4 |

- Distinct prompts per request, 128 tokens each, `--ctx 40960`, client-side over streaming API; 32/32 succeeded at every level; aggregate peaks around 8–16 and is flat to 32, so 8 is the sweet spot on one card[^qwen38-nvfp4-rtx5090].
- Where this loses: vLLM 0.28 on the same weights/box/harness does 134.5 / 266.6 / 545.8 / 546.6 tok/s at 2/4/8/16 — this stack leads at 2 concurrent and trails ~1.6× at 8–16, so vLLM is still the faster server for many simultaneous users while SparkInfer leads on one or few streams and holds far more context[^qwen38-nvfp4-rtx5090].
- Repeated long prefixes (~19×): a configured prefix file (`SPARKINFER_SERVER_PREFIX_TOKEN_FILE`, token ids kept warm across requests — not automatic caching, sequential requests only) turns a 32,022-token shared prefix from 5.75 s cold to 0.30 s warm; changing one word costs 3.30 s again, attributing the gain to the cache rather than warm-up[^qwen38-nvfp4-rtx5090].

## Speculative decoding (DSpark v2)

DSpark drafters trained and quantized against this NVFP4 checkpoint: recommended `gittensor-model-hub/Qwen3.8-27B-DSpark-NVFP4` (1.41 GB) and BF16 source `...-RTX5090-DSpark` (2.72 GB); the v2 drafter is retrained on a corpus rendered as served (XML tool calls with a real tools array, think blocks, reasoning-effort preamble), closing a train/serve mismatch that had cost most on agentic traffic[^qwen38-nvfp4-rtx5090].

240-prompt held-out harness (longer outputs, own settings — not comparable to the 24-prompt cross-engine figures; each set is internally consistent)[^qwen38-nvfp4-rtx5090]:

| Profile | Decode | Accept length | Drafter | vs no-spec |
| --- | --- | ---: | ---: | ---: |
| No speculation | 88.45 tok/s | — | — | 1.00× |
| Built-in MTP head | 136.90 tok/s | 2.758 | 5.53 GB | 1.68× |
| Stock RadixArk DSpark (FP8-trained) | 139.35 tok/s | 2.421 | 2.72 GB | 1.71× |
| Ours DSpark BF16 | 141.99 tok/s | 2.717 | 2.72 GB | 1.74× |
| Ours DSpark NVFP4 (v1) | 150.74 tok/s | 2.761 | 1.41 GB | 1.85× |
| Ours DSpark NVFP4 (v2) | 180.30 tok/s | 2.904 | 1.41 GB | 2.04× |

SparkInfer bench-harness pairing (bench only, not the HTTP server — ratio transfers, not absolute tok/s; bench baseline 97.1 vs server 92.9, one prompt per workload vs six)[^qwen38-nvfp4-rtx5090]:

| Workload | Autoregressive | + DSpark | Speedup | Accept τ |
| --- | --- | --- | ---: | ---: |
| Chat | 96.7 tok/s | 174.4 tok/s | 1.80× | 2.32 |
| Code | 97.2 tok/s | 420.2 tok/s | 4.32× | 6.78 |
| Math | 96.6 tok/s | 276.5 tok/s | 2.86× | 4.36 |
| JSON | 97.8 tok/s | 296.4 tok/s | 3.03× | 4.60 |
| Overall | 97.1 tok/s | 264.8 tok/s | 2.73× | — |

- Against SGLang's 1.89× on the same drafter, the larger SparkInfer gain comes from a verifier that keeps up with the block drafter; code accepts nearly the whole 8-token block (τ 6.78 of 8)[^qwen38-nvfp4-rtx5090].
- Speculation is lossless by construction (target verifies every drafted token): 9 of 12 bench runs token-identical to baseline; the 3 differing runs diverged at a single token then followed a different but valid continuation — a near-tie in target logits exposed by a different GEMM shape in verify vs single-token decode[^qwen38-nvfp4-rtx5090].
- Per-domain acceptance gains v1 → v2: math +18.0%, coding +3.6%, JSON/structured +6.5%, chat +2.5%, instruction +6.1%, overall +5.2%; long-context −0.4% (training caps at 2,048 tokens, never well represented); structured output sustains longer blocks than prose[^qwen38-nvfp4-rtx5090].
- Agentic tool calling (60 purpose-built scenarios, 10 tool schemas; the JSON row above is schema-constrained generation without tools, not agentic use): overall 3.299 → 3.891 (+17.9%), with parallel calls +24.7% and initial calls +27.4%; tool-call emission unchanged (38/60 both), so this is an acceptance gain, not a behavior change; output quality unchanged under strict acceptance[^qwen38-nvfp4-rtx5090].

## Accuracy smokes

- Quantizing `lm_head` and dropping MTP did not move quality on a matched 60-item smoke (GPQA/AIME/MMLU-Pro, 20 each, thinking on, `temperature=1.0`, seed 20260815): SparkInfer 41/60 (16k output budget) vs SGLang 40/60 (24k budget) — read as same weights, same accuracy, not an engine ranking; budgets differ because SparkInfer caps output per request; 6–9 length truncations per task[^qwen38-nvfp4-rtx5090].
- Earlier vLLM measurement on the previous build stands at 45/60 (75%) for both this line and Unsloth NVFP4 (GPQA 13/20 vs 14/20, AIME 15/20 vs 14/20, MMLU-Pro 17/20 tied)[^qwen38-nvfp4-rtx5090].
- Explicit source warning: these are 20-item smokes, not publishable benchmark scores — do not cite them as GPQA/AIME/MMLU-Pro results[^qwen38-nvfp4-rtx5090].

## Serving

SparkInfer one-command path (prebuilt GHCR image, zero-dependency C++/CUDA, ~1 GB, `sm_120` only; weights self-download ~18 GB on first run; ready ~10 s later; OpenAI-compatible text/image/video API)[^qwen38-nvfp4-rtx5090]:

```bash
docker run --gpus all -p 8080:8080 -v qwen38:/models \
  ghcr.io/gittensor-ai-lab/sparkinfer-qwen38:latest
```

```bash
curl localhost:8080/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model": "qwen38-nvfp4",
  "messages": [{"role": "user", "content": "What is the capital of Japan?"}],
  "chat_template_kwargs": {"enable_thinking": false}
}'
```

- Tuning env: `CTX=262144` default (full native window, 27.9 GB; 360,000 ceiling at 31.2 GB with decode ~74 tok/s); `SPARKINFER_MAX_OUTPUT_TOKENS=16384` (engine default 4096 — raising it without raising `CTX` fails concurrent requests with *server overloaded*); `MODEL_DIR`, `MODEL_NAME`/`PORT`, `SPARKINFER_SERVER_PREFIX_TOKEN_FILE`; NVFP4 `lm_head` loads natively[^qwen38-nvfp4-rtx5090].
- Caveat: `/v1/models` advertises `input_modalities` text+image only, so agent frameworks routing on that field will not offer video even though `video_url` parts work — send video explicitly (sparkinfer#983); provenance attested to image digest via `gh attestation verify`[^qwen38-nvfp4-rtx5090].
- Bench: `docker run --rm --gpus all --ipc=host -v qwen38:/models ghcr.io/gittensor-ai-lab/sparkinfer-qwen38:latest bench code` (fetches drafter on first use; DSpark path is bench-harness only — use SGLang for speculation over HTTP)[^qwen38-nvfp4-rtx5090].
- From source: `cmake -B build -DCMAKE_CUDA_ARCHITECTURES=120 -DBUILD_SERVER=ON && cmake --build build -j`, then `sparkinfer_server -m <weights> --tokenizer <weights>/tokenizer.json --ctx 262144`; needs CUDA 12.8+ and rustc ≥ 1.79[^qwen38-nvfp4-rtx5090].

SGLang with speculation (fastest HTTP path; drop the four `--speculative-*` lines for the maximum-context profile)[^qwen38-nvfp4-rtx5090]:

```bash
docker run -d --name sgl --gpus all --ipc=host --shm-size 32g -p 30000:30000 \
  -v hf_cache:/root/.cache/huggingface \
  lmsysorg/sglang:latest \
  sglang serve \
    --model-path gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090 \
    --trust-remote-code --tp-size 1 \
    --context-length 262144 \
    --kv-cache-dtype fp8_e4m3 \
    --attention-backend flashinfer \
    --chunked-prefill-size 2048 \
    --mamba-radix-cache-strategy extra_buffer_lazy \
    --mamba-ssm-dtype bfloat16 \
    --mem-fraction-static 0.90 \
    --max-running-requests 2 \
    --max-mamba-cache-size 12 \
    --speculative-algorithm DSPARK \
    --speculative-draft-model-path gittensor-model-hub/Qwen3.8-27B-DSpark-NVFP4 \
    --speculative-dspark-block-size 7 \
    --speculative-draft-model-quantization modelopt_fp4 \
    --reasoning-parser qwen3 \
    --tool-call-parser qwen3_coder \
    --host 0.0.0.0 --port 30000
```

- `--speculative-draft-model-quantization modelopt_fp4` is required — without it SGLang assumes BF16 and mis-loads packed U8 tensors; `--max-mamba-cache-size` must leave headroom (each DSpark request takes 4 Gated-DeltaNet state slots; size 4 provisions exactly one request and eviction can fail with `AssertionError: Can not alloc mamba cache`; rule ≥ 4 × `--max-running-requests` + 4)[^qwen38-nvfp4-rtx5090].

vLLM 0.27.x[^qwen38-nvfp4-rtx5090]:

```bash
vllm serve gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090 \
  --quantization modelopt \
  --kv-cache-dtype fp8 \
  --trust-remote-code \
  --max-model-len 262144 \
  --max-num-seqs 16 \
  --gpu-memory-utilization 0.97 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml
```

- First boot JITs the FlashInfer SM120 FP4 GEMM (`nvcc` + CUDA 13 headers; limit with `MAX_JOBS=2` on small host RAM); utilization 0.97 required for native 256K on 32 GB (0.90 holds only ~205K KV); thinking model — pass `enable_thinking: false` for short answers[^qwen38-nvfp4-rtx5090].

## Chat template

- Qwen3.8's own template with agentic fixes; renders byte-identical to upstream `Qwen/Qwen3.8-27B` on every non-tool path[^qwen38-nvfp4-rtx5090].
- Reasoning effort `xhigh` (default) / `medium` / `low` via `{"chat_template_kwargs": {"reasoning_effort": "medium"}}`; invalid values raise; `xhigh` is cheapest at equal accuracy — 12/12 correct on 12 verifiable problems (`temperature=0`, 3k budget, no truncations) with 245 vs 584/579 avg output tokens, holding on a harder 10-problem set (562 vs 939)[^qwen38-nvfp4-rtx5090].
- Tool calling is XML by default, matching `qwen3_xml` (vLLM) and `qwen3_coder` (SGLang) parsers; assistant `tool_calls` replayed from OpenAI-style responses render whether `function.arguments` is a dict or JSON string — the string form previously raised `TypeError: Can only get item pairs from a mapping` on second-turn agentic loops for direct `apply_chat_template`/llama.cpp/LM Studio users (server-side calling never affected — SGLang/vLLM normalize to dict first)[^qwen38-nvfp4-rtx5090].
- Kwargs: `reasoning_effort` (default `xhigh`), `enable_thinking` (default true; false emits closed empty think block), `preserve_thinking` (default true; false is prefix-cache safe), `tool_call_format` (`xml`/json), `continue_final_message` (prefills final turn, precedence over `add_generation_prompt`), `auto_disable_thinking_with_tools`, `max_tool_arg_chars`/`max_tool_response_chars` (opt-in truncation, off by default); `system` and `developer` roles accepted; consecutive tool responses grouped into one turn[^qwen38-nvfp4-rtx5090].
- Validation: 8/8 agent correctness (selection, arguments, parallel calls, no-tool restraint, synthesis, multi-step, failure recovery, tools-with-thinking-off); 240 held-out conversations render clean; multi-turn prompts token-level prefix-stable (KV reuse holds); paired A/B vs previous template left DSpark acceptance unchanged to slightly better; template contributions from `@TheChola`[^qwen38-nvfp4-rtx5090].

## Relationships

- Uses [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — this checkpoint's 1.89× SGLang-server and 2.73× SparkInfer-harness gains are DSpark block-drafting instances with block size 7.
- Uses [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — same Blackwell W4A4 serving shape and ModelOpt FP4 family, here a full NVFP4 `lm_head` plus removed MTP head rather than per-layer dynamic retention.
- Uses [NVFP4 Format and Scale-Dependent Accuracy](nvfp4-format-accuracy-scale.md) — the accuracy-tie vs QUASAR/NVIDIA under the same harness is NVFP4-format evidence with allocation (FP8 attention, BF16 head) as the differentiator.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base served here as a single-card Blackwell NVFP4 server build rather than Unsloth GGUF/NVFP4 local inference.
- Related to [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) — sibling server-side speculation path: the v2 NVFP4 drafter here (1.41 GB, trained against this target) is adapted from the stock RadixArk DSpark drafter covered there.
- Related to [NInfer Single-GPU Inference Engine](ninfer-single-gpu-inference-engine.md) — fellow single-RTX-5090 narrow engine: SparkInfer leads one/few streams with far more context here while vLLM leads at 8–16 concurrent.
- Related to [Qwen3.8-27B Community Variants](qwen3.8-27b-community-variants.md) — community NVFP4/speculative variant survey for the same 27B base.

## Contradictions

- No internal contradiction: the 92.9/85.8/161.7 cross-engine figures and the 88.45/150.74/180.30 held-out speculation figures come from different harnesses the source marks not comparable — preserved as two internally consistent sets[^qwen38-nvfp4-rtx5090].
- Published BF16 references for the same weights disagree (NVIDIA 88.92 vs QUASAR 91.41 on GPQA Diamond), so same-harness comparisons above must not be set against leaderboards[^qwen38-nvfp4-rtx5090].
- Engine choice trades off by load: SparkInfer leads at 1–2 concurrent streams with larger context; vLLM 0.28 leads ~1.6× at 8–16 concurrent on the same weights — neither is universally faster[^qwen38-nvfp4-rtx5090].

## Coverage limits

- Single-file model card inspected statically; no command was executed, so every performance, accuracy, VRAM, and context figure is **Reported** under the card's stated harnesses, not independently verified.
- Hero/benchmark PNGs referenced under `assets/` are absent from `raw/` and excluded as decorative — material numbers are carried by the card's tables, preserved above.
- External checkpoints (QUASAR, NVIDIA, Unsloth, RadixArk drafters/targets), engines (SparkInfer v0.5.5, SGLang 0.5.18, vLLM 0.27/0.28), ModelOpt `c4129b6`, `pre-final`/`pre-lmhead4` branches, and superseded `-No-MTP`/`-LMHead4` variants were not inspected.
- Launch flags, memory fractions, batch caps, chunked-prefill sizes, and the mamba-cache rule are snapshot values for the stated versions; `stale_after` above covers them per the serving domain rule.

[^qwen38-nvfp4-rtx5090]: RTX5090 Blackwell GPU Optimized Qwen-3.8-27B-NVFP4 — `../raw/Qwen3.8-27B-NVFP4-RTX5090.md` (HF model card: checkpoint/recipe, bandwidth rationale, cross-engine and three-build and RadixArk/Unsloth comparisons, concurrency and prefix tables, DSpark v2 per-domain/agentic tables, 60-item smokes, SparkInfer/SGLang/vLLM serving commands, chat-template kwargs and validation).
