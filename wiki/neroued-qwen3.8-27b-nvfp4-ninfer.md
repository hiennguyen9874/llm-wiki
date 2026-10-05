---
type: Concept
title: Neroued Qwen3.8-27B NVFP4 NInfer Artifact
description: Mixed NVFP4/FP8 NInfer artifact for Qwen3.8-27B with DFlash2 companion weights, RTX 5090 serving recipes, and reported MTP performance and EvalScope fidelity.
tags: [qwen3.8, nvfp4, ninfer, quantization, blackwell, rtx-5090, serving, speculative-decoding, mtp, dflash2]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T22:00:00Z }
stale_after: 2027-04-05
sources:
  - id: qwen38-nvfp4-ninfer
    resource: ../raw/Qwen3.8-27B-nvfp4-NInfer.md
    kind: documentation
    title: Qwen3.8-27B NVFP4 for NInfer
---

This `neroued/Qwen3.8-27B-nvfp4-NInfer` artifact is the NInfer-only mixed NVFP4/FP8 packaging of `Qwen/Qwen3.8-27B`, combining the official BF16 checkpoint with fixed packed Text weights from `unsloth/Qwen3.8-27B-NVFP4` in the native `.ninfer` container, with reported RTX 5090 MTP serving throughput, long-context prefill/decode tables, and EvalScope fidelity within ±2.5 points of the official BF16 card on four overlapping benchmarks[^qwen38-nvfp4-ninfer]. It is not a Transformers, Safetensors, or GGUF distribution and runs only under NInfer on one RTX 5090[^qwen38-nvfp4-ninfer].

## Artifact identity and precision placement

- File `qwen3_8_27b_nvfp4.ninfer`: 23,719,715,844 bytes (22.09 GiB), SHA-256 `74d2c57145e6ff11d1d2faa79594477f9bc903a611af1fb20218189fbbb77d82`, container version 3, architecture `Qwen3_5ForCausalLM`, public model name `qwen3.8-27b`[^qwen38-nvfp4-ninfer].
- Chat template `qwen3_8.jinja` with override `--chat-template FILE`; defaults are thinking on, effort `xhigh`, closed-turn reasoning retained[^qwen38-nvfp4-ninfer].
- Stored objects 1,246 (1,240 tensors and 6 resources): 112 NVFP4 tensors and 146 row-scaled FP8 tensors[^qwen38-nvfp4-ninfer].
- Uses the Qwen3.5 Dense architecture: Text layers 0–55 use NVFP4 MLP weights, while token embedding, attention input/output projections, GDN Q/K/V/Z and output projections, full output head, and Text layers 56–63 MLP weights use row-scaled FP8; control weights use BF16 with separate MTP, Vision, and DFlash2 weights[^qwen38-nvfp4-ninfer].
- Contains Text, Vision, MTP, DFlash2, the optimized proposal head, and frontend resources; Vision and speculative weights load only when selected at startup[^qwen38-nvfp4-ninfer].
- Source-derived NVFP4 and FP8 words are preserved without decode and requantization; only the official BF16 token embedding is encoded locally as row-scaled FP8[^qwen38-nvfp4-ninfer].
- Verify a download with[^qwen38-nvfp4-ninfer]:

```bash
printf '%s  %s\n' \
  '74d2c57145e6ff11d1d2faa79594477f9bc903a611af1fb20218189fbbb77d82' \
  'qwen3_8_27b_nvfp4.ninfer' | sha256sum --check
```

- Includes complete DFlash2 companion weights from `z-lab/Qwen3.8-27B-DFlash2` at revision `50307d4c4cde6860d4eee73e2547cd786fe8e8a4`; select `--spec dflash2 --draft-tokens 7 --lm-head-draft` with draft counts 1–15 supported, and DFlash2 requires the runtime revision listed below while existing performance and evaluation tables retain their stated MTP configurations and revisions[^qwen38-nvfp4-ninfer].

## Requirements and provenance

