---
license: apache-2.0
language:
- en
base_model:
- Qwen/Qwen3-4B
pipeline_tag: text-ranking
tags:
- finance
- legal
- code
- stem
- medical
library_name: sentence-transformers
model_max_length: 32768
---

<img src="https://i.imgur.com/oxvhvQu.png"/>

# Releasing zeroentropy/zerank-2

In search engines, [rerankers are crucial](https://www.zeroentropy.dev/blog/what-is-a-reranker-and-do-i-need-one) for improving the accuracy of your retrieval system.

However, SOTA rerankers are closed-source and proprietary. At ZeroEntropy, we've trained a SOTA reranker outperforming closed-source competitors, and we're launching our model here on HuggingFace.

This reranker [outperforms proprietary rerankers](https://www.zeroentropy.dev/articles/zerank-2-advanced-instruction-following-multimodal-reranker) such as `cohere-rerank-v3.5` and `gemini-2.5-flash` across a wide variety of domains, including finance, legal, code, STEM, medical, and conversational data.

At ZeroEntropy we've developed an innovative multi-stage pipeline that models query-document relevance scores as adjusted [Elo ratings](https://en.wikipedia.org/wiki/Elo_rating_system). See our Technical Report (https://arxiv.org/abs/2509.12541
) for more details.

This model is released under the [Apache License 2.0](./LICENSE).

## Model Details

| Property | Value |
|---|---|
| Parameters | 4B |
| Context Length | 32,768 tokens (32k) |
| Base Model | Qwen/Qwen3-4B |
| License | Apache-2.0 |

## How to Use
> **Breaking change (May 2026):** `model.predict()` now returns raw "Yes" logits instead of sigmoid'd probabilities in `[0, 1]`. Rankings are unchanged. To recover the previous 0-1 score, apply `(scores / 5).sigmoid()` — see the example below. Loading no longer requires `trust_remote_code=True`; passing it is harmless.

### Using Sentence Transformers

Install Sentence Transformers:

```bash
pip install sentence_transformers
```

Then load the model and score query/document pairs. `model.predict` returns the raw "Yes" logit per pair; rankings can be used directly. To map the logits to a 0-1 score range, apply a temperature-scaled sigmoid: `sigmoid(score / 5)`.

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("zeroentropy/zerank-2")

query_documents = [
    ("What is 2+2?", "4"),
    ("What is 2+2?", "The answer is definitely 1 million"),
]

scores = model.predict(query_documents, convert_to_tensor=True)
print(scores)
# tensor([ 5.4062, -4.5000], device='cuda:0', dtype=torch.bfloat16)

# Optional: convert to 0-1 probabilities
probabilities = (scores / 5).sigmoid()
print(probabilities)
# tensor([0.7461, 0.2891], device='cuda:0', dtype=torch.bfloat16)
```

You can also use `model.rank` to score and sort a list of documents for a single query:

```python
rankings = model.rank(
    "What is 2+2?",
    ["4", "The answer is definitely 1 million"],
)
for r in rankings:
    print(r)
# {'corpus_id': 0, 'score': np.float32(5.40625)}
# {'corpus_id': 1, 'score': np.float32(-4.5)}
```

The model can also be inferenced using ZeroEntropy's [/models/rerank](https://docs.zeroentropy.dev/api-reference/models/rerank) endpoint, and on [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-o7avk66msiukc).

## Evaluations

NDCG@10 scores between `zerank-2` and competing closed-source proprietary rerankers. Since we are evaluating rerankers, OpenAI's `text-embedding-3-small` is used as an initial retriever for the Top 100 candidate documents.

| Domain | OpenAI embeddings | ZeroEntropy zerank-2 | ZeroEntropy zerank-1 | Gemini 2.5 Flash (Listwise) | Cohere rerank-3.5 |
|------------------|-------------------|----------------------|----------------------|-----------------------------|-------------------|
| Web | 0.3819 | **0.6346** | 0.6069 | 0.5765 | 0.5594 |
| Conversational | 0.4305 | **0.6140** | 0.5801 | 0.6021 | 0.5648 |
| STEM & Logic | 0.3744 | **0.6521** | 0.6283 | 0.5447 | 0.5418 |
| Code | 0.4582 | **0.6528** | 0.6310 | 0.6128 | 0.5364 |
| Legal | 0.4101 | **0.6644** | 0.6222 | 0.5565 | 0.5257 |
| Biomedical | 0.4783 | **0.7217** | 0.6967 | 0.5371 | 0.6246 |
| Finance | 0.6232 | 0.7600 | 0.7539 | **0.7694** | 0.7402 |
| **Average** | **0.4509** | **0.6714** | **0.6456** | **0.5999** | **0.5847** |

<img src="https://cdn-uploads.huggingface.co/production/uploads/65ec60ccfc59f6e77ecc9ccb/UiDp8LsY4XIdRK5i3CAdD.png" alt="Graph showing the same table" width="1000"/>

## License

This model is licensed under the [Apache License 2.0](./LICENSE).
