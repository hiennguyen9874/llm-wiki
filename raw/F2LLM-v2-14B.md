---
license: apache-2.0
language:
- en
- zh
- ru
- es
- fr
- de
- ar
- nl
- vi
- hi
- ko
- ja
- it
- id
- pt
- pl
- tr
- da
- th
- sv
- fa
- uk
- cs
- 'no'
- el
- ca
- ro
- fi
- bg
- tl
- gl
- my
- hy
- km
- ne
- hu
- eu
- he
- lo
- sw
- az
- lv
- si
- sk
- tg
- et
- lt
- ms
- hr
- is
- sl
- sr
- ur
- bn
- af
- ta
- ka
- te
- ml
- mn
- nn
- kk
- cy
- mr
- sq
- nb
- mk
- jv
- kn
- eo
- la
- gu
- uz
- am
- oc
- be
- mg
- vo
- pa
- lb
- ht
- br
- ga
- xh
- tt
- bs
- yo
base_model:
- codefuse-ai/F2LLM-v2-14B-Preview
pipeline_tag: feature-extraction
library_name: transformers
tags:
- sentence-transformers
datasets:
- codefuse-ai/F2LLM-v2
---

# F2LLM-v2-14B

F2LLM-v2 is a family of general-purpose, multilingual embedding models in 8 distinct sizes ranging from 80M to 14B. Trained on a curated composite of 60 million publicly available high-quality data, F2LLM-v2 supports more than 200 languages, with a particular emphasis on previously underserved mid- and low-resource languages.

F2LLM-v2 is fully open. We release base models in 5 sizes, instruct models in 8 sizes, the training data, the training code, and intermediate checkpoints. The three smallest instruct models are pruned and trained from the 0.6B base model.

| Model | Base                                                                                | Instruct                                                            |
| ----- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| 80M   |                                                                                     | [🤗F2LLM-v2-80M](https://huggingface.co/codefuse-ai/F2LLM-v2-80M)   |
| 160M  |                                                                                     | [🤗F2LLM-v2-160M](https://huggingface.co/codefuse-ai/F2LLM-v2-160M) |
| 330M  |                                                                                     | [🤗F2LLM-v2-330M](https://huggingface.co/codefuse-ai/F2LLM-v2-330M) |
| 0.6B  | [🤗F2LLM-v2-0.6B-Preview](https://huggingface.co/codefuse-ai/F2LLM-v2-0.6B-Preview) | [🤗F2LLM-v2-0.6B](https://huggingface.co/codefuse-ai/F2LLM-v2-0.6B) |
| 1.7B  | [🤗F2LLM-v2-1.7B-Preview](https://huggingface.co/codefuse-ai/F2LLM-v2-1.7B-Preview) | [🤗F2LLM-v2-1.7B](https://huggingface.co/codefuse-ai/F2LLM-v2-1.7B) |
| 4B    | [🤗F2LLM-v2-4B-Preview](https://huggingface.co/codefuse-ai/F2LLM-v2-4B-Preview)     | [🤗F2LLM-v2-4B](https://huggingface.co/codefuse-ai/F2LLM-v2-4B)     |
| 8B    | [🤗F2LLM-v2-8B-Preview](https://huggingface.co/codefuse-ai/F2LLM-v2-8B-Preview)     | [🤗F2LLM-v2-8B](https://huggingface.co/codefuse-ai/F2LLM-v2-8B)     |
| 14B   | [🤗F2LLM-v2-14B-Preview](https://huggingface.co/codefuse-ai/F2LLM-v2-14B-Preview)   | [🤗F2LLM-v2-14B](https://huggingface.co/codefuse-ai/F2LLM-v2-14B)   |

## Usage

### With Sentence Transformers

To encode text with the [Sentence Transformers](https://www.sbert.net/) library:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("codefuse-ai/F2LLM-v2-14B", device="cuda:0", model_kwargs={"torch_dtype": "bfloat16"})
# Some sample query and documents
query = "What is F2LLM used for?"
documents = [
    'We present F2LLM, a family of fully open embedding LLMs that achieve a strong balance between model size, training data, and embedding performance.',
    'F2LLM is a model for computing text embeddings that can be used for various NLP tasks such as information retrieval, semantic search, and text classification.',
    'F2LLM 是 CodeFuse 开源的系列嵌入模型。',
    'F2LLM — это модель вычисления встраивания текста, которую можно использовать для различных задач НЛП, таких как поиск информации, семантический поиск и классификация текста.'
]
# Encode the query and documents separately. The encode_query method uses the query prompt
query_embedding = model.encode_query(query)
document_embeddings = model.encode_document(documents)
print(query_embedding.shape, document_embeddings.shape)
# (5120,) (4, 5120)
# Compute cosine similarity between the query and documents
similarity = model.similarity(query_embedding, document_embeddings)
print(similarity)
# tensor([[0.5773, 0.8323, 0.7229, 0.8062]])
```

### With Transformers

Or directly with the [Transformers](https://huggingface.co/docs/transformers/index) library:

```python
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F
model_path = "codefuse-ai/F2LLM-v2-14B"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModel.from_pretrained(model_path, torch_dtype=torch.bfloat16, device_map={'': 0})
query = "What is F2LLM used for?"
query_prompt = "Instruct: Given a question, retrieve passages that can help answer the question.\nQuery: "
documents = [
    'We present F2LLM, a family of fully open embedding LLMs that achieve a strong balance between model size, training data, and embedding performance.',
    'F2LLM is a model for computing text embeddings that can be used for various NLP tasks such as information retrieval, semantic search, and text classification.',
    'F2LLM 是 CodeFuse 开源的系列嵌入模型。',
    'F2LLM — это модель вычисления встраивания текста, которую можно использовать для различных задач НЛП, таких как поиск информации, семантический поиск и классификация текста.'
]
def encode(sentences):
    batch_size = len(sentences)
    # the tokenizer will automatically add eos token
    tokenized_inputs = tokenizer(sentences, padding=True, return_tensors='pt').to(model.device)
    last_hidden_state = model(**tokenized_inputs).last_hidden_state
    eos_positions = tokenized_inputs.attention_mask.sum(dim=1) - 1
    embeddings = last_hidden_state[torch.arange(batch_size, device=model.device), eos_positions]
    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings
# Encode the query and documents
query_embedding = encode([query_prompt + query])
document_embeddings = encode(documents)
print(query_embedding.shape, document_embeddings.shape)
# torch.Size([1, 5120]) torch.Size([4, 5120])
# Compute cosine similarity between the query and documents
similarity = query_embedding @ document_embeddings.T
print(similarity)
# tensor([[0.5781, 0.8281, 0.7227, 0.8047]], device='cuda:1',
#        dtype=torch.bfloat16, grad_fn=<MmBackward0>)
```

### Prompts

The model supports custom instructions in the following format:

```text
Instruct: your_instruction
Query:
```

In general, for retrieval and reranking tasks:

- use the prompt for queries
- do not prepend the prompt to documents/passages

For symmetric tasks such as STS, clustering, and bitext mining, you can encode the documents either with or without prompts. The model is trained to support both scenarios.

## Intermediate Checkpoints

To facilitate future research, we release intermediate checkpoints in the `intermediate_checkpoints` branch.

## Citation

```
@misc{f2llm-v2,
      title={F2LLM-v2: Inclusive, Performant, and Efficient Embeddings for a Multilingual World}, 
      author={Ziyin Zhang and Zihan Liao and Hang Yu and Peng Di and Rui Wang},
      year={2026},
      eprint={2603.19223},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2603.19223}, 
}
```