- **Evidence class:** **Observed** for stated requirements and revisions (static card inspection, no execution); **Reported** for all throughput and accuracy figures below[^qwen38-nvfp4-ninfer].
- Requires NInfer revision `04350ba9` (linked commit `98dada0e03cb073fd07f905400b5904bc6e82759`) or later built from source, 64-bit Linux, NVIDIA GeForce RTX 5090 (`sm_120a`), and CUDA Toolkit 13.1 or newer; NInfer provides no install target or packaged binary[^qwen38-nvfp4-ninfer].
- Holders of the official v2 file upgrade locally without re-downloading weights via the weight-conversion doc; the exact storage contract is in the v3 container reference and the artifact identity plus conversion provenance are published in `artifact-manifest.json`[^qwen38-nvfp4-ninfer].
- Provenance: base `Qwen/Qwen3.8-27B` revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` downloaded from `modelscope.cn/models/Qwen/Qwen3.8-27B`; quantized source `unsloth/Qwen3.8-27B-NVFP4` revision `60e813d4dbbdc5d64cf3f5a8caf2897bedf03679`; conversion recipe `qwen3_8_27b_nvfp4` with embedding encoder `fp8_row_maxabs`; converter and minimum runtime `https://github.com/Neroued/ninfer` at `98dada0e03cb073fd07f905400b5904bc6e82759`; ranking input SHA-256 `c692dc76388132c910547589b4fb4a0503fbd6ad50aaac6a509bbcb192a8afa5`[^qwen38-nvfp4-ninfer].
- License: this artifact, the base repository, and the quantized source repository are each Apache-2.0; users remain responsible for license and legal compliance[^qwen38-nvfp4-ninfer].

## Run recipes

- CLI text example (32,768-token allocation, up to 8,192 new tokens, FP8 KV, MTP with 3 draft tokens)[^qwen38-nvfp4-ninfer]:

```bash
hf download neroued/Qwen3.8-27B-nvfp4-NInfer \
  qwen3_8_27b_nvfp4.ninfer \
  --local-dir models

./build/apps/ninfer models/qwen3_8_27b_nvfp4.ninfer \
  --prompt "Explain prefill and decode in three sentences." \
  --max-context 32768 \
  --max-new 8192 \
  --kv-dtype fp8 \
  --spec mtp --draft-tokens 3 \
  --lm-head-draft
```

- Image, video, and structured chat history follow the CLI guide; flags and APIs are snapshot values for the stated NInfer revisions and fall under `stale_after` above[^qwen38-nvfp4-ninfer].
- Local server example with a 240,000-token logical ceiling per request, shared 240,000-token Device KV pool, two active requests when combined completion reservations fit, either request able to use the full pool alone, plus two extra Device checkpoint slots, eight pinned Host State slots, and 8 GiB pinned Host KV for reusable continuations under pressure[^qwen38-nvfp4-ninfer]:

```bash
./build/apps/ninfer-serve models/qwen3_8_27b_nvfp4.ninfer \
  --host 127.0.0.1 \
  --port 8080 \
  --max-context 240000 \
  --kv-capacity 240000 \
  --max-concurrency 2 \
  --kv-dtype fp8 \
  --device-state-slots 2 \
  --host-state-slots 8 \
  --host-kv-mib 8192 \
  --spec mtp --draft-tokens 3 \
  --lm-head-draft \
  --preserve-thinking
```

- Cache and admission semantics follow the resource-scheduling reference; the API surface follows the HTTP serving guide[^qwen38-nvfp4-ninfer].

## Supported use

- Text generation in thinking and non-thinking modes; image, multi-image, video, and mixed multimodal messages[^qwen38-nvfp4-ninfer].
- MTP speculative decoding with draft windows 1–5; DFlash2 with draft windows 1–15 using the included companion weights[^qwen38-nvfp4-ninfer].
- BF16, INT8, FP8, NVFP4, and K8V4 KV cache; CUDA Graph decode and compatible-prefix reuse; startup-bounded small-scale concurrent serving with true batched decode; NInfer CLI; OpenAI Responses Core, OpenAI Chat Completions, and Anthropic Messages serving[^qwen38-nvfp4-ninfer].

## Reported performance (one RTX 5090)

- **Evidence class:** **Reported** — measured September 28–29, 2026 with NInfer revision `7f6aafed`, one RTX 5090, driver 617.14, CUDA 13.4 compile/runtime/driver API, FP8 E4M3 row-256 KV, CUDA Graphs, 1,024-token prefill chunk, disabled prefix reuse, temperature 0.6 / top-p 0.95 / top-k 20 / min-p 0 / presence penalty 1.0 / frequency penalty 0; MTP0 has a 262,144-token context ceiling while MTP3 uses 131,072 tokens per request, three draft tokens, the optimized proposal head, and automatic shared KV capacity; per the SCOPE benchmark rule these are vendor-style serving runs, not cross-engine benchmarks[^qwen38-nvfp4-ninfer].
- Concurrent MTP=3 corpus makespan: each C is one complete 75-request corpus with three reasoning and twelve cross-scenario fixtures, five seeds per fixture, and fixed shuffled send order; makespan includes prefill, decode, admission waits, transitions, and drain while actual output lengths vary[^qwen38-nvfp4-ninfer]:

