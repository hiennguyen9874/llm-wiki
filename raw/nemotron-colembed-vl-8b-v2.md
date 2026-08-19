---
license: cc-by-nc-4.0
license_link: LICENSE
tags:
- text
- image
- vidore
- colpali
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

Introducing **nvidia/nemotron-colembed-vl-8b-v2**, the state-of-the-art late interaction embedding model that currently ranks No. 1 on ViDoRe V3—a comprehensive benchmark for enterprise retrieval use cases—as of January 26, 2026, with a score of `63.54` across 8 public tasks. The model was fine-tuned for query-document retrieval. Users can input `queries`, which are text, or `documents` which are page images, to the model. The model outputs ColBERT-style multi-vector numerical representations for input queries and documents.

✨ **Key Improvements:**
* ⚗️ **Advanced Model Merging:** Utilizes post-training model merging to combine the strengths of multiple fine-tuned checkpoints. This delivers the accuracy stability of an ensemble without any additional inference latency.
* 🌍 **Enhanced Synthetic Data:** We significantly enriched our training mixture with diverse multilingual synthetic data, improving semantic alignment across languages and complex document types.

This model is for non-commercial/research use only.  
See the Nemotron ColEmbed v2 [paper](https://arxiv.org/abs/2602.03992) for more details about its architecture, training and results.

### License/Terms of Use
The use of this model is governed by the [Creative Commons Attribution-NonCommercial 4.0 license](https://creativecommons.org/licenses/by-nc/4.0/deed.en) and the use of the post-processing scripts are licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt). Additional Information: Built with Qwen3-VL which is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt).

This project will download and install additional third-party open source software projects. Review the license terms of these open source projects before use.

### Deployment Geography
Global

### Use Case

**nemotron-colembed-vl-8b-v2** is a powerful, highly accurate model intended for researchers exploring applications that must understand or retrieve information across both text and image modalities. It is instrumental in multimodal RAG systems, where queries are in text format and documents are images, such as pages, text, charts, tables, or infographics. Potential applications include multimedia search engines, cross-modal retrieval systems, and conversational AI with rich input understanding.


### Release Date
01/26/2026 via [https://huggingface.co/nvidia/nemotron-colembed-vl-8b-v2](https://huggingface.co/nvidia/nemotron-colembed-vl-8b-v2)

## Model Architecture

- **Architecture Type:** Transformer
- **Network Architecture:** [Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) based encoder. 

The `nemotron-colembed-vl-8b-v2` is a transformer-based multimodal embedding model built from `Qwen3-VL-8B-Instruct`, which adopts a three-module architecture comprising a vision encoder (default to the [SigLIP2-SO-400M](https://huggingface.co/collections/google/siglip2) variant), an MLP-based vision–language merger, and a large language model (LLM) (see [technical report](https://arxiv.org/pdf/2511.21631) for details). It has approximately 8.8B parameters.


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
- **Other Properties Related to Output:** For each input token, the model outputs a 4096-dimensional embedding vector of floating-point values.

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA’s hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.


### Installation
The model requires `transformers>=4.57.2` and flash attention installed.

```bash
pip install "transformers>=4.57.2"
pip install flash-attn==2.6.3 --no-build-isolation
```
Depending on your environment you might need to upgrade polars and pydantic:

```bash
pip install -U datasets polars
pip install -U pydantic
```

### Transformers Usage

We provide an [example notebook](nemotron_colembed_4b_8b_v2_example_vidore_v3.ipynb) demonstrating model usage with a simple indexing and retrieval pipeline.   

We also provide a simple example code snippet below.  

```python
import requests
from PIL import Image
from io import BytesIO
import torch
from transformers import AutoModel
from transformers.image_utils import load_image
# Load Model

model = AutoModel.from_pretrained(
    'nvidia/nemotron-colembed-vl-8b-v2',
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

# tensor([[21.1969, 20.9079, 20.5363],
#         [32.2324, 32.8058, 32.2075],
#         [25.7505, 25.8201, 26.2726]], device='cuda:0')
```


## Software Integration: <br>

Runtime Engine(s): Not Applicable <br>
Supported Hardware Microarchitecture Compatibility:
- NVIDIA Ampere - A100 40GB and A100 80GB <br>
- NVIDIA Hopper - H100 80GB

Supported Operating System(s): Linux

## Model Version(s)
**nemotron-colembed-vl-8b-v2**

# Training and Evaluation Datasets

## Training Dataset

The model was trained on publicly available datasets, including [DocMatix-IR](https://huggingface.co/datasets/Tevatron/docmatix-ir), [VDR](https://huggingface.co/datasets/vdr-multilingual-train), [Vidore-ColPali-Training](https://huggingface.co/datasets/vidore/colpali_train_set), [VisRAG-Ret-Train-Synthetic-data](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-Synthetic-data), [VisRAG-Ret-Train-In-domain-data](https://huggingface.co/datasets/openbmb/VisRAG-Ret-Train-In-domain-data), and [Wiki-SS-NQ](https://huggingface.co/datasets/Tevatron/wiki-ss-nq).

**Data Modality**: Image

**Image Training Data Size**
- Less than a Million Images

**Data Collection Method by dataset:** Hybrid: Automated, Human, Synthetic <br>
**Labeling Method by dataset:** Hybrid: Automated, Human, Synthetic <br>
**Properties:** Training: The vision embedding model was fine-tuned on approximately 500k image samples.

## Evaluation Dataset

We evaluate the model on the datasets from [ViDoRe](https://huggingface.co/spaces/vidore/README) V1, V2 and V3 Visual Document Retrieval benchmarks.

[ViDoRe](https://huggingface.co/spaces/vidore/README) is a premier benchmark for Visual Document Retrieval and it is composed of various page-level retrieving tasks spanning multiple domains, languages, and settings. The latest version of the benchmark is [Vidore V3](https://huggingface.co/blog/QuentinJG/introducing-vidore-v3), a comprehensive evaluation of retrieval for enterprise use-cases.   

We provide a [script](https://huggingface.co/nvidia/nemotron-colembed-vl-8b-v2/blob/main/mteb2_eval.py) using [MTEB 2](https://github.com/embeddings-benchmark/mteb/tree/main/mteb) library to evaluate ColEmbed models on ViDoRe benchmarks.

- **Data Collection Method by dataset:** Hybrid: Automated, Human, Synthetic
- **Labeling Method by dataset:** Hybrid: Automated, Human, Synthetic
- **Properties:** More details on ViDoRe V1 and ViDoRe V2 can be found on their leaderboard. [Visual Document Retrieval Benchmark](https://huggingface.co/vidore), 


## Evaluation Results

### ViDoRE V1&V2 and V3 on MTEB leaderboards

```bash
pip install "mteb>=2.7.0, <3.0.0"
# Evaluates with Vidore V1 and V2
CUDA_VISIBLE_DEVICES=0; python3 mteb2_eval.py --model_name nvidia/nemotron-colembed-vl-8b-v2 --batch_size 16 --benchmark "VisualDocumentRetrieval"
# Evaluates with Vidore V3
CUDA_VISIBLE_DEVICES=0; python3 mteb2_eval.py --model_name nvidia/nemotron-colembed-vl-8b-v2 --batch_size 16 --benchmark "ViDoRe(v3)"
# Evaluates with a specific task/dataset of Vidore V3: Vidore3ComputerScienceRetrieval
CUDA_VISIBLE_DEVICES=0; python3 mteb2_eval.py --model_name nvidia/nemotron-colembed-vl-8b-v2 --batch_size 16 --benchmark "ViDoRe(v3)" --task-list Vidore3ComputerScienceRetrieval
```

In this section, we evaluate the performance of nemotron-colembed-vl-8b-v2 against other models that  previously achieved top-five rankings on the leaderboards.

We report results on the ViDoRe benchmark suite. The tables below summarize the image-modality accuracy of `nemotron-colembed-vl-8b-v2` on the ViDoRe V1, V2, and V3 benchmarks, alongside other NVIDIA nemotron-colembed models. Note that (M)MTEB leaderboards use Borda ranking. Each task acts like a voter that ranks models based on how well they perform. Models earn more points when they rank higher on a task. The model with the most total points across all tasks gets the top overall rank.


#### ViDoRe V3 (NDCG@10)

| Model | **Avg** | CompSci | Energy | FinanceEn | FinanceFr | HR | Industrial | Pharma | Physics |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **nemotron-colembed-8b**| **63.54** | 79.30 | 69.82 | 67.29 | 51.54 | 66.32 | 56.03 | 67.19 | 50.84 |
| tomoro-colqwen3-8b| 61.60 | 75.35 | 68.41 | 65.08 | 49.10 | 63.98 | 54.41 | 66.36 | 50.13|
| [nemotron-colembed-4b]((https://huggingface.co/nvidia/nemotron-colembed-4b-v2)) | 61.42 | 78.56 | 67.48 | 65.02 | 49.01 | 62.39 | 53.91 | 66.10 | 48.86 |
| tomoro-colqwen3-4b| 60.16 | 75.44 | 66.43 | 63.84 | 46.83 | 60.09 | 53.58 | 65.74 | 49.32 |
| [nemotron-colembed-3b-v2](https://huggingface.co/nvidia/llama-nemotron-colembed-3b-v2) | 59.70 | 77.09 | 64.88 | 64.23 | 44.41 | 62.28 | 51.71 | 66.04 | 46.93 |
| nomic-ai/colnomic-embed-multimodal-7b | 57.64 | 76.20 | 63.58 | 56.57 | 45.46 | 58.67 | 50.13 | 62.26 | 48.25 |
| jinaai/jina-embeddings-v4 | 57.54 | 71.81 | 63.50 | 59.30 | 46.10 | 59.53 | 50.38 | 63.09 | 46.63 |


#### ViDoRe V2 (NDCG@5)

| Model | **Avg** | BioMedicalLectures | ESGReportsHL | ESGReports | EconomicsReports |
| :--- | :--- | :--- | :--- | :--- | :--- |
| tomoro-colqwen3-8b| 65.40 | 65.47 | 75.98 | 60.71 | 59.46 |
| EvoQwen2.5-VL-Retriever-7B-v1 | 65.24 | 65.20 | 76.98 | 59.67 | 59.13 |
| [nemotron-colembed-8b](https://huggingface.co/nvidia/nemotron-colembed-8b-v2) | 65.16 | 66.16 | 73.15 | 60.56| 60.76 |
| tomoro-colqwen3-4b| 64.69 | 65.38 | 74.65 | 62.44 | 56.30 |
| [nemotron-colembed-4b]((https://huggingface.co/nvidia/nemotron-colembed-4b-v2)) | 64.49 | 64.32 | 71.43 | 61.48 | 60.75 |
| [nemotron-colembed-3b-v2](https://huggingface.co/nvidia/llama-nemotron-colembed-3b-v2)| 63.38 | 63.19 | 73.11 | 58.64 | 58.59 |
| [nemotron-colembed-3b-v1](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1)| 63.32 | 62.70 | 75.38 | 57.38 | 57.84 |


#### ViDoRe V1 (NDCG@5)

| Model | **Avg** | ArxivQA | DocVQA | InfoVQA | Shift | Syn-AI | Syn-Energy | Syn-Gov | Syn-Health | TabFQuAD | Tatdqa |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **nemotron-colembed-8b** | **92.65** | 93.08 | 68.05 | 94.56 | 93.30 | 100.00 | 97.89 | 98.89 | 99.63 | 97.74 | 83.37 |
| [nemotron-colembed-3b-v2](https://huggingface.co/nvidia/llama-nemotron-colembed-3b-v2)| 91.74 | 90.40 | 67.17 | 94.68 | 92.00 | 100.00 | 98.02 | 97.95 | 98.89 | 97.25 | 81.04 |
| nemotron-colembed-4b | 91.62 | 92.03 | 67.39 | 93.31 | 92.26 | 99.26 | 96.19 | 98.02 | 98.52 | 98.05 | 81.19 |
| [nemotron-colembed-3b-v1](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1)| 91.00 | 88.35 | 66.21 | 94.92 | 90.70 | 99.63 | 96.63 | 97.82 | 99.26 | 95.94 | 80.57 |
| tomoro-colqwen3-8b| 90.76 | 91.15 | 66.37 | 94.48 | 87.89 | 99.26 | 96.71 | 97.58 | 99.06 | 94.23 | 80.92 |
| EvoQwen2.5-VL-Retriever-7B-v1 | 90.68 | 91.49 | 65.07 | 94.11 | 88.80 | 99.63 | 96.63 | 96.29 | 98.89 | 93.63 | 82.26 |
| tomoro-colqwen3-4b| 90.57 | 90.58 | 66.30 | 94.31 | 87.39 | 99.26 | 96.91 | 97.17 | 99.63 | 94.33 | 79.87 |


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
