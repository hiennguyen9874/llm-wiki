---
type: Concept
title: UEmbed
description: A 2B, 4B, and 9B Qwen3.5 multimodal embedding family that emits dense and learned-sparse vectors from one causal forward pass.
tags: [embedding, retrieval, multimodal, dense-retrieval, sparse-retrieval, splade, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:30:37Z }
sources:
  - id: uembed-tech-report
    resource: ../raw/2608.02583_UEmbed/main.tex
    title: UEmbed technical-report LaTeX source
---

# UEmbed

UEmbed is a 2B, 4B, and 9B Qwen3.5-based multimodal embedding family. Each checkpoint produces normalized dense EOS embeddings and sparse lexical vectors from a single causal forward pass, for text, image, video, and visual-document retrieval.[^uembed-tech-report]

## Architecture

- The dense vector is the EOS hidden state immediately before 16 appended learnable special tokens; when sparse retrieval is not needed, those tokens may be omitted.[^uembed-tech-report]
- Each appended token attends to the preceding input and drives a separate linear sparse head over one of 16 disjoint vocabulary subsets. The subsets come from k-means clustering; concatenating the head outputs produces the sparse vector.[^uembed-tech-report]
- Vocabulary canonicalization strips accents, lowercases, and collapses whitespace, reducing 248,320 tokenizer entries to 184,016 canonical entries. The sparse activation is $\log(1 + \operatorname{ReLU}(\text{logits}))$.[^uembed-tech-report]
- Training combines dense cosine-similarity InfoNCE, sparse-inner-product InfoNCE, and query/document FLOPS regularization. The reported default uses equal dense/sparse loss weighting, dense temperature 0.03, sparse temperature 32, and 16 special tokens.[^uembed-tech-report]

## Training and deployment

The report describes a 3.94M-public-sample mixture: 1.55M text, 1.07M image, 0.84M video, and 0.48M visual-document examples. It fine-tunes attention and MLP projections with LoRA while freezing the visual encoder; Qwen3-VL-Embedding-8B mines multimodal hard negatives.[^uembed-tech-report]

Sparse vectors are compatible with inverted indexes, while the causal backbone remains compatible with autoregressive serving stacks. The report’s BrowseComp-Plus offline-index experiment shows a latency--quality trade-off as query activations are capped, but it does not publish the chart’s exact data or a multi-corpus scaling study.[^uembed-tech-report]

## Reported evaluation

On the report’s MMEB-v2 evaluation (78 datasets), 9B reaches 71.8 dense and 71.0 sparse; 4B reaches 70.4 and 69.7; and 2B reaches 66.5 and 65.5. These are author-reported results, and comparison tables exclude Qwen3-VL-Embedding from bolded best-score selection because its training data are described as large-scale proprietary data.[^uembed-tech-report]

On nine BEIR datasets, the reported 9B averages are 56.3 nDCG@10 dense and 55.2 sparse. The report also finds a small 2B hybrid gain on text and visual-document subsets, whereas image and video results are essentially unchanged from dense retrieval.[^uembed-tech-report]

## Limits

The authors report English/Chinese-heavy training data and limited sparse cross-lingual activation, occasional anomalous vocabulary activations, and a larger sparse-versus-dense gap on video than on text or visual-document tasks. The scores and explanations are author-reported, not independent validation.[^uembed-tech-report]

## Relationships

- **Includes variant:** [UEmbed-4B](uembed-4b.md).

[^uembed-tech-report]: [UEmbed technical-report LaTeX source](../raw/2608.02583_UEmbed/main.tex). The report supplies author-reported architecture, training, and evaluation claims. Its tables and rendered chart attachments were inspected; no external benchmark reproduction was available.
