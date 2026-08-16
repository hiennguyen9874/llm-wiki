---
type: Concept
title: Boundary-Matching Network (BMN)
description: A class-agnostic temporal action proposal network that jointly predicts boundaries and a dense start-duration confidence map.
tags: [video, temporal-action-proposals, temporal-localization, boundary-matching]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T09:44:11+07:00 }
sources:
  - id: bmn-paper
    resource: ../raw/BMN/main.tex
    title: BMN: Boundary-Matching Network for Temporal Action Proposal Generation
---

# Boundary-Matching Network (BMN)

Boundary-Matching Network (BMN) generates class-agnostic temporal action proposals from an untrimmed video’s feature sequence. It jointly predicts likely start/end boundaries and a dense proposal-confidence map indexed by start time and duration, then combines those signals to rank proposals.[^bmn-paper]

## Boundary-matching mechanism

A proposal is represented by a start boundary and duration; each cell in the Boundary-Matching (BM) confidence map therefore scores one proposal. Cells whose implied end boundary is outside the video are excluded.[^bmn-paper]

The BM layer creates a feature for every valid proposal in parallel. It uniformly samples 32 points over an expanded interval from $t_s - 0.25d$ to $t_e + 0.25d$, using linear interpolation for fractional positions, then applies pre-generated sampling masks to the temporal feature sequence by a dot product. This yields proposal features with internal and surrounding temporal context without independently constructing a feature for each candidate.[^bmn-paper]

## Network and training

A shared two-layer 1D-convolution base feeds two branches:

- The **Temporal Evaluation Module (TEM)** predicts a start-probability sequence and an end-probability sequence.
- The **Proposal Evaluation Module (PEM)** applies the BM layer, then 3D and 2D convolutions to produce classification and regression confidence maps over duration and start time.[^bmn-paper]

TEM is supervised by overlap between each temporal location and ground-truth start/end regions. Each PEM cell is labeled with the maximum temporal IoU of its proposal against ground-truth instances; its classification and regression maps use weighted binary logistic and L2 losses, respectively. The paper trains these objectives jointly as a multi-task model.[^bmn-paper]

## Proposal scoring

At inference, BMN selects high-probability or local-peak start and end locations, pairs them subject to a maximum duration, and obtains the two PEM scores at each proposal’s map cell. Its final score multiplies start and end probabilities by the geometric mean of the two PEM scores, followed by Soft-NMS (or, in comparison experiments, greedy NMS).[^bmn-paper]

## Reported results and limits

On ActivityNet-1.3 validation, the jointly trained model reported AR@100 of 75.01 and AUC of 67.10; the paper’s separately trained BMN configuration took 0.069 s and its jointly trained configuration 0.052 s per 3-minute video on an Nvidia 1080 Ti, compared with 0.629 s for its separately trained BSN baseline. These are paper-specific measurements with the stated features, dataset setup, and hardware—not current general performance guarantees.[^bmn-paper]

The model is proposal-only: action category assignment is supplied separately when the paper evaluates temporal action detection. Its feature encoder is also external to BMN; the reported implementation uses two-stream features, with C3D used in some THUMOS-14 comparisons.[^bmn-paper]

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for class-agnostic interval proposal generation before action classification.
- **Uses:** [Two-stream ConvNets for action recognition](two-stream-convnets-action-recognition.md) as one reported external feature encoder.

[^bmn-paper]: [BMN: Boundary-Matching Network for Temporal Action Proposal Generation](../raw/BMN/main.tex)
