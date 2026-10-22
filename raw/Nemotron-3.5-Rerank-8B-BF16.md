---
license: other
license_name: openmdw-1.1
license_link: https://openmdw.ai/license/1-1/
base_model:
  - mistralai/Ministral-3-8B-Instruct-2512-BF16
tags:
  - reranker
  - cross-encoder
  - visual-document-retrieval
  - multimodal reranking
  - semantic-search
  - rag
  - transformers
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
pipeline_tag: text-ranking
---

# Nemotron-3.5-Rerank-8B-BF16 Overview

## Description:  
**Nemotron-3.5-Rerank-8B-BF16** was developed by NVIDIA for multilingual and multimodal question-answering retrieval. It is a world-class reranker optimized to produce a logit representing the relevance of a document to a text query. Documents may contain text, page images, or both, including charts, tables, and infographics. The model can be integrated into classical or agentic vision RAG pipelines. For text retrieval, the model was evaluated across 34 languages: English, Arabic, Assamese, Bengali, Bulgarian, Chinese, Danish, Dutch, Finnish, French, German, Hindi, Hinglish, Indonesian, Italian, Japanese, Korean, Malay, Marathi, Nepali, Norwegian, Persian, Portuguese, Romanian, Russian, Spanish, Swahili, Swedish, Tamil, Telugu, Thai, Ukrainian, Urdu, and Vietnamese. For image retrieval, it was evaluated across 18 languages: Arabic, Bengali, Chinese, English, Persian, Finnish, French, German, Hindi, Indonesian, Japanese, Korean, Russian, Spanish, Swahili, Telugu, Thai, and Yoruba. The model may support additional languages beyond these evaluation sets.

