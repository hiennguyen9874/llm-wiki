---
type: Concept
title: Long-video temporal modeling
description: Scalable representations and retrieval mechanisms for preserving fine-grained events across long video contexts.
tags: [video, long-context, temporal-learning, efficiency]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-17T11:58:42+07:00 }
sources:
  - id: vivit-paper
    resource: ../raw/ViViT/main_arxiv.tex
    title: "ViViT: A Video Vision Transformer"
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
  - id: temporal-segment-networks
    resource: ../raw/TemporalSegmentNetworks/tsn_pami.tex
    title: Temporal Segment Networks for Action Recognition in Videos
  - id: timesformer-paper
    resource: ../raw/TimeSformer/TimeSformer_arxiv_v17.tex
    title: Is Space-Time Attention All You Need for Video Understanding?
  - id: mvit-paper
    resource: ../raw/MViT/mvit_arxiv.tex
    title: Multiscale Vision Transformers
  - id: video-swin-paper
    resource: ../raw/VideoSwin/main.tex
    title: Video Swin Transformer
  - id: actionformer-paper
    resource: ../raw/ActionFormer/main.tex
    title: "ActionFormer: Localizing Moments of Actions with Transformers"
  - id: futr-paper
    resource: ../raw/FutureTransformer/main.tex
    title: Future Transformer for Long-term Action Anticipation
  - id: mat-paper
    resource: ../raw/Memory-and-AnticipationTransformer/main.tex
    title: Memory-and-Anticipation Transformer for Online Action Understanding
  - id: lv-mae-paper
    resource: ../raw/LV-MAE/main.tex
    title: "LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders"
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
  - id: videoprism-paper
    resource: ../raw/2402.13217_VideoPrism/main.tex
    title: "VideoPrism: A Foundational Visual Encoder for Video Understanding"
  - id: vjepa2-paper
    resource: ../raw/2506.09985_V-JEPA 2/main.tex
    title: "V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning"
---

# Long-video temporal modeling

Long-video understanding cannot generally send every frame and visual token to global attention: context length and quadratic attention cost make this impractical. The source therefore emphasizes temporal compression, hierarchy, memory, and query-guided sampling.[^video-temporal-survey]

## Core strategies

- **Hierarchical modeling:** aggregate frames into clips, events, scenes, and video-level representations.
- **Temporal compression:** replace dense frame tokens with progressively coarser clip or event tokens.
- **Memory:** update a persistent state as new video segments arrive.
- **Query-guided retrieval or sampling:** select frames or segments conditional on a question rather than sampling uniformly.
- **Efficient temporal computation:** use sparse sampling, token pruning, local attention, adaptive resolution, or dynamic allocation of compute.

The common trade-off is retaining precise, short-lived events while modeling dependencies over minutes or hours.[^video-temporal-survey]

## Global attention over an observed prefix

FUTR provides task-specific evidence that full attention can be useful after temporal sampling and feature extraction: its encoder self-attends over sampled observed-frame features, while its decoder cross-attends to all encoder outputs and self-attends over a fixed sequence of future-action queries.[^futr-paper] On Breakfast, restricting decoder cross-attention to the most recent 25% of observed features rather than all of them reduced reported mean-over-classes accuracy by 2.0–3.3 points across the tested observation and prediction ratios.[^futr-paper]

This does not overturn the general scaling constraint: FUTR's experiments use pre-extracted I3D features on finite benchmark videos, and its authors identify the computation and memory of attention as a limitation. It is evidence for exploiting the whole available prefix at that scale, not for arbitrary-duration global attention.[^futr-paper]

## Segmented online memory compression

MAT provides a bounded-cache alternative for online action understanding. It splits the cached feature history into long- and short-term regions, runs shared learned queries over non-overlapping long-memory segments, pools each segment into a token, and lets recent short-memory tokens cross-attend to those compressed tokens. Its subsequent circular decoder exchanges the enhanced short-memory representation with learned latent future features; it does not retain the full history as decoder tokens.[^mat-paper]

