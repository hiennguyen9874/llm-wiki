---
type: Benchmark
title: Translation-memory embedding and reranker pairing benchmark (community report)
description: A community-reported, non-reproducible 15-language English-to-target translation-memory retrieval test of embedding-plus-reranker pairs, in which F2LLM-v2 4B/8B with zerank-2 4B score highest (MRR 0.919–0.922).
tags: [benchmark, embedding, reranking, multilingual, translation-memory, community-report]
status: stable
created: 2026-10-22
stale_after: 2027-01-20
generated: { by: llm-wiki-agent/1, at: 2026-10-22T12:00:00Z }
sources:
  - id: reddit-embed-rerank-thread
    resource: ../raw/best_embedding_reranking_model.md
    kind: web
    title: "r/LocalLLaMA thread: Best Embedding + Reranking Model (post and 41 comments)"
---

# Translation-memory embedding and reranker pairing benchmark (community report)

A r/LocalLLaMA post reports an end-to-end test of embedding-plus-reranker pairs for a translation-memory server: given an English phrase, sentence, or paragraph, retrieve the already-translated counterpart in one of 15 Western and Eastern target languages. In the poster's run, [F2LLM-v2](f2llm-v2.md) 4B or 8B paired with [zerank-2](zerank-2.md) 4B tops every other pair. The data are proprietary and the run is a single author's, so this is a **Reported**, unreproducible, practitioner datapoint, not a leaderboard. [^reddit-embed-rerank-thread]

## Protocol

- **Pipeline:** embed the corpus of translated data, embed the query, search, then rerank. Metrics are MRR (Mean Reciprocal Rank, the final score), Re-Δ (described as how much the reranker helped), and R@20 (correct translation within the 20 retrieved entries). [^reddit-embed-rerank-thread]
- **Runtime:** all local models ran on llama.cpp at Q8_0; API models (Voyage) were called remotely. The author later reported identical scores for BF16 and Q8_0 on F2LLM 4B + Zerank 4B. [^reddit-embed-rerank-thread]
- **Limits:** the benchmark data cannot be shared; no query counts, per-language scores (except Chinese below), confidence intervals, or latency measurements are given. Re-Δ's exact formula is not stated; the values are consistent with a relative MRR change versus embedding-only retrieval (**Synthesis**), and negative values mean the reranker lowered MRR. [^reddit-embed-rerank-thread]

## Results: all 15 languages

Table "Embed Model / Reranker Model" in the post body. Vendor-neutral, single-author, **Reported**.

| Embedding model | Reranker | MRR | Re-Δ | R@20 |
|---|---|---:|---:|---:|
| BGE M3 0.6B | BGE M3 Reranker V2 0.6B | 0.821 | −1.60% | 91.90% |
| BGE M3 0.6B | Qwen3-Reranker-0.6B | 0.776 | −7.50% | 91.90% |
| F2LLM 1.7B | Zerank 1 1.7B | 0.871 | −2.20% | 96.80% |
| Qwen3-Embedding-4B | Qwen3-Reranker-4B | 0.739 | +11.00% | 77.50% |
| Zembed 4B | zerank-2 4B | 0.664 | +25.80% | 67.10% |
| **F2LLM 4B** | **zerank-2 4B** | **0.919** | +2.40% | **98.40%** |
| **F2LLM 8B** | **zerank-2 4B** | **0.922** | +1.60% | **99.20%** |
| PPLX Embed V1 4B | zerank-2 4B | 0.8825 | +10.10% | 91.90% |
| Octen Embed 4B | zerank-2 4B | 0.853 | +12.40% | 89.00% |
| Voyage 4 Large [API] | Voyage Rerank 2.5 [API] | 0.889 | +8.50% | 94.70% |

**Reading (Synthesis):**

- **First-stage recall dominates.** Final MRR tracks R@20 closely: the pairs with R@20 above 96% all score MRR ≥ 0.871, while Qwen3-Embedding-4B (77.5%) and Zembed 4B (67.1%) fall to 0.739 and 0.664 despite large reranker gains of +11% and +25.8%. A reranker cannot recover a candidate the embedder did not retrieve.
- **Strong embedders gain little from reranking.** Re-Δ is only +1.6% to +2.4% for F2LLM 4B/8B and negative for F2LLM 1.7B and BGE M3, whereas weaker embedders gain 10–26%.
- **Qwen3 pair underperforms here.** [Qwen3-Embedding-4B](qwen3-embedding-4b.md) with [Qwen3-Reranker-4B](qwen3-reranker-4b.md) scores 0.739; with BGE M3 retrieval, [Qwen3-Reranker-0.6B](qwen3-reranker-0-6b.md) lowers MRR by 7.5%. The author attributes this to Qwen3 models winning public benchmarks but being "mediocre in real world use cases".
- **8B adds little.** F2LLM 8B improves MRR by 0.003 over 4B and R@20 by 0.8 points; the author judged the latency not worth it. A commenter said the 8B-versus-4B check for Qwen3 and Octen was only partial ("tested halfway"), and the table omits Qwen3 8B, which several commenters use. [^reddit-embed-rerank-thread]

The [Octen-Embedding-4B](octen-embedding-4b.md) row is a Qwen3-Embedding-4B derivative that scores above its base model in this pair (0.853 versus 0.739, with different recall), though only the zerank-2 reranker was shared across them. The comparison confounds embedder and reranker.

## Results: Chinese follow-up

In a comment, the author reported the same pipeline restricted to Simplified (zh-Hans) and Traditional (zh-Hant) Chinese. **Reported.**

