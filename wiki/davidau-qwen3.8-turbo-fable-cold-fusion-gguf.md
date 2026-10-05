---
type: Concept
title: DavidAU Qwen3.8-27B TURBO Fable Cold Fusion GGUF
description: TURBO thinking-compressed Heretic-uncensored fine-tune of Qwen3.8-27B scoring 735 ARC-C with NEO-CODER MAX/MTP GGUFs and llama.cpp serving guidance.
tags: [qwen3.8, gguf, quantization, finetune, reasoning, mtp, speculative-decoding, uncensored, llama-cpp, local-inference, vision]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T18:00:00Z }
sources:
  - id: turbo
    resource: ../raw/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF.md
    title: Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF (DavidAU model card)
---

DavidAU's TURBO-Fable-Cold-Fusion-735-882 is a multi-stage fine-tune, multi-fine-tune and multi-stage merge of `Qwen/Qwen3.8-27B` that combines `Qwen3.6-27B-Fable-Fusion-711` (dark-roast) and `Qwen3.8-27B-Cold-Fusion-GAIN-V1.1` DNA, re-Heretic-decensors and re-tunes it, and ships NEO-CODER MAX regular plus MTP GGUFs claiming 0.735 ARC-C / 0.882 ARC-E in 8-bit with 1/2-to-1/10 thinking-token reduction[^turbo]. **Reported** by the model card unless noted; all benchmark, refusal/KL, and throughput figures carry the unstated-protocol limits in Coverage limits.

## What TURBO changes

- Frontmatter declares Apache-2.0, `image-text-to-text` pipeline, base `DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU`, and `DavidAU/Polar-STRICT-Datasets` plus `DavidAU/F451-STRICT-Datasets`[^turbo]. **Reported**.
- Card headline is first fine-tune to exceed 730 ARC-C (735, stated 144 pts above Qwen3.8-27B) and 880 ARC-E in 8-bit with over 718 ARC-C in 4-bit; TURBO means drastically fewer thinking tokens (1/2 down to 1/10) while maintaining output detail and quality[^turbo]. **Reported**.
- Stated strict goals are higher general intelligence and problem solving, thinking blocks cut 1/2 to as low as 1/10 (median reduction roughly 2/3), reformatted and improved thinking blocks, faster token generation especially MTP, coverage across all three thinking modes, zero "benchmaxing", and maintained plus raised core benchmarks without damaging the core model outside that goal[^turbo]. **Reported**.
- Lineage is COLD FUSION (`GAIN` plus Unsloth trainers/systems, per-sample dynamic training invented during `Qwen3.6-27B-Fable-Fusion-711` R&D) together with Fable Fusion 711 training; this TURBO build contains both that 711 dark-roast and `Qwen3.8-27B-Cold-Fusion-GAIN-V1.1` as core DNA, then was Heretic-decensored again and fine-tuned after the merge[^turbo]. **Reported** method summary.
- Card self-grades the GAIN-V1.1 component at level 1–2 versus Fable-Fusion-711 at level 7–8, positions this as one of eleven team Qwen3.8-27B builds all over 717 ARC-C and exceeding base Qwen3.8 benches, and points to the `NM-DAU` source repo for build/bench details[^turbo]. **Reported**.
- Collaboration lists DavidAU (multi-stage tunes), Nightmedia (merge/benching), TeichAI (Polaris dataset), armand0e (light Fable 5 traces), trohrbaugh (Heretic stage 1), and nbeerbower (tunes/models), plus light Fable traces, light Claude Opus reasoning/thinking, F451 in-house, some GPT5 Polaris non-reasoning, and in-house ML/Heretic-repair datasets[^turbo]. **Reported**.
- Validation is per-stage benching of fine-tunes and every merge step plus final side-by-side human testing of base versus new model ("trust, but verify"); claimed effects are improved instruction following, higher general intelligence and problem solving, better thinking/reasoning, exceptional low quants, Heretic uncensored pre-tuning, no corruption of the base model, and retained vision[^turbo]. **Reported**.

## Thinking-token reduction and effort controls

