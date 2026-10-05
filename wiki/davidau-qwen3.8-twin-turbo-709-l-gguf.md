---
type: Concept
title: DavidAU Qwen3.8-27B TWIN-TURBO 709-L GGUF
description: TWIN-TURBO thinking-compressed Heretic-uncensored fine-tune of Qwen3.8-27B scoring 709 ARC-C with five reasoning plus five instruct modes and NEO/NEO MAX MTP GGUFs.
tags: [qwen3.8, gguf, quantization, finetune, reasoning, mtp, speculative-decoding, uncensored, llama-cpp, local-inference, vision]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T19:45:00Z }
sources:
  - id: twin
    resource: ../raw/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored-NM-DAU-NEO-MTP-GGUF.md
    title: Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored-NM-DAU-NEO-MTP-GGUF (DavidAU model card)
---

DavidAU's TWIN-TURBO-Fable-Cold-Fusion-709-L is a multi-stage fine-tune, multi-fine-tune and multi-stage merge of `Qwen/Qwen3.8-27B` that combines `Qwen3.6-27B-Fable-Fusion-711` (dark-roast) and `Qwen3.8-27B-Cold-Fusion-GAIN-V1.1` DNA, re-Heretic-decensors and re-tunes it with extra TWIN-TURBO tuning, and ships NEO plus NEO MAX regular and MTP GGUFs claiming 0.709 ARC-C in 8-bit and 0.701 in 4-bit with 1/2 down to 1/20 thinking-token reduction and five reasoning plus five zero-reasoning-token instruct modes switchable in chat, via API, or in the Jinja template[^twin]. **Reported** by the model card unless noted; all benchmark, refusal/KL, and throughput figures carry the unstated-protocol limits in Coverage limits.

## What TWIN-TURBO changes

- Frontmatter declares Apache-2.0, `image-text-to-text` pipeline, base `DavidAU/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored`, and `DavidAU/Polar-STRICT-Datasets` plus `DavidAU/F451-STRICT-Datasets` plus `DavidAU/THE-DECKARD-Datasets`; the entry point was inspected statically (**Observed**) with no commands executed[^twin]. **Reported** identity.
- Card headline is a tune matching the "legendary" Qwen3.6-27B FF711 stability and power at 709 ARC-C (stated 118 points above Qwen3.8-27B, framed as the OpenAI/Claude/Gemini "zone of intelligence") in 8-bit and 701 ARC-C in 4-bit; TWIN-TURBO means drastically fewer thinking tokens (1/2 down to as low as 1/20) while maintaining output detail and quality, in contrast to regular Qwen3.8-27B spending thousands of tokens on formatting before generating[^twin]. **Reported**.
- Instruct "medium" is the quoted 709 figure and reasoning is stated to score even higher; both 4-bit and 8-bit are claimed to exceed base Qwen3.8-27B on all seven critical benchmarks and to exceed all seven benches for Qwen3.6-35B-A3B, Qwen3.6-27B, and Qwen3.5-27B[^twin]. **Reported**.
- Stated strict goals are higher general intelligence and problem solving, smaller quants at higher quality, new reasoning and instruct modes, thinking blocks cut 1/2 to as low as 1/20 (median reduction roughly 2/3), reformatted and improved thinking blocks, faster token generation especially MTP, coverage across all three base thinking modes, zero "benchmaxing", and maintained plus raised core benchmarks without modifying the core model outside that goal[^twin]. **Reported**.
- Lineage is COLD FUSION (`GAIN` plus Unsloth trainers/systems, per-sample dynamic training invented during `Qwen3.6-27B-Fable-Fusion-711` R&D) together with Fable Fusion 711 training; this build contains both that 711 dark-roast and `Qwen3.8-27B-Cold-Fusion-GAIN-V1.1` as core DNA, then was Heretic-decensored again, fine-tuned, and given additional TWIN-TURBO tuning[^twin]. **Reported** method summary.
- Card self-grades the GAIN-V1.1 component at level 1–2 versus Fable-Fusion-711 at level 7–8, positions this as one of eleven team Qwen3.8-27B builds all over 700 ARC-C and exceeding base Qwen3.8 benches, and points to the `NM-DAU` source repo for build/bench details[^twin]. **Reported**.
- Collaboration lists DavidAU (multi-stage tunes), Nightmedia (merge/benching), TeichAI (Polaris dataset), armand0e (light Fable 5 traces), trohrbaugh (Heretic stage 1), and nbeerbower (tunes/models), plus light Fable traces, light Claude Opus reasoning/thinking, F451 in-house, some GPT5 Polaris non-reasoning, and in-house ML/Heretic-repair datasets; "einstein" reasoning mode is specially noted as built using some components from Stunspot Prompting at the public/free membership level[^twin]. **Reported**.
- Validation is per-stage benching of fine-tunes and every merge step plus final side-by-side human testing of base versus new model ("trust, but verify"); claimed effects are improved instruction following, higher general intelligence and problem solving, better thinking/reasoning, exceptional low quants, Heretic uncensored pre-tuning, no corruption of the base model, and retained vision[^twin]. **Reported**.

