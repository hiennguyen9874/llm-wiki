---
type: Concept
title: InternVideo
description: A video foundation-model system that combines masked-video and video–text pretraining through supervised cross-model attention.
tags: [video, foundation-models, representation-learning, self-supervised-learning, video-language]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:21:31+07:00 }
sources:
  - id: internvideo-paper
    resource: ../raw/InternVideo/main.tex
    title: "InternVideo: General Video Foundation Models via Generative and Discriminative Learning"
---

# InternVideo

InternVideo is a video foundation-model system that separately learns a masked-video representation and a video–text representation, then uses supervised cross-model attention to coordinate them. The source evaluates it across action understanding, video–language alignment, and open-set settings; it is evidence for benchmark-scale transfer, not for arbitrary-duration or higher-order video reasoning.[^internvideo-paper]

## Representation design

The masked branch is a VideoMAE-style ViT trained with high-ratio tube masking and joint space–time attention. The multimodal branch adapts a CLIP-pretrained UniFormerV2: it contrastively aligns independently encoded video and text, then uses a caption decoder with cross-attention for multimodal fusion. The paper also co-trains image–text data during multimodal pretraining.[^internvideo-paper]

After separate pretraining and supervised action-classification post-training, cross-model attention modules exchange intermediate tokens between the two branches. The source freezes the backbones except stated classification/query components during this interaction stage and learns a weighted combination of branch prediction scores.[^internvideo-paper]

## Task evidence

The source reports 91.1% top-1 accuracy on Kinetics-400 for its three-model configuration. It also uses an InternVideo ViT-H feature backbone with existing temporal-action-localization heads: ActionFormer reports average mAP of 71.58 on THUMOS-14, 39.00 on ActivityNet-v1.3, and 17.57 on FineAction; TCANet reports 41.55 on HACS Segment.[^internvideo-paper]

For video–language tasks, the multimodal encoder is fine-tuned for retrieval and question answering. For example, the paper reports text-to-video/video-to-text R@1 of 55.2/57.9 on MSR-VTT and VQA top-1 accuracy of 47.1 on MSR-VTT.[^internvideo-paper] These are paper-specific, contemporaneous comparisons, not a current general ranking or evidence of temporal grounding.

## Scope and limits

The pretraining corpus combines public data with self-collected web video; the paper says it includes video, audio, and sometimes subtitles, but does not provide sufficient detail here to independently assess its provenance, licensing, or demographic coverage.[^internvideo-paper] Its authors state that the system operates on clips and cannot handle long-term video tasks or higher-order tasks such as predicting a film plot from an observed portion.[^internvideo-paper]

Four supplied figure PDFs could not be inspected with the available tools; claims above are grounded in the textual manuscript and tables. A duplicate copy of the same manuscript exists under a nested source directory and was not treated as separate evidence.

## Relationships

- **Instantiates:** [Video temporal representation learning](video-temporal-representation-learning.md) by coordinating masked-video and video–text representations.[^internvideo-paper]
- **Supports:** [Temporal action understanding](temporal-action-understanding.md) as a pretrained feature backbone used with existing action-recognition and localization heads.[^internvideo-paper]
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) with video–text retrieval and question-answering features, while not establishing temporal grounding or reasoning performance.[^internvideo-paper]
- **Uses:** [VideoMAE](videomae.md) as the masked-video training design for one branch.[^internvideo-paper]
- **Uses:** [ActionFormer](actionformer.md) as a temporal-action-localization head in the reported backbone evaluation.[^internvideo-paper]

[^internvideo-paper]: [InternVideo: General Video Foundation Models via Generative and Discriminative Learning](../raw/InternVideo/main.tex)
