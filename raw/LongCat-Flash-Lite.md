---
license: mit
library_name: LongCat-Flash-Lite
pipeline_tag: text-generation
tags:
- transformers
---

# LongCat-Flash-Lite

<div align="center">
  <img src="https://raw.githubusercontent.com/meituan-longcat/LongCat-Flash-Chat/main/figures/longcat_logo.svg" 
       width="300" 
       alt="LongCat Logo"/>
</div>

<hr>


<div align="center" style="line-height: 1;">

  <a href="https://huggingface.co/meituan-longcat" target="_blank" style="margin: 2px;">
    <img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-LongCat-ffc107?color=ffc107&logoColor=white" style="display: inline-block; vertical-align: middle;"/>
  </a>
</div>

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
  <a href="https://arxiv.org/abs/2601.21204"><b>Tech Report</b>&nbsp;📄</a>
</p>

## Model Introduction
We introduce LongCat-Flash-Lite, a non-thinking 68.5B parameter Mixture-of-Experts (MoE) model with approximately 3B activated parameters, supporting a 256k context length through the YaRN method. Building upon the LongCat-Flash architecture, LongCat-Flash-Lite distinguishes itself through the integration of an **N-gram embedding** table designed to enhance both model performance and inference speed. Despite allocating over 30B parameters to embeddings, LongCat-Flash-Lite not only outperforms parameter-equivalent MoE baselines but also demonstrates exceptional competitiveness against existing models of comparable scale, particularly in the agentic and coding domains.



### Key Features

#### 🌟  Superior Scaling Efficiency: A Better Alternative to MoE
Through comprehensive scaling experiments across diverse scenarios, we identify specific regimes where embedding scaling achieves a superior Pareto frontier compared to increasing the number of experts, thereby offering a highly efficient alternative for model scaling. We further delineate a comprehensive set of architectural factors that determine embedding scaling efficacy, encompassing integration timing, parameter budgeting, hash collision mitigation, hyperparameter configuration, and embedding initialization, alongside the impacts of model width and depth. 

#### 🌟 Superior Inference Efficiency with Specialized System Optimization
In contrast to FFN-based experts, the N-gram embedding table inherently mitigates I/O bottlenecks within MoE layers, yielding substantial improvements in inference latency. Furthermore, we introduce a specialized N-gram Cache and develop synchronized kernels, which collectively and significantly boost inference efficiency.

#### 🌟 Strong Agentic and Coding Performance
LongCat-Flash-Lite demonstrates robust capabilities in agentic tool use and coding proficiency that are highly competitive relative to its model scale. 

