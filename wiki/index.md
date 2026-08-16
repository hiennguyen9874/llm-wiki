---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [Boundary-Matching Network (BMN)](boundary-matching-network.md) — A class-agnostic temporal action proposal network that jointly predicts boundaries and a dense start-duration confidence map.
- [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md) — A two-stream action-recognition architecture that inflates pretrained 2D image ConvNets into spatiotemporal 3D ConvNets.
- [Long-video temporal modeling](long-video-temporal-modeling.md) — Scalable representations and retrieval mechanisms for preserving fine-grained events across long video contexts.
- [MS-TCN (Multi-Stage Temporal Convolutional Network)](ms-tcn.md) — A full-resolution frame-level action-segmentation network that sequentially refines temporal class probabilities with stacked dilated-convolution stages.
- [Multiscale Vision Transformers (MViT)](multiscale-vision-transformers-mvit.md) — A staged video and image Transformer that pools token resolution while expanding channel capacity through its hierarchy.
- [Non-local Neural Networks](non-local-neural-networks.md) — Neural-network blocks that directly aggregate pairwise feature relations across all spatial, temporal, or spacetime positions.
- [Production temporal video analytics](production-temporal-video-analytics.md) — Selecting temporal models after detection and tracking by event complexity, latency, compute, data, and explainability constraints.
- [R(2+1)D](r-2-plus-1-d.md) — A ResNet video architecture that factorizes each 3D convolution into spatial 2D and temporal 1D convolutions separated by a nonlinearity.
- [SlowFast Networks](slowfast-networks.md) — A two-pathway video architecture that assigns sparse semantic processing and dense lightweight motion processing to separate temporal rates.
- [TimeSformer](timesformer.md) — A video Transformer that factorizes temporal and spatial self-attention over frame patches to make long-clip action recognition practical.
- [Temporal action understanding](temporal-action-understanding.md) — Video tasks that recognize, localize, segment, or anticipate actions across time.
- [Temporal Segment Networks](temporal-segment-networks.md) — A video-level action-recognition framework that samples snippets across equal temporal segments and learns their consensus.
- [Two-stream ConvNets for action recognition](two-stream-convnets-action-recognition.md) — A late-fusion video classifier that separates appearance in RGB frames from motion in stacked optical flow.
- [Video Swin Transformer](video-swin-transformer.md) — A hierarchical video Transformer that uses alternating local and shifted 3D attention windows to model spacetime efficiently.
- [VideoMAE](videomae.md) — A self-supervised video-pretraining method that reconstructs heavily tube-masked video cubes with an asymmetric Vision Transformer autoencoder.
- [Video temporal learning](video-temporal-learning.md) — A task taxonomy for learning temporal structure in video, spanning recognition, localization, representation learning, language grounding, and reasoning.
- [Video temporal representation learning](video-temporal-representation-learning.md) — Pretraining video features to encode appearance, motion, order, dynamics, and longer-range semantics for downstream tasks.
- [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) — Text-conditioned localization and inference over event timing, order, duration, frequency, state changes, and causal relations in video.
- [ViViT (Video Vision Transformer)](vivit.md) — A family of pure-Transformer video classifiers that tokenizes video as frames or tubelets and offers four space–time attention designs.
