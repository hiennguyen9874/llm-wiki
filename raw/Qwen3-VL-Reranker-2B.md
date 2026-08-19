---
license: apache-2.0
library_name: transformers
pipeline_tag: text-ranking
base_model:
- Qwen/Qwen3-VL-2B-Instruct
tags:
- sentence-transformers
- transformers
- multimodal rerank
- text rerank
---
# Qwen3-VL-Reranker-2B

<p align="center">
    <img src="https://model-demo.oss-cn-hangzhou.aliyuncs.com/Qwen3-VL-Reranker.png" width="400"/>
<p>

## Highlights

The **Qwen3-VL-Embedding** and **Qwen3-VL-Reranker** model series are the latest additions to the Qwen family, built upon the recently open-sourced and powerful Qwen3-VL foundation model. Specifically designed for multimodal information retrieval and cross-modal understanding, this suite accepts diverse inputs including text, images, screenshots, and videos, as well as inputs containing a mixture of these modalities.

While the Embedding model generates high-dimensional vectors for broad applications like retrieval and clustering, the Reranker model is engineered to refine these results, establishing a comprehensive pipeline for state-of-the-art multimodal search.

- **Multimodal Versatility**: Both models seamlessly handle a wide range of inputs—including text, images, screenshots, and video—within a unified framework. They deliver state-of-the-art performance across diverse multimodal tasks such as image-text retrieval, video-text matching, visual question answering (VQA), and multimodal content clustering.

- **Unified Representation Learning (Embedding)**: By leveraging the Qwen3-VL architecture, the Embedding model generates semantically rich vectors that capture both visual and textual information in a shared space. This facilitates efficient similarity computation and retrieval across different modalities.

- **High-Precision Reranking (Reranker)**: We also introduce the Qwen3-VL-Reranker series to complement the embedding model. The reranker takes a (query, document) pair as input—where both query and document may contain arbitrary single or mixed modalities—and outputs a precise relevance score. In retrieval pipelines, the two models are typically used in tandem: the embedding model performs efficient initial recall, while the reranker refines results in a subsequent re-ranking stage. This two-stage approach significantly boosts retrieval accuracy.

- **Exceptional Practicality**: Inheriting Qwen3-VL’s multilingual capabilities, the series supports over 30 languages, making it ideal for global applications. It is highly practical for real-world scenarios, offering flexible vector dimensions, customizable instructions for specific use cases, and strong performance even with quantized embeddings. These capabilities enable developers to seamlessly integrate both models into existing pipelines, unlocking powerful cross-lingual and cross-modal understanding.

**Qwen3-VL-Reranker-2B** has the following features:

- Model Type: MultiModal Rerank
- Supported Languages: 30+ Languages
- Supported Input Modalities: Text, images, screenshots, videos, and arbitrary multimodal combinations (e.g., text + image, text + video)
- Number of Parameters: 2B
- Context Length: 32k

