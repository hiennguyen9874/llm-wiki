---
tags:
- confucius4
- r2t2
- asr
- streaming
- real-time
- low-latency
- speech-recognition
- vllm
- multilingual
base_model: Qwen/Qwen3-ASR-1.7B
pipeline_tag: automatic-speech-recognition
license: other
license_name: netease-model-use-license-agreement
license_link: https://raw.githubusercontent.com/netease-youdao/Confucius4-R2T2/refs/heads/master/MODEL_LICENSE
---

<div align="center">
    <img src="https://raw.githubusercontent.com/netease-youdao/Confucius4-R2T2/refs/heads/master/resources/R2T2_logo.png" alt="Confucius4-R2T2" width="30%">
    <h1>Confucius4-R2T2: A Low Latency and High Accuracy Real-Time Speech Recognition Model</h1>
        <p>
        <b>
            Real
            Real-Time
            Transcription
        </b>
    </p>
</div>

<div align="center">
    <a href="https://github.com/netease-youdao/Confucius4-R2T2"><img src="https://img.shields.io/badge/GitHub-Confucius4--R2T2-181717?logo=github" alt="GitHub repository"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/netease-youdao/Confucius4-R2T2/blob/master/README.zh.md"><img src="https://img.shields.io/badge/README-中文版本-red" alt="Chinese README"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://raw.githubusercontent.com/netease-youdao/Confucius4-R2T2/refs/heads/master/MODEL_LICENSE"><img src="https://img.shields.io/badge/model_license-NetEase-blue" alt="Model license: NetEase Model Use License Agreement"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/netease-youdao/Confucius4-R2T2/blob/master/LICENSE"><img src="https://img.shields.io/badge/code_license-Apache%202.0-blue" alt="Code license: Apache 2.0"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://r2t2.youdao.com/demo"><img src="https://img.shields.io/badge/Demo-在线体验-orange" alt="Online demo"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://huggingface.co/netease-youdao/Confucius4-R2T2"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Confucius4R2T2-yellow" alt="Hugging Face model"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://modelscope.cn/models/netease-youdao/Confucius4-R2T2"><img src="https://img.shields.io/badge/ModelScope-Confucius4R2T2-purple" alt="ModelScope model"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://r2t2.ai/"><img src="https://img.shields.io/badge/Website-www.r2t2.ai-purple" alt="R2T2 website"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;
</div>
<br>

Confucius4-R2T2 is a low-latency and high-accuracy true streaming Automatic Speech Recognition (ASR) model that features fine-grained and configurable decoding chunks from 80 ms to 2 s. The model operates in append-only output mode: committing transcript text permanently without revising previous words, which is critical for applications where text must be processed or acted upon instantly. This results in a smoother user experience, avoiding disruptive text revisions and visual flickering in real-time applications, such as Real-Time Live Captioning & Subtitling, Downstream NLP Pipelines & LLM Agents, Simultaneous Speech Translation, etc.

R2T2, short for Real Real-Time Transcription, is built upon the Qwen3-ASR model. And it is trained with a unique set of data construction techniques including stable-prefix data, forced time-alignment data, and token-level audio segmentation. Combined with a Longest Stable Prefix (LSP) learning paradigm (tech report will be released soon), R2T2 can dynamically determine when a stable prefix can be safely emitted and when additional audio context is needed. By exposing only stable prefixes, the model provides high-quality context that conditions subsequent predictions while guaranteeing that previously emitted text remains unchanged. Despite its streaming design, R2T2 maintains strong accuracy in offline recognition.

- **Low-latency and high accuracy streaming recognition** — The model achieves accuracy close to that of offline  recognition, with only 200 to 600 milliseconds average latency.
- **Stable streaming output** — Emitted text is committed as it arrives and remains unchanged.
- **Configurable low-latency chunking** - Supports decoding chunks from 80 ms to 2 s for different latency/accuracy trade-offs.
- **No loss in offline accuracy** — Adding streaming support does not degrade offline recognition accuracy.
- **vLLM backend** — Provides high-throughput inference. A Hugging Face `transformers` backend is also available.
- **Context and hotword prompts** — Natively supported.
- **Multilingual support** — Optimized for **Chinese and English**, while also supporting a broad range of additional languages.

