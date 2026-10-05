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
  - id: ninfer-4080-thread
    resource: ../raw/i_built_ninfer_4080_for_16gb_class_gpus.md
    kind: discussion
    title: I built Ninfer 4080 for 16GB class GPUs
  - id: ninfer-5090-thread
    resource: ../raw/ninfer_and_a_5090_with_38_27b_is_making_me_cry.md
    kind: discussion
    title: Ninfer and a 5090 with 3.8 27B is making me cry tears of joy
  - id: ninfer-uncensored-5090-thread
    resource: ../raw/ninfer_qwen_3827b_uncensored_on_rtx_5090_175_toks.md
    kind: discussion
    title: NInfer Qwen 3.8-27B uncensored on RTX 5090 175 tok/s changed my life
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

## Reported production field reports (RTX 5090 thread)

- **Evidence class:** **Reported** — all figures below come from one r/LocalLLaMA post plus comments without stated engine revisions or fork commits (except `e0829866`), sampling, harness versions, or repeat protocol, so per the SCOPE benchmark rule they are non-comparable field reports, not benchmarks[^ninfer-5090-thread].
- OP launch profile (`qwen3_8_27b_nvfp4.ninfer`, `--max-context 240000`, `--kv-capacity 240000`, `--max-concurrency 2`, `--kv-dtype fp8`, `--host-kv-mib 16384`, `--spec mtp --draft-tokens 3 --lm-head-draft`, `--vision`, `--media-live-mib 2048`): peak ~220 tok/s decode, average in the 170s, described as roughly double prior llama.cpp throughput[^ninfer-5090-thread].
- Highest-detail production rig (RTX 5090 32 GB Blackwell/SM120, Ryzen 9 9950X3D, 1200 W PSU, 530 W limit plus 700–2700 MHz clock lock after combined CPU+GPU shutdowns, DietPi on Proxmox, Docker Compose via Komodo, OG `Neroued/ninfer` `sm120a` build, llama-swap router)[^ninfer-5090-thread]:

| Profile | Weights | Size | Context | KV |
|---|---|---:|---:|---|
| Qwen3.8-27B groupwise | Q4/Q5/Q6 mixed | 16.67 GB | 262,144 | int8 |
| Qwen3.8-27B groupwise + vision | same, vision on | 16.95 GB | 65,536–262,144 tested | int8 |
| Qwen3.8-27B NVFP4 | mixed NVFP4/FP8 | 21.5 GB | 131,072 | int8 |

