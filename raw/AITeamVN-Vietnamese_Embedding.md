---
license: apache-2.0
language:
- vi
base_model:
- BAAI/bge-m3
pipeline_tag: sentence-similarity
library_name: sentence-transformers
tags:
- Embedding
- onnx
---

 
## Model Card: Vietnamese_Embedding

Vietnamese_Embedding is an embedding model fine-tuned from the BGE-M3 model (https://huggingface.co/BAAI/bge-m3) to enhance retrieval capabilities for Vietnamese.

* The model was trained on approximately 300,000 triplets of queries, positive documents, and negative documents for Vietnamese.
* The model was trained with a maximum sequence length of 2048.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)
- **Maximum Sequence Length:** 2048 tokens
- **Output Dimensionality:** 1024 dimensions
- **Similarity Function:** Dot product Similarity
- **Language:** Vietnamese
- **Licence:** Apache 2.0

## Usage

```python
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer("AITeamVN/Vietnamese_Embedding")
model.max_seq_length = 2048
sentences_1 = ["Trí tuệ nhân tạo là gì", "Lợi ích của giấc ngủ"]
sentences_2 = ["Trí tuệ nhân tạo là công nghệ giúp máy móc suy nghĩ và học hỏi như con người. Nó hoạt động bằng cách thu thập dữ liệu, nhận diện mẫu và đưa ra quyết định.", 
               "Giấc ngủ giúp cơ thể và não bộ nghỉ ngơi, hồi phục năng lượng và cải thiện trí nhớ. Ngủ đủ giấc giúp tinh thần tỉnh táo và làm việc hiệu quả hơn."]
query_embedding = model.encode(sentences_1)
doc_embeddings = model.encode(sentences_2)
similarity = query_embedding @ doc_embeddings.T
print(similarity)

'''
array([[0.66212064, 0.33066642],
       [0.25866613, 0.5865289 ]], dtype=float32)
'''
```


### Evaluation:

- Dataset: Entire training dataset of Legal Zalo 2021. Our model was not trained on this dataset.

| Model                | Accuracy@1 | Accuracy@3 | Accuracy@5 | Accuracy@10  |  MRR@10 |
|----------------------|------------|------------|------------|-------------|--------------|
| Vietnamese_Reranker          | 0.7944     | 0.9324    | 0.9537     | 0.9740     | 0.8672       | 
| Vietnamese_Embedding_v2         | 0.7262     | 0.8927     | 0.9268     | 0.9578     | 0.8149       | 
| Vietnamese_Embedding  (public)          | 0.7274     | 0.8992     | 0.9305     | 0.9568     | 0.8181       | 
| Vietnamese-bi-encoder (BKAI)         | 0.7109     | 0.8680     | 0.9014     | 0.9299      | 0.7951       | 
| BGE-M3 | 0.5682     | 0.7728     | 0.8382     | 0.8921      | 0.6822       |

Vietnamese_Reranker and Vietnamese_Embedding_v2 was trained on 1100000 triplets. 

Although the score on the legal domain drops a bit on Vietnamese_Embedding_v2, since this phase data is much larger, it is very good for other domains.

You can access 2 model via link: [Vietnamese_Embedding_v2](AITeamVN/Vietnamese_Embedding_v2), [Vietnamese_Reranker](https://huggingface.co/AITeamVN/Vietnamese_Reranker)

You can reproduce the evaluation result by running code python evaluation_model.py (data downloaded from Kaggle).

## Contact

Email: nguyennhotrung3004@gmail.com

**Developer**

Member: Nguyễn Nho Trung, Nguyễn Nhật Quang, Nguyen Van Huy

## Citation

```Plaintext
@misc{Vietnamese_Embedding,
  title={Vietnamese_Embedding: Embedding model in Vietnamese language.},
  author={Nguyen Nho Trung, Nguyen Nhat Quang, Nguyen Van Huy},
  year={2025},
  publisher={Huggingface},
} 
```