Nemotron-3.5-Rerank-8B-BF16 achieves state-of-the-art results on the new [ViDoRe v3.1 Reranking leaderboard](https://leaderboard.mteb.org/benchmark/ViDoRe(v3.1)) as of October 20, 2026. Read more details in our [Blog Post](https://huggingface.co/blog/nvidia/nemotron-retriever-world-class-agentic-retrieval).

This model is ready for commercial or non-commercial use.


### License/Terms of Use:

**Governing Download Terms:** Use of the model is governed by the [OpenMDW License Agreement, version 1.1 (OpenMDW-1.1)](https://openmdw.ai/license/1-1/). <br>
**Additional Information:** The [Ministral-3-8B-Instruct-2512-BF16](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-BF16) base model is governed by the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt).


### Deployment Geography:
Global

### Use Case:  
The reranking model serves as a key component of a multimodal retrieval system, such as a vision RAG pipeline, where it helps improve overall retrieval accuracy. A multimodal retrieval system typically uses a multimodal embedding model (dense retrieval) to return a set of potentially relevant documents given an input query. The reranking model then evaluates these candidate documents in greater detail and reorders them based on their relevance to the query, producing a final ranking. By refining the initial retrieval results, the reranking stage can improve the precision of the retrieved documents and ultimately lead to more accurate downstream responses.  


### Release Date:
Hugging Face 10/20/2026 via https://huggingface.co/nvidia/Nemotron-3.5-Rerank-8B-BF16


## Model Architecture:   
**Architecture Type:** Transformer <br>
**Network Architecture:** The released model contains a Pixtral-based vision encoder and a bidirectional Ministral3 language-model tower. Training proceeded in two stages. In the first stage, an 8B reranker checkpoint derived from the [Ministral-3-8B-Instruct-2512-BF16](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-BF16) backbone was trained on a blend of text-only datasets. In the second stage, the 8B reranker model initialized from the first-stage checkpoint was trained on image and combined image-text datasets.

**Number of Model Parameters:** 8.38B

## Input:  
**Input Type(s):** Text, Image <br>
**Input Format(s):** Text: String; Image: Red, Green, Blue (RGB) <br>
**Input Parameters:** Text: One-Dimensional (1D), Image: Two-Dimensional (2D) <br>
**Other Properties Related to Input:** Each input is one text query paired with one document. The document may be an image, text, or a combination of image and text. The default image `longest_edge` is 1,120 pixels and can be increased to 1,540. The maximum context length is 32,768 tokens.

## Output:  
**Output Type(s):** Floats <br>
**Output Format:** List of Floats <br>
**Output Parameters:** One-Dimensional (1D) <br>
**Other Properties Related to Output:** Each output value corresponds to a raw logit. The higher the value, the more relevant a document is to a given query.

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA's hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.

## Installation

Create a Python 3.12 environment for the Transformers and Sentence Transformers examples:

```bash
uv venv --python 3.12 .venv-transformers
source .venv-transformers/bin/activate
uv pip install torch "transformers==5.20.0" accelerate pillow
```

And to install FlashAttention 2, you can either build it from source like so:

```bash
uv pip install packaging ninja
uv pip install flash-attn --no-build-isolation
```
or use a pre-built FlashAttention 2 kernel via the `kernels` package:
```bash
uv pip install kernels
```

The examples use Flash Attention 2 and were tested with `transformers==5.20.0`. The checkpoint uses `TokenizersBackend` and does not require `mistral_common`.

Model training and evaluations used `transformers==5.12.1`. Example outputs can vary with hardware and runtime.

### Transformers Usage

Score query/document pairs containing text, images, or both.

```python
import torch
from transformers import AutoModelForSequenceClassification, AutoProcessor
from transformers.image_utils import load_image

MODEL_PATH = "nvidia/Nemotron-3.5-Rerank-8B-BF16"  # Or a local checkpoint directory.
IMAGE_URL = "https://docs.nvidia.com/nemo-framework/user-guide/24.07/_images/nemo-llm-mm-stack.png"
MAX_MODEL_LEN = 32768
DEVICE = "cuda:0"


def main() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("This bfloat16 example requires a CUDA GPU.")

    processor = AutoProcessor.from_pretrained(MODEL_PATH)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        dtype=torch.bfloat16,
        device_map={"": DEVICE},
        attn_implementation="flash_attention_2",
    ).eval()

    def rerank(
        query: str,
        documents: list[dict],
    ) -> torch.Tensor:
        scores = []
        for document in documents:
            document_content = []
            if document.get("text") is not None:
                document_content.append({"type": "text", "text": document["text"]})
            if document.get("image") is not None:
                document_content.append({"type": "image", "image": document["image"]})

            inputs = processor.apply_chat_template(
                [
                    {
                        "role": "query",
                        "content": [{"type": "text", "text": query}],
                    },
                    {"role": "document", "content": document_content},
                ],
                tokenize=True,
                add_generation_prompt=False,
                return_dict=True,
                return_tensors="pt",
            )
            if inputs["input_ids"].shape[-1] > MAX_MODEL_LEN:
                raise ValueError("Input exceeds 32768 tokens; shorten the text or resize the image.")
            inputs = inputs.to(DEVICE)

            if inputs.get("pixel_values") is not None:
                inputs["pixel_values"] = inputs["pixel_values"].to(model.dtype)

            with torch.inference_mode():
                score = model(**inputs).logits.squeeze().float()
            scores.append(score)

        # Higher scores indicate greater predicted relevance.
        return torch.stack(scores)

    query = "What is NVIDIA NeMo Framework?"
    image = load_image(IMAGE_URL)
    nemo_text = "NeMo Framework offers comprehensive functionalities for developing both LLMs and Multimodal Models."
    biology_text = "A biological foundation model designed to analyze and generate DNA, RNA, and protein sequences."

    documents = [
        {
            "name": "nemo_image_text",
            "text": nemo_text,
            "image": image,
        },
        {
            "name": "nemo_text",
            "text": nemo_text,
            "image": None,
        },
        {
            "name": "nemo_image",
            "text": None,
            "image": image,
        },
        {
            "name": "biology_text",
            "text": biology_text,
            "image": None,
        },
    ]

    scores = rerank(
        query=query,
        documents=documents,
    )

    ranking = torch.argsort(scores, descending=True)

    for rank, document_index in enumerate(ranking.tolist(), start=1):
        document = documents[document_index]
        print(f"Rank {rank}: document={document['name']}, score={scores[document_index].item():.6f}")


if __name__ == "__main__":
    main()
```

Example output (higher scores indicate greater predicted relevance; values can vary with hardware and runtime):
```text
Rank 1: document=nemo_image_text, score=-1.799218
Rank 2: document=nemo_image, score=-1.823747
Rank 3: document=nemo_text, score=-2.100960
Rank 4: document=biology_text, score=-2.964395
```

### Sentence Transformers Usage

In the same environment, install Sentence Transformers:

```bash
uv pip install "sentence-transformers[image]==6.1.0"
```

Rank text, images, or combined text and images. Image URLs are loaded automatically.

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "nvidia/Nemotron-3.5-Rerank-8B-BF16",
    device="cuda",
    model_kwargs={"dtype": "bfloat16", "attn_implementation": "flash_attention_2"},
)