| C | Requests | Computed prefill tokens | Decode tokens | Makespan (s) | Requests/s | Corpus prefill (tok/s) | Corpus decode (tok/s) | Avg batch | MTP acceptance |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 75 | 15,460 | 693,701 | 4,115.22 | 0.0182 | 3.8 | 168.6 | 1.00 | 59.6% |
| 2 | 75 | 15,460 | 709,989 | 2,394.23 | 0.0313 | 6.5 | 296.5 | 1.90 | 58.9% |
| 4 | 75 | 15,460 | 722,202 | 1,640.17 | 0.0457 | 9.4 | 440.3 | 3.13 | 58.5% |
| 8 | 75 | 15,460 | 708,589 | 1,443.37 | 0.0520 | 10.7 | 490.9 | 3.52 | 59.5% |

- All 300 requests completed without request, CUDA, or allocation errors; automatic KV capacity is 131,072 / 262,144 / 253,632 / 225,024 tokens at C=1/2/4/8; C=8 averages batch 3.52 with up to five waiting requests in sampled intervals; resident MTP3 weights occupy 19.729 GiB with a 243.3 MiB workspace arena[^qwen38-nvfp4-ninfer].
- Long-context serving with MTP disabled (mean ± sample SD over five fixed seeds per fixture)[^qwen38-nvfp4-ninfer]:

| Prompt tokens | Samples | Prefill phase (tok/s) | Server TTFT (ms) | Decode phase (tok/s) |
|---:|---:|---:|---:|---:|
| 7,680 | 5 | 12,819.1 ± 16.8 | 602.7 ± 1.1 | 74.1 ± 0.3 |
| 64,512 | 5 | 8,658.2 ± 44.8 | 7,487.4 ± 37.7 | 68.2 ± 0.2 |
| 130,048 | 5 | 6,198.5 ± 19.6 | 21,055.7 ± 67.2 | 62.5 ± 0.3 |
| 260,096 | 5 | 4,016.4 ± 10.4 | 64,910.0 ± 171.8 | 53.4 ± 0.6 |

- MTP=3 single-request long-reasoning decode from the C=1 corpus, five samples per fixture[^qwen38-nvfp4-ninfer]:

| Fixture | Samples | Completion tokens | Decode phase (tok/s) | MTP3 acceptance | MTP3 tokens/round |
|---|---:|---:|---:|---:|---:|
| `long_decode_aime26_01` | 5 | 1,559.4 ± 727.2 | 207.4 ± 3.6 | 77.2% ± 1.8% | 3.32 ± 0.05 |
| `long_decode_aime26_15` | 5 | 65,536.0 ± 0.0 | 161.7 ± 3.8 | 57.2% ± 2.1% | 2.72 ± 0.06 |
| `long_decode_aime26_30` | 5 | 37,978.0 ± 7,474.4 | 170.0 ± 2.3 | 59.9% ± 1.5% | 2.80 ± 0.05 |

- MTP=3 single-request cross-scenario decode, each category pooling three fixtures × five seeds[^qwen38-nvfp4-ninfer]:

| Category | Samples | Decode phase (tok/s) | MTP3 acceptance | MTP3 tokens/round |
|---|---:|---:|---:|---:|
| Code | 15 | 205.3 ± 9.5 | 76.8% ± 5.1% | 3.30 ± 0.15 |
| Story | 15 | 132.6 ± 13.1 | 37.6% ± 7.1% | 2.13 ± 0.21 |
| Translation | 15 | 202.9 ± 12.3 | 75.2% ± 6.6% | 3.26 ± 0.20 |
| Structured | 15 | 231.7 ± 10.6 | 90.6% ± 5.6% | 3.72 ± 0.17 |

- All five AIME 15 samples reach the 65,536-token output budget; the C=1 corpus contains 40 stop-token and 35 output-limit results retained in statistics; these measurements do not score answer accuracy or task completion; full results and reproduction commands also cover DFlash2 K=7, MTP3 decode saturation, and completion outcomes[^qwen38-nvfp4-ninfer].

## Reported evaluation

- **Evidence class:** **Reported** — evaluated through NInfer's OpenAI-compatible serving route with thinking enabled, MTP=3, INT8 group-64 KV, EvalScope 1.9.0 0-shot rule-based scoring with one sample per problem at temperature 1.0, top-p 0.95, top-k 20, presence penalty 0.0, seed 42; text suite at 252,928-token context limit and multimodal suite with `--vision` at 81,920-token limit; treat as vendor benchmark evidence with no independent check here[^qwen38-nvfp4-ninfer]:

