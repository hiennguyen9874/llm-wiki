---
language:
- multilingual
base_model:
- google/t5gemma-2-4b-4b
pipeline_tag: text-ranking
datasets:
- KaLM-Embedding/KaLM-reranker-training-data
- KaLM-Embedding/KaLM-embedding-finetuning-data
- Shitao/bge-m3-data
tags:
- sentence-transformers
- transformers
- reranker
- encoder-decoder
- FBNL
- matryoshka
- multilingual
- retrieval
- RAG
license: apache-2.0
library_name: sentence-transformers
---


<h1 align="center">KaLM-Reranker-V1: Fast but Not Late Interaction for Compressed Document Reranking</h1>

<p align="center">
  <a href="https://replicate.com/itsukifujii/kalm-reranker-v1-large-r2">
    <img src="https://img.shields.io/badge/Replicate-Playground-000000.svg?logo=replicate&amp;logoColor=white" alt="Try on Replicate">
  </a>
  <a href="https://huggingface.co/collections/KaLM-Embedding/lychee-kalm-reranker-and-jev">
    <img src="https://img.shields.io/badge/%F0%9F%A4%97_Collection-KaLM--Reranker-ffbd45.svg" alt="Hugging Face Collection">
  </a>
  <a href="https://arxiv.org/abs/2606.22807">
    <img src="https://img.shields.io/badge/arXiv-2606.22807-b31b1b.svg" alt="Paper">
  </a>
  <a href="https://github.com/KaLM-Embedding">
    <img src="https://img.shields.io/badge/GitHub-KaLM--Embedding-blue.svg?logo=github" alt="GitHub">
  </a>
  <a href="https://www.apache.org/licenses/LICENSE-2.0">
    <img src="https://img.shields.io/badge/License-Apache--2.0-green.svg" alt="License">
  </a>
</p>


## What is KaLM-Reranker-V1-R2?

**KaLM-Reranker-V1-R2 is a substantially improved checkpoint release of KaLM-Reranker-V1.** It keeps the same fast-but-not-late-interaction (FBNL) architecture and inference interface as the original release, while introducing a stronger multi-stage training recipe for three practical goals:

1. **Stronger compression robustness.** R2 supports Matryoshka embedding pooling (MEP) from **1x to 128x**, extending the maximum validated compression ratio from 32x to 128x. Even at 128x compression, all three model sizes retain at least 92% of their average nDCG@10 at 2x compression on both BEIR and MIRACL.
2. **Adjustable test-time compute scaling.** A single KaLM-Reranker-V1-R2 checkpoint can trade compute for quality by changing the compression ratio. It can also use a coarse-to-fine cascade: cheaply screen all candidates with heavily compressed document representations, then spend more compute only on the most promising candidates.
3. **Better multi-domain and multilingual ranking.** At the default 4x compression ratio, every R2 model improves on BEIR, while MIRACL average nDCG@10 increases by **+9.03**, **+7.17**, and **+4.85** points for Nano, Small, and Large, respectively.

![kalm-reranker-v1-r2 architecture](./assets/framework.jpg)

| Capability | KaLM-Reranker-V1 | KaLM-Reranker-V1-R2 |
|:--|:--|:--|
| Validated MEP range | 1x-32x | **1x-128x** |
| Test-time compute |  Flexible compression | **Flexible allocation of inference-time computation** |
| Training | Supervised checkpoints | **High-quality SFT -> soft-label distillation -> model soup** |
| Multi-domain ranking | Strong | **Improved on BEIR for all three sizes** |
| Multilingual ranking | Limited | **Substantially improved across MIRACL's 18 languages** |

### R2 Training Checkpoints (Stages 1–3)

We release the checkpoints from the three-stage training pipeline described in the third version of our paper. Stage 1 uses supervised fine-tuning; Stage 2 produces two checkpoints through soft-label distillation; and Stage 3 combines them through model soup to produce the final R2 models. 

