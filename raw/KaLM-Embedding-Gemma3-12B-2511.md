---
datasets:
- KaLM-Embedding/KaLM-embedding-finetuning-data
base_model:
- google/gemma-3-12b-pt
pipeline_tag: sentence-similarity
library_name: sentence-transformers
tags:
- Retrieval
- STS
- Classification
- Clustering
- Reranking
- vllm
license: other
license_name: tencent-kalm-embedding-community
extra_gated_eu_disallowed: true
---


<h1 align="center">KaLM-Embedding-Gemma3-12B-2511</h1>

<p align="center">
  <a href="https://huggingface.co/tencent/KaLM-Embedding-Gemma3-12B-2511">
    <img src="https://img.shields.io/badge/%F0%9F%A4%97_HuggingFace-Model-ffbd45.svg" alt="HuggingFace">
  </a>
  <a href="https://kalm-embedding.github.io/">
    <img src="https://img.shields.io/badge/Home-Page-purple.svg?logo=github&" alt="Homepage">
  </a>
  <a href="https://arxiv.org/abs/2506.20923">
    <img src="https://img.shields.io/badge/Paper-KaLM--Embedding-d4333f?logo=arxiv&logoColor=white&colorA=cccccc&colorB=d4333f&style=flat" alt="Paper">
  </a>
</p>


## Short Description

**KaLM-Embedding-Gemma3-12B-2511** is a versatile and compact embedding model, which achieves SOTA performance in MMTEB (due to 11-2025).


## MMTEB Evaluation Results

| Rank (Borda) | Model | Mean (Task) | Mean (TaskType) | Bitext Mining | Classification | Clustering | Instruction Reranking | Multilabel Classification | Pair Classification | Reranking | Retrieval | STS |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **1** | **KaLM-Embedding-Gemma3-12B-2511** | **72.32** | **62.51** | **83.76** | **77.88** | 55.77 | 5.49 | **33.03** | 84.73 | 67.27 | **75.66** | 79.02 |
| 2 | llama-embed-nemotron-8b | 69.46 | 61.09 | 81.72 | 73.21 | 54.35 | 10.82 | 29.86 | 83.97 | **67.78** | 68.69 | 79.41 |
| 3 | Qwen3-Embedding-8B | 70.58 | 61.69 | 80.89 | 74.00 | **57.65** | 10.06 | 28.66 | **86.40** | 65.63 | 70.88 | **81.08** |
| 4 | gemini-embedding-001 | 68.37 | 59.59 | 79.28 | 71.82 | 54.59 | 5.18 | 29.16 | 83.63 | 65.58 | 67.71 | 79.40 |
| 5 | Qwen3-Embedding-4B | 69.45 | 60.86 | 79.36 | 72.33 | 57.15 | **11.56** | 26.77 | 85.05 | 65.08 | 69.60 | 80.86 |
| 6 | Qwen3-Embedding-0.6B | 64.34 | 56.01 | 72.23 | 66.83 | 52.33 | 5.09 | 24.59 | 80.83 | 61.41 | 64.65 | 76.17 |
| 7 | gte-Qwen2-7B-instruct | 62.51 | 55.93 | 73.92 | 61.55 | 52.77 | 4.94 | 25.48 | 85.13 | 65.55 | 60.08 | 73.98 |
| 8 | Linq-Embed-Mistral | 61.47 | 54.14 | 70.34 | 62.24 | 50.60 | 0.94 | 24.77 | 80.43 | 64.37 | 58.69 | 74.86 |
| 9 | multilingual-e5-large-instruct | 63.22 | 55.08 | 80.13 | 64.94 | 50.75 | -0.40 | 22.91 | 80.86 | 62.61 | 57.12 | 76.81 |
| 10 | embeddinggemma-300m | 61.15 | 54.31 | 64.40 | 60.90 | 51.17 | 5.61 | 24.82 | 81.40 | 63.25 | 62.49 | 74.73 |


## Model Details
- Model Size: 11.76B
- Embedding Dimension: 3840
- Max Input Tokens: 32k
- MRL dimensions: 3840, 2048, 1024, 512, 256, 128, and 64
- Pooling: lasttoken pooling


