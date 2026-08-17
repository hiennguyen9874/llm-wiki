---
type: Synthesis
title: Temporal heads comparison
description: A task-aware comparison of temporal heads and adjacent query-conditioned systems for recognition, segmentation, proposals, localization, online detection, anticipation, and grounding.
tags: [video, temporal-modeling, temporal-head, comparison]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:47:55+07:00 }
sources:
  - id: tsn-paper
    resource: ../raw/TemporalSegmentNetworks/tsn_pami.tex
    title: Temporal Segment Networks for Action Recognition in Videos
  - id: ms-tcn-paper
    resource: ../raw/MS-TCN/egpaper_final.tex
    title: "MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation"
  - id: bmn-paper
    resource: ../raw/BMN/main.tex
    title: "BMN: Boundary-Matching Network for Temporal Action Proposal Generation"
  - id: actionformer-paper
    resource: ../raw/ActionFormer/main.tex
    title: "ActionFormer: Localizing Moments of Actions with Transformers"
  - id: futr-paper
    resource: ../raw/FutureTransformer/main.tex
    title: Future Transformer for Long-term Action Anticipation
  - id: mat-paper
    resource: ../raw/Memory-and-AnticipationTransformer/main.tex
    title: Memory-and-Anticipation Transformer for Online Action Understanding
  - id: unitime-paper
    resource: ../raw/UniTime/main.tex
    title: Universal Video Temporal Grounding with Generative Multi-modal Large Language Models
  - id: f2g-paper
    resource: ../raw/Foresee-to-Ground/main.tex
    title: "Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding"
  - id: videoitg-paper
    resource: ../raw/VideoITG/main.tex
    title: "VideoITG: Multimodal Video Understanding with Instructed Temporal Grounding"
  - id: neus-qa-paper
    resource: ../raw/NeuS-QA/main.tex
    title: "NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning"
  - id: production-overview
    resource: ../raw/TongQuanCacPhuongPhapTemporal.md
    title: Tổng quan các phương pháp temporal
  - id: detector-tracker-temporal
    resource: ../raw/DetectorTrackerTemporal.md
    title: Detector + Tracker + Temporal Transformer architectures
---

# Temporal heads comparison

**Synthesis:** a temporal head should be selected by its required output, not by a single benchmark ranking. In the strict, pipeline-oriented sense, a temporal head maps an ordered feature sequence from a video backbone, detector, or tracker to task outputs. Under that definition, MS-TCN, BMN, ActionFormer, FUTR, and MAT are the clearest task heads in this wiki; TSN is a video-level sampling-and-consensus framework. UniTime, F2G, VideoITG, and NeuS-QA are adjacent query-conditioned grounding or retrieval systems rather than interchangeable lightweight heads.

## Task-aware comparison

| Model or family | Input and native output | Temporal mechanism | Online? | Best fit | Main limitation |
| --- | --- | --- | --- | --- | --- |
| [TSN](temporal-segment-networks.md) | Sparse snippets → one video label | Equal-duration sampling plus score consensus | No: uses samples across the video | Fixed-cost trimmed or untrimmed classification | Can miss short unsampled events; no boundaries |
| Generic TCN | Per-timestep or per-track features → sequence/event labels | Parallel dilated 1D convolutions | Can be causal if designed so | Low-latency single-track behavior | Finite receptive field; production ranking is only qualitative[^production-overview] |
| [MS-TCN](ms-tcn.md) | Frame features → label per frame | Acausal dilated TCN plus multi-stage probability refinement | No, as published | Offline action segmentation and boundary-aware labels | Fully supervised; future-frame access; not direct interval detection |
| [BMN](boundary-matching-network.md) | Video feature sequence → class-agnostic candidate intervals | Start/end probabilities plus dense start-duration confidence map | No | High-recall proposals before a separate classifier | Proposal-only; dense interval map and external encoder/classifier |
| [ActionFormer](actionformer.md) | Clip-feature sequence → `(start, end, class)` | Local-attention temporal pyramid plus anchor-free classification/regression | No, as documented | Single-stage temporal action localization | Dense interval labels, fixed vocabulary, external features |
| [FUTR](future-transformer-futr.md) | Observed-prefix features → ordered future classes and durations | Global encoder attention plus parallel future queries | Predictive from past-only input | Long-term sequence anticipation | Global-attention scaling; fixed query budget; sampled external features |
| [MAT](memory-and-anticipation-transformer-mat.md) | Cached past features → current class and fixed-gap future class | Segmented memory compression plus latent-future interaction | Yes | Online current-action detection and short/fixed-gap anticipation | No start/end intervals; bounded lossy cache; external features |
| Per-track Transformer | One track `(B,T,F)` → behavior/event output | Self-attention over one object history | Can be causal | Longer single-object dependencies than a small TCN | More data/compute; cannot directly model interactions[^detector-tracker-temporal] |
| Multi-object Transformer | Object tokens `(B,T,N,F)` → interaction/event output | Temporal and cross-object attention | Possible, but expensive | Collision, fight, near-miss, group interaction | Attention grows sharply with frames and objects[^detector-tracker-temporal] |
| Scene temporal/video model | Frame or clip features → scene event | Whole-scene temporal encoding | Depends on design | Crowd, violence, global scene state | Highest cost and weak object attribution[^production-overview][^detector-tracker-temporal] |

