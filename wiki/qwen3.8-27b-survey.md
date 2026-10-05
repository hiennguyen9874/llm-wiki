---
type: Synthesis
title: Qwen3.8-27B Ecosystem Survey
description: Cross-variant survey of Qwen3.8-27B covering base architecture, quantized/NVFP4/uncensored/fine-tuned derivatives, speculators, serving engines, reported performance, and hardware-based selection.
tags: [qwen3.8, survey, comparison, gguf, nvfp4, quantization, speculative-decoding, uncensored, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T07:21:32Z }
stale_after: 2027-04-05
sources:
  - id: qwen38
    resource: qwen3.8.md
    title: Qwen3.8 Local Deployment
  - id: community
    resource: qwen3.8-27b-community-variants.md
    title: Qwen3.8-27B Community Variants
  - id: ista
    resource: ista-qwen3.8-27b-gsq-rco-gguf.md
    title: ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF
  - id: dirk
    resource: dirk-qwen3.8-27b-gguf.md
    title: Dirk Qwen3.8-27B Sharp-Template GGUF
  - id: cdiamond
    resource: cdiamond-qwen3.8-27b-imatrix-nvfp4-mtp-gguf.md
    title: Cdiamond Qwen3.8-27B iMatrix NVFP4 MTP GGUF
  - id: gittensor
    resource: gittensor-qwen3.8-27b-nvfp4-rtx5090.md
    title: Gittensor Qwen3.8-27B NVFP4 RTX 5090
  - id: neroued
    resource: neroued-qwen3.8-27b-nvfp4-ninfer.md
    title: Neroued Qwen3.8-27B NVFP4 NInfer Artifact
  - id: hauhaucs
    resource: hauhaucs-qwen3.8-27b-aggressive-mtp-gguf.md
    title: HauhauCS Qwen3.8-27B Aggressive MTP GGUF
  - id: huihui
    resource: huihui-qwen3.8-27b-abliterated-gguf.md
    title: Huihui Qwen3.8-27B Abliterated GGUF
  - id: coletti
    resource: jonathancoletti-qwen3.8-27b-uncensored-gguf.md
    title: JonathanColetti Qwen3.8-27B Uncensored GGUF
  - id: obliteratus
    resource: obliteratus-qwen3.8-27b-obliterated.md
    title: OBLITERATUS Qwen3.8-27B OBLITERATED
  - id: rvn
    resource: rvn-qwen3.8-27b-heretic-abliterated-gguf.md
    title: RVN Qwen3.8-27B Heretic Abliterated Uncensored GGUF
  - id: coldfusion
    resource: davidau-qwen3.8-cold-fusion-gain-gguf.md
    title: DavidAU Qwen3.8-27B Cold Fusion GAIN GGUF
  - id: turbo
    resource: davidau-qwen3.8-turbo-fable-cold-fusion-gguf.md
    title: DavidAU Qwen3.8-27B TURBO Fable Cold Fusion GGUF
  - id: swift
    resource: swift-1.5-qwen3.8-27b-gsq-rco-gguf.md
    title: Swift 1.5 Qwen3.8-27B GSQ-RCO GGUF
  - id: dspark
    resource: qwen3.8-dspark.md
    title: Qwen3.8-27B DSpark Speculator
  - id: dflash2
    resource: dflash2-parallel-speculative-decoding.md
    title: DFlash 2 Parallel Speculative Decoding
  - id: ninfer
    resource: ninfer-single-gpu-inference-engine.md
    title: NInfer Single-GPU Inference Engine
  - id: ninfer4080
    resource: ninfer-4080-16gb-port.md
    title: NInfer 4080 16GB Port
  - id: hyperqwen
    resource: hyperqwen-serving-stack.md
    title: HyperQwen Qwen3.8-27B Serving Stack
---

Qwen3.8-27B is a dense 27B vision-reasoning model with a hybrid Gated DeltaNet/gated-attention stack, a native MTP head, and 256K context. Within weeks it gathered a broad derivative ecosystem: low-bit GGUF ladders (GSQ-RCO, Unsloth Dynamic, imatrix, K_P/K_L), Blackwell NVFP4 checkpoints, uncensored redistributions, thinking-compression fine-tunes, dedicated speculators (DSpark, DFlash2, FastMTP), and single-model engines (NInfer, SparkInfer, HyperQwen)[^qwen38][^community]. This survey compiles those concept pages into one comparison. Every number is **Reported** by its model card or thread. Cross-page rankings are **Synthesis**: hardware, engines, and harnesses differ, so only rows inside one source table compare directly.

