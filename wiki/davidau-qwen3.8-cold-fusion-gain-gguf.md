---
type: Concept
title: DavidAU Qwen3.8-27B Cold Fusion GAIN GGUF
description: Cold-Fusion GAIN fine-tune of Qwen3.8-27B cutting thinking tokens 1/2 to 1/10 with NEO-IMATRIX MAX/MTP GGUFs, Nightmedia benchmarks, and llama.cpp serving guidance.
tags: [qwen3.8, gguf, quantization, finetune, reasoning, mtp, speculative-decoding, llama-cpp, local-inference, vision]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T17:00:00Z }
sources:
  - id: coldfusion
    resource: ../raw/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1-NM-DAU-NEO-MAX-MTP-GGUF.md
    title: Qwen3.8-27B-Cold-Fusion-GAIN-V1.1-NM-DAU-NEO-MAX-MTP-GGUF (DavidAU model card)
---

DavidAU's Cold Fusion GAIN V1.1 is a detail-focused fine-tune of `Qwen/Qwen3.8-27B` that targets shorter thinking blocks (about 1/2 down to 1/10 the tokens, median roughly 2/3 reduction) with higher general intelligence and faster MTP decoding, shipped as NEO-IMATRIX `MAX`/MTP GGUFs with a separate `mmproj` for vision[^coldfusion]. **Reported** by the model card unless noted; all benchmark, accuracy, and throughput figures carry the unstated-protocol limits in Coverage limits.

## What Cold Fusion changes

- Base chain is `Qwen/Qwen3.8-27B` via `DavidAU/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1`; frontmatter declares Apache-2.0, `image-text-to-text` pipeline, and `DavidAU/Polar-STRICT-Datasets` plus `DavidAU/Reasoning-STRICT-Datasets`[^coldfusion]. **Reported**.
- Collaboration is DavidAU (tuning, Cold Fusion), Nightmedia (benching), and TeichAI (datasets)[^coldfusion]. **Reported**.
- Stated goals are higher general intelligence and problem solving, thinking blocks cut from 1/2 to as low as 1/10 with reformatted and improved reasoning, faster token generation especially MTP, coverage across all three thinking modes, zero "benchmaxing", and maintained or raised core benchmarks[^coldfusion]. **Reported**.
- COLD FUSION is `GAIN` plus Unsloth trainers/systems, invented during the `Qwen3.6-27B-Fable-Fusion-711` R&D; GAIN dynamically changes training per sample in real time as the model learns, stated to improve metrics and overall performance without overcooking or damaging the model[^coldfusion]. **Reported** method summary.
- Headline quant claim is 99% of BF16 performance at both 8-bit and 4-bit, with 4-bit at 99% of 8-bit performance, described as the strongest and most stable model at both widths[^coldfusion]. **Reported**.
- Card self-grades this tune at level 1–2 versus `Qwen3.6-27B-Fable-Fusion-711` at level 7–8, and announces a planned heavier 6-stage-plus-sub-stages Fable-pipeline tune (7–10 days minimum) including abliterated/uncensored work[^coldfusion]. **Reported**.
- Validation is per-stage benching plus final side-by-side human testing of base versus new model ("trust, but verify"); claimed effects are improved instruction following, higher general intelligence, smaller but high-detail reasoning and often compressed outputs, exceptional low quants, and no corruption of the base model with vision retained[^coldfusion]. **Reported**.

## Thinking-token reduction and effort controls

- Reduction spans all three Qwen3.8 reasoning modes (`xhigh` default, `medium`, `low`) while output detail stays high; more detailed prompts shrink thinking further because the model guesses less, and multi-turn refinements in the same chat often hit ~1/5 normal size or lower[^coldfusion]. **Reported**.
- Card warns the reasoning modification is a major model change to test carefully per use case[^coldfusion]. **Reported**.
- Without an app-level switch, set effort at the very top of the Jinja template (`xhigh` default)[^coldfusion]. **Reported**:

```
{%- set reasoning_effort = 'medium' %}
```

- In LMStudio use DEV mode with "advanced updates" off; other apps vary; the source GGUF recipe is to edit `chat-template.jinja` and the token-config/chat-template files from `DavidAU/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1`[^coldfusion]. **Reported**.
- Advanced Jinja behavior: Qwen3.8 uses system-prompt injection to control reasoning; `medium` disables injection so a custom reasoning system prompt can be set, while `xhigh`/`low` inject their own instructions and unknown values raise; the template can be edited to retune reasoning per use case[^coldfusion]. **Reported**.

## Quant packaging: NEO MAX, MTP, and LOW