## What each head actually solves

### Recognition and aggregation

[TSN](temporal-segment-networks.md) is appropriate when the output is one label for a whole video. Its fixed number of globally distributed snippets controls cost independently of duration, but sparse sampling sacrifices local event coverage. It is not a localizer: its multi-scale temporal-window integration still returns a video-level class.[^tsn-paper]

A generic LSTM/GRU, TCN, or Transformer can classify detector/tracker histories, but the wiki has no benchmark-controlled comparison among them. The production concepts only support a qualitative ordering: rules are cheapest and most explainable; TCNs are parallel and practical for single-track histories; Transformers justify their higher cost when longer dependencies or interactions matter.[^production-overview]

### Dense segmentation

[MS-TCN](ms-tcn.md) is the strongest fit when every timestep needs a label and over-segmentation is the principal error. Dilations preserve full resolution while expanding receptive field; later stages refine class probabilities, and the smoothing loss suppresses fragmented segments.[^ms-tcn-paper] It should not be treated as zero-look-ahead streaming evidence because the published convolutions are acausal.

### Proposals versus direct localization

[BMN](boundary-matching-network.md) and [ActionFormer](actionformer.md) both reason about intervals but produce different contracts:

- BMN returns class-agnostic proposals. It is useful when proposal recall and a separable downstream classifier are desired. The dense start-duration map evaluates interval content and context in parallel.[^bmn-paper]
- ActionFormer returns labeled intervals directly. Its anchor-free pyramid is simpler as an end task pipeline and handles multiple temporal scales without predefined windows.[^actionformer-paper]

Thus ActionFormer is the default among documented models for end-to-end *head-level* temporal action localization; BMN is preferable only when proposal generation must remain class-agnostic or modular. This is architectural synthesis, not a head-to-head benchmark conclusion.

### Anticipation and online detection

[FUTR](future-transformer-futr.md) predicts an ordered sequence of future action segments and durations in parallel. It is suited to long-term anticipation from a completed observed prefix, not current streaming detection. Its global access to sampled history helped in its reported ablation, but does not scale freely to arbitrary video duration.[^futr-paper]

[MAT](memory-and-anticipation-transformer-mat.md) is the documented choice for strict past-only inference: it classifies the current action and a selected future gap from cached features. Memory compression makes longer bounded history practical, but the result is a class at a timestep—not an interval—and compression is lossy.[^mat-paper]

## Query-conditioned temporal systems

These systems belong in the broader temporal stack but should not be equated with a small backbone head:

| System | Returned evidence/output | Distinguishing strength | Principal risk |
| --- | --- | --- | --- |
| [UniTime](unitime.md) | Query-matched start/end timestamps | Direct generative grounding with addressable timestamps and coarse-to-fine retrieval | Fixed token/clip budgets; generated boundary reliability |
| [F2G](foresee-to-ground.md) | Cited candidate span plus refined interval | Attributable intermediate span and compact Top-$K$ evidence pool | Candidate recall upper-bounds the final answer; single-primary-interval scope |
| [VideoITG](videoitg.md) | Top-ranked frames for a separate answering LLM | Instruction-conditioned evidence selection | Selection and answering are separate; unselected evidence is lost |
| [NeuS-QA](neus-qa.md) | Logic-satisfying interval for a VLM answer | Explicit temporal relations and model-checked retrieval | Verification is only as sound as proposition grounding; automaton construction is costly |

