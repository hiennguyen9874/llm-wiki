---
license: other
license_name: customized-nscl-v1
license_link: LICENSE
tags:
- transformers
- text
- sentence-similarity
- feature-extraction
- mteb
- mmteb
language:
- multilingual
library_name: sentence-transformers
datasets:
- nvidia/embed-nemotron-dataset-v1
---

# llama-embed-nemotron-8b

## Model Overview

### Description:
`llama-embed-nemotron-8b` is a versatile text embedding model trained by NVIDIA and optimized for retrieval, reranking, semantic similarity, and classification use cases. This model has robust capabilities for multilingual and cross-lingual text retrieval. It is designed to serve as a foundational component in text-based Retrieval-Augmented Generation (RAG) systems.

This model achieves state-of-the-art performance on the [multilingual MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) as of October 21, 2025.

Together with the model weights, we're releasing the full recipe behind the `llama-embed-nemotron-8b`:
- A detailed [technical report](https://arxiv.org/abs/2511.07025) focusing on our Synthetic Data Generation (SDG) pipeline and core design choices.
- The [training dataset](https://huggingface.co/datasets/nvidia/embed-nemotron-dataset-v1), featuring a curated mix of public and synthetic data.
- The full [training code via the NeMo AutoModel framework](https://github.com/NVIDIA-NeMo/Automodel/tree/main/examples/retrieval/bi_encoder/llama_embed_nemotron_8b).

This model is for non-commercial/research use only.

### License/Terms of Use

Governing Terms for `llama-embed-nemotron-8b` model: [NVIDIA License](https://huggingface.co/nvidia/llama-embed-nemotron-8b/blob/main/LICENSE) <br>
Additional Information: [Llama-3.1 Community License Agreement](https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct/blob/main/LICENSE) for meta-llama/Llama-3.1-8B. [Acceptable Use Policy](https://llama.meta.com/llama3_1/use-policy). Built with Llama. 

### Team

- Yauhen Babakhin
- Radek Osmulski
- Ronay Ak
- Gabriel Moreira
- Mengyao Xu
- Benedikt Schifferer
- Bo Liu
- Even Oldridge

Correspondence to Yauhen Babakhin (ybabakhin@nvidia.com) and Bo Liu (boli@nvidia.com).

### Citation

```
@misc{babakhin2025llamaembednemotron8buniversaltextembedding,
      title={Llama-Embed-Nemotron-8B: A Universal Text Embedding Model for Multilingual and Cross-Lingual Tasks}, 
      author={Yauhen Babakhin and Radek Osmulski and Ronay Ak and Gabriel Moreira and Mengyao Xu and Benedikt Schifferer and Bo Liu and Even Oldridge},
      year={2025},
      eprint={2511.07025},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2511.07025}, 
}
```
### NVIDIA’s Retrieval Models

| Model Name                                | Use Case               | Comment                                                                         |
|-------------------------------------------|------------------------|---------------------------------------------------------------------------------|
| [nvidia/omni-embed-nemotron-3b](https://huggingface.co/nvidia/omni-embed-nemotron-3b) | Research-Only          | Omni-Modal Embedding Model for Retrieving Text, Images, Audio, or Video                    |
| [nvidia/llama-NemoRetriever-ColEmbed-3B-v1](https://huggingface.co/nvidia/llama-nemoretriever-colembed-3b-v1) | Research-Only          | #1 ViDoRe V1, V2 and MTEB VisualDocumentRetrieval as of June 27, 2025           |
| [nvidia/llama-nemotron-embed-1b-v2](https://huggingface.co/nvidia/llama-nemotron-embed-1b-v2)                | Commercial Application | Text Embedding Model for Production Use Case of Text Document Retrieval         |
| [nvidia/llama-nemotron-rerank-1b-v2](https://huggingface.co/nvidia/llama-nemotron-rerank-1b-v2)               | Commercial Application | Text Reranker Model for Production Use Case of Text Document Retrieval          |
| [llama-3_2-nemoretriever-1b-vlm-embed-v1](https://build.nvidia.com/nvidia/llama-3_2-nemoretriever-1b-vlm-embed-v1)   | Commercial Application | MultiModal Embedding Model for Production Use Case of Visual Document Retrieval |
| [nvidia/llama-NemoRetriever-ColEmbed-1B-v1](https://huggingface.co/nvidia/llama-nemoretriever-colembed-1b-v1) | Research-Only          | Smaller Version of nvidia/llama-NemoRetriever-ColEmbed-3B-v1                    |
| [nvidia/NV-Embed-v2](https://huggingface.co/nvidia/NV-Embed-v2)                        | Research-Only          | #1 MTEB as of Aug 30, 2024                                                      |
| [nvidia/MM-Embed](https://huggingface.co/nvidia/MM-Embed)                           | Research-Only          | Improved nvidia/NV-Embed-v1 and multimodal embeddings                           |
| [nvidia/NV-Retriever-v1](https://huggingface.co/nvidia/NV-Retriever-v1)                    | Research-Only          | #1 MTEB BEIR as of July 12, 2024 


### Deployment Geography:
Global <br>

### Use Case: <br>
The `llama-embed-nemotron-8b` model is intended for researchers developing applications that need to understand or retrieve information from text. It is well-suited for multilingual RAG systems in which queries and documents are textual and may be in different languages. <br>

### Release Date:  <br>
Hugging Face on 10/21/2025 via https://huggingface.co/nvidia/llama-embed-nemotron-8b <br>

## Model Architecture:
- **Architecture Type:** Transformer Decoder <br>

- **Network Architecture:** Llama-3.1-8B with bi-directional attention <br>

- This model was developed based on `meta-llama/Llama-3.1-8B` model. <br> 
- Number of model parameters: 7,504,924,672 <br>

This `llama-embed-nemotron-8b` embedding model is a fine-tuned version of `Llama-3.1-8B` transformer decoder architecture, with a bidirectional attention mechanism. The model consists of 32 hidden layers and an embedding size of 4096, and trained on public datasets and synthetically generated datasets. Embedding models for text retrieval are typically trained using a bi-encoder architecture. This involves encoding a pair of sentences (for example, query and chunked passages) independently using the embedding model. Contrastive learning is used to maximize the similarity between the query and the passage that contains the answer, while minimizing the similarity between the query and sampled negative passages not useful to answer the question. <br> 


## Input: <br>

| Property | Query | Document |
|----------|-------|----------|
| Input Type | Text | Text |
| Input Format | List of strings | List of strings |
| Input Parameter | One-Dimensional (1D) | 1D |
| Other Properties |  Maximum input sequence length is 32768 tokens. |  Maximum input sequence length is 32768 tokens. |

## Output: <br>
**Output Type(s):** Floats <br>
**Output Format:** List of floats <br>
**Output Parameters:** One-Dimensional (1D) <br>
**Other Properties Related to Output:** Model outputs embedding vectors of a dimension 4096 for each text input. <br>

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA’s hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions. <br> 

### Usage

The `llama-embed-nemotron-8b` model is instruction-aware, meaning that it supports custom instructions to improve performance for specific use cases or scenarios. In particular, for Retrieval use case, model expects:
- Queries accompanied with the task instruction in the following template: `f"Instruct: {task_instruction}\nQuery: {query}"`
- Documents (passages) without any special handling

The model requires transformers version 4.51.0 and flash-attention (for GPU processing)
```bash
pip install transformers==4.51.0
pip install flash-attn==2.6.3
```

#### Sentence Transformers:

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

attn_implementation = "eager"  # Or "flash_attention_2"
model = SentenceTransformer(
    "nvidia/llama-embed-nemotron-8b",
    trust_remote_code=True,
    model_kwargs={"attn_implementation": attn_implementation, "torch_dtype": "bfloat16"},
    tokenizer_kwargs={"padding_side": "left"},
)

queries = [
    "How do neural networks learn patterns from examples?"
]
documents = [
    "Deep learning models adjust their weights through backpropagation, using gradient descent to minimize error on training data and improve predictions over time.",
    "Market prices are determined by the relationship between how much people want to buy a product and how much is available for sale, with scarcity driving prices up and abundance driving them down.",
]

# NOTE: encode_query uses the "query" prompt automatically
query_embeddings = model.encode_query(queries)
document_embeddings = model.encode_document(documents)

scores = (query_embeddings @ document_embeddings.T)

print(scores.tolist())
# [[0.3770667314529419, 0.05808388814330101]]
```

#### Hugging Face Transformers

```python
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer


def average_pool(last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Average pooling with attention mask."""

    last_hidden_states = last_hidden_states.to(torch.float32)
    last_hidden_states_masked = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    embedding = last_hidden_states_masked.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    embedding = F.normalize(embedding, dim=-1)
    
    return embedding

# Define task and queries
def get_instruction(task_instruction: str, query: str) -> str:
    return f"Instruct: {task_instruction}\nQuery: {query}"

model_name_or_path = "nvidia/llama-embed-nemotron-8b"

attn_implementation = "flash_attention_2" if torch.cuda.is_available() else "eager"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    model_name_or_path,
    trust_remote_code=True,
    padding_side="left",
)

# Load model
model = AutoModel.from_pretrained(
    model_name_or_path, 
    trust_remote_code=True,
    torch_dtype=torch.float16,
    attn_implementation=attn_implementation,
).eval()
model = model.to("cuda:0" if torch.cuda.is_available() else "cpu")

# Model is instruction-aware, which requires each query to have a short instruction with the task instruction
task = "Given a question, retrieve passages that answer the question"
queries = [
    get_instruction(task, "How do neural networks learn patterns from examples?"),
]

# No instruction is required for documents corpus
documents = [
    "Deep learning models adjust their weights through backpropagation, using gradient descent to minimize error on training data and improve predictions over time.",
    "Market prices are determined by the relationship between how much people want to buy a product and how much is available for sale, with scarcity driving prices up and abundance driving them down.",
]
input_texts = queries + documents

# Tokenize the input texts
batch_dict = tokenizer(
    text=input_texts,
    max_length=4096,
    padding=True,
    truncation=True,
    return_tensors="pt",
).to(model.device)
attention_mask = batch_dict["attention_mask"]

# Forward pass
model_outputs = model(**batch_dict)

# Average pooling
embeddings = average_pool(model_outputs.last_hidden_state, attention_mask)

scores = (embeddings[:1] @ embeddings[1:].T)

print(scores.tolist())
# [[0.37644022703170776, 0.05794818699359894]]
```

#### vLLM

1. Ensure you are using `vllm>=0.14.0`.
2. Start the vLLM server with the following command:

Minimal command (required):
```
vllm serve \
    nvidia/llama-embed-nemotron-8b \
    --trust-remote-code
```

If you already have a local copy of the model, you can also pass the local
path instead of the HF repo ID.

Optional flags:

- `--dtype <float32|bfloat16|float16>` to force precision (the default is `auto`, which resolves from model config; this model defaults to BF16).
- `--data-parallel-size <num_gpus_to_use>` for multi-GPU serving.
- `--port 8000` to set the server port.

Online serving example (OpenAI SDK):

```
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",  # required by OpenAI SDK; ignored by default in local vLLM
)

response = client.embeddings.create(
    input=['Instruct: Given a question, retrieve passages that answer the question\nQuery: summit define'],
    model="nvidia/llama-embed-nemotron-8b",
)
response.data[0].embedding
```

Offline inference example (Python API, no server required):

```
from vllm import LLM

llm = LLM(
    model="nvidia/llama-embed-nemotron-8b",
    runner="pooling",
    trust_remote_code=True,
)

outputs = llm.embed(["Instruct: Given a question, retrieve passages that answer the question\nQuery: summit define", "a summit is a meeting"])
for output in outputs:
    print(len(output.outputs.embedding))
```

## Software Integration:
**Runtime Engine(s):** 
* TensorRT, Triton <br> 

**Supported Hardware Microarchitecture Compatibility:** <br>
* NVIDIA Ampere <br>
* NVIDIA Hopper <br>
* NVIDIA Lovelace <br>
* NVIDIA Pascal <br>
* NVIDIA Turing <br>
* NVIDIA Volta <br>

**Preferred/Supported Operating System(s):**
* Linux <br>

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment. This AI model can be embedded as an Application Programming Interface (API) call into the software environment described above.

## Model Version(s):
  
llama-embed-nemotron-8b-v1

## Training and Testing Datasets

### Training Dataset:

**Data Modality** <br>
* Text <br>

**Text Training Data Size** <br>
* 1 Billion to 10 Trillion Tokens

**Data Collection Method by dataset** <br>
* Hybrid: Human, Automated, Synthetic

**Labeling Method by dataset**
* Hybrid: Human, Automated, Synthetic<br>

**Properties:** 16.4M query-passage pairs from public and synthetically generated datasets. <br>

### Testing Dataset:

We test the model on 131 tasks from [MMTEB: Massive Multilingual Text Embedding Benchmark](https://huggingface.co/spaces/mteb/leaderboard) (`MTEB(Multilingual, v2)` split).

**Benchmark specs:** <br>
- Number of languages: 1038
- Number of task types: 9
- Number of domains: 20 <br>

**MMTEB Leaderboard Benchmark Ranking** <br>

Below we present results for `MTEB(Multilingual, v2)` split of MMTEB benchmark (as of October 21, 2025). Ranking on MMTEB Leaderboards is performed based on the Borda rank. Each task is treated as a preference voter, which gives votes on the models per their relative performance on the task. The best model obtains the highest number of votes. The model with the highest number of votes across tasks obtains the highest rank. The Borda rank tends to prefer models that perform well broadly across tasks.

| Borda Rank | Model | Borda Votes | Mean (Task) |
|-------|-------|---------------------|---------------------|
| **1.** | llama-embed-nemotron-8b | **39,573** | 69.46 |
| 2. | gemini-embedding-001      |         39,368            |         68.37            |
| 3. | Qwen3-Embedding-8B      |         39,364            |         **70.58**            |
| 4. | Qwen3-Embedding-4B      |         39,099           |         69.45            |
| 5. | Qwen3-Embedding-0.6B      |         37,419            |         64.34            |
| 6. | gte-Qwen2-7B-instruct | 37,167 | 62.51 |
| 7. | Linq-Embed-Mistral |  37,149 | 61.47 |

**Data Collection Method by dataset:**
* Hybrid: Automated, Human, Synthetic<br>

**Labeling Method by dataset:**

* Hybrid: Automated, Human, Synthetic <br>

**Properties:**  More details about MMTEB benchmark can be found on their [leaderboard](https://huggingface.co/spaces/mteb/leaderboard) or in their published [paper](https://arxiv.org/pdf/2502.13595). <br>


## Inference:
**Acceleration Engine:** GPU <br>
**Test Hardware:** A100 80GB, H100 80GB <br>

## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse. <br> 

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).