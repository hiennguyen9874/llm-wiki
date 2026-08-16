---
type: Concept
title: UniTime
description: An MLLM-based universal video temporal-grounding framework that interleaves textual timestamps with scaled video tokens and retrieves moments coarse-to-fine.
tags: [video, video-language, temporal-grounding, multimodal-llm, long-video]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:36:46+07:00 }
sources:
  - id: unitime-paper
    resource: ../raw/UniTime/main.tex
    title: "Universal Video Temporal Grounding with Generative Multi-modal Large Language Models"
---

# UniTime

UniTime is a temporal-grounding framework for generative multimodal LLMs: it inserts textual timestamps alongside video tokens, then generates matching start and end times for a natural-language query. For long video, it combines a fixed token budget with coarse segment retrieval followed by fine-grained grounding within selected segments.[^unitime-paper]

## Method

Adaptive frame scaling allocates a per-frame token budget from a total budget. UniTime resizes short-video frames and uses feature-level bilinear token compression for longer video; inputs beyond a maximum frame count are split into clips. This preserves a fixed budget per processed clip, rather than giving the model unrestricted global access to an arbitrary-length video.[^unitime-paper]

Each frame or coarse segment is prefixed with free-text timestamp tokens. The MLLM receives this interleaved timestamp-and-visual sequence plus the query and generates the smallest matching interval among the supplied timestamps. Long-video inference first retrieves candidate segments per clip, can recursively aggregate and retrieve candidates, then performs fine-grained grounding in the selected segments.[^unitime-paper]

Training mixes full videos for coarse supervision with shorter sampled segments for fine supervision. Its video-centric batching groups a video's query-answer pairs behind a shared video encoding while attention masks prevent interactions between pairs; this is intended to avoid repeated video I/O and encoding.[^unitime-paper]

## Reported evidence and limits

The paper reports results in zero-shot, dataset-specific, and universal-pretraining settings on five temporal-grounding benchmarks, plus retrieval-augmented long-video VideoQA. Its stated Qwen2-VL-7B implementation samples at 2 fps, uses 128- and 1,024-frame thresholds, and caps an input at 16,384 tokens.[^unitime-paper]

These are source-reported benchmark results. The method's long-video capability depends on splitting, candidate retrieval, and refinement under a fixed per-clip token budget; it does not demonstrate lossless global processing of arbitrary-length video. The authors also identify reliance on fixed segment length and limited temporal-grounding-only training data as limitations.[^unitime-paper]

## Relationships

- **Instantiates:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) through timestamp-conditioned natural-language moment localization; it is grounding evidence, not general temporal-reasoning evidence.[^unitime-paper]
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) through adaptive allocation, segmented retrieval, and coarse-to-fine refinement.[^unitime-paper]
- **Supports:** retrieval-augmented long-video VideoQA by selecting a segment for a separate Qwen2-VL-7B answer-generation model; this is a two-stage evaluation, not an end-to-end unified reasoning model.[^unitime-paper]

[^unitime-paper]: [Universal Video Temporal Grounding with Generative Multi-modal Large Language Models](../raw/UniTime/main.tex)