## Base model

| Property | Value |
|---|---|
| Architecture | 64 layers: 48 Gated DeltaNet + 16 gated-attention; hidden 5,120, FFN 17,408[^hauhaucs] |
| Vocabulary | 248,320 padded[^hauhaucs] |
| Context | 262,144 native; up to 1M with framework-specific config[^hauhaucs] |
| Modalities | Text, image, video[^hauhaucs] |
| Drafting | One embedded MTP/NextN layer (15 tensors)[^ista][^rvn] |
| Thinking | Hybrid; `xhigh` effort default, plus `medium`/`low` and thinking-off[^qwen38][^dirk] |
| License | Apache-2.0[^coletti] |

- Memory guide (RAM+VRAM): 1-bit 7–8 GB, 2-bit 9–11, 3-bit 12–14, 4-bit 16–19, 6-bit 23–26, 8-bit 31, BF16 56 GB; MTP needs ~1–2 GB extra[^qwen38]. **Reported**.
- Vendor headline scores: SWE-bench Pro 61.7, Terminal Bench 2.1 73.0, GPQA Diamond 89.2, LiveCodeBench v6 90.3, IFBench 79.5 — ahead of Qwen3.6-27B on every listed row[^qwen38]. **Reported**.
- Default thinking sampling: temperature 1.0, top_p 0.95, top_k 20; instruct mode 0.7 / 0.80 / 20[^qwen38]. **Reported**.

## Variant taxonomy

| Family | Variants (wiki page) | Weights changed? |
|---|---|---|
| Official / reference | `Qwen/Qwen3.8-27B`, `-FP8`; Unsloth Dynamic 3.0 GGUF and NVFP4[^qwen38][^dspark] | No |
| Low-bit GGUF | [ISTA GSQ-RCO](ista-qwen3.8-27b-gsq-rco-gguf.md), [Dirk](dirk-qwen3.8-27b-gguf.md) (template only), [Cdiamond NVFP4 GGUF](cdiamond-qwen3.8-27b-imatrix-nvfp4-mtp-gguf.md) | Quantization only |
| NVFP4 serving | [Gittensor RTX 5090](gittensor-qwen3.8-27b-nvfp4-rtx5090.md), [Neroued NInfer](neroued-qwen3.8-27b-nvfp4-ninfer.md); RadixArk, Inferact, QUASAR, NVIDIA (named only)[^community][^gittensor] | Quantization only |
| Uncensored | [HauhauCS](hauhaucs-qwen3.8-27b-aggressive-mtp-gguf.md), [Huihui](huihui-qwen3.8-27b-abliterated-gguf.md), [JonathanColetti](jonathancoletti-qwen3.8-27b-uncensored-gguf.md), [OBLITERATUS](obliteratus-qwen3.8-27b-obliterated.md), [RVN](rvn-qwen3.8-27b-heretic-abliterated-gguf.md) | Refusal-direction edits |
| Thinking-efficient fine-tunes | [Cold Fusion GAIN](davidau-qwen3.8-cold-fusion-gain-gguf.md), [TURBO Fable](davidau-qwen3.8-turbo-fable-cold-fusion-gguf.md), [Swift 1.5](swift-1.5-qwen3.8-27b-gsq-rco-gguf.md) | Retrained |
| Speculators | [RadixArk DSpark](qwen3.8-dspark.md), [DFlash2](dflash2-parallel-speculative-decoding.md), Gittensor DSpark v2 NVFP4, HauhauCS FastMTP-32K | Separate draft |
| Listed only, no page | LM Studio GGUF/MLX, mlx-community MLX, cyankiwi AWQ-INT4 (21 GB), ggml-org GGUF, AtomicChat and bartowski imatrix GGUF[^community] | — |

## Quantization quality versus size

Low-bit GGUF (ISTA table versus BF16 and Unsloth Dynamic; harness and hardware unstated)[^ista]:

| Variant | bpw | GB | AIME25 | GPQA-D | LCB v6 |
|---|---:|---:|---:|---:|---:|
| BF16 | 16.00 | 53.8 | 100.00 | 89.90 | 85.71 |
| GSQ-RCO IQ2_XS | 2.50 | 8.4 | 96.67 | 84.85 | 76.57 |
| UD-IQ2_S | 2.49 | 8.4 | 86.67 | 76.26 | 72.00 |
| GSQ-RCO IQ3_XXS | 3.00 | 10.1 | 100.00 | 88.89 | 84.57 |
| GSQ-RCO IQ3_S | 3.50 | 11.8 | 100.00 | 89.39 | 85.71 |
| UD-IQ3_S | 3.52 | 12.0 | 96.67 | 89.90 | 84.00 |

- **Synthesis:** GSQ-RCO dominates at 2–3 bpw, and the methods converge near 3.5 bpw. Dirk builds on exactly this crossover: GSQ-RCO below ~3 bpw, Unsloth UD above it, in a 14-file 8.8–31.5 GB ladder[^dirk]. Swift 1.5 reuses ISTA's allocations for its own post-train (KLD 0.19 at IQ2_XS down to 0.051 at IQ3_S versus Swift BF16)[^swift].
- Unsloth Dynamic 3.0 is reported >10% better top-1% accuracy at equal size than other providers; Unsloth NVFP4 reports 92–97% top-1 agreement versus BF16 and ~1.5x BF16 throughput on B200[^qwen38]. **Reported**.
- Cdiamond's 5.01-bpw NVFP4 GGUF protects attention, DeltaNet, and late FFN tensors at Q5_K/Q6_K and ties Q4_1 on a short WikiText-2 check (6.1197 vs 6.1127)[^cdiamond]. **Reported**.
- Neroued's NVFP4/FP8 NInfer artifact stays within ±2.5 points of the official BF16 card on four overlapping benchmarks (e.g., GPQA-D 90.40 vs 89.2, IFBench 77.00 vs 79.5); the protocols differ[^neroued]. **Reported**.

NVFP4 checkpoints on one RTX 5090 (vLLM, same harness and sampling)[^gittensor]:

| | Gittensor | QUASAR | NVIDIA |
|---|---:|---:|---:|
| Overall accuracy (328 items) | 79.0% | 80.2% | 78.7% |
| Decode tok/s | 86.8 | 78.5 | 69.5 |
| KV tokens @131K ctx | 300,009 | 249,036 | 209,715 |
| Checkpoint | 17.92 GB | 19.7 GB | 21.0 GB |

- Quality is a statistical tie. What differs is bandwidth and KV headroom: NVIDIA keeps attention/GDN at FP8, QUASAR keeps `lm_head` at BF16, and Gittensor quantizes `lm_head` to NVFP4 and drops MTP[^gittensor]. **Reported**.
- In the same card's serving view, Gittensor decodes 85.8 tok/s on SGLang, RadixArk NVFP4 73.7, and Unsloth NVFP4 42.4 (vLLM, earlier run). Max context is 320,960 / 225,600 / 77,184 respectively[^gittensor]. **Reported**.

## Uncensored variants

| Variant | Method | Refusals | Damage signal |
|---|---|---|---|
| RVN | 3 ARA passes (Heretic) | 0–1/100 (base ~99) | KL 0.0085[^rvn] |
| TURBO Fable | Heretic ARA plus fine-tune/merge | 11/100 at stage 2 | KL 0.0025[^turbo] |
| JonathanColetti | One Heretic search, bf16 | 12/100 (base 98) | First-token KL 0.1191; PPL +0.7%[^coletti] |
| HauhauCS Aggressive | Proprietary profile | 0/465 | Not reported[^hauhaucs] |
| OBLITERATUS V3 | SVD + LEACE blend | Hard and soft refusals removed (manual audit) | MMLU 82.33 vs 84.46 (−2.12pp), STEM −3.3pp[^obliteratus] |
| Huihui | Layers 22–52 ablated, `K_L` requant | Not reported | None reported[^huihui] |

