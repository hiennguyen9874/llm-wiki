---
type: Concept
title: NInfer 4080 16GB Port
description: Community SM_89 port serving Qwen3.8-27B-GSQ at ~100K context on 16GB RTX 4080/4060Ti with DFlash2/MTP and compressed KV.
tags: [serving, speculative-decoding, quantization, kernels, qwen, long-context]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T12:00:00Z }
stale_after: 2027-04-05
sources:
  - id: ninfer-4080-thread
    resource: ../raw/i_built_ninfer_4080_for_16gb_class_gpus.md
    kind: discussion
    title: I built Ninfer 4080 for 16GB class GPUs
---

NInfer-4080 is a community port of NInfer for 16 GB-class `SM_89` GPUs, validated on an RTX 4080, serving `ISTA-DASLab-Qwen-3.8-27B-GSQ` at up to ~98–100K context with DFlash2/MTP speculation and compressed KV cache, reporting roughly 1,900–2,720 tok/s prefill and roughly 122–262 tok/s speculative decode depending on depth and speculator[^ninfer-4080-thread]. All throughput, accuracy, cost, and compatibility figures below are **Reported** from a single r/LocalLLaMA post plus its comments, without independent verification here and with the repo, weights, ledger, and run scripts uninspected.

## Identity and goals

- Author `u/roofkid` describes 20+ years in software engineering/architecture with no GPU-kernel background, approaching the port as product owner/requirements plus business decisions and software-engineering practice[^ninfer-4080-thread].
- Guiding principles were: fit RTX 4080 16 GB, use `ISTA-DASLab-Qwen-3.8-27B-GSQ`, use DFlash2 speculative decoding, reach 100K+ context, beat general engines such as llama.cpp/vLLM on prefill and generation, verify accuracy after changes, build cheaply with DeepSeek V4.1 Flash, use Pi as harness, and ship a Docker runtime[^ninfer-4080-thread].
- Project lives at `github.com/roofkid/ninfer-4080` on the `rtx4080-port` branch with roughly 30 semantic commits; the author calls this v1 a Pareto-80% state with no further significant Qwen3.8-27B effort planned[^ninfer-4080-thread].
- **Evidence class:** **Reported** — per the SCOPE benchmark rule the numbers below state hardware, model, depth, and metric but engine revision, sampling, harness version, and repeat protocol are unstated, so they are not comparable benchmarks yet.

## What changed versus upstream NInfer

- Added a quantization recipe converting the base `ISTA-DASLab/Qwen3.8-27B-3Bit-GSQ` safetensors checkpoint to `.ninfer` format without touching weights; Vision Tower, MTP head, and z-lab DFlash2 are included in the artifact and activated by launch flags[^ninfer-4080-thread].
- Added Q3 CUDA kernels for NInfer, which previously focused on NVFP4 and higher; the author invites porting those commits from `SM_89` to `SM_120` but does not judge difficulty[^ninfer-4080-thread].
- The GSQ checkpoint does not include RCO; the author understands it was the basis for ISTA-DASLab GGUFs and did not pursue RCO because reported benchmarks matched GGUF values[^ninfer-4080-thread].
- Special thanks are given to prior NInfer workers and specifically `sergiuszm` for the NInfer-4090 `SM_89` heavy lifting, plus ISTA-DASLab for the GSQ safetensors checkpoint[^ninfer-4080-thread].

## Reported performance on RTX 4080

- Headline maxima: 2,720 tok/s prefill and 262 tok/s generation on the RTX 4080 16 GB setup[^ninfer-4080-thread].
- Depth table with DFlash2 prefill, MTP3 decode, and DFlash2 `K=7` decode; parenthetical percentages are preserved as written without a stated denominator[^ninfer-4080-thread]:

| Depth | Prefill tok/s (DFlash2) | MTP3 decode tok/s | DFlash2 K=7 decode tok/s |
|---|---:|---:|---:|
| 8K | 2,719.9 | 151.2 (100%) | 166.7 (54.0%) |
| 32K | 2,424.9 | 141.7 (100%) | 262.3 (100%) |
| 64K | 2,125.5 | 130.7 (100%) | 239.1 (100%) |
| 98K | 1,895.1 | 122.3 (100%) | 212.7 (98.2%) |

- Greedy no-speculation baseline supplied on request, described as matching the author's llama.cpp greedy numbers and showing the gain comes from speculation[^ninfer-4080-thread]:

| Depth | Prefill tok/s | No-spec decode tok/s |
|---|---:|---:|
| 8K | 2,770.97 | 41.28 |
| 32K | 2,473.53 | 39.44 |
| 64K | 2,160.35 | 36.81 |
| 98K | 1,917.89 | 32.88 |

