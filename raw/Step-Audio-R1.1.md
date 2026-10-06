---
license: apache-2.0
pipeline_tag: audio-text-to-text
library_name: transformers
tags:
- audio-reasoning
- chain-of-thought
- multi-modal
- step-audio-r1
---

## Overview of Step-Audio-R1.1

<a href="https://www.stepfun.com/studio/audio?tab=conversation"><img src="https://img.shields.io/static/v1?label=Space%20Playground&message=Studio&color=yellow"></a> <a href="https://huggingface.co/spaces/stepfun-ai/Step-Audio-R1"><img src="https://img.shields.io/static/v1?label=Space&message=Web&color=green"></a> &ensp;

### Introduction
Step-Audio R1.1 (Realtime) is a major upgrade to Step-Audio-R1, designed for interactive spoken dialogue with both **real-time responsiveness** and **strong reasoning capability**.  

Unlike conventional streaming speech models that trade intelligence for latency, R1.1 enables *thinking while speaking*, achieving high intelligence without sacrificing speed.

### Mind-Paced Speaking (Low Latency)
Based on the research [*Mind-Paced Speaking*](MPS.pdf), the Realtime variant adopts a **Dual-Brain Architecture**:
- A **Formulation Brain** responsible for high-level reasoning
- An **Articulation Brain** dedicated to speech generation

This decoupling allows the model to perform **Chain-of-Thought reasoning during speech output**, maintaining ultra-low latency while handling complex tasks in real time.

### Acoustic-Grounded Reasoning (High Intelligence)
To address the *inverted scaling* issue—where reasoning over transcripts can degrade performance—Step-Audio R1.1 grounds its reasoning directly in acoustic representations rather than text alone.

Through iterative self-distillation, extended deliberation becomes a strength instead of a liability. This enables effective test-time compute scaling and leads to **state-of-the-art performance**, including top-ranking results on the AA benchmark.