query = "What is NVIDIA NeMo Framework?"
image_url = "https://docs.nvidia.com/nemo-framework/user-guide/24.07/_images/nemo-llm-mm-stack.png"
nemo_text = "NeMo Framework offers comprehensive functionalities for developing both LLMs and Multimodal Models."
biology_text = "A biological foundation model designed to analyze and generate DNA, RNA, and protein sequences."
document_names = ["nemo_image_text", "nemo_text", "nemo_image", "biology_text"]
documents = [
    {"image": image_url, "text": nemo_text},
    nemo_text,
    {"image": image_url},
    biology_text,
]

rankings = model.rank(query, documents, batch_size=1)
for rank, result in enumerate(rankings, start=1):
    name = document_names[result["corpus_id"]]
    print(f"Rank {rank}: document={name}, score={result['score']:.6f}")
```

Example output (BF16 scores can vary slightly with hardware, batching, and runtime):

```text
Rank 1: document=nemo_image_text, score=-1.804688
Rank 2: document=nemo_image, score=-1.820312
Rank 3: document=nemo_text, score=-2.109375
Rank 4: document=biology_text, score=-2.968750
```

### vLLM Usage

Generate relevance scores for text, image, and combined image-text documents with the vLLM Python API or an HTTP server.

#### Dependencies

Create a separate Python environment for vLLM. Set `MODEL_PATH` to the Hugging Face model ID or a local checkpoint directory:

```bash
uv venv --python 3.12 .venv-vllm
source .venv-vllm/bin/activate
uv pip install "vllm==0.32.0" "transformers==5.19.0" pillow httpx
export MODEL_PATH="nvidia/Nemotron-3.5-Rerank-8B-BF16"
```

These examples use vLLM 0.32.0, which requires `transformers>=5.16.1,<5.20.0`. Keep the vLLM environment separate from the Transformers 5.20.0 environment above. Image preprocessing uses the checkpoint's configured longest-edge limit of 1,120 pixels. The 32,768-token context includes both text and image tokens.

#### Offline Python

Each input scores one query against one document. Pass the query text with the `query` role and the document text and/or image placeholder with the `document` role to the model's chat template. The template renders the prompt and inserts the image placeholder. Pass the image pixels separately through `multi_modal_data`:

```python
import os

from transformers.image_utils import load_image
from vllm import LLM

MODEL_PATH = os.environ["MODEL_PATH"]
DOCUMENT_NAMES = ["nemo_image_text", "nemo_text", "nemo_image", "biology_text"]
IMAGE_URL = "https://docs.nvidia.com/nemo-framework/user-guide/24.07/_images/nemo-llm-mm-stack.png"
MAX_MODEL_LEN = 32768


def make_input(tokenizer, query, document):
    text = document["text"]
    image = document["image"]
    content = []
    if text is not None:
        content.append({"type": "text", "text": text})
    if image is not None:
        content.append({"type": "image"})

    messages = [
        {
            "role": "query",
            "content": [{"type": "text", "text": query}],
        },
        {
            "role": "document",
            "content": content,
        },
    ]

    # The template emits the image placeholder and escapes literal
    # control-token strings in user text.
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )

    request = {"prompt": prompt}
    if image is not None:
        request["multi_modal_data"] = {"image": image}
    return request