- Same rig, real production traffic rather than synthetic runs: groupwise decode 145–233 tok/s sustained over hours of agentic tool-calling with a 38,855-token largest single generation; NVFP4 decode 130–230 tok/s with a 61,180-token largest single generation; MTP draft-window-3 acceptance roughly 45–100% by content (code and structured tool calls accept higher than freeform prose); continuing-conversation prefix reuse cut TTFT sharply once working (one real example: 26,140-token prefix reused with 153 ms TTFT)[^ninfer-5090-thread].
- Same rig hit a genuine engine bug where prefix reuse silently failed for every plain OpenAI-protocol request without a session key despite showing enabled; fixed upstream in commit `e0829866` ("restore anonymous prefix reuse") by moving to current `master`[^ninfer-5090-thread].
- Second dual-5090 datapoint (two 5090s, one ninfer instance each, EPYC 7532, 128 GB DDR4-3200, 400 W limit each): average around 160 tok/s decode and 2,500 tok/s prefill with context raised to 400K[^ninfer-5090-thread].
- Context and concurrency semantics: the 240K pool is shared, so concurrent sessions split it (commenter example: three sessions share 240K as ~80K each); `--host-kv-mib` keeps KV backups in RAM so switched-away contexts resume without recomputing prefill[^ninfer-5090-thread].
- Alternative single-lane profile (`--max-context 131072`, `--kv-capacity 131072`, `--prefill-chunk 4096`, `--max-concurrency 1`, `--spec mtp --draft-tokens 5 --lm-head-draft`, `--kv-dtype int8`, `--device-state-slots 3`, `--host-kv-mib 2048`, `--vision`): reporter sees ~11.5 GB ninfer-serve host memory, ~200 tok/s on a synthetic vision-off benchmark and often ~150 tok/s on real agentic coding turns; a follow-up with the same flags but `--max-concurrency 1` otherwise reports being capped near 114 tok/s, so host RAM and remaining flags matter[^ninfer-5090-thread].
- Platform deltas are large but uncontrolled: one 5090 report averages ~140 tok/s via WSL2 on Windows 11 versus the OP's ~220 tok/s on Linux with a similar command; one Windows user reports only ~70 tok/s before switching to Linux; headless Linux versus display-manager VRAM is named as one lever (one reporter fits ~190K at Q8 KV headless)[^ninfer-5090-thread].
- Fork and platform matrix: original is Linux-only and `sm120a`-only built from source; Windows paths are the `natpate/ninfer-windows` fork, the `headpiece747/ninfer-5090-windows` native fork, or Docker plus WSL2 GPU passthrough[^ninfer-5090-thread]. Reported 4090 path (`sergiuszm/ninfer-4090`) is roughly 130–170 tok/s via Docker/WSL2 while the `UDPSendToFailed/ninfer-4090` fork repeatedly failed to build for another reporter; the collected fork list adds three more 4090 forks plus 3090, CMP 170HX, V100, and 5060Ti-for-4000-series notes, with 5080/5070Ti/4060Ti-16GB ports requested but absent[^ninfer-5090-thread]. No multi-GPU single instance: dual-5090 and dual-3090 reporters run one instance per GPU; a `syv-ai/qwen38-27b-rtx3090` pointer claims to beat ninfer-3090 and to cover dual 5060 Ti 16 GB, and a vLLM recipe pointer (`seanyourhighness/vllm-sm12x-nvfp4-dflash2`) claims ~200 tok/s on code with a 325K pool (MTP variant: 400K pool, ~100 tok/s concurrent) — both uninspected here[^ninfer-5090-thread].
- NVFP4 fidelity dispute, all **Reported** with no evaluation protocol: one side says Q6-to-NVFP4 loss is definitely present; the other side says Q4-class quantization holds up whenever actual evidence is shown; the quantitative middle claims roughly 55/45 NVFP4/FP8 weights for an effective ~6.06 BPW versus ~6.4 BPW for Q6_K_M, i.e. little sacrificed for roughly double throughput[^ninfer-5090-thread]. Adjacent speed note: Qwen3.6-35B-A3B at 500–600 tok/s in a Pi harness for well-scoped tasks[^ninfer-5090-thread].
- Operational warnings: verify real-world prefix-cache hits rather than trusting headline tok/s (a 4090 `feat/rtx-4090-sm89-native` commit series addressing cache misses is cited as reason to retest); `--vision` costs context and throughput; power, clocks, RAM, and display state matter at 240–400K contexts[^ninfer-5090-thread].

## Reported field reports (r/LocalLLM uncensored 5090 thread)

