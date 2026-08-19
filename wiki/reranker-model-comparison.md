---
type: Synthesis
title: Reranker model comparison
description: A use-case selection guide for the eleven dedicated reranker checkpoints documented from local raw model cards and reports.
tags: [reranking, retrieval, comparison, selection]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T14:36:00Z }
sources:
  - id: qwen-text-card
    resource: ../raw/Qwen3-Reranker-4B.md
    title: Qwen3 text reranker model card
  - id: qwen-vl-card
    resource: ../raw/Qwen3-VL-Reranker-8B.md
    title: Qwen3-VL reranker model card
  - id: zerank-card
    resource: ../raw/zerank-2-reranker.md
    title: zerank-2 model card
  - id: ettin-card
    resource: ../raw/ettin-reranker-68m-v1.md
    title: ettin-reranker-68m-v1 model card
  - id: jina-v35-card
    resource: ../raw/jina-reranker-v3.5.md
    title: jina-reranker-v3.5 model card
  - id: jina-v35-report
    resource: ../raw/2607.18152_jina-reranker-v3.5/main.tex
    title: jina-reranker-v3.5 technical report
  - id: xprovence-card
    resource: ../raw/xprovence-reranker-bgem3-v2.md
    title: XProvence model card
  - id: querit-card
    resource: ../raw/Querit-Reranker.md
    title: Querit-Reranker model card
---

# Reranker model comparison

For a commercial, text-only RAG or search system without a hard latency limit, use [Qwen3-Reranker-4B](qwen3-reranker-4b.md) as the default. It is Apache-2.0, supports 100+ languages and task instructions, and is the strongest Qwen size on the publisher's English retrieval and instruction-following evaluations. Use [Qwen3-Reranker-8B](qwen3-reranker-8b.md) when Chinese, multilingual, long-document, or code retrieval quality justifies the additional cost. [^qwen-text-card]

## Selection by use case

| Use case | Recommended model | Why | Important constraint |
|---|---|---|---|
| General commercial text RAG/search | [Qwen3-Reranker-4B](qwen3-reranker-4b.md) | Apache-2.0, 32K context, 100+ languages, custom instructions; leads its family on English retrieval (69.76) and FollowIR (14.84). | Pointwise scoring; publisher results rerank top 100 from Qwen3-Embedding-0.6B. [^qwen-text-card] |
| Chinese, multilingual, code, or maximum text quality | [Qwen3-Reranker-8B](qwen3-reranker-8b.md) | Best reported Qwen results on C-MTEB (77.45), MMTEB (72.94), MLDR (70.19), and code (81.22). | Same 32K pointwise design and evaluation regime; expect higher serving cost than 4B. [^qwen-text-card] |
| Low-cost multilingual text reranking | [Qwen3-Reranker-0.6B](qwen3-reranker-0-6b.md) | Apache-2.0, 100+ languages, instructions, and 32K context at the smallest Qwen size. | It trails 4B/8B on most reported tasks; use it only when throughput or memory dominates. [^qwen-text-card] |
| Image, screenshot, video, or mixed-modality retrieval | [Qwen3-VL-Reranker-8B](qwen3-vl-reranker-8b.md) | Apache-2.0 model that jointly reranks text, images, screenshots, video, and mixed pairs; it leads its 2B sibling on every reported aggregate. | Author-run top-100 pipeline scores; use [Qwen3-VL-Reranker-2B](qwen3-vl-reranker-2b.md) when 2B cost is necessary. [^qwen-vl-card] |
| Long candidate lists with low model size, non-commercial use | [jina-reranker-v3.5](jina-reranker-v3-5.md) | 0.6B listwise reranker with 131K context; one pass jointly ranks a candidate list and its report shows better BEIR than Qwen3-Reranker-4B under its stated protocol. | CC BY-NC 4.0: not suitable for ordinary commercial self-hosting. It trails 4B Qwen on reported MIRACL, RTEB, and structured retrieval. [^jina-v35-card] [^jina-v35-report] |
| Very high throughput / CPU or modest GPU, English only | [ettin-reranker-68m-v1](ettin-reranker-68m-v1.md) | Apache-2.0 68.6M cross-encoder; the card reports 1,916 pairs/s on RTX 3090 and 31.2 on an i7-13700K at 512 tokens. | English only and 7,999-token maximum; benchmark results are not directly comparable to Qwen's. [^ettin-card] |
| Web, STEM, legal, biomedical, finance, or code where its domain evaluation matches yours | [zerank-2](zerank-2.md) | Apache-2.0 4B/32K reranker; its publisher reports a 0.6714 average NDCG@10 across seven named domains. | Language support, throughput, and reproducible training detail are absent; validate against Qwen 4B on your corpus. [^zerank-card] |
| RAG context compression plus reranking, non-commercial use | [XProvence-reranker](xprovence-reranker.md) | Removes irrelevant sentences while providing a reranking score, reducing LLM context noise. | CC BY-NC-ND 4.0; optimized for QA and paragraph-scale training contexts, not a general commercial default. [^xprovence-card] |