| Embedding model | Reranker | zh-Hans MRR | Re-Δ | R@20 | zh-Hant MRR | Re-Δ | R@20 |
|---|---|---:|---:|---:|---:|---:|---:|
| F2LLM 1.7B | Zerank 1 1.7B | 0.932 | +2.20% | 99.70% | 0.939 | +1.40% | 99.70% |
| F2LLM 4B | zerank-2 4B | **0.961** | +5.80% | **100.00%** | **0.954** | +6.20% | **100.00%** |
| F2LLM 8B | zerank-2 4B | 0.957 | +6.10% | **100.00%** | **0.954** | +4.60% | **100.00%** |
| Voyage 4 Large [Paid] | Voyage Rerank 2.5 [Paid] | 0.936 | +6.60% | 97.00% | 0.944 | +3.80% | 98.90% |
| Qwen3-Embedding-4B | Qwen3-Reranker-4B | 0.888 | +14.40% | 94.50% | 0.872 | +11.10% | 91.60% |

Re-Δ for F2LLM 1.7B + Zerank 1 is positive here but −2.20% in the all-language table; the post does not explain the sign difference. [^reddit-embed-rerank-thread]

## Claims about zerank-2

- The author calls zerank-2 the best open reranker and says it was under a non-permissive license until about 16 days before the post, when Notion, having acquired ZeroEntropy, open-sourced it. The local [zerank-2 card](zerank-2.md) documents Apache-2.0; the acquisition and timing are **Reported** only.
- Commenters and the author say zerank-2 supports instruction following, which the Hugging Face card does not mention. Prepending an instruction such as "Find the X Language Translation of …" to the query is said to be what made zerank-2 "destroy anything else"; the author believes Qwen rerankers also support instructions (the [Qwen3 reranker cards](qwen3-reranker-4b.md) document this). No ablation numbers are given. [^reddit-embed-rerank-thread]

## Contested and anecdotal points in the comments

All **Reported / Unverified** practitioner opinions:

- **Public benchmark mismatch.** One commenter notes that Qwen3-Embedding-4B beats F2LLM-v2-4B on the multilingual MTEB overall and on retrieval. The wiki's [MTEB Multilingual v2 snapshot](mteb-multilingual-v2-leaderboard-snapshot.md) corroborates the aggregate gap (Qwen3-Embedding-4B 69.45 versus F2LLM-v2-4B 67.06 Mean (Task)). The author replies that F2LLM is ahead on individual languages and that Qwen3 wins public benchmarks but underperforms on bespoke tasks. [^reddit-embed-rerank-thread]
- **Alternatives named, not tested in the table:** Qwen3-VL 8B embedding/reranker as best open model; NVIDIA Nemotron-3 Embed 1B/8B (and a v2 VL embedder and VL reranker) said to "destroy" Qwen3 8B; [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md) (reported just under F2LLM-v2-4B on multilingual; the author called it an interesting candidate); gte-modernbert-base for low-VRAM use; bge-m3 with bge-reranker-v2-m3; MxBAI large on CPU. See [Nemotron-3-Embed-8B-BF16](nemotron-3-embed-8b-bf16.md) and [Qwen3-VL-Reranker-8B](qwen3-vl-reranker-8b.md).
- **Domain mismatch.** CoREB-Reranker is said to be a code-tuned reranker and zerank-2 a search-tuned one, so they target different domains; no head-to-head exists.
- **Selection advice.** One commenter advises choosing by what runs fast on your hardware, targeting 100–400 ms retrieval time, and adding reranking only after proving that tuning or upgrading the retriever does not fix the problem. The author reports the 4B stack runs near Voyage API speed at concurrency 1; no timings are given.
- **LLM-as-reranker.** One commenter uses Qwen3.5-4B-Q8_0 with a four-bucket relevance tool call as a reranker because dedicated rerankers underperformed; this is an anecdote without metrics. [^reddit-embed-rerank-thread]

## Coverage and trust limits

- Source is a single captured web discussion; the poster's handle and comments are not reproduced here. The capture's comment authors are anonymized, vote counts are not evidence, and one comment is redaction noise.
- The Chinese table was captured as HTML-rendered text; bold markers in it are the author's. No linked Hugging Face, MTEB, or ZeroEntropy pages were fetched; those claims remain unchecked.
- Use these figures only as a hypothesis for your own held-out evaluation with your languages, corpus, and latency budget; do not merge them with MTEB or vendor-reported tables.

## Relationships

- **Evaluates:** [F2LLM-v2](f2llm-v2.md) (embedder) and [zerank-2](zerank-2.md) (reranker) as the leading pair.
- **Compares with:** [Qwen3-Embedding-4B](qwen3-embedding-4b.md), [Qwen3-Reranker-4B](qwen3-reranker-4b.md), [Qwen3-Reranker-0.6B](qwen3-reranker-0-6b.md), and [Octen-Embedding-4B](octen-embedding-4b.md).
- **Contrasts with:** [MTEB Multilingual v2 leaderboard snapshot](mteb-multilingual-v2-leaderboard-snapshot.md), where Qwen3-Embedding-4B outranks F2LLM-v2-4B.
- **Complements:** [Reranker model comparison](reranker-model-comparison.md), whose table scores are publisher-reported under different protocols.

[^reddit-embed-rerank-thread]: [r/LocalLLaMA thread "Best Embedding + Reranking Model"](../raw/best_embedding_reranking_model.md) (original: reddit.com/r/LocalLLaMA/comments/1vjk57h). Locators: post body (protocol, results table, "Note" on Q8_0, closing opinions); "Comments 41" thread (Chinese table, 8B discussion, BF16 versus Q8_0, instruction-following exchange, alternative-model comments). Author-reported on proprietary data; not independently verified.