| Stage | Checkpoint | Nano | Small | Large |
| :--- | :--- | :--- | :--- | :--- |
| Stage 1 | Supervised fine-tuning | [KaLM-Reranker-V1-Nano-R2-Stage1](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Nano-R2-Stage1) | [KaLM-Reranker-V1-Small-R2-Stage1](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Small-R2-Stage1) | [KaLM-Reranker-V1-Large-R2-Stage1](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Large-R2-Stage1) |
| Stage 2 | Distillation (`r64-a32`) | [KaLM-Reranker-V1-Nano-R2-Stage2-r64-a32](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Nano-R2-Stage2-r64-a32) | [KaLM-Reranker-V1-Small-R2-Stage2-r64-a32](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Small-R2-Stage2-r64-a32) | [KaLM-Reranker-V1-Large-R2-Stage2-r64-a32](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Large-R2-Stage2-r64-a32) |
| Stage 2 | Distillation (`r96-a48`) | [KaLM-Reranker-V1-Nano-R2-Stage2-r96-a48](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Nano-R2-Stage2-r96-a48) | [KaLM-Reranker-V1-Small-R2-Stage2-r96-a48](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Small-R2-Stage2-r96-a48) | [KaLM-Reranker-V1-Large-R2-Stage2-r96-a48](https://huggingface.co/Yuki131/KaLM-Reranker-V1-Large-R2-Stage2-r96-a48) |
| Stage 3 | Final R2 model | [KaLM-Reranker-V1-Nano-R2](https://huggingface.co/KaLM-Embedding/KaLM-Reranker-V1-Nano-R2) | [KaLM-Reranker-V1-Small-R2](https://huggingface.co/KaLM-Embedding/KaLM-Reranker-V1-Small-R2) | [KaLM-Reranker-V1-Large-R2](https://huggingface.co/KaLM-Embedding/KaLM-Reranker-V1-Large-R2) |

### KaLM-Reranker-V1-R2 vs. the original KaLM-Reranker-V1
All results below use the same default compression ratio, `r=4`. KaLM-Reranker-V1 results are taken from the previous model cards; KaLM-Reranker-V1-R2 results are from the updated paper.

#### BEIR — Multi-domain Reranking

| Model | KaLM-Reranker-V1 | KaLM-Reranker-V1-R2 | Delta |
|:--|--:|--:|--:|
| Nano | 57.41 | **58.54** | **+1.13** |
| Small | 60.01 | **61.07** | **+1.06** |
| Large | 62.87 | **63.53** | **+0.66** |

#### MIRACL — Multilingual Reranking

| Model | KaLM-Reranker-V1 | KaLM-Reranker-V1-R2 | Delta |
|:--|--:|--:|--:|
| Nano | 62.08 | **71.11** | **+9.03** |
| Small | 66.89 | **74.06** | **+7.17** |
| Large | 70.07 | **74.92** | **+4.85** |

#### BEIR — Compression Robustness

| Model | 2x | 4x | 8x | 16x | 32x | 64x | 128x |
|:--|--:|--:|--:|--:|--:|--:|--:|
| KaLM-Reranker-V1-Nano | 57.69 | 57.41 | 56.46 | 55.19 | 52.88 | — | — |
| **KaLM-Reranker-V1-Nano-R2** | **58.75** | **58.54** | **58.17** | **57.47** | **56.74** | **55.88** | **55.11** |
| **Delta** | **+1.06** | **+1.13** | **+1.71** | **+2.28** | **+3.86** | — | — |
| KaLM-Reranker-V1-Small | 60.32 | 60.01 | 59.38 | 58.18 | 55.98 | — | — |
| **KaLM-Reranker-V1-Small-R2** | **61.17** | **61.07** | **60.74** | **60.25** | **59.54** | **58.84** | **58.20** |
| **Delta** | **+0.85** | **+1.06** | **+1.36** | **+2.07** | **+3.56** | — | — |
| KaLM-Reranker-V1-Large | 63.14 | 62.87 | 62.46 | 61.74 | 60.33 | — | — |
| **KaLM-Reranker-V1-Large-R2** | **63.69** | **63.53** | **63.15** | **62.70** | **62.18** | **61.60** | **61.23** |
| **Delta** | **+0.55** | **+0.66** | **+0.69** | **+0.96** | **+1.85** | — | — |

#### MIRACL — Compression Robustness

| Model | 2x | 4x | 8x | 16x | 32x | 64x | 128x |
|:--|--:|--:|--:|--:|--:|--:|--:|
| KaLM-Reranker-V1-Nano | 63.07 | 62.08 | 60.05 | 57.01 | 52.21 | — | — |
| **KaLM-Reranker-V1-Nano-R2** | **71.63** | **71.11** | **70.38** | **69.38** | **68.02** | **66.85** | **66.01** |
| **Delta** | **+8.56** | **+9.03** | **+10.33** | **+12.37** | **+15.81** | — | — |
| KaLM-Reranker-V1-Small | 67.28 | 66.89 | 65.36 | 62.96 | 59.07 | — | — |
| **KaLM-Reranker-V1-Small-R2** | **74.34** | **74.06** | **73.61** | **72.60** | **71.81** | **70.82** | **70.16** |
| **Delta** | **+7.06** | **+7.17** | **+8.25** | **+9.64** | **+12.74** | — | — |
| KaLM-Reranker-V1-Large | 70.30 | 70.07 | 69.63 | 68.25 | 65.94 | — | — |
| **KaLM-Reranker-V1-Large-R2** | **75.12** | **74.92** | **74.50** | **73.85** | **73.26** | **72.46** | **71.97** |
| **Delta** | **+4.82** | **+4.85** | **+4.87** | **+5.60** | **+7.32** | — | — |

KaLM-Reranker-V1-R2 consistently outperforms KaLM-Reranker-V1 at every shared compression ratio. The gains increase as compression becomes more aggressive, demonstrating substantially improved compression robustness.



### Model family

The reported sizes are **activated parameters**. Nano, Small, and Large are initialized from the T5Gemma2 270M-270M, 1B-1B, and 4B-4B encoder-decoder families, respectively.

| Models                                                                                       | Activated Params. | Non-Embedding Params. | Embedding Params. | #Layers (encoder + decoder) | Sequence Length | Document Token Dim. | MEP Support | Instruction Aware | Test-Time Compute |
| -------------------------------------------------------------------------------------------------  | -----------------: | --------------------: | ----------------: | --------------------------: | --------------: | ------------------: | ----------: | ----------------: | ----------------: |
| [KaLM-Reranker-V1-Nano-R2](https://huggingface.co/KaLM-Embedding/KaLM-Reranker-V1-Nano-R2)   | 0.27B              | 100M                  | 168M              | 18+18                       | 128K            | 640                 | 1x-128x     | Yes               | Yes               |
| [KaLM-Reranker-V1-Small-R2](https://huggingface.co/KaLM-Embedding/KaLM-Reranker-V1-Small-R2) | 1B                 | 698M                  | 302M              | 26+26                       | 128K            | 1152                | 1x-128x     | Yes               | Yes               |
| [KaLM-Reranker-V1-Large-R2](https://huggingface.co/KaLM-Embedding/KaLM-Reranker-V1-Large-R2) | 4B                 | 3209M                 | 675M              | 34+34                       | 128K            | 2560                | 1x-128x     | Yes               | Yes               |



### Prompt Template
```python
 f"<Document>: {document}"

```
```python
(
    f"<bos><start_of_turn>user\n"
    f"Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".\n\n"
    f"<Instruct>: {task_instruction}\n"
    f"<Query>: {query}<end_of_turn>\n"
    f"<start_of_turn>model\n\n\n\n"
)

```

![kalm-reranker-v1-r2 template](./assets/template.jpg)


### Evaluation
#### BEIR

The KaLM-Reranker-V1 series matches or outperforms strong industrial rerankers from the Qwen, BGE, Jina, and Mxbai families.
![beir](./assets/beir.jpg)

#### MIRACL
KaLM-Reranker-V1 achieves competitive performance on MIRACL. Within its parameter group, KaLM-Reranker-V1-Large ranks first in 11 of the 18 languages (i.e., ar, bn, de, en, es, fi, fr, ja,
ko, ru, and sw); six of these languages (i.e., en, es, de, ja, fr, and ru) have reported website usage rates totaling approximately 74.2% among websites with known content languages ([W3Techs, 2026](https://w3techs.com/technologies/overview/content_language)).
![miracl](./assets/miracl.jpg)

#### LMEB
On LMEB-Dialogue, a compact embedding model paired with our Nano reranker, which has only 0.27B activated parameters, remains competitive with 7–12B embedding models.
![lmeb](./assets/lmeb.jpg)
![lmeb_emb](./assets/lmeb_emb.jpg)

#### Ablation on multi-stage training

Across all three model sizes and all seven compression ratios, performance on BEIR and MIRACL improves consistently from Stage 1 to Stage 3, demonstrating the effectiveness of our multi-stage training pipeline. Concretely, Stage 1 establishes a robust foundation for document reranking, distillation in Stage 2 substantially improves performance, and Stage 3 yields further modest gains. More importantly, robustness to compression generally improves across the three training stages. For example, from Stage 1 to Stage 3, the performance retention of KaLM-Reranker-V1-Nano at r = 128 relative to r = 2 increases from 92.88% to 93.80% on BEIR and from 90.93% to 92.15% on MIRACL.

![lmeb_emb](./assets/ablation.jpg)

![kalm-reranker-v1-r2 training](./assets/training.jpg)

#### Potential of test-time compute scaling 
Results show that this multi-stage strategy largely preserves reranking effectiveness while reducing the estimated online
computation cost by a factor of several. For example, on BEIR, KaLM-Reranker-V1-Small
achieves an average nDCG@10 of 61.11 under setting (c), compared with 61.17 under setting (a),
while reducing the estimated relative serving cost from 8.65x to 2.75x. Interestingly, settings (c)
and (d) outperform setting (a) on some tasks, suggesting that reranking more candidates at a low
compression ratio does not necessarily improve reranking quality.

![test-time-compute](./assets/test-time-compute.jpg)

### Using Sentence Transformers

KaLM-Reranker-V1-Large-R2 can be loaded as a modular Sentence Transformers
`CrossEncoder`. This integration requires `sentence-transformers>=5.6,<6`,
`transformers>=5.3,<6`, and the PyTorch backend. The repository contains custom
modeling code, so load only trusted revisions and pass `trust_remote_code=True`.

```bash
pip install "sentence-transformers>=5.6,<6" "transformers>=5.3,<6"
```

```python
import torch
from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "KaLM-Embedding/KaLM-Reranker-V1-Large-R2",
    trust_remote_code=True,
    device="cuda",
    model_kwargs={"dtype": torch.bfloat16, "chunk_size": 4},
)

query = "What is the capital of China?"
documents = [
    "The capital of China is Beijing.",
    "Gravity attracts bodies toward one another.",
]
pairs = [(query, document) for document in documents]

# The default output is P(yes).
scores = model.predict(pairs)
rankings = model.rank(query, documents, return_documents=True)

# CrossEncoder prompts are interpreted as KaLM task instructions.
instruction = "Given a web search query, retrieve passages that answer the query."
custom_scores = model.predict(pairs, prompt=instruction)
custom_rankings = model.rank(query, documents, prompt=instruction)

# Use Identity to return yes_logit - no_logit instead of P(yes).
margins = model.predict(pairs, activation_fn=torch.nn.Identity())

print(f"scores: {scores}")
print(f"rankings: {rankings}")
print(f"custom_scores: {custom_scores}")
print(f"custom_rankings: {custom_rankings}")
print(f"margins: {margins}")

'''
scores: [9.8677725e-01 9.0574264e-05]
rankings: [{'corpus_id': 0, 'score': 0.98677725, 'text': 'The capital of China is Beijing.'}, {'corpus_id': 1, 'score': 9.057426e-05, 'text': 'Gravity attracts bodies toward one another.'}]
custom_scores: [9.7241479e-01 3.2129523e-05]
custom_rankings: [{'corpus_id': 0, 'score': 0.9724148}, {'corpus_id': 1, 'score': 3.2129523e-05}]
margins: [ 4.3125  -9.30925]
'''

```

Inputs must be ordered as `(query, document)`. By default, queries are
truncated to 512 tokens and documents to 1024 tokens. `chunk_size=4` performs a
mask-aware mean over each consecutive group of four encoder token states before
passing the compressed encoder output to the decoder. Set `chunk_size=None` to
disable compression, or change `model[0].chunk_size` after loading.

For CPU inference, use `device="cpu"` and
`model_kwargs={"dtype": torch.float32, "chunk_size": 4}`. Only the PyTorch
inference backend is currently supported; training, ONNX, and OpenVINO are not
included in this release.


### Using transformers
```python
import argparse
from typing import Optional


def optional_positive_int(value: str) -> Optional[int]:
    if value.lower() == "none":
        return None
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "must be a positive integer or 'none'"
        ) from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer or 'none'")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--model",
        default="KaLM-Embedding/KaLM-Reranker-V1-Large-R2",
        help="Hugging Face model ID or local checkpoint path.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Inference device, such as 'cuda', 'cuda:0', or 'cpu'.",
    )
    parser.add_argument(
        "--dtype",
        default=None,
        choices=("bfloat16", "bf16", "float16", "fp16", "float32", "fp32"),
        help="Model parameter dtype. By default, use BF16 on CUDA and FP32 on CPU.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Number of query-document pairs scored per inference batch.",
    )
    parser.add_argument(
        "--query-max-length",
        type=int,
        default=512,
        help=(
            "Maximum tokens in the raw query before it is inserted into the "
            "decoder prompt; prompt tokens are not included in this limit."
        ),
    )
    parser.add_argument(
        "--reranker-max-length",
        type=int,
        default=1024,
        help=(
            "Maximum encoder tokens for '<Document>: {passage}'. This is not a "
            "combined query-document context limit."
        ),
    )
    parser.add_argument(
        "--chunk-size",
        type=optional_positive_int,
        default=4,
        metavar="N|none",
        help=(
            "Number of encoder token hidden states per mean-pooled chunk; use "
            "'none' to disable encoder chunk pooling."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    from kalm_reranker import KaLMReranker

    reranker = KaLMReranker(
        args.model,
        device=args.device,
        dtype=args.dtype,
        batch_size=args.batch_size,
        query_max_length=args.query_max_length,
        max_length=args.reranker_max_length,
        chunk_size=args.chunk_size,
    )
    query = "What is the capital of China?"
    documents = [
        "The capital of China is Beijing.",
        "Gravity attracts bodies toward one another.",
    ]
    instruction = "Given a query, retrieve documents that answer the query."

    pairs = [(query, document) for document in documents]
    print("scores:", reranker.predict(pairs, instruction=instruction))
    print("rankings:", reranker.rank(query, documents, instruction=instruction))
    

if __name__ == "__main__":
    main()

'''
scores: [0.9867772459983826, 9.0574256319087e-05]
rankings: [{'corpus_id': 0, 'score': 0.9867772459983826}, {'corpus_id': 1, 'score': 9.0574256319087e-05}]
'''

```

### Using vLLM
An experimental single-GPU adapter is available for offline
`LLM.classify()` reranking and optional FastAPI serving. It reuses the original
checkpoint without adding or modifying model weights.

The adapter has been validated with Python 3.12, vLLM 0.19.1, Transformers
5.6.2 and CUDA BF16:

```bash
conda create -n kalm-vllm python=3.12 -y
conda activate kalm-vllm
pip install "vllm==0.19.1" "transformers==5.6.2"

hf download KaLM-Embedding/KaLM-Reranker-V1-Large-R2 \
  --local-dir ./KaLM-Reranker-V1-Large-R2
pip install ./KaLM-Reranker-V1-Large-R2/vllm_support --no-deps
export VLLM_PLUGINS=kalm_t5gemma2
```

If you modify the `vllm_support` source code for some reason 
(e.g. changing the model path in `vllm_support/src/kalm_t5gemma2_vllm_plugin/constants.py`), 
please run `pip install ./KaLM-Reranker-V1-Large-R2/vllm_support --no-deps --force-reinstall` to refresh the patch.

Offline Python:

```python
from kalm_t5gemma2_vllm_plugin import KaLMVLLMReranker

query = "What is the capital of China?"
documents = [
    "The capital of China is Beijing.",
    "Gravity attracts bodies toward one another.",
]

with KaLMVLLMReranker(
    "KaLM-Embedding/KaLM-Reranker-V1-Large-R2",
    query_max_length=512,
    document_max_length=1024,
    encoder_chunk_size=4,
) as reranker:
    print(reranker.rank(query, documents))
```

Offline CLI:

```bash
kalm-vllm-rerank --return-margin
```

To deploy the online service, install the HTTP dependencies and keep the
server running in the first terminal:

```bash
pip install "fastapi>=0.136,<0.137" "uvicorn>=0.46,<0.47"
export CUDA_VISIBLE_DEVICES=0
export VLLM_PLUGINS=kalm_t5gemma2

kalm-vllm-serve \
  --host 0.0.0.0 \
  --port 8000 \
  --model KaLM-Embedding/KaLM-Reranker-V1-Large-R2 \
  --query-max-length 512 \
  --document-max-length 1024 \
  --encoder-chunk-size 4 \
  --max-model-len 2048
```

In a second terminal, check the server:

```bash
conda activate kalm-vllm
kalm-vllm-client --base-url http://127.0.0.1:8000 --health
```

Use `/rerank` for one query and a list of documents. Results are sorted by
score:

```bash
kalm-vllm-client \
  --base-url http://127.0.0.1:8000 \
  --endpoint rerank \
  --json-file ./KaLM-Reranker-V1-Large-R2/vllm_support/examples/rerank_request.json \
  --return-margin \
  --top-k 10
```

Use `/score` to score a batch of independent query-document pairs. Results
preserve the input order and optional IDs:

```bash
kalm-vllm-client \
  --base-url http://127.0.0.1:8000 \
  --endpoint score \
  --json-file ./KaLM-Reranker-V1-Large-R2/vllm_support/examples/score_request.json \
  --return-margin
```

The default output is `P(yes)`. Set `return_margin=true` to also receive
`yes_logit - no_logit`; the client flag `--return-margin` applies the same
setting to a JSON file request. The supported encoder chunk sizes are
`1, 2, 4, 8, 16, 32`, with `4` as the default.

This adapter uses vLLM's plugin, scheduling and pooling interfaces while the
T5Gemma2 semantic forward still runs through Transformers. It is not vLLM's
native HTTP `/score` implementation or a complete vLLM-native kernel port.
See [the complete installation, API and troubleshooting guide](./vllm_support/README.md).


### Acknowledgements
We sincerely thank `jina-reranker-v3` and `Qwen3-Reranker` for their valuable inspiration and contributions to the reranking community, from which we have learned a lot.

### Citation
If you find this model useful, please consider citing our papers.
```
@misc{zhao2026kalmrerankerv1,
      title={KaLM-Reranker-V1: Fast but Not Late Interaction for Compressed Document Reranking}, 
      author={Xinping Zhao and Jiaxin Xu and Ziqi Dai and Xin Zhang and Shouzheng Huang and Danyu Tang and Xinshuo Hu and Meishan Zhang and Baotian Hu and Min Zhang},
      year={2026},
      eprint={2606.22807},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2606.22807}, 
}

@misc{zhao2026kalmembeddingv2,
      title={KaLM-Embedding-V2: Superior Training Techniques and Data Inspire A Versatile Embedding Model}, 
      author={Xinping Zhao and Xinshuo Hu and Zifei Shan and Shouzheng Huang and Yao Zhou and Xin Zhang and Zetian Sun and Zhenyu Liu and Dongfang Li and Xinyuan Wei and Youcheng Pan and Yang Xiang and Meishan Zhang and Haofen Wang and Jun Yu and Baotian Hu and Min Zhang},
      year={2026},
      eprint={2506.20923},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2506.20923}, 
}

@misc{hu2025kalmembedding,
      title={KaLM-Embedding: Superior Training Data Brings A Stronger Embedding Model}, 
      author={Xinshuo Hu and Zifei Shan and Xinping Zhao and Zetian Sun and Zhenyu Liu and Dongfang Li and Shaolin Ye and Xinyuan Wei and Qian Chen and Baotian Hu and Haofen Wang and Jun Yu and Min Zhang},
      year={2025},
      eprint={2501.01028},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2501.01028}, 
}
```

### Contact
If you encounter any issues, feel free to contact us via the email: <zhaoxinping@stu.hit.edu.cn>