This is evidence for lossy compression of a fixed experimental memory cache, not persistent state or arbitrary-duration retrieval. The reported model also consumes pre-extracted features, so it does not establish end-to-end long-video throughput.[^mat-paper]

## Fixed-budget global sampling

Temporal Segment Networks provide a concrete sparse-sampling alternative: divide a video into equal temporal segments, sample one short snippet from each, and aggregate shared-encoder predictions. With a fixed segment count, compute is independent of video duration while samples remain distributed over the whole video.[^temporal-segment-networks] The trade-off is that unsampled short events can be missed; this is a classification-oriented design rather than a complete event-preservation mechanism.

## Factorized long-clip attention

TimeSformer provides a concrete attention-based alternative: it splits attention into temporal interactions at each patch location followed by spatial interactions within each frame. This changes per-patch comparisons from joint attention's $NF + 1$ to $N + F + 2$, where $N$ is patches per frame and $F$ is frames.[^timesformer-paper] In its long configuration, the source processes 96 frames spanning 102.4 seconds per clip and averages multiple non-overlapping clip predictions to cover each multi-minute HowTo100M video.[^timesformer-paper] Factorization makes longer clips feasible; it does not make full-video global attention or lossless event preservation free.

## Factorised encoder for longer clips

ViViT offers a different factorization: it first reduces the patches at each temporal index with a spatial Transformer, then applies a temporal Transformer only to those per-index representations.[^vivit-paper] In the paper's Kinetics-400 ablation, its ViViT-L/16x2 factorised encoder processed 128 frames sampled at stride 2—enough to cover the dataset's 250-frame, 10-second video with one view—and the source reports its highest accuracy for that configuration.[^vivit-paper] The same paper explicitly limits this evidence to clip-level classification; it does not demonstrate retention or retrieval across arbitrary-length video.

## Multiscale token hierarchy

MViT provides a fixed-clip hierarchical alternative: it pools queries at stage boundaries to shorten the output token sequence, pools keys and values to reduce attention cost, and increases channel width as spatiotemporal resolution falls.[^mvit-paper] This is a concrete token-compression mechanism, but the source evaluates 16–64-frame clips rather than arbitrary-duration video; it does not provide persistent memory or retrieval over a full long video.[^mvit-paper]

## Local spatiotemporal windows

Video Swin Transformer uses joint self-attention inside fixed-size 3D windows and shifts the window grid across successive blocks. Its Kinetics-400 ablation found that an $8 \times 7 \times 7$ temporal-spatial window incurred 88 GFLOPs versus 106 GFLOPs for a temporally global $16 \times 7 \times 7$ window, with a 0.3-point top-1 reduction for the reported Swin-T configuration.[^video-swin-paper] This is a local-attention speed--accuracy trade-off for fixed clips; it neither supplies persistent memory nor demonstrates retrieval over an arbitrary-duration video.

## Local temporal windows with a pyramid

For interval-level temporal action localization, ActionFormer combines local self-attention with a temporal feature pyramid. Its fixed-size window therefore covers a progressively wider temporal span at coarser levels; the paper gives a window of 19 at a 16×-downsampled level as covering 304 feature-grid steps. On THUMOS14, its ablation reports the same 66.8% average mAP for window size 19 as full attention, while reporting 45.3 versus 57.8 GMACs for a 2,304-step input. This is task- and implementation-specific evidence, not a general long-video guarantee.[^actionformer-paper]

## Short-clip foundation encoders

VideoPrism directly samples eight frames during pretraining and normally 16 during evaluation. Its paper explicitly identifies long-video understanding as unresolved and suggests using the encoder as a component in a larger long-video system. Broad short-clip transfer and an ActivityNet result with an external G-TAD head therefore do not establish persistent memory, full-context retrieval, or arbitrary-duration evidence retention.[^videoprism-paper]

## Progressive training for longer clips

