---
license: mit
library_name: LongCat-Flash-Lite-Sparse
pipeline_tag: text-generation
tags:
- transformers
---
# LongCat-Flash-Lite-Sparse

<div align="center">
  <img src="https://raw.githubusercontent.com/meituan-longcat/LongCat-Flash-Chat/main/figures/longcat_logo.svg" 
       width="300" 
       alt="LongCat Logo"/>
</div>

<hr>

<div align="center" style="line-height: 1;">
  <a href="https://github.com/meituan-longcat/LongCat-Flash-Chat/blob/main/figures/wechat_official_accounts.png" target="_blank" style="margin: 2px;">
    <img alt="Wechat" src="https://img.shields.io/badge/WeChat-LongCat-brightgreen?logo=wechat&logoColor=white" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://x.com/Meituan_LongCat" target="_blank" style="margin: 2px;">
    <img alt="Twitter Follow" src="https://img.shields.io/badge/Twitter-LongCat-white?logo=x&logoColor=white" style="display: inline-block; vertical-align: middle;"/>
  </a>
</div>

<div align="center" style="line-height: 1;">
  <a href="https://huggingface.co/meituan-longcat/LongCat-Flash-Chat/blob/main/LICENSE" style="margin: 2px;">
    <img alt="License" src="https://img.shields.io/badge/License-MIT-f5de53?&color=f5de53" style="display: inline-block; vertical-align: middle;"/>
  </a>
</div>

<p align="center">
  <a href="https://arxiv.org/abs/2608.01662"><b>Tech Report</b> 📄</a>
</p>

## Model Introduction

