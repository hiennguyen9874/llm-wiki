---
license: other
license_name: openmdw-1.1
license_link: >-
  https://openmdw.ai/license/1-1/
base_model:
  - mistralai/Ministral-3-8B-Instruct-2512
tags:
  - text
  - text-embeddings
  - retrieval
  - semantic-search
  - transformers
  - rag
  - vllm
language:
  - multilingual
  - en
  - ar
  - as
  - bn
  - bg
  - zh
  - da
  - nl
  - fi
  - fr
  - de
  - hi
  - id
  - it
  - ja
  - ko
  - ms
  - mr
  - ne
  - "no"
  - fa
  - pt
  - ro
  - ru
  - es
  - sw
  - sv
  - ta
  - te
  - th
  - uk
  - ur
  - vi
library_name: sentence-transformers
pipeline_tag: sentence-similarity
---

<div align="center">

**NVIDIA Nemotron 3 Embed**

<a href="https://huggingface.co/nvidia/Nemotron-3-Embed-1B-BF16">
  <img alt="Nemotron 3 Embed 1B BF16" src="https://img.shields.io/badge/1B-BF16-76B900?style=for-the-badge&logo=nvidia&logoColor=white">
</a>
&nbsp;
<a href="https://huggingface.co/nvidia/Nemotron-3-Embed-1B-NVFP4">
  <img alt="Nemotron 3 Embed 1B NVFP4" src="https://img.shields.io/badge/1B-NVFP4-76B900?style=for-the-badge&logo=nvidia&logoColor=white">
</a>
&nbsp;
<a href="https://huggingface.co/nvidia/Nemotron-3-Embed-8B-BF16">
  <img alt="Nemotron 3 Embed 8B BF16" src="https://img.shields.io/badge/8B-BF16-76B900?style=for-the-badge&logo=nvidia&logoColor=white">
</a>

</div>

# Model Overview

### Description:
**Nemotron-3-Embed-8B-BF16** is a versatile text embedding model trained by NVIDIA and optimized for retrieval and semantic similarity tasks. It provides strong multilingual and cross-lingual retrieval capabilities and is designed to serve as a foundational component in text-based Retrieval-Augmented Generation (RAG) systems. This model was evaluated across 34 languages: English, Arabic, Assamese, Bengali, Bulgarian, Chinese, Danish, Dutch, Finnish, French, German, Hindi, Hinglish, Indonesian, Italian, Japanese, Korean, Malay, Marathi, Nepali, Norwegian, Persian, Portuguese, Romanian, Russian, Spanish, Swahili, Swedish, Tamil, Telugu, Thai, Ukrainian, Urdu, Vietnamese.

The model generates dense vector embeddings from multilingual text inputs, enabling retrieval, semantic search, and (agentic) RAG workflows. As a core component of text retrieval systems, an embedding model transforms text, such as questions or passages, into dense vector representations. These models are typically transformer encoders that process input tokens and produce embeddings suitable for efficient similarity matching.