For natural-language moment localization, UniTime is the most direct timestamp-decoding framework in the wiki, while F2G is preferable when an attributable candidate hypothesis matters. VideoITG is a selector rather than a boundary head, and NeuS-QA is a reasoning/retrieval pipeline rather than a learned temporal decoder.[^unitime-paper][^f2g-paper][^videoitg-paper][^neus-qa-paper]

## Evidence-based selection

1. **One label per clip/video:** TSN-style sparse global aggregation when fixed cost matters; use an RGB video backbone instead when dense local motion is central.
2. **One label per frame:** MS-TCN for offline fully supervised segmentation; redesign with causal convolutions and measure delay for streaming.
3. **Unlabeled candidate intervals:** BMN.
4. **Labeled action intervals:** ActionFormer.
5. **Current action from past-only context:** MAT, or a causal generic TCN for a smaller per-track deployment baseline.
6. **Ordered future action sequence:** FUTR.
7. **Natural-language interval:** UniTime for direct timestamp generation; F2G when cited candidate evidence is required.
8. **Long-video QA evidence selection:** VideoITG for learned top-$k$ frame selection; NeuS-QA when explicit temporal logic and inspectability justify its cost.
9. **Object interactions:** do not run independent per-track heads and expect interactions to emerge; use pair/multi-object context or selective scene escalation.

## Evaluation discipline

No global accuracy ranking is supported. Reported results use different outputs and metrics—video accuracy, frame accuracy/F1/edit, proposal AR/AUC, localization mAP at temporal IoU thresholds, anticipation recall/accuracy, and grounding recall/mIoU. They also use different datasets, feature backbones, optical flow, sampling rates, and compute exclusions. A valid deployment comparison must hold the feature extractor, labels, window, hardware, and latency accounting fixed, then measure task-appropriate quality plus end-to-end p50/p95 latency and throughput.

The dedicated model pages are mostly stable and grounded in primary papers. The generic production-family recommendations remain draft because their sources provide qualitative guidance without controlled datasets, hardware, or measured throughput.[^production-overview][^detector-tracker-temporal]

## Relationships

- **Compares:** [Temporal Segment Networks](temporal-segment-networks.md), [MS-TCN](ms-tcn.md), [Boundary-Matching Network](boundary-matching-network.md), [ActionFormer](actionformer.md), [Future Transformer](future-transformer-futr.md), and [Memory-and-Anticipation Transformer](memory-and-anticipation-transformer-mat.md).
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) by mapping output granularity to task-specific heads.
- **Extends to:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) while distinguishing grounding/retrieval systems from strict feature-sequence heads.
- **Uses:** [Production temporal video analytics](production-temporal-video-analytics.md) for draft per-track, interaction, scene-scope, and deployment trade-offs.

[^tsn-paper]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
[^ms-tcn-paper]: [MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation](../raw/MS-TCN/egpaper_final.tex)
[^bmn-paper]: [BMN: Boundary-Matching Network for Temporal Action Proposal Generation](../raw/BMN/main.tex)
[^actionformer-paper]: [ActionFormer: Localizing Moments of Actions with Transformers](../raw/ActionFormer/main.tex)
[^futr-paper]: [Future Transformer for Long-term Action Anticipation](../raw/FutureTransformer/main.tex)
[^mat-paper]: [Memory-and-Anticipation Transformer for Online Action Understanding](../raw/Memory-and-AnticipationTransformer/main.tex)
[^unitime-paper]: [Universal Video Temporal Grounding with Generative Multi-modal Large Language Models](../raw/UniTime/main.tex)
[^f2g-paper]: [Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding](../raw/Foresee-to-Ground/main.tex)
[^videoitg-paper]: [VideoITG: Multimodal Video Understanding with Instructed Temporal Grounding](../raw/VideoITG/main.tex)
[^neus-qa-paper]: [NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning](../raw/NeuS-QA/main.tex)
[^production-overview]: [Tổng quan các phương pháp temporal](../raw/TongQuanCacPhuongPhapTemporal.md)
[^detector-tracker-temporal]: [Detector + Tracker + Temporal Transformer architectures](../raw/DetectorTrackerTemporal.md)