| Benchmark | NInfer NVFP4 | Correct / total | Official Qwen3.8-27B BF16 |
|---|---:|---:|---:|
| IFBench (prompt-level strict) | 77.00% | 231 / 300 | 79.5 |
| AIME 2025 | 96.67% | 29 / 30 | — |
| AIME 2026 | 96.67% | 29 / 30 | — |
| GPQA-Diamond | 90.40% | 179 / 198 | 89.2 |
| ERQA | 66.25% | 265 / 400 | 65.5 |
| RealWorldQA | 83.53% | 639 / 765 | 85.9 |

- All 1,723 configured samples completed and were scored; IFBench additionally reports 80.50% instruction-level strict, 80.33% prompt-level loose, and 83.50% instruction-level loose; these are single-sample results, not pass@k[^qwen38-nvfp4-ninfer].
- The official BF16 figures come from the upstream model card whose sampling settings and IFBench metric level are unstated, so the last column is not a same-protocol comparison; NVFP4 deltas stay within ±2.5 points on the four overlapping benchmarks and the upstream card reports no AIME results[^qwen38-nvfp4-ninfer].

## Limits

- NInfer executes on one RTX 5090 and one CUDA device with startup-fixed capacity of 1–8 active requests per Engine[^qwen38-nvfp4-ninfer].
- No large-scale or preemptive continuous batching, priority/QoS scheduling, multi-GPU execution, CPU/GPU offload, or distributed serving; context allocation is subject to GPU memory and selected KV-cache type; NInfer does not execute generated tool calls[^qwen38-nvfp4-ninfer].

## Relationships

- Depends on [NInfer Single-GPU Inference Engine](ninfer-single-gpu-inference-engine.md) — this is the per-artifact model card behind that engine page's Qwen3.8-27B NVFP4 row: v3 container, RTX-5090-only `sm_120a` build, MTP 1–5 plus DFlash2 1–15 paths, and the EvalScope capability figures.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — the Unsloth GGUF/NVFP4 local route for the same 27B base served here as a single-card NInfer artifact rather than llama.cpp or vLLM inference.
- Uses [NVFP4 Format and Scale-Dependent Accuracy](nvfp4-format-accuracy-scale.md) — the 4-bit weight format behind the layers 0–55 NVFP4 MLP placement and the ±2.5-point BF16 fidelity comparison.
- Uses [Speculative Decoding Foundations](speculative-decoding-foundations.md) — the draft-verify-accept mechanism behind the MTP 59–91% acceptance and tokens-per-round figures reported here.
- Uses [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — the DFlash2 companion weights and 1–15 draft-window path included in this artifact.
- Related to [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) — sibling server-side speculation path for the same 27B base, distinct from the MTP/DFlash2 paths bundled here.
- Related to [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — the `unsloth/Qwen3.8-27B-NVFP4` packed Text weights fixed into this artifact without decode and requantization.

## Coverage limits

- Only `../raw/Qwen3.8-27B-nvfp4-NInfer.md` was inspected statically; no commands were executed, so every throughput and accuracy figure stays **Reported** under the card's stated harness and revisions.
- Linked entry points and attachments named in the source but absent from `raw/` were not inspected: Hugging Face pages (`neroued/...`, `Qwen/...`, `unsloth/...`, `z-lab/...-DFlash2`), `artifact-manifest.json`, `qwen3_8.jinja` chat template, NInfer repository revisions and docs (README, CLI, serving, performance, methodology, weight-conversion, resource-scheduling, artifact-container references), EvalScope 1.9.0, and the upstream Qwen3.8-27B model card used for the BF16 column.
- The minimum-runtime line names revision `04350ba9` while linking commit `98dada0e03cb073fd07f905400b5904bc6e82759`; both values are preserved as written without resolving which one governs.
- Launch flags, memory fractions, context ceilings, and KV-capacity behavior are snapshot values for the stated NInfer revisions and GPU/driver/CUDA combination; `stale_after` above covers them per the serving domain rule.
- No sensitive values found.

[^qwen38-nvfp4-ninfer]: Qwen3.8-27B NVFP4 for NInfer — `../raw/Qwen3.8-27B-nvfp4-NInfer.md` (HF model card with frontmatter `model-index` EvalScope scores; sections Artifact, Requirements, Download/CLI, Server, Supported use, Performance with MTP=3 corpus/long-context/long-reasoning/cross-scenario tables, Evaluation with correct/total plus BF16 column, Limits, Provenance, License).