V-JEPA 2 limits the expensive 64-frame, high-resolution regime to a final learning-rate cooldown after most training uses 16-frame 256×256 clips. The paper reports an 8.4× GPU-time reduction versus training its 64-frame 384×384 model at full resolution throughout, plus frozen-probe gains from longer training and evaluation clips. This is efficient bounded-clip scaling: direct context remains about 16 seconds, and the source reports no further understanding-task gains when pretraining with 128 or 256 frames.[^vjepa2-paper]

Its action-conditioned world model also rolls latent states forward autoregressively, but the authors report increasing prediction error and action-search cost with horizon. Evaluated robot planning consequently uses horizon one and manually scheduled image subgoals for pick-and-place, rather than solving long-horizon planning in one rollout.[^vjepa2-paper]

## Clip-token masked reconstruction

LV-MAE is a hierarchical temporal-compression strategy: a frozen short-video encoder produces one embedding per five-second segment, then a masked autoencoder models the segment sequence. Its reported implementation caps sequences at 256 clip tokens (about 21 minutes 20 seconds at that segment length), so its claim of scalable long-video processing is not evidence of arbitrary-duration global attention.[^lv-mae-paper]

## Coarse-to-fine timestamp retrieval

UniTime uses a generative MLLM to select free-text timestamps interleaved with frame or segment tokens. It scales each frame's token budget with video length, splits over-limit videos into clips, retrieves coarse segments, and refines boundaries within selected regions. This is a query-guided, fixed-budget retrieval strategy: it can recurse over candidate segments but does not retain or attend over the complete long-video token sequence at once.[^unitime-paper]

## Instruction-conditioned frame selection

VideoITG uses an instruction-conditioned selector to score up to 512 candidate frames and send the top-ranked frames to a separate answering Video-LLM. Its VidThinker training annotations first retrieve relevant five-second clips, then use instruction-type-specific frame sampling; semantic cues use diversity selection, motion cues fixed-rate sampling, joint cues a hybrid, and open-ended prompts sparse whole-video coverage.[^videoitg-paper]

This is a fixed-budget retrieval-and-selection strategy. The source reports improved benchmark scores over uniform sampling, but it does not establish lossless preservation of unselected events or unrestricted global attention over arbitrary-duration video.[^videoitg-paper]

## Video-wide candidate-span evidence

Foresee-to-Ground (F2G) first produces dense query-agnostic interval proposals from pooled temporal features, then retains a ranked Top-$K$ pool of candidate event spans. Each candidate has a coarse interval and fixed-length segment-local evidence tokens, allowing a grounding LLM to select from a compact video-wide hypothesis set rather than directly decode times from a flattened visual stream.[^f2g-paper]

This is a fixed-budget proposal-and-refinement mechanism, not lossless global attention or a guarantee that every event survives the pool. The source reports that candidate-pool coverage limits final grounding accuracy and notes a redundancy--coverage trade-off under a fixed $K$.[^f2g-paper]

## Logic-verified interval retrieval

NeuS-QA uses a query-conditioned alternative to uniform sampling: it retains a video interval only after a temporal-logic specification over VLM-detected events is satisfied by a frame-based automaton, then extends that interval for answer context. This constrains the answering VLM's input but does not remove the fixed cost of constructing the automaton or guarantee retention when the detector misses an event.[^neus-qa-paper]

## Architectural alternatives