- **Synthesis:** these KL figures use different definitions (first-token versus unspecified) and different prompt sets, so they do not rank the variants. RVN and JonathanColetti publish the most auditable evidence.
- A community NInfer thread ranks JonathanColetti above Huihui (IFBench 81% vs 80%, GPQA-D 84% vs 76%)[^ninfer]. **Reported**.
- Every uncensored family ships MTP-capable files; RVN keeps the head only in `-mtp` twins[^rvn][^huihui][^obliteratus][^turbo]. JonathanColetti notes the head was trained on the unedited model, so acceptance may drop slightly while output stays lossless[^coletti]. **Reported**.

## Thinking-efficient fine-tunes

- Swift 1.5 reports 58.5% fewer thinking tokens at +0.35% score. It ships under its own license and has no verified vision projector[^swift]. **Reported**.
- Cold Fusion GAIN cuts thinking to 1/2–1/10 of base. Q4_K_S runs ~75 tok/s regular and 90+ tok/s with MTP on an RTX 5090 (LMStudio)[^coldfusion]. **Reported**.
- TURBO Fable adds Heretic uncensoring and Fable merge DNA. It claims 735 ARC-C, and tool calling needs at least `q4km`[^turbo]. **Reported**.
- Dirk reaches a similar goal without retraining: the Sharp template defaults to `medium` effort and adds a terseness prompt[^dirk]. **Reported**.

## Speculative decoding

Mean acceptance, default sampling, block 8 (DFlash2 source)[^dflash2]:

| Drafter | GSM8K | HumanEval | MT-Bench | Mean |
|---|---:|---:|---:|---:|
| Native MTP | 5.02 | 3.91 | 3.74 | 4.28 |
| RadixArk DSpark | 4.36 | 3.30 | 3.01 | 3.62 |
| DFlash2 | 5.46 | 4.39 | 4.10 | 4.80 |

- DFlash2 reports 2.7–3.4x autoregressive throughput at batch 1 in SGLang. It runs in SGLang, vLLM, and llama.cpp (PR 27342)[^dflash2]. **Reported**.
- RadixArk DSpark v2 on one H200 (FP8 target): up to 3.16x at concurrency 1 (GSM8K 297.3 tok/s) and 1.85–2.48x at concurrency 8[^dspark]. **Reported**.
- Gittensor's retrained DSpark v2 NVFP4 drafter (1.41 GB) reaches 180.3 tok/s (2.04x), versus 136.9 tok/s (1.68x) for built-in MTP on its 240-prompt harness. In the SparkInfer bench, code accepts τ 6.78 of 8 (4.32x)[^gittensor]. **Reported**.
- HauhauCS FastMTP-32K sidecar plus patched llama.cpp: up to 3.02x document TG versus MTP-off on Blackwell[^hauhaucs]. **Reported**.
- In llama.cpp, embedded MTP pays best at small `n_max` (1–2): ~1.13–1.32x, with gains turning negative past ~4. A standalone Q8_0 draft can beat the fused low-bit head[^coletti]. **Reported**.
- **Synthesis:** acceptance depends on workload (code and structured output accept far more than prose or story) in every source that splits by task[^neroued][^gittensor][^dspark]. Plan speculation per workload, not by a single headline.

## Engines and hardware

Reported single-GPU operating points; protocols differ:

| Hardware | Stack + artifact | Decode | Context | Source |
|---|---|---|---|---|
| RTX 3090 24 GB | HyperQwen (vLLM 0.30.0 patched) | 127 tok/s single; ~1,035 aggregate @64 | 150K | [^hyperqwen] |
| RTX 4080 16 GB | NInfer-4080 + ISTA 3-bit GSQ | 122–262 tok/s (DFlash2/MTP3); ~33–41 no-spec | ~98K | [^ninfer4080] |
| RTX PRO 4000 Blackwell 24 GB | llama.cpp (6 PRs) + Cdiamond | 50.4 tok/s; 59.5 with MTP | 261.5K filled | [^cdiamond] |
| RTX 5090 32 GB | SparkInfer / SGLang + Gittensor | 92.9 / 85.8; 161.7 SGLang+DSpark | 360K / 321K | [^gittensor] |
| RTX 5090 32 GB | NInfer + Neroued NVFP4 | 147.7 (C=1) to 922.4 (C=8) MTP3 aggregate | 262K | [^ninfer][^neroued] |
| RTX PRO 6000 96 GB | llama.cpp + HauhauCS FastMTP | 138–219 tok/s document TG (Q8_K_P to IQ2_M) | 204.8K | [^hauhaucs] |