Please refer to our [technical report](https://arxiv.org/abs/2601.21204) for details!

## Evaluation Results

| Benchmark | Kimi-Linear-48B-A3B | Qwen3-Next-80B-A3B-Instruct | Gemini 2.5 Flash-Lite | LongCat-Flash-Lite |
|----------|---------------------|----------------------------|----------------------|---------|
| **Architecture** | MoE | MoE | - | MoE + NE |
| **# Total Params** | 48B | 80B | - | 68.5B |
| **# Activated Params** | 3B | 3B | - | 2.9B~4.5B |
| **Agentic Tool Use** | | | | |
| Tau2-Airline(avg@8) | 44.00 | 45.5* | 35.00 | 58.00 |
| Tau2-Retail(avg@8) | 18.86 | 57.3* | 37.50 | 73.10 |
| Tau2-Telecom(avg@8) | 15.68 | 13.2* | 21.93 | 72.80 |
| **Agentic Coding** | | | | |
| SWE-Bench(acc) | 32.80 | 37.60 | 41.3* | 54.40 |
| TerminalBench(acc) | 20.00 | 15.19 | 20.00 | 33.75 |
| SWE-Bench Multiligual | 37.20 | 31.30 | - | 38.10 |
|PRDBench | - | 15.36 | - |  39.63 |
| **General Domains** | | | | |
| GPQA-Diamond(avg@16) | 69.89 | 74.33 | 70.20* | 66.78 |
| MMLU(acc) | 79.91 | 89.28 | 84.68 | 85.52 |
| MMLU-Pro(acc) | 67.22 | 82.93 | 78.95 | 78.29 |
| CEval(acc) | 78.48 | 90.91 | 75.16 | 86.55 |
| CMMLU(acc) | 76.26 | 86.50 | 72.06 | 82.48 |
| **Mathematical Reasoning** | | | | |
| MATH500(acc) | 94.20 | 98.00 | 95.20 | 96.80 |
| AIME24(avg@32) | 70.52 | 81.35 | 63.33 | 72.19 |
| AIME25(avg@32) | 59.58 | 68.44 | 50.1* | 63.23 |

> **Note:** Values marked with * are sourced from public reports. NE is an abbreviation of N-gram Embedding.

## Quick Start
To use LongCat-Flash-Lite with transformers, we need at least 2 GPUs (80GB VRAM each, e.g., H100/A100 80GB), and we recommend the following environment:

* `python` >= 3.10
* `torch` >= 2.6
* `transformers` >= 4.57.6
* `accelerate` >= 1.10.0

```shell
pip install -U transformers==4.57.6 accelerate==1.10.0
```

Basic Usage Example:
```py
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "meituan-longcat/LongCat-Flash-Lite"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Give me a brief introduction to large language models."}
]
input_ids = tokenizer.apply_chat_template(
    messages, 
    add_generation_prompt=True, 
    return_tensors="pt"
).to(model.device)
generated_ids = model.generate(inputs=input_ids, max_new_tokens=256)
output_ids = generated_ids[0][len(input_ids[0]):].tolist()
response = tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")
print(response)
```

Tool Calling Example:
```py
tools = [
    {
        "type": "function",
        "function": {
            "name": "func_add",
            "description": "Calculate the sum of two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x1": {"type": "number", "description": "The first addend"},
                    "x2": {"type": "number", "description": "The second addend"}
                },
                "required": ["x1", "x2"]
            }
        }
    }
]
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Please tell me what is $$125679 + 234519$$?"},
    {
        "role": "assistant", 
        "content": "I'll calculate the sum of 125679 and 234519 for you.", 
        "tool_calls": [{"type": "function", "function": {"name": "func_add", "arguments": {"x1": 125679, "x2": 234519}}}]
    },
    {"role": "tool", "name": "func_add", "content": '{"ans": 360198}'}
]

input_ids = tokenizer.apply_chat_template(
    messages, 
    tools=tools,
    add_generation_prompt=True, 
    return_tensors="pt"
).to(model.device)
generated_ids = model.generate(inputs=input_ids, max_new_tokens=256)
output_ids = generated_ids[0][len(input_ids[0]):].tolist()
response = tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")
print(response)
```

Response Parsing:

```python
from parse_model_response import parse_model_response

response = tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")
parsed_message = parse_model_response(response, tools)
```
See [`parse_model_response.py`](./parse_model_response.py) for detailed implementation and examples.

<br>

Recommended Sampling Setting:
```shell
{ "repetition_penalty": 1.06, "temperature": 0.7, "top_p": 0.95, "top_k": 4 }
```

## Deployment

We have implemented basic adaptations in SGLang ([PR](https://github.com/sgl-project/sglang/pull/17838)) to support the deployment of LongCat-Flash-Lite.

LongCat-Flash-Lite can be served on a single node (e.g., 8xH20-141G) using a combination of Tensor Parallelism and Expert Parallelism.

Compile and update sgl-kernel first.

```shell
cd sgl-kernel
python3 -m uv build --wheel --color=always --no-build-isolation \
        -Ccmake.define.SGL_KERNEL_ENABLE_SM90A=1 \
        -Ccmake.define.CMAKE_POLICY_VERSION_MINIMUM=3.5 \
        -Cbuild-dir=build .
pip3 install dist/sgl_kernel-0.3.21-cp310-abi3-linux_x86_64.whl --force-reinstall
```
Then launch the server.
```py
python3 -m sglang.launch_server \
    --model meituan-longcat/LongCat-Flash-Lite \
    --port 8080 \
    --host 0.0.0.0 \
    --mem-fraction-static 0.9 \
    --max-running-requests 64 \
    --trust-remote-code \
    --skip-server-warmup \
    --attention-backend flashinfer \
    --ep 8 \
    --tp 8 \
    --disable-cuda-graph
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


## Citation

We kindly encourage citation of our work if you find it useful.

```
@misc{liu2026scalingembeddingsoutperformsscaling,
      title={Scaling Embeddings Outperforms Scaling Experts in Language Models}, 
      author={Hong Liu and Jiaqi Zhang and Chao Wang and Xing Hu and Linkun Lyu and Jiaqi Sun and Xurui Yang and Bo Wang and Fengcun Li and Yulei Qian and Lingtong Si and Yerui Sun and Rumei Li and Peng Pei and Yuchen Xie and Xunliang Cai},
      year={2026},
      eprint={2601.21204},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2601.21204}, 
}
```


## Contact
Please contact us at <a href="mailto:longcat-team@meituan.com">longcat-team@meituan.com</a> or open an issue if you have any questions.