The source identifies local/hierarchical attention and state-space models as alternatives to full global attention. It motivates state-space approaches by approximately linear sequence scaling, but does not provide verified comparative evidence that they are preferable for a particular video task.[^video-temporal-survey]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md).
- **Supports:** [Video temporal representation learning](video-temporal-representation-learning.md).
- **Uses:** [Temporal Segment Networks](temporal-segment-networks.md) as a fixed-budget sparse-sampling approach.
- **Uses:** [TimeSformer](timesformer.md) as a factorized-attention approach that expands clip-level temporal coverage.
- **Uses:** [ViViT (Video Vision Transformer)](vivit.md) as a spatial-then-temporal encoder that increases practical clip length.
- **Uses:** [Multiscale Vision Transformers (MViT)](multiscale-vision-transformers-mvit.md) as fixed-clip hierarchical token compression, not as arbitrary-length-video memory.[^mvit-paper]
- **Uses:** [Video Swin Transformer](video-swin-transformer.md) as local joint spatiotemporal attention with shifted cross-window connections, not as arbitrary-length-video memory.[^video-swin-paper]
- **Uses:** [ActionFormer](actionformer.md) as local temporal attention plus a feature pyramid for interval-level temporal action localization.[^actionformer-paper]
- **Uses:** [Future Transformer (FUTR)](future-transformer-futr.md) as global attention over sampled observed features for benchmark-scale long-term action anticipation, with explicit attention-scaling limits.[^futr-paper]
- **Uses:** [Memory-and-Anticipation Transformer (MAT)](memory-and-anticipation-transformer-mat.md) as segment-based, bounded-cache compression for online detection and anticipation, not as arbitrary-duration memory.[^mat-paper]
- **Uses:** [LV-MAE](lv-mae.md) as clip-token compression followed by masked reconstruction across a bounded long-video sequence.[^lv-mae-paper]
- **Uses:** [UniTime](unitime.md) as adaptive token allocation and hierarchical timestamp-conditioned retrieval for text queries, not as arbitrary-duration global memory.[^unitime-paper]
- **Uses:** [VideoITG](videoitg.md) as instruction-conditioned scoring and top-$k$ selection from a fixed frame budget for a separate answering Video-LLM, not as arbitrary-duration global memory.[^videoitg-paper]
- **Uses:** [NeuS-QA](neus-qa.md) as temporal-logic-constrained interval retrieval before VLM answering; automaton construction remains a VLM-grounding and compute bottleneck.[^neus-qa-paper]
- **Uses:** [Foresee-to-Ground (F2G)](foresee-to-ground.md) as a ranked Top-$K$ candidate-span pool with segment evidence before LLM boundary refinement; this does not guarantee arbitrary-duration coverage.[^f2g-paper]
- **Supports:** [VideoPrism](videoprism.md) when its frozen short-clip features are embedded in a separate long-video mechanism; VideoPrism itself supplies no such mechanism.[^videoprism-paper]
- **Supports:** [V-JEPA 2](v-jepa-2.md) beyond its bounded 64-frame context and short-horizon latent rollout; progressive-resolution training reduces cost but supplies no persistent memory.[^vjepa2-paper]

[^vivit-paper]: [ViViT: A Video Vision Transformer](../raw/ViViT/main_arxiv.tex)
[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^temporal-segment-networks]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
[^timesformer-paper]: [Is Space-Time Attention All You Need for Video Understanding?](../raw/TimeSformer/TimeSformer_arxiv_v17.tex)
[^mvit-paper]: [Multiscale Vision Transformers](../raw/MViT/mvit_arxiv.tex)
[^video-swin-paper]: [Video Swin Transformer](../raw/VideoSwin/main.tex)
[^actionformer-paper]: [ActionFormer: Localizing Moments of Actions with Transformers](../raw/ActionFormer/main.tex)
[^futr-paper]: [Future Transformer for Long-term Action Anticipation](../raw/FutureTransformer/main.tex)
[^mat-paper]: [Memory-and-Anticipation Transformer for Online Action Understanding](../raw/Memory-and-AnticipationTransformer/main.tex)
[^lv-mae-paper]: [LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders](../raw/LV-MAE/main.tex)
[^unitime-paper]: [Universal Video Temporal Grounding with Generative Multi-modal Large Language Models](../raw/UniTime/main.tex)
[^videoitg-paper]: [VideoITG: Multimodal Video Understanding with Instructed Temporal Grounding](../raw/VideoITG/main.tex)
[^neus-qa-paper]: [NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning](../raw/NeuS-QA/main.tex)
[^f2g-paper]: [Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding](../raw/Foresee-to-Ground/main.tex)
[^videoprism-paper]: [VideoPrism: A Foundational Visual Encoder for Video Understanding](../raw/2402.13217_VideoPrism/main.tex)
[^vjepa2-paper]: [V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning](../raw/2506.09985_V-JEPA%202/main.tex)