- NInfer accepts only one RTX 5090 (`sm_120a`) and its own `.ninfer` container, and supports no multi-GPU[^ninfer][^neroued]. Gittensor NVFP4 needs Blackwell `sm_120`, since Hopper loads the files but cannot run NVFP4[^gittensor]. **Reported**.
- For many concurrent users, general engines still win: vLLM 0.28 reaches ~546 tok/s aggregate at 8–16 requests, about 1.6x SparkInfer on the same box[^gittensor]. HyperQwen likewise finds speculation wins below ~8 users and plain batching wins above[^hyperqwen]. **Reported**.

## Selection guide

**Synthesis** from the tables above:

| Constraint | Start with |
|---|---|
| 8–12 GB VRAM | ISTA GSQ-RCO IQ2_S/IQ2_XS, or Dirk GSQ-RCO tiers[^ista][^dirk] |
| 16 GB | ISTA IQ3_S or Dirk UD-IQ4_XS; NInfer-4080 for speed on SM_89[^ista][^dirk][^ninfer4080] |
| 24 GB, long context | Cdiamond NVFP4 GGUF (Blackwell) or Dirk UD-Q4_K_XL/Q5_K_XL; HyperQwen on Ampere[^cdiamond][^dirk][^hyperqwen] |
| RTX 5090, one or few users | Gittensor NVFP4 + DSpark v2 (SparkInfer/SGLang) or Neroued on NInfer[^gittensor][^neroued] |
| Many concurrent users | vLLM/SGLang with an NVFP4 or FP8 checkpoint plus DFlash2 or DSpark[^gittensor][^dflash2][^dspark] |
| Uncensored with least damage | RVN; JonathanColetti for the most transparent evidence[^rvn][^coletti] |
| Fewer thinking tokens | Swift 1.5, Cold Fusion GAIN, or Dirk's template-only route[^swift][^coldfusion][^dirk] |

## Relationships

- Summarizes [Qwen3.8 Local Deployment](qwen3.8.md) and [Qwen3.8-27B Community Variants](qwen3.8-27b-community-variants.md), plus every per-variant page linked in the taxonomy.
- Uses [NInfer Single-GPU Inference Engine](ninfer-single-gpu-inference-engine.md), [NInfer 4080 16GB Port](ninfer-4080-16gb-port.md), and [HyperQwen Qwen3.8-27B Serving Stack](hyperqwen-serving-stack.md) as the engine evidence.
- Uses [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) and [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) as the speculator evidence.
- Related to [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md), which explains how to judge the PPL, KLD, and accuracy claims compared here.

## Contradictions

- RadixArk DSpark size: 1.36B per the QwenDevs post[^community], versus 1.86B (1,857,358,337) per the model card[^dspark]. Unreconciled.
- NVFP4 BF16 reference: NVIDIA reports 88.92 and QUASAR reports 91.41 GPQA Diamond for the same BF16 weights, so leaderboard-style comparisons across NVFP4 cards are unsafe[^gittensor].
- NInfer Qwen3.8-27B MTP3 acceptance: ~45–49% in the engine README table[^ninfer] versus ~58–60% in the Neroued card's corpus runs[^neroued]. The engine revisions, workloads, and acceptance definitions differ, so neither figure is chosen.

## Coverage limits

- Compiled from wiki concept pages only. `raw/` was not reopened, so every claim inherits the coverage limits of its cited page.
- No variant was downloaded or run. All figures are **Reported**, and the cross-page tables are **Synthesis** that mix hardware, engine revisions, and harnesses.
- Variants listed in [Qwen3.8-27B Community Variants](qwen3.8-27b-community-variants.md) without their own page (LM Studio, mlx-community, cyankiwi, ggml-org, AtomicChat, bartowski, Inferact, QUASAR, TWIN-TURBO, ThinkingCap) have no compiled evidence beyond their names.
- Engine flags, compatibility, and speeds are snapshot values; `stale_after` applies.