For more details, including benchmark evaluation, hardware requirements, and inference performance, please refer to our [technical report](https://arxiv.org/abs/2601.04720), [blog](https://qwen.ai/blog?id=qwen3-vl-embedding), [GitHub](https://github.com/QwenLM/Qwen3-VL-Embedding).

## Qwen3-VL-Embedding and Qwen3-VL-Reranker Model list

| Model | Size | Model Layers | Sequence Length | Embedding Dimension | Quantization Support | MRL Support | Instruction Aware |
|---|---|---|---|---|----------------------|---|---|
| [Qwen3-VL-Embedding-2B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) | 2B | 28 | 32K | 2048 | Yes | Yes | Yes |
| [Qwen3-VL-Embedding-8B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B) | 8B | 36 | 32K | 4096 | Yes | Yes | Yes |
| [Qwen3-VL-Reranker-2B](https://huggingface.co/Qwen/Qwen3-VL-Reranker-2B) | 2B | 28 | 32K | - | -  | - | Yes |
| [Qwen3-VL-Reranker-8B](https://huggingface.co/Qwen/Qwen3-VL-Reranker-8B) | 8B | 36 | 32K | - | -  | - | Yes |

> **Note**:
> - `Quantization Support` indicates the supported quantization post process for the output embedding. 
> - `MRL Support` indicates whether the embedding model supports custom dimensions for the final embedding. 
> - `Instruction Aware` notes whether the embedding or reranking model supports customizing the input instruction according to different tasks.
> Our evaluation indicates that, for most downstream tasks, using instructions (instruct) typically yields an improvement of 1% to 5% compared to not using them. Therefore, we recommend that developers create tailored instructions specific to their tasks and scenarios. In multilingual contexts, we also advise users to write their instructions in English, as most instructions utilized during the model training process were originally written in English.

## Model Performance

We utilize retrieval task datasets from various subtasks of [MMEB-v2](https://huggingface.co/spaces/TIGER-Lab/MMEB-Leaderboard) and [MMTEB](https://huggingface.co/spaces/mteb/leaderboard) retrieval benchmarks. For visual document retrieval, we employ [JinaVDR](https://huggingface.co/collections/jinaai/jinavdr-visual-document-retrieval) and [ViDoRe v3](https://huggingface.co/blog/QuentinJG/introducing-vidore-v3) datasets. Our results demonstrate that all Qwen3-VL-Reranker models consistently outperform the base embedding model and baseline rerankers, with the 8B variant achieving the best performance across most tasks.

| Model | Size | MMEB-v2(Retrieval) - Avg | MMEB-v2(Retrieval) - Image | MMEB-v2(Retrieval) - Video | MMEB-v2(Retrieval) - VisDoc | MMTEB(Retrieval) | JinaVDR | ViDoRe(v3) |
|-------|------|--------------------------|----------------------------|----------------------------|------------------------------|------------------|---------|------------|
| Qwen3-VL-Embedding-2B | 2B | 73.4 | 74.8 | 53.6 | 79.2 | 68.1 | 71.0 | 52.9 |
| jina-reranker-m0      | 2B |  - | 68.2 | -    | 85.2 | -    | 82.2 | 57.8 |
| Qwen3-VL-Reranker-2B | 2B | 75.1 | 73.8 | 52.1 | 83.4 | 70.0 | 80.9 | 60.8 |
| Qwen3-VL-Reranker-8B | 8B | 79.2 | 80.7 | 55.8 | 86.3 | 74.9 | 83.6 | 66.7 |

## Usage

### Using Sentence Transformers

Install Sentence Transformers:
```bash
pip install sentence_transformers
```

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-VL-Reranker-2B")

query = "A woman playing with her dog on a beach at sunset."
documents = [
    "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.",
    "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
    {
        "text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.",
        "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
    },
]

prompt = "Retrieve images or text relevant to the user's query."
pairs = [(query, doc) for doc in documents]
scores = model.predict(pairs, prompt=prompt)
print(scores)
# [1.8125, 0.5625, 1.3125]

rankings = model.rank(query, documents, prompt=prompt)
print(rankings)
# [{'corpus_id': 0, 'score': 1.8125}, {'corpus_id': 2, 'score': 1.3125}, {'corpus_id': 1, 'score': 0.5625}]
```

You can map scores to 0...1 with a sigmoid activation:

```python
scores = model.predict(pairs, activation_fn=torch.nn.Sigmoid(), prompt=prompt)
print(scores)
# [0.8594, 0.6367, 0.7891]
```

The default prompt is `"query"` with instruction `"Retrieve text relevant to the user's query."`. You can customize the instruction for your use case via the `prompt` parameter as shown above.

### Using Transformers

- **requirements**
```text
transformers>=4.57.0
qwen-vl-utils>=0.0.14
torch==2.8.0
```

```python
from scripts.qwen3_vl_reranker import Qwen3VLReranker

# Specify the model path
model_name_or_path = "Qwen/Qwen3-VL-Reranker-2B"

# Initialize the Qwen3VLEmbedder model
model = Qwen3VLReranker(model_name_or_path=model_name_or_path)
# We recommend enabling flash_attention_2 for better acceleration and memory saving,
# model = Qwen3VLReranker(model_name_or_path=model_name_or_path, torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2")

# Combine queries and documents into a single input list

inputs = {
    "instruction": "Retrieve images or text relevant to the user's query.",
    "query": {"text": "A woman playing with her dog on a beach at sunset."},
    "documents": [
        {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust."},
        {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"},
        {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.", "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"}
    ],
    "fps": 1.0
}

scores = model.process(inputs)
print(scores)
# [0.8613124489784241, 0.6757137179374695, 0.8125371336936951]
```

### Using vLLM
```python
import argparse
import os
from pathlib import Path
from typing import Dict, Any
from vllm import LLM, EngineArgs
from vllm.entrypoints.score_utils import ScoreMultiModalParam


queries = [
    {"text": "A woman playing with her dog on a beach at sunset."}
]

documents = [
    {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust."},
    {"image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"},
    {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.", 
     "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"}
]


def format_document_to_score_param(doc_dict: Dict[str, Any]) -> ScoreMultiModalParam:
    content = []
    
    text = doc_dict.get('text')
    image = doc_dict.get('image')
    
    if text:
        content.append({
            "type": "text",
            "text": text
        })
    
    if image:
        image_url = image
        if isinstance(image, str) and not image.startswith(('http', 'https', 'oss')):
            abs_image_path = os.path.abspath(image)
            image_url = 'file://' + abs_image_path
        
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        })
    
    if not content:
        content.append({
            "type": "text",
            "text": ""
        })
    
    return {"content": content}


def main():
    parser = argparse.ArgumentParser(description="Offline Reranker with vLLM")
    parser.add_argument("--model-path", type=str, default="models/Qwen3-VL-Reranker-2B", help="Path to the reranker model")
    parser.add_argument("--dtype", type=str, default="bfloat16", help="Data type (e.g., bfloat16)")
    parser.add_argument("--template-path", type=str, default="vllm/examples/pooling/score/template/qwen3_vl_reranker.jinja", 
                        help="Path to chat template file")
    args = parser.parse_args()
    
    print(f"Loading model from {args.model_path}...")
    
    engine_args = EngineArgs(
        model=args.model_path,
        runner="pooling",
        dtype=args.dtype,
        trust_remote_code=True,
        hf_overrides={
            "architectures": ["Qwen3VLForSequenceClassification"],
            "classifier_from_token": ["no", "yes"],
            "is_original_qwen3_reranker": True,
        },
    )
    
    llm = LLM(**vars(engine_args))
    
    template_path = Path(args.template_path)
    chat_template = template_path.read_text() if template_path.exists() else None
    
    for query_dict in queries:
        query_text = query_dict.get('text', '')
        print(f"\nQuery: {query_text}")
        
        scores = []
        for doc_dict in documents:
            doc_param = format_document_to_score_param(doc_dict)
            outputs = llm.score(query_text, doc_param, chat_template=chat_template)
            score = outputs[0].outputs.score
            scores.append(score)
        
        print(scores)


if __name__ == "__main__":
    main()

```

For more usage examples, please visit our [GitHub repository](https://github.com/QwenLM/Qwen3-VL-Embedding).

## Citation

If you find our work helpful, feel free to give us a cite.

```
@article{qwen3vlembedding,
  title={Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking},
  author={Li, Mingxin and Zhang, Yanzhao and Long, Dingkun and Chen Keqin and Song, Sibo and Bai, Shuai and Yang, Zhibo and Xie, Pengjun and Yang, An and Liu, Dayiheng and Zhou, Jingren and Lin, Junyang},
  journal={arXiv preprint arXiv:2601.04720},
  year={2026}
}
```