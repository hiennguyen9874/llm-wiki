---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md) — A 4.5B-parameter Qwen3.5-based visual document retrieval model using ColBERT-style late interaction and multilingual training data.
- [LFM2.5-ColBERT-350M](lfm2-5-colbert-350m.md) — A 353M-parameter multilingual late-interaction retriever built from LFM2.5-350M-Base, producing 128-dimensional token vectors scored with MaxSim.
- [LFM2.5-Embedding-350M](lfm2-5-embedding-350m.md) — A 354M-parameter multilingual dense bi-encoder built from LFM2.5-350M-Base, producing one 1,024-dimensional CLS vector per input and scored with cosine similarity.
- [Llama-Embed-Nemotron-8B](llama-embed-nemotron-8b.md)
- [MTEB Multilingual v2 leaderboard snapshot](mteb-multilingual-v2-leaderboard-snapshot.md) — A 45-model CSV ranking snapshot for MTEB Multilingual v2, led by Qwen3-Embedding-4B at 69.45 Mean (Task). — A 7.50B-parameter Llama-3.1-8B-derived multilingual text embedding model with bidirectional attention, 4,096-dimensional outputs, and self-reported top MMTEB multilingual-v2 Borda rank in October 2025.
- [Nemotron-3-Embed-1B-BF16](nemotron-3-embed-1b-bf16.md) — A 1.14B-parameter Ministral-3-3B-derived multilingual text embedding model with 2,048-dimensional mean-pooled outputs and self-reported 72.38 RTEB NDCG@10.
- [Nemotron-3-Embed-8B-BF16](nemotron-3-embed-8b-bf16.md) — An approximately 8B-parameter Ministral-3-8B-based multilingual text embedding encoder with 4,096-dimensional mean-pooled outputs and self-reported 78.46 RTEB NDCG@10.
- [Octen-Embedding-0.6B](octen-embedding-0-6b.md) — A 0.6B-parameter Qwen3-Embedding-0.6B-derived multilingual text embedding model with 1,024-dimensional outputs, a 32,768-token context limit, and a self-reported 0.7241 RTEB public score.
- [Octen-Embedding-4B](octen-embedding-4b.md) — A 4B-parameter Qwen3-Embedding-4B-derived multilingual text embedding model with 2,560-dimensional outputs, LoRA fine-tuning, and self-reported 0.7834 RTEB Mean (Task).
- [Octen-Embedding-8B](octen-embedding-8b.md) — A Qwen3-Embedding-8B-derived multilingual text embedding model reported as 7.6B in its family table and 8B in Model Details, with 4,096-dimensional outputs and a self-reported 0.8045 RTEB Mean (Task).
- [Qwen3-Embedding-8B](qwen3-embedding-8b.md) — An 8B-parameter Qwen3-based multilingual text embedding model with 36 layers, causal-attention EOS pooling, 4,096-dimensional Matryoshka embeddings, and reported leading June 2025 MTEB results.
- [Vintern-Embedding-1B](vintern-embedding-1b.md) — A reported 0.9B-parameter Vietnamese, English, and Chinese multimodal multi-vector embedding model built on Vintern-1B-v3_5 and trained on more than 1.5M VQA and text-QA pairs.
- [mLateOn](mlateon.md) — A 307M-parameter mmBERT-base multilingual ColBERT retriever with 128-dimensional token vectors, MaxSim scoring, and an 8,192-token context limit.
- [mmBERT-small](mmbert-small.md) — A 140M-parameter ModernBERT-based multilingual masked-language encoder covering 1,800+ languages, with an 8,192-token context window and 256,000-token Gemma 2 vocabulary.
- [DEk21_hcmute_embedding](dek21-hcmute-embedding.md) — A Vietnamese legal-text embedding model built from a RoBERTa sentence-transformer with 768-dimensional Matryoshka embeddings and mean pooling.
- [DeepX Embedding v1.0](deepx-embedding-v1.md) — A 772M-parameter Vietnamese legal retrieval embedding model using Gated DeltaNet-2 linear attention, Hyperloop weight sharing, and 256–1536-dimensional Matryoshka embeddings.
- [EmbeddingGemma 300M](embeddinggemma-300m.md) — A 300M-parameter Gemma 3-based multilingual text embedding model with 768-dimensional Matryoshka embeddings and on-device deployment focus.
- [F2LLM-v2-14B](f2llm-v2-14b.md) — A 14B-parameter instruct embedding model in the multilingual F2LLM-v2 family, with 5,120-dimensional normalized embeddings and claimed support for more than 200 languages.
- [Granite Embedding 311M Multilingual R2](granite-embedding-311m-multilingual-r2.md) — A 311M-parameter ModernBERT bi-encoder for multilingual text and code retrieval, with 768-dimensional Matryoshka embeddings and a 32,768-token context window.
- [Granite Embedding 97M Multilingual R2](granite-embedding-97m-multilingual-r2.md) — A 97M-parameter ModernBERT bi-encoder for multilingual text and code retrieval, with 384-dimensional embeddings and a 32,768-token context window.
- [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md) — A 0.6B-parameter multilingual decoder-only embedding model with 1,024-dimensional, last-token-pooled normalized outputs and a reported 69.0 Multilingual MTEB v2 score.
- [harrier-oss-v1-270m](harrier-oss-v1-270m.md) — A 270M-parameter multilingual decoder-only embedding model with 640-dimensional, last-token-pooled normalized outputs and a reported 66.5 Multilingual MTEB v2 score.
- [Jina Code Embeddings 0.5B](jina-code-embeddings-0-5b.md) — A Qwen2.5-Coder-0.5B-based code-retrieval embedding model with 896-dimensional last-token-pooled vectors, 32,768-token inputs, and stated support for 15+ programming languages.
- [Jina Code Embeddings 1.5B](jina-code-embeddings-1-5b.md) — A Qwen2.5-Coder-1.5B-based code-retrieval embedding model with 1,536-dimensional last-token-pooled vectors, 32,768-token inputs, and stated support for 15+ programming languages.
- [Jina Embeddings v4](jina-embeddings-v4.md) — A Qwen2.5-VL-3B-Instruct-based multimodal, multilingual embedding model offering dense and late-interaction retrieval outputs with task-selectable adapters.
- [Jina Embeddings v5 Text Nano](jina-embeddings-v5-text-nano.md) — A 239M-parameter EuroBERT-210M-based multilingual text embedding model with 768-dimensional last-token-pooled, Matryoshka-truncatable vectors.
- [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md) — A 677M-parameter Qwen3-0.6B-based multilingual text embedding model with 1,024-dimensional last-token-pooled Matryoshka vectors and a 32,768-token input limit.
- [KaLM-Embedding-Gemma3-12B-2511](kalm-embedding-gemma3-12b-2511.md) — An 11.76B-parameter Gemma 3-derived embedding model with 3,840-dimensional last-token-pooled Matryoshka outputs and self-reported top MMTEB rank as of November 2025.
