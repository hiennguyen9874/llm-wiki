---
pipeline_tag: visual-document-retrieval
library_name: transformers
language:
  - multilingual
license: other
license_name: webai-non-commercial-license-v1.0
license_link: https://huggingface.co/webAI-Official/webAI-ColVec1.1-4b/blob/main/LICENSE.md
base_model: Qwen/Qwen3.5-4B
datasets:
  - vidore/colpali_train_set
  - Tevatron/docmatix-ir
  - openbmb/VisRAG-Ret-Train-In-domain-data
  - openbmb/VisRAG-Ret-Train-Synthetic-data
  - llamaindex/vdr-multilingual-train
  - Tevatron/wiki-ss-nq
tags:
  - text
  - image
  - multimodal-embedding
  - visual-document-retrieval
  - vidore
  - colbert
  - colqwen3_5
  - multilingual-embedding
  - sentence-transformers
  - multi-vector
---

# webAI-Official/webAI-ColVec1.1-4b

## ⚡ Summary

**webAI-Official/webAI-ColVec1.1-4b** is a ColBERT-style multimodal
embedding model based on
[Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B). It maps text
queries and visual documents (images or rendered PDF pages) into aligned,
L2-normalized multi-vector embeddings for late-interaction retrieval.

The model uses bidirectional attention in Qwen3.5's full-attention layers and
a learned 640-dimensional projection head. The unused language-model head has
been removed from the released checkpoint.

### Training data

