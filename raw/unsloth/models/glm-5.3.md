# GLM-5.3 - How to Run Locally

Run the new GLM-5.3 model by Z.ai.

GLM-5.3 is Z.ai’s new 744B parameter (40B active) model. As of Aug 2026, GLM-5.3 is the **strongest open-model** to date, achieving SOTA on Terminal Bench 3.0 and Agents' Last Exam. GLM-5.3 uses the same base model as [GLM-5.2](/docs/models/glm-5.2.md), with every gain coming from post-training. The model has a **1M context** window and can now run locally via [Unsloth Dynamic](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs) GGUFs with llama.cpp or [Unsloth Desktop](#run-glm-5.3-in-unsloth).

<a href="/docs/models/glm-5.3-flash.md" class="button primary">GLM-5.3-Flash Guide</a><a href="/pages/Vh7nCmycTp5VqtHwO5Cj#run-glm-5.3-tutorials" class="button secondary">GLM-5.3 Guide</a>

{% hint style="info" %}
If you want to run [**GLM-5.3-Flash**](/docs/models/glm-5.3-flash.md), please read our [specific article](/docs/models/glm-5.3-flash.md) for it.
{% endhint %}

Dynamic 1-bit GGUF reaches **\~76%** top-1 accuracy while being **85% smaller**. Dynamic 2-bit reaches **\~81%** accuracy while being **83% smaller**. As GLM-5.3 has same size and arch as GLM-5.2, most requirements / settings are the same. Thanks Z.ai for Unsloth day-zero access. [**GLM-5.3-GGUF**](https://huggingface.co/unsloth/GLM-5.3-GGUF)

### **⚙️ Usage Guide**

The 2-bit dynamic quant `UD-IQ2_M` uses **239GB** of disk space works well on **256GB RAM** devices like a 2x NVIDIA DGX Sparks or a Mac Studio.

The **1-bit** quant will fit on 223GB RAM and 8-bit requires 810GB RAM.

**Table: Inference hardware requirements** (units = total memory: RAM + VRAM, or unified memory)

| 1-bit | 2-bit | 3-bit     | 4-bit     | 6-bit | 8-bit |
| ----- | ----- | --------- | --------- | ----- | ----- |
| 223GB | 245GB | 290-360GB | 372-475GB | 570GB | 810GB |

For best performance, make sure your total available memory, including VRAM and system RAM, exceeds the quantized model file size by a comfortable margin.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FJsaB5Sn5JEJXD40RU06i%2Fglm53_unsloth_dynamic_ggufs_top1_accuracy_updated.png?alt=media&amp;token=ef24f54e-c3a7-461e-aa02-ccb8f654fede" alt=""><figcaption></figcaption></figure>

#### Recommended Settings

GLM-5.3 has **3 thinking modes**: **Low**, **High**, and **Max**. Use Max Thinking for complicated coding tasks. In [Unsloth Desktop](/docs/desktop.md) you can easily toggle Low, High, and Max Thinking with a UI.

Use these settings for most use cases:

| Default Settings (Most Tasks) | Long agentic tasks  |
| ----------------------------- | ------------------- |
| `temperature` = 1.0           | `temperature` = 1.0 |
| `top_p` = 0.95                | `top_p` = 1.0       |

The **maximum context window** is `1,048,576`.

GLM-5.3 uses max reasoning by default and thinking cannot be disabled. `reasoning_effort` can be `low`, `high`, or `max`.

`clear_thinking` is false by default and they recommend true.

For reasoning effort customization (change 'low' to 'high' or 'max'):

```bash
--chat-template-kwargs '{"reasoning_effort":"low"}'
```

For multi-turn chat, use `clear_thinking=true` to remove reasoning from previous turns (recommended for this model):

```bash
--chat-template-kwargs '{"reasoning_effort":"max","clear_thinking":true}'
```

### Chat Template fixes

We found GLM uses an interesting `.{id}.` notation for chat templates, but many engines don't support this. We edited it to all `[id]` so Python list indexing syntax. See this [commit change](https://huggingface.co/unsloth/GLM-5.3/commit/05cd131f7ab554f983b81c6be97916450b0ff8d2) for more details.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F3d64OwoEjqpJ5fHum860%2Fimage.png?alt=media&amp;token=784da534-c703-4246-886d-bd058cf345f1" alt="" width="563"><figcaption></figcaption></figure>

## Run GLM-5.3 Tutorials:

You can now run GLM-5.3 in [llama.cpp](https://unsloth.ai/docs/models/glm-5.3#run-glm-5.3-in-llama.cpp) and [Unsloth Desktop](#run-glm-5.3-flash-in-unsloth). We will be utilizing the 239GB [`UD-IQ2_M`](https://huggingface.co/unsloth/GLM-5.3-GGUF/tree/main/UD-IQ2_M) quant for the best balance of accessibility and accuracy.

### 🦥 Run GLM-5.3 in Unsloth

GLM-5.3 can now run in [Unsloth Desktop](#run-qwen3.8-in-unsloth-desktop), an open-source UI app for local AI. **Unsloth automatically offloads to RAM and detects multiGPU setups**. With Unsloth Desktop, you can run models locally on **MacOS, Windows**, Linux and:

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

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FYVcpYHcS7vpnYcZUiwpO%2Fglm52%20example.png?alt=media&amp;token=d218ed4e-5102-48a6-943a-7d6b7a10446f" alt=""><figcaption></figcaption></figure>
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

#### Search and download GLM-5.3

Go to [Unsloth Chat](/docs/new/studio/chat.md) or Model hub and search for GLM-5.3 in the search bar and download your desired model and quant.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fpcug1oswnDUemsv08ffL%2FScreenshot%202026-08-28%20at%209.45.17%E2%80%AFAM.png?alt=media&amp;token=716b05f9-b0e9-4433-a592-6f9fdcec13a3" alt=""><figcaption></figcaption></figure>
{% endstep %}

{% step %}

#### Run GLM-5.3

Inference parameters should be auto-set when using Unsloth, however you can still change it manually. You can also edit the context length, chat template and other settings.

For more information, you can view our [Unsloth inference guide](/docs/new/studio/chat.md).
{% endstep %}

{% step %}

#### Serve GLM-5.3 with Unsloth API

You can use `unsloth run` command and serve GLM-5.3 via an API using `llama-server` runtime flags, including context sizing, GPU layers, threading, sampling, networking, and tool configuration. For more info see our [API docs](/docs/basics/api.md) or [unsloth start](/docs/integrations/unsloth-start.md).

{% code overflow="wrap" %}

```bash
unsloth run --model unsloth/GLM-5.3-GGUF:UD-IQ2_M
```

{% endcode %}
{% endstep %}

{% step %}

#### Unsloth is now ready

You can also do many other things with GLM-5.3 via Unsloth Desktop like:

* **Connect tools:** [Claude Code](/docs/basics/claude-code.md), [Codex](/docs/basics/codex.md), [web search](/docs/new/studio/chat.md#advanced-web-search), [MCP](/docs/basics/mcp.md) and more
* **Train models:** Fine-tune text, diffusion, [embedding](/docs/basics/embedding-finetuning.md), and more
* **Generate media:** Create and train [images](/docs/basics/diffusion-image.md), video, [TTS](/docs/basics/text-to-speech-tts-fine-tuning.md) locally

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FhxlaXPPPrWDFXhdkSdck%2FScreenshot%202026-08-27%20at%2011.59.01%E2%80%AFPM.png?alt=media&amp;token=a2ef8037-b657-473d-83e6-a5f5f22208ff" alt=""><figcaption></figcaption></figure>
{% endstep %}
{% endstepper %}

### 🦙 Run GLM-5.3 in llama.cpp

For this guide we'll be running the `UD-IQ2_M` quant which will require at least 245GB RAM. Feel free to change quantization type. For these tutorials, we will using [llama.cpp](https://https/github.com/ggml-org/llama.cpp) for fast local inference. GGUF: [**GLM-5.3-GGUF**](https://huggingface.co/unsloth/GLM-5.3-GGUF)&#x20;

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
You can now use `llama.cpp` directly to load and download models, just like `ollama run`. First, select the quantization type you want like `UD-IQ2_M`. Also use `export LLAMA_CACHE="unsloth/GLM-5.3-GGUF"` to force `llama.cpp` to save to a specific location. **Note this download process might be very slow**, so it's probably best to use the manual download process in the next section.

```bash
export LLAMA_CACHE="unsloth/GLM-5.3-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/GLM-5.3-GGUF:UD-IQ2_M \
    --temp 1.0 \
    --top-p 0.95 \
    --min-p 0.01
```

{% endstep %}

{% step %}
If you want to download the model manually **(much faster!)**, we can download the model via the code below (after installing `pip install huggingface_hub`). If downloads get stuck, see: [Hugging Face Hub, XET debugging](/docs/basics/troubleshooting-and-faqs/hugging-face-hub-xet-debugging.md)

```bash
hf download unsloth/GLM-5.3-GGUF \
    --local-dir unsloth/GLM-5.3-GGUF \
    --include "*UD-IQ2_M*" # Use "*UD-Q8_K_XL*" for near full precision
```

If you want to use the dynamic 1-bit, then do:

{% code overflow="wrap" expandable="true" %}

```bash
hf download unsloth/GLM-5.3-GGUF \
    --local-dir unsloth/GLM-5.3-GGUF \
    --include "*UD-IQ1_S*"
```

{% endcode %}
{% endstep %}

{% step %}
Then run the model in conversation mode. Use `unsloth/GLM-5.3-GGUF/UD-IQ2_M/GLM-5.3-UD-IQ2_M-00001-of-00006.gguf` for 2bit or `unsloth/GLM-5.3-GGUF/UD-IQ1_S/GLM-5.3-UD-IQ1_S-00001-of-00006.gguf`  for 1bit.

{% code overflow="wrap" %}

```bash
./llama.cpp/llama-cli \
    --model unsloth/GLM-5.3-GGUF/UD-IQ2_M/GLM-5.3-UD-IQ2_M-00001-of-00006.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --min-p 0.01
```

{% endcode %}
{% endstep %}

{% step %}
Similar to GLM-5.2, when you launch llama-cli, you will see:

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FUalNNvFxH613C9kcM3r4%2Fimage.png?alt=media&amp;token=f376e93d-26af-472f-8ea3-0968b57b004c" alt="" width="375"><figcaption></figcaption></figure>

Then after prompt, we made a cool small Snake game using `UD-IQ1_S` so 1-bit and it worked well with GLM-5.3!

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FDmysmr1aSotb5nIbLou5%2Fglm53-ezgif.com-video-to-gif-converter.gif?alt=media&amp;token=dff4c0a8-cf4f-43e8-99a0-40430ab8153b" alt="" width="395"><figcaption></figcaption></figure>
{% endstep %}
{% endstepper %}

#### 📐Long context via KV Cache quantization

To utilize long context in llama.cpp, use KV cache quantization to reduce memory usage.

Currently, these KV cache dtypes are supported: `f32`, `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, and `q5_1`. By default `f16` is used. `q4_1` uses around 5 bits per weight, allowing around **3.2x longer context lengths**.

```bash
./llama.cpp/llama-cli \
    --model unsloth/GLM-5.3-GGUF/UD-IQ2_M-/GLM-5.3-UD-IQ2_M-00001-of-00006.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --min-p 0.01 \
    --cache-type-k q4_1 \
    --cache-type-v q4_1 \
    --jinja \
    --chat-template-kwargs '{"reasoning_effort":"max"}'
```

### Quantization Analysis

We ran KLD for the quants we uploaded as well and it shows Q4\_K\_XL and Q5\_K\_XL are very close to the baseline, so aim for those.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F1ClHNDXzzv9r4bLywjEJ%2Fglm53_unsloth_dynamic_ggufs_kld_benchmarks_updated.png?alt=media&amp;token=9e4677e8-df89-4718-acf2-5c14aad393c9" alt=""><figcaption></figcaption></figure>

| quant        |    GB | top-1 % | mean KLD | 99.9% KLD |    PPL |
| ------------ | ----: | ------: | -------: | --------: | -----: |
| UD-IQ1\_S    | 216.7 |   72.56 | 0.687991 |     9.104 | 4.6130 |
| UD-IQ1\_M    | 228.5 |   75.64 | 0.565455 |     8.595 | 4.1410 |
| UD-IQ2\_M    | 238.6 |   78.53 | 0.453992 |     7.717 | 3.7433 |
| UD-Q2\_K\_XL | 253.9 |   80.93 | 0.374219 |     7.076 | 3.5048 |
| UD-IQ3\_XXS  | 281.7 |   84.15 | 0.272796 |     6.252 | 3.2482 |
| UD-Q3\_K\_XL | 343.0 |   88.86 | 0.141406 |     4.127 | 2.9107 |
| UD-IQ4\_XS   | 365.3 |   90.59 | 0.101496 |     3.177 | 2.8460 |
| UD-Q4\_K\_XL | 467.3 |   94.29 | 0.036922 |     1.309 | 2.7006 |
| UD-Q5\_K\_XL | 562.5 |   95.82 | 0.019728 |     0.786 | 2.6842 |
| UD-Q6\_K\_XL | 684.4 |   96.59 | 0.013257 |     0.534 | 2.6771 |

### 📊 Benchmarks

You can view GLM-5.3's key benchmark improvements in table format further below:

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fm0D8JgqiMhFBvxu1IBfm%2Fglm53bench.jpg?alt=media&amp;token=fe3e5fdf-c5e8-45a2-8a7a-941fdcd5ec6b" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Ftqb0wwb4uhbrmjB3bOAr%2Fglmcodingper.png?alt=media&amp;token=fc306ac0-a542-4675-b361-ccac23b691a8" alt=""><figcaption></figcaption></figure></div>

| Benchmark                               | GLM-5.3   | GLM-5.2 | Kimi K3 | <p>DeepSeek-V4</p><p>Pro-0813</p> | Qwen3.8-Max | Opus 4.8 | <p>Fable 5</p><p>(w/ fallback)</p> | GPT-5.6 Sol |
| --------------------------------------- | --------- | ------- | ------- | --------------------------------- | ----------- | -------- | ---------------------------------- | ----------- |
| Coding                                  |           |         |         |                                   |             |          |                                    |             |
| Terminal Bench 2.1                      | 88.2      | 81.0    | 88.3    | 87.9                              | 86.6        | 85.0     | 88.0                               | 88.8        |
| Terminal Bench 3.0                      | 28.3      | 4.6     | 17.4    | -                                 | -           | 21.1     | 33.7                               | 34.6        |
| <p>DeepSWE</p><p>v1.1</p>               | 66.9      | 46.2    | 67.5    | 62.7                              | 56.6        | 58.0     | 69.7                               | 72.7        |
| NL2Repo                                 | 58.0      | 48.9    | 58.0    | 61.1                              | 55.9        | 69.7     | -                                  | -           |
| <p>ProgramBench</p><p>Almost Solved</p> | 19.0      | 9.5     | 17.5    | -                                 | 10.5        | 15.5     | 33.0                               | 23.0        |
| FrontierSWE                             | 78.1      | 67.5    | -       | -                                 | -           | 66.5     | 88.2                               | -           |
| <p>SWE-Marathon</p><p>v1.1</p>          | 42.5      | 19.4    | 48.1    | -                                 | -           | 48.8     | 33.1                               | 42.5        |
| PostTrainBench                          | 39.8      | 31.7    | 32.0    | -                                 | -           | 32.9     | 41.8                               | 36.2        |
| Cyber                                   |           |         |         |                                   |             |          |                                    |             |
| CyberGym                                | 84.5      | 77.2    | 80.0    | 83.3                              | 78.5        | 78.1     | 83.8                               | 83.6        |
| <p>ExploitGym</p><p>2h / 6h</p>         | 105 / 130 | 29 / 39 | 36 / 70 | -                                 | 14 / 26     | 80 / 120 | 181 / 247                          | 216 / 293   |
| ExploitBench                            | 54.4      | 24.4    | 32.2    | -                                 | 28.8        | 40.0     | 78.0                               | 76.5        |
| Agentic                                 |           |         |         |                                   |             |          |                                    |             |
| Toolathlon Verified                     | 73.0      | 59.9    | 76.5    | 74.1                              | 72.5        | 76.2     | 74.7                               | 74.9        |
| <p>AutomationBench</p><p>v1.0.6</p>     | 48.2      | 26.2    | 46.7    | 43.2                              | 39.8        | 41.0     | 46.2                               | 45.8        |
| <p>Agents' Last Exam</p><p>ALE-CLI</p>  | 28.5      | 23.8    | 27.6    | 25.7                              | 27.0        | 25.7     | 23.8                               | 28.6        |
| HLE w/ Tools                            | 62.5      | 54.7    | 59.8    | 60.0                              | 56.2        | 57.9     | 63.9                               | 64.5        |
| GDPval-AA v2                            | 1769      | 1508    | 1682    | 1590                              | 1739        | 1588     | 1743                               | 1730        |
