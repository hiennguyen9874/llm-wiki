---
type: Concept
title: Nemotron-3-Embed-1B-BF16
description: A 1.14B-parameter Ministral-3-3B-derived multilingual text embedding model with 2,048-dimensional mean-pooled outputs and self-reported 72.38 RTEB NDCG@10.
tags: [embedding, retrieval, multilingual, nemotron, nvidia, ministral]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:34:59+07:00 }
sources:
  - id: nemotron-3-embed-1b-card
    resource: ../raw/Nemotron-3-Embed-1B-BF16.md
    title: Nemotron-3-Embed-1B-BF16 model card
---

# Nemotron-3-Embed-1B-BF16

Nemotron-3-Embed-1B-BF16 is NVIDIA's multilingual dense text-embedding model for retrieval and semantic similarity. It has approximately 1.14B parameters, is derived by pruning and distilling a Ministral-3-3B-Instruct-2512-based embedding model, and produces normalized 2,048-dimensional vectors through bidirectional-attention encoding and average pooling. [^nemotron-3-embed-1b-card]

## Benchmarks

The model card reports chunk-retrieval average NDCG@10 scores with its sequence length set to 4,096 tokens. It evaluates the model on 16 public Retrieval Embedding Benchmark (RTEB) tasks, MMTEB Retrieval datasets, and OCR-extracted text from eight ViDoRe-V3 datasets. These are model-card-reported results rather than independently reproduced measurements. [^nemotron-3-embed-1b-card]

| Benchmark | NDCG@10 |
|---|---:|
| RTEB | 72.38 |
| ViDoRe-V3 text | 57.74 |
| MMTEB (Retrieval) | 71.04 |

The card calls the model state of the art among comparably sized models on multiple multilingual retrieval benchmarks, but does not define the comparison set or provide per-task results in the supplied source. [^nemotron-3-embed-1b-card]

## Model size and architecture

- **Parameters:** approximately 1.14B. [^nemotron-3-embed-1b-card]
- **Backbone and derivation:** a pruned model based on `mistralai/Ministral-3-3B-Instruct-2512`. Two structured-pruning and distillation rounds reduced an embedding-trained 3B parent to 2B, then to the final 1.14B model. [^nemotron-3-embed-1b-card]
- **Pruning and distillation:** NVIDIA ModelOpt `mcore_minitron` neural-architecture search considered hidden width, FFN size, attention heads, and depth; candidates used a 50k in-domain calibration corpus. The 2B model was distilled from Nemotron-3-Embed-8B-BF16 using cosine-distance and MSE losses over a multilingual in-domain retrieval blend, then the procedure was repeated for the final model. [^nemotron-3-embed-1b-card]
- **Embedding encoder:** Transformer with bidirectional attention masking and average pooling over token representations. [^nemotron-3-embed-1b-card]
- **Dimensions and context:** hidden size and output dimension are 2,048; maximum input length is 32,768 tokens. Vectors may be prefix-sliced to smaller dimensions and L2-renormalized. [^nemotron-3-embed-1b-card]

## Language support

The card describes the model as multilingual and capable of multilingual and cross-lingual retrieval. It was evaluated across 34 languages: English, Arabic, Assamese, Bengali, Bulgarian, Chinese, Danish, Dutch, Finnish, French, German, Hindi, Hinglish, Indonesian, Italian, Japanese, Korean, Malay, Marathi, Nepali, Norwegian, Persian, Portuguese, Romanian, Russian, Spanish, Swahili, Swedish, Tamil, Telugu, Thai, Ukrainian, Urdu, and Vietnamese. Evaluation coverage is not a guarantee of quality for every language. [^nemotron-3-embed-1b-card]

## Training data

The model card reports more than **8.5M text training data points** in 161 dataset files. Distillation training used publicly available, commercially permissible datasets and synthetically generated data; collection and labeling are characterized as a hybrid of human, automated, and synthetic methods. [^nemotron-3-embed-1b-card]

Named public datasets include MIRACL, MLDR, HotpotQA, NQ, SQuAD, Stack Exchange, HoVer, TAT-QA, FinQA, PubMedQA, MedQuAD, JaQuAD, CoIR retrieval datasets, SWE-bench, MLQA, SpartQA, Winogrande, and TempReason. The card also names FinePdfs, CentralActs, BRIGHT, and MultiHiertt as seed datasets for synthetic pairs. [^nemotron-3-embed-1b-card]

Synthetic query–document pairs were generated from scratch or from seed data using the listed Qwen, Gemma, GPT-OSS, and NVIDIA Nemotron generative models. The supplied source does not state mixture proportions, data-language distribution, filtering procedures, or a license-by-dataset inventory. [^nemotron-3-embed-1b-card]

[^nemotron-3-embed-1b-card]: [Nemotron-3-Embed-1B-BF16 model card](../raw/Nemotron-3-Embed-1B-BF16.md). Architecture, training-data, language, and benchmark claims are reported by the model card; linked external datasets and benchmark materials were not independently inspected.