![image](https://cdn-uploads.huggingface.co/production/uploads/64ba9dfdbfd8286d23b5c0fd/GTZwkSO5q0ryc6BUC82uT.png)

![image](https://cdn-uploads.huggingface.co/production/uploads/64ba9dfdbfd8286d23b5c0fd/cN3V5c_6TmXVMPH8tuhu5.png)

![image](https://cdn-uploads.huggingface.co/production/uploads/64ba9dfdbfd8286d23b5c0fd/qx25DGHPuDEK5FK1hBxOB.png)

## Online demonstration

### StepFun Audio Studio

- Both Step-Audio-R1.1 are available in our [StepFun Audio Studio](https://www.stepfun.com/studio/audio).
- You will need an API key from the [StepFun Open Platform](https://platform.stepfun.com/).

## WeChat group

You can scan the following QR code to join our WeChat group for communication and discussion.
<div align="center">
  <img src="https://cdn-uploads.huggingface.co/production/uploads/66518fd07d8cb2629a514c18/DRdnp1SN-yxhlNOfy26mE.jpeg" width="200" alt="QR code">
</div>

## Model Usage
### 📜 Requirements
- **GPU**: NVIDIA GPUs with CUDA support (tested on 4×L40S/H100/H800/H20).
- **Operating System**: Linux.
- **Python**: >= 3.10.0.

### ⬇️ Download Model
First, you need to download the Step-Audio-R1 model weights.

**Method A · Git LFS**
   ```bash
   git lfs install
   git clone https://huggingface.co/stepfun-ai/Step-Audio-R1.1
   ```

**Method B · Hugging Face CLI**
   ```bash
   hf download stepfun-ai/Step-Audio-R1.1 --local-dir ./Step-Audio-R1.1
   ```

### 🚀 Deployment and Execution
We provide two ways to serve the model: Docker (recommended) or compiling the customized vLLM backend.

#### 🐳 Method 1 · Run with Docker (Recommended)

A customized vLLM image is required.

1.  **Pull the image**:
```bash
docker pull stepfun2025/vllm:step-audio-2-v20250909
```
2.  **Start the service**:
    Assuming the model is downloaded in the `Step-Audio-R1` folder in the current directory.

    ```bash
    docker run --rm -ti --gpus all \
        -v $(pwd)/Step-Audio-R1.1:/Step-Audio-R1.1 \
        -p 9999:9999 \
        stepfun2025/vllm:step-audio-2-v20250909 \
        -- vllm serve /Step-Audio-R1.1 \
        --served-model-name Step-Audio-R1.1 \
        --port 9999 \
        --max-model-len 16384 \
        --max-num-seqs 32 \
        --tensor-parallel-size 4 \
        --chat-template '{%- macro render_content(content) -%}{%- if content is string -%}{{- content.replace("<audio_patch>\n", "<audio_patch>") -}}{%- elif content is mapping -%}{{- content['"'"'value'"'"'] if '"'"'value'"'"' in content else content['"'"'text'"'"'] -}}{%- elif content is iterable -%}{%- for item in content -%}{%- if item.type == '"'"'text'"'"' -%}{{- item['"'"'value'"'"'] if '"'"'value'"'"' in item else item['"'"'text'"'"'] -}}{%- elif item.type == '"'"'audio'"'"' -%}<audio_patch>{%- endif -%}{%- endfor -%}{%- endif -%}{%- endmacro -%}{%- if tools -%}{{- '"'"'<|BOT|>system\n'"'"' -}}{%- if messages[0]['"'"'role'"'"'] == '"'"'system'"'"' -%}{{- render_content(messages[0]['"'"'content'"'"']) + '"'"'<|EOT|>'"'"' -}}{%- endif -%}{{- '"'"'<|BOT|>tool_json_schemas\n'"'"' + tools|tojson + '"'"'<|EOT|>'"'"' -}}{%- else -%}{%- if messages[0]['"'"'role'"'"'] == '"'"'system'"'"' -%}{{- '"'"'<|BOT|>system\n'"'"' + render_content(messages[0]['"'"'content'"'"']) + '"'"'<|EOT|>'"'"' -}}{%- endif -%}{%- endif -%}{%- for message in messages -%}{%- if message["role"] == "user" -%}{{- '"'"'<|BOT|>human\n'"'"' + render_content(message["content"]) + '"'"'<|EOT|>'"'"' -}}{%- elif message["role"] == "assistant" -%}{{- '"'"'<|BOT|>assistant\n'"'"' + (render_content(message["content"]) if message["content"] else '"'"''"'"') -}}{%- set is_last_assistant = true -%}{%- for m in messages[loop.index:] -%}{%- if m["role"] == "assistant" -%}{%- set is_last_assistant = false -%}{%- endif -%}{%- endfor -%}{%- if not is_last_assistant -%}{{- '"'"'<|EOT|>'"'"' -}}{%- endif -%}{%- elif message["role"] == "function_output" -%}{%- else -%}{%- if not (loop.first and message["role"] == "system") -%}{{- '"'"'<|BOT|>'"'"' + message["role"] + '"'"'\n'"'"' + render_content(message["content"]) + '"'"'<|EOT|>'"'"' -}}{%- endif -%}{%- endif -%}{%- endfor -%}{%- if add_generation_prompt -%}{{- '"'"'<|BOT|>assistant\n<think>\n'"'"' -}}{%- endif -%}' \
        --enable-log-requests \
        --interleave-mm-strings \
        --trust-remote-code
    ```
After the service starts, it will listen on `localhost:9999`.

#### 🐳  Method 2 · Run from Source (Compile vLLM)
Step-Audio-R1 requires a customized vLLM backend.

1.  **Download Source Code**:
    ```bash
    git clone https://github.com/stepfun-ai/vllm.git
    cd vllm
    ```

2.  **Prepare Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install and Compile**:
    vLLM contains both C++ and Python code. We mainly modified the Python code, so the C++ part can use the pre-compiled version to speed up the process.
    
    ```bash
    # Use pre-compiled C++ extensions (Recommended)
    VLLM_USE_PRECOMPILED=1 pip install -e .
    ```

4.  **Switch Branch**:
    After compilation, switch to the branch that supports Step-Audio.
    ```bash
    git checkout feat/step-audio-support
    ```

5.  **Start the Service**:
    ```bash
    # Ensure you are in the vllm directory and the virtual environment is activated
    source .venv/bin/activate

    python3 -m vllm.entrypoints.openai.api_server \
        --model ../Step-Audio-R1.1 \
        --served-model-name Step-Audio-R1.1 \
        --port 9999 \
        --host 0.0.0.0 \
        --max-model-len 65536 \
        --max-num-seqs 128 \
        --tensor-parallel-size 4 \
        --gpu-memory-utilization 0.85 \
        --trust-remote-code \
        --enable-log-requests \
        --interleave-mm-strings \
        --chat-template '{%- macro render_content(content) -%}{%- if content is string -%}{{- content.replace("<audio_patch>\n", "<audio_patch>") -}}{%- elif content is mapping -%}{{- content['"'"'value'"'"'] if '"'"'value'"'"' in content else content['"'"'text'"'"'] -}}{%- elif content is iterable -%}{%- for item in content -%}{%- if item.type == '"'"'text'"'"' -%}{{- item['"'"'value'"'"'] if '"'"'value'"'"' in item else item['"'"'text'"'"'] -}}{%- elif item.type == '"'"'audio'"'"' -%}<audio_patch>{%- endif -%}{%- endfor -%}{%- endif -%}{%- endmacro -%}{%- if tools -%}{{- '"'"'<|BOT|>system\n'"'"' -}}{%- if messages[0]['"'"'role'"'"'] == '"'"'system'"'"' -%}{{- render_content(messages[0]['"'"'content'"'"']) + '"'"'<|EOT|>'"'"' -}}{%- endif -%}{{- '"'"'<|BOT|>tool_json_schemas\n'"'"' + tools|tojson + '"'"'<|EOT|>'"'"' -}}{%- else -%}{%- if messages[0]['"'"'role'"'"'] == '"'"'system'"'"' -%}{{- '"'"'<|BOT|>system\n'"'"' + render_content(messages[0]['"'"'content'"'"']) + '"'"'<|EOT|>'"'"' -}}{%- endif -%}{%- endif -%}{%- for message in messages -%}{%- if message["role"] == "user" -%}{{- '"'"'<|BOT|>human\n'"'"' + render_content(message["content"]) + '"'"'<|EOT|>'"'"' -}}{%- elif message["role"] == "assistant" -%}{{- '"'"'<|BOT|>assistant\n'"'"' + (render_content(message["content"]) if message["content"] else '"'"''"'"') -}}{%- set is_last_assistant = true -%}{%- for m in messages[loop.index:] -%}{%- if m["role"] == "assistant" -%}{%- set is_last_assistant = false -%}{%- endif -%}{%- endfor -%}{%- if not is_last_assistant -%}{{- '"'"'<|EOT|>'"'"' -}}{%- endif -%}{%- elif message["role"] == "function_output" -%}{%- else -%}{%- if not (loop.first and message["role"] == "system") -%}{{- '"'"'<|BOT|>'"'"' + message["role"] + '"'"'\n'"'"' + render_content(message["content"]) + '"'"'<|EOT|>'"'"' -}}{%- endif -%}{%- endif -%}{%- endfor -%}{%- if add_generation_prompt -%}{{- '"'"'<|BOT|>assistant\n<think>\n'"'"' -}}{%- endif -%}'
    ```

After the service starts, it will listen on `localhost:9999`.