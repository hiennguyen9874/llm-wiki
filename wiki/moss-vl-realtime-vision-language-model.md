---
type: Concept
title: MOSS-VL real-time vision-language model
description: An 11.3B Qwen3-8B-based VLM that keeps visual tokens outside text decoding through gated cross-attention, then learns silence, response timing, and revision in a final Realtime-SFT stage.
tags: [vision-language-models, video-understanding, streaming, real-time-interaction, efficient-inference]
status: draft
created: 2026-08-20
generated: { by: llm-wiki-agent/1, at: 2026-08-20T10:09:14Z }
sources:
  - id: openmoss-moss-vl-2026
    resource: ../raw/2608.15045_MOSS-VL/main.tex
    title: MOSS-VL Technical Report
---

# MOSS-VL real-time vision-language model

MOSS-VL is an open 11.3B vision-language-model family designed for video that continues perceiving while it generates. It couples a Qwen3-8B-initialized decoder to native-resolution visual features only through zero-initialized gated cross-attention, then adds Realtime-SFT to teach a single model to remain silent, emit proactively, and revise as a stream evolves. The source’s architecture, data, code-release, and result claims are author-reported; its L5 real-time capability is qualitatively demonstrated, while public quantitative evaluation reaches streaming levels L2-L4 only.[^openmoss-moss-vl-2026]

## Architecture and operation

- **Separated visual memory:** A 27-layer vision encoder (initialized from Qwen3-VL) extracts native-resolution frame features, which are spatially merged 2x2 and projected to the decoder. The 48-layer decoder has 36 text self-attention layers and 12 tanh-gated cross-attention layers, inserted every fourth layer; visual patches are keys/values rather than decoded-sequence tokens. The gates start at zero, preserving the language backbone at initialization.[^openmoss-moss-vl-2026]
- **Stream-aligned positions:** XRoPE applies three-axis rotary positions `(t, h, w)` to text queries and visual keys so frame placeholders and visual separators advance on one logical timeline. Per-frame timestamp tokens separately expose wall-clock time, avoiding an assumption that sequence position implies frame rate.[^openmoss-moss-vl-2026]
- **Append-only streaming state:** Each incoming frame is encoded once and appended to the cross-attention KV cache. The text stream receives only timestamp and placeholder tokens, allowing generation to attend to new frame features without re-encoding prior frames or inserting their patches into self-attention.[^openmoss-moss-vl-2026]
- **Model lineage:** The reported 0708 release includes Base after four pre-training stages, Instruct after ordinary SFT, and Realtime after Realtime-SFT; two earlier 0408 Base/Instruct checkpoints are also released. The report evaluates Instruct offline and Realtime on streaming benchmarks.[^openmoss-moss-vl-2026]

## Training and response policy

The four-stage pre-training curriculum progresses from connector-only image-caption/OCR alignment (150.3B tokens, 8K context) to full-model multimodal training, high-quality training, and long-context annealing (450.1B tokens, 256K context). The report says its mixtures include collected/reorganized data and large-scale synthesized caption, OCR, grounding, and temporal-grounding data, decontaminated against its evaluation suites.[^openmoss-moss-vl-2026]

Standard SFT uses 7.6M samples (102.8B tokens) to form the offline Instruct model. Realtime-SFT continues from it with 0.56M samples (about 34.8B tokens, stated as under 3% of total training tokens). Each arriving frame has a decision slot: `<|silence|>`, `<|response|>` followed by a text chunk, or a final chunk closed by `<|silence|>`. It adds only the two state tokens and uses next-token prediction rather than a separate policy head.[^openmoss-moss-vl-2026]

The report says this corpus combines filtered/re-annotated open streaming data with caption-derived synthetic interactions, including delayed evidence, answer revision, and mid-reply interruption. It reports 2.2M emission decisions, 58.7% self-timed, and 5.1% of samples where the correct behavior is silence throughout. A focal, inverse-frequency reweighting targets the highly imbalanced silence/response state tokens. Offline mode uses no special prompt; streaming and real-time share one system prompt, so the three modes use the same weights.[^openmoss-moss-vl-2026]