- All regular and MTP quants are NEO IMATRIX, claimed +2–4% accuracy over normal GGUFs plus better long-context performance; the output tensor (10–20% of output) is raised to 16-bit full precision in every quant[^coldfusion]. **Reported**.
- MTP files carry `MTP` in the name with MTP tensors at Q8_0; keep temperature at 1 or below and repetition penalty at 1 (off) or MTP performance degrades; below 50% token acceptance (predict 2 tokens) switch to regular quants[^coldfusion]. **Reported**.
- Two `LOW` files (`IQ4_XS`, `Q6_K`) trade the MTP/output-tensor mods for max speed and reduced VRAM at possibly slightly lower quality than regular `MAX` quants[^coldfusion]. **Reported**.
- Reported speed on `Q4_K_S` 4-bit is ~75 tok/s regular versus 90+ tok/s MTP at 60% acceptance predicting 2 tokens, measured on an RTX 5090 under Windows 11 in LMStudio; Linux/Mac is generally faster and MTP varies with GPU, app, OS, and hardware, degrading on creative/complex prompts or temperature above 1 where regular GGUFs win[^coldfusion]. **Reported** with single-rig, single-app limits.
- Serving advice is to download at least one regular and one MTP quant and test per use case; MTP can also run faster as the context window fills or in multi-turn chats; there is otherwise no functional difference, only speed[^coldfusion]. **Reported**.
- Model scope is 256K context with GGUFs running in standard apps; vision is tested but needs one separate `mmproj` file in the same folder as the GGUF[^coldfusion]. **Reported**.

## Sampling and chat/roleplay settings

- Qwen3.8 thinking defaults are temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0; instruct/non-thinking defaults are temperature 0.7, top_p 0.80, top_k 20, min_p 0.0, presence_penalty 1.5, repetition_penalty 1.0; Qwen3.5/3.6 share those except precise-coding thinking uses temperature 0.6[^coldfusion]. **Reported**.
- Qwen3.8 shares the 3.5/3.6 tensor/layer framing, but new reasoning options may need parameter retuning (especially temperature), and Q4 and lower quants may want slightly higher temperatures for some uses[^coldfusion]. **Reported**.
- `presence_penalty` warning: major negative impact on coding, math, and other high-repeat thinking/output uses; start at 0.25 and raise only as needed, setting it only when loop prevention requires it[^coldfusion]. **Reported**.
- Context guidance is 8K–16K minimum with 24K–32K suggested even with reduced reasoning blocks[^coldfusion]. **Reported**.
- For KoboldCpp, oobabooga/text-generation-webui, or Silly Tavern chat/roleplay smoothing, set `smoothing_factor` (`Smooth_F` / `Smoothing`) to 1.5; text-generation-webui GGUF path needs `llama_HF` plus config files from the source-model collection; alternatives are repetition penalty 1.1–1.15 or Quadratic Sampling where supported[^coldfusion]. **Reported**.
- This is a "Class 1" model whose full parameter/sampler guide, example generations, and advanced issue remedies live in the linked Maximizing-Model-Performance collection[^coldfusion]. **Reported**; the external guide is uninspected.

## Nightmedia benchmarks

- Card frames Qwen3.8-27B as deeper-thinking, coding, and agentic focused versus Qwen3.5/3.6, citing its own testing, Qwen statements, and community/extended benches[^coldfusion]. **Reported**.
- Instruct-mode comparison (`arc/c, arc/e, boolq, hswag, obkqa, piqa, wino`) — **Reported** with harness/protocol unstated[^coldfusion]:

| Model | Scores |
| --- | --- |
| Cold-Fusion-GAIN-V1.1 mxfp8 (non-heretic) | 0.655, 0.838, 0.898, 0.751, 0.498, 0.807, 0.738 |
| Cold-Fusion-GAIN-V1.1 mxfp4 (non-heretic) | 0.645, 0.833, 0.887, 0.740, 0.496, 0.799, 0.732 |
| Qwen3.8-27B-Instruct mxfp8 base | 0.591, 0.782, 0.896, 0.746, 0.448, 0.801, 0.711 |
| Qwen3.8-27B-Instruct mxfp4 base | 0.581, 0.771, 0.889, 0.738, 0.442, 0.798, 0.713 |
| Qwen3.6-27B-Instruct mxfp8 base | 0.647, 0.803, 0.910, 0.773, 0.450, 0.806, 0.742 |
| Qwen3.6-35B-A3B-Instruct mxfp8 base | 0.581, 0.757, 0.892, 0.751, 0.428, 0.803, 0.688 |
| Qwen3.5-27B-Instruct mxfp8 base | 0.557, 0.711, 0.868, 0.533, 0.452, 0.706, 0.695 |

