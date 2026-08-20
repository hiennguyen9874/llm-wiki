---
type: Concept
title: DFlash 2 parallel selection and local convolution
description: DFlash 2 retains one-pass parallel drafting while selecting a coherent path through per-position candidates and adding block-local dynamic convolution to reduce late-position proposal decay.
tags: [speculative-decoding, dflash, parallel-drafting, convolution, inference]
status: stable
created: 2026-08-20
generated: { by: llm-wiki-agent/1, at: 2026-08-20T08:49:07Z }
sources:
  - id: inco-dflash2-2026
    resource: ../raw/DFlash2.md
    title: "DFlash 2: Keep Drafting Parallel"
---

# DFlash 2 parallel selection and local convolution

DFlash 2 extends DFlash’s parallel block drafting without an additional backbone or LM-head pass. It retains a small candidate list at every draft position, scores adjacent candidate pairs to choose a locally coherent path, and inserts a content-adaptive two-tap convolution around drafter sublayers to carry short-range within-block information.[^inco-dflash2-2026]

## Parallel path selection

Independent per-position top choices can be individually plausible but mutually inconsistent, causing early rejection during target verification. DFlash 2 retains the top 16 candidates at each position and scores a predecessor candidate $a$ and current candidate $b$ as

$$
S_t(a,b)=U_t(b)+\langle A(a)\odot H(h_t),B(b)\rangle.
$$

Here $U_t(b)$ is the base DFlash logit, $A$ and $B$ are learned 256-dimensional token embeddings, and $H(h_t)$ gates their compatibility using the current hidden state. All adjacent-pair scores are computed in parallel; the source describes a final sequential greedy walk from the last verified token, or sampling/rejection sampling over those precomputed scores.[^inco-dflash2-2026]

On the source’s five-layer Qwen3-4B/GSM8K setting, recall of the correct first proposal is 85.4% at rank 1 but 99.5% within the top 16. The reported selector-only ablation raises mean acceptance length from 4.27 to 4.61 at temperature zero and from 3.78 to 4.25 at temperature one, with 2.0M added parameters and 0.6% added draft–verify cycle latency.[^inco-dflash2-2026]

## Block-local dynamic convolution

The source calls the decline in candidate recall at later draft positions *suffix decay*. Its attention analysis reports that within-block attention mass falls from 30% in layer 1 to 8% in layer 5 and becomes concentrated in fewer heads. DFlash 2 therefore places a two-tap dynamic depthwise convolution before and after every attention and feed-forward sublayer:

$$
\operatorname{Conv}_{k}(x)_t=k_{t,0}\odot x_t+k_{t,1}\odot x_{t-1}.
$$

The first draft position reads the last verified token representation; later positions read their predecessor. Coefficients combine learned base kernels with hidden-state-dependent corrections shared across each 16-channel group. This creates block-local, predecessor-to-successor information flow while positions continue to compute in parallel.[^inco-dflash2-2026]

The reported five-layer convolutional drafter adds 16.5M parameters (3%) and 0.7% cycle latency. It approaches the source’s 15-layer DFlash recall curve while avoiding its reported 15.2% added latency; the source also reports layer-4/5 mean within-block attention falling from 9.4% to 0.5%, consistent with—but not proving—the convolution taking over local dependency work.[^inco-dflash2-2026]

## Relationships

- **Extends:** [DFlash block-diffusion speculative decoding](dflash-block-diffusion-speculative-decoding.md) with selection and local-dependency modules while retaining parallel block drafting.
- **Measured by:** [DFlash 2 evaluation and deployment](dflash-2-evaluation-and-deployment.md).
- **Uses:** [Speculative decoding exact sampling](speculative-decoding-exact-sampling.md) when rejection sampling is used to preserve the target distribution.

## Evidence limits

This is a vendor-authored release post, not an independently reviewed paper or reproduction. Its mechanism details, ablations, attention interpretation, and latency figures are limited to the stated Qwen3 configurations and workloads. The claim that rejection sampling leaves output distribution unchanged depends on a correct verifier and sampling implementation; it does not establish bitwise-identical output or a universal latency benefit.[^inco-dflash2-2026]

[^inco-dflash2-2026]: Inco AI, “DFlash 2: Keep Drafting Parallel” (August 2026), [source](../raw/DFlash2.md), “The Right Tokens Are Already There,” “Suffix Decay Is a Local Problem,” and “A Lightweight Local Convolution.” Local Figures 1, 3, and 4 were visually inspected and agree with their captions.
