---
type: Concept
title: InternVideo2
description: A staged video foundation-model family that couples unmasked-token distillation, video–audio–speech–text alignment, and video-conditioned next-token prediction.
tags: [video, foundation-models, representation-learning, multimodal-learning, video-language]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:34:53+07:00 }
sources:
  - id: internvideo2-paper
    resource: ../raw/InternVideo2/main.tex
    title: "InternVideo2: Scaling Foundation Models for Multimodal Video Understanding"
  - id: lv-mae-paper
    resource: ../raw/LV-MAE/main.tex
    title: "LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders"
---

# InternVideo2

InternVideo2 is a video foundation-model family trained progressively: it distills spatiotemporal features into a video encoder, aligns video with audio, speech, and text, then connects the encoder to an LLM for video dialogue. The source reports benchmark results across recognition, retrieval, temporal localization and grounding, audio tasks, and video QA; these are evaluations of the stated models and protocols, not a general proof of video reasoning or a world model.[^internvideo2-paper]

## Progressive training

**Stage 1** trains a ViT video encoder from scratch by aligning its unmasked token representations with InternVL-6B and VideoMAEv2-g teacher features. The paper masks 80% of tokens frame by frame, aligns selected final teacher layers through learned projections, and drops those projections after pretraining. Its 6B example sparsely samples eight 224×224 frames with 14×14 patches and uses 48 Transformer layers; this configuration is architecture-specific.[^internvideo2-paper]

**Stage 2** adds a BEATs-initialized audio encoder plus BERT-Large-initialized text encoder and multimodal decoder. It applies contrastive alignment, cross-modal matching, and masked-language losses across image, video, audio, speech, and textual descriptions. The source separates masked alignment from a final unmasked post-pretraining phase that freezes the vision encoder.[^internvideo2-paper]

**Stage 3** uses a Q-Former-style interface to connect the video encoder to an open-source LLM for next-token prediction. In its high-definition post-training, the source updates the video encoder and Q-Former and uses LoRA for the LLM; it describes this as video dialogue tuning rather than a novel video-encoder architecture.[^internvideo2-paper]

## Data and evidence limits

The paper describes K-Mash$_{2M}$ as 2M unlabeled videos for stage 1 and lists 300M image–text entries, 50M InternVid2 video–audio–speech–text clips, and 2.1M instruction-tuning examples for later stages. It says InternVid2 clips are semantically segmented with AutoShot and receive independently generated video, audio, and speech captions that an LLM refines and fuses.[^internvideo2-paper]

Data governance cannot be independently assessed from this source: it identifies anonymous video sources, says a subset of Chinese data was collected with academic-use permission, and does not provide sufficient licensing, consent, or complete provenance detail for the whole corpus.[^internvideo2-paper]

## Reported transfer evidence

With its stage-1 backbone and ActionFormer head, the source reports average mAP of 72.0 on THUMOS14, 43.3 on HACS Segment, 41.2 on ActivityNet, and 27.7 on FineAction. This supports the specified pretrained-backbone/head combinations, not a claim that InternVideo2 itself is a temporal-localization head.[^internvideo2-paper]

For video-language temporal grounding, the paper reports finetuned InternVideo2-6B features with CG-DETR at 71.42 R1@0.5 and 56.45 R1@0.7 on QVHighlight, and 70.03 R1@0.5 with 58.79 mIoU on Charades-STA. These are direct grounding evaluations, but they do not establish long-context evidence access or general temporal reasoning.[^internvideo2-paper]

## Limits

The authors state that InternVideo2 relies on fixed input resolution, sampling rate, and compressed tokens, which limits fine-grained information capture. They also state that its leading benchmark results do not guarantee a consistent implicit world model for visual reasoning. Its claims of broad task coverage should therefore not be read as evidence of arbitrary-duration or reliable causal reasoning.[^internvideo2-paper]

## Relationships

- **Instantiates:** [Video temporal representation learning](video-temporal-representation-learning.md) through staged token distillation, multimodal alignment, and video-conditioned next-token prediction.[^internvideo2-paper]
- **Supports:** [Temporal action understanding](temporal-action-understanding.md) as a reported pretrained feature backbone paired with ActionFormer.[^internvideo2-paper]
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) through reported CG-DETR temporal-grounding evaluations; this is not general reasoning evidence.[^internvideo2-paper]
- **Uses:** [ActionFormer](actionformer.md) as the reported temporal-action-localization head.[^internvideo2-paper]
- **Uses:** [VideoMAE V2](videomae-v2.md) through VideoMAE V2-g as a motion-aware stage-1 teacher.[^internvideo2-paper]
- **Supports:** [LV-MAE](lv-mae.md) as one reported frozen short-video segment encoder; this downstream use does not evaluate InternVideo2's own long-context capacity.[^lv-mae-paper]

[^internvideo2-paper]: [InternVideo2: Scaling Foundation Models for Multimodal Video Understanding](../raw/InternVideo2/main.tex)
[^lv-mae-paper]: [LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders](../raw/LV-MAE/main.tex)