def main() -> None:
    model = LLM(
        model=MODEL_PATH,
        compilation_config={"compile_mm_encoder": True},
        runner="pooling",
        dtype="bfloat16",
        limit_mm_per_prompt={"image": 1},
        max_model_len=MAX_MODEL_LEN,
        pooler_config={
            "seq_pooling_type": "MEAN",
            "use_activation": False,
        },
    )
    tokenizer = model.get_tokenizer()

    query = "What is NVIDIA NeMo Framework?"
    image = load_image(IMAGE_URL).convert("RGB")
    nemo_text = "NeMo Framework offers comprehensive functionalities for developing both LLMs and Multimodal Models."
    biology_text = "A biological foundation model designed to analyze and generate DNA, RNA, and protein sequences."

    documents = [
        {"text": nemo_text, "image": image},
        {"text": nemo_text, "image": None},
        {"text": None, "image": image},
        {"text": biology_text, "image": None},
    ]

    inputs = [make_input(tokenizer, query, document) for document in documents]
    outputs = model.encode(inputs, pooling_task="classify")
    scores = [(name, output.outputs.data.item()) for name, output in zip(DOCUMENT_NAMES, outputs)]
    scores.sort(key=lambda item: item[1], reverse=True)

    for rank, (name, score) in enumerate(scores, start=1):
        print(f"Rank {rank}: document={name}, score={score:.4f}")


if __name__ == "__main__":
    main()
```
Example output (higher scores indicate greater predicted relevance; values can vary with hardware and runtime):

```text
Rank 1: document=nemo_image_text, score=-1.8064
Rank 2: document=nemo_image, score=-1.8161
Rank 3: document=nemo_text, score=-2.1058
Rank 4: document=biology_text, score=-2.9541
```

#### Online Serving

Use the same environment and `MODEL_PATH` from the dependencies section. Start a local HTTP server with the checkpoint's chat template and structured content blocks:

```bash
python - <<'PYTHON'
import os
from pathlib import Path
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(os.environ["MODEL_PATH"])
Path("reranker_chat_template.jinja").write_text(tokenizer.get_chat_template())
PYTHON

vllm serve "$MODEL_PATH" \
    --served-model-name "nvidia/Nemotron-3.5-Rerank-8B-BF16" \
    --runner pooling \
    --dtype bfloat16 \
    --max-model-len 32768 \
    --compilation-config '{"compile_mm_encoder":true}' \
    --max-num-seqs 4 \
    --limit-mm-per-prompt '{"image":1}' \
    --pooler-config '{"seq_pooling_type":"MEAN","use_activation":false}' \
    --chat-template reranker_chat_template.jinja \
    --chat-template-content-format openai \
    --host 127.0.0.1 \
    --port 8000
```

After the server is ready, open another terminal in the same directory and activate the vLLM environment:

```bash
source .venv-vllm/bin/activate
```

Run the following Python client to send one query/document pair per request to `/classify`. The async client sends up to four requests concurrently and ranks the collected scores. The example covers text-only, image-only, and combined image-text documents. Each document can contain at most one image. The server preprocesses images using the checkpoint’s configured longest-edge limit of 1,120 pixels.

```python
import asyncio

import httpx

MODEL_ID = "nvidia/Nemotron-3.5-Rerank-8B-BF16"
ENDPOINT = "http://127.0.0.1:8000/classify"
MAX_CONCURRENCY = 4
query = "What is NVIDIA NeMo Framework?"
image_url = "https://docs.nvidia.com/nemo-framework/user-guide/24.07/_images/nemo-llm-mm-stack.png"
nemo_text = "NeMo Framework offers comprehensive functionalities for developing both LLMs and Multimodal Models."
biology_text = "A biological foundation model designed to analyze and generate DNA, RNA, and protein sequences."
image_block = {"type": "image_url", "image_url": {"url": image_url}}