- **Evidence class:** **Reported** — all figures below come from one r/LocalLLM post (260 votes, 100 comments) plus comments with no stated NInfer revisions or fork commits, sampling, harness versions, or shared repeat protocol, so per the SCOPE benchmark rule they are non-comparable field reports, not benchmarks[^ninfer-uncensored-5090-thread].
- OP profile: NInfer NVFP4 / groupwise-int with MTP on at ~175 tok/s decode and 262K context on one RTX 5090 32 GB, up from a prior ~64K usable context, described as significantly faster than frontier cloud models[^ninfer-uncensored-5090-thread].
- High-context prefill datapoint: ~248K tokens (247,802) at 1,675 tok/s prefill in 148 s, needle-in-haystack 90% depth measured Aug 22 on groupwise-int with `--kv-dtype int8`; the same commenter estimates ~2,500–3,000 tok/s at 150K explicitly as an estimate, not a measurement[^ninfer-uncensored-5090-thread].
- vLLM-nightly cross-check on different hardware: median 1,580 tok/s prefill across 3 runs at 262K 90% depth on an RTX PRO 4500 (described as near-5080 compute, 200 W cap) with `lyf/Qwen3.8-27B-Huihui-Abliterated-NVFP4-MTP-VL` and FP8 KV cache[^ninfer-uncensored-5090-thread].
- DFlash2 agentic datapoint: ~186 tok/s average in fully loaded agentic dev sessions at 218K context via Windows NInfer, using a larger NVFP4 build with DFlash2 baked in and a 55/45 FP4/FP8 split; reporter frames larger size as the tradeoff[^ninfer-uncensored-5090-thread].
- Quantization-fidelity reports, all **Reported** with no shared protocol: NInfer Q4 scored the same as Q8 on an unspecified benchmark (one reporter, previously on llama.cpp Q8); one commenter quantifies NVFP4 at ~88% of BF16 with Q6 ~92% and Q8 ~95%; one beginner reporter finds groupwise-int at least 10% slower than NVFP4[^ninfer-uncensored-5090-thread].
- Uncensored NInfer weights named: `lyf/Qwen3.8-27B-Huihui-Abliterated-NInfer-NVFP4` (Huihui abliterated Qwen3.8-27B pre-converted to NInfer NVFP4)[^ninfer-uncensored-5090-thread]. One reporter converts the original safetensor uncensored model with NInfer's own converter and ranks variants by IFBench-prompt-strict (Official 87% / HuiHui 80% / JohnanthanColetti 81% / Jiunsong 79%) and GPQA-Diamond (Official 84% / HuiHui 76% / JohnanthanColetti 84% / Jiunsong 86%), naming JohnanthanColetti best-so-far; abliteration-quality dispute persists with eye-test claims on both sides (base Q8 smarter vs. abliterated loops)[^ninfer-uncensored-5090-thread].
- Context-ceiling fork notes: one reporter caps upstream NInfer at ~175K with MTP4 on Qwen3.8, while `cometkim`/`gzenz` forks are said to allow up to 1M theoretically, with a personal `swift-qwen3.8` run at 484K ctx; same reporter sees prefill start at 4K–10K tok/s on 4K chunks but drop to ~1K at 150K+ context, with decode peaking at 410 tok/s at concurrency 2, ~220 single-thread max, and ~160–170 average[^ninfer-uncensored-5090-thread].
- Adjacent baselines and harnesses: same-model Q5 on Ollama at ~60 tok/s on a 5090; a self-ported 4090 ternary/`bonsai-2-27b` claim of 210 tok/s decode and 3K prefill; ThinkingCap Qwen3.8-27B as fewer-thinking-tokens without quality loss with a pre-converted `Schestex/ThinkingCap-Qwen3.8-27B-NInfer` pointer; Hermes overhead note of 7–8K system-prompt tokens from Mnemosyne memory plus Lossless Compaction alone; 5060Ti (`ruwwww/ninfer-5060ti`) and 5080 (`ninfer-5080/Qwen3.8-27B-RTX5080`, MTP/128K/vision) fork pointers noted as Linux-only by reporters[^ninfer-uncensored-5090-thread].
- Agentic-use pattern (redacted): the OP attributes long-horizon Hermes/`dsh` checklist plus test-acceptance-gate iteration to the 262K context, and describes a local-first routine that escalates stuck tasks to frontier cloud models; request-wording and cybersecurity-task specifics in the source are excluded here as non-durable prompt-manipulation detail[^ninfer-uncensored-5090-thread].

## Docker

- Build the runtime image on a host with the NVIDIA Container Toolkit via `docker build --tag ninfer:local .`, then mount `./models` read-only and run the same server profile with `--host 0.0.0.0` and port 8080 published[^ninfer-readme].

## Relationships