## Five reasoning plus five instruct modes

- Defaults are unchanged for drop-in use: reasoning at `xhigh`, instruct (thinking off) at `medium`; unlocking adds `xhigh`, `medium`, and `low` plus two new modes to instruct, where previously instruct was limited to `medium` power[^twin]. **Reported**.
- Reasoning modes are `spoon` (ULTRA xhigh research mode, hyper detailed, automatically uses more reasoning tokens), `einstein` (a `high` mode spawning up to 20 virtual agents to solve tasks, automatically uses more reasoning tokens), and standard Qwen3.8 `xhigh`, `medium`, and `low`; all five are also available as instruct modes with zero reasoning-token usage[^twin]. **Reported**.
- In-message switching uses `{REASON:xxx}` with `spoon`, `einstein`, `xhigh`, `medium`, or `low` for reasoning and `ispoon`, `ieinstein`, `ixhigh`, `imedium`, or `ilow` for instruct (the `i` prefix selects instruct); the marker can appear anywhere in the prompt, the last mode used persists for the current chat, a new chat reverts to defaults until the marker is used again, and the system strips the marker from the message stream so generation stays pure[^twin]. **Reported**.
- API form for reasoning (`reasoning_effort = 'xhigh'`, `enable_thinking = 'true'`) and instruct (`reasoning_effort = 'ixhigh'`, `enable_thinking = 'false'`); advanced use places chosen defaults at the top of the Jinja template[^twin]. **Reported**:

```
reasoning_effort = 'xhigh'
enable_thinking = 'true'
```

```
reasoning_effort = 'ixhigh'
enable_thinking = 'false'
```

## Thinking-token reduction and Jinja controls

- Reduction spans all three Qwen3.8 modes (`xhigh` default, `medium`, `low`) while output detail stays high; in many cases reasoning/output sizes invert as detail moves from the thinking block to the output, and the card frames untuned Qwen3.8-27B as looking repeatedly for 10k–40k thinking tokens before leaping while TURBO leaps almost immediately[^twin]. **Reported**.
- More detailed prompts shrink thinking further because the model guesses less; multi-turn refinements after the first output often hit ~1/5 normal size or lower; to buy back deeper reasoning the card recommends expanded task-specific instructions (for example asking for positioning checks or drafts) rather than generic "double check your work"[^twin]. **Reported**.
- Card warns the reasoning modification is a major model change to test carefully per use case[^twin]. **Reported**.
- Without an app-level switch, set effort at the very top of the Jinja template (`xhigh` default)[^twin]. **Reported**:

```
{%- set reasoning_effort = 'medium' %}
```

- In LMStudio use DEV mode with "advanced updates" off; other apps vary; the from-source quant recipe is to edit `chat-template.jinja` and the token-config/chat-template files from `DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU`[^twin]. **Reported**.
- Advanced Jinja behavior: Qwen3.8 uses system-prompt injection to control reasoning; `medium` disables injection so a custom reasoning system prompt can be set, while `xhigh`/`low` inject their own instructions and unknown values raise; the template plus system prompts can be retuned per use case[^twin]. **Reported**.

## Quant packaging: regular, MTP, and TOOLS

