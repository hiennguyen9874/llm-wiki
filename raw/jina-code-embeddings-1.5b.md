---
base_model:
- Qwen/Qwen2.5-Coder-1.5B
license: cc-by-nc-4.0
tags:
- feature-extraction
- mteb
- sentence-transformers
inference: false
library_name: transformers
---

<p align="center">
<img src="https://huggingface.co/datasets/jinaai/documentation-images/resolve/main/logo.webp" alt="Jina AI: Your Search Foundation, Supercharged!" width="150px">
</p>

# Jina Code Embeddings: A Small but Performant Code Embedding Model

## Intended Usage & Model Info
`jina-code-embeddings` is an embedding model for code retrieval. 
The model supports various types of code retrieval (text-to-code, code-to-code, code-to-text, code-to-completion) and technical question answering across 15+ programming languages. 


Built on [Qwen/Qwen2.5-Coder-1.5B](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B), `jina-code-embeddings-1.5b` features:

- **Multilingual support** (15+ programming languages) and compatibility with a wide range of domains, including web development, software development, machine learning, data science, and educational coding problems.
- **Task-specific instruction prefixes** for NL2Code, Code2Code, Code2NL, Code2Completion, and Technical QA, which can be selected at inference time.
- **Flexible embedding size**: dense embeddings are 1536-dimensional by default but can be truncated to as low as 128 with minimal performance loss.


Summary of features:

| Feature   | Jina Code Embeddings 1.5B   |
|------------|------------|
| Base Model | Qwen2.5-Coder-1.5B |
| Supported Tasks | `nl2code`, `code2code`, `code2nl`, `code2completion`, `qa` |
| Model DType | BFloat 16 |
| Max Sequence Length | 32768 |
| Embedding Vector Dimension | 1536 |
| Matryoshka dimensions | 128, 256, 512, 1024, 1536 |
| Pooling Strategy | Last-token pooling |
| Attention Mechanism | FlashAttention2 |

## Usage

<details>
  <summary>Requirements</a></summary>
  
The following Python packages are required:

- `transformers>=4.53.0`
- `torch>=2.7.1`
  
