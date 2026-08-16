---
type: Concept
title: Video-language temporal grounding and reasoning
description: Text-conditioned localization and inference over event timing, order, duration, frequency, state changes, and causal relations in video.
tags: [video, language, temporal-grounding, temporal-reasoning, video-llm]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:46:05+07:00 }
sources:
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
  - id: internvideo-paper
    resource: ../raw/InternVideo/main.tex
    title: "InternVideo: General Video Foundation Models via Generative and Discriminative Learning"
  - id: internvideo2-paper
    resource: ../raw/InternVideo2/main.tex
    title: "InternVideo2: Scaling Foundation Models for Multimodal Video Understanding"
  - id: unitime-paper
    resource: ../raw/UniTime/main.tex
    title: "Universal Video Temporal Grounding with Generative Multi-modal Large Language Models"
  - id: videoitg-paper
    resource: ../raw/VideoITG/main.tex
    title: "VideoITG: Multimodal Video Understanding with Instructed Temporal Grounding"
  - id: neus-qa-paper
    resource: ../raw/NeuS-QA/main.tex
    title: "NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning"
  - id: f2g-paper
    resource: ../raw/Foresee-to-Ground/main.tex
    title: "Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding"
---

# Video-language temporal grounding and reasoning

Video-language temporal grounding finds the interval in a video that matches a natural-language query; temporal reasoning additionally answers questions about relationships among events. The source treats these as distinct capabilities beyond image-style video QA.[^video-temporal-survey]

## Grounding

Given a video and query, temporal grounding returns a start and end time for the matching moment. The source uses the related names *moment retrieval*, *temporal sentence grounding*, and *natural-language video localization*.[^video-temporal-survey]

For long video, grounding needs a mechanism to preserve or retrieve relevant evidence without processing every frame at full resolution. Timestamp-aware tokens, adaptive frame scaling, and instruction-conditioned supervision are presented in the source as emerging approaches; their reported results are unverified in this wiki.[^video-temporal-survey]

## Reasoning relations

The source identifies these temporal reasoning targets:

- ordering: whether one event occurs before or after another;
- duration and frequency;
- intervening events and multi-hop relations;
- state transitions caused by actions; and
- causal explanations.

It argues that fine-grained temporal reasoning remains difficult for multimodal LLMs even when their appearance-based semantic understanding is strong.[^video-temporal-survey]

## Video–language alignment is not temporal grounding

InternVideo’s video–text branch contrastively aligns independently encoded video and text, then uses a caption decoder with cross-attention for multimodal fusion. The paper evaluates it on video retrieval and question answering, but does not report natural-language temporal localization or tests of temporal relations. It is therefore relevant as a source of video–text features, not evidence of the grounding and reasoning capabilities defined here.[^internvideo-paper]

InternVideo2 provides direct but bounded grounding evidence: with CG-DETR, its paper reports finetuned 6B features at 71.42 R1@0.5 and 56.45 R1@0.7 on QVHighlight, plus 70.03 R1@0.5 and 58.79 mIoU on Charades-STA. These evaluate natural-language moment localization under the stated protocols, not general temporal reasoning or arbitrary-duration evidence access.[^internvideo2-paper]

## Timestamp-conditioned MLLM grounding

UniTime makes each sampled frame or coarse segment addressable by interleaving a free-text timestamp with its visual tokens, then has an MLLM generate the matching interval. For long video, it retrieves coarse segments under a fixed token budget and refines within selected regions. This is direct temporal-grounding evidence, but does not establish arbitrary-duration full-context access or general temporal reasoning.[^unitime-paper]

## Instructed frame grounding

VideoITG supplies instruction-conditioned frame-selection supervision rather than only descriptive moment queries. Its automated VidThinker pipeline captions five-second clips under question-and-answer-derived cues, retrieves relevant clips, and selects relevant frames; its four instruction types pair semantic, motion, hybrid, or whole-video cues with different sampling strategies.[^videoitg-paper]

The reported full-attention selector scores a fixed candidate-frame budget and sends the top-ranked frames to a separate answering Video-LLM. This is evidence for query-conditioned evidence selection, not end-to-end answer optimization or general temporal reasoning.[^videoitg-paper]

## Cited event-span hypotheses

Foresee-to-Ground (F2G) supplies a different grounding interface: it constructs a compact, video-wide pool of learned candidate event spans, each with a span ID, coarse interval, and segment-local visual evidence. The Video-LLM is supervised to cite one span and then generate its answer and refined interval in a single structured response. This makes the intermediate hypothesis attributable, but a citation does not verify that the candidate or emitted boundary is correct.[^f2g-paper]

The source reports improvements over direct fine-tuning in its controlled Qwen3-VL-8B comparison and argues that residual errors are mainly limited by candidate-pool coverage. These are source-reported benchmark findings; the method covers single-interval visual grounding, not general multi-event temporal reasoning.[^f2g-paper]

## Explicit temporal representations

A neuro-symbolic direction translates questions and video events into explicit temporal relations such as *before*, *overlaps*, and *during*, then uses those relations to retrieve evidence before visual-language reasoning. This is a proposed architectural pattern in the source, not a verified general solution.[^video-temporal-survey]

## Logic-verified retrieval

NeuS-QA makes temporal relations executable: it translates a question into event propositions and a temporal-logic specification, labels a frame-based video automaton with VLM detections, and model-checks the specification before sending a satisfying interval to an answering VLM. This is evidence for query-conditioned, interpretable retrieval under the source's benchmark setup, not a guarantee that the VLM grounded every event correctly.[^neus-qa-paper]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Depends on:** [Long-video temporal modeling](long-video-temporal-modeling.md) for long-context evidence access.
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) for visual and video–text features.
- **Uses:** [InternVideo](internvideo.md) for video–text retrieval and question-answering features, not as a demonstrated temporal-grounding system.[^internvideo-paper]
- **Uses:** [InternVideo2](internvideo2.md) for reported CG-DETR temporal-grounding evaluations, not as general temporal-reasoning evidence.[^internvideo2-paper]
- **Includes:** [UniTime](unitime.md) as an MLLM temporal-grounding framework with textual timestamp tokens and coarse-to-fine long-video retrieval; this does not demonstrate general temporal reasoning.[^unitime-paper]
- **Includes:** [VideoITG](videoitg.md) as instruction-conditioned clip retrieval and fixed-budget frame selection for a separate answering Video-LLM; this is not general temporal-reasoning evidence.[^videoitg-paper]
- **Includes:** [NeuS-QA](neus-qa.md) as a temporal-logic and model-checking retrieval pipeline; its verification is conditional on VLM event grounding.[^neus-qa-paper]
- **Includes:** [Foresee-to-Ground (F2G)](foresee-to-ground.md) as cited candidate-span selection plus evidence-conditioned boundary refinement; it is grounding evidence, not evidence of general temporal reasoning.[^f2g-paper]

[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^internvideo-paper]: [InternVideo: General Video Foundation Models via Generative and Discriminative Learning](../raw/InternVideo/main.tex)
[^internvideo2-paper]: [InternVideo2: Scaling Foundation Models for Multimodal Video Understanding](../raw/InternVideo2/main.tex)
[^unitime-paper]: [Universal Video Temporal Grounding with Generative Multi-modal Large Language Models](../raw/UniTime/main.tex)
[^videoitg-paper]: [VideoITG: Multimodal Video Understanding with Instructed Temporal Grounding](../raw/VideoITG/main.tex)
[^neus-qa-paper]: [NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning](../raw/NeuS-QA/main.tex)
[^f2g-paper]: [Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding](../raw/Foresee-to-Ground/main.tex)