- All regular and MTP quants are NEO IMATRIX, claimed +2–4% accuracy over normal GGUFs plus better long-context performance; the output tensor (10–20% of output) is raised to 16-bit full precision on MAX quants only[^twin]. **Reported**; note the MAX-only scope differs from the sibling TURBO card's every-quant wording.
- MTP files carry `MTP` in the name with MTP tensors at Q8_0; keep temperature at 1 or below and repetition penalty at 1 (off) or MTP performance degrades; below 50% token acceptance (predict 2 tokens) switch to regular quants[^twin]. **Reported**.
- Reported speed on `Q4_K_S` 4-bit is ~75 tok/s regular versus 90+ tok/s MTP at 60% acceptance predicting 2 tokens, measured on an RTX 5090 under Windows 11 in LMStudio; Linux/Mac is generally faster and MTP varies with GPU, app, OS, and hardware, degrading on creative/complex prompts or temperature above 1 where regular GGUFs win[^twin]. **Reported** with single-rig, single-app limits.
- Serving advice is to download at least one regular and one MTP quant and test per use case; MTP can also run faster as the context fills or in multi-turn chats; there is otherwise no functional difference, only speed[^twin]. **Reported**.
- `TOOLS` GGUFs (word `tools` in the filename) keep all regular/MTP functions including every reasoning/instruct mode but add TOOL/AGENT-specific error checks and more robust tool-calling routines; the card says they may or may not beat the other GGUFs per use case and recommends trying both[^twin]. **Reported**.
- Model scope is 256K context with GGUFs running in standard apps; vision is tested but needs one separate `mmproj` file in the same folder as the GGUF[^twin]. **Reported**.

## Sampling, tool calling, and chat/roleplay

- Qwen thinking defaults are temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0; precise-coding thinking uses temperature 0.6; instruct/non-thinking uses temperature 0.7, top_p 0.80, top_k 20, min_p 0.0, presence_penalty 1.5, repetition_penalty 1.0; minimum 8K–16K context[^twin]. **Reported**.
- Tool calling needs minimum `q4km` (`q5ks`/`5km` better, `Q6` MAX or `low` recommended) with temperature 0.6/0.7 and repetition penalty 1 (off); below `q4km` tool calling may break and overly aggressive caching may further impair functions; a pinned community discussion carries a temporary fix while GGUFs are re-generated and re-uploaded[^twin]. **Reported**.
- For KoboldCpp, oobabooga/text-generation-webui, or Silly Tavern chat/roleplay smoothing, set `smoothing_factor` (`Smooth_F` / `Smoothing`) to 1.5; text-generation-webui GGUF path needs `llama_HF` plus config files from the source-file collection; alternatives are repetition penalty 1.1–1.15 or Quadratic Sampling where supported[^twin]. **Reported**.
- This is a "Class 1" model whose full parameter/sampler guide, example generations, and advanced issue remedies live in the linked Maximizing-Model-Performance collection[^twin]. **Reported**; the external guide is uninspected.
- Card notes uncensored-versus-trained-uncensored behavior: refusals are removed but some requests need extra directive push (including explicit slang terms for x-rated content) or output stays bland versus a model trained on uncensored content[^twin]. **Reported**; prompt contents and example generations are excluded per Coverage limits.

## Heretic de-censoring stats

- Stage 1 by trohrbaugh (`trohrbaugh/Qwen3.8-27B-heretic-ara`) uses Heretic v1.2.0+custom with Arbitrary-Rank Ablation (ARA) on `Qwen/Qwen3.8-27B`; table is KL 0.0535 with 0/100 refusals versus 99/100 for the original[^twin]. **Reported**.
- Stage 2 after stage-1 tuning/merges/adjustments in lab is KL 0.0025 with 11/100 refusals versus 86/100 for the stage-1 build; card prioritizes ultra-low KLD first (performance/quality) with low refusal rate second[^twin]. **Reported**.
- Stage 2 TWIN-TURBO split: this repo (`709-L`) reports 68/100 refusals at KL 0.0025, while the separate `709-ULTRA-HERETIC` repo reports 6/100 refusals at KL 0.0397; lower KLD is better and stage 2 was balanced for ultra-low KLD first with refusal rate second[^twin]. **Reported**.
- Safety boundary: uncensored adult-capable tune; card retains tame defaults requiring explicit direction for graphic content. Harmful-prompt contents, attack-chain detail, and verbatim explicit generations are excluded from this concept. **Synthesis** boundary decision.

