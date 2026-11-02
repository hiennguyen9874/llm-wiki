---
base_model: perplexity-ai/pplx-embed-v2-late-0.6b
base_model_relation: finetune
library_name: transformers
pipeline_tag: feature-extraction
tags:
  - feature-extraction
  - sentence-similarity
  - contextual-embeddings
  - custom_code
language:
  - multilingual
---

<p align="center">
  <img src="assets/logo.svg" alt="Perplexity Logo" width="400">
</p>

<p align="center">pplx-embed-v2-context: Multimodal Contextual Embeddings</p>

`pplx-embed-v2-context-0.6b` is a state-of-the-art vision-language embedding model for retrieval over text, images, and visual documents.
It supports contextual and non-contextual embeddings: In contextual mode, the model embeds chunks of a document with the surrounding context in view. In non-contextual mode, text inputs are embedded in isolation.
`pplx-embed-v2-context-0.6b` shares an embedding space with the 1024-dimensional MRL prefix of [pplx-embed-v2-context-9b](https://huggingface.co/perplexity-ai/pplx-embed-v2-context-9b). Documents can be embedded with one model and queried with another.

This model also supports contextual chunking for visual inputs. Chunked images can be retrieved via standard dense ANN indices. Chunking images can substantially improve retrieval performance.

For benchmark results and details on training, refer to our [technical report](https://arxiv.org/abs/2610.38854).

> [!IMPORTANT]
> When encoding chunks in contextual mode, the document chunks should be **non-overlapping**.

> [!IMPORTANT]
> Queries and documents are encoded with **different methods**: use `encode_queries` for queries and `encode` for document chunks. The model is trained with separate query and document prefixes, and encoding queries with `encode` silently degrades retrieval quality.

> [!IMPORTANT]
> Like `pplx-embed-context-v1`, the model natively produces *unnormalized* int8-quantized embeddings. Compare embeddings with *cosine similarity*, or pass `normalize_embeddings=True` and use the dot product.

## Text Embeddings

Requires `transformers>=5.4.0`, `torch`, `numpy`, `safetensors`, `tqdm`, Pillow, and torchvision. Install `flash-linear-attention` and `causal-conv1d` for the fast linear-attention path. The model uses custom code, so load it with `trust_remote_code=True`.

```python
from transformers import AutoModel

model = AutoModel.from_pretrained(
    "perplexity-ai/pplx-embed-v2-context-0.6b",
    trust_remote_code=True,
).to("cuda")

# Two documents, consisting of several chunks
documents = [
    [
        "Curiosity begins in childhood with endless questions about the world.",
        "As we grow, curiosity drives us to explore new ideas.",
        "Scientific breakthroughs often start with a curious question.",
    ],
    [
        "The curiosity rover explores Mars searching for ancient life.",
        "Each discovery on Mars sparks new questions about the universe.",
    ],
]

# Contextual mode
# One (chunk_count, 1024) array per document:
# chunk_embeddings[0].shape == (3, 1024), chunk_embeddings[1].shape == (2, 1024)
chunk_embeddings = model.encode(documents, normalize_embeddings=True)

# Each query is a single-chunk row.
queries = [["What drives scientific breakthroughs?"]]
query_embeddings = model.encode_queries(queries, normalize_embeddings=True)

scores = chunk_embeddings[0] @ query_embeddings[0][0]

# Non-contextual mode: flatten chunks into a batch of singletons
chunk_embeddings = model.encode(
    [[chunk] for doc in documents for chunk in doc],
    normalize_embeddings=True,
)
```

`encode(documents, ...)` and `encode_queries(queries, ...)` accept:

| Argument | Default | Description |
|---|---|---|
| `batch_size` | `32` | Documents (or queries) per forward pass |
| `normalize_embeddings` | `False` | L2-normalize outputs |
| `convert_to_numpy` | `True` | Return NumPy arrays; `False` returns CPU tensors |
| `show_progress_bar` | `False` | Show a progress bar |
| `device` | `None` | Move the model to this device before encoding |

The text API does not truncate inputs. Split or truncate documents that exceed
the configured input length before encoding. To obtain one embedding per
document, pass each document as a single-chunk list.

## Image Embeddings

Use `encode_images()` to embed document pages or other images as contextual
chunks. Pass a list of PIL images; each image produces one embedding per
horizontal band. Use `encode_queries()` for the corresponding text queries.

```python
import torch
from PIL import Image
from transformers import AutoModel

model = AutoModel.from_pretrained(
    "perplexity-ai/pplx-embed-v2-context-0.6b",
    trust_remote_code=True,
    dtype=torch.bfloat16,
    attn_implementation="sdpa",
).to("cuda").eval()

with Image.open("page.png") as page:
    image_embeddings = model.encode_images(
        [page.convert("RGB")],
        chunks=8,
        min_pixels=16384,
        max_pixels=1800000,
        normalize_embeddings=True,
    )

query_embeddings = model.encode_queries(
    [["What is the company's annual revenue?"]],
    normalize_embeddings=True,
)
page_score = (image_embeddings[0] @ query_embeddings[0][0]).max()
```

Each image is encoded in one contextual forward pass, with its merged visual
tokens divided into whole-row horizontal bands. Native three-axis MRoPE and image
wrappers are preserved. Separator tokens between bands use the midpoint of the
adjacent rows and the horizontal center of the image as their spatial position.
Only visual content is pooled; prefixes, wrappers, and separators are excluded.

`encode_images()` returns one `(actual_chunks, 1024)` array per page. The actual
chunk count is capped at the number of merged image rows.
Use cosine similarity per chunk and the maximum chunk score
for page retrieval, as shown above with normalized vectors.

| Image argument | Default | Description |
|---|---|---|
| `chunks` | `8` | Requested number of horizontal bands per page |
| `min_pixels` | `16384` | Processor minimum image pixel budget |
| `max_pixels` | `1800000` | Processor maximum image pixel budget |
| `batch_size` | `1` | Images per forward pass |

The image API also accepts `normalize_embeddings`, `convert_to_numpy`,
`show_progress_bar`, and `device` with the defaults listed above.
`prepare_images(images, chunks=8, min_pixels=16384, max_pixels=1800000)` exposes
the input tensors, chunk spans, masks, and position IDs without running the model.

## Citation

```bibtex
@article{eslami2026contextual,
  title   = {Contextual Embeddings Beyond the Gold Chunk},
  author  = {Eslami, Sedigheh and Krimmel, Markus and Barber, William and Chaffin, Antoine and Schall, Maximilian and Golde, Jonas and Milliken, Louis and Glazkova, Ekaterina and Bykov, Denis and Wang, Bo},
  journal = {arXiv preprint arXiv:2610.38854},
  year    = {2026},
  doi     = {10.48550/arXiv.2610.38854},
  url     = {https://arxiv.org/abs/2610.38854}
}
```