### Optional / Recommended
- **flash-attention**: Installing [flash-attention](https://github.com/Dao-AILab/flash-attention) is recommended for improved inference speed and efficiency, but not mandatory.
- **sentence-transformers**: If you want to use the model via the `sentence-transformers` interface, install this package as well.
</details>

<details>
  <summary>via <a href="https://huggingface.co/docs/transformers/en/index">transformers</a></summary>

```python
# !pip install transformers>=4.53.0 torch>=2.7.1

import torch
import torch.nn.functional as F

from transformers import AutoModel, AutoTokenizer

INSTRUCTION_CONFIG = {
    "nl2code": {
        "query": "Find the most relevant code snippet given the following query:\n",
        "passage": "Candidate code snippet:\n"
    },
    "qa": {
        "query": "Find the most relevant answer given the following question:\n",
        "passage": "Candidate answer:\n"
    },
    "code2code": {
        "query": "Find an equivalent code snippet given the following code snippet:\n",
        "passage": "Candidate code snippet:\n"
    },
    "code2nl": {
        "query": "Find the most relevant comment given the following code snippet:\n",
        "passage": "Candidate comment:\n"
    },
    "code2completion": {
        "query": "Find the most relevant completion given the following start of code snippet:\n",
        "passage": "Candidate completion:\n"
    }
}

MAX_LENGTH = 8192

def cosine_similarity(x,y):
    x = F.normalize(x, p=2, dim=1)
    y = F.normalize(y, p=2, dim=1)
    return x @ y.T

def last_token_pool(last_hidden_states, attention_mask):
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]

def add_instruction(instruction, query):
    return f'{instruction}{query}'

# The queries and documents to embed
queries = [
    add_instruction(INSTRUCTION_CONFIG["nl2code"]["query"], "print hello world in python"),
    add_instruction(INSTRUCTION_CONFIG["nl2code"]["query"], "initialize array of 5 zeros in c++")
]
documents = [
    add_instruction(INSTRUCTION_CONFIG["nl2code"]["passage"], "print('Hello World!')"),
    add_instruction(INSTRUCTION_CONFIG["nl2code"]["passage"], "int arr[5] = {0, 0, 0, 0, 0};")
]
all_inputs = queries + documents

tokenizer = AutoTokenizer.from_pretrained('jinaai/jina-code-embeddings-1.5b')
model = AutoModel.from_pretrained('jinaai/jina-code-embeddings-1.5b')

batch_dict = tokenizer(
    all_inputs,
    padding=True,
    truncation=True,
    max_length=MAX_LENGTH,
    return_tensors="pt",
)
batch_dict.to(model.device)
outputs = model(**batch_dict)
embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
query_embeddings = embeddings[:2]
passage_embeddings = embeddings[2:]

# Compute the (cosine) similarity between the query and document embeddings
scores = cosine_similarity(query_embeddings, passage_embeddings)
print(scores)
# tensor([[0.7647, 0.1115],
#         [0.0930, 0.6606]], grad_fn=<MmBackward0>)
```
</details>

<details>
  <summary>via <a href="https://sbert.net/">sentence-transformers</a></summary>

```python
# !pip install sentence_transformers>=5.0.0 torch>=2.7.1

import torch
from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer(
    "jinaai/jina-code-embeddings-1.5b",
    model_kwargs={
        "torch_dtype": torch.bfloat16,
        "attn_implementation": "flash_attention_2",
        "device_map": "cuda"
    },
    tokenizer_kwargs={"padding_side": "left"},
)

# The queries and documents to embed
queries = [
    "print hello world in python",
    "initialize array of 5 zeros in c++"
]
documents = [
    "print('Hello World!')",
    "int arr[5] = {0, 0, 0, 0, 0};"
]

query_embeddings = model.encode(queries, prompt_name="nl2code_query")
document_embeddings = model.encode(documents, prompt_name="nl2code_document")

# Compute the (cosine) similarity between the query and document embeddings
similarity = model.similarity(query_embeddings, document_embeddings)
print(similarity)
# tensor([[0.7670, 0.1117],
#         [0.0938, 0.6607]])
```
</details>

<details>
  <summary>via <a href="https://github.com/vllm-project/vllm">vLLM</a></summary>

```python

import torch
import torch.nn.functional as F
from vllm import LLM

INSTRUCTION_CONFIG = {
    "nl2code": {
        "query": "Find the most relevant code snippet given the following query:\n",
        "passage": "Candidate code snippet:\n"
    },
    "qa": {
        "query": "Find the most relevant answer given the following question:\n",
        "passage": "Candidate answer:\n"
    },
    "code2code": {
        "query": "Find an equivalent code snippet given the following code snippet:\n",
        "passage": "Candidate code snippet:\n"
    },
    "code2nl": {
        "query": "Find the most relevant comment given the following code snippet:\n",
        "passage": "Candidate comment:\n"
    },
    "code2completion": {
        "query": "Find the most relevant completion given the following start of code snippet:\n",
        "passage": "Candidate completion:\n"
    }
}

def add_instruction(instruction, text):
    return f"{instruction}{text}"

def cosine_similarity(x, y):
    x = F.normalize(x, p=2, dim=1)
    y = F.normalize(y, p=2, dim=1)
    return x @ y.T

# Build the queries and documents
queries = [
    add_instruction(INSTRUCTION_CONFIG["nl2code"]["query"], "print hello world in python"),
    add_instruction(INSTRUCTION_CONFIG["nl2code"]["query"], "initialize array of 5 zeros in c++"),
]
documents = [
    add_instruction(INSTRUCTION_CONFIG["nl2code"]["passage"], "print('Hello World!')"),
    add_instruction(INSTRUCTION_CONFIG["nl2code"]["passage"], "int arr[5] = {0, 0, 0, 0, 0};"),
]
all_inputs = queries + documents

# vLLM embedding model
llm = LLM(
    model="jinaai/jina-code-embeddings-1.5b",
    task="embed"
)

# Encode with vLLM
outputs = llm.encode(all_inputs)

# Collect embeddings into a single tensor
emb_list = []
for out in outputs:
    vec = out.outputs.data.detach()
    emb_list.append(vec)
embeddings = torch.stack(emb_list, dim=0)

# Split into query and passage embeddings
n_q = len(queries)
query_embeddings = embeddings[:n_q]
passage_embeddings = embeddings[n_q:]

# Cosine similarity matrix (queries x documents)
scores = cosine_similarity(query_embeddings, passage_embeddings)
print(scores)
# tensor([[0.7650, 0.1118],
#         [0.0937, 0.6613]])
```

</details>

## Citation

Please refer to our [technical report of jina-code-embeddings](https://arxiv.org/abs/2508.21290) for training details and benchmarks. If you find it useful in your research, please cite the following paper:

```
@misc{kryvosheieva2025efficientcodeembeddingscode,
      title={Efficient Code Embeddings from Code Generation Models}, 
      author={Daria Kryvosheieva and Saba Sturua and Michael Günther and Scott Martens and Han Xiao},
      year={2025},
      eprint={2508.21290},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2508.21290}, 
}
```

## Contact

Join our [Discord community](https://discord.jina.ai) and chat with other community members about ideas.