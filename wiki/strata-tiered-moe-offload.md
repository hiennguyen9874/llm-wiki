---
type: Concept
title: Strata Tiered MoE Offload Engine
description: Strata's consumer-PC engine for Qwen3.8-Flash-Next that splits dense weights and a hot-expert cache on the GPU, all experts computed in place on the CPU from RAM, and the n-gram table on SSD, with KV streaming, low-RAM modes, and chunked prefill.
tags: [strata, serving, local-inference, moe, expert-offload, cpu-gpu-hybrid, kv-cache, prefill, qwen3.8-flash-next, llama-cpp]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-04T20:00:00Z }
stale_after: 2027-04-04
sources:
  - id: strata-docs
    resource: ../raw/Strata/README.md
    scope: ../raw/Strata/
    kind: documentation
    title: Strata repository documentation (README, HOW_IT_WORKS, MODELS, DETAILS; engine up to 0.1.39b)
  - id: strata-thread-65tps
    resource: ../raw/qwen38flashnext-on-12gb-vram-65-tokens-per-second/index.md
    scope: ../raw/qwen38flashnext-on-12gb-vram-65-tokens-per-second/
    kind: discussion
    title: "Qwen3.8-Flash-Next on 12GB VRAM - 65 tokens per second (r/LocalLLaMA)"
  - id: strata-thread-5090
    resource: ../raw/strata-on-a-power-limited-5090-and-96gb-of/index.md
    scope: ../raw/strata-on-a-power-limited-5090-and-96gb-of/
    kind: discussion
    title: "Strata on a power limited 5090 and 96GB of DDR5-6400 (r/LocalLLaMA)"
  - id: strata-video-6x
    resource: ../raw/the-new-way-to-run-125b-models-6x-faster-than-llama.cpp-(strata).md
    kind: video
    title: "The New Way to Run 125B Models 6x Faster Than llama.cpp (Strata) (YouTube transcript)"
  - id: strata-thread-bots
    resource: ../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/index.md
    scope: ../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/
    kind: discussion
    title: "Yes bots we get it, Strata is good now please stop (r/LocalLLaMA)"
---

Strata is an MIT-licensed, single-model inference engine that runs the 125B-parameter MoE [Qwen3.8-Flash-Next](qwen3.8-flash-next-architecture.md) on a gaming PC with a 12 GB+ NVIDIA (CUDA) or AMD (HIP) GPU by placing each part of the model on the memory tier that suits its access pattern: every-token dense weights plus a cache of the most-used experts on the GPU, all 24,576 experts pinned in RAM and computed in place by the CPU when the GPU misses, and the 28.8 GB n-gram table on the SSD[^strata-docs]. It reuses llama.cpp/ggml pieces (i-quant formats, GPU dot products, the CPU backend for i-quant experts, `mtmd` for vision) and credits ideas from Splash, ninfer, and HyperQwen[^strata-docs]. Measured speeds and model choices live in [Strata Qwen3.8-Flash-Next Quants and Measured Speed](strata-qwen3.8-flash-next-quants-performance.md); drafting in [Strata MTP and Prompt-Lookup Speculation](strata-speculative-decoding.md); the HTTP server in [Strata Server API and Operations](strata-server-api.md).

## Why tiering works for this model

- The model has 24,576 experts (512 per layer across 48 layers) and each token routes to only 10 of them, so the full expert set never needs to be in VRAM at once (**Reported**)[^strata-docs].
- **Synthesis:** this exploits the same sparse activation as datacenter [expert parallelism](sglang-expert-parallelism.md), but trades interconnect bandwidth for a consumer PCIe link and CPU compute; the n-gram table's sparse deterministic addressing (see [Qwen3.8-Flash-Next Architecture](qwen3.8-flash-next-architecture.md#n-gram-embedding)) makes an SSD tier viable because only a few rows are read per token.
- Per-token byte arithmetic from a video explainer (**Reported**)[^strata-video-6x]: on the 66 GB Q2 build, one token reads ~0.66 GB of the ~34 GB expert store plus ~3.5 GB of always-on weights — roughly 4 GB of the 66 GB file, i.e. the 6B-active figure on the model card — while the ~29 GB / 51B-parameter n-gram table stays on SSD at 16 rows (~23 KB) per token; 36 of 48 attention layers hold constant-size state and 12 look back at most ~2,048 positions.
- Per-layer work split on the narrator's test machine (**Reported**)[^strata-video-6x]: each layer the GPU runs attention plus the router, serves already-held experts at once (a 12 GB card holding ~4,500 of 24,576), and the CPU computes the missing experts in RAM concurrently — about 34 ms per full pass, ~15 ms GPU plus ~13 ms CPU, each side waiting on the other per layer; the shipped usage profile serves about half of expert reads from the first message, adapting toward ~72% hits for the conversation.
- Community mechanism reading from a 2026-10-03 complaint thread that turned into corroboration (**Reported**)[^strata-thread-bots]: Qwen3.8-Flash-Next sparse attention needs only a small fraction of KV per token, so keeping KV in RAM costs little while VRAM holds experts under LRU; one reporter estimates ~50% of token generation served by VRAM-resident experts with SSD as last resort, and `setup.sh` calibrates placement to the machine. A second reporter frames the bottleneck as weights-transfer between tokens (125B MoE, ~180B with the n-gram table, ~6B active per pass) versus Qwen3.8-27B being compute-bound when it fits (**Reported**)[^strata-thread-bots].
- CPU-use signature from the same thread (**Reported**)[^strata-thread-bots]: Strata drives many/all CPU cores (one htop screenshot shows 12 cores engaged; one 5060 Ti reporter notes ~100% all-core use versus llama.cpp using one core at 100%), consistent with CPU-side expert compute; terminology dispute recorded as positions — one correction says this is not tiered storage because the full model loads in RAM with hot experts cached in VRAM, answered that tiered caching/storage is a fair label in LLM context.