- Reduction spans all three Qwen3.8 modes (`xhigh` default, `medium`, `low`) while output detail stays high; more detailed prompts shrink thinking further because the model guesses less, multi-turn refinements often hit ~1/5 normal size or lower, and in many cases reasoning/output sizes invert as detail moves from the thinking block to the output[^turbo]. **Reported**.
- Card warns the reasoning modification is a major model change to test carefully per use case, and gives the "look 10k–40k tokens before leaping" versus "TURBO leaps almost immediately" framing with an expanded-prompt remedy (add specific checking instructions) to buy back deeper reasoning[^turbo]. **Reported**.
- Without an app-level switch, set effort at the very top of the Jinja template (`xhigh` default)[^turbo]. **Reported**:

```
{%- set reasoning_effort = 'medium' %}
```

- In LMStudio use DEV mode with "advanced updates" off; other apps vary; the from-source quant recipe is to edit `chat-template.jinja` and the token-config/chat-template files from `DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU`[^turbo]. **Reported**.
- Advanced Jinja behavior: Qwen3.8 uses system-prompt injection to control reasoning; `medium` disables injection so a custom reasoning system prompt can be set, while `xhigh`/`low` inject their own instructions and unknown values raise; the template plus system prompts can be retuned per use case[^turbo]. **Reported**.

## Quant packaging: NEO-CODER MAX, MTP, and LOW

- All regular and MTP quants are NEO IMATRIX, claimed +2–4% accuracy over normal GGUFs plus better long-context performance; the output tensor (10–20% of output) is raised to 16-bit full precision in every quant[^turbo]. **Reported**.
- MTP files carry `MTP` in the name with MTP tensors at Q8_0; keep temperature at 1 or below and repetition penalty at 1 (off) or MTP performance degrades; below 50% token acceptance (predict 2 tokens) switch to regular quants[^turbo]. **Reported**.
- Two `LOW` files (`IQ4_XS`, `Q6_K`) reduce memory footprint at possibly slightly lower quality than regular `MAX` quants[^turbo]. **Reported**.
- Reported speed on `Q4_K_S` 4-bit is ~75 tok/s regular versus 90+ tok/s MTP at 60% acceptance predicting 2 tokens, measured on an RTX 5090 under Windows 11 in LMStudio; Linux/Mac is generally faster and MTP varies with GPU, app, OS, and hardware, degrading on creative/complex prompts or temperature above 1 where regular GGUFs win[^turbo]. **Reported** with single-rig, single-app limits.
- Serving advice is to download at least one regular and one MTP quant and test per use case; MTP can also run faster as the context fills or in multi-turn chats; there is otherwise no functional difference, only speed[^turbo]. **Reported**.
- Model scope is 256K context with GGUFs running in standard apps; vision is tested but needs one separate `mmproj` file in the same folder as the GGUF[^turbo]. **Reported**.

## Sampling, tool calling, and chat/roleplay

- Qwen thinking defaults are temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0; precise-coding thinking uses temperature 0.6; instruct/non-thinking uses temperature 0.7, top_p 0.80, top_k 20, min_p 0.0, presence_penalty 1.5, repetition_penalty 1.0; minimum 8K–16K context[^turbo]. **Reported**.
- Tool calling needs minimum `q4km` (`q5ks`/`5km` better, `Q6` MAX or low recommended) with temperature 0.6/0.7 and repetition penalty 1 (off); below `q4km` tool calling may break and overly aggressive caching may further impair functions[^turbo]. **Reported**.
- For KoboldCpp, oobabooga/text-generation-webui, or Silly Tavern chat/roleplay smoothing, set `smoothing_factor` (`Smooth_F` / `Smoothing`) to 1.5; text-generation-webui GGUF path needs `llama_HF` plus config files from the source-file collection; alternatives are repetition penalty 1.1–1.15 or Quadratic Sampling where supported[^turbo]. **Reported**.
- This is a "Class 1" model whose full parameter/sampler guide, example generations, and advanced issue remedies live in the linked Maximizing-Model-Performance collection[^turbo]. **Reported**; the external guide is uninspected.
- Card notes uncensored-versus-trained-uncensored behavior: refusals are removed but some requests need extra directive push (including explicit slang terms for x-rated content) or output stays bland versus a model trained on uncensored content[^turbo]. **Reported**; prompt contents and example generations are excluded per Coverage limits.

## Heretic de-censoring stats