- Real-work feel: 2K+ prefill on long prompts, about 150–200 tok/s decode on coding and about 100 tok/s on prose, subjectively much faster than the author's prior `beellama` daily driver at the same benchmark results[^ninfer-4080-thread].
- Accuracy checks used MBPP and HumanEval for ~30-minute turnaround: MBPP 90–92%, HumanEval 95–96%, with tiny degradations treated as measurement noise and attributed mainly to KV quantization[^ninfer-4080-thread].

## Context versus KV-accuracy trade

- Reaching 100K on 16 GB requires heavy KV compression because full 256K F16 context on Qwen3.8-27B needs exactly 16 GB VRAM for KV alone in the author's accounting[^ninfer-4080-thread].
- Shipped KV choice is `rk4v4-e8`; the author previously used `kvarn5/kvarn5` on `beellama` and reports no measurable difference after benchmarking, plus no subjective "fast garbage" effect[^ninfer-4080-thread].
- Accuracy ordering from the author's measurements is Int8 above `rk8v4a-e8` above `rk4v4-e8`; switching to Int8 KV keeps the same speed but drops context to about 50K, so context can be traded for accuracy[^ninfer-4080-thread].

## Hardware compatibility

- Architecture rule stated in comments: 3xxx is `SM_86`, 4xxx is `SM_89`, 5xxx is `SM_120`; 4xxx 16 GB cards have a good chance of running unmodified but slower, while 3xxx/5xxx need porting work[^ninfer-4080-thread].
- RTX 4060Ti 16 GB is confirmed working by a commenter but capped at about 92K total context, with vision enabled failing to allocate at 100K; reported spot numbers at 40–50% context use are prose 66 tok/s decode with 1,050 tok/s prefill and coding 96 tok/s decode with about 800 tok/s prefill[^ninfer-4080-thread].
- That 4060Ti setup is undervolted/power-limited on a PCIe 3.0 x1 secondary slot, needed `CUDA_VISIBLE_DEVICES=1` in dual-GPU, hung on "Creating CUDA graphs"/"Warming up" until `--no-cuda-graph`, and the author notes Windows plus an open browser or dGPU-driven display can steal the headroom needed for 100K[^ninfer-4080-thread].
- Isolated 4060Ti greedy report: no-spec 20.17 tok/s versus MTP3 70.98 tok/s, against the 4080 MTP3 reference 151.2 tok/s; the author treats the 4060Ti MTP number as roughly matching expectation at about 50%[^ninfer-4080-thread].
- RTX 4070Ti 16 GB is expected to run slower for the same memory-bandwidth/compute reason but was untested by the author; the 12 GB 4070Ti variant is advised to use MTP rather than DFlash2 plus text-only mode to save VRAM[^ninfer-4080-thread].
- RTX 5060Ti/5060/5070/5070Ti and GTX 980 are answered as not expected to start because they are not 4xxx 16 GB `SM_89` targets; Blackwell `sm120a`(range) needs separate work[^ninfer-4080-thread].
- A separate `ninfer-all` fork and a 4070Ti-via-m.2 `swift-bonsai-2` 100K report are mentioned by commenters only and were not tested by the author[^ninfer-4080-thread].

## Run and ops notes

- Docker runtime is offered for easy runs, and Windows users can run via Docker GPU passthrough or compile from source; run-script pointers name `scripts/run-ninfer-4080.bat` around line 144+ for 12 GB/text-only/MTP settings[^ninfer-4080-thread].
- The author returned to `xhigh` thinking on Qwen3.8-27B because speed hides the cost, and hid thinking blocks again as unreadable at that pace[^ninfer-4080-thread].
- Prefill speed is framed as the UX surprise: first long-prompt streaming felt immediate like a cloud endpoint versus 5–10 s waits without a cached system prompt, while at these prefill rates the context window fills in about 40 seconds[^ninfer-4080-thread].
- Initial memory-throughput measurements were around 200 GB/s against a 720 GB/s device ceiling, which the author cites as evidence for how much general engines leave on the table; cited narrow-engine peers are `vllm-radiance` for R9700, NInfer variants for CUDA, and Splash for Metal[^ninfer-4080-thread].

## Agentic build method and cost

