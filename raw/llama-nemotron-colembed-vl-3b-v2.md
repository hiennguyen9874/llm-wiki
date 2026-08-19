---
license: other
license_name: customized-nscl-v1
license_link: LICENSE
tags:
  - text
  - image
  - vidore
  - rag
  - multimodal-embedding
  - multilingual-embedding
  - Text-to-Visual Document (T→VD) retrieval
  - feature-extraction
language:
  - multilingual
inference: false
library_name: transformers
pipeline_tag: visual-document-retrieval
---

# Nemotron ColEmbed V2

<p align="center">
   🤗 <a href="https://huggingface.co/nvidia/nemotron-colembed-vl-8b-v2">8B</a> | &nbsp&nbsp 🤗 <a href="https://huggingface.co/nvidia/nemotron-colembed-vl-4b-v2">4B</a> | &nbsp&nbsp 🤗 <a href="https://huggingface.co/nvidia/llama-nemotron-colembed-vl-3b-v2">3B</a> &nbsp
</p>

# **Model Overview**

## Description

The **nvidia/llama-nemotron-colembed-vl-3b-v2** is a late interaction embedding model fine-tuned for query-document retrieval. Users can input `queries`, which are text, or `documents` which are page images, to the model. The model outputs ColBERT-style multi-vector numerical representations for input queries and documents. 

✨ **Key Improvements in v2:**
* ⚗️ **Advanced Model Merging:** Utilizes post-training model merging to combine the strengths of multiple fine-tuned checkpoints. This delivers the accuracy stability of an ensemble without any additional inference latency.
* 🌍 **Enhanced Synthetic Data:** We significantly enriched our training mixture with diverse multilingual synthetic data, improving semantic alignment across languages and complex document types.

