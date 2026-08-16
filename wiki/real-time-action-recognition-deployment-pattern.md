---
type: Synthesis
title: Real-time action-recognition deployment pattern
description: A draft hybrid design that prioritizes tracked-object temporal signals and rules, escalating to clip-level video inference only when needed.
tags: [video-analytics, action-recognition, realtime, deployment]
status: draft
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:55:27+07:00 }
sources:
  - id: temporal-video-analytics-overview
    resource: ../raw/TongQuanCacPhuongPhapTemporal.md
    title: Tổng quan các phương pháp temporal
  - id: detector-tracker-temporal
    resource: ../raw/DetectorTrackerTemporal.md
    title: Detector + Tracker + Temporal Transformer architectures
  - id: ms-tcn-paper
    resource: ../raw/MS-TCN/egpaper_final.tex
    title: MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation
  - id: mat-paper
    resource: ../raw/Memory-and-AnticipationTransformer/main.tex
    title: Memory-and-Anticipation Transformer for Online Action Understanding
---

# Real-time action-recognition deployment pattern

**Synthesis:** for many multi-camera, real-time event systems, use detector and tracker outputs as the primary temporal signal; classify each track with a small temporal model and verify explicit conditions with rules. Escalate only ambiguous or high-risk windows to a clip-level video model. This follows the qualitative production guidance, not a measured throughput or accuracy comparison.[^temporal-video-analytics-overview][^detector-tracker-temporal]

## Recommended hybrid pipeline

1. **Detect and track** people, vehicles, or task-specific objects; retain a fixed recent history per track.
2. **Rules first** for explicit, observable events (zones, direction, dwell time, PPE, counts, or distance thresholds). This path is inexpensive and auditable.[^temporal-video-analytics-overview]
3. **Per-track temporal classifier** for behaviors whose evidence is motion over time (for example, falls, loitering, or running). A TCN is the default candidate because the production source characterizes dilated convolutions as parallel and real-time-friendly; it has finite receptive field.[^temporal-video-analytics-overview]
4. **Temporal decision layer:** apply confidence persistence, hysteresis, and rule verification before emitting an alert. This is an engineering recommendation, not a claim evaluated by the cited papers.
5. **Selective escalation:** send only uncertain, interacting, or scene-level candidate windows to a clip-level RGB model or a broader temporal model. This preserves expensive video inference for cases where a per-track history cannot represent the event.[^detector-tracker-temporal]

A deployment must make the temporal classifier causal or tolerate an explicit look-ahead delay. The cited MS-TCN implementation is acausal and is therefore not direct evidence for zero-look-ahead streaming; it is evidence for dilated-convolution segmentation and refinement only.[^ms-tcn-paper]

## Select the temporal branch by event scope

| Event scope | Primary branch | Escalation or complement |
| --- | --- | --- |
| Explicit compliance or traffic condition | Detector + tracker + rules | Human review or clip evidence for disputed cases |
| One subject's evolving behavior | Per-track features + causal TCN | Bounded-memory temporal encoder if long history is material |
| Two or more objects interacting | Candidate-pair features + rules as a low-cost filter | Multi-object temporal model on selected windows |
| Crowd or whole-scene event | Scene features or clip-level video model | Use detector/tracker output for attribution where possible |

Per-track histories cannot directly model interactions, while flattened multi-object attention grows rapidly with the number of frames and objects.[^detector-tracker-temporal] Consequently, candidate filtering before a multi-object branch is a practical synthesis rather than a reported benchmark result.

## Bounded history and motion inputs

For a history-dependent online classifier, MAT is relevant because it predicts using cached past features and compresses historical segments; it does not establish end-to-end streaming throughput, and its source identifies feature extraction and optical-flow calculation as pipeline bottlenecks.[^mat-paper] Avoid making dense optical flow a mandatory always-on dependency unless its incremental accuracy is measured against its cost in the target environment.

## Validation gate

Before calling the design realtime, measure end-to-end rather than model-only latency: decode, detection, tracking, feature construction, temporal inference, alert persistence, and queueing. Report p50/p95 latency, sustained FPS per stream, streams per device, recall/precision and false alarms by event class, and behavior under crowding, occlusion, and tracker ID switches. These are deployment acceptance criteria proposed by this synthesis; the cited production sources do not provide them.

## Relationships

- **Applies:** [Production temporal video analytics](production-temporal-video-analytics.md) as a concrete deployment synthesis.
- **Uses:** [Temporal action understanding](temporal-action-understanding.md) to distinguish online detection, segmentation, and interval localization requirements.
- **Uses:** [MS-TCN (Multi-Stage Temporal Convolutional Network)](ms-tcn.md) as evidence for dilated temporal convolution, with an explicit causal-streaming limitation.
- **Uses:** [Memory-and-Anticipation Transformer (MAT)](memory-and-anticipation-transformer-mat.md) as a bounded-history option when per-track context must extend beyond a short window.

## Evidence limits

The production sources are qualitative and lack hardware, dataset, latency, throughput, and calibrated-accuracy measurements. This page therefore recommends an architecture to benchmark, not a proven real-time configuration or a universal model ranking.

[^temporal-video-analytics-overview]: [Tổng quan các phương pháp temporal](../raw/TongQuanCacPhuongPhapTemporal.md)
[^detector-tracker-temporal]: [Detector + Tracker + Temporal Transformer architectures](../raw/DetectorTrackerTemporal.md)
[^ms-tcn-paper]: [MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation](../raw/MS-TCN/egpaper_final.tex)
[^mat-paper]: [Memory-and-Anticipation Transformer for Online Action Understanding](../raw/Memory-and-AnticipationTransformer/main.tex)
