---
language:
  - vi
  - en
license: apache-2.0
tags:
  - feature-extraction
  - sentence-similarity
  - embedding
  - retrieval
  - vietnamese
  - legal
  - linear-attention
  - gated-deltanet
  - sentence-transformers
  - matryoshka
datasets:
  - unicamp-dl/mmarco
  - miracl/miracl
  - GreenNode/zalo-ai-legal-text-retrieval-vn
metrics:
  - ndcg_at_10
pipeline_tag: sentence-similarity
model-index:
  - name: DeepX Embedding v1.0
    results:
      - task:
          type: Retrieval
        dataset:
          name: Zalo Legal Text Retrieval
          type: GreenNode/zalo-ai-legal-text-retrieval-vn
        metrics:
          - type: ndcg_at_10
            value: 0.8162
          - type: mrr_at_10
            value: 0.7672
          - type: recall_at_10
            value: 0.9537
---

# DeepX Embedding v1.0

**Vietnamese Legal Document Retrieval — State-of-the-Art**

🌐 [Blog Post](https://dxtech.jp/deepx-embedding-v1-0-setting-a-new-sota-in-vietnamese-legal-retrieval/) | 💻 [GitHub](https://github.com/dx-tech-ai/deepx-embed)

DeepX Embedding v1.0 is a 772M parameter embedding model optimized for Vietnamese legal document retrieval. It combines Gated DeltaNet-2 linear attention (O(n)) with Hyperloop weight sharing to achieve strong retrieval quality while maintaining constant throughput regardless of sequence length.

**nDCG@10 = 0.8162** on Zalo Legal Text Retrieval — surpassing previous SOTA (0.7813) by +4.5%.

---

## Benchmark Results

| Model | Params | nDCG@10 |
|-------|--------|---------|
| intfloat/multilingual-e5-large | 560M | 0.6660 |
| mainguyen9/vietlegal-e5 | 560M | 0.7310 |
| mainguyen9/vietlegal-harrier-0.6b (prev SOTA) | 600M | 0.7813 |
| **DeepX Embedding v1.0** | **772M** | **0.8162** |

---

## Key Features

- **Linear attention O(n)** — Gated DeltaNet-2: processes 8K tokens with same VRAM as 512 tokens
- **Hyperloop architecture** — 35 compute passes from only 9 unique layer parameter sets
- **Matryoshka embeddings** — Quality at any dimension from 256d to 1536d

| Dimension | nDCG@10 | Quality vs Full |
|-----------|---------|-----------------|
| 256 | 0.78 | ~96% |
| 512 | 0.79 | ~97% |
| 768 | 0.80 | ~98% |
| 1024 | 0.81 | ~99% |
| 1536 (full) | 0.8162 | 100% |

- **ColBERT dual output** — Single vector (1536d) for ANN search + token vectors (128d) for MaxSim reranking
- **Custom vocabulary** — 186,046 tokens optimized for Vietnamese + English
- **YaRN RoPE** — 8K tokens validated, 128K supported

---

## Architecture

```
Input text
  → Custom Tokenizer (186,046 vocab)
  → Frozen Token Embedding (186046 × 1536)
  → Begin Block: 4 unique NarrowA layers
  → Phase1 Loop ×2: [WideA + NarrowA×4] per iteration = 10 passes
  → Phase2 Loop ×4: [NarrowB×4 + WideB] per iteration = 20 passes
  → End Block: 1 unique WideB layer
  → RMSNorm → Attention Pooling → 1536-d vector
```

Total: 35 compute passes. Per-loop LoRA + RoDE (Rotary Depth Embedding) differentiate each iteration.

### Model Size

| Component | Parameters |
|-----------|-----------|
| Token Embedding (frozen) | 286M |
| Backbone (trainable) | 486M |
| **Total** | **772M** |

---

## Gated DeltaNet-2 (GDN-2)

Pure linear attention with O(n) complexity. Each layer maintains a running state updated via learned decay, erase, and write gates:

```
state_t = decay_t * state_{t-1}
state_t -= erase_t * (erase_t @ state_t - write_t * v_t)
output_t = q_t @ state_t
```

No KV cache, no quadratic slowdown. Uses FLA (flash-linear-attention) Triton kernels for efficient chunk-parallel training.

---

## Training

| Setting | Value |
|---------|-------|
| GPUs | 2× RTX 5070 Ti 16GB (pipeline parallel) |
| Precision | BF16 |
| Optimizer | AdamW 8-bit |
| Sequence length | 8192 max |
| Loss | InfoNCE (τ=0.07) + Matryoshka (256, 512, 768, 1024, 1536) |
| Total training | ~600 GPU-hours |

Training pipeline: conservative training → long-sequence expose (4K-8K) → hard negative mining → domain boost.

---

## Usage

```python
import torch
from transformers import AutoTokenizer
from modeling.pipeline import DeepXPipeline
from config import DeepXConfig

# Load
tokenizer = AutoTokenizer.from_pretrained("dxtech-asia/deepx-embedding-v1")
config = DeepXConfig()
pipeline = DeepXPipeline.from_pretrained(config, "deepx_v1.0.pt")
pipeline.eval().cuda()

# Encode
text = "Mức phạt khi vượt đèn đỏ là bao nhiêu?"
inputs = tokenizer(text, return_tensors="pt", max_length=8192, truncation=True)
id_remap = torch.load("id_remap.pt")
input_ids = id_remap[inputs["input_ids"]]

with torch.no_grad():
    embedding = pipeline.encode(input_ids.cuda(), inputs["attention_mask"].cuda())
    # Shape: (1, 1536), L2-normalized
```

---

## Inference Speed

| Sequence Length | Latency (single doc) |
|----------------|---------------------|
| 512 tokens | ~0.1s |
| 2048 tokens | ~0.2s |
| 8192 tokens | ~0.8s |

On RTX 5070 Ti, FP16 inference.

---

## Citation

```bibtex
@misc{deepx2026embedding,
  title={DeepX Embedding v1.0: Vietnamese Legal Retrieval with Gated DeltaNet-2 Linear Attention},
  author={DX Tech Asia},
  year={2026},
  url={https://huggingface.co/dxtech-asia/deepx-embedding-v1}
}
```

## License

Apache 2.0
