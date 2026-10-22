---
type: Concept
title: EmbeddingGemma 2
description: A 740M-parameter Gemma 4-based open multimodal embedding model mapping text, code, images, video, and audio into one 768-dimensional Matryoshka space with selectively loadable modality encoders.
tags: [embedding, multimodal, matryoshka, gemma, on-device, audio, video]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T03:20:00Z }
sources:
  - id: embeddinggemma-2-card
    resource: ../raw/embeddinggemma-2.md
    kind: model-card
    title: EmbeddingGemma 2 model card
---

# EmbeddingGemma 2

EmbeddingGemma 2 is a Google DeepMind open embedding model that places text (including code), images, video, audio, and interleaved combinations of them in a single 768-dimensional vector space. It totals 740M parameters: a 270M text model (130M transformer backbone plus 140M embedder), a 170M vision encoder, and a 300M audio encoder. The card positions it for on-device search, RAG, classification, and clustering, and says it builds on Gemma 4. All figures below are **Reported** (vendor model card, no independent check).[^embeddinggemma-2-card]

## Architecture and specifications

| Item | Value |
|---|---|
| Parameters | 740M total; backbone 130M, embedder 140M, vision 170M, audio 300M |
| Text stack | 24 layers, model dim 512, hidden dim 2048, 4 heads, KV-heads 2 (local) / 1 (global), local:global 5:1, 1,024-token sliding window, GQA/MQA, gated FFN with GELU, vocabulary 262,144 |
| Pooling / projection | Mean pooling; 512→768 projection |
| Output | 768 dimensions native; MRL truncation to 512, 256, 128 |
| Context | 8,192 tokens shared across all modalities |
| Modalities | Text, images, video, audio |
| License | Apache 2.0 (front matter and header); the header's license link points to a Gemma 4 license page, and deployments must follow the Gemma Prohibited Use Policy |
| Languages | 100+ understood; training text covers 140+ languages; per-language parity is not claimed |

Source: Model Overview table and header.[^embeddinggemma-2-card]

## Benchmarks (768d, vendor-reported)

Scores are for the full-precision checkpoint. The card gives aggregate metrics only, no task-level results or evaluation protocol. Benchmark versions differ (for example MTEB multilingual v2, code v1, MMEB v2); do not mix with other versions. [^embeddinggemma-2-card]

| Modality | Benchmark | Metric | EmbeddingGemma 2 | EmbeddingGemma 1 |
|---|---|---|---:|---:|
| Text | MTEB multilingual v2 | Mean (Task) | 61.36 | 61.15 |
| Text | MTEB code v1 | Mean (Task), NDCG@10 | 78.68 | 68.76 |
| Image | MIEB lite | Mean (TaskType) | 64.64 | – |
| Image | MMEB v2 Image | Hit@1 | 57.28 | – |
| Visual document | MMEB v2 VisDoc | NDCG@5 | 67.84 | – |
| Video | MMEB v2 Video | Hit@1 | 50.67 | – |
| Audio | MSEB retrieval | MRR@10 | 69.54 | – |
| Audio | MAEB | Mean (Task) | 49.39 | – |

