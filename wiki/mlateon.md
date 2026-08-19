---
type: Concept
title: mLateOn
description: A 307M-parameter mmBERT-base multilingual ColBERT retriever with 128-dimensional token vectors, MaxSim scoring, and an 8,192-token context limit.
tags: [embedding, retrieval, late-interaction, colbert, multilingual, code, lighton]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:33:04+07:00 }
sources:
  - id: mlateon-card
    resource: ../raw/mLateOn.md
    title: mLateOn model card
---

# mLateOn

mLateOn is LightOn's 307M-parameter multilingual ColBERT (multi-vector) retrieval model, built on mmBERT-base and trained with PyLate. It represents queries and documents as 128-dimensional token vectors, scores them with MaxSim, and supports inputs up to 8,192 tokens. The model card reports strong results on English, multilingual, long-document, and code retrieval; these are vendor-reported rather than independently reproduced here. [^mlateon-card]

## Benchmarks

The model card reports NDCG@10 headline results across BEIR, MIRACL, MLDR, and MTEB Code. `tgt` denotes benchmark languages that overlap the nine retrieval-training languages; the unsuffixed multilingual results cover all benchmark languages. [^mlateon-card]

| Benchmark | Reported score | Result described by the model card |
|---|---:|---|
| BEIR | 57.56 | Highest among the models in its table; above English-only LateOn (57.22) |
| MIRACL target languages | 65.61 | Highest among the models in its table |
| MIRACL, all languages | 67.04 | Competitive with models trained on more languages; BGE-M3 scores 69.62 in the table |
| MLDR target languages | 87.69 | Highest in the table, 9.30 points above LFM2.5-ColBERT-350M (78.39) |
| MLDR, all languages | 77.92 | Reported aggregate across all benchmark languages |
| MTEB Code | 73.48 | Strong code-retrieval result; voyage-4-nano scores 76.43 in the table |

The source attributes the target-to-full MIRACL increase (65.61 to 67.04) to generalization to languages absent from retrieval fine-tuning, including Cyrillic-script languages and Japanese. It does not provide per-language scores, evaluation configurations, or independent replication. [^mlateon-card]

## Model size and architecture

- **Size and base:** 307M parameters, built on mmBERT-base. [^mlateon-card]
- **Retrieval architecture:** a PyLate ColBERT late-interaction encoder. Queries and documents produce multiple vectors (one per retained token); MaxSim aggregates token-level query–document similarities. This differs from a single-vector dense encoder. [^mlateon-card]
- **Projection stack:** a `ModernBertModel` transformer followed by bias-free identity dense layers of 768→1,536 (residual), 1,536→768 (residual), and 768→128 (no residual). [^mlateon-card]
- **Limits:** maximum sequence length of 8,192 tokens for both queries and documents; 128-dimensional output token vectors. [^mlateon-card]

## Language support

The card lists English, French, German, Italian, Spanish, Portuguese, Swedish, Norwegian, and Arabic. It also claims generalization to unseen languages and scripts, citing Cyrillic and Japanese as examples, but does not enumerate every such language or define a supported-language guarantee beyond the listed nine. [^mlateon-card]

## Training data

The model uses a translate-train recipe: validated English data was machine-translated into French, German, Italian, Spanish, Portuguese, Swedish, Norwegian, and Arabic, with cross-lingual pairs added for alignment. [^mlateon-card]

- **Pre-training:** a stated 2.8B-pair mixture comprising 2.16B multilingual curated pairs and 665M curated English pairs. The multilingual portion spans the eight non-English target languages and includes 220M cross-lingual pairs. The card says the English parent dataset contained 1.4B annotated pairs before filtering and deduplication. [^mlateon-card]
- **Fine-tuning:** a stated 16.3M-sample mixture across the nine listed languages plus Code and Code Edit splits. The process removes mined candidates whose score exceeds 95% of the positive's relevance, retains the top 10 remaining hard negatives per sample, and uses mxbai-rerank-large-v2 annotations for distillation. [^mlateon-card]
- **Multilingual fine-tuning:** MIRACL and MLDR negatives were mined from available datasets with snowflake-arctic-embed-l-v2.0 (2,048 negatives per sample); other language splits were translated from filtered English examples. The English unfiltered parent corpus is stated as 1.88M examples with 2,048 GTE-ModernBERT-mined negatives. [^mlateon-card]
- **Code data:** Code derives from LateOn-Code data; Code Edit derives from CommitPackFT and was decontaminated against CodeEditSearch by shared commit SHA, normalized-text match, and at least 50% 13-gram overlap. [^mlateon-card]

The source links released datasets but does not provide their licenses, collection dates, mixture proportions by language or data type, or independent data-quality audit; those omissions limit provenance and coverage assessment. [^mlateon-card]

[^mlateon-card]: [mLateOn model card](../raw/mLateOn.md). Model, benchmark, language, and training-data claims are reported by LightOn's model card.