## Usage
### sentence-transformers support
Using this model becomes easy when you have [sentence-transformers](https://www.SBERT.net) installed:

```
pip install -U sentence-transformers
```

You can use the model like this:

```python
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer(
    "tencent/KaLM-Embedding-Gemma3-12B-2511",
    trust_remote_code=True,
    model_kwargs={
        "torch_dtype": torch.bfloat16,
        "attn_implementation": "flash_attention_2",  # Optional
    },
)
model.max_seq_length = 512

sentences = ["This is an example sentence", "Each sentence is converted"]
prompt = "Instruct: Classifying the category of french news.\nQuery:"
embeddings = model.encode(
    sentences,
    prompt=prompt,
    normalize_embeddings=True,
    batch_size=256,
    show_progress_bar=True,
)
print(embeddings)
```

Or you can use `encode_query` and `encode_document` to automatically add the default prompt for queries (`"Instruct: Given a query, retrieve documents that answer the query \nQuery: "`) and documents (`""`), respectively.

```python
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer(
    "tencent/KaLM-Embedding-Gemma3-12B-2511",
    trust_remote_code=True,
    model_kwargs={
        "torch_dtype": torch.bfloat16,
        "attn_implementation": "flash_attention_2",  # Optional
    },
)
model.max_seq_length = 512

queries = [
    "What is the capital of China?",
    "Explain gravity",
]
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun.",
]

query_embeddings = model.encode_query(queries)
document_embeddings = model.encode_document(documents)

similarities = model.similarity(query_embeddings, document_embeddings)
print(similarities)
```

### vllm support
Note: Since [vllm](https://github.com/vllm-project/vllm/tree/main) only supports the [Gemma3ForCausalLM](https://huggingface.co/docs/transformers/en/model_doc/gemma3#transformers.Gemma3ForCausalLM) model class and not [Gemma3TextModel](https://huggingface.co/docs/transformers/en/model_doc/gemma3#transformers.Gemma3TextModel), model parameters must be loaded by specifying the CausalLM branch via `revision="CausalLM"`.

```python
from vllm import LLM

sentences = ["This is an example sentence", "Each sentence is converted"]

# Create an LLM.
# You should pass task="embed" for embedding models
model = LLM(
    model="tencent/KaLM-Embedding-Gemma3-12B-2511",
    task="embed",
    enforce_eager=True,
    revision="CausalLM",  # specify the CausalLM branch for Gemma3ForCausalLM config
)

outputs = model.embed(sentences)
embeddings = [output.outputs.embedding for output in outputs]
```

Verify the vLLM logs to ensure parameters are loaded correctly; incorrect branch specifications do not trigger exception errors. 
If issues arise during the vLLM download and loading process, it is recommended to manually download the model parameters to a local directory:
`huggingface-cli download tencent/KaLM-Embedding-Gemma3-12B-2511 --revision CausalLM --local-dir KaLM-Embedding-Gemma3-12B-CausalLM`


## Citation
If you find this model useful, please consider giving a star and citation.
```
@misc{zhao2025kalmembeddingv2,
      title={KaLM-Embedding-V2: Superior Training Techniques and Data Inspire A Versatile Embedding Model}, 
      author={Xinping Zhao and Xinshuo Hu and Zifei Shan and Shouzheng Huang and Yao Zhou and Xin Zhang and Zetian Sun and Zhenyu Liu and Dongfang Li and Xinyuan Wei and Youcheng Pan and Yang Xiang and Meishan Zhang and Haofen Wang and Jun Yu and Baotian Hu and Min Zhang},
      year={2025},
      eprint={2506.20923},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2506.20923}, 
}

@misc{hu2025kalmembedding,
      title={KaLM-Embedding: Superior Training Data Brings A Stronger Embedding Model}, 
      author={Xinshuo Hu and Zifei Shan and Xinping Zhao and Zetian Sun and Zhenyu Liu and Dongfang Li and Shaolin Ye and Xinyuan Wei and Qian Chen and Baotian Hu and Haofen Wang and Jun Yu and Min Zhang},
      year={2025},
      eprint={2501.01028},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2501.01028}, 
}
```


## Contact
If you encounter any issue, feel free to contact us via the email: <yanshek.woo@gmail.com>, <xinpingzhao@slai.edu.cn>