---
type: Concept
title: LayoutRL and Infinity-Parser
description: LayoutRL trains an end-to-end document-image parser with rewards for content similarity, segment count, and reading order; Infinity-Parser is its Qwen2.5-VL-7B implementation.
tags: [document-parsing, reinforcement-learning, vision-language-models]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:08:57Z }
sources:
  - id: infinity-parser-paper
    resource: ../raw/2506.03197_InfinityParser/main.tex
    title: "Infinity-Parser: Layout-Aware Reinforcement Learning for Scanned Document Parsing"
  - id: infinity-parser-model-card
    resource: ../raw/Infinity-Parser-7B.md
    title: Infinity-Parser-7B model card
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
---

# LayoutRL and Infinity-Parser

LayoutRL is an end-to-end reinforcement-learning approach for converting scanned document images directly into structured Markdown. Instead of producing an explicit reasoning trace, the policy emits a final parse and receives a verifiable reward that combines content fidelity, element-count agreement, and reading-order preservation. Infinity-Parser is the paper's 7B implementation, trained from Qwen2.5-VL-7B with GRPO and the [Infinity-Doc-400K](infinity-doc-400k.md) corpus.[^infinity-parser-paper]

## Method

For each document, GRPO samples a group of candidate outputs, scores each with the multi-aspect reward, and derives relative advantages within the group without a learned critic. The three reward components are:[^infinity-parser-paper]

- **Edit-distance reward:** normalized character-level Levenshtein similarity between matched predicted and reference segments.
- **Count reward:** penalizes differences between predicted and reference paragraph counts.
- **Order reward:** penalizes pairwise inversions among matched paragraphs relative to the reference reading order.

The method first applies the Hungarian algorithm to match predicted and reference segments one-to-one. It then averages edit similarity over matched pairs, computes count and order terms from the matching, and sums the three rewards with equal coefficients in the displayed objective.[^infinity-parser-paper]

## Reported implementation

The authors report direct RL from Qwen2.5-VL-7B on a random 43K-document subset, using Verl, eight 80 GB A100 GPUs, eight responses per input, an 8,192-token response limit, temperature 1.0, rollout and global batch sizes of 128, AdamW at a learning rate of $10^{-6}$, KL coefficient $10^{-2}$, and one training epoch.[^infinity-parser-paper]

## Reported results

All results below are author-reported and were not independently reproduced from this source bundle:[^infinity-parser-paper]

- On OmniDocBench, Infinity-Parser-7B reports overall edit distances of **0.141 for English** and **0.197 for Chinese**, lower than the compared systems in the paper's table.
- On olmOCR-Bench, it reports an **82.5 overall score**, compared with 77.4 for anchored olmOCR v0.1.68.
- On PubTabNet, it reports **93.46 TEDS-S** and **91.82 TEDS**; on FinTabNet, **97.16 TEDS-S** and **95.92 TEDS**.
- The reward ablation reports progressive gains from edit-only RL to edit-plus-count and then the full reward. The full direct-RL configuration reaches 0.141/0.197 English/Chinese edit distance and 0.104 category error; adding SFT before RL changes these to 0.163/0.195 and 0.092, so its benefit is metric-dependent rather than uniformly absent.
- Training curves and domain-held-out evaluations in the paper show stronger page-level and out-of-distribution scores for RL than SFT, while paragraph-level gaps are smaller. These plots support the paper's generalization claim but do not isolate whether the gain comes from RL itself, reward design, sampling compute, or other training differences.

## Model card and release

The model card identifies the release as **Infinity-Parser-7B**, links to GitHub, Hugging Face dataset and demo pages, and declares an Apache-2.0 license. Those external endpoints and the linked quick-start instructions were not independently inspected.[^infinity-parser-model-card]

## Trust limits and open questions

- The model card says the model does not emit layout or bounding-box information and lacks chart and figure perception, visual reasoning, and structured graphical extraction. It also says this prevents reading-order prediction, which is in tension with both its own claimed reading-order benchmark evaluation and the paper's order-preservation reward; the sources do not clarify whether the limitation concerns a distinct bounding-box reading-order interface rather than ordered text output.[^infinity-parser-model-card][^infinity-parser-paper]
- The model card's referenced `assets/` directory is absent from this local source bundle, so its architecture, benchmark, general-capability, and comparison images could not be inspected. Its prose claims state-of-the-art results but supplies no auditable values in the Markdown itself.[^infinity-parser-model-card]
- The source is an author manuscript and labels its artifacts as forthcoming; this bundle does not contain the dataset, model weights, training code, or evaluation scripts needed to reproduce the claims.[^infinity-parser-paper]
- The reward equations leave edge cases underspecified: the count term can become negative when overprediction exceeds the reference count, and the order term has a zero denominator for fewer than two reference elements.[^infinity-parser-paper]
- The prose calls the final objective a weighted combination, but the displayed equation is an unweighted sum. No alternative coefficients are reported.[^infinity-parser-paper]
- The paper compares direct RL and SFT, but its evidence does not by itself establish the broad causal claim that SFT memorizes while RL generalizes.
- Training targets longer than 8K tokens are left-truncated, which can remove early-page content and potentially alter layout and reading-order supervision.[^infinity-parser-paper]

## Relationships

- **Precedes:** [Infinity-Parser2](infinity-parser2.md), which the later report describes as its next generation and expands from page-to-Markdown parsing to multi-task structured outputs.[^infinity-parser2-report]
- **Uses:** [Infinity-Doc-400K](infinity-doc-400k.md) supplies synthetic and pseudo-labeled document/reference pairs for training and reward computation.
- **Compared with:** [PP-StructureV3](pp-structurev3.md) addresses the same page-to-structured-document task with a modular specialist pipeline rather than an end-to-end 7B VLM; cross-paper benchmark ranks require matched evaluation versions and protocols.

[^infinity-parser-paper]: Wang et al., *Infinity-Parser: Layout-Aware Reinforcement Learning for Scanned Document Parsing*, local LaTeX source bundle at [main.tex](../raw/2506.03197_InfinityParser/main.tex), including its referenced section and figure files (accessed 2026-08-17).
[^infinity-parser-model-card]: *Infinity-Parser-7B model card*, local Markdown source at [Infinity-Parser-7B.md](../raw/Infinity-Parser-7B.md); referenced image assets were absent (accessed 2026-08-17).
[^infinity-parser2-report]: INF Team, *Infinity-Parser2 Technical Report*, local LaTeX source at [arxiv_latex.tex](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex) (accessed 2026-08-17).
