---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md) — A 4.5B-parameter Qwen3.5-based visual document retrieval model using ColBERT-style late interaction and multilingual training data.
- [EVIE-Preview-4.5B](evie-preview-4-5b.md) — A 4.54B-parameter Qwen3.5-based multilingual visual-document retriever producing native 128-dimensional token embeddings for MaxSim late interaction.
- [LFM2.5-ColBERT-350M](lfm2-5-colbert-350m.md) — A 353M-parameter multilingual late-interaction retriever built from LFM2.5-350M-Base, producing 128-dimensional token vectors scored with MaxSim.
- [LFM2.5-Embedding-350M](lfm2-5-embedding-350m.md) — A 354M-parameter multilingual dense bi-encoder built from LFM2.5-350M-Base, producing one 1,024-dimensional CLS vector per input and scored with cosine similarity.
- [Llama-Embed-Nemotron-8B](llama-embed-nemotron-8b.md)
- [Llama-Nemotron-ColEmbed-VL-3B-v2](llama-nemotron-colembed-vl-3b-v2.md) — An approximately 4.4B-parameter SigLIP2-and-Llama-3.2-based multilingual visual-document retriever producing 3,072-dimensional token embeddings for ColBERT-style late interaction.
- [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) — An 89-entry multimodal embedding ranking snapshot whose reported overall leader is Tianmu-Emb-Uni at 52.83 and whose 13 nonzero v3 entries are also led by Tianmu-Emb-Uni at 40.50.
- [MTEB Multilingual v2 leaderboard snapshot](mteb-multilingual-v2-leaderboard-snapshot.md) — A 45-model CSV ranking snapshot for MTEB Multilingual v2, led by Qwen3-Embedding-4B at 69.45 Mean (Task). — A 7.50B-parameter Llama-3.1-8B-derived multilingual text embedding model with bidirectional attention, 4,096-dimensional outputs, and self-reported top MMTEB multilingual-v2 Borda rank in October 2025.
- [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md) — A scope-aware comparison of the wiki's 21 documented multimodal embedding checkpoints and the limited 89-entry MMEB v3 ranking snapshot.
- [Nemotron-ColEmbed-VL-8B-v2](nemotron-colembed-vl-8b-v2.md) — An approximately 8.8B-parameter Qwen3-VL-based multilingual visual-document retriever producing 4,096-dimensional token embeddings for ColBERT-style late interaction.
- [Nemotron-3-Embed-1B-BF16](nemotron-3-embed-1b-bf16.md) — A 1.14B-parameter Ministral-3-3B-derived multilingual text embedding model with 2,048-dimensional mean-pooled outputs and self-reported 72.38 RTEB NDCG@10.
- [Nemotron-3-Embed-8B-BF16](nemotron-3-embed-8b-bf16.md) — An approximately 8B-parameter Ministral-3-8B-based multilingual text embedding encoder with 4,096-dimensional mean-pooled outputs and self-reported 78.46 RTEB NDCG@10.
- [Octen-Embedding-0.6B](octen-embedding-0-6b.md) — A 0.6B-parameter Qwen3-Embedding-0.6B-derived multilingual text embedding model with 1,024-dimensional outputs, a 32,768-token context limit, and a self-reported 0.7241 RTEB public score.
- [Octen-Embedding-4B](octen-embedding-4b.md) — A 4B-parameter Qwen3-Embedding-4B-derived multilingual text embedding model with 2,560-dimensional outputs, LoRA fine-tuning, and self-reported 0.7834 RTEB Mean (Task).
- [Octen-Embedding-8B](octen-embedding-8b.md) — A Qwen3-Embedding-8B-derived multilingual text embedding model reported as 7.6B in its family table and 8B in Model Details, with 4,096-dimensional outputs and a self-reported 0.8045 RTEB Mean (Task).
- [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md) — A 4.703B-parameter Qwen2.5-Omni Thinker-based multimodal bi-encoder for text, image, audio, and video retrieval, producing 2,048-dimensional embeddings.
- [Qwen3-Embedding-0.6B](qwen3-embedding-0-6b.md) — A 0.6B-parameter Qwen3 multilingual text embedding model with 28 layers, a 32K-token context limit, 1,024-dimensional Matryoshka embeddings, and reported June 2025 MMTEB results.
- [Qwen3-Embedding-4B](qwen3-embedding-4b.md) — A 4B-parameter Qwen3 multilingual text embedding model with 36 layers, a 32K-token context limit, 2,560-dimensional Matryoshka embeddings, and reported leading June 2025 MMTEB results.
- [Qwen3-Embedding-8B](qwen3-embedding-8b.md) — An 8B-parameter Qwen3-based multilingual text embedding model with 36 layers, causal-attention EOS pooling, 4,096-dimensional Matryoshka embeddings, and reported leading June 2025 MTEB results.
- [Qwen3-VL, harrier, Qwen3, F2LLM, and Jina embedding comparison](embedding-model-comparison-qwen3-vl-harrier-qwen3-f2llm.md) — A scope-aware comparison of Qwen3-VL-Embedding-2B, harrier-oss-v1-0.6b, Qwen3-Embedding-4B and 0.6B, F2LLM-v2-4B, and Jina Embeddings v5 Text Small.
- [Querit-Reranker](querit-reranker.md) — A multilingual MoE text reranker with 4.92B total parameters, 0.43B active parameters, 24 layers, and a 128K-token context limit.
- [Qwen3-Reranker-0.6B](qwen3-reranker-0-6b.md) — A 0.6B-parameter, 28-layer Qwen3 point-wise reranker with a 32K-token context limit and reported June 2025 retrieval and instruction-following results.
- [Qwen3-Reranker-4B](qwen3-reranker-4b.md) — A 4B-parameter, 36-layer Qwen3 point-wise reranker with a 32K-token context limit and reported June 2025 retrieval and instruction-following results.
- [Qwen3-Reranker-8B](qwen3-reranker-8b.md) — An Apache-2.0 8B-parameter, 36-layer Qwen3 point-wise reranker with 32K-token context, 100+ language support, configurable instructions, and reported June 2025 retrieval results.
- [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) — A 2B-parameter, 28-layer Qwen3-VL-based multimodal embedding model with 32K context, 64–2,048-dimensional outputs, 30+ language support, and reported MMEB-V2 and MMTEB results.
- [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) — An 8B-parameter, 36-layer Qwen3-VL-based multimodal embedding model with 32K context, 64–4,096-dimensional outputs, 30+ language support, and reported MMEB-V2 and MMTEB results.
- [Qwen3-VL-Reranker-2B](qwen3-vl-reranker-2b.md) — An Apache-2.0 2B-parameter, 28-layer instruction-aware multimodal cross-encoder reranker with a 32K context limit and binary yes/no relevance scoring.
- [Qwen3-VL-Reranker-8B](qwen3-vl-reranker-8b.md) — An Apache-2.0 8B-parameter, 36-layer instruction-aware multimodal cross-encoder reranker with a 32K context limit and binary yes/no relevance scoring.
- [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md) — An 8B-scale unified multimodal embedding model combining a Qwen3-VL embedding backbone with a Qwen2.5-Omni audio tower, producing 3,584-dimensional vectors and reporting 53.27 across 190 MMEB-V3 tasks.
- [Tomoro ColQwen3 Embed 4B](tomoro-colqwen3-embed-4b.md) — A 4B-class Qwen3-VL-based multilingual multimodal late-interaction retriever with 320-dimensional token embeddings and reported ViDoRe and video-retrieval results.
- [Tomoro ColQwen3 Embed 8B](tomoro-colqwen3-embed-8b.md) — An 8B-class Qwen3-VL-based multilingual multimodal late-interaction retriever with 320-dimensional token embeddings and self-reported ViDoRe and video-retrieval results.
- [UEmbed](uembed.md) — A 2B, 4B, and 9B Qwen3.5 multimodal embedding family that emits dense and learned-sparse vectors from one causal forward pass.
- [UEmbed-4B](uembed-4b.md) — A 4B-parameter Qwen3.5-based decoder-only multimodal embedding model producing dense and SPLADE-style sparse vectors, with reported MMEB-v3 results.
- [Vintern-Embedding-1B](vintern-embedding-1b.md) — A reported 0.9B-parameter Vietnamese, English, and Chinese multimodal multi-vector embedding model built on Vintern-1B-v3_5 and trained on more than 1.5M VQA and text-QA pairs.
- [webAI-ColVec1.1-4b](webai-colvec1-1-4b.md) — A 4.54B-parameter Qwen3.5-based multilingual visual-document retriever producing 640-dimensional token embeddings for ColBERT-style MaxSim late interaction.
- [webAI-ColVec1.1-8b](webai-colvec1-1-8b.md) — An 8.40B-parameter Qwen3.5-based multilingual visual-document retriever producing 640-dimensional token embeddings for ColBERT-style MaxSim late interaction.
- [XProvence-reranker](xprovence-reranker.md) — A 568M-parameter multilingual BGE-M3-derived model that jointly prunes irrelevant sentences from retrieved passages and supplies reranking scores for RAG question answering.
- [zerank-2](zerank-2.md) — A 4B-parameter Apache-2.0 Qwen3-4B-based text reranker with a 32,768-token context limit and raw-logit Sentence Transformers scoring.
- [mLateOn](mlateon.md) — A 307M-parameter mmBERT-base multilingual ColBERT retriever with 128-dimensional token vectors, MaxSim scoring, and an 8,192-token context limit.
- [mmBERT-small](mmbert-small.md) — A 140M-parameter ModernBERT-based multilingual masked-language encoder covering 1,800+ languages, with an 8,192-token context window and 256,000-token Gemma 2 vocabulary.
- [DEk21_hcmute_embedding](dek21-hcmute-embedding.md) — A Vietnamese legal-text embedding model built from a RoBERTa sentence-transformer with 768-dimensional Matryoshka embeddings and mean pooling.
- [DeepX Embedding v1.0](deepx-embedding-v1.md) — A 772M-parameter Vietnamese legal retrieval embedding model using Gated DeltaNet-2 linear attention, Hyperloop weight sharing, and 256–1536-dimensional Matryoshka embeddings.
- [e5-omni](e5-omni.md) — A Qwen2.5-Omni-based 3B/7B omni-modal embedding family that uses explicit temperature, negative-selection, and covariance alignment during contrastive training.
- [EmbeddingGemma 300M](embeddinggemma-300m.md) — A 300M-parameter Gemma 3-based multilingual text embedding model with 768-dimensional Matryoshka embeddings and on-device deployment focus.
- [ettin-reranker-68m-v1](ettin-reranker-68m-v1.md) — A 68.6M-parameter English cross-encoder reranker with a 7,999-token maximum sequence length, trained on 143.4M query–document pairs.
- [F2LLM-v2](f2llm-v2.md) — An eight-size, Qwen3-based multilingual embedding family trained on a reported 60 million samples in 282 natural and 40+ programming languages.
- [F2LLM-v2-14B](f2llm-v2-14b.md) — A 13.99B-parameter F2LLM-v2 embedding model with 5,120-dimensional EOS-pooled Matryoshka embeddings and author-reported results on 17 MTEB benchmarks.
- [GELATO](gelato.md) — A frozen-tower method for extending an existing text embedding space to image, video, and audio using small, task-specific modality projectors.
- [Granite Embedding 311M Multilingual R2](granite-embedding-311m-multilingual-r2.md) — A 311M-parameter ModernBERT bi-encoder for multilingual text and code retrieval, with 768-dimensional Matryoshka embeddings and a 32,768-token context window.
- [Granite Embedding 97M Multilingual R2](granite-embedding-97m-multilingual-r2.md) — A 97M-parameter ModernBERT bi-encoder for multilingual text and code retrieval, with 384-dimensional embeddings and a 32,768-token context window.
- [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md) — A 0.6B-parameter multilingual decoder-only embedding model with 1,024-dimensional, last-token-pooled normalized outputs and a reported 69.0 Multilingual MTEB v2 score.
- [harrier-oss-v1-270m](harrier-oss-v1-270m.md) — A 270M-parameter multilingual decoder-only embedding model with 640-dimensional, last-token-pooled normalized outputs and a reported 66.5 Multilingual MTEB v2 score.
- [Jina Code Embeddings 0.5B](jina-code-embeddings-0-5b.md) — A Qwen2.5-Coder-0.5B-based code-retrieval embedding model with 896-dimensional last-token-pooled vectors, 32,768-token inputs, and stated support for 15+ programming languages.
- [Jina Code Embeddings 1.5B](jina-code-embeddings-1-5b.md) — A Qwen2.5-Coder-1.5B-based code-retrieval embedding model with 1,536-dimensional last-token-pooled vectors, 32,768-token inputs, and stated support for 15+ programming languages.
- [jina-reranker-v3](jina-reranker-v3.md) — A deprecated 0.6B-parameter multilingual listwise document reranker that jointly scores a query and up to 64 documents in a 131K-token context.
- [jina-reranker-v3.5](jina-reranker-v3-5.md) — A 0.6B-parameter multilingual listwise reranker with 131K-token context, 3L2G hybrid attention, and reported gains in general, domain, structured, and multilingual retrieval.
- [Jina Embeddings v4](jina-embeddings-v4.md) — A Qwen2.5-VL-3B-Instruct-based multimodal, multilingual embedding model offering dense and late-interaction retrieval outputs with task-selectable adapters.
- [Jina Embeddings v5 Omni Nano](jina-embeddings-v5-omni-nano.md) — An approximately 1B-parameter multimodal embedding model with locked aligned modality towers, 768-dimensional last-token-pooled vectors, and text, image, video, and audio support.
- [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md) — A reported 1.74B-parameter multimodal embedding model with locked aligned modality towers, 1,024-dimensional last-token-pooled vectors, and text, image, video, and audio support.
- [Jina Embeddings v5 Text Nano](jina-embeddings-v5-text-nano.md) — A 239M-parameter EuroBERT-210M-based multilingual text embedding model with 768-dimensional last-token-pooled, Matryoshka-truncatable vectors.
- [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md) — A 677M-parameter Qwen3-0.6B-based multilingual text embedding model with 1,024-dimensional last-token-pooled Matryoshka vectors and a 32,768-token input limit.
- [KaLM-Embedding-Gemma3-12B-2511](kalm-embedding-gemma3-12b-2511.md) — An 11.76B-parameter Gemma 3-derived embedding model with 3,840-dimensional last-token-pooled Matryoshka outputs and self-reported top MMTEB rank as of November 2025.