Experimental results show that R2T2 achieves state-of-the-art (SOTA) performance in both latency and recognition quality among a range of open-source models, while remaining competitive with leading closed-source systems. The [GitHub repository](https://github.com/netease-youdao/Confucius4-R2T2) provides inference code, a minimal usage example, and a vLLM-based backend supporting both offline and real-time streaming inference.

## Table of Contents

- [Overview](#overview)
- [Demo](#demo)
  - [Side-by-side comparison with GPT-Live-Transcribe](#side-by-side-comparison-with-gpt-live-transcribe)
  - [Additional resources](#additional-resources)
- [Evaluation](#evaluation)
  - [Streaming performance](#streaming-performance)
  - [Accuracy](#accuracy)
    - [English](#english)
    - [Chinese](#chinese)
- [Installation](#installation)
  - [Clone the repository](#clone-the-repository)
  - [Option 1: Conda](#option-1-conda)
  - [Option 2: uv](#option-2-uv)
- [Docker (recommended)](#docker-recommended)
  - [1. Start a container](#1-start-a-container)
  - [2. Run the example inside the container](#2-run-the-example-inside-the-container)
  - [3. Manage the container](#3-manage-the-container)
- [Quick Start](#quick-start)
  - [Configuration](#configuration)
- [Python API](#python-api)
  - [Offline transcription (vLLM backend)](#offline-transcription-vllm-backend)
  - [Streaming transcription (vLLM backend)](#streaming-transcription-vllm-backend)
- [WebSocket Server](#websocket-server)
  - [Start and stop the server](#start-and-stop-the-server)
  - [WebSocket endpoint](#websocket-endpoint)
  - [Message format](#message-format)
  - [Example client](#example-client)
- [Supported Languages](#supported-languages)
- [Community & Contact](#community--contact)
  - [WeChat Group](#wechat-group)
  - [Discord Server](#discord-server)
  - [Business contact](#business-contact)
  - [GitHub Issues](#github-issues)
- [Acknowledgements](#acknowledgements)
- [Citation](#citation)
- [License](#license)

---

## Overview

<div align="center">
  <img src="https://raw.githubusercontent.com/netease-youdao/Confucius4-R2T2/refs/heads/master/resources/R2T2_framework.png" alt="Confucius4-R2T2 framework" width="70%">
  <p><i>Figure 1. Overall framework of R2T2.</i></p>
</div>

## Demo

### Side-by-side comparison with GPT-Live-Transcribe

<div align="center">
  <video controls playsinline preload="metadata" width="90%" src="https://github.com/user-attachments/assets/1b21c04a-766a-434f-96dc-580376b305f1" title="GPT-Live-Transcribe and R2T2 processing the same audio together in real time — a side-by-side comparison.">
    Your browser does not support embedded video.
  </video>
  <p><a href="https://github.com/user-attachments/assets/1b21c04a-766a-434f-96dc-580376b305f1">Watch the comparison video</a></p>
  <p><i>Figure 2. GPT-Live-Transcribe and R2T2 processing the same audio, shown together in real time — a side-by-side comparison.</i></p>
</div>

### Additional resources

More demonstrations, comparisons, and supporting resources will be added here.

## Evaluation

> If you are an author or maintainer of a model included in these comparisons and have questions or concerns about the results, please feel free to contact us through the [GitHub issue tracker](https://github.com/netease-youdao/Confucius4-R2T2/issues). We are happy to share evaluation details and work with you to verify or correct them.

### Streaming performance

The streaming API supports decoding chunks from 80 ms to 2 s; the figures below show representative WER/latency trade-offs at 160 ms.

<div align="center">
  <img src="https://raw.githubusercontent.com/netease-youdao/Confucius4-R2T2/refs/heads/master/resources/asr_en_wer_latency.svg" alt="English WER and retrospective chunk-wise latency comparison across ASR models and configurations" width="80%">
  <p><i>Figure 3. English WER and retrospective chunk-wise latency across model and configuration settings.</i></p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/netease-youdao/Confucius4-R2T2/refs/heads/master/resources/asr_cn_wer_latency.svg" alt="Chinese CER and retrospective chunk-wise latency comparison across ASR models and configurations" width="80%">
  <p><i>Figure 4. Chinese CER and retrospective chunk-wise latency across model and configuration settings.</i></p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/netease-youdao/Confucius4-R2T2/refs/heads/master/resources/asr_pareto_wer_latency.svg" alt="English and Chinese accuracy-latency Pareto frontier for representative streaming ASR configurations" width="96%">
  <p><i>Figure 5. Accuracy-latency Pareto frontier. Lower-left is better; the frontier uses retrospective chunk-wise mean fuzzy latency.</i></p>
</div>

### Accuracy

English results use WER (%), and Chinese results use CER (%); lower is better.

※ Pseudo-streaming model: its partial transcript may revise previously emitted text; unmarked models use true streaming, append-only output.

#### English

<div align="center">
<table>
<thead><tr>
<th rowspan="2" scope="col" align="left">Dataset</th>
<th colspan="2" scope="colgroup" align="center">Qwen</th>
<th rowspan="2" scope="col" align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>R2T2 (Ours)</strong><br><sub>160ms</sub></th>
<th colspan="4" scope="colgroup" align="center">Open-source</th>
<th colspan="3" scope="colgroup" align="center">Proprietary</th>
</tr><tr>
<th scope="col" align="center">Qwen3-ASR※<br><sub>2s/u2/t5</sub></th>
<th scope="col" align="center">Qwen3-ASR base<br><sub>160ms</sub></th>
<th scope="col" align="center">X-ASR<br><sub>160ms</sub></th>
<th scope="col" align="center">WhisperRT※<br><sub>200ms</sub></th>
<th scope="col" align="center">Nemotron<br><sub>160ms</sub></th>
<th scope="col" align="center">Voxtral<br><sub>160ms</sub></th>
<th scope="col" align="center">AssemblyAI※<br><sub>min_latency</sub></th>
<th scope="col" align="center">Commercial A※</th>
<th scope="col" align="center">Commercial B※</th>
</tr></thead><tbody>
<tr>
<th scope="row" align="left">AMI</th>
<td align="center">9.25</td>
<td align="center">24.79</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>11.37</strong></td>
<td align="center">14.41</td>
<td align="center">24.19</td>
<td align="center">18.11</td>
<td align="center">15.94</td>
<td align="center">12.00</td>
<td align="center">13.27</td>
<td align="center">8.44</td>
</tr>
<tr>
<th scope="row" align="left">Giga-clean</th>
<td align="center">8.61</td>
<td align="center">24.37</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>9.60</strong></td>
<td align="center">10.26</td>
<td align="center">13.81</td>
<td align="center">12.67</td>
<td align="center">11.13</td>
<td align="center">9.21</td>
<td align="center">8.84</td>
<td align="center">9.46</td>
</tr>
<tr>
<th scope="row" align="left">LS-clean</th>
<td align="center">1.67</td>
<td align="center">22.30</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>2.13</strong></td>
<td align="center">3.86</td>
<td align="center">4.70</td>
<td align="center">3.71</td>
<td align="center">2.49</td>
<td align="center">1.89</td>
<td align="center">1.73</td>
<td align="center">1.25</td>
</tr>
<tr>
<th scope="row" align="left">LS-other</th>
<td align="center">3.54</td>
<td align="center">25.74</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>4.88</strong></td>
<td align="center">9.64</td>
<td align="center">9.86</td>
<td align="center">8.27</td>
<td align="center">7.15</td>
<td align="center">3.37</td>
<td align="center">3.57</td>
<td align="center">2.48</td>
</tr>
<tr>
<th scope="row" align="left">SPGI</th>
<td align="center">2.90</td>
<td align="center">22.25</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>3.00</strong></td>
<td align="center">5.14</td>
<td align="center">8.66</td>
<td align="center">3.93</td>
<td align="center">3.06</td>
<td align="center">2.14</td>
<td align="center">3.06</td>
<td align="center">1.74</td>
</tr>
<tr>
<th scope="row" align="left">VoxPopuli</th>
<td align="center">3.02</td>
<td align="center">20.71</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>3.07</strong></td>
<td align="center">5.68</td>
<td align="center">8.28</td>
<td align="center">5.69</td>
<td align="center">6.30</td>
<td align="center">4.75</td>
<td align="center">3.17</td>
<td align="center">3.14</td>
</tr>
<tr>
<th scope="row" align="left">Earnings22</th>
<td align="center">6.68</td>
<td align="center">29.72</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>9.36</strong></td>
<td align="center">15.95</td>
<td align="center">35.08</td>
<td align="center">17.22</td>
<td align="center">11.66</td>
<td align="center">7.47</td>
<td align="center">10.32</td>
<td align="center">8.96</td>
</tr>
<tr>
<th scope="row" align="left">TED-LIUM</th>
<td align="center">2.33</td>
<td align="center">19.18</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>3.34</strong></td>
<td align="center">3.75</td>
<td align="center">6.67</td>
<td align="center">5.11</td>
<td align="center">4.60</td>
<td align="center">3.23</td>
<td align="center">3.08</td>
<td align="center">3.30</td>
</tr>
<tr>
<th scope="row" align="left">EN-RealSI</th>
<td align="center">6.54</td>
<td align="center">13.75</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>8.40</strong></td>
<td align="center">8.97</td>
<td align="center">35.36</td>
<td align="center">10.69</td>
<td align="center">14.75</td>
<td align="center">9.73</td>
<td align="center">8.73</td>
<td align="center">17.05</td>
</tr>
</tbody></table></div>

#### Chinese

<div align="center">
<table>
<thead><tr>
<th rowspan="2" scope="col" align="left">Dataset</th>
<th colspan="2" scope="colgroup" align="center">Qwen</th>
<th rowspan="2" scope="col" align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>R2T2 (Ours)</strong><br><sub>160ms</sub></th>
<th colspan="4" scope="colgroup" align="center">Open-source</th>
<th colspan="3" scope="colgroup" align="center">Proprietary</th>
</tr><tr>
<th scope="col" align="center">Qwen3-ASR※<br><sub>2s/u2/t5</sub></th>
<th scope="col" align="center">Qwen3-ASR base<br><sub>160ms</sub></th>
<th scope="col" align="center">X-ASR<br><sub>160ms</sub></th>
<th scope="col" align="center">WhisperRT※<br><sub>200ms</sub></th>
<th scope="col" align="center">Nemotron<br><sub>160ms</sub></th>
<th scope="col" align="center">Voxtral<br><sub>160ms</sub></th>
<th scope="col" align="center">AssemblyAI※<br><sub>min_latency</sub></th>
<th scope="col" align="center">Commercial A※</th>
<th scope="col" align="center">Commercial B※</th>
</tr></thead><tbody>
<tr>
<th scope="row" align="left">Wenet-net</th>
<td align="center">4.94</td>
<td align="center">19.79</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>5.87</strong></td>
<td align="center">8.81</td>
<td align="center">U</td>
<td align="center">24.70</td>
<td align="center">23.53</td>
<td align="center">12.91</td>
<td align="center">5.13</td>
<td align="center">4.79</td>
</tr>
<tr>
<th scope="row" align="left">Wenet-meeting</th>
<td align="center">5.97</td>
<td align="center">20.38</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>7.27</strong></td>
<td align="center">11.33</td>
<td align="center">U</td>
<td align="center">20.18</td>
<td align="center">60.54</td>
<td align="center">11.84</td>
<td align="center">7.07</td>
<td align="center">3.75</td>
</tr>
<tr>
<th scope="row" align="left">SPEECHIO-06</th>
<td align="center">6.10</td>
<td align="center">24.50</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>7.30</strong></td>
<td align="center">7.86</td>
<td align="center">U</td>
<td align="center">22.52</td>
<td align="center">32.16</td>
<td align="center">15.08</td>
<td align="center">5.67</td>
<td align="center">5.34</td>
</tr>
<tr>
<th scope="row" align="left">SPEECHIO-07</th>
<td align="center">6.19</td>
<td align="center">21.16</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>8.20</strong></td>
<td align="center">11.22</td>
<td align="center">U</td>
<td align="center">24.28</td>
<td align="center">22.97</td>
<td align="center">10.84</td>
<td align="center">6.45</td>
<td align="center">6.46</td>
</tr>
<tr>
<th scope="row" align="left">CN-RealSI</th>
<td align="center">3.34</td>
<td align="center">39.72</td>
<td align="center" style="background-color: rgba(79, 140, 255, 0.14); border-left: 2px solid #4F8CFF; border-right: 2px solid #4F8CFF;"><strong>3.48</strong></td>
<td align="center">4.92</td>
<td align="center">U</td>
<td align="center">11.52</td>
<td align="center">8.74</td>
<td align="center">5.15</td>
<td align="center">3.99</td>
<td align="center">3.64</td>
</tr>
</tbody></table></div>

## Installation

We recommend using a **fresh, isolated environment**. For local development and
source installation, use the **Conda** or **uv** environment below. **Docker** is
recommended for quickly running the project with a preconfigured CUDA and runtime
environment — see [Docker](#docker-recommended).

### Clone the repository

```bash
git clone https://github.com/netease-youdao/Confucius4-R2T2.git
cd Confucius4-R2T2
```

### Option 1: Conda

```bash
conda create -n confucius4-r2t2 python=3.12 -y
conda activate confucius4-r2t2

# Install the package with the vLLM backend
pip install -e .
```

### Option 2: uv

```bash
uv venv --python 3.12
source .venv/bin/activate

# Install the package with the vLLM backend
uv pip install -e .
```

Python 3.10+ is supported. Python 3.12 is the version we test against.

vLLM has strict CUDA / PyTorch compatibility requirements. If the install
fails to resolve, check the version matrix on the [vLLM website](https://docs.vllm.ai/)
and pin a combination that matches your CUDA runtime.

## Docker (recommended)

R2T2 runs out of the box on the official **Qwen3-ASR** Docker image, which already ships every runtime library we need.

Pre-built image: [qwenllm/qwen3-asr](https://hub.docker.com/r/qwenllm/qwen3-asr).

Before you begin, install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) to enable GPU access from Docker. If Docker Hub access is slow or unreliable in your region, you may need to configure a registry mirror.

### 1. Start a container

```bash
LOCAL_WORKDIR=/path/to/your/workspace   # host path that will be mounted into the container
HOST_PORT=8000
CONTAINER_PORT=80

docker run --gpus all --name confucius4-r2t2 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p $HOST_PORT:$CONTAINER_PORT \
    --mount type=bind,source=$LOCAL_WORKDIR,target=/data/shared/confucius4-r2t2 \
    --shm-size=4gb \
    -it qwenllm/qwen3-asr:latest
```

Your local workspace (`$LOCAL_WORKDIR`) — including a checkout of this repository and the R2T2 checkpoint — will be mounted inside the container at `/data/shared/confucius4-r2t2`. Host port `8000` is mapped to container port `80`; services running inside the container must bind to `0.0.0.0` (not `127.0.0.1`) for port forwarding to work.

### 2. Run the example inside the container

Once inside the container's shell:

```bash
cd /data/shared/confucius4-r2t2/Confucius4-R2T2
MODEL_PATH=/data/shared/confucius4-r2t2/Confucius4-R2T2 \
    ./run_example.sh /path/to/audio.wav
```

### 3. Manage the container

```bash
# re-enter after exiting
docker start confucius4-r2t2
docker exec -it confucius4-r2t2 bash

# remove completely
docker rm -f confucius4-r2t2
```

## Quick Start

Grab any audio file (mono or stereo, any sample rate — it is resampled to 16 kHz internally) and run:

```bash
./run_example.sh /path/to/audio.wav \
    --model_path /path/to/Confucius4-R2T2 \
    --infer_mode stream_vllm \
    --language Chinese \
    --chunk_size_ms 160
```

Logs are written to `run_example.log` by default. Run `./run_example.sh --help` to see the full flag list.

### Configuration

`run_example.sh` reads the following environment variables (all optional):

| Variable              | Default            | Description                                            |
| --------------------- | ------------------ | ------------------------------------------------------ |
| `MODEL_PATH`          | (required)         | Path or HF repo id of the R2T2 checkpoint              |
| `AUDIO`               | first CLI argument | Path to the input audio file                           |
| `INFER_MODE`          | `stream_vllm`      | `stream_vllm` or `onetime_vllm`                        |
| `LANGUAGE`            | `Chinese`          | Language hint (e.g. `Chinese`, `English`, …)           |
| `CHUNK_SIZE_MS`       | `160`              | Streaming chunk size (80 ms–2 s supported)             |
| `UNFIXED_TOKEN_NUM`   | `1`                | Number of unfixed trailing tokens (rollback window)    |
| `CONTEXT`             | `""`               | Context / hotword hint prepended to the prompt         |
| `CUDA_VISIBLE_DEVICES`| `0`                | GPU id(s) to expose                                    |
| `LOG_FILE`            | `run_example.log`  | Where to write logs                                    |

You can also call `example.py` directly and pass any of these as flags (`--audio`, `--model_path`, `--infer_mode`, `--language`, `--chunk_size_ms`, `--lookahead_ms`, `--unfixed_token_num`, `--context`).

## Python API

Audio inputs can be passed as a local path, a URL, base64 data, or a `(np.ndarray, sr)` tuple. Batched inference is supported. Remember to wrap vLLM code under `if __name__ == '__main__':` to avoid the `spawn` error described in [vLLM Troubleshooting](https://docs.vllm.ai/en/latest/usage/troubleshooting/#python-multiprocessing).

### Offline transcription (vLLM backend)

```python
import librosa
from qwen_asr import Qwen3ASRModel

if __name__ == "__main__":
    asr = Qwen3ASRModel.LLM(
        model="/path/to/Confucius4-R2T2",
        gpu_memory_utilization=0.5,
        max_inference_batch_size=32,
        max_new_tokens=4096,
    )

    wav, sr = librosa.load("path/to/audio.wav", sr=16000, mono=True)

    results = asr.transcribe(
        audio=[(wav, 16000)],
        language=["Chinese"],       # or [None]
        return_time_stamps=False,
    )
    print(results[0].language, results[0].text)
```

### Streaming transcription (vLLM backend)

```python
import librosa
from qwen_asr import Qwen3ASRModel

if __name__ == "__main__":
    asr = Qwen3ASRModel.LLM(
        model="/path/to/Confucius4-R2T2",
        gpu_memory_utilization=0.4,
        max_new_tokens=4,           # keep small for low-latency streaming
    )

    wav, sr = librosa.load("path/to/audio.wav", sr=16000, mono=True)

    state = asr.init_streaming_state(
        context="",                 # optional hotword / topic hint
        language="Chinese",         # or None
        unfixed_chunk_num=0,
        unfixed_token_num=1,
        chunk_size_sec=0.16,
    )

    step = int(0.16 * 16000)
    for pos in range(0, len(wav), step):
        seg = wav[pos : pos + step]
        _, text = asr.streaming_transcribe(seg, state, max_new_tokens=2)
        print("text:", text)

    asr.finish_streaming_transcribe(state)
    print("final:", state.text)
```

For a complete streaming example with adaptive `max_new_tokens` and initial-chunk lookahead handling, see [`example.py`](https://github.com/netease-youdao/Confucius4-R2T2/blob/master/example.py).

## WebSocket Server

For real-time, multi-client streaming ASR, the [GitHub repository](https://github.com/netease-youdao/Confucius4-R2T2) ships a ready-to-run WebSocket server (`ws_server.py`), a launcher script (`run_start_server.sh`), and a reference Python client (`ws_client.py`).

### Start and stop the server

```bash
# Start with a VAD model
./run_start_server.sh start \
    --model_path /path/to/Confucius4-R2T2 \
    --vad_model_path /path/to/Stream-VAD \
    --port 8272 \
    --gpu 0

# Stop
./run_start_server.sh kill

# Restart in one step
./run_start_server.sh restart \
    --model_path /path/to/Confucius4-R2T2 \
    --vad_model_path /path/to/Stream-VAD \
    --port 8272 \
    --gpu 0
```

| Flag                  | Env var              | Default                                                        | Description                                          |
| --------------------- | -------------------- | -------------------------------------------------------------- | ---------------------------------------------------- |
| `-m`, `--model_path`  | `ASR_MODEL_PATH`     | (required)                                                    | Path or HF repo id of the R2T2 checkpoint            |
| `-v`,`--vad_model_path`    | `VAD_MODEL_PATH`     | `checkpoints/vad/Stream-VAD`                                        | Path to the FireRedVAD Stream-VAD model              |
| `-p`, `--port`        | `PORT`               | `8272`                                                         | Port the WebSocket server binds to                   |
| `-g`, `--gpu`         | `CUDA_VISIBLE_DEVICES` | `0`                                                            | GPU id(s) exposed to the server process              |
| `-h`, `--host`        | `HOST_TAG`           | `localhost`                                                    | Host tag used only in the log file name              |

The launcher resolves its own directory, so it can be invoked from anywhere. Logs are written to `nohup_service_ws_<host_tag>_<port>.log` in the current directory. The FireRedVAD model is available from [Hugging Face](https://huggingface.co/FireRedTeam/FireRedVAD/tree/main). We recommend downloading the model files into this repository's `checkpoints` directory:

```bash
# The FireRedVAD repo ships several detectors, but only the streaming one is
# needed. Both commands below keep the `Stream-VAD/` folder name, so the files
# land in checkpoints/vad/Stream-VAD with no extra nesting.

# Option A — hf CLI (pip install -U "huggingface_hub[cli]")
hf download FireRedTeam/FireRedVAD \
    --include "Stream-VAD/*" \
    --local-dir checkpoints/vad

# Option B — git clone
git clone https://huggingface.co/FireRedTeam/FireRedVAD
cp -r FireRedVAD/Stream-VAD checkpoints/vad/
```

Either command leaves the model at `checkpoints/vad/Stream-VAD`, which is exactly what `--vad_model_path` defaults to — so you can drop the flag entirely.

### WebSocket endpoint

| Path                       | Behavior                                                                 |
| -------------------------- | ------------------------------------------------------------------------ |
| `/asr_stream_api_v1`       | Streaming ASR. Each message's `text` is the **new (incremental)** chunk. |

### Message format

**Client → Server:**

- Send raw 16 kHz mono PCM as `int16` binary frames (the reference client uses ≈160 ms per frame, i.e. 2560 samples × 2 bytes).
- Send the string `"YOUDAO_ONETIME_ASR_STREAM_EOS"` to signal end-of-audio; the server will emit any final text and close.

**Server → Client:** JSON messages of the form

```json
{
  "status": "success",
  "requestId": "<uuid>",
  "msg": {
    "text": "hello",
    "reset": false,
    "asr_cost_ms": 35.4,
    "total_cost_ms": 42.0
  }
}
```

- `text` is the newly recognized (incremental) segment since the previous message. Concatenate them client-side to get the full transcript.

### Example client

`ws_client.py` is a minimal example that streams a WAV file to the server and prints the responses.

```bash
# Uses the default URI (ws://localhost:8272/asr_stream_api_v1) and built-in sample audio
python ws_client.py

# Point at a custom endpoint and audio file
python ws_client.py \
    --uri wss://your.host/asr_stream_api_v1 \
    --audio resources/test.wav \
    --save service_ws_test \
    --audio-id test.wav
```

Command-line options:

| Flag                 | Env var        | Default                                       | Description                                                        |
| -------------------- | -------------- | --------------------------------------------- | ------------------------------------------------------------------ |
| `--uri` / `-u`       | `ASR_WS_URI`   | `ws://localhost:8272/asr_stream_api_v1`       | WebSocket endpoint to connect to.                                  |
| `--audio` / `-a`     | —              | built-in sample path                          | Input audio file (WAV, 16 kHz mono recommended).                   |
| `--save` / `-s`      | —              | `service_ws_test`                             | File to append the final transcript to.                            |
| `--audio-id`         | —              | basename of `--audio`                         | Identifier written next to the result in `--save`.                 |

## Supported Languages

R2T2 is optimized for streaming recognition in Chinese and English. Beyond these primary languages, it retains useful cross-lingual streaming capability on languages such as French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish, Arabic, etc.

## Community & Contact

Join our community to ask questions, share ideas, and connect with other users and developers.

### WeChat Group

Scan the QR code below to join our WeChat group:

<img src="https://raw.githubusercontent.com/netease-youdao/Confucius4-R2T2/refs/heads/master/resources/wechat-qrcode.png" alt="WeChat group QR code" width="200">

### Discord Server

[Join our Discord server](https://discord.gg/GfhaWkCyb)

### Business contact

For high-concurrency, production-grade, domestically deployable, or private deployment solutions, as well as business inquiries and partnership opportunities, please feel free to contact us through the channels below.

- **Phone:** +86 010-82558901
- **Email:** [AIcloud_Business@corp.youdao.com](mailto:AIcloud_Business@corp.youdao.com)

### GitHub Issues

We also welcome discussions in this repository’s [Issues](https://github.com/netease-youdao/Confucius4-R2T2/issues) section. Feel free to ask questions, report bugs, or suggest improvements!

---

## Acknowledgements

We sincerely thank the Alibaba Qwen team for open-sourcing the [Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR) modeling code, which provides the architectural foundation for R2T2.

## Citation

If you use this repository or the R2T2 checkpoint in your research, please cite **Confucius4-R2T2** (this project):

```bibtex
@misc{Confucius4-R2T2,
  title        = {Confucius4-R2T2: A Low Latency and High Accuracy Real-Time Speech Recognition Model},
  author       = {NetEase Youdao},
  year         = {2026},
  howpublished = {https://github.com/netease-youdao/Confucius4-R2T2}
}
```

## License

R2T2 uses **dual licensing** to distinguish the source code from the model weights:

- **Code** in the accompanying GitHub repository is released under the [Apache License 2.0](https://github.com/netease-youdao/Confucius4-R2T2/blob/master/LICENSE) and is free to use, modify, and redistribute (including commercially) under the terms of that license.
- **Model weights** are released under the [NetEase Model Use License Agreement](https://github.com/netease-youdao/Confucius4-R2T2/blob/master/MODEL_LICENSE).