LongCat-Flash-Lite-Sparse is a non-thinking Mixture-of-Experts (MoE) model with 69B total parameters and approximately 3B activated parameters per token. Built on [LongCat-Flash-Lite](https://huggingface.co/meituan-longcat/LongCat-Flash-Lite), it replaces dense MLA with **LongCat Sparse Attention (LSA)** and natively supports context lengths of up to 1M tokens. Compared with its dense predecessor, LongCat-Flash-Lite-Sparse improves long-context inference efficiency and agentic capabilities while preserving strong reasoning and general-knowledge performance.

### Key Features

#### 🌟 LongCat Sparse Attention (LSA)

LSA is a hardware-efficient sparse-attention framework that extends DeepSeek Sparse Attention (DSA) with three complementary indexing mechanisms:

- **Streaming-Aware Indexing (SI)** reallocates part of the token-selection budget to a fixed sink and local sliding window while retaining dynamic sparse selection for the remaining tokens. This design converts fragmented KV access into more predictable, contiguous reads, improving HBM access efficiency and effective bandwidth.
- **Cross-Layer Indexing (CLI)** exploits the stability of attention saliency across adjacent layers, allowing multiple consecutive layers to reuse the results of a single indexing pass at inference time. This capability is learned through cross-layer distillation during training.
- **Hierarchical Indexing (HI)** adopts a coarse-to-fine, two-stage scoring scheme: it first recalls candidate blocks using coarse-grained scores and then performs fine-grained token selection within those blocks. By reducing the candidate space processed for each query, HI lowers indexing overhead and can be enabled at inference time without additional training.

Together, these mechanisms enable LongCat-Flash-Lite-Sparse to process long contexts substantially more efficiently without compromising model quality.


#### 🌟 Native 1M-Token Context Support

To strengthen long-context capabilities, we update the long-context extension stage of LongCat-Flash-Lite with an enriched corpus and a progressive schedule that scales to 1,024K, enabling native support for context lengths up to 1M.

#### 🌟 Strong Agentic Performance

LongCat-Flash-Lite-Sparse delivers stronger performance than its dense predecessor on agentic coding, search, and tool-use tasks.

Please refer to our [technical report](https://arxiv.org/abs/2608.01662) for details!

## Evaluation Results

## Standard Benchmarks

| Benchmark                     | Lite-Dense | Lite-Sparse (w/o HI) | Lite-Sparse (w/ HI) |
| ----------------------------- | ---------- | -------------------- | ------------------- |
| **Agentic Coding**            |            |                      |                     |
| SWE-Bench Verified(acc)       | 54.40      | 68.20            | 65.20               |
| SWE-Bench Pro(acc)            | -          | 40.63            | 39.40               |
| SWE-Bench Multilingual(acc)   | 38.10      | 59.33            | 56.00               |
| TerminalBench 2.0(acc)        | 33.75  | 33.70                | 32.58               |
| **Agentic Tool Use**          |            |                      |                     |
| τ²-Telecom(avg@4)             | 72.80      | 95.18                | 96.05           |
| VitaBench(avg@4)              | 7.00       | 21.67            | 20.42               |
| MCP-Atlas                     | -          | 45.60            | 45.00               |
| **Agentic Search**            |            |                      |                     |
| BrowseComp(pass@1)            | -          | 48.62            | 48.18               |
| BrowseComp-zh(pass@1)         | -          | 61.94            | 61.59               |
| RWSearch(pass@1)              | -          | 68.50            | 66.00               |
| **General Domains**           |            |                      |                     |
| MMLU(acc)                     | 85.52  | 85.31                | 85.14               |
| MMLU-Pro(acc)                 | 78.29      | 79.24            | 78.68               |
| CMMLU(acc)                    | 82.48      | 84.25                | 84.51           |
| C-Eval(acc)                   | 86.55  | 85.76                | 85.71               |
| **Mathematical Reasoning**    |            |                      |                     |
| GPQA-Diamond(avg@16)          | 66.78      | 69.49            | 69.03               |
| MATH500(acc)                  | 96.80  | 95.80                | 96.80           |
| AIME 2026(avg@32)             | -          | 65.73            | 64.90               |
| HMMT 2026 Feb(avg@32)         | -          | 40.53                | 41.47           |
| BeyondAIME(avg@10)            | -          | 44.20            | 42.30               |
| IMO AnswerBench(avg@4)        | -          | 49.38            | 46.69               |

> **Note:** Lite-Dense denotes the LongCat-Flash-Lite, with metrics sourced from its [technical report](https://arxiv.org/abs/2601.21204). Lite-Sparse (w/o HI) and Lite-Sparse (w/ HI) denote the sparse variants evaluated without and with Hierarchical Indexing, respectively.

## Long-Context Benchmarks

| Capability Dimension | Benchmark            | Lite-Sparse (w/o HI) | Lite-Sparse (w/ HI) |
| -------------------- | -------------------- | -------------------- | ------------------- |
| **Foundational**     |                      |                      |                     |
| Retrieval            | MRCR (8-needle)      | 44.66            | 44.47               |
| Aggregation          | OOLong-Synth         | 38.42            | 37.88               |
| Multi-step Reasoning | GraphWalks Extend    | 66.27            | 65.63               |
| **Application**      |                      |                      |                     |
| Question Answering   | LOFT Retrieval Extend| 43.75                | 44.38           |
| In-context Learning  | HELMET-ICL Extend    | 91.63            | 90.50               |
| Code Understanding   | LongCodeQA           | 62.30            | 59.37               |
| Long-range Memory    | AMemBench-ACU        | 33.25            | 33.13               |
| Holistic Assessment  | LongBench-v2         | 52.50                | 53.64           |
| Holistic Assessment  | AA-LCR               | 48.00            | 47.33               |


## Deployment

We have implemented basic adaptations in SGLang ([PR](https://github.com/sgl-project/sglang/pull/32918)) to support the deployment of LongCat-Flash-Lite-Sparse.

LongCat-Flash-Lite-Sparse can be served on a single node (e.g., 1xH20-141G).

The server can be launched as follows:

```py
python3 -m sglang.launch_server \
  --trust-remote-code \
  --model meituan-longcat/LongCat-Flash-Lite-Sparse \
  --host 0.0.0.0 \
  --port 30000 \
  --max-running-requests 64 \
  --mem-fraction-static 0.93 \
  --chunked-prefill-size 2048 \
  --nsa-prefill-backend fa3 \
  --kv-cache-dtype bfloat16
```

## License Agreement

This repository, including both the model weights and the source code, is released under the **MIT License**.

Any contributions to this repository are licensed under the MIT License, unless otherwise stated. This license does not grant any rights to use Meituan trademarks or patents.

For details, see the [LICENSE](./LICENSE) file.

## Usage Considerations

This model has not been specifically designed or comprehensively evaluated for every possible downstream application.

Developers should take into account the known limitations of large language models, including performance variations across different languages, and carefully assess accuracy, safety, and fairness before deploying the model in sensitive or high-risk scenarios.
It is the responsibility of developers and downstream users to understand and comply with all applicable laws and regulations relevant to their use case, including but not limited to data protection, privacy, and content safety requirements.

Nothing in this Model Card should be interpreted as altering or restricting the terms of the MIT License under which the model is released.

<!-- ## Citation

We kindly encourage citation of our work if you find it useful.

```

``` -->

## Contact

Please contact us at <a href="mailto:longcat-team@meituan.com">longcat-team@meituan.com</a> or open an issue if you have any questions.
