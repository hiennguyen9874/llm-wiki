---
tags:
- mteb
- sentence-transformers
- transformers
language:
- multilingual
- af
- am
- ar
- as
- az
- be
- bg
- bn
- br
- bs
- ca
- cs
- cy
- da
- de
- el
- en
- eo
- es
- et
- eu
- fa
- fi
- fr
- fy
- ga
- gd
- gl
- gu
- ha
- he
- hi
- hr
- hu
- hy
- id
- is
- it
- ja
- jv
- ka
- kk
- km
- kn
- ko
- ku
- ky
- la
- lo
- lt
- lv
- mg
- mk
- ml
- mn
- mr
- ms
- my
- ne
- nl
- 'no'
- om
- or
- pa
- pl
- ps
- pt
- ro
- ru
- sa
- sd
- si
- sk
- sl
- so
- sq
- sr
- su
- sv
- sw
- ta
- te
- th
- tl
- tr
- ug
- uk
- ur
- uz
- vi
- xh
- yi
- zh
license: mit
---

## harrier-oss-v1

harrier-oss-v1 is a family of multilingual text embedding models developed by Microsoft.
The models use decoder-only architectures with last-token pooling and L2 normalization to produce dense text embeddings.
They can be applied to a wide range of tasks, including but not limited to **retrieval**, **clustering**, **semantic similarity**, **classification**, **bitext mining**, and **reranking**.
The models achieve state-of-the-art results on the [Multilingual MTEB v2](https://huggingface.co/spaces/mteb/leaderboard) benchmark as of the release date.

| Model                                                                       | Parameters | Embedding Dimension | Max Tokens | MTEB v2 Score |
|-----------------------------------------------------------------------------|------------|---------------------|------------|---------------|
| [harrier-oss-v1-270m](https://huggingface.co/microsoft/harrier-oss-v1-270m) | 270M       | 640                 | 32,768     | 66.5          |
| [harrier-oss-v1-0.6b](https://huggingface.co/microsoft/harrier-oss-v1-0.6b) | 0.6B       | 1,024               | 32,768     | 69.0          |
| [harrier-oss-v1-27b](https://huggingface.co/microsoft/harrier-oss-v1-27b)   | 27B        | 5,376               | 32,768     | **74.3**      |

## Training

All models are trained with contrastive learning objectives on a large-scale mixture of multilingual datasets covering diverse tasks.
The 270m and 0.6b variants are additionally trained with knowledge distillation from larger embedding models.

## Usage

Below is an example to encode queries and passages from the MS-MARCO passage ranking dataset.

### Sentence Transformers

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("microsoft/harrier-oss-v1-0.6b", model_kwargs={"dtype": "auto"})

queries = [
    "how much protein should a female eat",
    "summit define",
]
documents = [
    "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day.",
    "Definition of summit for English Language Learners. : 1  the highest point of a mountain : the top of a mountain. : 2  the highest level. : 3  a meeting or series of meetings between the leaders of two or more governments."
]

query_embeddings = model.encode(queries, prompt_name="web_search_query")
document_embeddings = model.encode(documents)

scores = (query_embeddings @ document_embeddings.T) * 100
print(scores.tolist())
```

Have a look at [config_sentence_transformers.json](config_sentence_transformers.json) for the prompts that are pre-configured, such as `web_search_query`, `sts_query`, and `bitext_query`. You can also use a custom instruction directly via e.g. `model.encode(queries, prompt="Instruct: Retrieve semantically similar text\nQuery: ")`.


### Transformers

```python
import torch
import torch.nn.functional as F

from torch import Tensor
from transformers import AutoTokenizer, AutoModel


def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery: {query}'


# Each query must come with a one-sentence instruction that describes the task
task = 'Given a web search query, retrieve relevant passages that answer the query'
queries = [
    get_detailed_instruct(task, 'how much protein should a female eat'),
    get_detailed_instruct(task, 'summit define')
]
# No need to add instruction for retrieval documents
documents = [
    "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day.",
    "Definition of summit for English Language Learners. : 1  the highest point of a mountain : the top of a mountain. : 2  the highest level. : 3  a meeting or series of meetings between the leaders of two or more governments."
]
input_texts = queries + documents

tokenizer = AutoTokenizer.from_pretrained('microsoft/harrier-oss-v1-0.6b')
model = AutoModel.from_pretrained('microsoft/harrier-oss-v1-0.6b', dtype='auto')
model.eval()
model.cuda()

max_length = 32768
# Tokenize the input texts
batch_dict = tokenizer(input_texts, max_length=max_length, padding=True, truncation=True, return_tensors='pt')
batch_dict = {k: v.cuda() for k, v in batch_dict.items()}

outputs = model(**batch_dict)
embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

# normalize embeddings
embeddings = F.normalize(embeddings, p=2, dim=1)
scores = (embeddings[:2] @ embeddings[2:].T) * 100
print(scores.tolist())
```

## Supported Languages

The models are trained on multilingual data and support a wide range of languages,
including but not limited to: Arabic, Bulgarian, Catalan, Czech, Danish, German, Greek, English, Spanish,
Estonian, Persian, Finnish, French, Hebrew, Hindi, Croatian, Hungarian, Indonesian, Italian, Japanese,
Korean, Lithuanian, Latvian, Macedonian, Malay, Dutch, Norwegian, Polish, Portuguese, Romanian, Russian,
Slovak, Slovenian, Albanian, Serbian, Swedish, Thai, Turkish, Ukrainian, Urdu, Vietnamese, and Chinese.

## Evaluation

Please follow the [mteb](https://github.com/embeddings-benchmark/mteb) repository on how to reproduce our scores.
The evaluation prompts used for each task are also available at [mteb_v2_eval_prompts.json](mteb_v2_eval_prompts.json).

## FAQ

**1. Do I need to add instructions to the query?**

Yes, this is how the model is trained, otherwise you will see a performance degradation.
The task definition should be a one-sentence instruction that describes the task.
This is a way to customize text embeddings for different scenarios through natural language instructions.

On the other hand, there is no need to add instructions to the document side.

**2. Why are my reproduced results slightly different from reported in the model card?**

Different versions of `transformers` and `pytorch` could cause negligible but non-zero performance differences.

**3. What pooling strategy does this model use?**

The model uses **last-token pooling** — the embedding of the last non-padding token is used as the sentence representation.
The embedding is then L2-normalized. This is handled automatically when using Sentence Transformers.