- Stage 1 by trohrbaugh (`trohrbaugh/Qwen3.8-27B-heretic-ara`) uses Heretic v1.2.0+custom with Arbitrary-Rank Ablation (ARA) on `Qwen/Qwen3.8-27B`; table is KL 0.0535 with 0/100 refusals versus 99/100 for the original[^turbo]. **Reported**.
- Stage 2 after stage-1 tuning/merges/adjustments in lab is KL 0.0025 with 11/100 refusals versus 86/100 for the stage-1 build; card prioritizes ultra-low KLD first (performance/quality) with low refusal rate second[^turbo]. **Reported**.
- Safety boundary: uncensored adult-capable tune; card retains tame defaults requiring explicit direction for graphic content. Harmful-prompt contents, attack-chain detail, and verbatim explicit generations are excluded from this concept. **Synthesis** boundary decision.

## Nightmedia benchmarks

- Instruct-mode comparison (`arc/c, arc/e, boolq, hswag, obkqa, piqa, wino`) — **Reported** with harness/protocol unstated[^turbo]:

| Model | Scores |
| --- | --- |
| TURBO-Fable-Cold-Fusion-735-882 mxfp8 | 0.735, 0.882, 0.917, 0.832, 0.530, 0.837, 0.785 |
| TURBO-Fable-Cold-Fusion-735-882 mxfp4 | 0.719, 0.887, 0.916, 0.821, 0.524, 0.831, 0.786 |
| Qwen3.8-27B mxfp8 base | 0.591, 0.782, 0.896, 0.746, 0.448, 0.801, 0.711 |
| Qwen3.8-27B mxfp4 base | 0.581, 0.771, 0.889, 0.738, 0.442, 0.798, 0.713 |
| Qwen3.6-27B mxfp8 base | 0.647, 0.803, 0.910, 0.773, 0.450, 0.806, 0.742 |
| Qwen3.6-35B-A3B-Instruct mxfp8 base | 0.581, 0.757, 0.892, 0.751, 0.428, 0.803, 0.688 |
| Qwen3.5-27B mxfp8 base | 0.557, 0.711, 0.868, 0.533, 0.452, 0.706, 0.695 |