## Nightmedia benchmarks

- Instruct-mode comparison (`arc/c, arc/e, boolq, hswag, obkqa, piqa, wino`) — **Reported** with harness/protocol unstated[^twin]:

| Model | Scores |
| --- | --- |
| TWIN-TURBO-709-L mxfp8 | 0.709, 0.876, 0.914, 0.827, 0.524, 0.834, 0.779 |
| TWIN-TURBO-709-L mxfp4 | 0.701, 0.877, 0.913, 0.821, 0.518, 0.830, 0.786 |
| TWIN-TURBO-709-ULTRA-HERETIC Stage2b-rplus3 mxfp8 (separate repo) | 0.699, 0.873, 0.911, 0.827, 0.528, 0.833, 0.781 |
| TWIN-TURBO-709-ULTRA-HERETIC Stage2b-rplus3 mxfp4 (separate repo) | 0.692, 0.879, 0.910, 0.823, 0.518, 0.835, 0.775 |
| Qwen3.8-27B mxfp8 base | 0.591, 0.782, 0.896, 0.746, 0.448, 0.801, 0.711 |
| Qwen3.8-27B mxfp4 base | 0.581, 0.771, 0.889, 0.738, 0.442, 0.798, 0.713 |
| Qwen3.6-27B mxfp8 base | 0.647, 0.803, 0.910, 0.773, 0.450, 0.806, 0.742 |
| Qwen3.6-35B-A3B-Instruct mxfp8 base | 0.581, 0.757, 0.892, 0.751, 0.428, 0.803, 0.688 |
| Qwen3.5-27B mxfp8 base | 0.557, 0.711, 0.868, 0.533, 0.452, 0.706, 0.695 |

