---
library_name: colpali_engine
license: apache-2.0
tags:
- visual-document-retrieval
- safetensors
- qwen3_5
- colbert
- late-interaction
- multi-vector
- lora
- model-soup
- optimized
language:
- en
- fr
- de
- es
- zh
arxiv: 2407.01449
model_type: vision-language
pipeline_tag: visual-document-retrieval
base_model:
- Qwen/Qwen3.5-4B
datasets:
- vidore/colpali_train_set
- openbmb/VisRAG-Ret-Train-Synthetic-data
- openbmb/VisRAG-Ret-Train-In-domain-data
- llamaindex/vdr-multilingual-train
- vidore/tatdqa_train
- Metric-AI/tabfquad_train_set
---

# ColQwen3.5-4.5B-v3

A visual document retrieval model using ColBERT-style late interaction with [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B).

**4.5B parameters | 128-dim embeddings | LoRA (r=16, alpha=64) | BF16**

> **Note on embed dim.** Projection head is 320-dim (trained). `config.json` sets `dim: 320` (read by `ColQwen3_5`) with `embed_dim: 320` as a synonym for cross-ecosystem tools, so `ColQwen3_5.from_pretrained(...)` loads correctly by default. Leaderboard columns showing `128` reflect the colpali-engine class default (`self.dim = getattr(config, "dim", 128)`) and not the actual output dim.

## Design Philosophy

V3 builds on V2 with automated hyperparameter search and evolutionary model soup merging. The search identified an optimal LoRA config (r=16, alpha=64) with cosine scheduling, and the final checkpoint is a per-layer evolutionary merge with V2. The result is a +0.0219 improvement over V2 across benchmarks.

## Benchmark Results

### ViDoRe V3 (nDCG@10)