- Built with DeepSeek V4.1 Flash for cost efficiency, about 2B tokens for about $13 using off-hours plus low cache-read pricing; the author notes electricity may now cost more than those tokens[^ninfer-4080-thread].
- Harness was Pi with only non-cosmetic extensions `hashline edit pro` plus internet search via Ketch through local SearXNG with a self-written skill[^ninfer-4080-thread].
- Process was test-driven: start from a `grill-me` skill interrogation of the guiding principles, try one idea at a time, keep port-ledger and RTX-4080 plan docs (AI-maintained), reject ideas that tie or regress, over about two weekends[^ninfer-4080-thread].
- The author reports writing roughly one CUDA tutorial snippet in a lifetime, relying instead on conceptual LLM/hardware understanding plus engineering and agentic practices[^ninfer-4080-thread].

## Contradictions

- Decode-versus-KV dispute: one commenter reports roofline work on `r9700`/llama.cpp finding under 5% decode headroom and attributes narrow-engine gains to quantized-KV compromise, while the author replies that Int8 KV costs half the context with identical speed in this setup and asks whether `vllm-radiance` was tried; neither side is chosen here[^ninfer-4080-thread].
- Strata positioning: when asked for a Strata-Gwen port, the author says Strata already excels and differs architecturally — NInfer keeps everything in VRAM while Strata offloads heavily to RAM/disk — so 4080 owners with enough system RAM can use Strata today[^ninfer-4080-thread].

## Relationships

- Related to [NInfer Single-GPU Inference Engine](ninfer-single-gpu-inference-engine.md) — upstream `SM_120a`/RTX-5090 NInfer this port forks for `SM_89` 16 GB cards with added Q3 kernels and GSQ conversion.
- Related to [Narrow Single-Model Inference Engines](narrow-inference-engines.md) — one-model/one-GPU-family instance extending the ninfer row from 5090-only to 16 GB 4xxx cards, with the generality-tax and lifespan-lock-in trade still applying.
- Uses [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — the speculation path behind the DFlash2 `K=7` decode column and the z-lab DFlash2 weights bundled in this port.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — general GGUF/NVFP4 local route for the same Qwen3.8-27B family served here as a GSQ `.ninfer` artifact.
- Related to [KV Cache Compression and Optimization](kv-cache-compression-optimization.md) — taxonomy behind the `rk4v4-e8` versus `rk8v4a-e8` versus Int8 context-for-accuracy trade reported here.
- Related to [Speculative Decoding Foundations](speculative-decoding-foundations.md) — draft-verify-accept mechanism explaining why no-spec decode matches llama.cpp while MTP/DFlash2 decode is several times faster here.

## Coverage limits

- Only `../raw/i_built_ninfer_4080_for_16gb_class_gpus.md` was inspected statically; no commands were executed.
- `github.com/roofkid/ninfer-4080`, the `rtx4080-port` branch and its ~30 commits, port-ledger and RTX-4080 plan docs, `scripts/run-ninfer-4080.bat`, Docker image, `ISTA-DASLab/Qwen3.8-27B-3Bit-GSQ` weights, `byteshape.com` GSQ article, `beellama` baseline, `ninfer-all` and `gem16` links, M4-48GB higher-quant comparisons, and MBPP/HumanEval harnesses were not inspected.
- Post date, engine version/commit, sampling, harness version, and measurement protocol are unstated in the capture; vote count (55) and comment count (54) are capture-time values.
- No sensitive values found.

[^ninfer-4080-thread]: u/roofkid, "I built Ninfer 4080 for 16GB class GPUs" — `../raw/i_built_ninfer_4080_for_16gb_class_gpus.md` (r/LocalLLaMA post plus 54 comments): guiding principles, `roofkid/ninfer-4080` `rtx4080-port` branch with ~30 commits, `ISTA-DASLab-Qwen-3.8-27B-GSQ` plus DFlash2 at 100K on RTX 4080 16 GB, Results depth table (8K/32K/64K/98K prefill plus MTP3 and DFlash2-K=7 decode with percentages), greedy no-spec table on request (8K–98K prefill plus 41.28–32.88 tok/s), MBPP 90–92% and HumanEval 95–96% with KV-quant attribution, `rk4v4-e8` versus `kvarn5` versus Int8 context trade with 256K-F16-equals-16GB claim, `SM_86`/`SM_89`/`SM_120` compatibility rule, 4060Ti 92K/66–96 tok/s report with `CUDA_VISIBLE_DEVICES`/`--no-cuda-graph` notes, 4070Ti-16GB expectation and 12GB MTP/text-only advice, 5xxx/GTX-980 non-support answers, Q3-kernel plus GSQ-recipe plus no-RCO notes, Docker/Windows/`run-ninfer-4080.bat` pointers, Pi plus DeepSeek-V4.1-Flash ~2B-tokens-for-$13 plus `grill-me`/TDD/two-weekend method, 200-vs-720-GB/s and prefill-UX learnings, Strata-VRAM-versus-offload distinction, and decode-versus-KV-quant dispute.