- Test notes: Instruct mode suits the harness better; thinking-mode testing also shows gains but not their full extent, and thinking mode is expected to exceed Instruct scores in most cases; BF16 is roughly 2–5 points above MXFP8 per metric with some metrics higher[^twin]. **Reported**.
- Sibling positioning in the card's "SUPER Qwen Universe" (Fable-Fusion-711 27B, TURBO 735-882, this TWIN-TURBO 709-L, GAIN-V1.1, 40B Claude-Opus-Deckard, 9B Defiant) and third-party/community-tab claims are promotional cross-linking and are not reproduced beyond this pointer[^twin]. **Synthesis** exclusion decision.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the official Unsloth GGUF/NVFP4 local path while this page is the TWIN-TURBO thinking-compression Heretic fine-tune with in-chat/API/Jinja mode switching and its own NEO/NEO MAX ladder plus sampling guidance.
- Related to [DavidAU Qwen3.8-27B TURBO Fable Cold Fusion GGUF](davidau-qwen3.8-turbo-fable-cold-fusion-gguf.md) — sibling tune sharing COLD FUSION plus Fable-711 DNA, Heretic re-decensoring, NEO-IMATRIX plus Q8_0-MTP packaging, Jinja effort controls, and Nightmedia Instruct-mode tables; TURBO headlines 735/882 with 1/2-to-1/10 reduction and NEO-CODER MAX tiers while TWIN-TURBO headlines 709/701 with 1/2-to-1/20 reduction, spoon/einstein modes, and NEO/NEO MAX plus TOOLS tiers.
- Related to [DavidAU Qwen3.8-27B Cold Fusion GAIN GGUF](davidau-qwen3.8-cold-fusion-gain-gguf.md) — sibling tune sharing GAIN/Unsloth lineage, NEO-IMATRIX plus Q8_0-MTP packaging, Jinja effort controls, and Nightmedia Instruct-mode tables; GAIN-V1.1 is non-Heretic level 1–2 groundwork while TWIN-TURBO adds Fable-711 DNA plus Heretic re-decensoring, extra TWIN tuning, and the 709/701 headline.
- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — the NEO-IMATRIX packaging here is a per-layer dynamic/imatrix-calibrated GGUF family in the same lineage, with the card's +2–4% claim kept as **Reported**.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — the `MTP`-suffixed tiers preserve multi-token-prediction heads with the same temperature, repetition-penalty, and acceptance-rate (`<50%` switch) operating rules documented there.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — this family targets standard-app GGUF serving (LMStudio-measured) with a separate `mmproj` vision file.
- Related to [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — the KL/refusal and BF16-plus-points claims are the fidelity signals that page says to judge with KL, trajectory, and leakage-controlled checks; no such evaluation is in the source.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored-NM-DAU-NEO-MTP-GGUF.md` inspected statically (**Observed**); no commands executed, so install, Jinja, sampling, smoothing, MTP, tool-calling, and vision recipes are **Reported**, not reproduced.
- Referenced `launch-arm.gif` is absent from `raw/` and excluded as decorative; no GGUF file-size ladder, imatrix recipe, perplexity table, or checksum/manifest appears in this card, so per-file fit and fidelity guidance is absent.
- Creative-writing snippet plus the `FIVE DETAILED EXAMPLE GENERATION(S)` placeholder (`TO BE ADDED`) excluded as transient narrative with explicit content; only the reduced-thinking claim they illustrate is compiled above.
- Embedded official Qwen3.8-27B documentation (highlights, model overview, text/VL benchmark tables, serving, Quickstart/API, Best Practices/YaRN, citation) reconciled against existing coverage in [Qwen3.8 Local Deployment](qwen3.8.md) and related Qwen3.8/SGLang concepts rather than re-ingested; only TWIN-TURBO-specific deltas are compiled here.
- External artifacts uninspected: `NM-DAU` source repo, upstream `Qwen/Qwen3.8-27B`, Polar/F451/Deckard datasets, Fable-Fusion-711/TURBO-735/GAIN-V1.1/ULTRA-HERETIC/40B/9B sibling repos, trohrbaugh Heretic ARA build, Stunspot Prompting components, source-file collection, Maximizing-Model-Performance guide, community-tab reports including the pinned tool-calling fix, and linked SGLang/vLLM/TokenSpeed/QwenCloud docs.
- Benchmark and speed figures state no harness version, workload shape, or full metric definitions beyond benchmark names (single RTX 5090 / Windows 11 / LMStudio note for tok/s only), so per the SCOPE benchmark rule everything stays **Reported**.
- Placeholder `OPENAI_API_KEY`/`OPENAI_BASE_URL` values in the embedded API examples carry no secret; no live credentials found.

[^twin]: DavidAU TWIN-TURBO-Fable-Cold-Fusion-709-L model card — `../raw/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored-NM-DAU-NEO-MTP-GGUF.md` (frontmatter with Apache-2.0, Polar/F451-STRICT plus THE-DECKARD datasets, `NM-DAU` TWIN-TURBO base; TWIN-TURBO headline with 709 8-bit and 701 4-bit claims; STRONGER/CTRL five-plus-five mode summary; multi-stage lineage with COLD FUSION GAIN plus Fable 711 DNA, Heretic re-decensoring, and extra TWIN tuning; COLAB plus Stunspot special mention; eleven-build program; TESTING with trust-but-verify human testing; five reasoning plus five instruct modes with in-chat `{REASON:xxx}` persistence, API kwargs, and Jinja `reasoning_effort` edits with injection detail; thinking-reduction and prompt-expansion notes; TOOL CALLING minima with pinned-fix pointer; Regular/MTP/TOOLS GGUFS with NEO IMATRIX, MAX-only 16-bit output tensor, Q8_0 MTP, temp/rep-pen and 50%-acceptance rules, and 75 vs 90+ tok/s note; 256K plus VISION mmproj; Qwen Model Settings; DE-CENSORING STATS stage 1/2 plus 709-L/ULTRA-HERETIC tables; BENCHMARKS by Nightmedia Instruct-mode table with thinking-exceeds-instruct and BF16 +2–5 notes; SUPER Qwen Universe; uncensored-vs-trained note; CHAT/ROLEPLAY 1.5 smoothing; Class 1 guide pointer; embedded official Qwen3.8-27B docs; FIVE DETAILED EXAMPLE GENERATION(S) placeholder): TWIN-TURBO 1/2-to-1/20 thinking reduction with spoon/einstein modes, NEO/NEO MAX plus TOOLS packaging, Nightmedia 7-bench deltas, ARA Heretic KLD/refusal evidence, and sampling/tool/vision serving guidance.