_Rankings on the live [ViDoRe V3 leaderboard](https://huggingface.co/spaces/vidore/vidore-leaderboard) drift as new submissions land. At release, v3 held **#3 overall**; figures below were captured on 2026-04-20, where v3 sits at **#6 on Mean (Task)** and remains **top-3 among 4B-class models**._

| Rank | Model | Memory (MB) | Params (B) | Embed Dim | Max Tokens | Mean (Task) | Mean (Public) | Mean (Private) |
|------|-------|-------------|------------|-----------|------------|-------------|---------------|----------------|
| 1 | nemotron-colembed-vl-8b-v2 | 16722 | 8.7 | 4096 | 262144 | 63.42 | 63.54 | 62.92 |
| 2 | webAI-ColVec1-9b | — | 9.42 | 2560 | 262144 | 63.00 | 64.45 | 57.20 |
| 3 | webAI-ColVec1-4b | — | 4.541 | 640 | 262144 | 62.22 | 63.39 | 57.55 |
| 4 | tomoro-colqwen3-embed-8b | 16724 | 8.0 | 320 | 262144 | 61.59 | 61.60 | 61.56 |
| 5 | nemotron-colembed-vl-4b-v2 | 9206 | 4.8 | 2560 | 262144 | 61.54 | 61.42 | 62.04 |
| **6** | **colqwen3.5-4.5B-v3** | **8660** | **4.6** | **128** | **262144** | **61.46** | **61.56** | **61.06** |
| 7 | Ops-Colqwen3-4B | 9206 | 4.8 | 2560 | 32768 | 61.17 | 61.27 | 60.78 |
| 8 | tomoro-colqwen3-embed-4b | 8466 | 4.0 | 320 | 262144 | 60.20 | 60.16 | 60.33 |
| 9 | llama-nemotron-colembed-vl-3b-v2 | 8403 | 4.407 | 3072 | 8192 | 59.79 | 59.70 | 60.16 |
| 10 | jina-embeddings-v4 | 7500 | 3.935 | 2048 | 32768 | 57.52 | 57.54 | 57.41 |


### ViDoRe V1+V2 (nDCG@5)

| Rank | Model | ArxivQA | DocVQA | InfoVQA | ShiftProj | SynAI | SynEnergy | SynGov | SynHealth | Tabfquad | Tatdqa | BioMed | ESGHL | ESG | Econ | Avg |
|------|-------|---------|--------|---------|-----------|-------|-----------|--------|-----------|----------|--------|--------|-------|-----|------|-----|
| 1 | Ops-Colqwen3-4B | 91.8 | 66.5 | 94.0 | 90.8 | 99.6 | 97.3 | 98.0 | 99.6 | 93.6 | 82.4 | 65.5 | 78.6 | 66.0 | 64.5 | 84.9 |
| 2 | nemotron-colembed-vl-8b-v2 | 93.1 | 68.1 | 94.6 | 93.3 | 100.0 | 97.9 | 98.9 | 99.6 | 97.7 | 83.4 | 66.2 | 73.2 | 60.6 | 60.8 | 84.8 |
| 3 | nemotron-colembed-vl-4b-v2 | 92.0 | 67.4 | 93.3 | 92.3 | 99.3 | 96.2 | 98.0 | 98.5 | 98.1 | 81.2 | 64.3 | 71.4 | 61.5 | 60.8 | 83.9 |
| **4** | **colqwen3.5-4.5B-v3** | 91.9 | 66.6 | 93.6 | 90.2 | 100.0 | 97.1 | 97.3 | 98.9 | 95.9 | **84.0** | 65.3 | 73.8 | 58.0 | 59.9 | **83.7** |
| 5 | llama-nemotron-colembed-vl-3b-v2 | 90.4 | 67.2 | 94.7 | 92.0 | 100.0 | 98.0 | 98.0 | 98.9 | 97.3 | 81.0 | 63.2 | 73.1 | 58.6 | 58.6 | 83.6 |
| 6 | tomoro-colqwen3-embed-8b | 91.2 | 66.4 | 94.5 | 87.9 | 99.3 | 96.7 | 97.6 | 99.1 | 94.2 | 80.9 | 65.5 | 76.0 | 60.7 | 59.5 | 83.5 |
| 7 | EvoQwen2.5-VL-Retriever-7B-v1 | 91.5 | 65.1 | 94.1 | 88.8 | 99.6 | 96.6 | 96.3 | 98.9 | 93.6 | 82.3 | 65.2 | 77.0 | 59.7 | 59.1 | 83.4 |
| 8 | tomoro-colqwen3-embed-4b | 90.6 | 66.3 | 94.3 | 87.4 | 99.3 | 96.9 | 97.2 | 99.6 | 94.3 | 79.9 | 65.4 | 74.6 | 62.4 | 56.3 | 83.2 |
| 9 | llama-nemoretriever-colembed-3b-v1 | 88.4 | 66.2 | 94.9 | 90.7 | 99.6 | 96.6 | 97.8 | 99.3 | 95.9 | 80.6 | 62.7 | 75.4 | 57.4 | 57.8 | 83.1 |
| 10 | SauerkrautLM-ColQwen3-8b-v0.1 | 93.8 | 64.7 | 94.5 | 90.4 | 98.6 | 96.5 | 96.8 | 99.3 | 92.2 | 84.0 | 63.3 | 70.8 | 57.9 | 58.0 | 82.9 |

### Limitations

- Trails Nemotron 8B on most V3 tasks (1.9 points gap on Mean Task)
- V1+V2 average slightly below Ops-ColQwen3 and Nemotron variants
- V2 is the weakest benchmark area (ESG, Econ)
- Larger 4B+ submissions (webAI-ColVec1-4b/9b) released after v3 now lead overall Mean (Task); v3 remains top-3 among 4B-class models

## Usage

```python
import torch
from PIL import Image
from colpali_engine.models import ColQwen3_5, ColQwen3_5Processor

model = ColQwen3_5.from_pretrained(
    "athrael-soju/colqwen3.5-4.5B-v3",
    torch_dtype=torch.bfloat16,
    device_map="cuda",
    attn_implementation="sdpa",
)
processor = ColQwen3_5Processor.from_pretrained("athrael-soju/colqwen3.5-4.5B-v3")

# Embed document images
images = [Image.open("page1.png"), Image.open("page2.png")]
batch = processor.process_images(images).to(model.device)
with torch.no_grad():
    doc_embeddings = model(**batch)

# Embed queries
queries = ["What is the revenue for Q4?", "Show me the organizational chart"]
batch = processor.process_queries(queries).to(model.device)
with torch.no_grad():
    model.rope_deltas = None
    query_embeddings = model(**batch)

# Score with MaxSim
scores = processor.score(query_embeddings, doc_embeddings)
```

## Training

### Pipeline

1. Hyperparameter search: multi-objective optimization across V1+V3, found optimal LoRA config
2. Full training: 3 seeds (42, 123, 456) with optimized hyperparameters, 1 epoch
3. Seed merge: full state dict averaging (3 seeds into 1)
4. Model soup: per-layer evolutionary merge with V2

### Training Data (~776K pairs)

- vidore/colpali_train_set: 127K
- openbmb/VisRAG-Ret-Train-Synthetic-data: 239K
- openbmb/VisRAG-Ret-Train-In-domain-data: 123K
- llamaindex/vdr-multilingual-train: ~270K (5 languages)
- vidore/tatdqa_train: ~13K (finance)
- Metric-AI/tabfquad_train_set: ~1.5K (tables)

### Hyperparameters

| Parameter | Value |
|-----------|-------|
| LoRA r | 16 |
| LoRA alpha | 64 (alpha/r = 4.0) |
| LR | 4.57e-5 |
| Scheduler | cosine |
| Dropout | 0.197 |
| Warmup | 8% |
| Weight decay | 0.02 |
| Batch size | 32 |
| Hard negatives | 2/sample |
| Seeds | 42, 123, 456 |

### Technical Notes

- PEFT's `add_weighted_adapter` is broken for ColQwen3.5 (both DARE-TIES and linear). Use full state dict averaging for seed merging.
- Model soup done via direct state dict interpolation with per-layer optimized weights.
- B200/Blackwell GPUs require Conv3d to F.linear monkey-patch.
- Always clear `rope_deltas` before forward passes with hard negatives.

## Transparency

The complete evaluation trail from V1, V2, and V3 development is available at [athrael-soju/colqwen-optimization-trail](https://huggingface.co/datasets/athrael-soju/colqwen-optimization-trail). This includes every intermediate evaluation showing which candidates were tried, what scores they got, and which were selected for publication. All selection decisions were evaluated against the same public ViDoRe benchmarks used for final reporting.

## Archived Versions (V1 and V2)

V1 and V2 model snapshots have been consolidated into this repository to reduce sprawl and preserve provenance. Full contents of the previously-separate `colqwen3.5-4.5B-v1` and `colqwen3.5-4.5B-v2` repositories are available here under:

- **`v1/`** — complete V1 snapshot (weights, model card, tokenizer, configs)
- **`v2/`** — complete V2 snapshot (weights, model card, tokenizer, configs)

Each subfolder contains the full original file set (`model.safetensors`, `README.md`, `config.json`, `chat_template.jinja`, `processor_config.json`, `tokenizer.json`, `tokenizer_config.json`).

To load an archived version:

```python
from colpali_engine.models import ColQwen3_5, ColQwen3_5Processor
# V1
model = ColQwen3_5.from_pretrained("athrael-soju/colqwen3.5-4.5B-v3", subfolder="v1", ...)
processor = ColQwen3_5Processor.from_pretrained("athrael-soju/colqwen3.5-4.5B-v3", subfolder="v1")
# V2
model = ColQwen3_5.from_pretrained("athrael-soju/colqwen3.5-4.5B-v3", subfolder="v2", ...)
```

The top-level files remain the V3 model — the recommended version for production use.

## Citation

```bibtex
@misc{colqwen35v3,
  title={ColQwen3.5-v3: Visual Document Retrieval with Evolutionary Model Soups},
  author={athrael-soju},
  year={2026},
  url={https://huggingface.co/athrael-soju/colqwen3.5-4.5B-v3}
}
```

## License

Apache 2.0