[^qwen38]: [Qwen3.8 Local Deployment](qwen3.8.md) — sections Model identity, Hardware requirements, Recommended settings, NVFP4 faster inference, Source-reported benchmarks.
[^community]: [Qwen3.8-27B Community Variants](qwen3.8-27b-community-variants.md) — sections Local-use variants, Serving and faster-inference variants, Contradictions.
[^ista]: [ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF](ista-qwen3.8-27b-gsq-rco-gguf.md) — sections Available files, Card-reported results.
[^dirk]: [Dirk Qwen3.8-27B Sharp-Template GGUF](dirk-qwen3.8-27b-gguf.md) — sections What Dirk changes, Thinking-effort controls, Quant ladder and VRAM picks, Why two quantizers.
[^cdiamond]: [Cdiamond Qwen3.8-27B iMatrix NVFP4 MTP GGUF](cdiamond-qwen3.8-27b-imatrix-nvfp4-mtp-gguf.md) — sections Quant recipe and calibration, Measured results, Pinned llama.cpp branch.
[^gittensor]: [Gittensor Qwen3.8-27B NVFP4 RTX 5090](gittensor-qwen3.8-27b-nvfp4-rtx5090.md) — sections Checkpoint identity and recipe, Cross-engine performance, Against the other NVFP4 builds (both tables), Concurrency and prefix reuse, Speculative decoding (DSpark v2).
[^neroued]: [Neroued Qwen3.8-27B NVFP4 NInfer Artifact](neroued-qwen3.8-27b-nvfp4-ninfer.md) — sections Requirements and provenance, Reported performance (one RTX 5090), Reported evaluation.
[^hauhaucs]: [HauhauCS Qwen3.8-27B Aggressive MTP GGUF](hauhaucs-qwen3.8-27b-aggressive-mtp-gguf.md) — sections Method and lineage, Architecture and specs, HauhauCS FastMTP, Measured speeds.
[^huihui]: [Huihui Qwen3.8-27B Abliterated GGUF](huihui-qwen3.8-27b-abliterated-gguf.md) — sections Variant series and ablation scope, Non-standard K_L quantization, Coverage limits.
[^coletti]: [JonathanColetti Qwen3.8-27B Uncensored GGUF](jonathancoletti-qwen3.8-27b-uncensored-gguf.md) — sections Method and lineage, Quantization fidelity, Capability and refusal behaviour, Speculative decoding.
[^obliteratus]: [OBLITERATUS Qwen3.8-27B OBLITERATED](obliteratus-qwen3.8-27b-obliterated.md) — sections V1 to V3 lineage, Reported evaluation.
[^rvn]: [RVN Qwen3.8-27B Heretic Abliterated Uncensored GGUF](rvn-qwen3.8-27b-heretic-abliterated-gguf.md) — sections Lineage and intent, Model architecture, Refusal evaluation.
[^coldfusion]: [DavidAU Qwen3.8-27B Cold Fusion GAIN GGUF](davidau-qwen3.8-cold-fusion-gain-gguf.md) — sections What Cold Fusion changes, Quant packaging: NEO MAX, MTP, and LOW.
[^turbo]: [DavidAU Qwen3.8-27B TURBO Fable Cold Fusion GGUF](davidau-qwen3.8-turbo-fable-cold-fusion-gguf.md) — sections What TURBO changes, Sampling, tool calling, and chat/roleplay, Heretic de-censoring stats.
[^swift]: [Swift 1.5 Qwen3.8-27B GSQ-RCO GGUF](swift-1.5-qwen3.8-27b-gsq-rco-gguf.md) — sections Base model and thinking efficiency, Available files, Usage, Quantization procedure.
[^dspark]: [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) — sections Model identity and architecture, Acceptance length, Throughput (H200, concurrency 1 and 8).
[^dflash2]: [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — Qwen3.8-27B acceptance table and Deployment section.
[^ninfer]: [NInfer Single-GPU Inference Engine](ninfer-single-gpu-inference-engine.md) — sections Identity and product boundary, Reported performance (RTX 5090), Reported field reports (r/LocalLLM uncensored 5090 thread).
[^ninfer4080]: [NInfer 4080 16GB Port](ninfer-4080-16gb-port.md) — sections What changed versus upstream NInfer, Reported performance on RTX 4080.
[^hyperqwen]: [HyperQwen Qwen3.8-27B Serving Stack](hyperqwen-serving-stack.md) — sections Reported numbers behind the letters, What transfers.
