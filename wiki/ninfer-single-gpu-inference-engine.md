---
type: Concept
title: NInfer Single-GPU Inference Engine
description: From-scratch C++/CUDA engine serving Qwen3.6/3.8 checkpoints on one RTX 5090 with MTP/DFlash speculation and prefix reuse.
tags: [serving, speculative-decoding, quantization, qwen, long-context]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T12:00:00Z }
stale_after: 2027-04-05
sources:
  - id: ninfer-readme
    resource: ../raw/ninfer.md
    kind: documentation
    title: NInfer
---

NInfer is a from-scratch C++/CUDA inference engine for Qwen3.5 Dense and MoE architectures on a single NVIDIA GeForce RTX 5090, serving text, image, and video prompts through a local CLI or OpenAI-/Anthropic-compatible HTTP APIs with one resident model and one to eight execution lanes fixed at startup[^ninfer-readme]. All throughput and capability scores below are **Reported** from this README capture alone, without independent verification here and with linked run records, docs, tools, and weights uninspected.

## Identity and product boundary

- Personal project under the Apache License 2.0; support is voluntary via Ko-fi with no purchase, returns, promised features, or governance role[^ninfer-readme].
- Deliberately specialized runtime: one GPU, one resident model, one to eight resident execution lanes with bounded FIFO ingress, fixed at startup[^ninfer-readme].
- No priority/QoS, weight offload, multi-GPU, or distributed serving; parsed tool calls are returned to the client without execution; in-tree C++ headers are not distributed as an installed SDK[^ninfer-readme].
- There is no install target or packaged binary distribution; NInfer runs from its source build tree[^ninfer-readme].
- GPU residency is fixed at process startup: `--spec` selects speculative-decoding residency and `--vision` independently selects Vision residency[^ninfer-readme].

## Official artifacts

- Five official v3 `.ninfer` artifacts, each carrying model configuration, encoded weights, logical bindings, and frontend resources[^ninfer-readme]:

| Model | Weights | Artifact |
|---|---|---|
| Qwen3.6-27B | `groupwise-int` | `qwen3_6_27b.ninfer` |
| Qwen3.6-27B | `nvfp4` | `qwen3_6_27b_nvfp4.ninfer` |
| Qwen3.8-27B | `groupwise-int` | `qwen3_8_27b.ninfer` |
| Qwen3.8-27B | `nvfp4` | `qwen3_8_27b_nvfp4.ninfer` |
| Qwen3.6-35B-A3B | `groupwise-int` | `qwen3_6_35b_a3b.ninfer` |

- The current engine requires v3 artifacts; existing official v2 downloads upgrade locally without re-downloading weights, via the weight-conversion doc that was not inspected[^ninfer-readme].
- Custom weights are converted with an official recipe or another supported mixture of formats, via the uninspected weight-conversion doc; NVFP4 artifacts derive partly from third-party packed weights (Qwen3.6-27B from `rdtand/...-NVFP4-BF16-vllm`, Qwen3.8-27B from `unsloth/...-NVFP4`), whose source repos are Apache-2.0 while vendored dependencies keep their own licenses under `third_party/`[^ninfer-readme].

## Build requirements

- Requires 64-bit Linux, one RTX 5090, a CUDA toolkit supporting `sm_120a`, CMake 3.28+, a C++20 host compiler, Ninja, `pkg-config`, FFmpeg development libraries (`libavformat`, `libavcodec`, `libavutil`, `libswscale`), and `libcurl >= 7.85`; CUDA 13.1 is the validated toolkit and the build rejects architectures other than `sm_120a`[^ninfer-readme].
- Product build[^ninfer-readme]:

