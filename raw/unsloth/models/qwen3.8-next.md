# Qwen3.8-Flash-Next: How to Run Locally

Guide to run Qwen3.8-Flash-Next locally.

Qwen3.8-Flash-Next is a new open-weight, **125B parameter** MoE multimodal model from Qwen. Built on the new Qwen4 architecture, it supports a 262K context window and advanced reasoning. [Qwen3.8](/docs/models/qwen3.8.md)-Flash-Next outperforms Claude-4.6-Opus (Max) and can run locally on devices with **75GB RAM**/unified memory with no GPU VRAM required. To run the model, use our [GGUFs](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF) via llama.cpp or [Unsloth Desktop](/docs/desktop.md). Thank you Qwen for day zero access.

{% columns %}
{% column %}
**1-bit is 75GB** and uses 4-bit for the Ngram / PLE. This is **79% smaller** than BF16 (355GB), and retains a **top-1% accuracy of 80%**.

<a href="/pages/Ef8lrnBt1lmETOqIFCHj#run-qwen3.8-flash-next-in-unsloth" class="button primary">Run Qwen3.8-Flash</a><a href="https://unsloth.ai/download" class="button secondary">Download Unsloth</a>

{% hint style="success" %}
[**MTP**](#mtp-guide) is here! Run Qwen3.8-Flash 1.3-1.7x Faster in [Unsloth Desktop](#run-qwen3.8-flash-next-in-unsloth)!
{% endhint %}
{% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F1YneA51oWzaIiwep9H5I%2F1000024423.gif?alt=media&amp;token=40a169cc-12f1-403a-898c-b310f81ff52a" alt=""><figcaption><p>4-bit Qwen3.8-Flash running in Unsloth</p></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

### :gear: Usage Guide

Whether you run **Qwen3.8-Flash-Next** on a CPU with system RAM or on a GPU with VRAM may make relatively little difference. Its unique architecture allows inference using RAM or unified memory to achieve performance closer to that of GPU VRAM than is typical for other models. This makes it particularly well suited to Macs, NVIDIA DGX Spark systems, and other devices with large memory capacities.

You will need at least **75 GB of RAM or unified memory** to run the model. Its smallest 1-bit quantized version is larger than usual because of new Ngram layers or per layer embeddings which is like a lookup table. However, this also means the quantization is less aggressive, allowing the model to retain more of its original accuracy than more heavily quantized models. You can also offload the PLE / Ngram layer to SSD and use mmap which allows less usage of CPU and GPU VRAM.

#### Qwen3.8-Flash-Next Requirements:

The smallest quant works on 75GB RAM so it's best to have a 96GB RAM/unified memory device.\
**Table: Hardware requirements** (units = total memory: RAM + VRAM, or unified memory)

<table><thead><tr><th>1-bit</th><th>2-bit</th><th>3-bit</th><th>4-bit</th><th width="128">5-bit</th><th>8-bit</th><th>BF16</th></tr></thead><tbody><tr><td>75 GB</td><td>79 GB</td><td>90 GB</td><td>96-114 GB</td><td>163 GB</td><td>200 GB</td><td>355 GB</td></tr></tbody></table>

{% hint style="info" %}
If you want to use [MTP](/docs/models/mtp.md) for faster inference, prepare to have 1-2GB extra headroom.
{% endhint %}

### Recommended Settings

Qwen3.8-Flash-Next is a **hybrid thinking** model with different default settings for thinking and non-thinking modes. Extra high is enabled by default so if you want shorter thinking traces, you can [adjust the thinking effort](#thinking--preserve-thinking):

| Parameter            | Thinking Mode | Instruct (non-thinking) Mode |
| -------------------- | ------------- | ---------------------------- |
| `temperature`        | 1.0           | 0.7                          |
| `top_p`              | 0.95          | 0.80                         |
| `top_k`              | 20            | 20                           |
| `min_p`              | 0.0           | 0.0                          |
| `presence_penalty`   | 0.0           | 1.5                          |
| `repetition_penalty` | 1.0           | 1.0                          |

* Context length = up to `262,144`
* Thinking Mode: `temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`
* Instruct (or non-thinking) mode: `temperature=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`

### 💡 Thinking + Preserve Thinking

{% columns %}
{% column %}
Qwen3.8-Flash-Next has **Preserve Thinking** which leaves the thinking trace from the previous conversation. This increases the number of tokens you use, but could increase accuracy in continued conversations. [Unsloth](#run-qwen3.8-in-unsloth-desktop) has 'Think' and Preserved Thinking toggles for Qwen3.8 (see right):
{% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FLdgmjRrb5qhpbY9PwYe8%2FScreenshot%202026-08-14%20at%2011.26.15%E2%80%AFAM.png?alt=media&amp;token=6333f5ca-196d-46ae-9efd-2e522014e6db" alt=""><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

Qwen3.8-Flash-Next comes with support for `reasoning_effort`, which can be used to adjust reasoning depth and control cost. These toggles are automatically enabled in Unsloth:

* `xhigh` (default): for complex tasks demanding thorough analysis
* `medium`: balancing accuracy and speed
* `low`: efficient reasoning optimizing for speed and cost
* none

{% hint style="warning" %}
To change[ thinking / reasoning](#how-to-enable-or-disable-reasoning-and-thinking) effort in `unsloth run` or `llama-server`, use `--chat-template-kwargs '{"reasoning_effort":"medium"}'`

If you're on **Windows** Powershell, use: `--chat-template-kwargs "{\"reasoning_effort\":\"medium\"}"`

Change `medium` to your desired reasoning level.
{% endhint %}

### Quantization Analysis

We ran KLD for Qwen3.8-Flash quants, and show that 80% top-1% accuracy recovery is possible with 79% less disk space usage. The new architecture uses PLE / Ngrams, and these are not quantized that heavily (4-bit minimum) since they have random access pattern, and quantizing them heavily will damage the model.

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FPemX6jyt4OWohwHfcjqo%2Fqwen38_flash_unsloth_top1_accuracy_new_data.png?alt=media&amp;token=3fd7713b-e9d9-43d4-bbca-96d56df43a80" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F8bGa4A4jbGsn0qrNY6Gc%2Fqwen38_flash_unsloth_kld_new_data.png?alt=media&amp;token=45ac0e9a-c9b3-4530-90f6-ed8a2328ef08" alt=""><figcaption></figcaption></figure></div>

| quant        | GB    | top-1 % | mean KLD | 99.9% KLD |
| ------------ | ----- | ------- | -------- | --------- |
| UD-IQ1\_S    | 72.5  | 77.325  | 0.396070 | 7.2126    |
| UD-IQ1\_M    | 74.5  | 79.691  | 0.314739 | 6.1965    |
| UD-Q2\_K\_XL | 78.9  | 82.715  | 0.224607 | 4.9121    |
| UD-IQ3\_XXS  | 82.0  | 85.414  | 0.165120 | 4.0375    |
| UD-Q3\_K\_XL | 90.0  | 88.315  | 0.106504 | 3.0538    |
| UD-IQ4\_XS   | 93.7  | 89.554  | 0.083630 | 2.3677    |
| UD-Q4\_K\_XL | 111.3 | 92.255  | 0.046893 | 1.5468    |
| UD-Q5\_K\_XL | 158.3 | 93.680  | 0.030415 | 1.0036    |
| UD-Q6\_K\_XL | 169.2 | 94.089  | 0.027091 | 0.8416    |
| Q8\_0        | 188.2 | 94.122  | 0.026574 | 0.8118    |

## Run Qwen3.8-Flash-Next Guide

You can now run Qwen3.8-Flash-Next in Unsloth Desktop and llama.cpp. Feel free to change quantization type.

* Hugging Face: [Qwen3.8-Flash-Next-**GGUF**](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF)
* ModelScope: [Qwen3.8-Flash-Next-GGUF](https://www.modelscope.cn/models/unsloth/Qwen3.8-Flash-Next-GGUF)

<a href="/pages/CLyZKmpoJZpdaJXhLW4v#run-qwen3.8-in-unsloth-desktop" class="button primary">Run in Unsloth Desktop</a><a href="/pages/CLyZKmpoJZpdaJXhLW4v#run-qwen3.8-in-llama.cpp" class="button secondary">Run in llama.cpp</a><a href="/docs/models/qwen3.8-next.md#mtp-guide" class="button primary">MTP Guide</a>

{% hint style="success" %}
Qwen3.8-Flash-Next is now available to run locally in [Unsloth Desktop](#run-qwen3.8-flash-next-in-unsloth)!
{% endhint %}

### 🦥 Run Qwen3.8-Flash-Next in Unsloth

Qwen3.8-Flash-Next now is able to run in [Unsloth Desktop](#run-qwen3.8-in-unsloth-desktop), an open-source UI app for local AI. **Unsloth automatically offloads to RAM and detects multiGPU setups**. With Unsloth Desktop, you can run models locally on **MacOS, Windows**, Linux and:

{% columns %}
{% column %}

* Search, download, [run GGUFs](/docs/new/studio.md#run-models-locally), MLX and safetensor models
* [**Self-healing** tool calling](/docs/new/studio/chat.md#auto-healing-tool-calling) + **web search**
* [**Code execution**](/docs/desktop.md#code-execution) (Python, Bash)
* [Automatic inference](https://unsloth.ai/docs/desktop#feature-deep-dive) parameter tuning (temp, top-p, etc.)
* Fast CPU + GPU inference via MLX and llama.cpp
* [Train LLMs](/docs/new/studio.md#no-code-training) 2x faster with 70% less VRAM
  {% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F6IXaXdTVyvbrnjehlxys%2Fkimik3.gif?alt=media&amp;token=31e1213b-d7da-46e9-bc7f-3a8c402513fc" alt=""><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

{% stepper %}
{% step %}

#### Install Unsloth

The easiest way to get started is by downloading the [Unsloth Desktop app](/docs/desktop.md). Works on [macOS](/docs/get-started/install/mac.md), [Windows](/docs/get-started/install/windows-installation.md), and [Linux](/docs/get-started/install/linux.md).

<a href="https://unsloth.ai/download" class="button primary" data-icon="down-to-bracket">Download Unsloth</a>

* <i class="fa-apple">:apple:</i> [Download for macOS](https://unsloth.ai/download/mac)
* <i class="fa-windows">:windows:</i> [Download for Windows](https://unsloth.ai/download/windows)
* <i class="fa-linux">:linux:</i> [Download for Linux](https://unsloth.ai/download/linux)

Or, if you prefer to install manually:

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

#### Search and download Qwen3.8-Flash-Next

Go to [Unsloth Chat](/docs/new/studio/chat.md) or Model hub and search for Qwen3.8-Flash in the search bar and download your desired model and quant.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FiEMEgtWrGc0DMZ4FLRez%2FScreenshot%202026-08-27%20at%204.21.05%E2%80%AFAM.png?alt=media&amp;token=94ad9ccf-f882-48b0-8aaa-83e90bfc2630" alt=""><figcaption></figcaption></figure>
{% endstep %}

{% step %}

#### Run Qwen3.8-Flash-Next

MTP is automatically enabled bit you can disable it. Inference parameters should be auto-set when using Unsloth, however you can still change it manually. You can also edit the context length, chat template and other settings.

For more information, you can view our [Unsloth inference guide](/docs/new/studio/chat.md).

For example using Unsloth Desktop with the 397GB Qwen3.8 (-91% smaller) allows you to toggle thinking modes, allow inline canvas, web search and code execution and much more.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F1YneA51oWzaIiwep9H5I%2F1000024423.gif?alt=media&amp;token=40a169cc-12f1-403a-898c-b310f81ff52a" alt=""><figcaption></figcaption></figure>
{% endstep %}

{% step %}

#### Serve Qwen3.8-Flash-Next with Unsloth API

You can use `unsloth run` command and serve Qwen3.8 via an API using `llama-server` runtime flags, including context sizing, GPU layers, threading, sampling, networking, and tool configuration. For more info see our [API docs](/docs/basics/api.md) or [unsloth start](/docs/integrations/unsloth-start.md).

{% code overflow="wrap" %}

```bash
unsloth run --model unsloth/Qwen3.8-Flash-Next-GGUF:UD-Q4_K_XL
```

{% endcode %}
{% endstep %}

{% step %}

#### Unsloth is now ready

You can also do many other things with Qwen3.8-Flash-Next via Unsloth Desktop like:

* **Connect tools:** [Claude Code](/docs/basics/claude-code.md), [Codex](/docs/basics/codex.md), [web search](/docs/new/studio/chat.md#advanced-web-search), [MCP](/docs/basics/mcp.md) and more
* **Train models:** Fine-tune text, diffusion, [embedding](/docs/basics/embedding-finetuning.md), and more
* **Generate media:** Create and train [images](/docs/basics/diffusion-image.md), video, [TTS](/docs/basics/text-to-speech-tts-fine-tuning.md) locally

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FRnU2breyPzalRzIHyq8U%2FScreenshot%202026-08-28%20at%2012.12.20%E2%80%AFAM.png?alt=media&amp;token=da925810-e1d3-4c06-bf27-7caad15a2330" alt=""><figcaption></figcaption></figure>
{% endstep %}
{% endstepper %}

### :llama: Run Qwen3.8-Flash-Next in llama.cpp

{% stepper %}
{% step %}
Install the latest version of llama.cpp. You can follow the build instructions below as well. Change `-DGGML_CUDA=ON` to `-DGGML_CUDA=OFF` if you don't have a GPU or just want CPU inference. **For Apple Mac / Metal devices**, set `-DGGML_CUDA=OFF` then continue as usual - Metal support is on by default.

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
To run the model, you can do:

{% code overflow="wrap" %}

```bash
pip install -U "huggingface_hub[cli]"
hf download unsloth/Qwen3.8-Flash-Next-GGUF \
    --local-dir unsloth/Qwen3.8-Flash-Next-GGUF \
    --include "*UD-Q4_K_XL*" # Use "*IQ2_XXS*" for 2-bit
```

{% endcode %}
{% endstep %}

{% step %}
Then to run it:

{% code overflow="wrap" %}

```bash
./llama.cpp/llama-cli \
    --model unsloth/Qwen3.8-Flash-Next-GGUF/UD-IQ1_S/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.0
```

{% endcode %}
{% endstep %}
{% endstepper %}

### MTP Guide

Qwen3.8-Flash can run with 1.3 to **1.7x faster inference** via [MTP](/docs/models/mtp.md) (Multi-Token Prediction) with no accuracy degradation! MTP enables Qwen3.8-Flash to reach **170 tokens/s** on 1x RTX 6000 PRO GPU compared to the 100 token baseline. MTP speeds up inference by letting a model predict multiple upcoming tokens at once instead of generating one token per step, and is especially effective on GPUs.

To run Qwen3.8-Flash with MTP, MTP is enabled by default in [Unsloth Desktop](#run-qwen3.8-flash-next-in-unsloth) or you can use our custom llama.cpp PR.

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F39BmPdGOL8IlwrdQFsGh%2Fqwen38_flash_next_unsloth_ggufs_mtp_speedup_no_mtp.png?alt=media&amp;token=77c52179-821a-406b-a5ab-fd027ebe8d30" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FF9IF8IWG2DAgfLBXzhyz%2Fqwen38_flash_next_unsloth_ggufs_mtp_decode_tokens_per_s.png?alt=media&amp;token=def0f8fb-5268-4e33-9e85-0a1fed4a1156" alt=""><figcaption></figcaption></figure></div>

Gains are smaller on devices with lower memory bandwidth, such as older Macs. We created both shared MTP modules (excludes the embed\_tokens and shares it with the main model) to save disk space, RAM and VRAM usage by around 1 to 2GB.

| MTP Type | General MTP | Shared MTP | Savings |
| -------- | ----------- | ---------- | ------- |
| BF16     | 7.77 GB     | 5.23 GB    | 2.54 GB |
| Q8\_0    | 4.14 GB     | 2.79 GB    | 1.35 GB |
| Q4\_K\_M | 2.79 GB     | 1.91 GB    | 880 MB  |

The 3-bit MTP quant works on 91GB RAM so it's best to have a 96GB RAM/unified memory device.\
**Table: MTP Hardware requirements** (units = total memory: RAM + VRAM, or unified memory)

<table><thead><tr><th>1-bit</th><th>2-bit</th><th>3-bit</th><th>4-bit</th><th width="128">5-bit</th><th>8-bit</th><th>BF16</th></tr></thead><tbody><tr><td>76 GB</td><td>80 GB</td><td>91 GB</td><td>97-115 GB</td><td>164 GB</td><td>200 GB</td><td>355 GB</td></tr></tbody></table>

#### Run MTP Qwen3.8-Flash

To run Qwen3.8-Flash with MTP, all you need to do is [**install Unsloth Desktop**](#run-qwen3.8-flash-next-in-unsloth) or update to the latest verison of Unsloth then re-download the model or download the MTP file. See further below for llama.cpp instructions.

{% columns %}
{% column %}
Unsloth Desktop Works on [macOS](/docs/get-started/install/mac.md), [Windows](/docs/get-started/install/windows-installation.md), and [Linux](/docs/get-started/install/linux.md).

<a href="https://unsloth.ai/download" class="button primary" data-icon="down-to-bracket">Download Unsloth</a>

* <i class="fa-apple">:apple:</i> [Download for macOS](https://unsloth.ai/download/mac)
* <i class="fa-windows">:windows:</i> [Download for Windows](https://unsloth.ai/download/windows)
* <i class="fa-linux">:linux:</i> [Download for Linux](https://unsloth.ai/download/linux)

In Unsloth Desktop, you can also change the number of draft tokens or customize MTP. Use the advanced settings in the right sidebar, and enable "Advanced settings" and you can select MTP / Ngram speculative decoding, the number of draft tokens and more:
{% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FqKy281quNOdn5toIr5am%2Fimage.png?alt=media&amp;token=bf0f6f00-1192-4494-977c-1bf4fa346fa0" alt="" width="305"><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

#### MTP Llama.cpp Guide

{% code overflow="wrap" %}

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone --branch qwen4exp/mtp https://github.com/danielhanchen/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

{% endcode %}

Then to download the shared MTP module:

{% code overflow="wrap" %}

```bash
pip install -U "huggingface_hub[cli]"
hf download unsloth/Qwen3.8-Flash-Next-GGUF \
    --local-dir unsloth/Qwen3.8-Flash-Next-GGUF \
    --include "*mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf*"
```

{% endcode %}

And to use llama-server with it:

{% code overflow="wrap" %}

```bash
llama.cpp/llama-server \
    -hf unsloth/Qwen3.8-Flash-Next-GGUF:UD-Q4_K_XL \
    -md unsloth/Qwen3.8-Flash-Next-GGUF/MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf \
    --spec-type draft-mtp --spec-draft-n-max 5
```

{% endcode %}

### 📊 Benchmarks

For GGUF quantization benchmarks you can see above for our [quantization analysis](#quantization-analysis) or [Dynamic V3.0 article](/docs/basics/dynamic-3.0-ggufs.md).

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FJFGDUmmWUvJMD0eCUbiE%2Fqwennextbe.jpg?alt=media&amp;token=0be96d30-9f51-41f3-8e3a-3366a4fdfb93" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FpQBzoQNziZtrFDHCyN3t%2Fbench2max.jpg?alt=media&amp;token=3d6adbe3-6c8b-4cb4-937f-f434ebd7f106" alt=""><figcaption></figcaption></figure></div>
