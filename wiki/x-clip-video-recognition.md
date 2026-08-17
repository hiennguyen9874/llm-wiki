---
type: Concept
title: "X-CLIP: CLIP adaptation for video recognition"
description: A language-image-model adaptation for video classification that adds message-token cross-frame attention, temporal integration, and video-conditioned text prompting.
tags: [video, action-recognition, clip, transformers, prompting]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T11:53:40+07:00 }
sources:
  - id: xclip-recognition-paper
    resource: ../raw/2208.02816_X-CLIP/main.tex
    title: Expanding Language-Image Pretrained Models for General Video Recognition
---

# X-CLIP: CLIP adaptation for video recognition

X-CLIP adapts a pretrained language-image model to clip-level video classification rather than pretraining a video-text model from scratch. It preserves much of the image encoder's frame-wise structure while adding lightweight communication across frames, integrates frame representations into a video representation, and conditions class-text embeddings on each video's visual content. The paper evaluates fully supervised, few-shot, and zero-shot action recognition.[^xclip-recognition-paper]

## Architecture

The video encoder has two stages:

1. **Cross-frame communication transformer (CCT):** each frame retains its class and patch tokens. At every block, a projected frame class token becomes a temporary message token. Cross-frame fusion attention exchanges information among the frames' message tokens; intra-frame diffusion attention then lets each fused message interact with its own frame tokens. The message is discarded before the block's feed-forward network and regenerated at the next block.[^xclip-recognition-paper]
2. **Multi-frame integration transformer (MIT):** a shallow temporal Transformer processes the final frame-level class representations with temporal position embeddings; average pooling yields the video representation. X-CLIP uses a one-layer MIT for its CLIP variants.[^xclip-recognition-paper]

The intra-frame attention inherits pretrained image-encoder weights, while cross-frame fusion and MIT are randomly initialized. This preserves the pretrained encoder's per-frame token pattern while introducing temporal exchange through only one message token per frame.[^xclip-recognition-paper]

## Video-specific text prompting

The pretrained text encoder initially embeds bare category labels. A two-block prompting module uses each class embedding as a query over temporally averaged visual patch features, producing a video-conditioned prompt that is residually added to the original class embedding with a learned scale initialized to 0.1. Classification uses cosine similarity between the video representation and these instance-conditioned class representations.[^xclip-recognition-paper]

This mechanism differs from selecting or learning one global prompt template: the textual class representation varies with the candidate video. In the paper's X-CLIP-B/16 ablation, video-specific prompting reported 70.0% zero-shot accuracy versus 63.9% for a 16-template ensemble and 63.2% for learned prompt vectors under the stated protocol.[^xclip-recognition-paper]

## Reported evidence

Under the paper's protocols:

- X-CLIP-L/14 with 8 frames reported 87.1% Kinetics-400 top-1 accuracy at 658 GFLOPs per view and 88.3% Kinetics-600 top-1.[^xclip-recognition-paper]
- X-CLIP-B/16 reported zero-shot top-1 of 44.6% on HMDB-51, 72.0% on UCF-101, and 65.2% on the sampled unseen-class Kinetics-600 protocol after Kinetics-400 training.[^xclip-recognition-paper]
- With two labeled examples per class, X-CLIP-B/16 reported 53.0% on HMDB-51 and 76.4% on UCF-101. These comparisons benefit from CLIP's 400M image-text pretraining and are not controlled solely for architecture.[^xclip-recognition-paper]
- In a Kinetics-400 component ablation, CLIP-Mean scored 80.0%; cross-frame communication raised this to 81.2%, MIT to 81.7%, and video-specific prompting to 82.3%. Four-by-three-view inference then reached 83.8%, so the final increment is an inference-cost trade-off rather than an architectural gain.[^xclip-recognition-paper]

The supplementary comparisons narrow the architectural evidence: X-CLIP scored 82.3% fully supervised versus 82.1% for joint spacetime attention while using 145 versus 184 GFLOPs, and it had a larger advantage in the paper's two-shot HMDB-51 setting (50.8% versus 41.3%). A from-scratch single-modality experiment also reported 47.8% versus 45.3% for frame averaging, indicating that the temporal architecture's measured gain was not entirely dependent on language-image pretraining in that setup.[^xclip-recognition-paper]

## Scope and evidence limits

This X-CLIP is Ni et al.'s video-recognition model and is distinct from the similarly named [X-CLIP video-text retrieval model](x-clip-video-text-retrieval.md) by Ma et al. It predicts one class for a sampled clip or video; it does not output temporal boundaries, frame-level segments, or future actions. Its zero-shot claims also require supervised Kinetics-400 adaptation before evaluation on unseen target classes, so they are cross-dataset zero-shot recognition rather than training-free CLIP inference.[^xclip-recognition-paper]

Results are source-reported, protocol-specific comparisons from the 2022 paper, not a current model ranking. The manuscript, all eleven imported table files, and all four figure PDFs were inspected.

## Relationships

- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) by adapting pretrained language-image encoders with cross-frame message passing and temporal integration.[^xclip-recognition-paper]
- **Supports:** [Temporal action understanding](temporal-action-understanding.md) specifically at clip-level action recognition, including fully supervised, few-shot, and cross-dataset zero-shot settings.[^xclip-recognition-paper]
- **Distinct from:** [X-CLIP: multi-grained video-text retrieval](x-clip-video-text-retrieval.md), which ranks video-text pairs rather than classifying action labels.[^xclip-recognition-paper]

[^xclip-recognition-paper]: [Expanding Language-Image Pretrained Models for General Video Recognition](../raw/2208.02816_X-CLIP/main.tex)