## Reported evidence

- **Streaming:** Against the report’s selected open streaming baselines, MOSS-VL-Realtime reports best averages on OVO-Bench (70.2 vs. 65.3 runner-up), OmniMMI (32.7 vs. 25.4), and ProactiveVideoQA (47.2 vs. 42.7), and second on StreamingBench visual average (69.7 vs. 71.1). It reports the strongest score on three proactive subsets: OmniMMI proactive alerting (66.0 vs. 37.5), StreamingBench proactive output (60.0 vs. 53.2), and OVO-Bench forward active responding (62.1 vs. 55.8). Baseline values are largely taken from their respective reports, so protocols and coverage differ across comparisons.[^openmoss-moss-vl-2026]
- **Offline:** MOSS-VL-Instruct is compared with 7-12B open models on 39 benchmarks. The report highlights temporal-reasoning leads on Minerva (40.5), TOMATO (39.5), and VideoMME-Logical (17.1), while also reporting deficits on MMMU, document-oriented tasks, and standard grounding. Except for specified Gemma and OmniDocBench entries, baseline values come from official reports and may use different inference settings.[^openmoss-moss-vl-2026]
- **Serving:** On one H200 using SGLang, compared with Qwen3-VL-8B under a stated shared Qwen3-8B language backbone and matched visual-token conditions, the reported MOSS-VL time-to-first-token advantage increases from 2.8x to 5.1x as visual context grows; end-to-end latency advantage rises from 1.9x to 4.3x. Same-video tests retain roughly twice as many MOSS-VL vision tokens because it does not temporally compress frames, so this is a source-specific architectural comparison rather than a general latency ranking.[^openmoss-moss-vl-2026]

## Limits and evidence boundaries

- The report is a supplied August 2026 technical report. Its full LaTeX manuscript, appendix, tables, and rendered architecture, position-encoding, latency, overview, and demo figures were reviewed; no independent replication, weights, code execution, training data, or external benchmark audit was performed here. Reported claims remain unverified.[^openmoss-moss-vl-2026]
- The source defines L5 as perception during text generation, enabling a reply to be revised or stopped when evidence changes. It offers live demos and released real-time inference code as qualitative evidence, but states that public benchmarks only quantify L2-L4 and that an L5 benchmark remains absent.[^openmoss-moss-vl-2026]
- MOSS-VL has no audio input on StreamingBench and does not report the audio-dependent Omni-Source group. Offline comparisons vary in frame count, resolution, protocols, baseline model sizes, and whether results were reproduced by the authors.[^openmoss-moss-vl-2026]
- The model family does not use reinforcement learning or a thinking mode in the reported release. The authors associate this with weaker reasoning-heavy and document-centric results, but this is an attribution from their discussion rather than a controlled causal ablation.[^openmoss-moss-vl-2026]

## Relationships

- Synthesized by: [Recent vision-language research directions](recent-vision-language-research-directions.md), which distinguishes MOSS-VL's decoder-integrated response policy from codec-native gating approaches.
- Used by: [Vision-language task-to-model map](vision-language-task-to-model-map.md) for real-time video understanding where an explicit L2-L4 streaming evaluation and qualitative L5 behavior are relevant.
- Related: [Mage-VL codec-native streaming vision-language model](mage-vl-codec-native-streaming-vision-language-model.md) is another wiki concept for offline and proactive video streaming, but it applies codec-guided input sparsity and an external event gate rather than MOSS-VL's cross-attention cache and decoder-token response policy.

[^openmoss-moss-vl-2026]: OpenMOSS Team, “MOSS-VL Technical Report” (technical report, August 2026), [complete supplied manuscript source](../raw/2608.15045_MOSS-VL/main.tex).
