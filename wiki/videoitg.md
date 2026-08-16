---
type: Concept
title: VideoITG
description: An instruction-conditioned Video-LLM frame-selection framework and automatically constructed 40K-video temporal-grounding dataset.
tags: [video, video-llm, temporal-grounding, frame-selection, multimodal-llm]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T03:40:02Z }
sources:
  - id: videoitg-paper
    resource: ../raw/VideoITG/main.tex
    title: "VideoITG: Multimodal Video Understanding with Instructed Temporal Grounding"
---

# VideoITG

VideoITG is an instruction-conditioned frame-selection framework for a separate answering Video-LLM. Its accompanying VideoITG-40K dataset has 40K videos and 500K instruction-grounded annotations, generated through the automated VidThinker pipeline.[^videoitg-paper]

## VidThinker data construction

VidThinker progressively narrows each question-answer pair's visual evidence:

1. Split a video into five-second clips; derive instruction-relevant phrases from the question and answer with an LLM, then use a VLM to produce visually grounded, instruction-conditioned clip captions.
2. Have an LLM select the relevant clip indices from the ordered captions, considering semantic and temporal relations.
3. Classify frames within selected clips as relevant or not relevant and retain positive frames.[^videoitg-paper]

The pipeline assigns one of four sampling strategies: CLIP-feature diversity selection for semantic-only instructions, fixed-rate sampling for motion-only instructions, a hybrid of both for joint semantic-and-motion instructions, and sparse diverse coverage over the whole video for open-ended instructions without explicit cues.[^videoitg-paper]

The dataset is derived from LLaVA-Video data; the paper reports videos of 30 seconds to three minutes (120 seconds on average) and 10--15 multiple-choice or open-ended QA pairs per video.[^videoitg-paper] The appendix says the clip-retrieval stage uses GPT-4o-mini and reports human-in-the-loop review, but does not specify the reviewed sample size or inter-annotator agreement.[^videoitg-paper]

## Frame selector

Given encoded frame features and an instruction, VideoITG scores frames for relevance; the downstream Video-LLM answers from the selected frame features and instruction. The paper describes three alternatives:

- a generative next-token formulation for frame classification;
- a frame classifier retaining causal attention, with a per-frame spatially averaged anchor token after the instruction to mediate temporal cues; and
- a full-attention frame classifier that average-pools each frame's visual tokens and omits anchors.[^videoitg-paper]

The reported experiments use the full-attention variant for subsequent evaluations. The stated implementation can score up to 512 frames (16 visual tokens each) and selects the top 32 by default; this is fixed-budget candidate scoring, not unrestricted full-video attention.[^videoitg-paper]

## Reported evidence and limits

The source reports higher benchmark scores than uniform sampling across the evaluated answering Video-LLMs and long-video QA benchmarks. For example, with LLaVA-Video-7B, selecting 32 frames raised the reported average across LongVideoBench, MLVU, and VideoMME duration splits from 58.4 to 62.9; these are source-reported comparisons, not independently verified here.[^videoitg-paper]

On one NVIDIA A100 configuration, the paper reports 6.42 seconds per sample for scoring 512 frames, selecting 32, and generating 27 text tokens; the vision encoder and answering LLM account for 5.81 seconds of that total. This is a hardware- and configuration-specific measurement, not a general throughput guarantee.[^videoitg-paper]

The selector and answering Video-LLM remain separate inference modules. The source does not establish end-to-end gradient optimization between selection and answer quality, nor lossless coverage of videos beyond its scored-frame budget.[^videoitg-paper]

## Relationships

- **Instantiates:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) through instruction-conditioned clip retrieval and frame relevance selection; this is grounding supervision and frame selection, not evidence of general temporal reasoning.[^videoitg-paper]
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) through instruction-conditioned, fixed-budget candidate scoring and top-$k$ frame selection.[^videoitg-paper]

[^videoitg-paper]: [VideoITG: Multimodal Video Understanding with Instructed Temporal Grounding](../raw/VideoITG/main.tex)
