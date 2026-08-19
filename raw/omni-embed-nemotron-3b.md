---
license: other
license_name: customized-nscl-v1
license_link: LICENSE
tags:
  - text
  - image
  - video
  - audio
  - vidore
  - multimodal-embedding
  - Text-to-Video retrieval
  - Text-to-Audio retrieval
  - Visual Document Retrieval
  - feature-extraction
  - sentence-transformers
language:
  - en
library_name: sentence-transformers
pipeline_tag: sentence-similarity
---

# Omni-Embed-Nemotron-3B

## Description

NV-QwenOmni-Embed-3B-v1 is a versatile multimodal embedding model capable of encoding content across multiple modalities, including text, image, audio, and video, either individually or in combination, and supports retrieval using queries that can also be multimodal. It is designed to serve as a foundational component in multi-modal Retrieval-Augmented Generation (RAG) systems.

The foundational Qwen Omni model ([Qwen/Qwen2.5-Omni-3B](https://huggingface.co/Qwen/Qwen2.5-Omni-3B)) is based on the Thinker-Talker architecture. We only leverage the Thinker component to encode and understand diverse modalities. In this implementation, we do not include the Talker component, as the model focuses on multimodal understanding rather than response generation.

This model is for research and development only.

For more technical details, please refer to our technical report: [Omni-Embed-Nemotron: A Unified Multimodal Retrieval Model for Text, Image, Audio, and Video](https://arxiv.org/abs/2510.03458)

### License/Terms of Use

Governing Terms for nvidia/omni-embed-nemotron-3b model: [NVIDIA OneWay Noncommercial License.](https://huggingface.co/nvidia/omni-embed-nemotron-3b/blob/main/LICENSE)

ADDITIONAL INFORMATION: [Qwen RESEARCH LICENSE AGREEMENT](https://huggingface.co/Qwen/Qwen2.5-Omni-3B/blob/main/LICENSE)


This project will download and install additional third-party open source software projects. Review the license terms of these open source projects before use.

### Team
- Mengyao Xu
- Gabriel Moreira
- Radek Osmulski
- Ronay Ak
- Yauhen Babakhin
- Bo Liu
- Even Oldridge
- Benedikt Schifferer

### Citation

```
@article{xu2025omni,
  title={Omni-Embed-Nemotron: A Unified Multimodal Retrieval Model for Text, Image, Audio, and Video},
  author={Xu, Mengyao and Zhou, Wenfei and Babakhin, Yauhen and Moreira, Gabriel and Ak, Ronay and Osmulski, Radek and Liu, Bo and Oldridge, Even and Schifferer, Benedikt},
  journal={arXiv preprint arXiv:2510.03458},
  year={2025}
}
@misc{moreira2025nvretrieverimprovingtextembedding,
      title={NV-Retriever: Improving text embedding models with effective hard-negative mining}, 
      author={Gabriel de Souza P. Moreira and Radek Osmulski and Mengyao Xu and Ronay Ak and Benedikt Schifferer and Even Oldridge},
      year={2025},
      eprint={2407.15831},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2407.15831}, 
}
```

### Deployment Geography
Global

### Use Case
NV-Omni-Embed is intended for researchers and developers building retrieval-based applications that require understanding and retrieve information across multiple modalities. It is particularly useful in multimodal RAG systems, where queries and documents may include combinations of text, images, audio, and videos. Potential applications include multimedia search engines, cross-modal retrieval systems, and conversational AI with rich input understanding.

### Release Date
Huggingface 10/1/2025 via [https://huggingface.co/nvidia/omni-embed-nemotron-3b]

## Model Architecture

- **Architecture Type:** Transformer
- **Network Architecture:** Qwen/Qwen2.5-Omni-3B

NV-QwenOmni-Embed-3B-v1 is a transformer-based multimodal embedding model built on top of the Thinker component from [Qwen/Qwen2.5-Omni-3B](https://huggingface.co/Qwen/Qwen2.5-Omni-3B). Unlike the original Thinker-Talker architecture, this model does not include the Talker module, as it is designed specifically for multimodal understanding and retrieval rather than response generation. Number of model parameters is 4.7B. 

The model incorporates a vision encoder, an audio encoder, and a large language model (LLM) from the Qwen architecture to process diverse modalities. Unlike the Omni model, which interleaves audio and video tokens with TMRoPE, our retrieval encoder keeps the two streams separate. Audio and video are encoded independently, preserving their full temporal structure without interleaving. Our experiments show this design improves retrieval performance. 

NV-QwenOmni-Embed-3B-v1 is trained using a bi-encoder architecture where queries and candidate inputs are embedded independently. A contrastive learning objective is employed to align relevant query-content pairs while pushing apart unrelated ones in the shared embedding space.





## Input

| Property | Query | Document |
|----------|-------|----------|
| **Input Type** | Text \| Image \| Audio \| Video \| Any combination | Text \| Image \| Audio \| Video \| Any combination |
| **Input Format** | List of strings, image tensors, audio arrays, or video clips | List of text strings, images, audio, or video clips |



|  | Text | Image | Video | Audio |
|---|---|---|---|---|
| **Input Parameter**  | str, list[str], or pre-tokenized list[list[str]]; encoded to token IDs; per-sample 1D; batched 2D [batch, seq_len] | PIL.Image, np.ndarray, or torch.Tensor; per-sample 3D; batched 4D | np.ndarray, torch.Tensor, list of frames per-sample 4D; batched 5D; or file (like .mp4) | 1D waveform (np.ndarray or torch.Tensor) per-sample 1D; batched 2D [batch, num_samples], or file |


**Other Properties**: The model's maximum context length is 32768 tokens. 

## Output

- **Output Type:** Floats
- **Output Format:** List of float arrays
- **Output Parameters:** A tensor of floats equivalent to [batchsize x 2048]
- **Other Properties Related to Output:** Model outputs embedding vectors of dimension 2048 for each input.

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA’s hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.

### Usage

#### Using Sentence Transformers

Install Sentence Transformers:
```bash
pip install sentence_transformers
```

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "nvidia/omni-embed-nemotron-3b",
    trust_remote_code=True,
    model_kwargs={"attn_implementation": "flash_attention_2"},
)

# Configure Transformer video/audio processing
model[0].processing_kwargs.update({
    "video": {
        "min_pixels": 32 * 14 * 14,
        "max_pixels": 64 * 28 * 28,
        "do_sample_frames": True,
        "fps": 2,
    },
    "audio": {"max_length": 2048000},
})

# In this example we're using text queries and text+video+audio documents, but other combinations are also supported
queries = ["Drawing of a cat", "Drawing of a guitar", "Man walking down the street"]
# One document: text + video + audio (a video of someone drawing a guitar)
documents = [
    {
        "text": "This is a passage to be embedded",
        "video": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2.5-Omni/draw.mp4",
        "audio": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2.5-Omni/draw.mp4",
    },
]

query_embeddings = model.encode_query(queries)
document_embeddings = model.encode_document(documents)
print(query_embeddings.shape, document_embeddings.shape)
# (3, 2048) (1, 2048)

similarities = model.similarity(query_embeddings, document_embeddings)
print(similarities)
# tensor([[0.3532],
#         [0.5502],
#         [0.2215]])
```

> **Note:** The model supports text, image, audio, and video inputs. For larger non-text inputs (e.g. long videos), you may need to adjust `model[0].processing_kwargs` to control resolution and frame sampling.

#### Using Transformers

The model requires transformers version 4.51.3
```
pip install git+https://github.com/huggingface/transformers.git@v4.51.3-Qwen2.5-Omni-preview
```

```
import torch
from qwen_omni_utils import process_mm_info
import torch.nn.functional as F
from transformers import AutoModel, AutoProcessor

model_name_or_path = "nvidia/omni-embed-nemotron-3b"
model = AutoModel.from_pretrained(
    model_name_or_path, 
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    trust_remote_code=True,
)

model = model.to("cuda:0")
model.eval()

documents = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "passage: This is a passage to be embedded"
            },
            {
                "type": "video",
                "video": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2.5-Omni/draw.mp4"
            },
            {
                "type": "audio",
                "audio": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2.5-Omni/draw.mp4"
            }
        ]
    },
]

processor = AutoProcessor.from_pretrained(model_name_or_path, trust_remote_code=True)
documents_texts = processor.apply_chat_template(documents, add_generation_prompt=False, tokenize=False)
audio, images, videos = process_mm_info(documents, use_audio_in_video=False)

videos_kwargs = {
    "min_pixels": 32*14*14,
    "max_pixels": 64*28*28,
    "use_audio_in_video": False,
}
text_kwargs = {
    "truncation": True,
    "padding": True,
    "max_length": 204800,
}
batch_dict = processor(
    text=documents_texts, 
    images=images, 
    videos=videos, 
    audio=audio,
    return_tensors="pt",
    text_kwargs=text_kwargs,
    videos_kwargs=videos_kwargs,
    audio_kwargs={"max_length": 2048000},
)

batch_dict = {k: v.to(model.device) for k, v in batch_dict.items()}
last_hidden_states = model(**batch_dict, output_hidden_states=True).hidden_states[-1]
# Average Pooling
attention_mask = batch_dict["attention_mask"]
last_hidden_states_masked = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
embedding = last_hidden_states_masked.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
embedding = F.normalize(embedding, dim=-1)
print(embedding)
print(embedding.shape)
```


## Software Integration: <br>

Runtime Engine(s): TensorRT, Triton
Supported Hardware Microarchitecture Compatibility: A100 40GB, A100 80GB, H100 80GB
Supported Operating System(s): Linux

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment.

## Model Version(s)
- **Nvidia Omni Embed Nemotron 3B**
- **Short name:** omni-embed-nemotron-3b-v1

# Training and Evaluation Datasets

## Training Dataset

**Data Modality**:
Image
Text

**Image Training Data Size**: 1 Million to 1 Billion Images

**Text Training Data Size**: Less than a Billion Tokens


The model was trained on publicly available datasets, including[HotpotQA](https://huggingface.co/datasets/hotpotqa/hotpot_qa), [MIRACL](https://huggingface.co/datasets/SEACrowd/miracl), [Natural Questions (NQ)](https://huggingface.co/datasets/irds/natural-questions), [Stack Exchange](https://huggingface.co/datasets/HuggingFaceH4/stack-exchange-preferences), [SQuAD](https://huggingface.co/datasets/squad), [Tiger Math/Stack](https://huggingface.co/datasets/TIGER-Lab/WebInstructSub), [DocMatix-IR](https://huggingface.co/datasets/Tevatron/docmatix-ir), [Vidore-ColPali-Training](https://huggingface.co/datasets/vidore/colpali_train_set), and [Wiki-SS-NQ](https://huggingface.co/datasets/Tevatron/wiki-ss-nq).

- **Data Collection Method by dataset:** Hybrid: Automated, Human, Synthetic
- **Labeling Method by dataset:** Hybrid: Automated, Human, Synthetic
- **Properties:** 1M samples from public datasets.

## Evaluation Dataset
We evaluate our model on multiple benchmarks covering different modalities. For text retrieval, we select some text retrieval datasets from [MTEB](https://huggingface.co/spaces/mteb/leaderboard). For image retrieval, evaluation is conducted on the public ViDoRe V1 dataset. Since no established video retrieval benchmarks exist, we construct two custom evaluation sets based on the LPM dataset and FineVideo. To provide fair comparison with the state-of-the-art text-only baselines, we use the speech-to-text transcripts released with FineVideo and the transcripts from LPM as the input corpus for standard text retrieval models.

- **Data Collection Method by dataset:** Hybrid: Automated, Human, Synthetic
- **Labeling Method by dataset:** Hybrid: Automated, Human, Synthetic
- **Properties:** More details on ViDoRe V1 can be found on their leaderboard: [Visual Document Retrieval Benchmark](https://huggingface.co/vidore).

### Model performance comparison on Video retrieval datasets (LPM and FineVideo) using NDCG@10 and NDCG@5 metrics:

| Model | NDCG@10 LPM | NDCG@10 FineVideo | NDCG@10 Avg | NDCG@5 LPM | NDCG@5 FineVideo | NDCG@5 Avg |
|---|---|---|---|---|---|---|
| Qwen/Qwen3-Embedding-4B | 0.8634 | 0.5405 | 0.7020 | 0.8518 | 0.5264 | 0.6891 |
| intfloat/multilingual-e5-large-instruct | 0.7952 | 0.4456 | 0.6204 | 0.7759 | 0.4300 | 0.6030 |
| stella\_en\_1.5B\_v5 | 0.8522 | 0.5359 | 0.6941 | 0.8404 | 0.5206 | 0.6805 |
| nvidia/omni-embed-nemotron-3b | 0.8465 | 0.5662 | **0.7064** | 0.8355 | 0.5486 | **0.6921** |

Multimodal retrieval performance across input modalities on LPM and FineVideo using NDCG@10. Baselines support text only; multimodal settings apply to Omni.

### LPM performance (NDCG@10) modalities breakdown

| Model | Text (Transcript+OCR) | Audio-Only | Video-Only | Audio+Video Fusion | Audio+Video Separately |
|---|---|---|---|---|---|
| Qwen/Qwen3-Embedding-4B | 0.8634 | N/A | N/A | N/A | N/A |
| intfloat/multilingual-e5-large-instruct | 0.7952 | N/A | N/A | N/A | N/A |
| stella\_en\_1.5B\_v5 | 0.8522 | N/A | N/A | N/A | N/A |
| nvidia/omni-embed-nemotron-3b | 0.8636 | 0.8238 | 0.7365 | 0.8373 | 0.8465 |

### FineVideo performance (NDCG@10) modalities breakdown

| Model | Text (Transcript) | Audio-Only | Video-Only | Audio+Video Fusion | Audio+Video Separately |
|---|---|---|---|---|---|
| Qwen/Qwen3-Embedding-4B | 0.5405 | N/A | N/A | N/A | N/A |
| intfloat/multilingual-e5-large-instruct | 0.4456 | N/A | N/A | N/A | N/A |
| stella\_en\_1.5B\_v5 | 0.5359 | N/A | N/A | N/A | N/A |
| nvidia/omni-embed-nemotron-3b | 0.6082 | 0.5407 | 0.4488 | 0.4700 | 0.5662 |

### Evaluation of embedding models across text retrieval benchmarks. Results are reported using nDCG@10.
| Model | Avg. | NQ | FiQA-2018 | SciFact | SCIDOCS | ArguAna | NFCorpus | Quora | LegalBench-CorpLobby | CQAdupGaming | CQAdupUnix |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen/Qwen3-Embedding-4B | 0.6654 | 0.6313 | 0.6122 | 0.7833 | 0.3144 | 0.7564 | 0.4110 | 0.8806 | 0.9542 | 0.7151 | 0.5960 |
| intfloat/multilingual-e5-large-instruct | 0.5900 | 0.6350 | 0.4865 | 0.7162 | 0.1924 | 0.5848 | 0.3634 | 0.8926 | 0.9425 | 0.6396 | 0.4473 |
| stella\_en\_1.5B\_v5 | 0.6050 | 0.7180 | 0.5996 | 0.8009 | 0.2677 | 0.5706 | 0.4200 | 0.9003 | 0.9468 | 0.5359 | 0.2903 |
| nvidia/omni-embed-nemotron-3b | 0.6059 | 0.6808 | 0.5382 | 0.7405 | 0.2163 | 0.5891 | 0.3644 | 0.8347 | 0.9413 | 0.6432 | 0.5102 |

### Evaluation of baseline models and our models on [ViDoRe V1](https://huggingface.co/spaces/vidore/vidore-leaderboard}{) (as of September 30th). Results are presented using nDCG@5 metrics.

| Model | Size (M) | Avg. | ArxivQA | DocVQA | InfoVQA | Shift Project | AI | Energy | Gov. Reports | Healthcare | TabFQuad | TAT-DQA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nvidia/llama-nemoretriever-colembed-1b-v1 | 2418 | 90.5 | 87.6 | 64.5 | 93.6 | 92.3 | 100 | 96.6 | 96.7 | 99.6 | 94.3 | 79.8 |
| nvidia/llama-nemoretriever-colembed-3b-v1 | 4407 | 91.0 | 88.4 | 66.2 | 94.9 | 90.7 | 99.6 | 96.6 | 97.8 | 99.3 | 95.9 | 80.6 |
| nomic-ai/colnomic-embed-multimodal-3b | 3000 | 89.9 | 88.2 | 61.3 | 92.8 | 90.2 | 96.3 | 97.3 | 96.6 | 98.3 | 94.5 | 83.1 |
| vidore/colqwen2.5-v0.2 | 3000 | 89.6 | 89.1 | 63.5 | 92.6 | 88.0 | 99.6 | 95.8 | 96.6 | 98.0 | 90.8 | 82.1 |
| vidore/colqwen2-v1.0 | 2210 | 89.2 | 88.0 | 61.5 | 92.5 | 89.9 | 99.0 | 95.9 | 95.5 | 98.8 | 89.0 | 82.2 |
| vidore/colpali-v1.3 | 2920 | 84.7 | 83.7 | 58.7 | 85.7 | 76.5 | 96.6 | 94.6 | 95.9 | 97.4 | 86.7 | 70.7 |
| vidore/colpali-v1.2 | 2920 | 83.4 | 77.9 | 56.5 | 82.4 | 78.3 | 97.5 | 94.4 | 94.9 | 95.4 | 88.4 | 68.1 |
| nvidia/omni-embed-nemotron-3b | 4703 | 85.7 | 85.3 | 59.2 | 89.2 | 78.6 | 98.1 | 93.5 | 95.4 | 95.8 | 91.0 | 69.7 |






## Inference:
**Acceleration Engine:** Not Applicable <br>
**Test Hardware:** A100 40GB, A100 80GB, H100 80GB

## Ethical Considerations
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://app.intigriti.com/programs/nvidia/nvidiavdp/detail).  

## Bias

| Field | Response |
| ----- | ----- |
| Participation considerations from adversely impacted groups [protected classes](https://www.senate.ca.gov/content/protected-classes) in model design and testing | None |
| Measures taken to mitigate against unwanted bias | None |

## Explainability

| Field | Response |
| ----- | ----- |
| Intended Application & Domain: | Multi-modality corpus and query embedding for question and answer retrieval. |
| Model Type: | Transformer encoder. |
| Intended User: | Creators of generative AI focused on conversational models, as well as users aiming to develop question-and-answer applications, can benefit from leveraging the dense retrieval technologies. These applications can efficiently handle large, multi-modal corpora, including images, text, videos, and audio. |
| Output: | Array of float numbers (Dense vector for input content, which may include multi-modal corpora). |
| Describe how the model works: | Model transforms the input into a dense vector representation. |
| Performance Metrics: | Accuracy |
| Potential Known Risks: | This model does not guarantee to always retrieve the correct corpus for a given query. |
| Licensing & Terms of Use: | **Governing Terms:**<br>Your use of the software container and model is governed by the [NVIDIA Software and Model Evaluation License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-and-model-evaluation-license/)<br><br>**Additional Information:**<br>[Qwen RESEARCH LICENSE AGREEMENT](https://huggingface.co/Qwen/Qwen2.5-Omni-3B/blob/main/LICENSE)  |
| Technical Limitations: | The model's max sequence length is 32768. Longer sequence inputs should be truncated. |
| Name the adversely impacted groups this has been tested to deliver comparable outcomes regardless of: | N/A |
| Verified to have met prescribed NVIDIA quality standards: | Yes |

## Privacy

| Field | Response |
| ----- | ----- |
| Generatable or reverse engineerable personal data? | None |
| Personal data used to create this model? | None |
| How often is dataset reviewed? | Dataset is initially reviewed upon addition, and subsequent reviews are conducted as needed or upon request for changes. |
| Is there provenance for all datasets used in training? | Yes |
| Does data labeling (annotation, metadata) comply with privacy laws? | Yes |
| Is data compliant with data subject requests for data correction or removal, if such a request was made? | No, not possible with externally-sourced data. |
| Applicable Privacy Policy | https://www.nvidia.com/en-us/about-nvidia/privacy-policy/ |

## Safety And Security

| Field | Response |
| ----- | ----- |
| Model Application(s): | Multi-modal Corpus Embedding for Retrieval. The model processes input from various modalities—text, image, audio, and video—either independently or in combination. |
| Use Case Restrictions: | Governing Terms:Your use of the model is governed by the [NVIDIA Open License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/). Additional Information: [Qwen RESEARCH LICENSE AGREEMENT](https://huggingface.co/Qwen/Qwen2.5-Omni-3B/blob/main/LICENSE).   |
| Model and dataset restrictions: | The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development. Restrictions enforce dataset access during training, and dataset license constraints adhered to. |
| Describe the life critical impact (if present) | Not applicable |
