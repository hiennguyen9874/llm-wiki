---
license: apache-2.0
language:
- vi
base_model:
- BAAI/bge-reranker-v2-m3
pipeline_tag: sentence-similarity
library_name: sentence-transformers
tags:
- Embedding
- Reranker
---

 
## Model Card: Vietnamese_Reranker

Vietnamese_Reranker is an reranker model fine-tuned from the bge-reranker-v2-m3 model (https://huggingface.co/BAAI/bge-reranker-v2-m3) to enhance retrieval capabilities for Vietnamese.

* The model was trained on approximately 1,100,000 triplets of queries, positive documents, and negative documents for Vietnamese.
* The model was trained with a maximum sequence length of 2304 (256 for query and 2048 for passages).

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- **Maximum Sequence Length:** 2304 tokens (256 for query and 2048 for passages)
- **Output Dimensionality:** 1024 dimensions
- **Similarity Function:** Dot product Similarity
- **Language:** Vietnamese
- **Licence:** Apache 2.0

## Usage

```python
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('AITeamVN/Vietnamese_Reranker')
model = AutoModelForSequenceClassification.from_pretrained('AITeamVN/Vietnamese_Reranker')
model.eval()
MAX_LENGTH = 2304
pairs = [['Trí tuệ nhân tạo là gì?', 'Trí tuệ nhân tạo là công nghệ giúp máy móc suy nghĩ và học hỏi như con người. Nó hoạt động bằng cách thu thập dữ liệu, nhận diện mẫu và đưa ra quyết định.'],
         ['Trí tuệ nhân tạo là gì?', 'Giấc ngủ giúp cơ thể và não bộ nghỉ ngơi, hồi phục năng lượng và cải thiện trí nhớ. Ngủ đủ giấc giúp tinh thần tỉnh táo và làm việc hiệu quả hơn.']]
with torch.no_grad():
    inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=MAX_LENGTH)
    scores = model(**inputs, return_dict=True).logits.view(-1, ).float()
    print(scores)

'''
# tensor([ 7.5590, -9.0743])
'''
```


### Evaluation:

- Dataset: Entire training dataset of Legal Zalo 2021. Our model was not trained on this dataset.

| Model                | Accuracy@1 | Accuracy@3 | Accuracy@5 | Accuracy@10  |  MRR@10 |
|----------------------|------------|------------|------------|-------------|--------------|
| Vietnamese_Reranker            | 0.7944     | 0.9324    | 0.9537     | 0.9740     | 0.8672       | 
| Vietnamese_Embedding_v2           | 0.7262     | 0.8927     | 0.9268     | 0.9578     | 0.8149       | 
| Vietnamese_Embedding            | 0.7274     | 0.8992     | 0.9305     | 0.9568     | 0.8181       | 
| Vietnamese-bi-encoder (BKAI)         | 0.7109     | 0.8680     | 0.9014     | 0.9299      | 0.7951       | 
| BGE-M3 | 0.5682     | 0.7728     | 0.8382     | 0.8921      | 0.6822       |

Vietnamese_Reranker and Vietnamese_Embedding_v2 was trained on 1,100,000 triplets. 

Although the score on the legal domain drops a bit on Vietnamese_Embedding_v2 (Phase 2), since this phase data is much larger, it is  good for other domains.


## Contact

Email: nguyennhotrung3004@gmail.com

**Developer**

Member: Nguyễn Nho Trung, Nguyễn Nhật Quang, Nguyễn Văn Huy.

## Citation

```Plaintext
@misc{Vietnamese_Embedding,
  title={Vietnamese_Embedding: Embedding model in Vietnamese language.},
  author={Nguyen Nho Trung, Nguyen Nhat Quang, Nguyễn Văn Huy},
  year={2025},
  publisher={Huggingface},
} 
```