---
license: mit
pipeline_tag: text-generation
---
<p align="center">
    <img src="https://mdn.alipayobjects.com/huamei_qa8qxu/afts/img/A*4QxcQrBlTiAAAAAAQXAAAAgAemJ7AQ/original" width="100"/>
</p>
<p align="center">🤗 <a href="https://huggingface.co/inclusionAI">Hugging Face</a>&nbsp;&nbsp; | &nbsp;&nbsp;🤖 <a href="https://modelscope.cn/organization/inclusionAI">ModelScope </a>&nbsp;&nbsp; | &nbsp;&nbsp;🐙 <a href="https://openrouter.ai/inclusionai/ling-3.0-tiny:free">OpenRouter </a>&nbsp;&nbsp;</p>

# Introduction
We are introducing **Ling-3.0-tiny**, a lightweight hybrid reasoning MoE model with **7.9B** total parameters and only **1.3B** activated parameters per token. 
It is designed to deliver strong reasoning and agentic capabilities at low inference cost, making advanced model capabilities more accessible for local and resource-constrained deployment. 
BF16, FP8, and INT4 weights are provided for a wide range of hardware and deployment settings.

Key highlights of the model are summarized below:

+ **Efficient Hybrid-Linear Architecture:** Ling-3.0-tiny integrates a 3:1 alternating stacking of KDA and MLA (3 Kimi Delta Attention layers followed by 1 Multi-Head Latent Attention layer per 4-layer block) with a sparse MoE FFN comprising 128 routed experts. Each token activates only 8 routed experts and 1 shared expert, allowing the model to balance long-context modeling capability, parameter efficiency, and computational cost.
+ **Native Hybrid Reasoning and Agentic Capabilities:** Ling-3.0-tiny supports both fast responses and multi-step reasoning, with thinking mode configurable per request through `enable_thinking`. It delivers balanced performance across general agent tasks, coding, mathematical and scientific reasoning, and instruction following.
+ **Local and Edge Deployment:** Designed for efficient local deployment, Ling-3.0-tiny has been validated on **NVIDIA DGX Spark, Apple Silicon MacBook, and Mac mini**, enabling capable reasoning and agentic workloads without datacenter-class GPUs. With FP8, Ling-3.0-tiny reaches around **100-105 tokens/s on DGX Spark** and **86-90 tokens/s on an M4 Pro MacBook**, with approximately **8.34 GiB peak memory usage** at an 8K context length.

# Model Overview
Ling-3.0-tiny inherits the hybrid linear attation architecture of Ling-3.0 series, while being specifically optimized for lightweight and accessible deployment. The model has 7.9B total parameters, with only 1.3B parameters activated per token.

The architecture of Ling-3.0-tiny is designed to make computational efficiency serve real-world agentic performance.

+ A 3:1 KDA–MLA architecture (3 KDA layers and 1 MLA layer per 4-layer block) provides more efficient long-context processing;
+ A sparse MoE FFN with 128 experts activates 8 routed experts and 1 shared expert per token, enabling broad model capabilities with only 1.3B activated parameters per token.
+ Native hybrid reasoning enables fast responses for routine tasks and multi-step reasoning for complex tasks within a single model.

Overall, these designs deliver the inference efficiency needed to deploy lightweight models in real-world agentic workflows.