documents = [
    ("nemo_image_text", [{"type": "text", "text": nemo_text}, image_block]),
    ("nemo_text", [{"type": "text", "text": nemo_text}]),
    ("nemo_image", [image_block]),
    ("biology_text", [{"type": "text", "text": biology_text}]),
]


async def main() -> None:
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    async with httpx.AsyncClient(timeout=120.0) as client:

        async def score_document(name, content):
            payload = {
                "model": MODEL_ID,
                "messages": [
                    {"role": "query", "content": [{"type": "text", "text": query}]},
                    {"role": "document", "content": content},
                ],
                "add_special_tokens": False,
                "use_activation": False,
            }
            async with semaphore:
                response = await client.post(ENDPOINT, json=payload)
                response.raise_for_status()
                result = response.json()
            return name, result["data"][0]["probs"][0]

        scores = await asyncio.gather(*(score_document(name, content) for name, content in documents))

    for name, score in sorted(scores, key=lambda item: item[1], reverse=True):
        print(f"{name}: {score:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
```

With `use_activation=False`, `probs[0]` contains the raw relevance logit, not a probability. Higher scores indicate greater predicted relevance. `add_special_tokens=False` avoids adding tokens beyond those rendered by the checkpoint's template.

Use `/classify` with the structured `query` and `document` messages shown above for multimodal inputs. The `/score` and `/rerank` request-rendering paths can mishandle this checkpoint's image placeholders. Image URLs must be accessible to the server; base64-encoded image data URLs can also be supplied in `image_url.url`.

<details>
<summary>Troubleshooting: Flash Attention 2 with older Transformers versions</summary>

For the Transformers and Sentence Transformers examples, `flash_attention_2`
can cause CUDA errors or incorrect outputs with image inputs in Transformers
5.17.0, 5.18.0, and 5.19.0. Upgrade to `transformers==5.20.0`.

</details>

## Software Integration:
**Runtime Engine(s):**
* Transformers
* Sentence Transformers
* vLLM

**Supported Hardware Microarchitecture Compatibility:**
* NVIDIA Ampere
* NVIDIA Blackwell
* NVIDIA Hopper

**Supported Operating System(s):** Linux  

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment.  


## Model Version(s): 
**Nemotron-3.5-Rerank-8B-BF16**


## Training, Testing, and Evaluation Datasets:


### Training Dataset:

**Data Modality:**
* Text  
* Image  


**Image Training Data Size:** 2.3M samples containing images, with or without accompanying text <br>
**Text Training Data Size:** 21M text-only data samples <br>
**Data Collection Method by dataset:** Automated, Manually-Labeled, Synthetic  
**Labeling Method by dataset:** Automated, Manually-Labeled, Synthetic  
**Properties:** Training was conducted using publicly available, commercially permissible datasets and synthetically generated datasets.

#### Public Datasets:
The language model component of the `Nemotron-3.5-Rerank-8B-BF16` was trained on a blend of text-only dataset files. The public source files used to create text-only training datasets are listed in the [Nemotron-3-Embed-8B-BF16](https://huggingface.co/nvidia/Nemotron-3-Embed-8B-BF16#dataset-overview) model card. 

The following publicly available datasets were also used to train the vision encoder and multimodal projector on image-only and combined image-text inputs.

| Dataset name | Reference |
| --- | --- |
| ArxivQA | [https://huggingface.co/datasets/MMInstruction/ArxivQA](https://huggingface.co/datasets/MMInstruction/ArxivQA) |
| ColPali-PDF | [https://huggingface.co/datasets/vidore/colpali_train_set](https://huggingface.co/datasets/vidore/colpali_train_set) |
| InfoVQA | [https://www.docvqa.org/datasets/infographicvqa](https://www.docvqa.org/datasets/infographicvqa) |
| TAT-DQA | [https://github.com/NExTplusplus/TAT-DQA](https://github.com/NExTplusplus/TAT-DQA) |
| docmatix-ir | [https://huggingface.co/datasets/Tevatron/docmatix-ir](https://huggingface.co/datasets/Tevatron/docmatix-ir) |
| Docmatix | [https://huggingface.co/datasets/HuggingFaceM4/Docmatix](https://huggingface.co/datasets/HuggingFaceM4/Docmatix) |
| wiki-ss-nq | [https://huggingface.co/datasets/Tevatron/wiki-ss-nq](https://huggingface.co/datasets/Tevatron/wiki-ss-nq) |

Synthetic text and image datasets were created either by generating queries from seed documents or by generating complete question–answer pairs through LLM-based prompting using the models listed below.

<table>
  <tr>
    <th>LLMs used to generate synthetic datasets</th>
  </tr>
  <tr>
    <td>nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16<br>nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4</td>
  </tr>
  <tr>
    <td>Qwen/Qwen3-Next-80B-A3B-Instruct<br>Qwen/Qwen3-235B-A22B<br>Qwen/Qwen3.5-397B-A17B<br>Qwen/Qwen3.5-35B-A3B<br>Qwen/Qwen3.6-27B<br>Qwen/Qwen3.6-35B-A3B<br>Qwen/Qwen3.8-27B</td>
  </tr>
  <tr>
    <td>google/gemma-4-31B-it</td>
  </tr>
  <tr>
    <td>mistralai/Pixtral-12B-2409</td>
  </tr>
  <tr>
    <td>openai/gpt-oss-120b<br>openai/gpt-oss-20b</td>
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
  <tr>
    <td>Digital Corpora</td>
    <td><a href="https://digitalcorpora.org/corpora/file-corpora/cc-main-2021-31-pdf-untruncated/">https://digitalcorpora.org/corpora/file-corpora/cc-main-2021-31-pdf-untruncated/</a></td>
  </tr>
  <tr>
    <td>Vdr-multilingual</td>
    <td><a href="https://huggingface.co/datasets/llamaindex/vdr-multilingual-train">https://huggingface.co/datasets/llamaindex/vdr-multilingual-train</a></td>
  </tr>
</table>

### Testing Dataset:

**Data Collection Method by dataset:** Not Applicable  
**Labeling Method by dataset:** Not Applicable  
**Properties:** Not Applicable. Model quality was assessed using the evaluation benchmark datasets described in the Evaluation Dataset subsection.

### Evaluation Dataset:

**Benchmark**:
- [ViDoRe V3](https://huggingface.co/blog/QuentinJG/introducing-vidore-v3)
- [MIRACL-VISION ](https://huggingface.co/datasets/nvidia/miracl-vision) <br>

**Benchmark Score:** NDCG@10 <br>

The `Nemotron-3.5-Rerank-8B-BF16` model was evaluated with the model's default image `longest_edge` set to 1,120 pixels. `Qwen3-VL-Reranker-8B` was evaluated with the model's default `max_pixels` set to 1,310,720. Both models reranked the top 50 candidates retrieved by the [Nemotron-3.5-Embed-1B-BF16](https://huggingface.co/nvidia/Nemotron-3.5-Embed-1B-BF16) model. 

<table>
  <tr>
    <th rowspan="2">Model</th>
    <th colspan="3" style="text-align: center">ViDoRe V3</th>
    <th>MIRACL-VISION</th>
  </tr>
  <tr>
    <th>image</th>
    <th>text</th>
    <th>image + text</th>
    <th>image</th>
  </tr>
  <tr>
    <td><a href="https://huggingface.co/nvidia/Nemotron-3.5-Embed-1B-BF16">Nemotron-3.5-Embed-1B-BF16</a></td>
    <td>58.02</td>
    <td>57.80</td>
    <td>58.82</td>
    <td>68.93</td>
  </tr>
  <tr>
    <td><a href="https://huggingface.co/Qwen/Qwen3-VL-Reranker-8B">Qwen3-VL-Reranker-8B</a></td>
    <td>66.02</td>
    <td>64.88</td>
    <td>66.03</td>
    <td>75.06</td>
  </tr>
  <tr>
    <td><strong>Nemotron-3.5-Rerank-8B-BF16</strong></td>
    <td><strong>67.22</strong></td>
    <td><strong>66.89</strong></td>
    <td><strong>67.56</strong></td>
    <td><strong>78.69</strong></td>
  </tr>
</table>

**Data Collection Method by dataset:** Automated, Manually-Labeled, Synthetic <br>
**Labeling Method by dataset:** Automated, Manually-Labeled, Synthetic <br>
**Properties:** `ViDoRe V3` is a visual document retrieval benchmark covering 8 public and 2 private datasets across professional domains. `MIRACL-VISION` is a multilingual visual retrieval dataset for 18 different languages. It is an extension of MIRACL, a popular text-only multilingual retrieval dataset.

## Inference:
**Acceleration Engine:** Transformers, PyTorch, vLLM <br>
**Hardware Requirements (GPU Architecture, Model):**
* NVIDIA Ampere (A100 80GB)
* NVIDIA Blackwell (GB200 186GB)
* NVIDIA Hopper (H100 80GB)


## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.  
Please make sure you have proper rights and permissions for all input image and video content; if image or video includes people, personal health information, or intellectual property, the image or video generated will not blur or maintain proportions of image subjects included.  
For more detailed information on ethical considerations for this model, please see the [Explainability](#explainability), [Bias](#bias), [Safety & Security](#safety), and [Privacy](#privacy) Subcards.  
Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

## Bias

| Field | Response |
| ----- | ----- |
| Participation considerations from adversely impacted groups [protected classes](https://calcivilrights.ca.gov/disputeresolution/protected-characteristics/) in model design and testing: | None |
| Measures taken to mitigate against unwanted bias: | None |
| Bias Metric (If Measured): | Not Applicable |

## Explainability

| Field | Response |
| ----- | ----- |
| Intended Task/Domain: | Passage or document ranking for question and answer retrieval. |
| Model Type: | Transformer cross-encoder. |
| Intended Users: | Generative AI developers working with conversational AI models. This is suitable for users building question-answering applications over large multimodal corpora and aiming to improve retrieval performance by reranking a set of candidate documents for a given question. The corpus may include visually rich document images (e.g., pages with text, figures, tables, charts, or infographics) and/or text extracted from documents. |
| Output: | List of Floats (Score/Logit indicating if a passage/document relevant to a question). |
| Describe how the model works: | The model outputs a relevance score (logit) reflecting how strongly it predicts that the passage or document contains the information required to answer the question. |
| List the groups (or group characteristics) for which this was tested to produce comparable outcomes: | Not Applicable |
| Technical Limitations & Mitigation: | The model’s max sequence length is 32768 tokens. If the combined text-and-image sequence exceeds that limit, truncate the text or reduce the image resolution until it fits. |
| Verified to have met prescribed NVIDIA quality standards: | Yes |
| Performance Metrics: | Accuracy, Latency, Throughput|
| Potential Known Risks: | This model does not always guarantee to provide a meaningful ranking of document(s) for a given query. |
| Licensing: | Use of the model is governed by the [OpenMDW License Agreement, version 1.1 (OpenMDW-1.1)](https://openmdw.ai/license/1-1/). Additional Information: The [Ministral-3-8B-Instruct-2512-BF16](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-BF16) base model is governed by the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt). |


## Privacy

The datasets used to train this model were reviewed before release. Please review NVIDIA’s Privacy Policy (https://www.nvidia.com/en-us/about-nvidia/privacy-policy/) for more information.


## Safety

| Field | Response |
| ----- | ----- |
| Model Application Field(s): | Document reranking for retrieval. User queries are text. Documents can be text or page images (including pages with charts, tables, and infographics). |
| Describe the life critical impact (if present). | Not Applicable |
| Use Case Restrictions: | Use of the model is governed by the [OpenMDW License Agreement, version 1.1 (OpenMDW-1.1)](https://openmdw.ai/license/1-1/). Additional Information: The [Ministral-3-8B-Instruct-2512-BF16](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-BF16) base model is governed by the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt). |
| Model and dataset restrictions: | The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development. Restrictions enforce dataset access during training, and dataset license constraints adhered to. |
