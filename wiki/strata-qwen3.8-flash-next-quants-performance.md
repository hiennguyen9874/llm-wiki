---
type: Concept
title: Strata Qwen3.8-Flash-Next Quants and Measured Speed
description: Which Qwen3.8-Flash-Next quantization (GSQ-RCO Q2_0/IQ2_XS/IQ3_XXS/IQ3_S, expert-pruned Coder, Swift 1.5, Unsloth UD-IQ4_XS/UD-Q4_K_XL) fits which RAM under Strata, with measured prompt/output tok/s on RTX 5070 and RX 9070 XT.
tags: [strata, qwen3.8-flash-next, quantization, gguf, ista-daslab, gsq-rco, expert-pruning, unsloth, benchmark, local-inference, consumer-gpu]
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
  - id: strata-thread-sep30
    resource: ../raw/qwen38-flash-next-istadaslab-gguf-50ts-tg-and/index.md
    scope: ../raw/qwen38-flash-next-istadaslab-gguf-50ts-tg-and/
    kind: discussion
    title: "Qwen3.8 flash next ISTA-DASLab GGUF 50t/s TG and 1500t/s PP with 12GB VRAM and 64GB RAM Laptop on 'Strata' engine (r/LocalLLaMA)"
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

Under [Strata's tiered offload](strata-tiered-moe-offload.md), the binding constraint for Qwen3.8-Flash-Next on a PC is system RAM (it must hold the experts plus ~10 GB), while VRAM size sets speed; the project ships ISTA-DASLab's GSQ-RCO GGUF quantizations in four sizes, an expert-pruned Coder for 32 GB machines, UkisAI's shorter-thinking Swift 1.5 fine-tune, and Unsloth 4-bit variants that spill experts to SSD[^strata-docs]. All numbers below are **Reported** project measurements with one code-agent prompt per length, 256 generated tokens, and MTP speculation on[^strata-docs]. Independent user reports from a 2026-09-30 r/LocalLLaMA thread are collected in a separate section below; those figures are likewise **Reported** and lack a controlled protocol[^strata-thread-sep30]. A second, earlier thread started 2026-09-24 by the engine author adds author-measured 128K tables plus further independent rig reports; its figures are likewise **Reported** with no shared protocol and one internal headline/body tension noted below[^strata-thread-65tps]. A third thread (2026-10-02–2026-10-04, power-limited RTX 5090 + 96 GB DDR5-6400) adds high-RAM 5090-class numbers plus an eddoursul-fork UD-Q4_K_XL setup report; all its figures are likewise **Reported** with engine version unstated and no shared protocol[^strata-thread-5090].

## Pick by RAM

| RAM | Recommendation | Reason |
| --- | --- | --- |
| 32 GB | Coder | Only size whose experts (23 GB) fit; with a 24 GB GPU, Q2_0/IQ2_XS also run via low-RAM mode[^strata-docs] |
| 48 GB | IQ2_XS (or Q2_0) | Larger sizes do not fit[^strata-docs] |
| 64 GB | IQ2_XS recommended; IQ3_XXS / IQ3_S fit | IQ3_S with little else open[^strata-docs] |
| ≥96 GB | IQ3_S or Unsloth UD-IQ4_XS | Room for the largest sizes[^strata-docs] |

Fit rule: RAM ≥ experts + ~10 GB, with experts of 34 GB (Q2_0), 35.5 (IQ2_XS), 43 (IQ3_XXS), 50 (IQ3_S), 23 (Coder); dense weights go to the GPU and shard 2 (the ~29 GB n-gram lookup table) stays on SSD; a bigger GPU does not lower RAM need except in low-RAM mode[^strata-docs].

## Sizes

| Size | RAM+VRAM need | Download | Quality claim |
| --- | ---: | ---: | --- |
| Q2_0 | 37.6 GB | 66 GB | good |
| IQ2_XS | 39.2 GB | 68 GB | better (recommended) |
| IQ3_XXS | 47.0 GB | 76 GB | great |
| IQ3_S | 54.8 GB | — | "matches the full model on the published tests" (original only) |

Sizes and quality labels from the project tables[^strata-docs]; the MTP draft layer adds ~6 GB download (+1 GB with images), and Q2_0 on AVX-512 CPUs writes a one-time ~40 GB repacked layout[^strata-docs].

- **Synthesis:** Strata's ~38–55 GB footprint is well below the 75 GB minimum quoted for Unsloth's 1-bit GGUF in [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md), mainly because Strata leaves the n-gram table on SSD and counts only RAM+VRAM; the figures are not directly comparable quality-for-size.

## Variants

- **Coder (ISTA-DASLab, Apache-2.0 per card):** keeps 256 of 512 experts per layer (still 10 active), chosen with RCO on code, agentic, and vision calibration data; authors report 91.3% of full-model SWE-bench Verified and 98.7% of LiveCodeBench v6 (**Reported**)[^strata-docs]. Named IQ1_M for 1.89 bits per original parameter, kept experts stored like IQ3_S; shard 1 is 29.6 GB, 262K context fits on 64 GB; shipped profile gives 72% GPU expert hits on a 12 GB card[^strata-docs]. Weaker outside code and in non-English text, including CJK where #438 saw wrong or looping Chinese answers[^strata-docs].
- **Swift 1.5 (UkisAI, Swift Open License 1.0):** fine-tune claiming 63% fewer thinking tokens, 1.8× sooner answers, <1% accuracy loss (**Reported**); same architecture and per-token speed (4K IQ2_XS 465/78.7 vs original 467/78.3 prompt/output tok/s); no IQ3_S; authors recommend IQ2_XS[^strata-docs]. Project spot check: 8/8 on 8 reasoning questions for both, Swift 1,234 output tokens in 28 s vs original 2,682 in 46 s — explicitly "not a benchmark"[^strata-docs].
- **Unsloth UD-IQ4_XS:** regular choice from 0.1.39 (engine ≥0.1.38, ≥48 GB RAM); 94 GB download, 59.5 GB experts (IQ3_S and IQ4_NL), between IQ3_S and UD-Q4_K_XL in quality; RAM minus 24 GB of experts kept in RAM, rest from SSD until ~80 GB RAM[^strata-docs]. See [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md).
- **Unsloth UD-Q4_K_XL (experimental):** 111 GB download, 72–77 GB experts, closest to full model; 7–8.5 tok/s on 64 GB + RTX 5070 12 GB; needs NVMe and one NVIDIA GPU, no images; picks llama.cpp's token at 97.5–99% of short greedy positions and 90–91% after a 16K prompt, differing mostly at near-ties (**Reported**)[^strata-docs].
- **OrcaRouter Uncensored IQ3_XXS:** manual setup only, needs a packing conversion[^strata-docs].

## Measured speed (engine 0.1.26, RTX 5070 12 GB, Ryzen 5 7600, 64 GB DDR5-5200, Windows)

Settings: `--prefill auto`, 8-bit KV above 4K, KV streaming from 64K; "262K" is a 259,943-token prompt[^strata-docs].

| Model | Prompt 4K | Prompt 32K | Prompt 128K | Output 4K | Output 32K | Output 128K | Output 262K |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Q2_0 | 1,299 | 2,171 | 2,107 | 93.0 | 81.8 | 73.7 | 60.3† |
| IQ2_XS | 1,256 | 2,092 | 1,752 | 78.6 | 76.3 | 62.7 | 52.8† |
| IQ3_XXS | 1,007 | 1,745 | 1,602 | 61.6 | 58.5 | 49.0 | — |
| IQ3_S | 913 | 1,624 | 1,443 | 53.3 | 48.3 | 45.5 | — |
| Coder | 1,583 | 2,177 | 2,208 | 55.1 | 54.9 | 43.0 | 42.8† |

† carried over from 0.1.14[^strata-docs]. Engine 0.1.36 raised Q2_0 to 2,653 prompt tok/s at 32K and 93.5/76.4 output at 4K/128K via fused int8 prompt kernels and thread-block-cluster decode kernels (RTX 50, sm_90+)[^strata-docs].

- **AMD RX 9070 XT 16 GB, Ryzen 9 3900X, 47 GB RAM, Linux:** Q2_0 60/48 tok/s output (short/128K), 1,160 prompt; IQ2_XS 52/36, 1,110; Coder 44/33, 1,420[^strata-docs].
- **Estimated, ±20%:** RTX 3090 24 GB Q2_0 ~140 output at 4K, ~100 at 128K; RTX 5060 Ti 16 GB Q2_0 ~87 at 4K; GPU part scaled by memory bandwidth and CPU part by VRAM-held experts; prompt estimates predate 0.1.13[^strata-docs].
- Output speed varies by several percent with the text because acceptance of drafted tokens varies; time to first token ≈ prompt length / prompt speed (Q2_0 ~25 s at 32K, 4.5 min at 262K)[^strata-docs].
- Images on (encoder on GPU, ~1.4 GB VRAM reserved, ~1,000 fewer cached experts) costs 2–8% output at 4K[^strata-docs].
- Windows Task Scheduler defaults (Below-normal priority, limited token without `SeLockMemoryPrivilege`) slowed expert load from ~1.45 GiB/s (~35 s) to 0.05 GiB/s (13–14 min) on an RTX 5070 Ti + 9800X3D; Normal priority plus "Run with highest privileges" restored it[^strata-docs].
- Limit: slower than tables if a monitor or other programs take VRAM or RAM runs below rated speed (EXPO/XMP)[^strata-docs].

## Independent community measurements

A 2026-09-30 r/LocalLLaMA thread (original post plus comments through 2026-10-04) gives independent Strata numbers on consumer rigs[^strata-thread-sep30]. All figures in this section are **Reported**: self-reported screenshots or log lines with no shared protocol — and commenters note the project's published speed tables were measured with greedy decoding, so they are the best case[^strata-thread-sep30].

The original poster ran ISTA-DASLab's IQ3_XXS on a laptop (RTX 5070 Ti 12 GB, 64 GB DDR5, Intel 275HX, gen4 SSD) via Unsloth Studio over the local API, with screenshots linked but not captured in `raw/`: 51 tok/s generation at 43K context depth versus 23 tok/s from stock llama.cpp on the same quant, and 1,500 tok/s prompt processing on 32K context versus 100 tok/s from stock llama.cpp; the quant loads up to 200K context at 8-bit KV (131K used), at 11 GB VRAM and 56 GB RAM[^strata-thread-sep30]. The poster rates IQ3_XXS quality excellent and repeats ISTA-DASLab's claim that IQ3_S recovers full-model coding performance (**Reported**)[^strata-thread-sep30].

| Rig (consumer, self-reported) | Quant and context | Gen tok/s | PP tok/s |
| --- | --- | ---: | ---: |
| RTX 5070 Ti laptop 12 GB + 64 GB DDR5 (OP) | IQ3_XXS; 43K gen / 32K PP | 51 | 1,500 |
| RTX 5090, 262K ctx | quant unstated | 100–130 | 4,000–4,500 |
| RTX 5090, Swift 1.5 XXS, 256K | Swift 1.5 | 160–190 | >6,000 |
| RTX 4090 + 64 GB DDR4, 262K max (@64K measured) | IQ3_S, k8v4 KV | 70 | ~1,000 |
| RTX 3090 Ti + 128 GB DDR5, 262K | IQ3_S | ~37 avg (19–69) | ~2,200 |
| RTX 3090 + 128 GB DDR4 | Swift 1.5 IQ3_XXS | 70 (peak 85) | ~1,200 |
| RTX 5070 Ti + 128 GB DDR4 | Swift IQ2_XS / IQ3_XXS | 80–120 / 60–80 | ~2,000 |
| RTX 4070 | IQ3-class (unstated) | 50+ | ~2,000 |
| RTX 3060 12 GB + 64 GB DDR4, 262K | IQ2_XS, q4_0 KV | ~58 (peak 63) | ~630–660 |
| RTX 3060 12 GB + 64 GB DDR4 | Coder | 46–51 | — |
| RX 7900XTX + 64 GB, 110–128K | IQ3_S / IQ2_XS | 45–60 / ~50 | — |
| RX 9070 XT + 48 GB DDR4, ROCm/Windows, 32K | Q2_0 | 46 stable | ~1,030 |

- Matched-quant stock-llama.cpp baselines stated in-thread: OP (IQ3_XXS) 23 gen / 100 PP; RTX 3090 mainline 25 gen / 750 PP versus Strata 70 / ~1,200 (Swift IQ3_XXS); another 3090 reporter ~300 PP versus ~1,000 PP on a 30K prompt[^strata-thread-sep30].
- Generation speed holds up with context (43K–262K), including a 17-hour 262K coding session averaging ~37 tok/s — the serving-relevant property for a RAM-offload MoE engine[^strata-thread-sep30].
- Single-reporter extras, all **Reported**: the StrataGP fork (`madvise(MADV_HUGEPAGE)` on the ~30 GB expert cache) claims ~+15% decode (52→58 tok/s on i5-12600K/AVX2/DDR4) with bit-identical output; SSD offload gives "zero noticeable drop"; AtomicChat IQ4_XS runs 40 gen / 500 PP on a 5090 with 32 GB RAM[^strata-thread-sep30].
- Regressions: adding a second RTX 3060 slowed decode 31→21 tok/s and dual-card PP (190) trailed single-card PP (550–650); concurrent parallel requests evict cached data, with the owner promising a fix[^strata-thread-sep30].

## Author-thread measurements (engine-author thread, 2026-09-24–2026-10-02)

The thread author is the Strata author (KnownAd4832), reporting on his own engine on 64 GB DDR5-5600, 12 GB RTX 5070 SFF, Ryzen 5 7600, Windows, against ISTA-DASLab GSQ-RCO GGUFs[^strata-thread-65tps]. Prior llama.cpp baseline stated in-thread: ~15 tok/s output and 100–120 tok/s prompt processing with IQ3_XXS on the same 12 GB RTX 5070[^strata-thread-65tps].

Author-measured 128K-context table (**Reported**)[^strata-thread-65tps]:

| Quant | Output tok/s @128K | Prompt tok/s @128K | Min RAM+VRAM |
| --- | ---: | ---: | ---: |
| Q2_0 | 65.1 | 543 | 37.6 GB |
| IQ2_XS | 52.0 | 472 | 39.2 GB |
| IQ3_XXS | 44.8 | 414 | 47.0 GB |

Vision encoder adds 0.91 GB; only the n-gram table streams from SSD[^strata-thread-65tps]. Limit: the post intro claims the same IQ3_XXS runs at ~65 output / ~430 prompt, which matches the Q2_0 row rather than the IQ3_XXS row — headline/body tension recorded as stated, context lengths for the intro claim unstated[^strata-thread-65tps]. Later author updates in-thread: GSQ-RCO IQ3_S at ~52 tok/s, claimed same category as BF16 per ISTA-DASLab (**Reported**); Coder variant at ~44 tok/s output / ~1,300 prompt tok/s runnable on 32 GB RAM (64 GB RAM+VRAM for full 265K context)[^strata-thread-65tps].

| Rig (self-reported in author thread) | Quant and context | Gen tok/s | PP tok/s |
| --- | --- | ---: | ---: |
| Laptop 12 GB VRAM + 64 GB DDR5, Intel 275HX no AVX-512 (MLDataScientist) | same quant | 50 | 500–600 |
| RTX 5080 + 64 GB RAM, 64K ctx, MTP spec 3 (Sid3effect) | IQ3_XXS | 96.2 (94.6 @100K YAML analysis) | 622.7 @100K |
| RTX 3080 20 GB + 128 GB DDR3, Strata 0.1.14, 262K ctx int8 KV (ductoan266) | Q2_0 | 40–60 (58.3 @100K, 45.6 @3.4K) | 1,014 @100K (1.67x over pre-0.1.14 609) |
| RTX 3090 24 GB + 32 GB DDR4, Strata 0.1.18, Coder IQ1_M 131K ctx int8 KV (orangeswim) | Coder, 119K prompts | 75 thinking-off / 29 thinking-on @119K (90–100 short ctx) | ~1,170 cold; 1.9 s full-118K re-request via prompt cache |
| RTX 5090 laptop 24 GB + 64 GB (Right-Band3478) | IQ3_S, 10K summarization | 54 | 600 |
| RTX 3060 12 GB + 48 GB DDR4, 64K (PestiferousGamer) | unstated | "crazy speeds" screenshot only | — |
| 8 GB VRAM + 64 GB DDR4 (DarkJanissary) | unstated | 40 | — |
| RTX 2060 12 GB + 48 GB RAM, PCIe Gen3 x8 (Wrong_Wind_1806) | IQ2_XS | 4.9 avg (6.5 max) | 12 |

- Matched-quant deltas stated in-thread: 23 TG / 100 PP via llama.cpp vs 50 / 500 via Strata on the same 12 GB + 64 GB laptop; 7–10 TG via llama vs 50–60 via Strata on 8 GB VRAM (~5x); GenerelSchwerz llama.cpp fork capped at 23 TG on that laptop vs 50 TG Strata for the same quant[^strata-thread-65tps].
- Retrieval/quality spot checks (**Reported**): 100K-context retrieval 8/8 with 2/2 OCR on the 3080 rig; 26-needle @118.8K on the 3090/Coder rig 300/312 (96.2%) with misses omitted never hallucinated, follow-up fact-check CORRECT 12/12, valid JSON every run; first long request after load page-thrashed (~4 tok/s) with the identical warm request 16x faster[^strata-thread-65tps].
- Tuning notes: `--expert-cache auto` (~5,229 slots / 8.48 GB) left 0–200 MB VRAM and stalled inference on the 5080 rig — explicit `--expert-cache 3500` plus `--pool-workers 8 --no-host-worker` eliminated lock-ups; the same pool-worker cut fixed a 100%-CPU laptop freeze with no speed loss[^strata-thread-65tps].
- Multi-GPU is early: 12 GB 3060 over OCuLink reached 27 TG @64K and 22 TG @256K (IQ3-XS), two GPUs 30+ TG, all four slower over shared USB4; the author states the engine is not yet multi-GPU optimized[^strata-thread-65tps].

## Power-limited 5090 thread (2026-10-02–2026-10-04)

The original poster runs Qwen3.8-Flash-Next at IQ3_S with 128K context at 8-bit on a power-limited RTX 5090 plus 96 GB DDR5-6400, reporting 150–200 tok/s decode and 5,000–6,000 tok/s prefill in the title, then up to 225 tok/s decode with prefill peaking around 6,500 tok/s on the latest version in a 2026-10-04 follow-up (**Reported**)[^strata-thread-5090]. The attached monitor screenshot corroborates the range: 194.0 tok/s generation with 5,004 tok/s prefill at 100% GPU load, 446 W of a 600 W budget, PCIe Gen5 x16, 31.7/32 GB VRAM in use, and recent ~97K-prompt requests at 92–97 tok/s with 87–97% expert hit rates (**Reported**, screenshot inspected)[^strata-thread-5090]. Limit: engine version unstated, headline prompt length beyond 128K context unstated, and no sampling or measurement protocol stated — per the benchmark rule these stay **Reported** snapshots, not comparable benchmarks.

- OP rig detail (self-reported 2026-10-04): AMD Ryzen 9 9950X3D, Ubuntu Server after a fresh install set up for this purpose, plain power limit on the GPU (previously undervolted on Windows)[^strata-thread-5090]. OP attributes a same-model lower result (~100 tok/s at ~200 W, 5090 + 128 GB DDR5-6000, Intel 270K Plus, 200K max context, vision on, Q8 cache) to bandwidth restriction, advising checks of full PCIe Gen5 x16 plus a fast non-lane-sharing NVMe; that reporter reached ~170 tok/s for some prompts after tweaking (**Reported**)[^strata-thread-5090].
- Context-size-for-VRAM rule restated in-thread: context size limits how many experts fit in VRAM, so larger context runs slower (**Reported**)[^strata-thread-5090].

| Rig (self-reported in this thread) | Quant and context | Gen tok/s | PP tok/s |
| --- | --- | ---: | ---: |
| Power-limited 5090 + 96 GB DDR5-6400, IQ3_S 128K 8-bit KV (OP) | IQ3_S; 128K ctx | 150–200 (up to 225) | 5,000–6,000 (peak ~6,500) |
| 5090 + 128 GB RAM, 256K ctx, modified pelican-svg prompt | unstated (IQ class) | ~60 | ~2,000 |
| 5090 + 3090 + 128 GB RAM, full context + vision (eddoursul fork) | Unsloth UD-Q4_K_XL | ~100 (80–100 range) | ~2,600 |
| 4090 + 5060 Ti 40 GB + 94 GB RAM, 262,144 ctx 8-bit KV streamed (32,768/layer VRAM, rest RAM), 8,765 experts (25.6 GB) in VRAM, MTP ≤3 + prompt lookup | Unsloth UD-Q4_K_XL | 25 | 700 |
| 4090 + 96 GB DDR5 Windows, 75 GB budget, 2 GB VRAM reserve, 128K | IQ3_S | 50–60 (~100 south under Windows per second reporter; up to ~100 Linux-equivalent) | ~1,400 |
| 4070 Ti Super + 64 GB DDR4, Linux, IQ3 streaming cache | IQ3_S | ~60 MTP-missing chars, ~80 story / up to ~120 code (avg ~90) with MTP fixed | 2,300–3,000 by length |
| 5070 Ti + 128 GB RAM (two reports) | IQ class | high-30s–low-40s, later 1,000 PP rig after re-setup; 2,000 PP with two 5070 Ti | 454 (first 769 then settled) → ~1,000 single / ~2,000 dual |
| 3090 + 96 GB DDR4, 200K+ real project work | UD-Q4_K_XL | — | ~1,000 |
| 7900 XTX + 64 GB RAM (~3/4 used), 128K, ~97% expert hit rate | GSQ RCO quant | similar-quality impression vs Qwen3.8-27B-Q6_K in less time | — |
| 4090 + 64 GB DDR5, IQ3_XXS (NixOS, after update) | IQ3_XXS | ~80 (was ~40 before update/setup fix) | — |
| 4090M laptop (4080-class power) + 7945HX + 64 GB DDR5, max ctx | IQ3_S | 50–60 | — |
| 2×3090 (dual vs single) | IQ3-class | 75–85 (single GPU only drops to the same band) | — |
| 5090 + 64 GB DDR5, Switch 1.5 IQ3_XXS | Swift 1.5 IQ3_XXS | similar to OP | — |
| 8 GB VRAM + 64 GB DDR5, 90K ctx (linked report) | Q2 IQ3-class | 40 | — |

- Matched-engine deltas stated here (**Reported**): UD-Q4_K_XL on the 5090+3090 fork rig ~80–100 / ~2.6K vs ~29 / ~285 on llama.cpp and ~32 / ~1.3K on EXL3, with ~74 GB RAM pinned while loaded[^strata-thread-5090]. FreeToken comparison offered in-thread: GPU-only expert cache ~30 tok/s when experts fetch often else ~60, coding average 40–50, omp sessions ~40 including prefill, prefill 5,000–6,000 peak and ~3,300 average on a 9950X3D + 160 GB + single 5090 (plus V620 build-out); FreeToken lacks MTP and runs nvfp4 (~q4) while Strata runs at most Q3 with MTP, so a no-MTP Strata number was requested for apples-to-apples but not posted[^strata-thread-5090].
- UD-Q4_K_XL-on-Strata setup (eddoursul fork `custom` branch, K-quant expert kernels; open PR against upstream; upstream supports only ISTA models at thread date): pull official MTP tensors separately and pack for spec decoding (UD GGUF lacks the MTP head in Strata's form); ignore the stale `GPU hit path is NOT CORRECT` boot warning (old non-native kernel text, closed issue #23; reporter matched llama.cpp 64/64 top-1); do not use `--max-context 262144` (loads then hangs every request with `qsa_block_topk: unsupported geometry or cap` — 262136 works, literally 8 tokens less); `--expert-cache auto` eats VRAM to ~700 MiB free so add `--vram-reserve-mib 1600` for vision headroom; mainline llama.cpp will not load these weights (unknown arch — use Unsloth's build for comparison) (**Reported** how-to)[^strata-thread-5090].
- Quality dispute in-thread (no resolution; recorded as positions, all **Reported**): IQ3 called compromised with looping/unsure behavior on hard programming tasks vs Qwen3.8-27B PrismaScout, preferring local-inference-lab experimental nvfp4 as indistinguishable from fp8; GSQ-RCO defended as best quant with ISTA-DASLab tests near BF16 and a third-party byteshape KLD table cited performing like Unsloth Q5_K_XL; counter that Q4 is barely 93% same top-p so IQ3 must crack on long tasks as errors accumulate, answered that top-p misses can be synonyms; one 27B GSQ-RCO report of 10x token blow-up with failed tool calls vs one RCO week-long hard-task report of robust behavior; information-theory note that ~6 bit is the bend where lower precision starts hurting, modulated by model size vs training data (**Reported** positions)[^strata-thread-5090].

## Fidelity and validation status

- No token- or logit-level parity check between Strata and llama.cpp existed at thread date; the proposed protocol is same GGUF, tokenizer, and prompt/token IDs with deterministic settings (temperature 0, greedy/argmax, fixed seed), 1–10K tokens across short, long, random-token, and multilingual prompts with zero mismatches, plus per-step logit comparison within tolerance[^strata-thread-sep30].
- The only comparison posted is an 8-prompt character-level check (Claude-assisted script via pastebin, temperature and seed unstated): 5/8 identical, 3 diverged with similarities 0.994, 0.447, and 0.977 (average agreeing fraction 79.5%), which its author scored PASS-within-tolerance[^strata-thread-sep30]. **Reported** with a weak method: character overlap is not token parity, and one case diverges badly.
- Whether sampling settings take effect is disputed: one user reports temperature changes nothing (suspecting hard-coded greedy), while another reports a clear T=0 vs T=1.5 difference with thinking off and top-p/top-k maxed (**Reported**, **Unverified**)[^strata-thread-sep30].
- In the author thread, one run pastes a live engine guardrail verbatim: `*** WARNING: --expert-cache is enabled and the GPU hit path is NOT CORRECT. The generated tokens diverge from a cache-off run (measured: first difference at token 40 at 2.97% hits, token 0 at 54.4%). Any timing from this run is real; any OUTPUT from it is not. ***` — i.e. speed stands, tokens do not, until the hit path is fixed (**Reported** engine self-check)[^strata-thread-65tps].
- A code-review comment flags undocumented internals (missing `ref/gdn.py`, lazy per-(layer, expert) dequantization plan, README-vs-paper CPU-vs-GPU expert-compute wording, FP32-vs-BF16 dequant wording, 5 GB MTP GGUF vs 0.8 GB MTP layer, ~3.25 tok/round implying ~0.8 acceptance as high for quantized models) over a short 256-token 88 tok/s benchmark window; the author replies the build used Claude/Codex plus Astra and DeepSeek Flash with ~7B tokens spent on testing (**Reported**, **Unverified**)[^strata-thread-65tps].
- Cross-quant KL reference posted in-thread (ExLlamaV3/TabbyAPI, RTX 5070 Ti, 199K ctx, **Reported**): EXL3 6.05 bpw KL 0.0031 vs bf16; EXL3 5.05 0.0040; EXL3 4.05 0.0067; NVFP4 W4A16 0.0100; UD-IQ4_XS ~4.25 0.0165; EXL3 3.05 0.0177; UD-IQ3_XXS ~3.2 0.0349 — with that reporter's setup at ~21.5 TG / ~1,740 PP[^strata-thread-65tps]. No Strata-vs-llama.cpp token/logit parity run exists in either thread.
- The self-identified Strata owner states output is not degraded and these are standard RCO/Swift quants, announces Unsloth-quant support from v0.1.31, and promises a concurrent-request cache fix (**Reported**)[^strata-thread-sep30].
- Subjective quality reports ("feels no different", "same quality as bigger quants") are not fidelity evidence; a 256K-context Coder user reports frequent thought loops hitting the reasoning budget, with advice to use the full non-pruned model or lower reasoning[^strata-thread-sep30].

## Fit notes from the thread

- At thread date the engine is CUDA-only with experimental AMD support (a ROCm-on-Windows PR reports doubling prefill 500→1,030 tok/s on a 9070 XT); it runs on Linux and Windows but only with select ISTA-DASLab GGUFs, with Unsloth-quant support landing in v0.1.31[^strata-thread-sep30].
- KV-cache width is an open tuning question: reporters use q4_0, int8, k8v4, and 8-bit KV, and one thread asks whether 4-bit KV hurts coding quality with no answer in the inspected comments[^strata-thread-sep30].
- Opinion stated as trend, not fact: popular models will each get their own tuned engine while general engines trade peak speed for compatibility — the thesis of [Narrow Single-Model Inference Engines](narrow-inference-engines.md)[^strata-thread-sep30].

## Headline anatomy, sizing, quality, and cost arithmetic (video explainer)

A YouTube-transcript explainer walks through the viral "6x" number and the buying decision; every figure here is **Reported** narrator testimony with no shared protocol, and the comparison builds and versions are unstated except Strata 0.1[^strata-video-6x].

- **What the 6x is made of:** the narrator's own pre-Strata baseline was ~15 tok/s on the 3-bit build (via a llama.cpp-based tool on an RTX 5070, six-core CPU, 64 GB DDR5) with 3 min 11 s to first token on a ~20K prompt; tuning lifted the same setup to ~29 tok/s before Strata shipped (Sept 18); the 93 tok/s headline is the 2-bit build — so 93/15 ≈ 6.2x compares the fastest result against the slowest baseline, while matched 3-bit-vs-3-bit is ~2.1x and one RTX 3090 matched-quant report (3.5-bit, 31 vs 74 tok/s, llama.cpp without its speculation equivalent) is ~2.4x. **Synthesis:** plan on a 2–2.5x fair band depending on hardware and build, consistent with the independent 2–3x snapshots above.
- **Sizing rule:** the CPU side is RAM-bandwidth-bound — about 42 GB/s pulled for the 2-bit build, roughly all DDR5 delivers, so DDR4 nearly doubles the CPU half of each layer while the GPU waits; the narrator's RAM ran at 5,200 MT/s with the BIOS memory profile off (enabling XMP/Expo is free speed); 64 GB is the threshold (~34 GB experts plus ~10 GB OS), 32 GB drops to the expert-halved Coder; more VRAM caches more experts (RTX 5090 32 GB holding 17,463 of 24,576 at 179 tok/s on the 2-bit build, vs ~79 tok/s stated for the 12 GB 5070-class card with the build name garbled in the transcript)[^strata-video-6x].
- **Quality cost of the fast builds:** per the quant publisher's tests against the full model (narrator says "Aista"), LiveCodeBench scores 87.4 full-precision vs 81.1 on the 2-bit Q2 build (~6 points) vs 86.3 on the 3-bit IQ3 build (~1 point); at full precision the model leads the 27B Qwen3.8 by under a point on SWE-Bench Pro (62.5 vs 61.7), so the fastest build gives back more than the lead it was bought for on code — practical rule stated as 3-bit for coding, 2-bit for chatting[^strata-video-6x].
- **Buy-vs-API arithmetic:** 64 GB of DDR5-6000 at $913 (late-September price index; all-time low $159 — then dearer than an RTX 5070) buys ~1.9B tokens at the hosted $0.47/M output price, which takes ~242 days of round-the-clock generation at 93 tok/s to emit, and the hosted copy serves concurrent requests; stated local value is privacy, offline use, and API-backend use — price the API before buying RAM, while a PC that already has 64 GB of DDR5 gets free speed[^strata-video-6x].

## Complaint-thread community reports (2026-10-03–2026-10-04)

A complaint about Strata hype (`Yes bots we get it, Strata is good now please stop`) drew mostly corroborating firsthand reports; every figure here is **Reported** with no shared protocol, unstated engine versions, and quants often omitted — one commenter notes posts omitting quant say little[^strata-thread-bots].

- **Setup menu restated:** `setup.sh` offers (1) original Qwen3.8-Flash-Next GSQ-RCO by ISTA-DASLab, (2) Swift 1.5 fine-tune (~-63% thinking tokens, ~1.8x sooner answers per its authors), (3) Coder expert-halved coding variant (~32 GB RAM, faster, weaker outside code), (4) Unsloth 4-bit experimental (~111 GB download, most experts from SSD, ~7–8.5 tok/s on 64 GB) (**Reported** menu text)[^strata-thread-bots].
- **Selected rigs:** dual 5080s 20 tok/s llama.cpp → 80–100 Strata (**Reported**); R9 5900X + 64 GB DDR4 + 3090 IQ3_XXS 15 → 65+ tok/s (**Reported**); Legion laptop 24 GB VRAM + 128 GB RAM heaviest IQ3_S at 262K ~82 tok/s decode (**Reported**); 5060 Ti 16 GB ~60 tok/s gen and ~1,200 PP feeling smarter than 27B (**Reported**); 3090 + 100+ tok/s via opencode (**Reported**); Unsloth Desktop 40–50 gen / 100 prefill → 80–100 gen / 1,300–2,000 prefill at same quant (**Reported**); 7900 XTX + 64 GB 1,300–1,500 PP and 80–120 TG even past 100K (**Reported**); 5090 35–45 → 90–145 tok/s moving from NVFP4-class to GSQ IQ3 with auto VRAM calibration (**Reported**); 2×P40 20+ TG long-context up to 45 fresh at 256K (**Reported**); 5090 + 64 GB up to ~180 tok/s (**Reported**); 4070 12 GB + 32 GB DDR5 Coder 35–70 tok/s vs ~8 tok/s default LM Studio (**Reported**); 5060 Ti IQ2_XXS-class 45–66 tok/s while coding (**Reported**); 4090 + 64 GB Swift IQ3_XXS / IQ3_S 110 tok/s at 252K and 130 tok/s at 128K with q8 KV (**Reported**); 2×16 GB VRAM + 192 GB RAM user runs Strata for Flash Next alongside vLLM 27B NVFP4 and ExLlama GLM 5.3 Flash (**Reported**)[^strata-thread-bots].
- **32 GB RAM viability:** reporters confirm it works with the Coder variant, `--low-ram on`, or `--resident-budget-gib 40` (one UD-IQ4_XS 93.7 GB case keeps ~20 GB on disk at ~100 tok/s decode); 3090 24 GB + 64 GB holds 70–60 tok/s even at 256K with SSD offload, and 11 GB VRAM use leaves headroom for more GPU offload (**Reported**)[^strata-thread-bots].
- **Quality open question:** two commenters note no proper eval exists yet and ask whether speed merely buys tolerance for bigger models at worse quants, canceling quality gains; GSQ-RCO IQ3_S ≈ BF16 remains a publisher claim awaiting third-party validation, with one counter-claim that GSQ-RCO is unremarkable versus Unsloth GGUFs (**Reported** positions)[^strata-thread-bots].
- **Experimental SSD path:** one 3070 8 GB + 64 GB DDR4 report integrates colibri dual-SSD streaming (omp/astra) on UD-Q4_K_XL: 57 → 70 tok/s prefill and 12.1 → 13.4 tok/s generation with experts spilling to SSD (**Reported**, needs more testing)[^strata-thread-bots].

## Hardware requirements

- NVIDIA RTX 20–50 or listed AMD RDNA2–4 cards with ≥12 GB VRAM (8 GB runs slowly); x86-64 AVX2 CPU (AVX-512 a bit faster); NVIDIA driver ≥580; NVMe SSD strongly recommended; ~70–120 GB disk for model files[^strata-docs].

## Relationships

- Uses [Strata Tiered MoE Offload Engine](strata-tiered-moe-offload.md) — memory-tier rules that make RAM the fit constraint and VRAM the speed lever.
- Uses [Strata MTP and Prompt-Lookup Speculation](strata-speculative-decoding.md) — every output figure is measured with MTP on.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — Unsloth's own GGUF sizes and llama.cpp guidance for the same model.
- Related to [Qwen3.8-Flash-Next HF Release and Serving](qwen3.8-flash-next-hf-release.md) — the upstream checkpoint these quants derive from.
- Related to [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — KL and top-1 agreement are the fidelity signals Strata reports.
- Related to [Narrow Single-Model Inference Engines](narrow-inference-engines.md) — all four threads' independent 2–5x snapshots and per-model-engine trend claim support that page's thesis.

## Coverage limits

- ISTA-DASLab, UkisAI, and Unsloth model cards, `UNSLOTH_Q4.md`, `AMD_HIP.md`, `COMMUNITY_BENCHMARKS.md`, and `bench/results/` are referenced but absent from `raw/`; quality labels ("good" to "best") are not tied to a named benchmark in the inspected docs.
- Benchmarks are single-machine, single-prompt-per-length project runs; no cross-engine baseline (llama.cpp, vLLM) at matched settings is provided in the inspected files.
- Both r/LocalLLaMA threads' screenshots, HF model links, pastebin comparison script, StrataGP fork, PRs, and `bench/results/` READMEs are linked but absent from `raw/`; OP-vs-llama.cpp deltas rest on screenshots or log lines not captured here.
- In the 2026-10-03 complaint thread, preview.redd.it/imgur screenshots, the Niko1221 repo link, llama.cpp hot-expert PR link, localbench URLs, and hashyy link are cited secondhand from comment text; screenshots, code, weights, and linked benchmarks were not inspected here[^strata-thread-bots].
- In the 2026-10-02 power-limited-5090 thread, preview.redd.it screenshots beyond the attached monitor image, HF/blog links, the eddoursul fork branch, issue #23, and Unsloth-build references are cited secondhand from comment text; the monitor screenshot (`assets/hmr77h6in2th1.png`) was inspected, the fork code and linked weights were not[^strata-thread-5090].
- No deterministic token/logit parity check between Strata and llama.cpp exists in the inspected material; the one 8-prompt comparison is character-level with unstated temperature and seed.
- In the author thread, GitHub/HF URLs, the carteakey.dev blog, preview.redd.it screenshots, and the `setup.py`/`CMakeLists.txt` SM75 patch diffs are cited secondhand from comment text; the engine repo itself was not inspected here[^strata-thread-65tps].
- Open question from the author thread: whether the 37.6–47 GB minimums include the full 128K KV cache or only model plus runtime, asked against a DS4-Q4 262K/M3-Ultra comparison — unanswered in the inspected comments[^strata-thread-65tps].
- Video-explainer limits: narrator-reported figures with no measurement protocol; comparison Strata/llama.cpp builds and sampling settings unstated (Strata named only as version 0.1); no timecodes in the captured transcript; linked GitHub repo, paper, model card, and price-index page not inspected[^strata-video-6x].

[^strata-docs]: Strata docs — `../raw/Strata/MODELS.md` "Pick by RAM", "How fast is each size", "The sizes", "Will it fit?", "The versions"; `../raw/Strata/DETAILS.md` "Speed (measured)" (intro, 0.1.36 note, prompt/output tables, time to first token), "Other GPUs (estimated)", "Which model?" and its Coder/Swift 1.5/UD-Q4_K_XL subsections, "Before you start", "Running it at startup (Task Scheduler)", "Speed with images on", and Troubleshooting ("Slower than the tables"); `../raw/Strata/README.md` "How fast is it?", "What you need", "Which model should I pick?".
[^strata-thread-sep30]: r/LocalLLaMA thread "Qwen3.8 flash next ISTA-DASLab GGUF 50t/s TG and 1500t/s PP with 12GB VRAM and 64GB RAM Laptop on 'Strata' engine" — `../raw/qwen38-flash-next-istadaslab-gguf-50ts-tg-and/index.md` (original post plus comments, 2026-09-30–2026-10-04): OP laptop measurements (IQ3_XXS, 51 tok/s at 43K, 1,500 tok/s PP at 32K, 11 GB VRAM + 56 GB RAM), community rig reports (RTX 3060–5090, RX 7900XTX/9070 XT), 8-prompt character-level comparison, greedy-decoding methodology note, temperature dispute, owner statements, and StrataGP-fork/SSD-offload claims.
[^strata-thread-65tps]: r/LocalLLaMA thread "Qwen3.8-Flash-Next on 12GB VRAM - 65 tokens per second" — `../raw/qwen38flashnext-on-12gb-vram-65-tokens-per-second/index.md` (author post plus comments, 2026-09-24–2026-10-02): author 128K table (Q2_0 65.1/543, IQ2_XS 52.0/472, IQ3_XXS 44.8/414; minima 37.6/39.2/47 GB + 0.91 GB vision) on RTX 5070 12 GB + 64 GB DDR5 + Ryzen 5 7600, IQ3_S/Coder updates, community rigs (5080/5090/3090/3080/3060/2060/A4500, 8 GB VRAM), expert-cache divergence warning, EXL3 KL table, KV-cache persistence fix, SM75 patches, and tuning notes.
[^strata-thread-5090]: r/LocalLLaMA thread "Strata on a power limited 5090 and 96GB of DDR5-6400" — `../raw/strata-on-a-power-limited-5090-and-96gb-of/index.md` (original post plus comments, 2026-10-02–2026-10-04): OP power-limited 5090 + 96 GB DDR5-6400 IQ3_S 128K 8-bit headline (150–200 decode / 5–6K prefill, later up to 225 / ~6.5K peak) with inspected monitor screenshot `assets/hmr77h6in2th1.png` (194.0 tok/s, 5,004 PP, 446 W, Gen5 x16); 5090/4090/3090/4070Ti/5070Ti/7900XTX rig reports; eddoursul-fork UD-Q4_K_XL setup (MTP packing, stale hit-path warning, 262136 ctx cap, `--vram-reserve-mib 1600`); FreeToken-vs-Strata MTP comparison; IQ3/RCO/NVFP4 quality dispute.

[^strata-thread-bots]: r/LocalLLaMA thread "Yes bots we get it, Strata is good now please stop" — `../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/index.md` (original post plus comments, 2026-10-03–2026-10-04): `setup.sh` four-model menu, 5090/3090/4070/5060Ti/2xP40/7900XTX rig reports, 32 GB-RAM fit notes (`--low-ram`, `--resident-budget-gib`), quant-omission caveat, no-eval quality dispute, and colibri dual-SSD experiment.

[^strata-video-6x]: "The New Way to Run 125B Models 6x Faster Than llama.cpp (Strata)" — `../raw/the-new-way-to-run-125b-models-6x-faster-than-llama.cpp-(strata).md` (YouTube transcript, English; channel, URL, and publish date not captured — content places it after the 2026-10-01 llama.cpp MTP merge): 15 → 29 tok/s pre-Strata tuning baseline with 3 min 11 s TTFT on ~20K prompt (RTX 5070, six-core CPU, 64 GB DDR5), 93 tok/s 2-bit headline with 6.2x-vs-2.1x/2.4x decomposition, ~42 GB/s CPU bandwidth with DDR4/XMP notes, 64 GB threshold and 5090-vs-5070 VRAM scaling, Aista LiveCodeBench 87.4/81.1/86.3 with SWE-Bench Pro 62.5-vs-61.7 context, and $913-vs-$159 RAM with $0.47/M hosted arithmetic.