The text gain is small on multilingual v2 (+0.21) and large on code (+9.92 NDCG@10; the card's "~14% improvement" is consistent with the relative gain). The truncation table lists MTEB English v2 at 68.46 for the 768d vector; the [EmbeddingGemma 300M](embeddinggemma-300m.md) concept records 69.67 for its predecessor on the same benchmark, so English v2 appears slightly lower (Synthesis; the card makes no such comparison). [^embeddinggemma-2-card]

### Matryoshka truncation

Truncated vectors must be re-normalized. The card reports the following Mean (Task) values (MMEB v2 is Overall). [^embeddinggemma-2-card]

| Dim | Ratio | MTEB multi v2 | MTEB eng v2 | MTEB code v1 | MIEB lite | MMEB v2 | MSEB retr. | MAEB |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 768 | 1:1 | 61.36 | 68.46 | 78.68 | 64.64 | 59.01 | 69.54 | 49.39 |
| 512 | 1:1.5 | 61.17 | 68.41 | 77.24 | 64.32 | 58.38 | 69.18 | 49.21 |
| 256 | 1:3 | 60.41 | 67.78 | 76.18 | 63.13 | 56.24 | 66.76 | 48.91 |
| 128 | 1:6 | 57.89 | 65.68 | 71.41 | 59.06 | 45.65 | 56.71 | 46.92 |

Quality is near-lossless to 256d; 128d suits text-only work, while MMEB v2 falls 13.4 points and MSEB 12.8 points, so validate on your own workload. (The card's "up to 6x" storage reduction corresponds to 128d.) [^embeddinggemma-2-card]

## Usage rules

- **Task prefixes (text only).** Asymmetric tasks use a query prefix and a document prefix; symmetric tasks use the same prefix for all inputs. Prompt names: `SearchQuery` (`task: search result | query: {query}`), `QuestionAnswering`, `FactChecking`, `CodeRetrieval`, `Classification`, `Clustering`, `SentenceSimilarity`. Documents are formatted `title: {title} | text: {content}`, or `title: none`. `prompt_name="Document"` applies `title: none` only; titled documents must be formatted manually. Images, video, and audio take no prefix. Omitting prefixes still works but lowers precision. [^embeddinggemma-2-card]
- **Truncation.** Re-normalize after slicing (silent quality loss otherwise); queries and documents must share a dimension. Use `truncate_dim` with `normalize_embeddings=True` in Sentence Transformers. [^embeddinggemma-2-card]
- **Precision.** Use `bfloat16` or `float32`; **never `float16`**, whose range is exceeded and yields NaN or silently degraded embeddings. The same constraint applies to [EmbeddingGemma 300M](embeddinggemma-300m.md). [^embeddinggemma-2-card]
- **Selective loading.** Modality encoders are independent and can be disabled via `config_kwargs` (support varies by library): text only 270M, text+image 440M, text+audio 570M, full 740M. [^embeddinggemma-2-card]

## Multimodal input

An input may interleave text with media using placeholder tokens `<|image|>`, `<|video|>`, `<|audio|>`; each placeholder is filled in order from the matching key and one embedding is returned for the whole input, comparable with any other EmbeddingGemma 2 embedding (for example a text-only query). All modalities consume the single 8,192-token budget: [^embeddinggemma-2-card]

| Modality | Default token cost | Approx. max alone |
|---|---|---|
| Text | 1 per subword | 8,192 tokens |
| Image | 280 per image | ~29 images |
| Video | 140 per frame (1 fps default, configurable) | ~58 frames |
| Audio | 25 per second (mono, 16 kHz) | ~327 s |

A configurable vision "soft token" budget of 70–1,120 per image or frame trades latency for fine-grained quality; at the lowest budget up to ~114 images or frames fit. Mixed inputs share the budget, so each modality fits less. [^embeddinggemma-2-card]

## Training data and safety

Pre-training data (cutoff January 2025) spans web documents (140+ languages), code, images, video, audio, and cross-modality paired samples. Filtering covers CSAM, certain personal/sensitive data, and quality and safety. The card states there is no post-training alignment or output moderation; dataset names, mixture proportions, token counts, and the training objective are not disclosed. [^embeddinggemma-2-card]

## Limitations and coverage

- Self-reported benchmarks, aggregates only; "among the strongest multimodal embedding models under 1B parameters" is an unsupported vendor claim.
- Language performance is uneven by the card's own statement; no per-language results.
- No comparisons to other multimodal embedding models, so it is not placed in the [multimodal embedding model comparison](multimodal-embedding-model-comparison.md) or MMEB ranking snapshots here.
- Training recipe, loss, and hardware are not documented; only the model card (`../raw/embeddinggemma-2.md`) was inspected, statically. Linked blog, GitHub, and documentation pages were not captured. The header's "Apache 2.0" label alongside a Gemma 4 license link is an unresolved inconsistency; check the upstream license before use.

## Relationships

- Successor generation to: [EmbeddingGemma 300M](embeddinggemma-300m.md), a text-only 300M model; the card reports it as "EmbeddingGemma 1" in its comparison column. [^embeddinggemma-2-card]
- Comparable in scope to the omni-modal [Jina Embeddings v5 Omni Nano](jina-embeddings-v5-omni-nano.md) (text, image, video, audio, 768d, removable towers) — no shared benchmark in the sources. (Synthesis)

[^embeddinggemma-2-card]: [EmbeddingGemma 2 model card](../raw/embeddinggemma-2.md), header, Model Overview, Benchmark Results, Best Practices §1–5, Model Data, Usage and Limitations. Vendor-authored; no revision recorded.
