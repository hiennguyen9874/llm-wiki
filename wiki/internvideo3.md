---
type: Concept
title: InternVideo3
description: A Qwen3-based multimodal model that combines closed-loop multimodal contextual reasoning, latent KV-cache compression, and staged long-video post-training.
tags: [video, multimodal-agents, long-context, video-language, temporal-reasoning]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:41:57+07:00 }
sources:
  - id: internvideo3-paper
    resource: ../raw/2606.12195_InternVideo3/main.tex
    title: "InternVideo3: Agentify Foundation Models with Multimodal Contextual Reasoning"
---

# InternVideo3

InternVideo3 adapts a Qwen3-based 7/8B multimodal backbone for long-video reasoning through three coupled elements: Multimodal Contextual Reasoning (MCR), Multimodal Multi-head Latent Attention (M²LA), and staged long-video training. The paper reports strong direct-QA and grounding results plus one preliminary agentic-inference gain, but it does not establish general multimodal agency: most evaluations are static benchmarks, agent demonstrations are qualitative, and tool failures can contaminate the shared context.[^internvideo3-paper]

## Multimodal Contextual Reasoning

MCR represents the query, visual observations, intermediate reasoning, actions, tool feedback, and memory in one evolving autoregressive context. Each step observes evidence, reasons, selects an action, receives feedback, and appends the resulting trace to the context; optional summarization or compression controls growth. Actions can request temporal or spatial re-perception, call ASR, segmentation, temporal grounding, or search, read or write memory, verify support, or terminate.[^internvideo3-paper]

This is a contextual belief-update abstraction rather than an action-conditioned environment simulator. Its ingredients—tool use, memory, reflection, and iterative evidence gathering—are not claimed as individually novel; the contribution is their video-oriented unified formulation and implementation.[^internvideo3-paper]

## M²LA context efficiency

M²LA converts GQA attention into a latent-cache form while retaining the multimodal token stream. It caches compact per-token latent states, reconstructs head- or group-specific content keys and values during attention, and retains a small position-aware RoPE key path. Modality-aware adapters accommodate different vision- and text-token distributions, while layer- and modality-dependent latent ranks expose a memory–fidelity trade-off.[^internvideo3-paper]

For Qwen3-style head-wise QK normalization, the conversion relies on an empirical approximation: concentrated high-dimensional RMS values make RMSNorm locally resemble constant linear scaling. A calibration pass learns a global norm-linear substitute before continued pretraining. This is a model- and calibration-dependent approximation, not a general proof that nonlinear normalization can always be replaced safely.[^internvideo3-paper]

On one H200, batch size 1, bf16, a 16K-token decode, and no external acceleration, the paper reports 39.96 versus 21.74 tokens/s after a 32K prefill and 4.77×/5.01× decode speedups after 256K/384K prefills. Its figure shows M²LA running through 768K prefill while the baseline is out of memory from 512K, and the text reports roughly 50% lower KV-cache use. These are source-specific systems measurements; the prose inconsistently describes the tested maximum as 512K even though the figure and caption include 640K and 768K.[^internvideo3-paper]

## Training and data

Training proceeds through continued pretraining after attention conversion, short-to-long supervised fine-tuning (SFT), rule-based group sequence policy optimization, and on-policy distillation from Qwen3-235B. The curriculum moves from up to 512 frames at 2 fps (about 32K tokens) to up to 2,048 frames at 4 fps (up to 256K tokens). Continued pretraining uses a reported 16M multimodal samples and 13.5B tokens; broader SFT uses about 7.2M samples.[^internvideo3-paper]

The long-video supervision component contains 379,629 videos with a reported mean duration of 15.8 minutes and about 100K total hours. Scene-aware clips receive teacher captions that are hierarchically merged into narratives, then support more than 1M synthesized QA pairs across perception, spatiotemporal understanding, event reasoning, and holistic semantics. RL retains 5K temporal-grounding examples with SFT-model IoU in `[0.1, 0.7]` and 10K multiple-choice questions whose sampled answers include both successes and failures. On-policy distillation selects student trajectories where a stronger teacher is correct or materially more complete.[^internvideo3-paper]

The source does not provide enough detail to independently assess licensing, consent, deduplication, or provenance for the complete mixture, including 115K YouTube-based reasoning videos and previously used instruction corpora. Dataset counts are therefore reported quantities, not an independent governance audit.[^internvideo3-paper]

## Reported evidence

Among the paper's listed open-weight systems, InternVideo3 reports 73.8 on Video-MME, 77.3 on MLVU, 69.4 on VRBench, and 76.6 on EgoSchema; it does not lead every listed task, scoring 27.6 versus Qwen3-VL-8B's 27.9 on VideoMME-v2 and 55.7 versus 58.0 on LVBench. It also reports direct temporal-grounding scores of 59.9 on QVHighlights, 50.4 on Charades-STA, and 47.9 on ActivityNet Captions under each benchmark's official metric.[^internvideo3-paper]

Ablations report a four-benchmark average of 66.8 for the full recipe, versus 64.7 without continued pretraining, 65.4 without long-context training, and 64.8 without curated long-video data. These ablations support complementarity within the paper's setup but do not isolate MCR, M²LA, data scale, and teacher effects across matched independent systems.[^internvideo3-paper]

The agentic Video-MME experiment reports 75.8 with MCR versus 73.1 for direct QA, while the main table reports 73.8 for InternVideo3. The source does not fully reconcile these configurations, and it says agentic inference did not consistently improve other benchmarks. The four supplied demos illustrate selected evidence and answers but provide no large-scale quantitative agent evaluation.[^internvideo3-paper]

## Limits

InternVideo3 is a video-centric step toward multimodal agents, not evidence of broad GUI, browser, mobile, embodied, or persistent multi-session agency. Its external ASR, retrieval, segmentation, grounding, and search tools are not jointly optimized; their errors can propagate through the shared context. M²LA is specifically a GQA-to-latent-attention conversion and may be less relevant to backbones with native latent, linear, or hierarchical compressed attention.[^internvideo3-paper]

## Relationships

- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) through latent KV-cache compression, a short-to-long context curriculum, hierarchical memory, and targeted evidence retrieval.[^internvideo3-paper]
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) through direct grounding evaluations and MCR's iterative evidence-selection loop.[^internvideo3-paper]
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) through a vision encoder connected to a Qwen3-based multimodal language backbone; InternVideo3 is an end-to-end MLLM system rather than a standalone video encoder.[^internvideo3-paper]

[^internvideo3-paper]: [InternVideo3: Agentify Foundation Models with Multimodal Contextual Reasoning](../raw/2606.12195_InternVideo3/main.tex)