- Test notes: Instruct mode suits the harness better; thinking-mode testing also shows gains but not their full extent, and thinking mode is expected to exceed Instruct scores in most cases; BF16 is roughly 2–5 points above MXFP8 per metric with some metrics higher[^turbo]. **Reported**.
- Card claims both 4-bit and 8-bit TURBO exceed base Qwen3.8-27B on all seven critical benchmarks and exceed all seven benches for Qwen3.6-35B-A3B, Qwen3.6-27B, and Qwen3.5-27B[^turbo]. **Reported**.
- Sibling positioning in the card's "SUPER Qwen Universe" (Fable-Fusion-711 27B, this TURBO 735-882, TWIN-TURBO 709-L, GAIN-V1.1, 40B Claude-Opus-Deckard, 9B Defiant) and third-party/community-tab tool-calling claims are promotional cross-linking and are not reproduced beyond this pointer[^turbo]. **Synthesis** exclusion decision.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the official Unsloth GGUF/NVFP4 local path while this page is the TURBO thinking-compression Heretic fine-tune with its own NEO-CODER MAX/MTP ladder and sampling guidance.
- Related to [DavidAU Qwen3.8-27B Cold Fusion GAIN GGUF](davidau-qwen3.8-cold-fusion-gain-gguf.md) — sibling tune sharing GAIN/Unsloth lineage, NEO-IMATRIX plus Q8_0-MTP packaging, Jinja effort controls, and Nightmedia Instruct-mode tables; GAIN-V1.1 is non-Heretic level 1–2 groundwork while TURBO adds Fable-711 DNA plus Heretic re-decensoring and the 735/882 headline.
- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — the NEO-IMATRIX packaging here is a per-layer dynamic/imatrix-calibrated GGUF family in the same lineage, with the card's +2–4% claim kept as **Reported**.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — the `MTP`-suffixed tiers preserve multi-token-prediction heads with the same temperature, repetition-penalty, and acceptance-rate (`<50%` switch) operating rules documented there.
- Related to [RVN Qwen3.8-27B Heretic Abliterated Uncensored GGUF](rvn-qwen3.8-27b-heretic-abliterated-gguf.md) — another ARA-Heretic uncensored 27B GGUF; RVN reports three-pass refinement with multilingual calibration while TURBO reports two-stage KLD/refusal tables plus Fable/Cold-Fusion retraining.
- Related to [Dirk Qwen3.8-27B Sharp-Template GGUF](dirk-qwen3.8-27b-gguf.md) — another community 27B repackaging preserving MTP; Dirk changes only the chat template while TURBO retrains reasoning for fewer thinking tokens.
- Related to [Huihui Qwen3.8-27B Abliterated GGUF](huihui-qwen3.8-27b-abliterated-gguf.md) — another community 27B GGUF; Huihui ablates refusal layers with `K_L` requantization while TURBO Heretic-decensors then retrains for reasoning compression with output-tensor/MTP precision mods.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — this family targets standard-app GGUF serving (LMStudio-measured) with a separate `mmproj` vision file.
- Related to [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — the KL/refusal and BF16-plus-points claims are the fidelity signals that page says to judge with KL, trajectory, and leakage-controlled checks; no such evaluation is in the source.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF.md` inspected statically (**Observed**); no commands executed, so install, Jinja, sampling, smoothing, MTP, tool-calling, and vision recipes are **Reported**, not reproduced.
- Referenced `star-wars-hans-solo.gif` and `qwen38-27b-turbo-tfcf735.png` are absent from `raw/`; the PNG's benchmark visual is covered by the transcribed table above and both assets are excluded as decorative.
- Five detailed example generations plus the inline creative-writing snippet (lines ~72–100, ~1073–7184, including export CSS and an intimacy-themed prompt) excluded as transient narrative with explicit content; only the reduced-thinking claim they illustrate is compiled above.
- Embedded official Qwen3.8-27B documentation (highlights, model overview, text/VL benchmark tables, Quickstart/API, Best Practices/YaRN, citation) reconciled against existing coverage in [Qwen3.8 Local Deployment](qwen3.8.md) and related Qwen3.8/SGLang concepts rather than re-ingested; only TURBO-specific deltas are compiled here.
- External artifacts uninspected: `NM-DAU` source repo, upstream `Qwen/Qwen3.8-27B`, Polar/F451/Reasoning-STRICT datasets, Fable-Fusion-711/TWIN-TURBO/40B/9B sibling repos, trohrbaugh Heretic ARA build, source-file collection, Maximizing-Model-Performance guide, community-tab reports, and linked SGLang/vLLM/TokenSpeed/QwenCloud docs.
- Benchmark and speed figures state no harness version, workload shape, or full metric definitions beyond benchmark names (single RTX 5090 / Windows 11 / LMStudio note for tok/s only), so per the SCOPE benchmark rule everything stays **Reported**.
- Placeholder `OPENAI_API_KEY`/`OPENAI_BASE_URL` values in the embedded API examples carry no secret; no live credentials found.

[^turbo]: DavidAU TURBO-Fable-Cold-Fusion-735-882 model card — `../raw/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF.md` (frontmatter with Apache-2.0, Polar/F451-STRICT datasets, `NM-DAU` TURBO base; TURBO headline with 735/882 8-bit and 719 4-bit claims; strict goals; COLD FUSION GAIN plus Fable 711 DNA; COLAB; eleven-build program; TESTING with trust-but-verify human testing; IMPORTANT usage help; TOOL CALLING minima; GENERAL MODEL USAGE with prompt-expansion remedy; Modification of REASONING with Jinja `reasoning_effort` edit and ADVANCED injection detail; Regular and MTP GGUFS with NEO IMATRIX, 16-bit output tensor, Q8_0 MTP, temp/rep-pen and 50%-acceptance rules, LOW tiers; SPEED 75 vs 90+ tok/s note; Model 256K plus VISION mmproj; Qwen Model Settings; DE-CENSORING STATS stage 1/2 KLD/refusal tables; BENCHMARKS by Nightmedia Instruct-mode table with thinking-exceeds-instruct and BF16 +2–5 notes; SUPER Qwen Universe; uncensored-vs-trained note; CHAT/ROLEPLAY 1.5 smoothing; Class 1 guide pointer; embedded official Qwen3.8-27B docs; FIVE DETAILED EXAMPLE GENERATION(S) header): TURBO multi-stage lineage with 1/2-to-1/10 thinking reduction across xhigh/medium/low, NEO-CODER MAX/MTP/LOW packaging with Q8_0 MTP and 16-bit output-tensor mods, Nightmedia 7-bench deltas, ARA Heretic KLD/refusal evidence, and sampling/tool/vision serving guidance.
