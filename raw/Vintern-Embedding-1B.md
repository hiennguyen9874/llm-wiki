---
library_name: transformers
language:
- vi
- en
- zh
base_model:
- 5CD-AI/Vintern-1B-v3_5
pipeline_tag: visual-document-retrieval
---
![image/jpeg](https://cdn-uploads.huggingface.co/production/uploads/6336b5c831efcb5647f00170/fIGkSSYfHtG7MN3iCgqZe.jpeg)


## Model Details

**Vintern-Embedding-1B** is the next-generation embedding model built on top of the base [Vintern-1B-v3\_5](https://huggingface.co/5CD-AI/Vintern-1B-v3_5). It was trained on over **1.5 million high-quality question–document pairs**, including both **Visual Question Answering (VQA)** and **pure text QA** tasks. Leveraging this large and diverse dataset, the model is capable of handling a wide range of **cross-modal retrieval tasks**, including:

* **Text → Visual**
* **Text → Text**

Compared to **ColVintern-1B-v1**, which was more experimental, this version is significantly optimized and achieves **much higher retrieval quality**. Despite having only **\~0.9B parameters**, it performs competitively with larger 2B–7B multimodal embedding models, making it both **lightweight and highly effective**.

---

### Benchmark Highlights

* **GreenNode/Markdown Table Retrieval (Vietnamese)**

  * Achieved **MAP\@5 = 57.01** and **Mean = 59.71**, clearly multi-vector embedding outperforming all existing multilingual and Vietnamese-specific embedding baselines.

* **GreenNode/Zalo Legal Text Retrieval (Vietnamese)**

  * Scored **Mean = 73.14**, on par with or surpassing Vietnamese-specialized models, showing strong performance on legal retrieval tasks.

* **ViDoRe Benchmark (Global Multimodal Standard)**

  * Reached **Average Score = 82.85**, improving over **ColVintern-1B v1 (78.8)** and approaching the performance of several 2B–3B multimodal embedding models.
  * Particularly strong in domains such as **Artificial Intelligence (97.52)**, **Healthcare (97.09)**, and **Government (93.97)**.

---

### Summary

👉 **Vintern-Embedding-1B (v2)** delivers **robust cross-modal retrieval**, excels on both **Vietnamese-specific** and **global multimodal benchmarks**, and remains highly **efficient at \~1B parameters**. It is a strong choice for **RAG pipelines**, **multimodal search engines**, and **information retrieval applications** in both **English and Vietnamese**.


### Benchmark Details

Dataset:  [GreenNode/GreenNode-Table-Markdown-Retrieval](https://huggingface.co/datasets/GreenNode/GreenNode-Table-Markdown-Retrieval-VN)

| Model Name                             | MAP@5 ↑ | MRR@5 ↑ | NDCG@5 ↑ | Recall@5 ↑ | Mean ↑ |
|----------------------------------------|---------|---------|----------|------------|--------|
| **Multilingual Embedding models**      |         |         |          |            |        |
| me5_small                              | 33.75   | 33.75   | 35.68    | 41.49      | 36.17  |
| me5_large                              | 38.16   | 38.16   | 40.27    | 46.62      | 40.80  |
| M3-Embedding                           | 36.52   | 36.52   | 38.60    | 44.84      | 39.12  |
| OpenAI-embedding-v3                    | 30.61   | 30.61   | 32.57    | 38.46      | 33.06  |
| **Vietnamese Embedding models (Prior Work)** |   |         |          |            |        |
| halong-embedding                       | 32.15   | 32.15   | 34.13    | 40.09      | 34.63  |
| sup-SimCSE-VietNamese-phobert_base     | 10.90   | 10.90   | 12.03    | 15.41      | 12.31  |
| vietnamese-bi-encoder                  | 13.61   | 13.61   | 14.63    | 17.68      | 14.89  |
| **GreenNode-Embedding**               |         |         |          |            |        |
| M3-GN-VN                               | 41.85 | 41.85 | 44.15  | 57.05    | 46.23|
| M3-GN-VN-Mixed                         | 42.08   | 42.08   | 44.33    | 51.06      | 44.89  |
| **Ours – Multi-vector embedding**   |         |         |          |            |        |
| Vintern-Embedding-1B                      | 57.01   | 57.01   | 59.17    | 65.65      | 59.71  |
				

Dataset:  [GreenNode/zalo-ai-legal-text-retrieval-vn](https://huggingface.co/datasets/GreenNode/zalo-ai-legal-text-retrieval-vn)


| Model Name                             | MAP@5 ↑ | MRR@5 ↑ | NDCG@5 ↑ | Recall@5 ↑ | Mean ↑ |
|----------------------------------------|---------|---------|----------|------------|--------|
| **Multilingual Embedding models**      |         |         |          |            |        |
| me5_small                              | 54.68   | 54.37   | 58.32    | 69.16      | 59.13  |
| me5_large                              | 60.14   | 59.62   | 64.17    | 76.02      | 64.99  |
| M3-Embedding                           | 69.34  |  68.96  |  73.70   |  86.68     |  74.67 |
| OpenAI-embedding-v3                    | 38.68   | 38.80   | 41.53    | 49.94      | 41.74  |
| **Vietnamese Embedding models (Prior Work)** |         |         |          |            |        |
| halong-embedding                       | 52.57   | 52.28   | 56.64    | 68.72      | 57.55  |
| sup-SimCSE-VietNamese-phobert_base     | 25.15   | 25.07   | 27.81    | 35.79      | 28.46  |
| vietnamese-bi-encoder                  | 54.88   | 54.47   | 59.10    | 79.51      | 61.99  |
| **GreenNode-Embedding**                |         |         |          |            |        |
| M3-GN-VN                               | 65.03   | 64.80   | 69.19    | 81.66      | 70.17  |
| M3-GN-VN-Mixed                         | 69.75   | 69.28   | 74.01    | 86.74      | 74.95  |
| **Ours – Multi-vector embedding**   |         |         |          |            |        |
| Vintern-Embedding-1B                   | 68.90   | 69.06   | 72.32    | 82.29      | 73.14  |

				
Dataset: [ViDoRe Benchmark](https://huggingface.co/collections/vidore/vidore-benchmark-667173f98e70a1c0fa4db00d)


![image/png](https://cdn-uploads.huggingface.co/production/uploads/6336b5c831efcb5647f00170/BtTD8aky0w4SDZUvrP-XF.png)

| Model                                          | Model_Size | Average_Score | ArxivQA | DocVQA | InfoVQA | Artificial Intelligence | Energy | Government | Healthcare Industry | TAT-DQA |
|-----------------------------------------------|------------|---------------|---------|--------|---------|-------------------------|--------|------------|----------------------|---------|
| royokong/e5-v                                 | 8.3B       | 62.88         | 48.3    | 34.7   | 69.2    | 78.9                    | 78.1   | 82.2       | 82.3                 | 29.3    |
| TIGER-Lab/VLM2Vec-Full                        | 4.2B       | 51.16         | 42.8    | 26.7   | 66.7    | 53.5                    | 63.5   | 64         | 70.7                 | 21.4    |
| nvidia/llama-nemoretriever-colembed-3b-v1     | 4.4B       | 90.42         | 88.4    | 66.2   | 94.9    | 99.6                    | 96.6   | 97.8       | 99.3                 | 80.6    |
| nvidia/llama-nemoretriever-colembed-1b-v1     | 2.4B       | 89.8          | 87.6    | 64.5   | 93.6    | 100                     | 96.6   | 96.7       | 99.6                 | 79.8    |
| jinaai/jina-embeddings-v4                     | 3.8B     | 89.38         | 88.5    | 60.1   | 93.8    | 99.3                    | 97.3   | 96.6       | 99.1                 | 80.3    |
| nomic-ai/colnomic-embed-multimodal-3b         | 3B       | 89.25         | 88.1    | 61.3   | 92.8    | 96.3                    | 97.4   | 96.6       | 98.3                 | 83.2    |
| nomic-ai/colnomic-embed-multimodal-7b         | 7B       | 89.00         | 88.3    | 60.1   | 92.2    | 98.8                    | 96.3   | 95.9       | 99.3                 | 81.1    |
| vidore/colqwen2.5-v0.2                        | 3B       | 89.58         | 88.9    | 63.6   | 92.5    | 99.6                    | 96.1   | 95.8       | 98                   | 82.1    |
| vidore/colqwen2-v1.0                          | 2.2B     | 89.18         | 88      | 61.5   | 92.5    | 99                      | 95.9   | 95.5       | 98.8                 | 82.2    |
| ibm-granite/granite-vision-3.3-2b-embedding   | 3B       | 85.98         | 84.2    | 54.6   | 89.7    | 98.9                    | 96.3   | 97.3       | 98.9                 | 67.9    |
| vidore/colpali-v1.3                           | 3B       | 85.44         | 83.3    | 58.4   | 85.5    | 97.4                    | 94.6   | 96.1       | 97.4                 | 70.8    |
| vidore/colpali-v1.2                           | 3B       | 83.16         | 77.8    | 56.6   | 82.2    | 97.5                    | 93.8   | 94.4       | 94.9                 | 68.1    |
| ColVintern-1B                                 | 0.9B     | 78.8          | 71.6    | 48.3   | 84.6    | 92.9                    | 88.7   | 89.4       | 95.2                 | 59.6    |
| **Vintern-Embedding-1B**                      | 0.9B     | 82.85         | 75.37   | 51.79  | 86.2    | 97.52                   | 93.19  | 93.97      | 97.09                | 67.72   |

## Examples:

**Query Input:**
```
"Sử dụng ma tuý bị gì ?"
```
Relevant Document Output:
```
Ma túy, thuốc gây nghiện, thuốc hướng thần và tiền chất ma túy;
c) Vi phạm các quy định về nghiên cứu, giám định, kiểm định, kiểm nghiệm, sản xuất, bảo quản, tồn trữ chất ma túy, tiền chất ma túy;
d) Vi phạm các quy định về giao nhận, tàng trữ, vận chuyển chất ma túy, thuốc gây nghiện, thuốc hướng thần, tiền chất ma túy;
đ) Vi phạm các quy định về phân phối, mua bán, sử dụng, trao đổi chất ma túy, thuốc gây nghiện, thuốc hướng thần, tiền chất ma túy;
e) Vi phạm các quy định về quản lý, kiểm soát, lưu giữ chất ma túy, thuốc gây nghiện, thuốc hướng thần, tiền chất tại các khu vực cửa khẩu, biên giới, trên biển;
g) Thực hiện cai nghiện ma túy vượt quá phạm vi hoạt động được ghi trong giấy phép hoạt động cai nghiện ma túy tự nguyện.
6. Phạt tiền từ 40.000.000 đồng đến 50.000.000 đồng đối với hành vi cho mượn, cho thuê, chuyển nhượng hoặc sử dụng giấy phép hoạt động cai nghiện ma túy tự nguyện vào các mục đích khác.
7. Phạt tiền từ 50.000.000 đồng đến 75.000.000 đồng đối với hành vi tổ chức cai nghiện ma tú
```

**Query Input:**
```
"Đi xe bằng 1 bánh bị phạt bao nhiêu ?"
```
Relevant Image Output:
<img src="https://cdn-uploads.huggingface.co/production/uploads/6336b5c831efcb5647f00170/X3oqsaFXmjIXP6EbZo74U.png"
     alt="Relevant output"
     style="width:400px; height:auto;">

**Query Input:**
```
"Kinh tế Campuchia tăng trưởng như nào năm 2021 ?"
```
Relevant Image Output:
<img src="https://cdn-uploads.huggingface.co/production/uploads/6336b5c831efcb5647f00170/HjdqTV_lCsd3PsheukC49.png"
     alt="Relevant output"
     style="width:400px; height:auto;">

**Query Input:**
```
"Công nghiệp từ năm 2017 tăng trưởng ra sao ?"
```
Relevant Image Output:
<img src="https://cdn-uploads.huggingface.co/production/uploads/6336b5c831efcb5647f00170/yaWo4EiQ8hhCDj9jzOaMu.png"
     alt="Relevant output"
     style="width:400px; height:auto;">

## Quickstart:
Installation:

```bash
pip install decord
pip install transformers==4.48.2
pip install flash_attn
```
Download samples:

```bash
wget https://huggingface.co/5CD-AI/ColVintern-1B-v1/resolve/main/ex1.jpg
wget https://huggingface.co/5CD-AI/ColVintern-1B-v1/resolve/main/ex2.jpg
```

Inference:

```python
import torch
from PIL import Image
from transformers import AutoModel, AutoProcessor
import matplotlib.pyplot as plt

# ==============================
# 1. Load Model and Processor
# ==============================
model_name = "5CD-AI/Vintern-Embedding-1B"

model = AutoModel.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,       
    low_cpu_mem_usage=True,
    trust_remote_code=True,
).eval().cuda()                        

processor = AutoProcessor.from_pretrained(
    model_name,
    trust_remote_code=True
)

# ==============================
# 2. Prepare Input Data
# ==============================
# !wget https://huggingface.co/5CD-AI/ColVintern-1B-v1/resolve/main/ex1.jpg
# !wget https://huggingface.co/5CD-AI/ColVintern-1B-v1/resolve/main/ex2.jpg
images = [Image.open("ex1.jpg"), Image.open("ex2.jpg")]
batch_images = processor.process_images(images)

queries = [
    "Cảng Hải Phòng ở đâu ?",
    "Phí giao hàng bao nhiêu ?",
]
batch_queries = processor.process_queries(queries)

text_documents = [
    "Cảng Hải Phòng là một cụm cảng biển tổng hợp cấp quốc gia, lớn thứ 2 ở Việt Nam sau cảng Sài Gòn, là cửa ngõ quốc tế của Việt Nam, nằm tại ba quận Hồng Bàng, Ngô Quyền và Hải An. Bên cạnh đó, cùng tên Cảng Hải Phòng (tiếng Anh: Port of Hai Phong hoặc Hai Phong Port) là một cụm cảng biển thuộc Công ty cổ phần cảng Hải Phòng tại thành phố Hải Phòng, Việt Nam. Đây là một trong hai cảng biển tổng hợp lớn và lâu đời nhất tại Việt Nam, cùng với Công ty Cảng Sài Gòn ở phía Nam.",
    "Sân bay Chu Lai (tỉnh Quảng Nam) cũng được hãng hàng không giá rẻ Vietjet đề xuất đầu tư nâng cấp 20.000 tỉ đồng theo 3 giai đoạn từ 2020-2025 để đến năm 2025 trở thành Cảng hàng không quốc tế và trở thành trung tâm trung chuyển, vận tải hàng hóa lớn của cả nước theo quy hoạch của Bộ GTVT năm 2015.",
]
batch_text_docs = processor.process_docs(text_documents)

raw_docs = images + text_documents

# ==============================
# 3. Move Tensors to GPU
# ==============================
batch_images["pixel_values"] = batch_images["pixel_values"].cuda().bfloat16()
batch_images["input_ids"] = batch_images["input_ids"].cuda()
batch_images["attention_mask"] = batch_images["attention_mask"].cuda().bfloat16()

batch_queries["input_ids"] = batch_queries["input_ids"].cuda()
batch_queries["attention_mask"] = batch_queries["attention_mask"].cuda().bfloat16()

batch_text_docs["input_ids"] = batch_text_docs["input_ids"].cuda()
batch_text_docs["attention_mask"] = batch_text_docs["attention_mask"].cuda().bfloat16()

# ==============================
# 4. Generate Embeddings
# ==============================
with torch.no_grad():
    image_embeddings = model(**batch_images)
    query_embeddings = model(**batch_queries)
    text_docs_embeddings = model(**batch_text_docs)

# ==============================
# 5. Compute Similarity Scores
# ==============================
scores = processor.score_multi_vector(
    query_embeddings,
    list(image_embeddings) + list(text_docs_embeddings)
)

max_scores, max_indices = torch.max(scores, dim=1)

# ==============================
# 6. Print Results
# ==============================
for i, query in enumerate(queries):
    print("=" * 100)
    print(f"Query: '{query}'")
    print(f"Score: {max_scores[i].item()}\n")
    
    doc = raw_docs[max_indices[i]]
    if isinstance(doc, str):
        print(f"Matched Text Document:\n{doc}\n")
    else:
        plt.figure(figsize=(5, 5))
        plt.imshow(doc)
        plt.axis("off")
        plt.show()

```

Quickstart Google Colab: https://colab.research.google.com/drive/1jkP7fJja5RmSrP5Ad0_Csu7zPtIz-AwV?usp=sharing