## Benchmark comparison

**Do not merge the following tables into one overall rank.** Each table uses a different candidate generator, benchmark version, and sometimes a different metric. Scores are publisher/author-reported pipeline results, not independent end-to-end evaluations.

### 1. Same Qwen text-reranking protocol

All models rerank the same top-100 candidates retrieved by Qwen3-Embedding-0.6B. Higher is better.

| Model | MTEB English | C-MTEB | MMTEB | MLDR | MTEB Code | FollowIR |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3-Reranker-0.6B | 65.80 | 71.31 | 66.36 | 67.28 | 73.42 | 5.41 |
| **Qwen3-Reranker-4B** | **69.76** | 75.94 | 72.74 | 69.97 | 81.20 | **14.84** |
| **Qwen3-Reranker-8B** | 69.02 | **77.45** | **72.94** | **70.19** | **81.22** | 8.05 |

**Reading:** 4B is the best English and instruction-following Qwen; 8B is best in Chinese, multilingual, long-document, and code retrieval. 0.6B is a cost-oriented option, not a quality winner. [^qwen-text-card]

### 2. Same Qwen multimodal protocol

All models rerank top-100 candidates from Qwen3-VL-Embedding-2B. Higher is better. MMEB is multimodal retrieval; JinaVDR and ViDoRe v3 evaluate visual-document retrieval.

| Model | MMEB-v2 avg | Image | Video | Visual document | MMTEB | JinaVDR | ViDoRe v3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3-VL-Embedding-2B (first-stage baseline) | 73.4 | 74.8 | 53.6 | 79.2 | 68.1 | 71.0 | 52.9 |
| Qwen3-VL-Reranker-2B | 75.1* | 73.8 | 52.1 | 83.4 | 70.0 | 80.9 | 60.8 |
| **Qwen3-VL-Reranker-8B** | **79.2** | **80.7** | **55.8** | **86.3** | **74.9** | **83.6** | **66.7** |

\*The accompanying technical report gives 75.2 rather than 75.1; the source does not explain the 0.1 difference. **Reading:** 2B substantially improves visual-document metrics at lower cost; 8B is consistently stronger and is the quality choice. [^qwen-vl-card]

### 3. Jina report's direct text comparison

The Jina report reranks top-100 candidates from Jina Embeddings v5 Text Small; Struct-IR instead uses a controlled pool. Values are nDCG@10 (%).

| Model | BEIR | MIRACL | RTEB† | Struct-IR |
|---|---:|---:|---:|---:|
| Qwen3-Reranker-0.6B | 56.94 | 67.12 | 68.41 | 41.9 |
| Qwen3-Reranker-4B | 62.28 | **76.56** | **77.68** | **55.6** |
| jina-reranker-v3 (deprecated) | 62.10 | 72.20 | 68.01 | 38.7 |
| **jina-reranker-v3.5** | **63.20** | 74.11 | 70.95 | 48.3 |

