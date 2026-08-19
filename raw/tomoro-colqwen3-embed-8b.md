---
license: apache-2.0
license_name: apache-2.0
license_link: https://www.apache.org/licenses/LICENSE-2.0
tags:
- sentence-transformers
- multi-vector
- text
- image
- video
- multimodal-embedding
- vidore
- colpali
- colqwen3
- multilingual-embedding
language:
- multilingual
library_name: transformers
pipeline_tag: visual-document-retrieval
base_model:
- Qwen/Qwen3-VL-8B-Instruct
---

# TomoroAI/tomoro-colqwen3-embed-8b

## ⚡ Executive Summary

**TomoroAI/tomoro-colqwen3-embed-8b** is a state-of-the-art [ColPali](https://arxiv.org/abs/2407.01449)-style multimodal embedding model. It maps text queries, visual documents (images, PDFs) or short videos into aligned multi-vector embeddings.

Built by merging **[Qwen/Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct)** with **[Qwen/Qwen3-Embedding-8B](https://huggingface.co/Qwen/Qwen3-Embedding-8B)**, this model inherits robust text retrieval capabilities while preserving a full vision stack. It has been fine-tuned on a curated mixture of [VDR](https://huggingface.co/datasets/vdr-multilingual-train), [ViDoRe-ColPali-Training](https://huggingface.co/datasets/vidore/colpali_train_set), [VisRAG-Ret-Train-Synthetic-data](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-Synthetic-data), and [VisRAG-Ret-Train-In-domain-data](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-In-domain-data). It achieves SOTA or competitive performance across **ViDoRe V1-V3** (English and Multilingual) while offering a significantly reduced embedding footprint compared to other full-dim Colpali model alternatives.

## 🛠️ Model Specifications

| Feature | Detail |
| :--- | :--- |
| **Architecture** | Qwen3-VL 8B (Encoder-only variant) + 320-dim Projection Head |
| **Methodology** | ColPali-style Late Interaction (MaxSim scoring) |
| **Token Budget** | Up to 1,280 visual tokens per page or 5120 visual tokens per video (text prompts constrained only by the base context window) |
| **Context Window** | 32k (inherited from base), typical usage < 2k tokens |
| **Output** | Multi-vector (Seq_Len × 320), L2-normalized |
| **Supported Modalities** | Text Queries, RGB Images, Synthetic Documents, Short Video (Frame-wise) |
| **Precision** | `bfloat16` weights, FlashAttention 2 enabled |



### Key Properties

* **Merged Encoders:** Combines the Qwen3-VL vision encoder (patch-grid tokens with spatial merge) and language encoder.
* **Projection:** A custom 320-dim head projects every token (text or visual) into a vector.
* **Processing:**
    * **Queries:** Left-padded text sequences.
    * **Documents:** Rendered with a lightweight vision prompt and flattened into image tokens.
    * **Video:** Supports video retrieval by decoding videos into frames and processing via the vision stack (generalization capability, not explicitly fine-tuned; dedicated benchmark coming soon).
* **Storage Efficiency:**
    * *Baseline (NVIDIA Nemo-3B):* Stores 1,802 tokens @ 3,072 dims (≈10.3 TB for 1M images).
    * *Tomoro ColQwen3:* Stores max 1,280 tokens @ 320 dims (**≈0.82 TB for 1M images**).
    * **Result:** **13× smaller footprint** with higher performance.

---

## 📊 Evaluation Results

We report results on the **ViDoRe** benchmark suite. The model sets new standards on multilingual and English splits on ViDoRe V2 and V3 while maintaining comparable high performance on ViDoRe V1.

### ViDoRe V3 (Latest)

**English nDCG@5**
| Model | CompSci | Energy | FinanceEn | FinanceFr | HR | Industrial | Pharma | Physics | **Avg** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[tomoro-colqwen3-8b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-8b)** | 0.7443 | **0.6491** | **0.6823** | **0.4546** | **0.6421** | 0.5766 | **0.6665** | **0.4747** | **0.6113** |
| [tomoro-colqwen3-4b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-4b) | 0.7419 | 0.6023 | 0.6753 | 0.4202 | 0.6037 | **0.5787** | 0.6612 | 0.4640 | 0.5934 |
| [nemo-colembed-3b](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1) | 0.7514 | 0.5838 | 0.6712 | 0.3730 | 0.6256 | 0.5447 | 0.6524 | 0.4128 | 0.5769 |
| [jinaai/jina-embeddings-v4](https://huggingface.co/jinaai/jina-embeddings-v4) | 0.7175 | 0.5842 | 0.6417 | 0.3859 | 0.6206 | 0.5443 | 0.6303 | 0.4191 | 0.5680 |
| [nomic-ai/colnomic-embed-multimodal-7b](https://huggingface.co/nomic-ai/colnomic-embed-multimodal-7b) | **0.7528** | 0.5824 | 0.6041 | 0.3877 | 0.6060 | 0.5229 | 0.6226 | 0.4423 | 0.5651 |

**Multilingual nDCG@5** (Excluding English Subsets)
| Model | CompSci | Energy | FinanceEn | FinanceFr | HR | Industrial | Pharma | Physics | **Avg** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[tomoro-colqwen3-8b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-8b)** | 0.7194 | **0.6619** | **0.6172** | **0.4570** | **0.6097** | **0.5164** | **0.6403** | **0.4706** | **0.5866** |
| [tomoro-colqwen3-4b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-4b) | 0.7213 | 0.6374 | 0.6019 | 0.4305 | 0.5637 | 0.5131 | 0.6351 | 0.4636 | 0.5708 |
| [nemo-colembed-3b](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1) | 0.7216 | 0.5901 | 0.5646 | 0.4102 | 0.5504 | 0.4335 | 0.6170 | 0.4192 | 0.5383 |
| [jinaai/jina-embeddings-v4](https://huggingface.co/jinaai/jina-embeddings-v4) | 0.6843 | 0.6036 | 0.5482 | 0.4249 | 0.5542 | 0.4732 | 0.6059 | 0.4381 | 0.5416 |
| [nomic-ai/colnomic-embed-multimodal-7b](https://huggingface.co/nomic-ai/colnomic-embed-multimodal-7b) | **0.7333** | 0.6160 | 0.5219 | 0.4169 | 0.5494 | 0.4764 | 0.5938 | 0.4449 | 0.5441 |

### ViDoRe V2

**English nDCG@5**
| Model | BioMed | ESG HL | ESG Rpts | Economics | **Avg** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[tomoro-colqwen3-8b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-8b)** | **0.6784** | **0.7598** | **0.6549** | 0.6159 | **0.6772** |
| [tomoro-colqwen3-4b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-4b) | 0.6718 | 0.7465 | 0.6300 | 0.5910 | 0.6598 |
| [nemo-colembed-3b](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1) | 0.6518 | 0.7538 | 0.6030 | **0.6619** | 0.6676 |
| [jinaai/jina-embeddings-v4](https://huggingface.co/jinaai/jina-embeddings-v4) | 0.6359 | 0.6512 | 0.5194 | 0.5955 | 0.6005 |
| [nomic-ai/colnomic-embed-multimodal-7b](https://huggingface.co/nomic-ai/colnomic-embed-multimodal-7b) | 0.6479 | 0.6871 | 0.5498 | 0.5955 | 0.6201 |

**Multilingual nDCG@5**
| Model | BioMed | ESG Rpts | Economics | **Avg** |
| :--- | :--- | :--- | :--- | :--- |
| **[tomoro-colqwen3-8b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-8b)** | 0.6467 | 0.5911 | **0.5875** | **0.6085** |
| [tomoro-colqwen3-4b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-4b) | **0.6478** | **0.6226** | 0.5536 | 0.6080 |
| [nemo-colembed-3b](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1) | 0.6187 | 0.5640 | 0.5506 | 0.5778 |
| [jinaai/jina-embeddings-v4](https://huggingface.co/jinaai/jina-embeddings-v4) | 0.5994 | 0.5178 | 0.5364 | 0.5512 |
| [nomic-ai/colnomic-embed-multimodal-7b](https://huggingface.co/nomic-ai/colnomic-embed-multimodal-7b) | 0.6224 | 0.5336 | 0.5433 | 0.5664 |

### ViDoRe V1 (English nDCG@5)

| Model | ArxivQA | DocVQA | InfoVQA | Shift | Syn-AI | Syn-Eng | Syn-Gov | Syn-Health | TabFQuAD | Tatdqa | **Avg** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[tomoro-colqwen3-8b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-8b)** | **0.9115** | **0.6637** | 0.9448 | 0.8789 | 0.9926 | 0.9671 | **0.9758** | 0.9906 | 0.9423 | 0.8092 | 0.9076 |
| [tomoro-colqwen3-4b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-4b) | 0.9066 | 0.6624 | 0.9429 | 0.8739 | 0.9926 | 0.9691 | 0.9717 | **0.9963** | 0.9433 | 0.7983 | 0.9057 |
| [nemo-colembed-3b](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1) | 0.8835 | 0.6621 | **0.9492** | 0.9070 | **0.9963** | 0.9663 | 0.9782 | 0.9926 | 0.9594 | 0.8057 | **0.9100** |
| [jinaai/jina-embeddings-v4](https://huggingface.co/jinaai/jina-embeddings-v4) | 0.8846 | 0.6014 | 0.9379 | **0.9293** | 0.9926 | **0.9726** | 0.9659 | 0.9913 | 0.9560 | 0.8035 | 0.9035 |
| [nomic-ai/colnomic-embed-multimodal-7b](https://huggingface.co/nomic-ai/colnomic-embed-multimodal-7b) | 0.8832 | 0.6011 | 0.9221 | 0.8930 | 0.9876 | 0.9626 | 0.9592 | 0.9926 | **0.9596** | **0.8108** | 0.8972 |


### Video Retrieval Evaluation

To demonstrate that Tomoro ColQwen3 strongly generalizes to video retrieval, we evaluated the models on the [CareBench](https://carebench.github.io/) for text to video (General Retrieval) task and [MMEB-V2](https://huggingface.co/datasets/TIGER-Lab/MMEB-V2) video_ret benchmark.

#### CareBench Evaluation

For this evaluation, we utilized a **raw video encoding** approach: our models encoded the video files directly without any additional textual annotations or metadata inputs. This highlights the model's ability to perform retrieval based purely on visual semantics.

| Model | Recall@1 | Recall@5 | Recall@10 |
| :--- | :--- | :--- | :--- |
| **[tomoro-colqwen3-8b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-8b)** | **0.8670** | **0.9590** | 0.9850 |
| [tomoro-colqwen3-4b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-4b) | 0.8620 | 0.9570 | 0.9800 |
| [Care7B](https://huggingface.co/MCG-NJU/CaRe-7B) | 0.7700 | 0.9560 | **0.9870** |

#### MMEB-V2 video_ret Evaluation

All below evaluations are using Hit@1 metric.

| Model | MSR-VTT | MSVD | DiDeMo | VATEX | YouCook2 | Average |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [tomoro-colqwen3-8b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-8b) | 50.3 | 71.2 | 58.8 | 48.0 | 27.8 | 51.2 |
| **[tomoro-colqwen3-4b](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-4b)** | 51.1 | 72.3 | **59.5** | 49.0 | 26.6 | **51.7** |
| **[IFM-TTE-7B](https://interestfm-tte.github.io/)** | 52.7 | **73.1** | 49.7 | **51.5** | **31.6** | **51.7** |
| [seed-1.6-embedding](https://seed1-6-embedding.github.io/) | **55.3** | 71.3 | 56.7 | 48.8 | 24.6 | 51.3 |

`IFM-TTE-7B` and `seed-1.6-embedding` utilize video-text fine-tuning, whereas the Tomoro ColQwen series relies solely on image-text data.

---

## 💻 Usage

The processor exposes `process_texts`, `process_images`, and `score_multi_vector`.

### Prerequisites

We strongly suggest `flash-attn` to be installed. If not, please change to `attention_impl="sdpa"`

Currently we only support torch==2.8.0, for higher pytorch version, please build flash attention manually, otherwise performance throughput could be low.

```bash
pip install torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu128
pip install transformers pillow requests
pip install flash-attn --no-build-isolation
```

### Using Sentence Transformers

`tomoro-colqwen3-embed-8b` can be used as a multi-vector (ColBERT-style late interaction) retriever directly with Sentence Transformers via the `MultiVectorEncoder`.

```bash
pip install "sentence-transformers[image]>=6.0.0"
```

```python
from sentence_transformers import MultiVectorEncoder

model = MultiVectorEncoder("TomoroAI/tomoro-colqwen3-embed-8b", trust_remote_code=True)

queries = [
    "What is the variable represented on the y-axis of the graph?",
    "Total outlay is maximum in which year?",
]
documents = [
    f"https://huggingface.co/datasets/sentence-transformers/example-documents/resolve/main/doc{i}.jpg"
    for i in range(1, 5)
]

query_embeddings = model.encode_query(queries, convert_to_tensor=True)
document_embeddings = model.encode_document(documents, convert_to_tensor=True)
print(f"Query 0 shape:    {tuple(query_embeddings[0].shape)}")
print(f"Document 0 shape: {tuple(document_embeddings[0].shape)}")
# Query 0 shape:    (23, 320)
# Document 0 shape: (1251, 320)

# MaxSim late-interaction scoring (rows = queries, columns = images)
scores = model.similarity(query_embeddings, document_embeddings)
print(scores)
# tensor([[12.4336,  8.5479,  6.7305,  5.1968],
#         [ 4.5449, 11.1719,  4.8320,  4.5195]])
```

> [!NOTE]
> Pages are tiled adaptively, so document embeddings vary in length (1251 tokens for the first three
> example pages, 1271 for the fourth). MaxSim handles that, and `model.similarity` masks the padding.

### Using Transformers

```python
import torch
from transformers import AutoModel, AutoProcessor
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO

# Configuration
MODEL_ID = "TomoroAI/tomoro-colqwen3-embed-8b"
DTYPE = torch.bfloat16
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load Model & Processor
processor = AutoProcessor.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    max_num_visual_tokens=1280,
)
model = AutoModel.from_pretrained(
    MODEL_ID,
    dtype=DTYPE,
    attn_implementation="flash_attention_2",
    trust_remote_code=True,
    device_map=DEVICE,
).eval()

# Sample Data
queries = [
    "Retrieve the city of Singapore",
    "Retrieve the city of Beijing",
    "Retrieve the city of London",
]
docs = [
    "https://upload.wikimedia.org/wikipedia/commons/2/27/Singapore_skyline_2022.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/61/Beijing_skyline_at_night.JPG",
    "https://upload.wikimedia.org/wikipedia/commons/4/49/London_skyline.jpg",
]

def load_image(url: str) -> Image.Image:
    # Some CDNs (e.g., Wikimedia) expect a browser-like UA to avoid 403s.
    for headers in ({}, {"User-Agent": "Mozilla/5.0 (compatible; ColQwen3-demo/1.0)"}):
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 403:
            continue
        resp.raise_for_status()
        try:
            return Image.open(BytesIO(resp.content)).convert("RGB")
        except UnidentifiedImageError as e:
            raise RuntimeError(f"Failed to decode image from {url}") from e
    raise RuntimeError(f"Could not fetch image (HTTP 403) from {url}; try downloading locally and loading from file path.")

# Helper Functions
def encode_queries(texts, batch_size=8):
    outputs = []
    for start in range(0, len(texts), batch_size):
        batch = processor.process_texts(texts=texts[start : start + batch_size])
        batch = {k: v.to(DEVICE) for k, v in batch.items()}
        with torch.inference_mode():
            out = model(**batch)
            vecs = out.embeddings.to(torch.bfloat16).cpu()
        outputs.extend(vecs)
    return outputs

def encode_docs(urls, batch_size=4):
    pil_images = [load_image(url) for url in urls]
    outputs = []
    for start in range(0, len(pil_images), batch_size):
        batch_imgs = pil_images[start : start + batch_size]
        features = processor.process_images(images=batch_imgs)
        features = {k: v.to(DEVICE) if isinstance(v, torch.Tensor) else v for k, v in features.items()}
        with torch.inference_mode():
            out = model(**features)
            vecs = out.embeddings.to(torch.bfloat16).cpu()
        outputs.extend(vecs)
    return outputs

# Execution
query_embeddings = encode_queries(queries)
doc_embeddings = encode_docs(docs)

# MaxSim Scoring
scores = processor.score_multi_vector(query_embeddings, doc_embeddings)
print(scores)
```

#### 🎞️ Lightweight Video Retrieval

ColQwen3 generalizes to short videos while learning from image-text retrieval task. This minimal example samples a clip with `torchvision`, encodes queries and frames, then pools frame embeddings with a per-dimension max before MaxSim scoring.

We recommand use of maximum 5120 visual tokens for video retrieval task for best performance.

```python
from pathlib import Path

import torch
from transformers import AutoModel, AutoProcessor

MODEL_ID = "TomoroAI/tomoro-colqwen3-embed-8b"
DTYPE = torch.bfloat16
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    max_num_visual_tokens=5120,
)
model = AutoModel.from_pretrained(
    MODEL_ID,
    dtype=DTYPE,
    attn_implementation="flash_attention_2",
    trust_remote_code=True,
    device_map=DEVICE,
).eval()

queries = ["Retrieve the football video", "Find the basketball clip", "Find the swimming clip", "Find the wrestling clip"]
videos = ["/root/sample_videos/football.mp4", "/root/sample_videos/basketball.mp4", "/root/sample_videos/swimming.mp4",  "/root/sample_videos/wrestling.mp4"]


def encode_queries(texts):
    batch = processor.process_texts(texts=texts)
    batch = {k: v.to(DEVICE) for k, v in batch.items()}
    with torch.inference_mode():
        out = model(**batch)
    return out.embeddings.to(torch.bfloat16).cpu()

def encode_videos(paths):
    vids = [str(Path(p).expanduser()) for p in paths]
    feats = processor(
        videos=vids,
        padding="longest",
        return_tensors=None,  # keep metadata as Python objects until we drop it
        videos_kwargs={"return_metadata": True},
    )
    feats.pop("video_metadata", None)  # drop metadata before forwarding to the model
    feats = feats.convert_to_tensors(tensor_type="pt")
    feats = {k: v.to(DEVICE) if isinstance(v, torch.Tensor) else v for k, v in feats.items()}
    with torch.inference_mode():
        out = model(**feats)
    return out.embeddings.to(torch.bfloat16).cpu()

q_emb = encode_queries(queries)
v_emb = encode_videos(videos)
scores = processor.score_multi_vector(q_emb, v_emb)
print(scores)
```

-----

## ⚖️ Strengths & Limitations

### Strengths

  * **Performance:** State of the art retrieval performance on ViDoRe V2 & V3 dataset with excellent performance on multimodal document retrieval. 
  * **Complex Layouts:** Excellent handling of chart-rich PDFs, domain-specific documents.
  * **End-to-end Retrieval:** Capable of OCR-free retrieval on unseen multimodal documents without using an intermediate vision LLM to generate summary for retrieval. 
  * **Retrieval Task Transfer:** Inherited strong text retrieval performance from the merged vector of the Qwen3-Embedding-8B model.
  * **Multilingualism:** Strong performance on non-English document inputs.

### Limitations

  * **Video Support:** The retrieval model generalizes to video retrieval on our preliminary findings, however it's not fine-tuned on large-scale video retrieval datasets, we plan to further improve this in the future. 
  * **Storage Cost:** Still larger than single‑vector baselines despite the smaller token dimension.
  * **Retrieval Instructions:** The model currently is not fine-tuned with diverse system instructions similar to Qwen3-Embedding models, we intent to improve this with more synthetic dataset in the future. 

### License & Data

Distributed under **Apache 2.0**.

  * **Weights:** Upstream Qwen checkpoints retain their community licenses; ensure compliance when mixing.
  * **Data:** Training data includes ViDoRe/MTEB corpora and synthetic VisRAG assets.

### Acknowledgement

We gratefully acknowledge the support of **[Tomoro AI](https://tomoro.ai/)**, a leading AI engineering firm dedicated to delivering high-quality enterprise solutions that accelerate complex R&D and business transformation. This work is directly applied to enhance Tomoro’s customized multimodal agentic RAG pipelines, empowering the autonomous agents to parse, reason over, and retrieve from large-scale enterprise **internal documentation**. By bridging the gap between vision and language, this model supports Tomoro AI's mission to **accelerate the delivery of high-quality** enterprise multimodal solutions and deploy robust, production-grade intelligence across high-stakes industries.


## 📚 Citation

If you use this model, please cite:

```bibtex
@misc{huang2025beyond,
  author = {Huang, Xin and Tan, Kye Min},
  title = {Beyond Text: Unlocking True Multimodal, End-to-end RAG with Tomoro ColQwen3},
  year = {2025},
  url = {https://tomoro.ai/insights/beyond-text-unlocking-true-multimodal-end-to-end-rag-with-tomoro-colqwen3},
  publisher = {Tomoro.ai}
}
```