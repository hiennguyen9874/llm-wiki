---
type: Concept
title: BERT masked-language and next-sentence pre-training
description: BERT learns bidirectional token representations by predicting selected corrupted tokens and jointly classifying whether paired text spans are consecutive.
tags: [bert, pre-training, masked-language-modeling, next-sentence-prediction]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:22:53Z }
sources:
  - id: devlin-bert-2018
    resource: ../raw/arXiv-1810.04805v2/main.tex
    title: BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
---

# BERT masked-language and next-sentence pre-training

BERT pre-trains its encoder with masked language modeling (MLM) and next-sentence prediction (NSP). MLM hides the target from its contextual representation so every encoder layer can condition on both directions; NSP trains the `[CLS]` state to distinguish contiguous spans from randomly paired spans.[^devlin-bert-2018]

## Masked language modeling

The training generator selects 15% of WordPiece positions for prediction and optimizes cross-entropy for their original tokens only. At selected positions, it substitutes `[MASK]` 80% of the time, a random token 10% of the time, and leaves the token unchanged 10% of the time. The mixed corruption reduces the mismatch from `[MASK]` not appearing in fine-tuning inputs.[^devlin-bert-2018]

The source’s ablation found fine-tuning relatively robust to alternate mixtures, while always using `[MASK]` was weaker for its fixed-feature NER setup. It also found an all-random corruption strategy substantially weaker than BERT’s mixture in the reported settings.[^devlin-bert-2018]

## Next-sentence prediction

For each pair of text spans A and B, B is the actual following span half of the time (`IsNext`) and a random corpus span half of the time (`NotNext`). The final `[CLS]` state predicts this binary label. The paper’s ablation associates removing NSP with lower reported QNLI, MNLI, and SQuAD v1.1 development scores; this is evidence for the tested BERT-era setup, not a universal claim about all pre-training recipes.[^devlin-bert-2018]

## Training regime

The paper pre-trained on BooksCorpus (about 800M words) plus English Wikipedia text (about 2.5B words). It used 1M steps of Adam with 256 sequences per batch, 10,000 warmup steps, linear learning-rate decay, and 0.1 dropout; 90% of steps used length 128 and the final 10% length 512 to reduce the cost of quadratic attention.[^devlin-bert-2018]

## Relationships

- **Pre-trains:** [BERT bidirectional transfer learning](bert-bidirectional-transfer-learning.md).
- **Depends on:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) to combine left and right context in the encoder.

[^devlin-bert-2018]: Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova, “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,” arXiv:1810.04805v2, bundled [LaTeX source](../raw/arXiv-1810.04805v2/main.tex), including `bert.tex`, `bert_details.tex`, and the ablation tables.
