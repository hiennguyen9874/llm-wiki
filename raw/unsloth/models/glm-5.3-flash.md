# GLM-5.3-Flash: How to Run Locally

Run the new GLM-5.3-Flash aka ox-alpha model by Z.ai.

GLM-5.3-Flash, also known as **`ox-alpha`**, is Z.ai’s new 320B parameter (18B active) multimodal open model which **outperforms** [GLM-5.2](/docs/models/glm-5.2.md). GLM-5.3-Flash is the smaller version of [GLM-5.3](/docs/models/glm-5.3.md) and rivals **Claude Opus 4.8** on coding and agentic benchmarks. You can now run the 1-bit model locally on 102GB RAM/VRAM or 3-bit on 128GB setups via llama.cpp or [Unsloth](https://github.com/unslothai/unsloth). Thank you Z.ai for day-zero access.

Unsloth dynamic **1-bit** (93GB) GGUFs retains **71% of top-1% accuracy** whilst being **85% smaller** vs BF16 (642GB). Dynamic 3-bit is 76% smaller and retains 87% accuracy.

​​<a href="/pages/0rzkFBbEB4pMiyscrTYW#run-glm-5.3-flash-ox-alpha-locally" class="button primary">Run GLM-5.3-Flash Guide</a><a href="https://unsloth.ai/download" class="button secondary">Download Unsloth</a>

{% hint style="success" %}
**Sep 4:** GLM-5.3-Flash now runs with [**3.3x faster inference**](#faster-inference-and-mtp-support)**!**
{% endhint %}

{% columns %}
{% column width="50%" %}
GLM-5.3-Flash was trained on 30T tokens and is built on a newly trained base model. Its hybrid sparse and linear attention architecture lowers long-context serving costs without sacrificing accuracy.

You can now run the model directly in [Unsloth Desktop](#run-glm-5.3-flash-in-unsloth).
{% endcolumn %}

{% column width="50%" %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FqPVJA6BHcCJIkQQrDvpD%2FScreenshot%202026-08-27%20at%207.38.11%E2%80%AFAM.png?alt=media&amp;token=576a6810-3f32-4e4c-a0d8-8a84cb733a52" alt=""><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

### :gear: Usage Guide

#### GLM-5.3-Flash Requirements:

The smallest 1-bit quant works on 100GB RAM while 3-bit works on 128GB devices like a Mac or NVIDIA DGX Spark.\
**Table: Hardware requirements** (units = total memory: RAM + VRAM, or unified memory)

| 1-bit  | 2-bit  | 3-bit      | 4-bit      | 8-bit  | BF16   |
| ------ | ------ | ---------- | ---------- | ------ | ------ |
| 100 GB | 115 GB | 128-150 GB | 162-210 GB | 350 GB | 650 GB |

### Recommended Settings

GLM-5.3-Flash has **3 thinking modes**: Low, High, and Max. Use Max Thinking for complicated tasks. In [Unsloth](#run-glm-5.2-in-unsloth-studio), you can easily select Low, High, or Max Thinking with a toggle in the chat area.

Use these settings for most use cases:

| Default Settings (Most Tasks) | DeepSWE              |
| ----------------------------- | -------------------- |
| `temperature` = 1.0           | `temperature` = 0.95 |
| `top_p` = 0.95                | `top_p` = 1.0        |

* **Maximum context window:** `1,048,576`.

#### Changing reasoning effort

GLM-5.3-Flash uses Max reasoning by default. It also supports reasoning efforts where `reasoning_effort` can be "low", "high", or "max".

### Faster Inference & MTP Support

As of Sep 4, we’ve added several improvements and optimizations to our day-zero [llama.cpp PR](https://github.com/ggml-org/llama.cpp/pull/27754). We implemented faster decoding pat plus bonus MTP support, enabling up to **3.3× faster inference** at long context lengths!

Everything works out of the box in [Unsloth Desktop](#run-glm-5.3-flash-in-unsloth), simply update to the latest version if needed. No additional modules or MTP files are required. Alternatively, you can follow our [llama.cpp](#run-glm-5.3-flash-in-llama.cpp) guide.

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FRKSzhmcluWnoNwUxFS40%2Fimage.png?alt=media&amp;token=872cd9b0-e968-4a0d-977c-5315d0ca3e49" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F2tUYioUQhnyCv1pJTfld%2Fimage.png?alt=media&amp;token=b8bfd0de-22c8-4f30-8bfd-36656ae3c16e" alt=""><figcaption></figcaption></figure></div>

Using GLM-5.3-Flash UD-IQ1\_S on 1xB200 and disregarding MTP first, we get:

| Test         | Baseline tok/s | Optimized tok/s |
| ------------ | -------------: | --------------: |
| pp512        |        1121.80 |          1122.0 |
| tg32         |          62.79 |           63.10 |
| tg32 @ 4096  |          53.52 |           59.50 |
| tg32 @ 16384 |          41.02 |           57.99 |
| tg32 @ 65536 |          20.66 |           48.99 |

Then once we add MTP, we see even larger payoffs especially for longer contexts. However we should stop at around n=2 as more draft tokens makes inference slower.

| prompt | MTP off |  n=2 |  n=3 |  n=5 |
| ------ | ------: | ---: | ---: | ---: |
| 4096   |    58.6 | 86.5 | 80.2 | 63.7 |
| 16K    |    55.0 |      | 77.2 |      |

For shorter context lengths, we still see speedups, albeit up to 1.6x faster.

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FmX36IJYj83OgfeQbCjh5%2Fimage.png?alt=media&amp;token=56e0ea43-df0b-47c4-8551-849921ef3913" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FCebn6JiIDQpQMSOz8nIX%2Fimage.png?alt=media&amp;token=1f76ea17-4970-45ae-b92e-3abce29628d7" alt=""><figcaption></figcaption></figure></div>

### 📈 Quantization Analysis

We quantized GLM-5.3-Flash down to UD-IQ1\_S 1bit (93.09GB) and it retains 71% of top-1% accuracy whilst being 85% smaller vs BF16 (641.64GB)

Dynamic 2-bit UD-Q2\_K\_XL is 109GB, is 83% smaller and retains 78% of accuracy.\
Dynamic 3-bit UD-IQ3\_XXS is 120GB, is 81% smaller and retains 82% of accuracy.\
Dynamic 4-bit UD-Q4\_K\_XL is 200GB, is 69% smaller and retains 93% of accuracy.

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FHB3bFxI8Cm3IOw3CRzvR%2Fglm53_flash_dynamic_ggufs_top1_accuracy_new_data.png?alt=media&amp;token=49882cca-1643-4e81-ad64-9d53c75ab93a" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FthGU2pMvyHLSsnOal90W%2Fglm53_flash_dynamic_ggufs_kld_benchmarks_new_data.png?alt=media&amp;token=204f70ee-cae2-4a63-b958-d4ec515f4ce3" alt=""><figcaption></figcaption></figure></div>

| Quant        | size   | top-1 acc | mean KLD | KLD 99.9% |
| ------------ | ------ | --------- | -------- | --------- |
| UD-IQ1\_S    | 93.09  | 70.89%    | 0.669714 | 9.1658    |
| UD-IQ1\_M    | 97.58  | 73.06%    | 0.572413 | 8.5069    |
| UD-IQ2\_XXS  | 101.84 | 76.30%    | 0.450148 | 7.5764    |
| UD-Q2\_K\_XL | 108.72 | 78.34%    | 0.380134 | 6.8412    |
| UD-IQ3\_XXS  | 120.37 | 81.63%    | 0.283772 | 5.9611    |
| UD-Q3\_K\_XL | 147.54 | 86.25%    | 0.159697 | 4.0281    |
| UD-IQ4\_XS   | 156.82 | 88.18%    | 0.116652 | 3.1014    |
| UD-Q4\_K\_XL | 199.71 | 92.22%    | 0.049294 | 1.4894    |
| UD-Q5\_K\_XL | 240.31 | 94.35%    | 0.027052 | 0.8696    |
| UD-Q6\_K\_XL | 291.83 | 95.23%    | 0.019007 | 0.6267    |

## Run GLM-5.3-Flash (Ox-Alpha) Locally

You can now run GLM-5.3-Flash (Ox-Alpha) in Unsloth Desktop and llama.cpp with our [specific PR](https://github.com/ggml-org/llama.cpp/pull/27754). We are using 3-bit `UD-IQ3_XXS` in our demos as it fits on 128GB devices. Feel free to change quantization type.

* Hugging Face: [GLM-5.3-Flash-GGUF](https://huggingface.co/unsloth/GLM-5.3-Flash-GGUF)

<a href="/pages/0rzkFBbEB4pMiyscrTYW#run-glm-5.3-flash-in-unsloth" class="button primary">Run in Unsloth Desktop</a><a href="/pages/0rzkFBbEB4pMiyscrTYW#run-glm-5.3-flash-in-llama.cpp" class="button secondary">Run in llama.cpp</a>

### 🦥 Run GLM-5.3-Flash in Unsloth

GLM-5.3-Flash can now run in [Unsloth Desktop](#run-qwen3.8-in-unsloth-desktop), an open-source UI app for local AI. **Unsloth automatically offloads to RAM and detects multiGPU setups**. With Unsloth Desktop, you can run models locally on **MacOS, Windows**, Linux and:

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

#### Search and download GLM-5.3-Flash

Go to [Unsloth Chat](/docs/new/studio/chat.md) or Model hub and search for GLM-5.3-Flash in the search bar and download your desired model and quant.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FvOQkVli16S26FygKi2gw%2FScreenshot%202026-08-27%20at%204.18.11%E2%80%AFAM.png?alt=media&amp;token=df7914de-597e-43b9-8147-d568ccca0a51" alt=""><figcaption></figcaption></figure>
{% endstep %}

{% step %}

#### Run GLM-5.3-Flash

Inference parameters should be auto-set when using Unsloth, however you can still change it manually. You can also edit the context length, chat template and other settings.

For more information, you can view our [Unsloth inference guide](/docs/new/studio/chat.md). 1-bit running below:

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FwmOvZRaD61XCmMDBlHOD%2FScreenshot%202026-08-27%20at%207.08.52%E2%80%AFAM.png?alt=media&amp;token=4980f172-4323-43a0-9338-fe0e2ca749b6" alt=""><figcaption></figcaption></figure>
{% endstep %}

{% step %}

#### Serve GLM-5.3-Flash with Unsloth API

You can use `unsloth run` command and serve GLM-5.3-Flash via an API using `llama-server` runtime flags, including context sizing, GPU layers, threading, sampling, networking, and tool configuration. For more info see our [API docs](/docs/basics/api.md) or [unsloth start](/docs/integrations/unsloth-start.md).

{% code overflow="wrap" %}

```bash
unsloth run --model unsloth/GLM-5.3-Flash-GGUF:UD-IQ3_XXS
```

{% endcode %}
{% endstep %}

{% step %}

#### Unsloth is now ready

You can also do many other things with GLM-5.3-Flash via Unsloth Desktop like:

* **Connect tools:** [Claude Code](/docs/basics/claude-code.md), [Codex](/docs/basics/codex.md), [web search](/docs/new/studio/chat.md#advanced-web-search), [MCP](/docs/basics/mcp.md) and more
* **Train models:** Fine-tune text, diffusion, [embedding](/docs/basics/embedding-finetuning.md), and more
* **Generate media:** Create and train [images](/docs/basics/diffusion-image.md), video, [TTS](/docs/basics/text-to-speech-tts-fine-tuning.md) locally

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FNYiWxq5OX7NdPoqxp2Hu%2FScreenshot%202026-08-27%20at%2011.59.01%E2%80%AFPM.png?alt=media&amp;token=d9311caa-6935-47b3-a767-5c48e92b7c25" alt=""><figcaption></figcaption></figure>
{% endstep %}
{% endstepper %}

### :llama: Run GLM-5.3-Flash in llama.cpp

{% stepper %}
{% step %}
We need to use our specific llama.cpp PR [here](https://github.com/unslothai/llama.cpp/pull/61). You can follow the build instructions below as well. Change `-DGGML_CUDA=ON` to `-DGGML_CUDA=OFF` if you don't have a GPU or just want CPU inference. **For Apple Mac / Metal devices**, set `-DGGML_CUDA=OFF` then continue as usual - Metal support is on by default.

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone --branch glm5next/upstream https://github.com/unslothai/llama.cpp
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
hf download unsloth/GLM-5.3-Flash-GGUF \
    --local-dir unsloth/GLM-5.3-Flash-GGUF \
    --include "*UD-IQ3_XXS*" # Use "*IQ2_XXS*" for 2-bit
```

{% endcode %}
{% endstep %}

{% step %}
Then to run it:

{% code overflow="wrap" %}

```bash
./llama.cpp/llama-cli \
    --model unsloth/GLM-5.3-Flash-GGUF/UD-IQ3_XXS/GLM-5.3-Flash-UD-IQ3_XXS-00001-of-00004.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --chat-template-kwargs '{"reasoning_effort":"max"}'
```

{% endcode %}

Replace `UD-IQ3_XXS` with your preferred quant, such as `IQ2_XXS` for 2-bit once uploaded.
{% endstep %}
{% endstepper %}

## 📊 Benchmarks

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FfxF1H1wdQe3vKBepuhdA%2Fimage.png?alt=media&amp;token=b6e590cc-fafb-43b3-8e8b-0b318200cbcb" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FUy73TYPneV9NarmiUgJZ%2Fimage.png?alt=media&amp;token=8b344785-cb9b-4c61-bf55-4fdc77be1d0a" alt=""><figcaption></figcaption></figure></div>

| Benchmark                               | GLM-5.3-Flash | GLM-5.2 | DeepSeek-V4-Vision-Exp | Opus 4.8 | GPT-5.6 Terra | Gemini 3.7 Flash |
| --------------------------------------- | ------------- | ------- | ---------------------- | -------- | ------------- | ---------------- |
| Coding                                  |               |         |                        |          |               |                  |
| Terminal Bench 2.1                      | 84.3          | 81.0    | 83.9                   | 85.0     | 87.4          | 85.8             |
| <p>DeepSWE</p><p>v1.1</p>               | 63.4          | 46.2    | 59.3                   | 58.0     | 69.6          | 65.3             |
| NL2Repo                                 | 56.3          | 48.9    | 57.7                   | 69.7     | -             | -                |
| Agentic                                 |               |         |                        |          |               |                  |
| Toolathlon Verified                     | 78.4          | 59.9    | 75.9                   | 76.2     | 74.9          | -                |
| <p>AutomationBench</p><p>v1.0.6</p>     | 48.8          | 26.2    | 38.8                   | 41.0     | 37.2          | 52.3             |
| Agents' Last Exam                       | 26.3          | 20.4    | 27.3                   | 27.0     | 28.0          | -                |
| HLE w/ Tools                            | 55.3          | 54.7    | 55.1                   | 57.9     | -             | -                |
| GDPval-AA v2                            | 1773          | 1504    | 1675                   | 1582     | 1571          | 1527             |
| Vision                                  |               |         |                        |          |               |                  |
| OfficeQA Pro                            | 62.4          | -       | 57.9                   | 48.9     | -             | -                |
| <p>CharXiv Reasoning</p><p>w/ Tools</p> | 89.4          | -       | 80.4                   | 89.9     | 88.0          | 88.7             |
| <p>Chartography</p><p>w/ Tools</p>      | 78.0          | -       | 64.3                   | 75.0     | 68.0          | 65.0             |
| BabyVision                              | 53.4          | -       | 35.1                   | 46.8     | 61.6          | 70.9             |
| MVbench                                 | 77.8          | -       | 69.4                   | 67.1     | 75.0          | 82.2             |
| MMVU                                    | 80.5          | -       | 72.7                   | 67.4     | 75.8          | 82.3             |
