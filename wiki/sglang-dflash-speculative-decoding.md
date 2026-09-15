---
type: Concept
title: SGLang DFlash Speculative Decoding
description: Block-diffusion drafting with KV injection on the Spec V2 overlap engine for higher throughput than MTP and EAGLE baselines.
tags: [sglang, speculative-decoding, dflash, diffusion]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T17:00:00Z }
sources:
  - id: dflash-v2
    resource: ../raw/2026-06-15-next-generation-speculative-decoding-dflash-v2/index.md
    title: "The next generation of speculative decoding: DFlash and Spec V2"
  - id: nemotron-dflash
    resource: ../raw/DFlash.md
    title: NVIDIA Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash
  - id: dflash2
    resource: ../raw/DFlash2.md
    title: "DFlash 2: Keep Drafting Parallel"
---

DFlash pairs a lightweight block-diffusion draft model that proposes a whole token block in one forward pass with per-layer KV injection of target-model hidden states, served on SGLang's Spec V2 overlap engine to beat both baseline and native MTP throughput[^dflash-v2].

## How DFlash works

Autoregressive LLM decoding generates one token at a time with low arithmetic intensity; speculative decoding uses a small fast drafter to propose tokens for parallel target verification with no quality impact[^dflash-v2]. EAGLE-series and native MTP modules still draft autoregressively, moving the sequential bottleneck into the drafter[^dflash-v2].

DFlash replaces sequential drafting with two ideas[^dflash-v2]:

- **Parallel block-diffusion drafting:** a small diffusion drafter generates an entire block of draft tokens in parallel in a single forward pass, which suits GPUs/TPUs better than one-by-one drafting.
- **KV injection:** instead of only feeding target features at the draft input, target context hidden states are projected and injected directly into the KV cache of every draft layer. The drafter skips modeling full context from scratch and focuses on the next block using the same tensors as later target layers. This scales better with draft depth than EAGLE-style input-only conditioning, whose signal fades in deeper drafters.

Directly training a small block-diffusion drafter alone gives low acceptance length, while using a large diffusion LLM such as SpecDiff-2 as drafter adds memory and drafting cost; KV injection is what keeps the drafter small while retaining acceptance[^dflash-v2]. Xiaomi MiMo v2.5-Pro-UltraSpeed uses DFlash to exceed 1k output tok/s[^dflash-v2].

## Why it is fast

Speedup depends on accepted tokens per cycle and extra draft cost; DFlash improves both because diffusion lowers draft cost and injection raises acceptance[^dflash-v2].

For Qwen3-4B with 5-layer EAGLE-3 versus 5-layer DFlash drafters on the same data, reported as `acc_len / speedup`[^dflash-v2]:

| Task | EAGLE-3 (5 layers) | DFlash |
| --- | --- | --- |
| GSM8K | 4.2 / 2.1x | **4.2 / 3.3x** |
| HumanEval | 4.3 / 2.2x | **4.0 / 3.2x** |
| MT-Bench | 3.1 / 1.4x | **3.0 / 2.2x** |

Diffusion-only ablation still beats EAGLE-3 end to end despite lower acceptance, showing the drafting-cost win[^dflash-v2]:

| Task | EAGLE-3 (5 layers) | DFlash (diffusion only) |
| --- | --- | --- |
| GSM8K | 4.2 / 2.1x | **3.5 / 2.9x** |
| HumanEval | 4.3 / 2.2x | **3.5 / 2.9x** |
| MT-Bench | 3.1 / 1.4x | **2.6 / 2.0x** |

Injection-only ablation in autoregressive mode raises acceptance over EAGLE-3, showing the draft-quality win[^dflash-v2]:

| Task | EAGLE-3 (5 layers) | DFlash (injection only) |
| --- | --- | --- |
| GSM8K | 4.2 / 2.1x | **4.8 / 2.4x** |
| HumanEval | 4.3 / 2.2x | **4.6 / 2.3x** |
| MT-Bench | 3.1 / 1.4x | **3.4 / 1.5x** |

A 5-layer DFlash drafter generating 4, 8, or 16 tokens has much lower drafting latency than a single-layer EAGLE-3 drafter producing 4 tokens; autoregressive draft cost grows roughly linearly with draft length, forcing shallow drafters, while DFlash stays nearly flat across block sizes[^dflash-v2].