This model is for non-commercial/research use only.  
Check the Nemotron ColEmbed v2 [paper](https://arxiv.org/abs/2602.03992) for more details.

### License/Terms of Use
The use of this model is governed by the [NVIDIA Non-Commercial License Agreement](https://huggingface.co/nvidia/llama-nemotron-colembed-vl-3b-v2/blob/main/LICENSE) and the use of the post-processing scripts are licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt). It is built with Meta Llama 3.2. Llama 3.2 is licensed under the [Llama 3.2 Community License](https://www.llama.com/llama3_2/license/), Copyright © Meta Platforms, Inc. All Rights Reserved.

This project will download and install additional third-party open source software projects. Review the license terms of these open source projects before use.

### Deployment Geography
Global

### Use Case
llama-nemotron-colembed-v2 is intended for researchers exploring applications that must understand or retrieve information across both text and image modalities. It is instrumental in multimodal RAG systems, where queries are in text format and documents are images, such as pages, text, charts, tables or infographics. Potential applications include multimedia search engines, cross-modal retrieval systems, and conversational AI with rich input understanding.

### Release Date
01/26/2026

## Model Architecture

- **Architecture Type:** Transformer
- **Network Architecture:** [google/siglip2-giant-opt-patch16-384](https://huggingface.co/google/siglip2-giant-opt-patch16-384) + [meta-llama/Llama-3.2-3B](https://huggingface.co/meta-llama/Llama-3.2-3B)

The llama-nemotron-colembed-vl-3b-v2 is a transformer-based multimodal embedding model built on top of a VLM based on google/siglip2-giant-opt-patch16-384 and meta-llama/Llama-3.2-3B. It has approximately 4.4B parameters.


## Input(s):
**Input Type(s):** Image, Text <br>

**Input Format(s):** <br>
- Image: List of images- Red, Green, Blue (RGB) <br>
- Text: List of Strings <br>

**Input Parameters:** <br>
- Image: Two-Dimensional (2D) <br>
- Text: One-Dimensional (1D) <br>


**Other Properties Related to Input:** 
- The model's maximum context length we evaluated is 10240 tokens. <br>
- Each image tile consumes 256 tokens. We have tested this model extensively with these settings on config.json - `max_input_tiles = 8`, `use_thumbnails = True`, so that every image is split into maximum of 8 tiles + 1 thumbnail (whole image at lower resolution). Images must be python PIL format. The model will scale the image into multiple tiles of 512x512.


## Outputs

- **Output Type:** Floats
- **Output Format:** List of float arrays
- **Output Parameters:**  The list of floats equivalent to [batchsize x seq length x embedding_dim]
- **Other Properties Related to Output:** For each input token, the model outputs a 3072-dimensional embedding vector of floating-point values.

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA’s hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.


### Installation
The model requires `transformers>=4.45.0` and flash attention installed.

```bash
pip install "transformers>=4.45.0"
pip install flash-attn==2.6.3 --no-build-isolation
```

Depending on your environment you might need to upgrade polars and pydantic:

```bash
pip install -U datasets polars
pip install -U pydantic
```

### Transformers Usage

```python
import requests
from PIL import Image
from io import BytesIO
import torch
from transformers import AutoModel
from transformers.image_utils import load_image
# Load Model

model = AutoModel.from_pretrained(
    'nvidia/llama-nemotron-colembed-vl-3b-v2',
    device_map='cuda',
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
).eval()

# Queries
queries = [
    'How is AI improving the intelligence and capabilities of robots?',
    'Canary, a multilingual model that transcribes speech in English, Spanish, German, and French with punctuation and capitalization.',
    'Generative AI can generate DNA sequences that can be translated into proteins for bioengineering.'
]

image_urls = [
    "https://developer.download.nvidia.com/images/isaac/nvidia-isaac-lab-1920x1080.jpg",
    "https://developer-blogs.nvidia.com/wp-content/uploads/2024/03/asr-nemo-canary-featured.jpg",
    "https://blogs.nvidia.com/wp-content/uploads/2023/02/genome-sequencing-helix.jpg"
]

# Load all images (load_image handles both local paths and URLs)
images = [load_image(img_path) for img_path in image_urls]

# Encoding
query_embeddings = model.forward_queries(queries, batch_size=8)
image_embeddings = model.forward_images(images, batch_size=8)

scores = model.get_scores(
    query_embeddings,
    image_embeddings
)
# Diagonal should have higher scores
print(scores)

# tensor([[10.9662, 10.6623, 10.0281],
#         [17.7323, 18.6031, 17.7613],
#         [13.2915, 13.6993, 13.7968]], device='cuda:0')
```


## Software Integration: <br>

Runtime Engine(s): Not Applicable <br>
Supported Hardware Microarchitecture Compatibility:
- NVIDIA Ampere - A100 40GB and A100 80GB <br>
- NVIDIA Hopper - H100 80GB

Supported Operating System(s): Linux

## Model Version(s)
**llama-nemotron-colembed-vl-3b-v2**

# Training and Evaluation Datasets

## Training Dataset

The model was trained on publicly available datasets, including [HotpotQA](https://huggingface.co/datasets/hotpotqa/hotpot_qa), [MIRACL](https://huggingface.co/datasets/SEACrowd/miracl), [Natural Questions (NQ)](https://huggingface.co/datasets/irds/natural-questions), [Stack Exchange](https://huggingface.co/datasets/HuggingFaceH4/stack-exchange-preferences), [SQuAD](https://huggingface.co/datasets/squad), [Tiger Math/Stack](https://huggingface.co/datasets/TIGER-Lab/WebInstructSub), [DocMatix-IR](https://huggingface.co/datasets/Tevatron/docmatix-ir), [VDR](https://huggingface.co/datasets/vdr-multilingual-train), [Vidore-ColPali-Training](https://huggingface.co/datasets/vidore/colpali_train_set), [VisRAG-Ret-Train-Synthetic-data](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-Synthetic-data), [VisRAG-Ret-Train-In-domain-data](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-In-domain-data), and [Wiki-SS-NQ](https://huggingface.co/datasets/Tevatron/wiki-ss-nq).

**Data Modality**: Text and image

**Image Training Data Size**
- Less than a Million Images

**Data Collection Method by dataset:** Hybrid: Automated, Human, Synthetic <br>
**Labeling Method by dataset:** Hybrid: Automated, Human, Synthetic <br>
**Properties:** Training: The text component is comprised of semi-supervised pre-training on 12M samples from public datasets and fine-tuning on 1.5M samples from public datasets. The vision embedding model was fine-tuned on approximately 500k image samples.

To enhance robustness, we augmented the fine-tuning mixture with diverse multilingual synthetic queries. These were generated to target complex document layouts and cross-lingual retrieval scenarios within our existing high-quality image data.

## Evaluation Dataset

We evaluate the model on the datasets from [ViDoRe](https://huggingface.co/spaces/vidore/README) V1, V2 and V3 Visual Document Retrieval benchmarks.

[ViDoRe](https://huggingface.co/spaces/vidore/README) is a premier benchmark for Visual Document Retrieval and it is composed of various page-level retrieving tasks spanning multiple domains, languages, and settings. The latest version of the benchmark is [Vidore V3](https://huggingface.co/blog/QuentinJG/introducing-vidore-v3), a comprehensive evaluation of retrieval for enterprise use-cases.   

We provide a [script](https://huggingface.co/nvidia/llama-nemotron-colembed-vl-3b-v2/blob/main/mteb2_eval.py) script using [MTEB 2](https://github.com/embeddings-benchmark/mteb/tree/main/mteb) library to evaluate ColEmbed models on ViDoRe benchmarks.

- **Data Collection Method by dataset:** Hybrid: Automated, Human, Synthetic
- **Labeling Method by dataset:** Hybrid: Automated, Human, Synthetic
- **Properties:** More details on ViDoRe V1 and ViDoRe V2 can be found on their leaderboard. [Visual Document Retrieval Benchmark](https://huggingface.co/vidore), 


## Evaluation Results

### ViDoRE V1&V2 and V3 on MTEB leaderboards

```bash
pip install "mteb>=2.6.0, <3.0.0"
# Evaluates with Vidore V1 and V2
CUDA_VISIBLE_DEVICES=0; python3 mteb2_eval.py --model_name nvidia/llama-nemotron-colembed-vl-3b-v2 --batch_size 16 --benchmark "VisualDocumentRetrieval"
# Evaluates with Vidore V3
CUDA_VISIBLE_DEVICES=0; python3 mteb2_eval.py --model_name nvidia/llama-nemotron-colembed-vl-3b-v2 --batch_size 16 --benchmark "ViDoRe(v3)"
# Evaluates with a specific task/dataset of Vidore V3: Vidore3ComputerScienceRetrieval
CUDA_VISIBLE_DEVICES=0; python3 mteb2_eval.py --model_name nvidia/llama-nemotron-colembed-vl-3b-v2 --batch_size 16 --benchmark "ViDoRe(v3)" --task-list Vidore3ComputerScienceRetrieval
```

In this section, we compare the performance of llama-nemotron-colembed-vl-3b-v2 with its previous version [llama-nemoretriever-colembed-3b-v1](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1).

In the table below, we compare the performance of v2 against the previous v1 version. The v2 model demonstrates higher retrieval accuracy across all ViDoRe benchmarks. 

Note: Accuracy for ViDoRe V1 and V2 is reported as NDCG@5, while accuracy for ViDoRe V3 is reported as NDCG@10.

| **Benchmark** | **llama-nemoretriever-colembed-3b-v1** | **llama-nemotron-colembed-vl-3b-v2** |
| :--- | :---: | :---: |
| **ViDoRe V1** | 0.9100 | **0.9174** |
| **ViDoRe V2** | 0.6332 | **0.6338** |
| **ViDoRe V3** | 0.5707 | **0.5970** |

## Inference:
**Acceleration Engine:** Not Applicable <br>
**Test Hardware:** A100 40GB, A100 80GB, H100 80GB



### Citation

```
@misc{moreira2026_nemotron_colembed_v2,
      title={Nemotron ColEmbed V2: Top-Performing Late Interaction embedding models for Visual Document Retrieval}, 
      author={Gabriel de Souza P. Moreira, Ronay Ak, Mengyao Xu, Oliver Holworthy, Benedikt Schifferer, Zhiding Yu, Yauhen Babakhin, Radek Osmulski, Jiarui Cai, Ryan Chesler, Bo Liu, Even Oldridge},
      year={2026},
      eprint={2602.03992},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2602.03992}, 
}
```

## **Ethical Considerations**

NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. When downloaded or used in accordance with our terms of service, developers should work with their supporting model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

Please make sure you have proper rights and permissions for all input image and video content; if image or video includes people, personal health information, or intellectual property, the image or video generated will not blur or maintain proportions of image subjects included.

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://app.intigriti.com/programs/nvidia/nvidiavdp/detail).