- Related to [NInfer 4080 16GB Port](ninfer-4080-16gb-port.md) — community `SM_89` fork for Qwen3.8-27B-GSQ at ~100K on 16 GB RTX 4080/4060Ti with added Q3 kernels, GSQ conversion, and DFlash2/MTP plus compressed-KV reported figures (**Reported**)[^ninfer-4080-thread].
- Related to [Narrow Single-Model Inference Engines](narrow-inference-engines.md) — NInfer is one of the six single-model, single-hardware engines in that set, here grounded in its own README rather than secondhand coverage.
- Related to [Qwen3.6 Local Deployment](qwen3.6.md) — the Unsloth GGUF/MLX/NVFP4 local route for the same Qwen3.6-27B and 35B-A3B models NInfer ships as `.ninfer` artifacts.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — the Unsloth local route for the same Qwen3.8-27B family NInfer ships as `.ninfer` artifacts.
- Related to [Speculative Decoding Foundations](speculative-decoding-foundations.md) — the draft-verify-accept mechanism behind the MTP and DFlash/DFlash2 acceptance and tok/s figures reported here.
- Related to [NVFP4 Format and Scale-Dependent Accuracy](nvfp4-format-accuracy-scale.md) — the 4-bit weight format behind the NVFP4 artifact and decode rows reported here.
- Related to [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — the baked-in DFlash2 path behind the 186 tok/s at 218K agentic report in the uncensored-5090 thread (**Reported**)[^ninfer-uncensored-5090-thread].

## Coverage limits

- Only `../raw/ninfer.md` was inspected statically; no commands were executed.
- Linked entry points and attachments named in the source but absent from `raw/` were not inspected: `docs/README.md`, `docs/cli.md`, `docs/serving.md`, `docs/performance.md`, `docs/performance/methodology.md`, per-model performance pages, `docs/perplexity.md`, `docs/weight-conversion.md`, `docs/maintainer/build-system.md`, `docs/maintainer/resource-scheduling-and-context-cache.md`, `tools/README.md`, `tools/bench/ttft/`, `examples/cli/`, `CONTRIBUTING.md`, `LICENSE`, `model-cards/*` READMEs, Hugging Face artifact pages, and the `Neroued/ninfer` repo itself.
- Source date, revision, and engine version are unstated in this capture; build validation is read from the stated CUDA 13.1 and `sm_120a` requirements.
- `../raw/i_built_ninfer_4080_for_16gb_class_gpus.md` was compiled in [NInfer 4080 16GB Port](ninfer-4080-16gb-port.md); only the relationship pointer above is added here, with full 4080 tables and limits kept on that page.
- Only the text of `../raw/ninfer_and_a_5090_with_38_27b_is_making_me_cry.md` was inspected statically; no commands were executed.
- Linked or named artifacts absent from `raw/` were not inspected: all GitHub forks and repos (OG `Neroued/ninfer`, four 4090 forks, 3090, CMP 170HX, V100, `natpate/ninfer-windows`, `headpiece747/ninfer-5090-windows`, `syv-ai/qwen38-27b-rtx3090`, `seanyourhighness/vllm-sm12x-nvfp4-dflash2`), the `.ninfer` weights, the anonpaste Hermes skill, the LiveCodeBench/Fable-5 thread, the NIM-API suggestion, and the preview PNG metrics chart.
- Thread figures carry no engine revisions or fork commits (except `e0829866`), sampling settings, harness versions, or repeat protocol, so they stay **Reported** and non-comparable per the SCOPE benchmark rule.
- Only the text of `../raw/ninfer_qwen_3827b_uncensored_on_rtx_5090_175_toks.md` was inspected statically; no commands were executed. Named HF checkpoints (`lyf/...`, `Schestex/...`, `ninfer-5080/...`), repos/forks (`ruwwww/ninfer-5060ti`, `cometkim`, `gzenz`, `club-3090`), weights, harnesses (Hermes, `dsh`), and linked screenshots/threads were not inspected. Jailbreak-style request-wording, cybersecurity-task specifics, CTF/SQLMap anecdote, and OS-choice debate were excluded as non-durable or manipulation detail; the agent-escalation pattern above is the redacted durable remainder.
- No sensitive values found.

[^ninfer-readme]: NInfer — `../raw/ninfer.md` (README capture: from-scratch C++/CUDA engine for Qwen3.5 Dense/MoE on one RTX 5090 with CLI plus OpenAI-/Anthropic-compatible APIs and 1–8 startup-fixed lanes; five Qwen3.6/3.8 v3 `.ninfer` artifacts with v2-upgrade and weight-conversion pointers; Linux/5090/`sm_120a`/CUDA-13.1/CMake-3.28/C++20/Ninja/FFmpeg/libcurl build plus `release`/`dev` presets and no install target; 240K `--max-context`/`--kv-capacity` serve example with `--kv-dtype fp8`, two state slots, MTP3, `--lm-head-draft`, `--preserve-thinking`, StateImage/Host-budget and pause/resume semantics; 32K CLI example with stdout/stderr split; KV-plus-continuation checkpoints with Device/Host retention; CUDA-Graph MTP3 decode and single-request prefill/decode tables with FP8-E4M3-row-256 vs INT8-group-64 KV note; EvalScope-1.9.0 thinking+MTP3 capability table with Qwen3.6 0.6/1.0 vs Qwen3.8 1.0/0.0 sampling and 262,144/252,928/81,920 context notes; MTP 1–5, 35B-A3B DFlash 1–15, Qwen3.8 DFlash2 companion `--spec dflash2 --draft-tokens 7` with 1–15 and full/optimized heads; BF16/INT8/FP8/NVFP4/K8V4 KV, perplexity scoring, prefix reuse, sampling defaults, Responses/Chat/Anthropic API support; one-GPU/one-model/1–8-lane/FIFO boundary with no QoS/offload/multi-GPU/distribution, fixed KV pool, native paths, no tool execution or SDK; Docker build/run; Apache-2.0 license with Qwen plus `rdtand`/`unsloth` NVFP4 weight provenance and Ko-fi support note).
[^ninfer-4080-thread]: u/roofkid, "I built Ninfer 4080 for 16GB class GPUs" — `../raw/i_built_ninfer_4080_for_16gb_class_gpus.md` (r/LocalLLaMA post plus comments: `SM_89` 4080 port of NInfer for `ISTA-DASLab-Qwen-3.8-27B-GSQ` with Q3 kernels, GSQ conversion, and DFlash2/MTP figures; relationship pointer only here, full synthesis in [NInfer 4080 16GB Port](ninfer-4080-16gb-port.md)).
[^ninfer-5090-thread]: u/Rollingsound514, "Ninfer and a 5090 with 3.8 27B is making me cry tears of joy" — `../raw/ninfer_and_a_5090_with_38_27b_is_making_me_cry.md` (r/LocalLLaMA capture: 190-vote OP post with NVFP4 serve command and 170–220 tok/s claim plus ~2x-llama.cpp comparison; production-rig comment with 5090/9950X3D/Proxmox/DietPi/Komodo/llama-swap setup, three weight-profile size/context rows, sustained decode bands, 38K/61K max generations, 45–100% MTP acceptance, 26K-prefix 153 ms TTFT, and `e0829866` anonymous-prefix-reuse fix; dual-5090 EPYC comment; 131K single-lane int8/MTP5 profile; WSL2/Windows-vs-Linux deltas; 4090-fork results and collected 4090/3090/CMP170HX/V100/5060Ti fork pointers; syv-ai and vLLM-dflash2 alternative pointers; NVFP4 6.06-vs-6.4-BPW dispute; cache-miss, vision-cost, and power/clock warnings; preview PNG uninspected).
[^ninfer-uncensored-5090-thread]: u/EntrepreneurLeast445, "NInfer Qwen 3.8-27B uncensored on RTX 5090 175 tok/s changed my life" — `../raw/ninfer_qwen_3827b_uncensored_on_rtx_5090_175_toks.md` (r/LocalLLM post, 260 votes / 100 comments: OP body with 175 tok/s NVFP4/groupwise-int+MTP and 262K-ctx claims plus Hermes/`dsh` long-reasoning and cloud-escalation pattern; prefill comments at 247,802 tokens / 1,675 tok/s / 148 s with int8 KV and 150K estimate, RTX PRO 4500 vLLM-nightly 1,580 tok/s median, Windows DFlash2 186 tok/s at 218K with 55/45 FP4/FP8 split; Q4==Q8, 88/92/95% fidelity, and ≥10% groupwise-int slowdown reports; `lyf/...-NInfer-NVFP4` pointer with IFBench/GPQA variant table; upstream-175K vs. `cometkim`/`gzenz` 1M/484K fork notes with prefill-drop and decode bands; Ollama-Q5, 4090-ternary, ThinkingCap, Hermes-overhead, and 5060Ti/5080 fork pointers).