## SGLang implementation

SGLang first added DFlash to the V1 speculative engine, then to the V2 engine that is now default[^dflash-v2]. The V1 engine is now deprecated[^dflash-v2].

V1 work added a `DFlashWorker` controlling draft execution and a `DFlashDraftModel` it drives, plus cross draft-target KV-cache integration for injection[^dflash-v2]. As with other SGLang speculation paths, the draft worker talks to the scheduler via `forward_batch_generation` and wraps a target worker for verification passes[^dflash-v2].

The KV-injection novelty ties draft and target state: EAGLE keeps a fully private draft KV cache from projection of draft latents, while DFlash passes target latents through a draft KV projection[^dflash-v2]. To avoid storing those latents in precious KV-cache space and to preserve radix-cache sharing across same-prefix requests, SGLang runs the draft KV projection ahead of the rest of the draft forward pass as immediate materialization, using a layer-batched linear projection and a fused Triton kernel for norm+RoPE post-processing[^dflash-v2].

## Spec V2 overlap scheduling

V2 targets host-device synchronization overhead rather than only GPU kernels[^dflash-v2]. Its overlap scheduler overlaps[^dflash-v2]:

1. host-side `pop_and_process` cleanup after GPU batch N-1 with GPU work on batch N;
2. host KV allocation in `prepare_for_decode` for batch N with GPU work on batch N-1.

On Qwen3-8B, single B200, concurrency 32, V2 optimizations raised throughput from ~11.4 ktok/s to ~15.3 ktok/s, over 33%[^dflash-v2]. Enable the overlap plan stream when serving DFlash[^dflash-v2]:

```shell
export SGLANG_ENABLE_OVERLAP_PLAN_STREAM=1
```

## Performance for Qwen3.5-397B-A17B

The jointly released DFlash drafter for Qwen3.5-397B-A17B beats baseline and native MTP in every tested setting across GSM8K, HumanEval, MT-Bench, MATH500, MBPP, and concurrencies 1–32[^dflash-v2].

Headline HumanEval setting is Qwen3.5-397B-A17B BF16, greedy decoding, thinking enabled, max new tokens 4096, 8xB200 on Modal, acceptance averaged across requests, draft sizes tuned for max throughput with MTP 7 steps and DFlash block 16[^dflash-v2]:

- Baseline: 203 tok/s (1.00x)
- MTP: 558 tok/s (2.75x)
- DFlash: 875 tok/s (4.31x)

That is >4.3x baseline and ~1.5x MTP at concurrency 1 on HumanEval[^dflash-v2].

The wider sweep compares baseline against MTP steps 3/7/15 and DFlash blocks 4/8/16[^dflash-v2]. Annotated best throughputs at concurrency 1 are 711 tok/s (3.48x) on GSM8K, 832 tok/s (4.07x) on MATH500, 875 tok/s (4.31x) on HumanEval, 808 tok/s (3.95x) on MBPP, and 546 tok/s (2.69x) on MT-Bench; at concurrency 32 the best are 6159 tok/s (2.37x), 6910 tok/s (2.64x), 6784 tok/s (2.77x), 6681 tok/s (2.59x), and 4763 tok/s (1.88x) respectively, with DFlash block 8 or 16 winning depending on task and concurrency[^dflash-v2]. Reproduction details are in the Hugging Face model repo benchmark directory[^dflash-v2].

## Deployment

Released drafters[^dflash-v2]:

- `z-lab/Qwen3.5-397B-A17B-DFlash`
- `modal-labs/Qwen3.5-397B-A17B-DFlash`
- `lmsys/Qwen3.5-397B-A17B-DFlash`
- Z Lab [DFlash collection](https://huggingface.co/collections/z-lab/dflash) for additional target models

Example SGLang launch from the source[^dflash-v2]:

```shell
export SGLANG_ENABLE_OVERLAP_PLAN_STREAM=1

python -m sglang.launch_server \
  --model-path Qwen/Qwen3.5-397B-A17B \
  --trust-remote-code \
  --speculative-algorithm DFLASH \
  --speculative-draft-model-path modal-labs/Qwen3.5-397B-A17B-DFlash \
  --speculative-dflash-block-size 8 \
  --speculative-draft-attention-backend fa4 \
  --attention-backend trtllm_mha \
  --linear-attn-prefill-backend triton \
  --linear-attn-decode-backend flashinfer \
  --mamba-scheduler-strategy extra_buffer \
  --tp-size 8 \
  --max-running-requests 32 \
  --cuda-graph-max-bs-decode 32 \
  --cuda-graph-backend-prefill tc_piecewise \
  --enable-flashinfer-allreduce-fusion \
  --mem-fraction-static 0.8 \
  --host 0.0.0.0 \
```

The same block-diffusion plus KV-injection approach applies to most target LLMs; the source invites teams wanting a custom DFlash speculator to contact Z Lab or Modal[^dflash-v2]. A Modal low-latency SGLang example is also linked from the source[^dflash-v2].

A vLLM/llama.cpp DFlash checkpoint example is [Nemotron 3.5 Lightning DFlash Speculator](nemotron-3.5-lightning-dflash.md): `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash` for Nemotron-3.5-Lightning-30B-A3B targets with an 833M dense-GQA drafter, SPEED-Bench draft-length-7 overall acceptance 3.16, and low-concurrency data-centre/workstation serving on H100, GB200, and RTX 5090[^nemotron-dflash].

## DFlash 2 upgrade

[DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) keeps the one-pass DFlash design and adds a top-16 parallel path selector (+2.0M params, +0.6% cycle latency) plus a block-local two-tap dynamic convolution (+16.5M params, +0.7% latency) for about 21% higher acceptance at about 1.3% combined latency on the reported Qwen3.5-4B setup[^dflash2]. Day-zero drafters are `incoai/Qwen3.8-27B-DFlash2` and `incoai/Muse-Glimmer-30B-DFlash2`, served in SGLang with `--speculative-algorithm DFLASH`[^dflash2].

## Relationships

- Related to [DFlash Block Diffusion Speculative Decoding](dflash-block-diffusion.md) — original DFlash paper method, training, and benchmark detail behind this serving path.
- Related to [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — one-pass upgrade with path selection and local convolution; see that page for selector/convolution detail and Qwen3.8-27B / Muse Glimmer acceptance.

- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — base EAGLE/MTP entry; DFlash is the parallel-diffusion alternative served on Spec V2.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — canonical reference for launch, parallelism, memory, and backend flags used in the DFlash command.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — backend selection behind the `fa4`, `trtllm_mha`, Triton, and FlashInfer choices in the example.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — DeepSeek-V4 native MTP path versus external DFlash drafter comparison point.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — autoregressive EAGLE baseline DFlash is benchmarked against.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native-MTP throughput baseline DFlash beats on Qwen3.5-397B-A17B.
- Related to [vLLM Dynamic Speculative Decoding](vllm-dynamic-speculative-decoding.md) — vLLM dynamic-K table is tested with DFlash among other methods.
- Related to [Nemotron 3.5 Lightning DFlash Speculator](nemotron-3.5-lightning-dflash.md) — vLLM/llama.cpp DFlash checkpoint for Nemotron-3.5-Lightning-30B-A3B with SPEED-Bench acceptance evidence.

## Coverage limits

- All four source images were inspected: headline throughput bars, architecture diagram, concurrency 1/32 sweep, and EAGLE-3 versus DFlash draft-latency chart; numeric claims above come from source text plus chart annotations.
- The original DFlash paper method, training, and systematic benchmarks are now compiled in [DFlash Block Diffusion Speculative Decoding](dflash-block-diffusion.md); SpecDiff-2, Medusa/EAGLE/MTP papers, host-overhead blog, SGLang PR diffs beyond the source summary, and Hugging Face benchmark reproduction scripts were not inspected beyond the descriptions cited here[^dflash-v2].
- Launch flags, block size 8, and MTP 7-step / DFlash block-16 headline choices are workload-specific optima from the source setup, not universal defaults[^dflash-v2].

[^dflash-v2]: The next generation of speculative decoding: DFlash and Spec V2 — `../raw/2026-06-15-next-generation-speculative-decoding-dflash-v2/index.md`.
[^nemotron-dflash]: NVIDIA Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash — `../raw/DFlash.md`.
[^dflash2]: DFlash 2: Keep Drafting Parallel — `../raw/DFlash2.md`.
