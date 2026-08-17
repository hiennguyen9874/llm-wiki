---
type: Concept
title: "X-CLIP: multi-grained video-text retrieval"
description: A CLIP-initialized video-text retriever that combines video-sentence, video-word, sentence-frame, and frame-word similarities through attention-weighted aggregation.
tags: [video, language, retrieval, contrastive-learning, clip]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T11:49:06+07:00 }
sources:
  - id: xclip-paper
    resource: ../raw/2207.07285_X-CLIP/sample-base.tex
    title: "X-CLIP: End-to-End Multi-grained Contrastive Learning for Video-Text Retrieval"
---

# X-CLIP: multi-grained video-text retrieval

X-CLIP is an end-to-end video-text retrieval model that augments ordinary video-sentence contrast with video-word, sentence-frame, and frame-word comparisons. Its Attention Over Similarity Matrix (AOSM) module converts the resulting vectors and matrix into instance-level scores by emphasizing strongly matching frames and words rather than treating every element equally or retaining only one maximum.[^xclip-paper]

## Architecture

The visual path samples one frame per second, encodes each frame with a CLIP-initialized ViT, and applies a three-layer Transformer with temporal position embeddings. Mean pooling the temporally encoded frame features gives a video-level representation. The CLIP-initialized text Transformer supplies word-token features and an end-of-sequence sentence feature.[^xclip-paper]

For a video-text pair, X-CLIP computes four dot-product-based comparisons:

- **video-sentence:** one coarse-grained score;
- **video-word:** cross-grained similarities between the pooled video and every word;
- **sentence-frame:** cross-grained similarities between the sentence and every frame; and
- **frame-word:** a fine-grained frame-by-word similarity matrix.[^xclip-paper]

AOSM applies softmax weights to the video-word and sentence-frame vectors. For the frame-word matrix, it aggregates along each axis and then applies attention again to produce video-oriented and sentence-oriented scores, which it averages. The final retrieval score is the mean of all four granularity scores, and training uses symmetric batchwise InfoNCE for video-to-text and text-to-video retrieval.[^xclip-paper]

## Reported evidence

On the paper's MSR-VTT Training-9K protocol, the ViT-B/16 model reports text-to-video R@1 of 49.3 and video-to-text R@1 of 48.9. The paper also reports text-to-video R@1 of 50.4 on MSVD, 26.1 on LSMDC, 47.8 on DiDeMo, and 46.2 on ActivityNet.[^xclip-paper] These are source-reported, contemporaneous comparisons rather than a current model ranking.

The MSR-VTT ViT-B/32 ablations provide evidence for the model's components under one protocol:

- all four contrast types reach 46.1 text-to-video R@1 versus 43.0 for video-sentence contrast alone;
- AOSM reaches 46.1 R@1 versus 43.2-44.9 for the tested mean/max aggregation variants; and
- adding the temporal encoder raises text-to-video/video-to-text R@1 from 45.2/45.6 to 46.1/46.8.[^xclip-paper]

The appendix reports that frame-word-only contrast degrades more than the other single-granularity variants as the MSR-VTT training subset shrinks from 9K to 3K and 0.1K videos. This supports the narrower interpretation that fine-grained pairwise alignment is harder to optimize with little task data in this setup, not a general sample-complexity law.[^xclip-paper]

## Scope and evidence limits

X-CLIP ranks whole videos and texts; it does not return temporal boundaries or demonstrate reasoning about event order, duration, or causality. Its DiDeMo and ActivityNet evaluations concatenate a video's captions for video-paragraph retrieval rather than localizing individual captioned moments.[^xclip-paper]

The manuscript's visual-representation section defines temporally encoded frame features as the final fine-grained representation, and the architecture figure routes those features into similarity computation. However, the sentence-frame and frame-word equations use the symbol previously assigned to frame-encoder outputs. The source does not resolve whether this is only a notation error, so the exact implementation should be checked in the linked code before reproduction.[^xclip-paper]

The manuscript and six material figure attachments (contrast design, architecture, data-size ablation, Transformer alternative, and qualitative retrieval examples) were inspected. Four similarly named figure variants were not inspected; the claims above are grounded in the manuscript text, tables, and inspected figures.

## Relationships

- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) through CLIP-initialized frame/text encoders and a learned temporal encoder.[^xclip-paper]
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) only as video-text retrieval and alignment infrastructure; the source does not evaluate temporal grounding or reasoning.[^xclip-paper]

[^xclip-paper]: [X-CLIP: End-to-End Multi-grained Contrastive Learning for Video-Text Retrieval](../raw/2207.07285_X-CLIP/sample-base.tex)