- Test notes: Instruct mode suits the harness better; thinking-mode testing also shows gains but not their full extent, and thinking mode is expected to exceed Instruct scores in most cases; BF16 is roughly 2–5 points above MXFP8 per metric with some metrics higher[^coldfusion]. **Reported**.
- Sibling positioning in the card's "SUPER Qwen Universe" (Fable-Fusion-711 27B, TURBO 735-882, TWIN-TURBO 709-L, this GAIN-V1.1, 40B Claude-Opus-Deckard, 9B Defiant) is promotional cross-linking and is not reproduced beyond this pointer; all sibling performance characterizations stay **Reported** in the source[^coldfusion]. **Synthesis** exclusion decision.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the official Unsloth GGUF/NVFP4 local path while this page is the Cold-Fusion thinking-compression fine-tune with its own NEO-IMATRIX MAX/MTP ladder and sampling guidance.
- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — the NEO-IMATRIX packaging here is a per-layer dynamic/imatrix-calibrated GGUF family in the same lineage, with the card's +2–4% claim kept as **Reported**.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — the `MTP`-suffixed tiers preserve multi-token-prediction heads with the same temperature, repetition-penalty, and acceptance-rate (`<50%` switch) operating rules documented there.
- Related to [Dirk Qwen3.8-27B Sharp-Template GGUF](dirk-qwen3.8-27b-gguf.md) — another community 27B repackaging preserving MTP; Dirk changes only the chat template while Cold Fusion retrains reasoning for fewer thinking tokens.
- Related to [Huihui Qwen3.8-27B Abliterated GGUF](huihui-qwen3.8-27b-abliterated-gguf.md) — another community 27B GGUF; Huihui ablates refusal layers with `K_L` requantization while Cold Fusion tunes for reasoning compression with output-tensor/MTP precision mods.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — this family targets standard-app GGUF serving (LMStudio-measured) with a separate `mmproj` vision file.
- Related to [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — the 99%-of-BF16 and BF16-plus-points claims are the fidelity signals that page says to judge with KL, trajectory, and leakage-controlled checks; no such evaluation is in the source.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1-NM-DAU-NEO-MAX-MTP-GGUF.md` inspected statically (**Observed**); no commands executed, so install, Jinja, sampling, MTP, and vision recipes are **Reported**, not reproduced.
- `cannonball.webp` referenced by the card is absent from `raw/` and excluded as decorative.
- Example generations (lines ~921–6883, four examples plus exported-document CSS) excluded as transient narrative; only the reduced-thinking claim they illustrate is compiled above.
- Embedded official Qwen3.8-27B documentation (architecture, text/VL benchmark tables, Quickstart/API, Best Practices/YaRN) reconciled against existing coverage in [Qwen3.8 Local Deployment](qwen3.8.md) and related Qwen3.8/SGLang concepts rather than re-ingested; only Cold-Fusion-specific deltas are compiled here.
- External artifacts uninspected: base `DavidAU/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1`, upstream `Qwen/Qwen3.8-27B`, Polar/Reasoning-STRICT datasets, Fable-Fusion-711/TURBO/TWIN/40B/9B sibling repos, source-file collection, Maximizing-Model-Performance guide, and linked SGLang/vLLM/TokenSpeed/QwenCloud docs.
- Benchmark and speed figures state no harness version, workload shape, or full metric definitions beyond benchmark names (single RTX 5090 / Windows 11 / LMStudio note for tok/s only), so per the SCOPE benchmark rule everything stays **Reported**.
- Placeholder `OPENAI_API_KEY`/`OPENAI_BASE_URL` values in the embedded API examples carry no secret; no live credentials found.

[^coldfusion]: DavidAU Cold Fusion GAIN V1.1 model card — `../raw/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1-NM-DAU-NEO-MAX-MTP-GGUF.md` (frontmatter with Apache-2.0, Polar/Reasoning-STRICT datasets, `DavidAU/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1` base; sections COLD FUSION training, TESTING, IMPORTANT, Modification of REASONING, Regular and MTP GGUFS, Model, VISION, Qwen Model Settings, BENCHMARKS by Nightmedia, SUPER Qwen Universe, chat/roleplay smoothing, Class 1 guide pointer, embedded official Qwen3.8-27B docs, EXAMPLE GENERATION(S)): GAIN per-sample dynamic training with 99%-BF16 quant claims and level 1–2 self-grade; 1/2-to-1/10 thinking reduction across xhigh/medium/low with Jinja `reasoning_effort` edit and medium-disables-injection detail; NEO IMATRIX +2–4% with 16-bit output tensor, Q8_0 MTP tensors, temp/rep-pen and 50%-acceptance rules, LOW IQ4_XS/Q6_K tiers, 75 vs 90+ tok/s Q4_K_S note, 256K plus mmproj vision; Qwen 3.8/3.5/3.6 sampling tables with presence-penalty and 24–32K context guidance and 1.5 smoothing; Nightmedia Instruct-mode arc/boolq/hswag/obkqa/piqa/wino table with thinking-exceeds-instruct and BF16 +2–5 notes.