We created filtered, balanced, and multilingual curated subsets from six public
datasets: [ColPali Train Set](https://huggingface.co/datasets/vidore/colpali_train_set),
[Docmatix-IR](https://huggingface.co/datasets/Tevatron/docmatix-ir),
[VisRAG In-Domain](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-In-domain-data),
[VisRAG Synthetic](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-Synthetic-data),
[VDR Multilingual Train](https://huggingface.co/datasets/llamaindex/vdr-multilingual-train),
and [Wiki-SS-NQ](https://huggingface.co/datasets/Tevatron/wiki-ss-nq). This
Qwen3.5-4B-backbone model was trained on a 500,000-sample curated subset as well
as synthetically generated data.

## 🛠️ Model specifications

| Feature | Detail |
| :--- | :--- |
| **Architecture** | Qwen3.5-4B vision-language model + 640-dimensional linear projection |
| **Released parameters** | 4,540,904,576 |
| **Method** | ColBERT-style late interaction with MaxSim scoring |
| **Output** | L2-normalized multi-vector embeddings `(sequence_length, 640)` |
| **Modalities** | Text queries and document images |
| **Attention** | Bidirectional full-attention layers; selectable SDPA, FlashAttention 2, or FlashAttention 3 kernel |
| **Visual-token budget** | 1,792 tokens per image in the released processor |
| **Training** | LoRA adapters and a fully trained projection layer, merged for release |
| **Weights** | `bfloat16`; language-model head removed |

### Key properties

- **Unified encoder:** The same model encodes text and document images.
- **Token-level retrieval:** Multi-vector embeddings preserve fine-grained
  layout and content signals that single-vector pooling can discard.
- **Compact projection:** Hidden states are projected to 640 dimensions
  without an activation function.
- **Bidirectional retrieval attention:** Selecting SDPA, FlashAttention 2, or
  FlashAttention 3 changes the execution kernel, not the model's bidirectional
  attention mode.

## 📊 Evaluation results

The table reports NDCG@10 scores on the ViDoRe V3 tasks as percentages rather
than values between 0 and 1 (for example, 0.80 is shown as 80.00). Each task
value is the mean of its six language subsets. Mean (Public) is the unweighted
mean of the eight public task values, Mean (Private) covers the Nuclear and
Telecom tasks, and the final mean is the unweighted mean across all ten tasks.
Models are sorted by the final mean.

The evaluation software versions and setup are documented under
[Reproducing the evaluation environment](#reproducing-the-evaluation-environment).
For the reported evaluation, SDPA was selected as the attention
implementation, the released processor used a 1,792 visual-token budget, and
the batch size was 32.

Model encoding used `bfloat16`. Before MaxSim scoring, query and document
embeddings were moved to CPU and converted to `float32`; all reported ViDoRe
results use this FP32 scoring path. Because floating-point calculations and
kernel execution can vary across accelerator hardware, independent
evaluations may produce slightly different results. The submitted MTEB
artifacts are the canonical source for the reported scores.

All table values are shown to two decimal places. ColVec1.1 values are rounded
from the submitted artifacts using round-half-up. Comparator values were read
from the live
[ViDoRe V3 MTEB leaderboard](https://mteb-leaderboard.hf.space/benchmark/ViDoRe%28v3%29)
on July 31, 2026.

| Model | **Final mean** | **Mean (Public)** | **Mean (Private)** | Computer Science | Energy | FinanceEn | FinanceFr | HR | Industrial | Nuclear | Pharmaceuticals | Physics | Telecom |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **[webAI-ColVec1.1-8b](https://huggingface.co/webAI-Official/webAI-ColVec1.1-8b)** | **64.95** | **65.32** | **63.47** | 80.08 | 70.12 | **71.90** | **54.87** | 68.55 | **57.65** | 53.66 | 67.88 | 51.50 | **73.29** |
| [VultronRetriever Prime](https://huggingface.co/vultr/VultronRetrieverPrime-Qwen3.5-8B) | 64.26 | 64.72 | 62.43 | 79.81 | **70.26** | 69.01 | 54.51 | 66.82 | 57.41 | 53.59 | **68.19** | **51.73** | 71.27 |
| **webAI-ColVec1.1-4b (this model)** | 63.90 | 64.24 | 62.53 | 80.34 | 69.50 | 69.18 | 53.13 | 66.90 | 56.36 | 53.30 | 67.25 | 51.24 | 71.76 |
| [VultronRetriever Core](https://huggingface.co/vultr/VultronRetrieverCore-Qwen3.5-4.5B) | 63.57 | 63.72 | 63.00 | 79.77 | 69.19 | 68.93 | 52.02 | 66.10 | 56.11 | **54.90** | 67.45 | 50.18 | 71.10 |
| [Nemotron ColEmbed VL 8B V2](https://huggingface.co/nvidia/nemotron-colembed-vl-8b-v2) | 63.42 | 63.54 | 62.92 | 79.29 | 69.82 | 67.29 | 51.54 | 66.32 | 56.03 | 53.84 | 67.19 | 50.84 | 72.00 |
| [webAI-ColVec1-9b](https://huggingface.co/webAI-Official/webAI-ColVec1-9b) | 63.00 | 64.45 | 57.20 | **80.92** | 69.77 | 68.28 | 53.72 | **70.04** | 57.18 | 47.66 | 67.32 | 48.38 | 66.74 |
| [webAI-ColVec1-4b](https://huggingface.co/webAI-Official/webAI-ColVec1-4b) | 62.22 | 63.39 | 57.55 | 79.84 | 68.70 | 68.49 | 51.11 | 67.40 | 55.73 | 48.22 | 65.68 | 50.15 | 66.88 |
| [Tomoro ColQwen3 Embed 8B](https://huggingface.co/TomoroAI/tomoro-colqwen3-embed-8b) | 61.59 | 61.60 | 61.56 | 75.35 | 68.41 | 65.08 | 49.10 | 63.98 | 54.41 | 52.65 | 66.36 | 50.13 | 70.46 |

The current MTEB leaderboard entries named `webAI-ColVec1-4b` and
`webAI-ColVec1-9b` refer to the previous ColVec1 release, not these ColVec1.1
checkpoints.

## 💻 Usage

### Using Sentence Transformers

The checkpoint loads as a `MultiVectorEncoder`, which is available from
Sentence Transformers v6.0.0:

```bash
pip install "sentence-transformers[image]>=6.0.0"
```

`encode_query` and `encode_document` apply the query and document prompt
formats, the ten query-augmentation tokens, and the L2-normalized
640-dimensional projection. `similarity` computes the MaxSim score matrix.

```python
from io import BytesIO

import requests
from PIL import Image
from sentence_transformers import MultiVectorEncoder

model = MultiVectorEncoder("webAI-Official/webAI-ColVec1.1-4b", trust_remote_code=True)

queries = [
    "When was the United States Declaration of Independence proclaimed?",
    "Who printed the edition of Romeo and Juliet?",
]
document_urls = [
    "https://upload.wikimedia.org/wikipedia/commons/8/89/US-original-Declaration-1776.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Romeoandjuliet1597.jpg/500px-Romeoandjuliet1597.jpg",
]
documents = [
    Image.open(BytesIO(requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30).content))
    for url in document_urls
]

query_embeddings = model.encode_query(queries)
document_embeddings = model.encode_document(documents)
print(query_embeddings[0].shape, document_embeddings[0].shape)
# (27, 640) (523, 640)

scores = model.similarity(query_embeddings, document_embeddings)
print(scores)
# tensor([[23.3935,  5.7660],
#         [ 4.8504, 23.1851]])
print("Best document per query:", scores.argmax(dim=1))
# Best document per query: tensor([0, 1])
```

Documents may also be given as file paths or URLs instead of `PIL.Image`
objects. The Wikimedia URLs above are fetched with a browser `User-Agent`
because Wikimedia rejects the default one. Both encode methods accept a
`batch_size`, and the loading options are forwarded through `model_kwargs`
(`dtype`, `attn_implementation`, `device_map`) and `processor_kwargs`
(`max_num_visual_tokens`):

```python
model = MultiVectorEncoder(
    "webAI-Official/webAI-ColVec1.1-4b",
    trust_remote_code=True,
    model_kwargs={"attn_implementation": "sdpa", "device_map": "cuda:0"},
    processor_kwargs={"max_num_visual_tokens": 1024},
)
```

The scores above come from the plain load, which uses the checkpoint's
`bfloat16` weights and SDPA. MaxSim is accumulated in `float32` rather
than in the embedding dtype, matching the scoring path behind the reported
evaluation, so a `bfloat16` `score_retrieval` call on the same embeddings
returns coarser values. The scores still move in the second decimal place
across PyTorch and Transformers builds. Text passed to `encode_document`
is rendered as a query, because the model defines no text-document format,
and a warning says so.

### Using transformers

The processor provides the current retrieval API:

- `process_images(images)` prepares one or more document images.
- `process_queries(texts)` prepares one or more natural-language queries.
- `score_retrieval(query_embeddings, document_embeddings)` computes a MaxSim
  score matrix with shape `(number_of_queries, number_of_documents)`.

### Quick start

Create and activate a Python 3.12 virtual environment, then install the
validated PyTorch CUDA 12.8 build and the minimal packages required for SDPA
inference. If you are already using an isolated Python environment, skip the
first two commands.

```bash
python3.12 -m venv .venv
source .venv/bin/activate

python -m pip install \
  torch==2.9.0 torchvision==0.24.0 \
  --index-url https://download.pytorch.org/whl/cu128

python -m pip install \
  "transformers>=5.14.1,<6.0.0" \
  accelerate pillow requests safetensors
```

The following example uses SDPA, the portable default and the attention
implementation used for the reported evaluation. It does not require
FlashAttention.

```python
from io import BytesIO

import requests
import torch
from PIL import Image
from transformers import AutoModel, AutoProcessor

MODEL_ID = "webAI-Official/webAI-ColVec1.1-4b"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Portable default and the backend used by the published evaluation:
ATTN_IMPLEMENTATION = "sdpa"

processor = AutoProcessor.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    max_num_visual_tokens=1792,
)
model = AutoModel.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    dtype=torch.bfloat16,
    attn_implementation=ATTN_IMPLEMENTATION,
    device_map=DEVICE,
).eval()

queries = [
    "When was the United States Declaration of Independence proclaimed?",
    "Who printed the edition of Romeo and Juliet?",
]
document_urls = [
    "https://upload.wikimedia.org/wikipedia/commons/8/89/US-original-Declaration-1776.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Romeoandjuliet1597.jpg/500px-Romeoandjuliet1597.jpg",
]


def load_image(url: str) -> Image.Image:
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")


device = next(model.parameters()).device
query_inputs = processor.process_queries(queries)
document_inputs = processor.process_images(
    [load_image(url) for url in document_urls]
)
query_inputs = {
    key: value.to(device) if isinstance(value, torch.Tensor) else value
    for key, value in query_inputs.items()
}
document_inputs = {
    key: value.to(device) if isinstance(value, torch.Tensor) else value
    for key, value in document_inputs.items()
}

with torch.inference_mode():
    query_batch = model(**query_inputs)
    document_batch = model(**document_inputs)

query_embeddings = [embedding.cpu() for embedding in query_batch]
document_embeddings = [embedding.cpu() for embedding in document_batch]
scores = processor.score_retrieval(
    query_embeddings,
    document_embeddings,
    output_dtype=torch.float32,
)

print(scores)
print("Best document per query:", scores.argmax(dim=1))
```

The released processor uses a 1,792 visual-token budget by default. To reduce
memory use, pass a lower `max_num_visual_tokens` value to
`AutoProcessor.from_pretrained`; this changes document granularity and may
change retrieval scores.

### Optional acceleration

The model can run with compatible PyTorch and CUDA builds using SDPA,
FlashAttention 2, or FlashAttention 3. CPU execution is supported through
PyTorch's SDPA math fallback, but is generally impractical for a model of this
size.

Qwen3.5 uses a hybrid stack of full-attention and GatedDeltaNet
linear-attention layers. These kernels serve different parts of the model:

- `flash-attn` can accelerate the full-attention layers when selected.
- `causal-conv1d` and `flash-linear-attention` (`fla`) accelerate the
  GatedDeltaNet layers. Transformers can fall back to PyTorch implementations
  without them.
- `tilelang` provides optimized GPU kernels for some FLA operations. FLA uses
  these kernels when the operation and hardware are supported and uses another
  implementation otherwise. Pin `apache-tvm-ffi<0.1.10` alongside it to keep
  TileLang's TVM dependency compatible.

[flash-attn](https://github.com/Dao-AILab/flash-attention) and
[causal-conv1d](https://github.com/Dao-AILab/causal-conv1d) ship as prebuilt
wheels tied to a specific Python, PyTorch, CUDA, and C++ ABI combination, so
install the build that matches your environment;
[flash-linear-attention](https://github.com/fla-org/flash-linear-attention) and
[TileLang](https://github.com/tile-ai/tilelang) install from PyPI. The exact
versions used for the reported scores are pinned in
[Reproducing the evaluation environment](#reproducing-the-evaluation-environment).

`causal-conv1d`, `flash-linear-attention`, and `tilelang` are detected
automatically once installed, so the GatedDeltaNet layers need no configuration
change. Only the full-attention backend is selected explicitly, as a one-line
change to the model loading code in [Quick start](#quick-start):

```python
ATTN_IMPLEMENTATION = "flash_attention_2"  # or "flash_attention_3"
```

FlashAttention 2 and FlashAttention 3 both preserve the model's bidirectional
attention, and FlashAttention 3 can improve throughput on Hopper GPUs
(H100/H200). PyTorch's built-in SDPA remains the more portable choice because
it does not require a separate FlashAttention package or ABI-compatible wheel.
Changing the full-attention implementation may introduce small floating-point
differences and affect only those layers, not the GatedDeltaNet layers.

### Reproducing the evaluation environment

The complete pinned Python environment is provided in
[`evaluation-requirements-cu128.txt`](./evaluation-requirements-cu128.txt),
which reproduces the recorded Linux x86-64, CPython 3.12, CUDA 12.8, and
PyTorch 2.9 environment used for evaluation. Its pinned wheel URLs are specific
to that platform, so a different environment needs matching wheels or a source
build.

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/), ensure
Git is available, and then run:

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate

uv pip install \
  torch==2.9.0 torchvision==0.24.0 \
  --index-url https://download.pytorch.org/whl/cu128

uv pip install -r evaluation-requirements-cu128.txt
uv pip check
```

The requirements include FlashAttention 2 as an optional supported backend;
its presence does not change the SDPA configuration used for the reported
scores.

The ViDoRe V3 scores used the following core software versions:

```text
Python 3.12
PyTorch 2.9.0 + CUDA 12.8
Transformers 5.14.1
MTEB 2.18.6 (commit d56a414b45ebad0d03495de000b4880d8b028d4a)
Sentence Transformers 5.6.0
causal-conv1d 1.6.2.post1
flash-linear-attention 0.5.1
TileLang 0.1.9
Attention implementation: SDPA
```

## ⚖️ Strengths and limitations

### Strengths

- **Performance:** State-of-the-art retrieval performance among 4B models on
  the public ViDoRe V3 tasks, with excellent multimodal document retrieval
  results.
- **Complex layouts:** Excellent handling of chart-rich PDFs and
  domain-specific documents.
- **End-to-end retrieval:** OCR-free retrieval on unseen multimodal documents
  without using an intermediate vision-language model to generate summaries.
- **Multilingualism:** Strong performance on non-English document inputs.

### Limitations

- **Storage cost:** Still larger than single-vector baselines despite the
  smaller token dimension.

## License

Model weights are distributed under the
[webAI Non-Commercial License v1.0](https://huggingface.co/webAI-Official/webAI-ColVec1.1-4b/blob/main/LICENSE.md).
See the repository's `NOTICES.md` for upstream attribution.

## 📚 Citation

```bibtex
@misc{webai_colvec1_1_4b,
  title  = {webAI-ColVec1.1-4b: A Bidirectional Multi-Vector Model for Visual Document Retrieval},
  author = {webAI},
  year   = {2026},
  url    = {https://huggingface.co/webAI-Official/webAI-ColVec1.1-4b}
}
```