<!-- Ling-3.0-tiny architecture diagram -->
![](https://cdn-uploads.huggingface.co/production/uploads/675fc648a63fff7b5be452f6/mifa16S1bZajl5mX90s_O.png)

# Evaluation
We evaluated Ling-3.0-tiny across agentic tasks, coding, long-context understanding, knowledge reliability, mathematical and scientific reasoning, and instruction following.
Ling-3.0-tiny achieves a score of **25** on the Artificial Analysis Intelligence Index v4.1.1 and **16** on the Artificial Analysis Agentic Index. 
In Artificial Analysis testing, Ling-3.0-tiny reaches an output speed of over **160 tokens/s**, with approximately **18 seconds** of end-to-end latency for a 500-token response, including reasoning time. 
These results highlight the model's efficiency relative to its 1.3B activated parameter footprint.

The following table presents representative benchmarks for Ling-3.0-tiny:

![image](https://cdn-uploads.huggingface.co/production/uploads/6502cf8fbdaeae26417cd3c9/g9Thw4ohjkDGYw0Cq7mKi.png)

> + Thinking mode is enabled by default. The recommended sampling parameters for Ling-3.0-tiny are `temperature=1.0`, `top_p=0.95`, and `top_k=20`.
> + Terminal-Bench 2.1: Evaluated under the Artificial Analysis (AA) protocol using the default Terminus 2 harness, a unified 2-hour timeout, the provided JSON parser in preserve-thinking mode, and 3 runs per task (mean). Decoding uses temperature=1.0, max_new_tokens=32K, with a 256K context window.

# Quickstart
## SGLang
The hardware- and recipe-specific launch matrix (BF16/FP8 × Low-Latency / High-Throughput / HiCache + Mooncake), with a live command generator and verified configurations, lives in the SGLang cookbook:

**Cookbook:** https://docs.sglang.io/cookbook/autoregressive/InclusionAI/Ling-3.0-tiny


### Install SGLang
Use the pre-built image that tracks the Ling-3.0 runtime:

```bash
docker pull lmsysorg/sglang:dev-Ling-3.0-tiny
```

### Run Inference
Recommended low-latency recipe (built-in MTP / NEXTN, 256K YaRN context) on 1× 141GB-class GPU (H20-3e) or a 1-GPU Blackwell node:

**Server**

```bash
docker run --rm --gpus all --ipc=host --shm-size 32g \
  -p 30000:30000 \
  -e HF_TOKEN=<your-hf-token> \
  lmsysorg/sglang:dev-Ling-3.0-tiny \
  env SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1 \
  python3 -m sglang.launch_server \
    --model-path inclusionAI/Ling-3.0-tiny \
    --tp 1 \
    --json-model-override-args '{"rope_scaling":{"rope_type":"yarn","factor":2.0,"rope_theta":6000000,"partial_rotary_factor":0.5,"original_max_position_embeddings":131072}}' \
    --context-length 262144 \
    --speculative-algorithm NEXTN \
    --mem-fraction-static 0.8 \
    --host 0.0.0.0 \
    --port 30000
```

**Client**

Thinking is enabled by default by both the chat template and the `ling3` reasoning parser. Disable it per request with `"chat_template_kwargs": {"enable_thinking": false}`. We recommend the sampling parameters `temperature=1.0`, `top_p=0.95`, and `top_k=20`.

```bash
curl -s http://localhost:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "auto",
       "messages": [{"role": "user", "content": "What is the capital of France?"}],
       "stream": true,
       "temperature": 1.0,
       "top_k": 20,
       "top_p": 0.95
     }'
```
For `--reasoning-parser ling3` / `--tool-call-parser ling3`, the HiCache + Mooncake L3 setup, and GSM8K / bench_serving reproduction commands, see the cookbook page linked above.

## vLLM
### Install vLLM with Ling-3.0 Support
```bash
pip install uv

uv venv ~/my_ling_env

source ~/my_ling_env/bin/activate

git clone -b ling_3_0 https://github.com/inclusionAI/vllm-ling-v3.git

cd vllm-ling-v3

VLLM_USE_PRECOMPILED=1 uv pip install --editable . --torch-backend=auto
```

### Run Inference
Here is the example to run Ling-3.0-tiny with a single GPU, where the server port is `${PORT}`:

**Server**

```bash
vllm serve "$MODEL_PATH" \
    --port "$PORT" \
    --trust-remote-code \
    --served-model-name auto \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.85 \
    --enable-prefix-caching \
    --mamba-cache-mode align \
    --enable-auto-tool-choice \
    --tool-call-parser ling3 \
    --reasoning-parser ling3
```

**Client**

For better performance, We recommend setting `enable_thinking=true` with `temperature=1.0`, `top_p=0.95`, and `top_k=20`.

```bash
curl -s http://${MASTER_IP}:${PORT}/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "auto",
       "messages": [{"role": "user", "content": "What is the capital of France?"}],
       "chat_template_kwargs": {"enable_thinking": true},
       "stream": true,
       "temperature": 1.0, 
       "top_k": 20,
       "top_p": 0.95
     }'
```

## Ollama
> + This configuration has been verified on an M4 Pro Mac with 48 GB of unified memory.

### Preparation and Build
```bash
git clone https://github.com/ollama/ollama.git
cd ollama
git fetch origin refs/pull/17643/head:bailing-moe-v3
git switch bailing-moe-v3

cmake -B build .
cmake --build build --parallel 8
```

> + Support is currently provided by [ollama/ollama#17643](https://github.com/ollama/ollama/pull/17643) and is limited to running via MLX on Apple Silicon.
> + Use the local `./ollama` executable built from source in this section. This functionality is not yet included in the official Ollama release.

### Import Model
Replace `/absolute/path/to/bf16_weights` with the absolute path to the BF16 model weights directory. The imported model will be named `ling-tiny-bf16`:

```bash
printf 'FROM /absolute/path/to/bf16_weights\n' > /tmp/Modelfile.ling
./ollama create ling-tiny-bf16 --experimental -f /tmp/Modelfile.ling
```

### Start Service
Set the default context length to 8192, and then start the Ollama service:

```bash
# The service listens on http://127.0.0.1:11434 by default
OLLAMA_CONTEXT_LENGTH=8192 ./ollama serve
```

### Call API
```bash
curl -sS http://127.0.0.1:11434/api/generate -d '{
  "model": "ling-tiny-bf16",
  "prompt": "<role>SYSTEM</role>detailed thinking on<|role_end|><role>HUMAN</role>Calculate 17 × 23 and output only the number.<|role_end|><role>ASSISTANT</role>\n<think>",
  "raw": true,
  "think": true,
  "stream": false,
  "options": {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 20,
    "num_predict": 2048
  }
}' | jq -r .response
```