**Nemotron-3-Embed-8B-BF16** achieves state-of-the-art performance on the multilingual [RTEB leaderboard](https://mteb-leaderboard.hf.space/benchmark/RTEB(beta)) as of July 16, 2026. Read more details in our [Blog Post](https://huggingface.co/blog/nvidia/nemotron-3-embed-wins-rteb).

This model is ready for commercial use.

### License/Terms of Use:

This model and its associated configuration files are licensed under the [OpenMDW License Agreement, version 1.1 (OpenMDW-1.1)](https://openmdw.ai/license/1-1/). Additional Information: Built with [Ministral-3-8B-Instruct-2512](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) which is released under Apache 2.0.

This project will download and install additional third-party open source software projects. Review the license terms of these open source projects before use.

### Deployment Geography:
Global

### Use Case: <br>

**Nemotron-3-Embed-8B-BF16** is most suitable for users who want to build a multilingual question-and-answer application over a large text corpus, leveraging the latest dense retrieval technologies.

### Release Date: <br>

07/16/2026 via https://huggingface.co/nvidia/Nemotron-3-Embed-8B-BF16

## Model Architecture:
**Architecture Type:** Transformer <br>

**Network Architecture:** [Ministral-3-8B-Instruct-2512](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) based encoder model. <br>

**Number of model parameters:** The model has approximately 8B parameters. <br>

**Hidden Size:** 4096 <br>

The **Nemotron-3-Embed-8B-BF16** model is a transformer-based text embedding model trained with bidirectional attention masking, where the final embedding vector is obtained by applying average pooling to the transformer’s token-level representations. It encodes each input text into a dense embedding vector of dimension 4096.


## Input(s):
**Input Type(s):** Text <br>

**Input Format(s):** <br>
- Text: List of strings <br>

**Input Parameters:** <br>
- Text: One-Dimensional (1D) <br>

**Other Properties Related to Input:** Text inputs should be tokenized by the model tokenizer. The model’s max sequence length is 32768. Longer inputs should be chunked or truncated. <br>

## Output(s):

**Output Type(s):** Floats <br>

**Output Format(s):** <br>
- List of float arrays <br>

**Output Parameters:** One-Dimensional (1D) embedding vector per input text string <br>

**Other Properties Related to Output:** The model outputs a 4096-dimensional embedding vector for each input text string. It also supports dynamic embedding sizes by slicing the vector from the start (for example, keeping the first 2048 or 1024 dimensions). These sliced embeddings remain highly functional, provided the resulting sub-vector is re-normalized (L2 normalization) after slicing. <br>

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA's hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions. <br>


## Usage

For local Python examples, use the Hugging Face model ID by default. If you are working from a local checkout, replace `MODEL_ID` with that path. For vLLM online serving from a local checkpoint, use the local checkpoint example.

```python
MODEL_ID = "nvidia/Nemotron-3-Embed-8B-BF16"
```

Use this model for retrieval-style embeddings. Add the `query: ` prefix for queries and the `passage: ` prefix for documents. Embeddings are L2-normalized, so dot product and cosine similarity are equivalent. The output tables use `q[i]` for queries and `d[i]` for documents. Scores are rounded to four decimals. Exact values can vary by runtime and package version.

### Local Python Dependencies

The BF16 checkpoints support Transformers `5.2.0` and above. The examples also require a CUDA-enabled PyTorch installation that matches your driver and CUDA environment.

If you are not using an NVIDIA PyTorch container, install PyTorch first. Use the [PyTorch local installation selector](https://pytorch.org/get-started/locally/) to choose the command that matches your operating system, package manager, and CUDA environment. If the default PyPI wheel matches your CUDA environment, run:

```bash
pip install --upgrade torch
```

For non-default CUDA environments, the selector can include an additional `--index-url` argument. Use that CUDA-specific index URL when the default PyPI wheel does not match your CUDA environment.

Then install Transformers and Sentence Transformers:

```bash
pip install --upgrade "transformers>=5.2.0" "sentence-transformers>=5.4.1"
```

NVIDIA tested the examples in `nvcr.io/nvidia/pytorch:26.06-py3` with the container-provided Torch and CUDA stack. Inside NVIDIA PyTorch containers, do not upgrade Torch. Install only the missing packages:

```bash
pip install --upgrade "transformers>=5.2.0" "sentence-transformers>=5.4.1"
```

The tested `nvcr.io/nvidia/pytorch:26.06-py3` container includes `flash-attn`, so the snippets use FlashAttention-2 by default. If your environment does not have FlashAttention-2, set `attn_implementation` or `ATTN_IMPLEMENTATION` to `sdpa`.


### Sentence Transformers

Use Sentence Transformers for the simplest local Python interface. It reads the saved query and document prompts and normalization metadata.

```python
import torch
from sentence_transformers import SentenceTransformer

MODEL_ID = "nvidia/Nemotron-3-Embed-8B-BF16"

model = SentenceTransformer(
    MODEL_ID,
    device="cuda",
    model_kwargs={
        "dtype": torch.bfloat16,
        "attn_implementation": "flash_attention_2",
    },
    processor_kwargs={"padding_side": "left"},
)
model.max_seq_length = 32768

QUERIES = [
    "Write a Python function that counts the frequency of each element in a list of lists.",
    "Write a function that orders a dictionary with tuple keys by the product of each key's tuple values.",
    "What symptoms and common triggers help distinguish eczema from other inflammatory skin conditions?",
    "How can someone reduce exposure to pollen during allergy season?",
]

DOCUMENTS = [
    "def frequency_lists(list1):\n    flattened = [item for sublist in list1 for item in sublist]\n    counts = {}\n    for item in flattened:\n        if item in counts:\n            counts[item] += 1\n        else:\n            counts[item] = 1\n    return counts",
    "def sort_dict_item(test_dict):\n    return {key: test_dict[key] for key in sorted(test_dict.keys(), key=lambda ele: ele[0] * ele[1])}",
    "Eczema commonly causes itchy, dry, inflamed patches of skin. The affected areas may look red, scaly, cracked, or darker than the surrounding skin depending on skin tone. Symptoms can flare after exposure to irritants, allergens, stress, or changes in weather.",
    "People with pollen allergy can reduce exposure by staying indoors on dry, windy days, avoiding early-morning outdoor activity, and going outside after rain when pollen levels are lower. They should check pollen forecasts, close windows and doors when counts are high, and consider starting allergy medication before symptoms begin if high pollen is expected. After being outside, showering, changing clothes, avoiding outdoor laundry drying, and wearing a face mask for yard work can help limit pollen contact.",
]
query_embeddings = model.encode_query(QUERIES, batch_size=1, convert_to_tensor=True)
document_embeddings = model.encode_document(DOCUMENTS, batch_size=1, convert_to_tensor=True)

scores = model.similarity(query_embeddings, document_embeddings)
print("Similarity scores:")
print(f"{'':>4}" + "".join(f"d[{i}]".rjust(10) for i in range(scores.shape[1])))
for query_index, row in enumerate(scores):
    print(f"q[{query_index}]" + "".join(f"{score.item():>10.4f}" for score in row))
```

<details>
<summary>Sentence Transformers Expected Output</summary>

```text
Similarity scores:
          d[0]      d[1]      d[2]      d[3]
q[0]    0.7852    0.0496    0.0115   -0.0299
q[1]    0.0457    0.6562   -0.0645    0.0452
q[2]   -0.0016   -0.0530    0.6602    0.1123
q[3]   -0.0170   -0.0036    0.1147    0.8008
```

</details>

### Transformers

Use Transformers when you want manual control over tokenization, pooling, or batching.

```python
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

MODEL_ID = "nvidia/Nemotron-3-Embed-8B-BF16"
MAX_LENGTH = 32768
BATCH_SIZE = 1
DTYPE = torch.bfloat16
ATTN_IMPLEMENTATION = "flash_attention_2"

QUERIES = [
    "Write a Python function that counts the frequency of each element in a list of lists.",
    "Write a function that orders a dictionary with tuple keys by the product of each key's tuple values.",
    "What symptoms and common triggers help distinguish eczema from other inflammatory skin conditions?",
    "How can someone reduce exposure to pollen during allergy season?",
]

DOCUMENTS = [
    "def frequency_lists(list1):\n    flattened = [item for sublist in list1 for item in sublist]\n    counts = {}\n    for item in flattened:\n        if item in counts:\n            counts[item] += 1\n        else:\n            counts[item] = 1\n    return counts",
    "def sort_dict_item(test_dict):\n    return {key: test_dict[key] for key in sorted(test_dict.keys(), key=lambda ele: ele[0] * ele[1])}",
    "Eczema commonly causes itchy, dry, inflamed patches of skin. The affected areas may look red, scaly, cracked, or darker than the surrounding skin depending on skin tone. Symptoms can flare after exposure to irritants, allergens, stress, or changes in weather.",
    "People with pollen allergy can reduce exposure by staying indoors on dry, windy days, avoiding early-morning outdoor activity, and going outside after rain when pollen levels are lower. They should check pollen forecasts, close windows and doors when counts are high, and consider starting allergy medication before symptoms begin if high pollen is expected. After being outside, showering, changing clothes, avoiding outdoor laundry drying, and wearing a face mask for yard work can help limit pollen contact.",
]

def average_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    last_hidden = last_hidden_state.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

if not torch.cuda.is_available():
    raise RuntimeError("CUDA is required for practical BF16 inference.")

device = torch.device("cuda")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, padding_side="left")
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModel.from_pretrained(
    MODEL_ID,
    dtype=DTYPE,
    attn_implementation=ATTN_IMPLEMENTATION,
).to(device)
model.eval()

def encode_texts(texts: list[str]) -> torch.Tensor:
    embedding_batches = []

    for start in range(0, len(texts), BATCH_SIZE):
        encoded = tokenizer(
            texts[start : start + BATCH_SIZE],
            max_length=MAX_LENGTH,
            truncation=True,
            padding=True,
            return_tensors="pt",
        )
        encoded = {name: tensor.to(device) for name, tensor in encoded.items()}

        with torch.inference_mode():
            output = model(**encoded)
            pooled = average_pool(output.last_hidden_state, encoded["attention_mask"])
            embeddings = F.normalize(pooled, p=2, dim=-1)

        embedding_batches.append(embeddings.detach().cpu().to(torch.float32))

    return torch.cat(embedding_batches, dim=0)

embeddings = encode_texts(
    ["query: " + query for query in QUERIES]
    + ["passage: " + doc for doc in DOCUMENTS]
)
query_embeddings = embeddings[: len(QUERIES)]
document_embeddings = embeddings[len(QUERIES) :]

scores = query_embeddings @ document_embeddings.T
print("Similarity scores:")
print(f"{'':>4}" + "".join(f"d[{i}]".rjust(10) for i in range(scores.shape[1])))
for query_index, row in enumerate(scores):
    print(f"q[{query_index}]" + "".join(f"{score.item():>10.4f}" for score in row))
```

<details>
<summary>Transformers Expected Output</summary>

```text
Similarity scores:
          d[0]      d[1]      d[2]      d[3]
q[0]    0.7856    0.0496    0.0113   -0.0298
q[1]    0.0458    0.6505   -0.0642    0.0451
q[2]   -0.0018   -0.0529    0.6609    0.1124
q[3]   -0.0171   -0.0034    0.1151    0.8004
```

</details>

### vLLM Dependencies

For BF16, use `vllm==0.25.0` for `/v2/embed` serving. NVIDIA also validated `vllm serve "$MODEL_ID"` with `vllm/vllm-openai:v0.21.0`, `nvcr.io/nvidia/vllm:26.06-py3`, and `vllm/vllm-openai:v0.24.0` for this checkpoint.

```bash
pip install --upgrade "vllm==0.25.0" openai requests numpy
```

**FP8 acceleration:** On NVIDIA Hopper and Ada Lovelace GPUs, enable FP8 in vLLM online with `--quantization fp8_per_tensor`, or offline with `quantization="fp8_per_tensor"` in `LLM(...)`. Validated with vLLM `0.25.0` on H100; accuracy matched BF16.



### vLLM Offline Python

Use the offline Python API when you want local vLLM inference without running an HTTP server. `LLM.embed` accepts formatted strings, so add the `query: ` and `passage: ` prefixes manually.

<details>
<summary>vLLM Offline Python Example</summary>

```python
import numpy as np
from vllm import LLM

MODEL_ID = "nvidia/Nemotron-3-Embed-8B-BF16"

QUERIES = [
    "Write a Python function that counts the frequency of each element in a list of lists.",
    "Write a function that orders a dictionary with tuple keys by the product of each key's tuple values.",
    "What symptoms and common triggers help distinguish eczema from other inflammatory skin conditions?",
    "How can someone reduce exposure to pollen during allergy season?",
]

DOCUMENTS = [
    "def frequency_lists(list1):\n    flattened = [item for sublist in list1 for item in sublist]\n    counts = {}\n    for item in flattened:\n        if item in counts:\n            counts[item] += 1\n        else:\n            counts[item] = 1\n    return counts",
    "def sort_dict_item(test_dict):\n    return {key: test_dict[key] for key in sorted(test_dict.keys(), key=lambda ele: ele[0] * ele[1])}",
    "Eczema commonly causes itchy, dry, inflamed patches of skin. The affected areas may look red, scaly, cracked, or darker than the surrounding skin depending on skin tone. Symptoms can flare after exposure to irritants, allergens, stress, or changes in weather.",
    "People with pollen allergy can reduce exposure by staying indoors on dry, windy days, avoiding early-morning outdoor activity, and going outside after rain when pollen levels are lower. They should check pollen forecasts, close windows and doors when counts are high, and consider starting allergy medication before symptoms begin if high pollen is expected. After being outside, showering, changing clothes, avoiding outdoor laundry drying, and wearing a face mask for yard work can help limit pollen contact.",
]

def main():
    llm = LLM(model=MODEL_ID)
    texts = ["query: " + query for query in QUERIES] + [
        "passage: " + doc for doc in DOCUMENTS
    ]
    outputs = llm.embed(texts, use_tqdm=False)
    embeddings = np.array(
        [output.outputs.embedding for output in outputs],
        dtype=np.float32,
    )

    query_embeddings = embeddings[: len(QUERIES)]
    document_embeddings = embeddings[len(QUERIES) :]

    scores = query_embeddings @ document_embeddings.T
    print("Similarity scores:")
    print(f"{'':>4}" + "".join(f"d[{i}]".rjust(10) for i in range(scores.shape[1])))
    for query_index, row in enumerate(scores):
        print(f"q[{query_index}]" + "".join(f"{score:>10.4f}" for score in row))


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>vLLM Offline Python Expected Output</summary>

```text
Similarity scores:
          d[0]      d[1]      d[2]      d[3]
q[0]    0.7846    0.0489    0.0118   -0.0301
q[1]    0.0454    0.6505   -0.0645    0.0455
q[2]   -0.0018   -0.0531    0.6611    0.1120
q[3]   -0.0166   -0.0040    0.1148    0.7983
```

</details>

### vLLM Online Serving

```bash
MODEL_ID=nvidia/Nemotron-3-Embed-8B-BF16

vllm serve "$MODEL_ID"
```

vLLM defaults to port `8000`. Add host and port when you need an explicit bind address or a non-default port:

```bash
vllm serve "$MODEL_ID" --host 0.0.0.0 --port 8000
```

If you serve the Hugging Face model ID, the served model name defaults to `nvidia/Nemotron-3-Embed-8B-BF16`. If you serve a local checkpoint path, vLLM still reads the model config and weights from that path; `--served-model-name` only sets the model name accepted by API requests.

```bash
MODEL_PATH=/path/to/local/Nemotron-3-Embed-8B-BF16
vllm serve "$MODEL_PATH" --host 0.0.0.0 --port 8000 --served-model-name nvidia/Nemotron-3-Embed-8B-BF16
```

With `--served-model-name`, client requests continue to use `MODEL = "nvidia/Nemotron-3-Embed-8B-BF16"`. If you omit it, use the served name reported by `/v1/models` in client requests.

#### Recommended Retrieval Endpoint

After the server is running, use `/v2/embed` for retrieval. Send raw query and document strings. `input_type` applies the saved query and document prompts:

```python
import numpy as np
import requests

MODEL = "nvidia/Nemotron-3-Embed-8B-BF16"
URL = "http://localhost:8000/v2/embed"

QUERIES = [
    "Write a Python function that counts the frequency of each element in a list of lists.",
    "Write a function that orders a dictionary with tuple keys by the product of each key's tuple values.",
    "What symptoms and common triggers help distinguish eczema from other inflammatory skin conditions?",
    "How can someone reduce exposure to pollen during allergy season?",
]

DOCUMENTS = [
    "def frequency_lists(list1):\n    flattened = [item for sublist in list1 for item in sublist]\n    counts = {}\n    for item in flattened:\n        if item in counts:\n            counts[item] += 1\n        else:\n            counts[item] = 1\n    return counts",
    "def sort_dict_item(test_dict):\n    return {key: test_dict[key] for key in sorted(test_dict.keys(), key=lambda ele: ele[0] * ele[1])}",
    "Eczema commonly causes itchy, dry, inflamed patches of skin. The affected areas may look red, scaly, cracked, or darker than the surrounding skin depending on skin tone. Symptoms can flare after exposure to irritants, allergens, stress, or changes in weather.",
    "People with pollen allergy can reduce exposure by staying indoors on dry, windy days, avoiding early-morning outdoor activity, and going outside after rain when pollen levels are lower. They should check pollen forecasts, close windows and doors when counts are high, and consider starting allergy medication before symptoms begin if high pollen is expected. After being outside, showering, changing clothes, avoiding outdoor laundry drying, and wearing a face mask for yard work can help limit pollen contact.",
]

def embed(input_type: str, texts: list[str]) -> np.ndarray:
    response = requests.post(
        URL,
        json={
            "model": MODEL,
            "input_type": input_type,
            "texts": texts,
            "embedding_types": ["float"],
            "truncate": "END",
        },
        timeout=120,
    )
    response.raise_for_status()
    return np.array(response.json()["embeddings"]["float"], dtype=np.float32)

query_embeddings = embed("query", QUERIES)
document_embeddings = embed("document", DOCUMENTS)

scores = query_embeddings @ document_embeddings.T
print("Similarity scores:")
print(f"{'':>4}" + "".join(f"d[{i}]".rjust(10) for i in range(scores.shape[1])))
for query_index, row in enumerate(scores):
    print(f"q[{query_index}]" + "".join(f"{score:>10.4f}" for score in row))
```

<details>
<summary>Recommended Retrieval Endpoint Expected Output</summary>

```text
Similarity scores:
          d[0]      d[1]      d[2]      d[3]
q[0]    0.7848    0.0489    0.0117   -0.0298
q[1]    0.0454    0.6512   -0.0644    0.0455
q[2]   -0.0021   -0.0529    0.6614    0.1121
q[3]   -0.0169   -0.0033    0.1151    0.7989
```

</details>

You can also use the OpenAI-compatible `/v1/embeddings` endpoint. For those requests, pass strings in `input` and manually prefix them with `query: ` or `passage: `.

### Expected Configuration Warning

When this checkpoint is loaded by Transformers, whether directly or through Sentence Transformers or vLLM, the following warning may appear:

```text
[transformers] Unrecognized keys in `rope_parameters` for 'rope_type'='yarn': {'apply_yarn_scaling'}
```

This warning is expected and does not prevent model loading or inference. `apply_yarn_scaling` is retained as a temporary vLLM compatibility field that preserves the checkpoint's intended long-context RoPE behavior. Do not remove it from `config.json`. The upstream compatibility work is tracked in [vLLM issue #48621](https://github.com/vllm-project/vllm/issues/48621).


## Software Integration:
**Runtime Engine(s):**  PyTorch, vLLM<br>

**Supported Hardware Microarchitecture Compatibility:** <br>
- NVIDIA Ampere
- NVIDIA Blackwell
- NVIDIA Hopper

**Supported Operating System(s):** <br>
* Linux <br>

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment. <br>

## Model Version(s):
**Nemotron-3-Embed-8B-BF16** <br>

## Training, Testing, and Evaluation Datasets:

### Dataset Overview:
**Total Size:** 50M+ data samples<br>
**Dataset Partition:** Training [100%], Testing [N/A — evaluation benchmarks used separately], Validation [N/A — evaluation benchmarks used separately].

Model training was conducted using publicly available, commercially permissible datasets and synthetically generated datasets. Synthetic datasets were created either by generating queries from seed documents or by generating complete question–answer pairs through LLM-based prompting using the LLMs listed below.<br>

### Public Datasets:

| Dataset name | Reference |
| --- | --- |
| MIRACL | [https://huggingface.co/datasets/miracl/miracl](https://huggingface.co/datasets/miracl/miracl) |
| MLDR | [https://huggingface.co/datasets/Shitao/MLDR](https://huggingface.co/datasets/Shitao/MLDR) |
| HotpotQA | [https://hotpotqa.github.io/](https://hotpotqa.github.io/) |
| NQ | [https://huggingface.co/datasets/sentence-transformers/embedding-training-data](https://huggingface.co/datasets/sentence-transformers/embedding-training-data) |
| SQuAD | [https://rajpurkar.github.io/SQuAD-explorer/](https://rajpurkar.github.io/SQuAD-explorer/) |
| Stack Exchange | [https://archive.org/details/stackexchange](https://archive.org/details/stackexchange) |
| HoVer | [https://hover-nlp.github.io/](https://hover-nlp.github.io/) |
| TAT-QA | [https://huggingface.co/datasets/next-tat/TAT-QA](https://huggingface.co/datasets/next-tat/TAT-QA) |
| FinQA | [https://github.com/czyssrs/FinQA/tree/main](https://github.com/czyssrs/FinQA/tree/main) |
| PubMedQA | [https://huggingface.co/datasets/qiaojin/PubMedQA/viewer/pqa_labeled](https://huggingface.co/datasets/qiaojin/PubMedQA/viewer/pqa_labeled) |
| MedQuAD | [https://github.com/abachaa/MedQuAD](https://github.com/abachaa/MedQuAD) |
| JaQuAD | [https://huggingface.co/datasets/SkelterLabsInc/JaQuAD](https://huggingface.co/datasets/SkelterLabsInc/JaQuAD) |
| coir_apps | [https://huggingface.co/datasets/CoIR-Retrieval/apps](https://huggingface.co/datasets/CoIR-Retrieval/apps) |
| coir_cosqa | [https://huggingface.co/datasets/CoIR-Retrieval/cosqa](https://huggingface.co/datasets/CoIR-Retrieval/cosqa) |
| coir_stackoverflow_qa | [https://huggingface.co/datasets/CoIR-Retrieval/stackoverflow-qa](https://huggingface.co/datasets/CoIR-Retrieval/stackoverflow-qa) |
| coir_codetrans_dl | [https://huggingface.co/datasets/CoIR-Retrieval/codetrans-dl](https://huggingface.co/datasets/CoIR-Retrieval/codetrans-dl) |
| coir_codetrans_contest | [https://huggingface.co/datasets/CoIR-Retrieval/codetrans-contest](https://huggingface.co/datasets/CoIR-Retrieval/codetrans-contest) |
| synthetic_text2sql | [https://huggingface.co/datasets/CoIR-Retrieval/synthetic-text2sql](https://huggingface.co/datasets/CoIR-Retrieval/synthetic-text2sql) |
| SWE-bench | [https://huggingface.co/datasets/princeton-nlp/SWE-bench/viewer/default/train](https://huggingface.co/datasets/princeton-nlp/SWE-bench/viewer/default/train) |
| MLQA | [https://github.com/facebookresearch/MLQA](https://github.com/facebookresearch/MLQA) |
| SpartQA | [https://github.com/HLR/SpartQA_generation](https://github.com/HLR/SpartQA_generation) |
| Winogrande | [https://github.com/allenai/winogrande](https://github.com/allenai/winogrande) |
| TempReason | [https://huggingface.co/datasets/tonytan48/TempReason](https://huggingface.co/datasets/tonytan48/TempReason) |
| PAQ | [https://huggingface.co/datasets/sentence-transformers/embedding-training-data](https://huggingface.co/datasets/sentence-transformers/embedding-training-data) |
| Wikipedia | [https://huggingface.co/datasets/wikimedia/wikipedia](https://huggingface.co/datasets/wikimedia/wikipedia) |
| CCNews | [https://commoncrawl.org/2016/10/news-dataset-available/](https://commoncrawl.org/2016/10/news-dataset-available/) |
| S2ORC | [https://huggingface.co/datasets/sentence-transformers/embedding-training-data](https://huggingface.co/datasets/sentence-transformers/embedding-training-data) |
| Reddit | [https://huggingface.co/datasets/sentence-transformers/reddit-title-body](https://huggingface.co/datasets/sentence-transformers/reddit-title-body) |

### Synthetic Datasets:

Synthetic query-document pairs were generated either from scratch or by using seed datasets to generate queries with the models listed below.

<table>
  <tr>
    <th>LLMs used to generate synthetic datasets:</th>
  </tr>
  <tr>
    <td>Qwen/Qwen3-Next-80B-A3B-Instruct<br>Qwen/Qwen3-235B-A22B<br>Qwen/Qwen3.5-397B-A17B<br>Qwen/Qwen3.6-27B<br>Qwen/Qwen3.6-35B-A3B</td>
  </tr>
  <tr>
    <td>google/gemma-4-31B-it</td>
  </tr>
  <tr>
    <td>openai/gpt-oss-120b<br>openai/gpt-oss-20b</td>
  </tr>
  <tr>
    <td>nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16<br>nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4</td>
  </tr>
</table>

<table>
  <tr>
    <th colspan="2">Seed Datasets</th>
  </tr>
  <tr>
    <th>Dataset</th>
    <th>Reference</th>
  </tr>
  <tr>
    <td>FinePdfs</td>
    <td><a href="https://huggingface.co/datasets/HuggingFaceFW/finepdfs">https://huggingface.co/datasets/HuggingFaceFW/finepdfs</a></td>
  </tr>
  <tr>
    <td>CentralActs</td>
    <td><a href="https://zenodo.org/records/5088102">https://zenodo.org/records/5088102</a></td>
  </tr>
  <tr>
    <td>BRIGHT</td>
    <td><a href="https://huggingface.co/datasets/xlangai/BRIGHT">https://huggingface.co/datasets/xlangai/BRIGHT</a></td>
  </tr>
  <tr>
    <td>MultiHiertt</td>
    <td><a href="https://github.com/psunlpgroup/MultiHiertt">https://github.com/psunlpgroup/MultiHiertt</a></td>
  </tr>
</table>


### Training Dataset:

#### Data Modality:
* Text <br>

#### Training Data Size:

**Text Training Data Size:** 50M+ data samples <br>

**Data Collection Method by dataset:** Hybrid: Human, Automated, Synthetic <br>

**Labeling Method by dataset:** Hybrid: Human, Automated, Synthetic <br>

**Properties:** Model training was conducted on text datasets using question–passage pairs from publicly available, commercially permissible datasets and synthetically generated datasets. <br>


### Testing Dataset:

**Data Collection Method by dataset:** Not Applicable <br>

**Labeling Method by dataset:** Not Applicable <br>

**Properties:** Not Applicable. Model quality was assessed using the evaluation benchmark datasets described in the Evaluation Dataset subsection. <br>


### Evaluation Dataset:

**Data Collection Method by dataset:** Hybrid: Human, Automated, Synthetic <br>

**Labeling Method by dataset:** Hybrid: Human, Automated, Synthetic <br>

**Properties:** This model is evaluated on 16 public tasks on [Retrieval Embedding Benchmark (RTEB)](https://huggingface.co/blog/rteb), a new benchmark designed to reliably evaluate the retrieval accuracy of embedding models for real-world applications. More details on RTEB can be found on their [leaderboard](https://huggingface.co/spaces/mteb/leaderboard?benchmark_name=RTEB%28beta%29).

We also evaluated the model on the [MMTEB (Retrieval) benchmark datasets](https://huggingface.co/spaces/mteb/leaderboard) ([paper](https://arxiv.org/pdf/2502.13595)), and on the eight text datasets (extracted via OCR) from the [ViDoRe-V3 benchmark](https://mteb-leaderboard.hf.space/benchmark/ViDoRe(v3)).

We set the model sequence length to 4096 for the evaluation results below.

<table>
  <tr>
    <th colspan="4">Text Retrieval benchmarks (chunk retrieval) - Avg. NDCG@10</th>
  </tr>
  <tr>
    <th>Model Name</th>
    <th>RTEB 16</th>
    <th>ViDoRe-V3 text</th>
    <th>MMTEB (Retrieval)</th>
  </tr>
  <tr>
    <td>llama-nemotron-embed-vl-1b-v2</td>
    <td>61.98</td>
    <td>52.54</td>
    <td>59.71</td>
  </tr>
  <tr>
    <td>Nemotron-3-Embed-1B-BF16</td>
    <td>72.38</td>
    <td>57.74</td>
    <td>71.04</td>
  </tr>
  <tr>
    <td>Nemotron-3-Embed-8B-BF16</td>
    <td>78.46</td>
    <td>60.60</td>
    <td>75.45</td>
  </tr>
</table>


## Inference:
**Acceleration Engine:** PyTorch, vLLM <br>
**Test Hardware:**
- NVIDIA Ampere - A100 80GB
- NVIDIA Hopper - H100 80GB


## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse. <br>

For more detailed information on ethical considerations for this model, please see the Model Card++ Bias, Explainability, Safety & Security, and Privacy Subcards. <br>

Please report model quality, risk, security vulnerabilities or NVIDIA AI concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/). <br>

## Bias

| Field | Response |
| ----- | ----- |
| Participation considerations from adversely impacted groups [protected classes](https://www.senate.ca.gov/content/protected-classes) in model design and testing: | None |
| Measures taken to mitigate against unwanted bias: | None |
| Bias Metric (If Measured): | None |

## Explainability

| Field | Response |
| ----- | ----- |
| Intended Task/Domain: | Passage and query embedding for question and answer retrieval |
| Model Type: | Transformer encoder |
| Intended Users: | Generative AI creators working with conversational AI models - users who want to build a multilingual question and answer application over a large text corpus, leveraging the latest dense retrieval technologies. |
| Output: | Array of float numbers (Dense Vector Representation for the input text) |
| Describe how the model works: | Model transforms the tokenized input text into a dense vector representation. |
| Name the adversely impacted groups this has been tested to deliver comparable outcomes regardless of: | Not Applicable |
| Technical Limitations & Mitigation: | The model’s max sequence length is 32768. Therefore, longer text inputs should be truncated. |
| Verified to have met prescribed NVIDIA quality standards: | Yes |
| Performance Metrics: | Accuracy, Throughput, and Latency |
| Potential Known Risks: | This model does not always guarantee to retrieve the correct passage(s) for a given query. |
| Licensing: | This model and its associated configuration files are licensed under the [OpenMDW License Agreement, version 1.1 (OpenMDW-1.1)](https://openmdw.ai/license/1-1/). Additional Information: Built with [Ministral-3-8B-Instruct-2512](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) which is released under Apache 2.0. |

## Privacy

| Field | Response |
| ----- | ----- |
| Generatable or reverse engineerable personal data? | None |
| Was consent obtained for any personal data used? | Not Applicable |
| Personal data used to create this model? | None Known |
| How often is the dataset reviewed? | Before Every Release |
| Is there provenance for all datasets used in training? | Yes |
| Does data labeling (annotation, metadata) comply with privacy laws? | Yes |
| Was data from user interactions with the AI model (e.g. user input and prompts) used to train the model? | Yes |
| Is data compliant with data subject requests for data correction or removal, if such a request was made? | No, not possible with externally-sourced data. |
| Applicable Privacy Policy | https://www.nvidia.com/en-us/about-nvidia/privacy-policy/ |

## Safety

| Field | Response |
| ----- | ----- |
| Model Application(s): | Text Embedding for Retrieval |
| Describe the physical safety impact (if present). | Not Applicable |
| Use Case Restrictions: | This model and its associated configuration files are licensed under the [OpenMDW License Agreement, version 1.1 (OpenMDW-1.1)](https://openmdw.ai/license/1-1/). Additional Information: Built with [Ministral-3-8B-Instruct-2512](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) which is released under Apache 2.0. |
| Model and dataset restrictions: | The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development. Restrictions enforce dataset access during training, and dataset license constraints adhered to. |