## Tier placement

| Tier | Holds | Notes |
| --- | --- | --- |
| GPU (VRAM) | Attention and DeltaNet mixers, gated-residual weights, routers, shared experts, output head, MTP draft layer, KV cache (from 64K only its most-read part), and an expert cache filling remaining VRAM | Expert cache adapts to the conversation (`--adapt-every`)[^strata-docs] |
| RAM | All 24,576 experts, pinned | CPU computes non-cached experts in place with AVX-512/AVX2 kernels (ggml's for i-quants) concurrently with the GPU[^strata-docs] |
| SSD | 28.8 GB n-gram table | Read a few rows per token unbuffered (`--ple-io direct`); `--ple-io ram` for rotational disks (#605)[^strata-docs] |

- "More VRAM matters more than a faster GPU": every extra GB holds ~700 more experts, each one the CPU no longer computes (**Reported**)[^strata-docs].
- The shipped expert profile ranks all 24,576 experts since 0.1.14 (before, the cache stopped at 8,000); `tools/make_profile.py` builds a profile from a `--dump-routing` trace, and `--reorder` (0.1.39) puts the trace's pairs first[^strata-docs].
- `--pcie-frac` sets the share of VRAM-missing experts copied to the GPU instead of computed on the CPU; `--calibrate` (0.1.19, NVIDIA) measures `--pcie-frac`, `--spec-min-p`, and `--pool-workers` per PC and keeps a setting only when it is >3% faster[^strata-docs].
- `"expert_profile_save"` (0.1.36, #477, opt-in) persists the learned cache order across restarts; the file is described as a fingerprint of usage that stays on the PC[^strata-docs].

## KV cache placement and formats

- **KV streaming (0.1.5):** at ≥64K context, setup keeps the KV cache in RAM and only the attention-read part in VRAM (`--kv-resident 32768`), freeing VRAM for experts; Q2_0 at 262K went 50.9 → 62.6 tok/s (1,589 → 3,872 VRAM experts), about +6% at 128K, at ~13.7 KB RAM per context token (**Reported**, RTX 5070 12 GB)[^strata-docs]. Not available under WSL or with `--kv k8v4`[^strata-docs].
- **Default 8-bit KV** above 4K context[^strata-docs].
- **4-bit KV (`--kv q4_0`, 0.1.8):** Hadamard rotation before 4-bit rounding halves KV memory, ~4% faster at 128K, but perplexity +8–12% on long documents while needle tests still pass (**Reported**)[^strata-docs].
- **K8V4 (`--kv k8v4`, 0.1.25):** 8-bit keys, rotated 4-bit values, 23% less KV memory than 8-bit; RTX 3090 Coder at 198K: 85 → 99 tok/s output, same needle results, prompts 2–5% slower; pays off mostly on large cards at long context (**Reported**)[^strata-docs].
- Related KV-precision tradeoffs in other engines: [vLLM Quantized KV Cache](vllm-quantized-kv-cache.md), [SGLang Quantized KV Cache](sglang-quantized-kv-cache.md).
- **KV-cache persistence lifecycle (Reported):** early builds discarded the KV cache every prompt — reviewers called it unusable for agentic loops despite 65 tok/s decode, since multi-turn tool calling re-prefilled each step; by 0.1.18 the cache persists across turns, with one reporter measuring ~20% lower decode than 0.1.4 but much faster small-tool invocation, and a 3090/Coder rig re-serving a full 118K prompt from cache in 1.9 s[^strata-thread-65tps].
- **Setup default and community KV-precision dispute (Reported, Unverified):** `setup.sh` offers q8 vs q4 KV with an editable JSON config (`"--kv", "fp16"` reported working)[^strata-thread-bots]; one position calls Q8 KV virtually lossless at half the memory, the counter cites a localbench KV-quant benchmark as KLD-equivalent of dropping from Q8_K_XL to IQ4_XS weights with damage visible on 32K long-document columns and compounding with context, answered that Qwen 27B Q8 KV measures near-lossless while KV4 costs about a quant size — links and tables uninspected here. Separately, Qwen's vLLM recipes pointing at `--kv-cache-dtype fp8` plus `attention-config.indexer_kv_dtype fp8` surprised one commenter into reconsidering how much workspace full-precision KV wastes (**Reported**)[^strata-thread-bots].

## Low-RAM modes

| Mode | Engine | Mechanism |
| --- | --- | --- |
| Mapped (`--mmap-experts`) | 0.1.26 | Experts mapped from the pack's `experts.bin`; OS file cache holds what the GPU does not; Coder committed memory 36 → ~13 GB with the same answers[^strata-docs] |
| Resident (`--resident-experts`) | 0.1.30 | Copies exactly the non-GPU experts into (page-locked) RAM so steady decoding reads nothing from SSD; swaps keep RAM holding the GPU's complement; leaves 4 GB free (`STRATA_RESIDENT_HEADROOM_GIB`)[^strata-docs] |
| GGUF read in place | 0.1.31 | Native packs need no `experts.bin`; experts read from GGUF offsets validated against `native_experts.txt`, 8 fetch threads; identical tokens and logits on the Coder over 64 greedy tokens[^strata-docs] |
| RAM budget (`--resident-budget-gib N`) | 0.1.31 | Hottest N GiB of non-GPU experts locked in RAM, rest via file cache, plus next-layer router lookahead page warming (`STRATA_LOOKAHEAD`)[^strata-docs] |
| Arena mmap (`STRATA_ARENA_MMAP=1`, Linux) | 0.1.39 | Maps a native pack's expert arena read-only for multi-GPU, small-RAM boxes; 2×16 GB GPUs + 32 GB RAM: available RAM ~1 → 25 GB[^strata-docs] |

- With a small GPU in mapped mode most experts come from SSD and speed collapses; the RAM-budget mode is what runs Unsloth UD-Q4_K_XL (72 GiB experts) at 7–8.5 tok/s on a 64 GB PC with an RTX 5070, versus ~3 tok/s before (**Reported**)[^strata-docs].
- Multi-GPU in low-RAM mode uses the mapped variant (resident has no layer split yet); two users measured 1.3–1.6× over one card, but the file cache can drive free RAM to 0 during long prompts (**Reported**, #364/#384)[^strata-docs].
- Two-GPU expert-tier placement from the 2026-10-02 thread (eddoursul fork, second card as expert tier rather than layer split): put the slower/smaller card as main and the bigger card on the expert tier — one reporter benchmarked 3090-main/5090-expert-tier 15–30% faster than the reverse across code/prose/summary, reasoning the extra VRAM does more good holding experts than running the model (**Reported**); heterogeneous NVIDIA+AMD layer splitting is expected to cause more problems than it solves, with no evidence either way[^strata-thread-5090].
- Bandwidth diagnostic from the same thread (**Reported**): a 5090 showing only ~200 W with ~100 tok/s versus ~400 W+ at 150–225 tok/s signals a bandwidth restriction — verify full PCIe Gen5 x16 plus a fast non-lane-sharing NVMe[^strata-thread-5090].
- Observability: `--stats`, server-log `expert tiers`, and `/metrics` fields `ram_blobs`, `file_blobs`, `file_mb`, `hit_rate`, and `pcie_share` (0.1.39, #588); `hit_rate` excludes PCIe-read experts, so raising `--pcie-frac` raises it even when decode slows[^strata-docs].
- Thread tuning notes from a 2026-10-02 5090-class report (all **Reported**): leave `--prefill` on `auto` so dynamic chunk sizes borrow expert-cache slots and restore experts after prefill; run the setup `--calibrate` pass to fit the engine; with 128 GB RAM put the ~25 GB n-gram table in RAM via `--ple-io "ram"` instead of SSD[^strata-thread-5090].
- VRAM-headroom and context-cap gotchas from the same thread (**Reported**): `--expert-cache auto` can eat VRAM down to ~700 MiB free, so add `--vram-reserve-mib 1600` for vision headroom; `--max-context 262144` loads then hangs every request (`qsa_block_topk: unsupported geometry or cap` in the log) while 262136 works[^strata-thread-5090].

## Prefill path

- Since 0.1.13 prompts run in chunks up to 8,192 tokens (`--prefill auto`, 32,768 opt-in) sized to borrowed expert-cache slots; experts use llama.cpp's quantized MMQ kernels instead of FP16 expansion; the next layer's experts stream over PCIe during the current layer's attention; the PLE block runs per chunk[^strata-docs].
- Effect on RTX 5070 12 GB, 32K prompt: Q2_0 572 → 1,290 tok/s, IQ3_S 383 → 1,208; output unchanged; needles 5/5 from 1K to 262K (**Reported**)[^strata-docs].
- 0.1.36 fused int8 tensor-core prompt kernels for Q2_0 (RTX 30+): +16–22% prompt speed with teacher-forced KL vs FP16 of 0.009 (previous 0.012) at 32K (**Reported**)[^strata-docs].
- 0.1.39b (#583) sizes the streamed ring in bytes: IQ3_XXS 32K prompts +18.5%/+9%, Coder +3%, IQ3_S unchanged; changes long-prompt bits vs 0.1.39 with IQ3_XXS 8K KL 0.042 (was 0.054) and 32K 0.020 (0.019) against an FP16 prompt path (**Reported**)[^strata-docs].
- **Synthesis:** compare with [vLLM Chunked Prefill](vllm-chunked-prefill.md), where chunking serves batch scheduling; here chunk size is bounded by VRAM borrowed from the expert cache and by keeping the PCIe expert-streaming ring full.

## Determinism

- Greedy output can differ run to run because CPU single-token (ggml) and multi-token kernels round differently and the grouping depends on drafts (#152); `STRATA_IQ_MT_MIN=1` removes draft dependence at −1..−3% IQ3_S decode[^strata-docs].
- Byte-identical repeats through the server additionally need `--prompt-cache 0 --adapt-swaps 0 --pcie-frac 0` because the adaptive tier and PCIe share change where (GPU vs CPU) an expert is rounded (#410); IQ3_XXS test: all three switches gave 1 distinct answer in 4, defaults 2 of 4 (**Reported**)[^strata-docs]. Seed-reproducible sampling needs `--adapt-every 100000` (static residency)[^strata-docs].
- Separately, the engine can flag its own GPU hit path as incorrect: one pasted run warns `--expert-cache` diverges from a cache-off run (first difference at token 40 at 2.97% hits; token 0 at 54.4%) and states timings are real but outputs are not (**Reported** engine self-check)[^strata-thread-65tps].
- Related: [vLLM Batch Invariance](vllm-batch-invariance.md) and [SGLang Deterministic Inference](sglang-deterministic-inference.md) address the analogous batching-dependent nondeterminism in server engines.

## Relationships

- Uses [Qwen3.8-Flash-Next Architecture and Evaluation](qwen3.8-flash-next-architecture.md) — GDN/QSA mixers, gated residual, MTP, and layer-2 n-gram table that define what goes on each tier.
- Related to [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — datacenter serving of the same model, which also offloads PLE/n-gram to the host.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — the Unsloth GGUF plus llama.cpp local route; Strata additionally runs Unsloth UD-IQ4_XS/UD-Q4_K_XL via its SSD tier.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — Strata borrows llama.cpp/ggml kernels but is a model-specific engine rather than a general runtime.
- Related to [vLLM KV Offloading](vllm-kv-offloading.md) — KV-to-CPU tiering in a server engine, versus Strata's expert-weight tiering plus KV streaming.
- Compared in [Narrow Single-Model Inference Engines](narrow-inference-engines.md) — secondhand Carteakey numbers (Strata ~2–2.6x over llama.cpp on Qwen3.8-Flash-Next) and the generality tradeoff behind them.

## Coverage limits

- Source identity is the documentation package `raw/Strata/` (README, HOW_IT_WORKS, MODELS, DETAILS); no git revision was captured. Linked docs (INSTALL, MULTI_GPU, BATCHING, AMD_HIP, UNSLOTH_Q4, ORCA, MCP_SERVER, TROUBLESHOOTING, COMMUNITY_BENCHMARKS, OLDER_GPUS, INTEL_ARC, AI_SETUP), the `Strata-Paper.pdf`, `bench/results/`, SVG/WebP/MP4 media, and translated READMEs are absent from `raw/` and were not inspected.
- All performance and quality figures are project-reported measurements, not reproduced here.
- The 2026-09-24 author-thread rig reports, SM75 patch diffs, screenshots, and linked HF/blog URLs are cited secondhand from comment text; the engine repo was not inspected here[^strata-thread-65tps].
- No credentials or PII found; `some-long-secret` is a placeholder in the docs.
- A YouTube-transcript explainer (narrator-reported, no measurement protocol, no timecodes in the capture) corroborates the tiering mechanism and adds the per-token byte arithmetic, the 34/15/13 ms split, and the ~50%-to-72% cache ramp above; its headline-speed claims are reconciled under [Strata Qwen3.8-Flash-Next Quants and Measured Speed](strata-qwen3.8-flash-next-quants-performance.md)[^strata-video-6x].
- The 2026-10-02 power-limited-5090 thread's fork branch, issue #23, `--vram-reserve-mib`, and `qsa_block_topk` log text are cited secondhand from comment text; the engine repo was not inspected here[^strata-thread-5090].
- The 2026-10-03 complaint-thread figures, `setup.sh` menu text, JSON KV flag, parking flags, fork/PR links, imgur/redd.it screenshots, and localbench/vLLM-recipe URLs are cited secondhand from comment text; the engine repo, weights, screenshots, and linked benchmarks were not inspected here[^strata-thread-bots].

[^strata-thread-5090]: r/LocalLLaMA thread "Strata on a power limited 5090 and 96GB of DDR5-6400" — `../raw/strata-on-a-power-limited-5090-and-96gb-of/index.md` (original post plus comments, 2026-10-02–2026-10-04): `--prefill auto` borrowing, `--calibrate`, `--ple-io "ram"` n-gram tip, VRAM-reserve and 262136 context-cap gotchas, 3090-main/5090-expert-tier 15–30% placement rule, and PCIe/power bandwidth diagnostic.

[^strata-docs]: Strata docs — `../raw/Strata/HOW_IT_WORKS.md` "Who does what" and "Reading long texts"; `../raw/Strata/DETAILS.md` "Speed (measured)" (0.1.36 note, KV streaming, 4-bit KV, K8V4, reproducible greedy output, low-RAM mode, resident, arena mmap, without `experts.bin`, RAM budget, "How much came from where", "Faster prompts"), "Other GPUs (estimated)" (expert-profile note), "Tuning for your PC (`--calibrate`)", "Sharing the GPU" (expert_profile_save), "Current limits (v1)", and "How it works" (tiers, `--ple-io`, 0.1.39b ring); `../raw/Strata/README.md` "How does it work?" and "Credits and license".
[^strata-thread-65tps]: r/LocalLLaMA thread "Qwen3.8-Flash-Next on 12GB VRAM - 65 tokens per second" — `../raw/qwen38flashnext-on-12gb-vram-65-tokens-per-second/index.md` (author post plus comments, 2026-09-24–2026-10-02): KV-cache flush-then-persist lifecycle, `--expert-cache` GPU-hit-path divergence warning, 118K prompt-cache re-request, and auto-vs-explicit expert-cache tuning.

[^strata-thread-bots]: r/LocalLLaMA thread "Yes bots we get it, Strata is good now please stop" — `../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/index.md` (original post plus comments, 2026-10-03–2026-10-04): sparse-attention KV-in-RAM rationale (jmager), transfer-bound vs compute-bound framing (bilinenuzayli), ~50% VRAM-expert estimate (thedirtyscreech), all-core CPU use (ColorsOfCosmos, Ori_553), tiered-storage terminology dispute (Tylnesh, Lugnut1206, Yorn2), `setup.sh` four-model menu and q8/q4 KV choice (nsfnd), fp16 JSON edit (nsfnd), Q8-vs-Q4 KV dispute with localbench link (MerePotato, Hefty_Wolverine_553, A_Moist_Towe1, dannone9), and vLLM fp8 KV-recipe pointer (enternoescape).

[^strata-video-6x]: "The New Way to Run 125B Models 6x Faster Than llama.cpp (Strata)" — `../raw/the-new-way-to-run-125b-models-6x-faster-than-llama.cpp-(strata).md` (YouTube transcript, English; channel, URL, and publish date not captured — content places it after the 2026-10-01 llama.cpp MTP merge): Q2 byte arithmetic (66 GB file, ~34 GB experts, 0.66 GB + 3.5 GB ≈ 4 GB/token), 29 GB / 51B-parameter SSD table at 16 rows (~23 KB)/token, 36 constant-state + 12 ≤2,048-position attention layers, per-layer GPU/CPU split (~34 ms ≈ 15 ms + 13 ms), ~4,500-expert 12 GB cache with ~50%-to-72% ramp, and the "priced every decision in bytes moved per token" design quote.