†RTEB excludes the MIRACL average. **Reading:** Jina v3.5 narrowly wins BEIR at 0.6B, but Qwen 4B wins the reported multilingual, domain, and structured columns. This does not override license constraints: Jina v3.5 is CC BY-NC 4.0. [^jina-v35-card] [^jina-v35-report]

### 4. Other reported benchmarks

| Model | Protocol and reported result | Interpretation |
|---|---|---|
| ettin-reranker-68m-v1 | MTEB English v2 Retrieval, top-100 reranking averaged over six retrievers: **0.5915** NDCG@10. Its card's same table lists Qwen3-4B 0.6367, Qwen3-0.6B 0.5940, and zerank-2 0.5300; 4B Qwen-based models were capped at 8,192 tokens. | Ettin is competitive with Qwen 0.6B at only 68.6M parameters, but trails Qwen 4B; it is English-only. [^ettin-card] |
| zerank-2 | Top-100 from OpenAI `text-embedding-3-small`: NDCG@10 **0.6714** average across Web, Conversational, STEM, Code, Legal, Biomedical, and Finance; scores range 0.6140–0.7600. | Strong publisher-reported domain table, but it cannot be numerically compared with Qwen/Jina tables. [^zerank-card] |
| XProvence-reranker | Claims evaluation on 26 languages and six datasets with little-to-no loss while pruning, but gives no numeric scores or full protocol. | Cannot rank it against the others. [^xprovence-card] |
| Querit-Reranker | No benchmark, scoring-interface, or quantitative evaluation is provided in the local card. | Cannot rank it. [^querit-card] |

## Do not select by default

- [Querit-Reranker](querit-reranker.md) is Apache-2.0 and offers 128K context with 0.43B active MoE parameters, but its raw card provides no scoring interface, benchmark numbers, or reproducible evaluation. [^querit-card]
- [jina-reranker-v3](jina-reranker-v3.md) is deprecated; v3.5 is its documented drop-in successor.

## Comparison limits

The available scores are **not a unified leaderboard**: Qwen text uses Qwen3-Embedding-0.6B for top-100 retrieval, Qwen-VL uses Qwen3-VL-Embedding-2B, Jina v3.5 uses Jina Embeddings v5 Text Small, zerank-2 uses OpenAI `text-embedding-3-small`, and ettin averages six first-stage embedding models. All are publisher or author reports. Run a held-out evaluation with your retrieval model, languages, document lengths, and latency budget before committing.

## Relationships

- **Supersedes for selection:** [jina-reranker-v3](jina-reranker-v3.md) is deprecated in favor of [jina-reranker-v3.5](jina-reranker-v3-5.md).
- **Uses:** Qwen's text rerankers use task-specific instructions; their card reports a 1%–5% decrease when instruction is omitted. [^qwen-text-card]

[^qwen-text-card]: [Qwen3-Reranker-4B model card](../raw/Qwen3-Reranker-4B.md). The family comparison, license, capability, and benchmark claims are publisher-authored.
[^qwen-vl-card]: [Qwen3-VL-Reranker-8B model card](../raw/Qwen3-VL-Reranker-8B.md). The multimodal, licensing, and benchmark claims are publisher-authored.
[^zerank-card]: [zerank-2 model card](../raw/zerank-2-reranker.md). The domain scores and deployment claims are publisher-authored.
[^ettin-card]: [ettin-reranker-68m-v1 model card](../raw/ettin-reranker-68m-v1.md). The benchmark and throughput claims are publisher-authored.
[^jina-v35-card]: [jina-reranker-v3.5 model card](../raw/jina-reranker-v3.5.md). Licensing, architecture, and API claims are publisher-authored.
[^jina-v35-report]: [jina-reranker-v3.5 technical report](../raw/2607.18152_jina-reranker-v3.5/main.tex). Comparative benchmark claims are author-reported.
[^xprovence-card]: [XProvence model card](../raw/xprovence-reranker-bgem3-v2.md). Pruning, licensing, and training-scope claims are publisher-authored.
[^querit-card]: [Querit-Reranker model card](../raw/Querit-Reranker.md). Capability claims are publisher-authored.
