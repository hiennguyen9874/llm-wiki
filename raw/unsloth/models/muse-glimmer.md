# Muse Glimmer - How to Run Locally

Learn how to run the new Muse Glimmer 30B model from Meta.

Muse Glimmer is Meta’s new open-weight **30B** parameter **dense vision model**, designed for local agentic and coding workflows. It is the first open model from Meta Superintelligence Labs, and is released under the **Apache 2.0** license. This guide covers running Muse Glimmer 30B with **Unsloth Dynamic** quants for maximum performance.

{% columns %}
{% column %}
Muse Glimmer 30B runs locally on **18GB RAM/VRAM** setups, including Mac and GPU/CPU systems. You can **run** or **fine-tune Muse Glimmer with** [**Unsloth**](#unsloth-guide). We collaborated with Meta and Hugging Face on llama.cpp inference implementation. Thank you Meta for providing Unsloth with day-zero support.

<a href="/docs/models/muse-glimmer.md#run-muse-glimmer-tutorials" class="button primary">Run Muse Glimmer Tutorials</a><a href="/docs/models/muse-glimmer/train.md" class="button secondary">Fine-tune Muse Glimmer</a>
{% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fw02045vWPT8A7cDuXSnS%2Fsksdklklds.gif?alt=media&amp;token=8fdd1a6f-733e-4dcc-87d3-a42e0a5bf98d" alt=""><figcaption><p>2-bit Muse Glimmer running in Unsloth</p></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

### Usage Guide

Muse Glimmer can plan multi-step tasks, execute sequential tool calls, recover from failures, adapt as conditions change, use runtime memory, and resume work across long-running sessions when state is persisted. This persistence comes from the agent harness, not the model. With **vision support**, Muse Glimmer is ideal for multimodal workflows.

#### Hardware requirements

Muse Glimmer 30B uses about **58 GB for full precision BF16 weights.** Unsloth Dynamic quants tries to recover as much accuracy as possible through quantization allowing Muse Glimmer 30B to fix on smaller devices like RTX 5090s and so on.

**Table: Muse Glimmer 30B Inference GGUF recommended hardware requirements** (units = total memory: RAM + VRAM, or unified memory).

| 2-bit    | 3-bit    | 4-bit | 6-bit    | 8-bit |
| -------- | -------- | ----- | -------- | ----- |
| 12-14 GB | 14-15 GB | 17 GB | 20-22 GB | 34 GB |

**Detailed requirements table:**

| Quantization                  | Recommended RAM/VRAM: | Hardware examples        |
| ----------------------------- | --------------------- | ------------------------ |
| 2-bit (`UD-Q2_K_XL`)          | 12-14+ GB             | RTX 4080                 |
| 3-bit (`UD-Q3_K_XL`)          | 14-15 GB+             | RTX 4090                 |
| 4-bit (`UD-Q4_K_XL`, `NVFP4`) | 17 GB+                | **Mac 32GB**             |
| 6-bit (`UD-Q6_K_XL`)          | 20-22 GB+             | **RTX 5090, Mac 48GB**   |
| 8-bit (`UD-Q8_K_XL`)          | 34 GB+                | **Mac 128GB, DGX Spark** |
| BF16 (full precision)         | 58 GB+                | **Mac 128GB, DGX Spark** |

{% hint style="info" %}
As a rule of thumb, your total available memory should at least exceed the size of the quantized model you download. If it does not, llama.cpp can still run using partial RAM / disk offload, but generation will be slower. You will also need more compute, depending on the context window you use.
{% endhint %}

#### Recommended Settings

It is recommended to use Meta's default Muse Glimmer parameters:

* `temperature = 1.0`
* `top_p = 0.95`
* `top_k = 64`

Maximum context length: `131,072` (default) up to `262,144`

#### Thinking Settings

Muse Glimmer supports controllable reasoning efforts including:

* low
* medium
* high
* xhigh

## Run Muse Glimmer Tutorials

Because quantized Muse Glimmer 30B comes in several sizes, the recommended starting point for the models is [**Dynamic**](/docs/basics/dynamic-3.0-ggufs.md) **4-bit (UD** . Muse Glimmer 30B[ GGUFs](https://huggingface.co/unsloth/Muse-Glimmer-30B-GGUF).

<a href="/docs/models/muse-glimmer.md#unsloth-guide" class="button primary">🦥 Unsloth Guide</a><a href="/pages/1hXO5DDKxmP1zKUUnBnA#llama.cpp-guide" class="button primary">🦙 Llama.cpp Guide</a>

### 🦥 Unsloth Guide

Muse Glimmer 30B can now be run and fine-tuned in Unsloth Desktop, our new open-source desktop app for local AI. Unsloth lets you run models locally on **MacOS, Windows**, Linux and:

{% columns %}
{% column %}

* Search, download, [run GGUFs](/docs/new/studio.md#run-models-locally) and safetensor models
* [**Self-healing** tool calling](/docs/new/studio.md#execute-code--heal-tool-calling) + **web search**
* [**Code execution**](/docs/new/studio.md#run-models-locally) (Python, Bash)
* [Automatic inference](https://unsloth.ai/docs/desktop#feature-deep-dive) parameter tuning (temp, top-p, etc.)
* Fast CPU + GPU inference via llama.cpp
* [Train LLMs](/docs/new/studio.md#no-code-training) 2x faster with 70% less VRAM
  {% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FCwcXvmLERJSUNF6iNTiY%2Fdeepseek-v4-flash-0731-unsloth-studio.png?alt=media&amp;token=6fdc0216-d21e-42e7-bb57-8e1abf6e7f4f" alt=""><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

{% stepper %}
{% step %}

#### Install Unsloth

**Unsloth runs on** [**macOS**](/docs/get-started/install/mac.md)**,** [**Windows**](/docs/get-started/install/windows-installation.md)**, and** [**Linux**](/docs/get-started/install/linux.md)**.**

<a href="https://unsloth.ai/download" class="button primary" data-icon="down-to-bracket">Download Unsloth</a>

Or, for manual installation:

MacOS, Linux, WSL:

```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```

Windows PowerShell:

```bash
irm https://unsloth.ai/install.ps1 | iex
```

{% endstep %}

{% step %}

#### Launch Unsloth and Search and download Muse Glimmer

On first launch go to the Model hub tab and search for Muse Glimmer in the search bar and download your desired model and quant.
{% endstep %}

{% step %}

#### Run Muse Glimmer

Inference parameters should be auto-set when using Unsloth Desktop, however you can still change it manually. You can also edit the context length, chat template and other settings. You can run GGUFs and MLX files.

For more information, you can view our [Unsloth inference guide](/docs/new/studio/chat.md).

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FfkziNyeYlwSTjrRhQIru%2Fkimik3.gif?alt=media&amp;token=790b6266-65e7-4200-a8e5-11dc23e74678" alt=""><figcaption></figcaption></figure>
{% endstep %}

{% step %}

#### Serve Muse Glimmer with Unsloth API

You can use `unsloth run` command and serve Muse Glimmer via an API using `llama-server` runtime flags, including context sizing, GPU layers, threading, sampling, networking, and tool configuration. For more info see our [API docs](/docs/basics/api.md) or [unsloth start](/docs/integrations/unsloth-start.md).

```bash
unsloth run --model unsloth/Muse-Glimmer-30B-GGUF:UD-Q4_K_XL
```

{% endstep %}

{% step %}

#### Unsloth is now ready

You can also do many other things with Muse Glimmer via Unsloth Desktop like:

* **Connect tools:** [Claude Code](/docs/basics/claude-code.md), [Codex](/docs/basics/codex.md), [web search](/docs/new/studio/chat.md#advanced-web-search), [MCP](/docs/basics/mcp.md) and more
* **Train models:** Fine-tune text, diffusion, [embedding](/docs/basics/embedding-finetuning.md), and more
* **Generate media:** Create and train [images](/docs/basics/diffusion-image.md), video, [TTS](/docs/basics/text-to-speech-tts-fine-tuning.md) locally
  {% endstep %}
  {% endstepper %}

### 🦙 Llama.cpp Guide

For this guide we will be utilizing Dynamic 4-bit for Muse Glimmer 30B. See: [Muse Glimmer 30B collection](https://huggingface.co/collections/unsloth/muse-glimmer)

{% stepper %}
{% step %}
Obtain the latest `llama.cpp` **on** [**GitHub here**](https://github.com/ggml-org/llama.cpp). You can follow the build instructions below as well. Change `-DGGML_CUDA=ON` to `-DGGML_CUDA=OFF` if you don't have a GPU or just want CPU inference. **For Apple Mac / Metal devices**, set `-DGGML_CUDA=OFF` then continue as usual - Metal support is on by default.

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone https://github.com/ggml-org/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

{% endstep %}

{% step %}
If you want to use `llama.cpp` directly to load models, you can follow commands below, according to each model. `UD-Q4_K_XL` is the quantization type. You can also download via Hugging Face (step 3). This is similar to `ollama run` . Use `export LLAMA_CACHE="folder"` to force `llama.cpp` to save to a specific location. There is no need to set context length as llama.cpp automatically uses the exact amount required.

```bash
export LLAMA_CACHE="unsloth/Muse-Glimmer-30B-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/Muse-Glimmer-30B-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64
```

{% endstep %}

{% step %}
You can also download the model manually as well via the code below (after installing `pip install huggingface_hub`). You can choose `UD-Q4_K_XL` or other quantized versions like `Q8_0` . If downloads get stuck, see: [Hugging Face Hub, XET debugging](/docs/basics/troubleshooting-and-faqs/hugging-face-hub-xet-debugging.md)

```bash
hf download unsloth/Muse-Glimmer-30B-GGUF \
    --local-dir unsloth/Muse-Glimmer-30B-GGUF \
    --include "*mmproj-BF16*" \
    --include "*UD-Q4_K_XL*" # Use "*UD-Q2_K_XL*" for Dynamic 2bit
```

{% endstep %}

{% step %}
Then run the model in conversation mode (with vision `mmproj-F16`):

{% code overflow="wrap" %}

```bash
./llama.cpp/llama-cli \
    --model unsloth/Muse-Glimmer-30B-GGUF/Muse-Glimmer-30B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Muse-Glimmer-30B-GGUF/mmproj-BF16.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64
```

{% endcode %}
{% endstep %}

{% step %}

#### Llama-server deployment

To deploy Muse Glimmer 30B on llama-server, use:

```bash
./llama.cpp/llama-server \
    --model unsloth/Muse-Glimmer-30B-GGUF/Muse-Glimmer-30B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Muse-Glimmer-30B-GGUF/mmproj-BF16.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64 \
    --alias "unsloth/Muse-Glimmer-30B-GGUF" \
    --port 8001
```

{% endstep %}
{% endstepper %}

### :wrench: Fine-tune

You can now fine-tune Meta’s Muse Glimmer-30B with [Unsloth](https://github.com/unslothai/unsloth) on a **24GB card**! Muse Glimmer is a 30B parameter multimodal agentic model optimized for local deployment.

We provide multiple Kaggle notebooks which provide 30 hours for free with 2x Tesla T4 GPUs!

{% columns %}
{% column %}
Muse Glimmer Vision Kaggle

{% embed url="<https://www.kaggle.com/notebooks/welcome?src=https://github.com/unslothai/notebooks/blob/main/nb/Kaggle-Muse_Glimmer_(30B)-Vision.ipynb&accelerator=nvidiaTeslaT4>" %}
{% endcolumn %}

{% column %}
Muse Glimmer Conversational Kaggle

{% embed url="<https://www.kaggle.com/notebooks/welcome?src=https://github.com/unslothai/notebooks/blob/main/nb/Kaggle-Muse_Glimmer_(30B)-Conversational.ipynb&accelerator=nvidiaTeslaT4>" %}
{% endcolumn %}
{% endcolumns %}

### Benchmarks

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FlBA3dI7za973jBKMKT8D%2FScreenshot%202026-08-10%20at%202.28.04%E2%80%AFAM.png?alt=media&amp;token=c80b2746-dedc-4bac-bf17-645b3368599d" alt=""><figcaption></figcaption></figure>

| Category                             | Benchmark                          |                     Muse Glimmer-30B High Reasoning                    |                        Gemma4-31B Thinking Mode                        |                   Qwen3.6-27B Thinking Mode                   |
| ------------------------------------ | ---------------------------------- | :--------------------------------------------------------------------: | :--------------------------------------------------------------------: | :-----------------------------------------------------------: |
| *General Agentic*                    | MCP Atlas (Public)                 |                                **75.5**                                |                                  54.2                                  |                              62.5                             |
|                                      | DeepSearch QA                      |                                **74.6**                                |                                  61.7                                  |                              71.1                             |
|                                      | 𝛕3-Banking                        |                                **23.5**                                |                                  15.1                                  |                              16.7                             |
|                                      | WildClawBench                      |                                **47.6**                                |                                  37.6                                  |                              43.2                             |
|                                      | GDPVal-AA v2                       |                                   953                                  |                                   811                                  |                            **1141**                           |
|                                      | Gaia2                              |                                **43.3**                                |                                  36.4                                  |                              40.0                             |
|                                      | SkillsBench (with skills)          |                                  44.3                                  |                                  32.4                                  |                            **46.6**                           |
|                                      | OSWorld-Verified                   |                                  65.9                                  |                                  58.5                                  |                            **75.6**                           |
| *Agentic Coding*                     | SWE-Bench Pro                      |                                **51.2**                                |                                  36.9                                  |                              50.2                             |
|                                      | SWE-Bench Verified                 |                                  76.0                                  |                                  66.6                                  |                            **77.2**                           |
|                                      | TerminalBench 2.1 (with terminus2) |                                  51.7                                  |                                  43.4                                  |                            **60.7**                           |
|                                      | SciCode                            |                                **43.6**                                |                                  43.4                                  |                              39.8                             |
| *Multimodal*                         | Charxiv Reasoning                  |                                **78.8**                                |                                  77.7                                  |                              78.4                             |
|                                      | ScreenSpot Pro                     |                                  75.4                                  |                                  75.9                                  |                            **76.1**                           |
|                                      | OmniDocBench v1.5                  |                                  75.8                                  |                                  72.5                                  |                            **77.8**                           |
|                                      | MMMU Pro                           |                                   74                                   |                                   73                                   |                             **75**                            |
|                                      |                                    |                                                                        |                                                                        |                                                               |
| *Safety*                             | CI Memories                        |              <p>Violation (↓): 26.4<br>Coverage: 64.8</p>              |      <p>Violation (↓): <strong>12.1</strong><br>Coverage: 53.0</p>     | <p>Violation (↓): 53.4<br>Coverage: <strong>66.9</strong></p> |
|                                      | Siren AgentDojo                    | <p>Attack Success Rate (↓): 28.4<br>Utility: <strong>94.2</strong></p> | <p>Attack Success Rate (↓): <strong>25.6</strong><br>Utility: 90.8</p> |     <p>Attack Success Rate (↓): 40.3<br>Utility: 92.7</p>     |
|                                      |                                    |                                                                        |                                                                        |                                                               |
| *General Capabilities and Reasoning* | IFBench                            |                                **77.0**                                |                                  76.0                                  |                              70.8                             |
|                                      | AIME 2026                          |                                **94.7**                                |                                  89.2                                  |                              94.1                             |
|                                      | GPQA Diamond (AA)                  |                                  83.5                                  |                                **85.7**                                |                              84.2                             |
|                                      | HLE Text (AA)                      |                                  22.0                                  |                                **23.6**                                |                              23.1                             |
|                                      | AA-LCR                             |                                **80.0**                                |                                  68.3                                  |                              73.3                             |
|                                      | Beam128K                           |                                **65.1**                                |                                  58.2                                  |                              63.0                             |