```bash
git clone https://github.com/Neroued/ninfer.git
cd ninfer
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

- `cmake --preset release` configures the same product build; `cmake --preset dev` also enables tests and benchmarks and finds a Python 3 interpreter; both presets use `build/` and reset build options, with machine-specific paths in the ignored `CMakeUserPresets.json`[^ninfer-readme].
- Tests and benchmarks are excluded from the default build; Python tools run independently of CMake and the standalone HBM probe has its own build command in the uninspected `tools/README.md`[^ninfer-readme].

## Serve and CLI operation

- Example text/agent server with two lanes and prefix caching (240K-token logical ceiling per request, shared 240K-token Device KV pool, FP8 KV, MTP with 3 draft tokens)[^ninfer-readme]:

```bash
./build/apps/ninfer-serve models/qwen3_8_27b_nvfp4.ninfer \
  --max-context 240000 \
  --kv-capacity 240000 \
  --max-concurrency 2 \
  --kv-dtype fp8 \
  --device-state-slots 2 \
  --spec mtp --draft-tokens 3 \
  --lm-head-draft \
  --preserve-thinking
```

- `--max-context` is each sequence's logical limit; `--kv-capacity` sizes the shared Main Text KV pool for active requests plus retained prefixes, and `auto` resolves the largest legal capacity from post-weight memory with 1 GiB sizing headroom; explicit capacities stay fixed for the process lifetime[^ninfer-readme].
- The example profile adds two extra Device StateImages plus the default shared pinned Host budget of 8 GiB plus eight model StateImages for retained state, KV, and pause snapshots; requests acquire KV pages as execution advances and under pressure the scheduler can pause a request and resume it later[^ninfer-readme].
- Serves OpenAI Responses Core, OpenAI Chat Completions, and Anthropic Messages including streaming, tools, local response state, token counting, and usage accounting; exact current options come from the relevant `--help`[^ninfer-readme].
- One-shot CLI example with a 32,768-token allocation and up to 8,192 new tokens; answer content goes to stdout while diagnostics, reasoning, timing, throughput, memory, and speculative-decoding reports go to stderr, with terminal-aware progress lines and `--log-level debug` for full startup detail[^ninfer-readme].
- Structured image/video input uses `--messages FILE` and `--vision` per the uninspected CLI guide and committed examples[^ninfer-readme].

## Resource-aware reuse and scheduling

- A reusable checkpoint combines KV with the complete continuation state at an exact token frontier; the engine retains completed conversation endpoints and stable input boundaries for multi-turn and agent reuse[^ninfer-readme].
- Inactive checkpoints share Device and pinned Host capacity; pressure reclaims retained resources before pausing resident requests, and paused requests resume from a snapshot or rebuild state by replaying committed tokens[^ninfer-readme].
- Algorithm detail lives in the uninspected resource-scheduling doc; public-HTTP hot-reuse, Host-resume, eviction, shared-prefix, scheduling-boundary, and multimodal-load coverage lives in the uninspected serve-TTFT benchmark[^ninfer-readme].

## Speculative decoding

- MTP speculative decoding with draft windows of one to five tokens, enabled in the examples via `--spec mtp --draft-tokens 3 --lm-head-draft`[^ninfer-readme].
- The 35B-A3B target additionally supports DFlash with draft windows of one to fifteen for Text and image/video Vision prompts; Qwen3.8-27B artifacts with DFlash2 companion weights support `--spec dflash2 --draft-tokens 7` on the same Text/Vision engine path with draft counts 1–15 and full or optimized proposal heads[^ninfer-readme].
- Qwen3.6-35B-A3B DFlash combines with Vision to accelerate generated-text decode after multimodal prefill, not Vision encoding itself[^ninfer-readme].

## KV formats, sampling, and scoring

- Supported KV storage: BF16, INT8, FP8, NVFP4, and K8V4[^ninfer-readme].
- Published runs use FP8 E4M3 row-256 KV for Qwen3.8 and INT8 group-64 KV for Qwen3.6[^ninfer-readme].
- Includes offline causal-perplexity scoring, private and shared exact-prefix reuse with Device/Host State and KV retention, model-aware sampling defaults with explicit overrides, and thinking/non-thinking prompt modes plus chunked prefill, exact-batch CUDA Graph decode, and startup-bounded batched decode[^ninfer-readme].

## Reported performance (RTX 5090)

- **Evidence class:** **Reported** — hardware (RTX 5090), model profile, and workload shape are stated, but engine revision, sampling, harness version, and repeat protocol are not in this capture, so per the SCOPE benchmark rule these are not comparable benchmarks yet; full run records and methodology live in linked per-model pages that were not inspected[^ninfer-readme].
- Concurrent MTP3 decode used CUDA Graphs, MTP3, and one 8,192-token generation per active request; throughput counts aggregate committed decode tokens from complete intervals at the configured concurrency, with acceptance over the complete request wave[^ninfer-readme]:

| Model profile | C=1 tok/s / accept | C=2 tok/s / accept | C=4 tok/s / accept | C=8 tok/s / accept |
|---|---:|---:|---:|---:|
| Qwen3.6-27B `groupwise-int` | 185.8 / 68.2% | 247.0 / 69.0% | 309.5 / 68.4% | 535.0 / 68.3% |
| Qwen3.6-27B `nvfp4` | 202.4 / 69.3% | 399.7 / 71.4% | 699.7 / 69.3% | 1,146.9 / 68.6% |
| Qwen3.6-35B-A3B `groupwise-int` | 642.5 / 68.6% | 907.2 / 66.3% | 1,213.5 / 69.6% | 1,380.7 / 68.0% |
| Qwen3.8-27B `groupwise-int` | 136.5 / 44.4% | 253.3 / 45.2% | 398.1 / 46.1% | 582.4 / 46.4% |
| Qwen3.8-27B `nvfp4` | 147.7 / 46.2% | 291.0 / 48.7% | 522.2 / 45.8% | 922.4 / 46.1% |

- Single-request serving used CUDA Graphs, a 1,024-token prefill chunk, and five fixed seeds after warm-up; the table keeps one short-prefill, one extreme-prefill, and one structured-output MTP3 point per profile with full matrices in the uninspected per-model pages[^ninfer-readme]:

| Model profile | 7,680-token prefill | 260,096-token prefill | Structured MTP3 decode |
|---|---:|---:|---:|
| Qwen3.6-35B-A3B `groupwise-int` | 17,705.4 tok/s | 5,247.0 tok/s | 779.6 tok/s |
| Qwen3.6-27B `groupwise-int` | 3,218.1 tok/s | 1,614.8 tok/s | 193.0 tok/s |
| Qwen3.6-27B `nvfp4` | 11,191.5 tok/s | 2,510.6 tok/s | 252.2 tok/s |
| Qwen3.8-27B `groupwise-int` | 3,331.9 tok/s | 2,139.4 tok/s | 214.7 tok/s |
| Qwen3.8-27B `nvfp4` | 12,819.1 tok/s | 4,016.4 tok/s | 231.7 tok/s |

## Reported evaluation

- **Evidence class:** **Reported** — measured through NInfer's OpenAI-compatible route with thinking enabled, MTP3, and EvalScope 1.9.0 (0-shot, rule scoring, one sample per problem); treat as vendor-style benchmark evidence with no independent check here[^ninfer-readme].
- Qwen3.6 rows used temperature 0.6 and presence penalty 1.0; Qwen3.8 rows used temperature 1.0 and presence penalty 0.0; multimodal rows used `--vision` with an 81,920-token context limit; text rows used 262,144 tokens except Qwen3.8-27B NVFP4 at 252,928 tokens to fit the RTX 5090 after weights; model cards with correct/total counts were not inspected[^ninfer-readme]:

| Model profile | AIME 2025 | AIME 2026 | GPQA-Diamond | ERQA | RealWorldQA |
|---|---:|---:|---:|---:|---:|
| Qwen3.6-27B groupwise-int | 86.67% | 93.33% | 86.87% | — | — |
| Qwen3.6-27B NVFP4 | 93.33% | 93.33% | 84.34% | — | — |
| Qwen3.6-35B-A3B groupwise-int | 90.00% | 90.00% | 85.35% | — | — |
| Qwen3.8-27B groupwise-int | 96.67% | 96.67% | 87.37% | 66.25% | 82.22% |
| Qwen3.8-27B NVFP4 | 96.67% | 96.67% | 90.40% | 66.25% | 83.53% |

## Docker

- Build the runtime image on a host with the NVIDIA Container Toolkit via `docker build --tag ninfer:local .`, then mount `./models` read-only and run the same server profile with `--host 0.0.0.0` and port 8080 published[^ninfer-readme].

## Relationships

- Related to [Narrow Single-Model Inference Engines](narrow-inference-engines.md) — NInfer is one of the six single-model, single-hardware engines in that set, here grounded in its own README rather than secondhand coverage.
- Related to [Qwen3.6 Local Deployment](qwen3.6.md) — the Unsloth GGUF/MLX/NVFP4 local route for the same Qwen3.6-27B and 35B-A3B models NInfer ships as `.ninfer` artifacts.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — the Unsloth local route for the same Qwen3.8-27B family NInfer ships as `.ninfer` artifacts.
- Related to [Speculative Decoding Foundations](speculative-decoding-foundations.md) — the draft-verify-accept mechanism behind the MTP and DFlash/DFlash2 acceptance and tok/s figures reported here.
- Related to [NVFP4 Format and Scale-Dependent Accuracy](nvfp4-format-accuracy-scale.md) — the 4-bit weight format behind the NVFP4 artifact and decode rows reported here.

## Coverage limits

- Only `../raw/ninfer.md` was inspected statically; no commands were executed.
- Linked entry points and attachments named in the source but absent from `raw/` were not inspected: `docs/README.md`, `docs/cli.md`, `docs/serving.md`, `docs/performance.md`, `docs/performance/methodology.md`, per-model performance pages, `docs/perplexity.md`, `docs/weight-conversion.md`, `docs/maintainer/build-system.md`, `docs/maintainer/resource-scheduling-and-context-cache.md`, `tools/README.md`, `tools/bench/ttft/`, `examples/cli/`, `CONTRIBUTING.md`, `LICENSE`, `model-cards/*` READMEs, Hugging Face artifact pages, and the `Neroued/ninfer` repo itself.
- Source date, revision, and engine version are unstated in this capture; build validation is read from the stated CUDA 13.1 and `sm_120a` requirements.
- No sensitive values found.

[^ninfer-readme]: NInfer — `../raw/ninfer.md` (README capture: from-scratch C++/CUDA engine for Qwen3.5 Dense/MoE on one RTX 5090 with CLI plus OpenAI-/Anthropic-compatible APIs and 1–8 startup-fixed lanes; five Qwen3.6/3.8 v3 `.ninfer` artifacts with v2-upgrade and weight-conversion pointers; Linux/5090/`sm_120a`/CUDA-13.1/CMake-3.28/C++20/Ninja/FFmpeg/libcurl build plus `release`/`dev` presets and no install target; 240K `--max-context`/`--kv-capacity` serve example with `--kv-dtype fp8`, two state slots, MTP3, `--lm-head-draft`, `--preserve-thinking`, StateImage/Host-budget and pause/resume semantics; 32K CLI example with stdout/stderr split; KV-plus-continuation checkpoints with Device/Host retention; CUDA-Graph MTP3 decode and single-request prefill/decode tables with FP8-E4M3-row-256 vs INT8-group-64 KV note; EvalScope-1.9.0 thinking+MTP3 capability table with Qwen3.6 0.6/1.0 vs Qwen3.8 1.0/0.0 sampling and 262,144/252,928/81,920 context notes; MTP 1–5, 35B-A3B DFlash 1–15, Qwen3.8 DFlash2 companion `--spec dflash2 --draft-tokens 7` with 1–15 and full/optimized heads; BF16/INT8/FP8/NVFP4/K8V4 KV, perplexity scoring, prefix reuse, sampling defaults, Responses/Chat/Anthropic API support; one-GPU/one-model/1–8-lane/FIFO boundary with no QoS/offload/multi-GPU/distribution, fixed KV pool, native paths, no tool execution or SDK; Docker build/run; Apache-2.0 license with Qwen plus `rdtand`/`unsloth` NVFP4 weight provenance and Ko-fi support note).
