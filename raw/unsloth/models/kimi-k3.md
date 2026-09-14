# Kimi K3 - How to Run Locally

Guide to running Kimi K3 quants on your local setup.

Kimi K3 by Moonshot AI is a 2.8T parameter open-weight model (104B active) built for SOTA coding, agentic, long-context, and chat workloads. It is the **strongest open model** to date, rivaling Claude 4.8 Opus and GPT-5.6. Kimi K3 has native vision, a 1M-token context window and uses MXFP4. Full-precision inference requires 1.56 TB of storage and 1-bit Kimi K3 [Unsloth](https://github.com/unslothai/unsloth) Dynamic GGUF requires **594 GB (62% less)**.

{% columns %}
{% column %}
Dynamic 1-bit (see right) reaches **\~78.9%** top-1 accuracy while being **62% smaller**. Dynamic 2-bit 861.3GB reaches **\~90%** accuracy while being **45% smaller**. Run [**Kimi-K3-GGUF**](https://huggingface.co/unsloth/Kimi-K3-GGUF) via [Unsloth Studio](/docs/new/studio.md) or llama.cpp. Kimi K3 can run on a NVIDIA DGX Station, or Mac Studio connected to a 128GB RAM device.&#x20;

For **lossless** Kimi K3, use Q8 (`UD-Q8_K_XL`), which is **50GB larger** than Q4 (`UD-Q4_K_XL`). We are still investigating if we can push it under 512GiB (dynamic 1-bit is 553.2 GiB) without damaging the model.

<a href="/docs/models/kimi-k3.md" class="button primary">Run Kimi K3 Tutorials</a><a href="/docs/models/kimi-k3.md#usage-guide" class="button secondary">Quant Results</a>
{% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FIGaAihxYkmTtlCYjIMQT%2Fglm%20example.gif?alt=media&amp;token=5738222c-69e6-4be1-b777-4ccc0baf0aa3" alt=""><figcaption><p>1-bit Kimi K3 GGUF vs Claude 5 vs GPT 5.6</p></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

**Table: Hardware requirements** (units = total memory: RAM + VRAM, or unified memory)

| Dynamic 1-bit S | Dynamic 1-bit M | Dynamic 2-bit XXS | Dynamic 2-bit XL | Q8 (Lossless) |
| --------------- | --------------- | ----------------- | ---------------- | ------------- |
| 610 GB          | 665 GB          | 726 GB            | 880 GB           | 1.6 TB        |

### Kimi K3 GGUF Implementation Details

We built on top of [llama.cpp PR](https://github.com/ggml-org/llama.cpp/pull/26185) with [our fork](https://github.com/unslothai/llama.cpp/pull/48) which includes vision support and some bug fixes.

1. The mmproj / vision tower is similar to the Kimi-K2.5 tower, but with RMSNorm, no biases, a non-square fused QKV (qkv width != n\_embd) and a post-norm projector.
2. We found when running llama.cpp, the `n_tokens * 40` budget failed at large batch sizes, and so we had to up to `n_tokens * 160`&#x20;
3. We also had to convert the Kimi chat template to a jinja format.
4. We tested as much as we could to cover all cases. Kimi by default has been trained with **preserved thinking on**, so all thinking traces are not deleted, but kept.

### 📊 Quantization Analysis

Like Kimi [K2.6](/docs/models/kimi-k2.6.md) and [K2.7](/docs/models/kimi-k2.7-code.md), K3's `UD-Q8_K_XL` is lossless because Kimi uses MXFP4 for MoE weights and BF16 for everything else, and `Q8_K_XL` follows that exactly. `UD-Q4_K_XL` is similar except some of remaining tensors (except norms etc) are `Q8_0`, so it is near full precision and requires 1.56 TB RAM/VRAM. `UD-Q8_K_XL` is 'truly lossless' vs the MXFP4 full safetensors version.

<table><thead><tr><th width="119.20001220703125">Quant</th><th width="71.60000610351562" align="right">GB</th><th width="124.800048828125" align="right">mean KLD</th><th width="104.9998779296875" align="right">PPL(q)</th><th width="188.79998779296875" align="right">top-1 agree %</th><th width="140.20001220703125" align="right">RMS dp %</th></tr></thead><tbody><tr><td><code>UD-IQ1_S</code></td><td align="right">594.0</td><td align="right">0.5645</td><td align="right">2.5789</td><td align="right">78.875 +/- 0.107</td><td align="right">36.495</td></tr><tr><td><code>UD-IQ1_M</code></td><td align="right">648.9</td><td align="right">0.4789</td><td align="right">2.3639</td><td align="right">81.219 +/- 0.103</td><td align="right">33.629</td></tr><tr><td><code>UD-IQ2_XXS</code></td><td align="right">711.1</td><td align="right">0.3784</td><td align="right">2.1266</td><td align="right">84.127 +/- 0.096</td><td align="right">29.826</td></tr><tr><td><code>UD-Q2_K_XL</code></td><td align="right">861.3</td><td align="right">0.1779</td><td align="right">1.7359</td><td align="right">90.390 +/- 0.077</td><td align="right">19.862</td></tr><tr><td><code>UD-Q4_K_XL</code></td><td align="right">1,510</td><td align="right"></td><td align="right">1.4579</td><td align="right"></td><td align="right"></td></tr><tr><td><code>UD-Q8_K_XL</code></td><td align="right">1,560</td><td align="right"></td><td align="right">1.4581</td><td align="right"></td><td align="right"></td></tr></tbody></table>

For imatrix generation and quantization, we used the 1.56 TB lossless `UD-Q8_K_XL` throughout calibration; its perplexity is 1.4581. Our Dynamic-1bit quant reaches 2.58 perplexity with 79% top-1 accuracy, making it surprisingly usable.

Other community quants are larger yet degrade far more. For example, one 618.9 GB quant `IQ1_M` exceeds our 594 GB 1-bit quant, but its perplexity jumps to 54.56 - 21× worse. The same pattern holds for `IQ2_XXS`: 725 GB at 96 PPL vs. our 711 GB at 2.12 PPL - 45× worse, meaning their 2-bit performs even worse than their 1-bit. This highlights importance of dynamic quantization + proper calibration.

**We also provide Top-1% Accuracy, KLD plots:**

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FfJOkWbg4O0vmlatF2nDY%2Ftop1_agreement_vs_disk_space_kld_style.png?alt=media&amp;token=77eb470c-b203-4ba8-a3d6-87d04af5c671" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fk4oLNDcM6nP8MG432DKE%2Fimage.png?alt=media&amp;token=4e5bdff7-6656-43d5-a902-62d97fd07fe1" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FfNYtyZStOo5RY6NSod4r%2Fmean_kld_vs_disk_space.png?alt=media&amp;token=1cd52540-48e2-49fa-9320-8b62c7b3f455" alt=""><figcaption></figcaption></figure></div>

### :gear: Usage Guide

Kimi K3 is **thinking-only**, with **`preserve_thinking` always enabled** and **max** thinking on by default. Instant mode is not supported. Thinking effort is configured with the `reasoning_effort` request field, and K3 supports `"low"`, `"high"`, and `"max"` thinking efforts.

| Default           | Agentic           |
| ----------------- | ----------------- |
| temperature = 1.0 | temperature = 1.0 |
| top\_p = 0.95     | top\_p = 1.0      |

* Context length = up to `1,048,576`
* Low, High, Max Thinking is toggagle in Unsloth

If the model fits, you will get \~20 tokens/s generation when using B200s and >120 tokens / s throughput. We recommend [`UD-IQ1_S`](https://huggingface.co/unsloth/Kimi-K3-GGUF?show_file_info=UD-IQ1_S%2FKimi-K3-UD-IQ1_S-00001-of-00015.gguf) (594GB) as a good size/quality balance. Best rule of thumb: RAM+VRAM ≈ the quant size; otherwise it’ll still work, just much slower due to disk offloading.

## Run Kimi K3 Guide

You can now run Kimi K3 in [llama.cpp](#run-in-llama.cpp) and [Unsloth Desktop](https://unsloth.ai/docs/models/pages/cZiZ00cwk1GGz1O1TOHo#run-glm-5.2-in-unsloth-studio). We will be utilizing the 594GB [`UD-IQ1_S`](https://huggingface.co/unsloth/Kimi-K3-GGUF?show_file_info=UD-IQ1_S%2FKimi-K3-UD-IQ1_S-00001-of-00015.gguf) quant for best results in terms of accessibility and accuracy and it will require at least 610GB RAM. Feel free to change quantization type. GGUF: [**Kimi-K3-GGUF**](https://huggingface.co/unsloth/Kimi-K3-GGUF)

### 🦥 Run Kimi-K3 in Unsloth

Kimi K3 can run in [Unsloth Desktop](/docs/desktop.md), an open-source desktop UI for local AI. **Unsloth Desktop automatically offloads to RAM and detects multiGPU setups**. With Unsloth Studio, you can run models locally on **MacOS, Windows**, Linux and:

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

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F6IXaXdTVyvbrnjehlxys%2Fkimik3.gif?alt=media&amp;token=31e1213b-d7da-46e9-bc7f-3a8c402513fc" alt=""><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

{% stepper %}
{% step %}
**Install and Launch Unsloth**

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

**Launch Unsloth**

MacOS, Linux, WSL and Windows:

```bash
unsloth studio
```

Then open `http://127.0.0.1:8888` (or your specific URL) in your browser.

**Launch Unsloth securely with HTTPS and Cloudflare**

**NEW!** Unsloth now provides a secure way to launch Unsloth over HTTPS through a free Cloudflare tunnel. Use the below (works in Windows, Mac & Linux):

```bash
unsloth studio --secure
```

{% endstep %}

{% step %}
**Search and download Kimi K3**

Unsloth Studio automatically offloads to RAM and detects multiGPU setups. On first launch you will need to create a password to secure your account and sign in again later.

Then go to the Model hub tab and search for **Kimi K3** in the search bar and download your desired model and quant. Ensure you have enough compute the run the model.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fl55nPVDRlWRPoZOnHyg2%2FScreenshot%202026-07-29%20at%203.12.19%E2%80%AFAM.png?alt=media&amp;token=4f910816-8075-4d14-b398-bc00a417a710" alt=""><figcaption></figcaption></figure>
{% endstep %}

{% step %}
**Run Kimi K3**

Inference parameters should be auto-set when using Unsloth Studio, however you can still change it manually. You can also toggle **low, high or max thinking**, edit the context length, chat template and other settings.

For more information, you can view our [Unsloth Studio inference guide](/docs/new/studio/chat.md).

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F6IXaXdTVyvbrnjehlxys%2Fkimik3.gif?alt=media&amp;token=31e1213b-d7da-46e9-bc7f-3a8c402513fc" alt=""><figcaption><p>Example of 1-bit Kimi-K3 running with Unsloth's Canvas</p></figcaption></figure>
{% endstep %}
{% endstepper %}

### 🦙 Run Kimi K3 in llama.cpp

For these tutorials, we will use [llama.cpp](https://github.com/ggml-org/llama.cpp) for fast local inference, especially if you have a CPU. We [created a fork](https://github.com/unslothai/llama.cpp/pull/48) specifically to support Kimi K3 vision thus. This builds on top of another [llama.cpp PR](https://github.com/ggml-org/llama.cpp/pull/26185).

{% stepper %}
{% step %}
Obtain the SPECIFIC Unsloth fork of `llama.cpp` on [**GitHub here**](https://github.com/unslothai/llama.cpp/pull/48) to enable vision support. You can follow the build instructions below as well. Change `-DGGML_CUDA=ON` to `-DGGML_CUDA=OFF` if you don't have a GPU or just want CPU inference. **For Apple Mac / Metal devices**, set `-DGGML_CUDA=OFF` then continue as usual - Metal support is on by default.

```bash
git clone https://github.com/unslothai/llama.cpp
cd llama.cpp
git fetch origin pull/48/head:kimi-k3-fullsize-vision
git checkout kimi-k3-fullsize-vision
cd ..
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

{% endstep %}

{% step %}
**Let's first get an image!** You can also upload images as well. We shall use [this image](https://raw.githubusercontent.com/unslothai/unsloth/refs/heads/main/images/unsloth%20made%20with%20love.png), which is just our mini logo showing how finetunes are made with Unsloth:

{% code overflow="wrap" %}

```bash
wget https://raw.githubusercontent.com/unslothai/unsloth/refs/heads/main/images/unsloth%20made%20with%20love.png -O unsloth.png
```

{% endcode %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-9bf7ec93680f889d7602e5f56a8d677d6a58ae6a%2Funsloth%20made%20with%20love.png?alt=media" alt="" width="188"><figcaption></figcaption></figure>

Let's get the 2nd image [here](https://files.worldwildlife.org/wwfcmsprod/images/Sloth_Sitting_iStock_3_12_2014/story_full_width/8l7pbjmj29_iStock_000011145477Large_mini__1_.jpg)

{% code overflow="wrap" %}

```bash
wget https://files.worldwildlife.org/wwfcmsprod/images/Sloth_Sitting_iStock_3_12_2014/story_full_width/8l7pbjmj29_iStock_000011145477Large_mini__1_.jpg -O picture.png
```

{% endcode %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-4b30cc86b2c75edf95ee1ec6fe0c51fb30afd6c0%2F8l7pbjmj29_iStock_000011145477Large_mini__1_.jpg?alt=media" alt="" width="188"><figcaption></figcaption></figure>
{% endstep %}

{% step %}
You can now use `llama.cpp` directly to load and download models, just like `ollama run`. First, select the quantization type you want like `IQ1_S`. Also use `export LLAMA_CACHE="folder"` to force `llama.cpp` to save to a specific location. **Note this download process might be very slow**, so it's probably best to use the manual download process in the next section.

```bash
export LLAMA_CACHE="unsloth/Kimi-K3-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/Kimi-K3-GGUF:UD-IQ1_S \
    --temp 1.0 \
    --top-p 0.95
```

{% endstep %}

{% step %}
If you want to download the model manually, we can download the model via the code below (after installing `pip install huggingface_hub`). If downloads get stuck, see: [Hugging Face Hub, XET debugging](/docs/basics/troubleshooting-and-faqs/hugging-face-hub-xet-debugging.md)

```bash
hf download unsloth/Kimi-K3-GGUF \
    --local-dir unsloth/Kimi-K3-GGUF \
    --include "*mmproj-BF16*" \
    --include "*UD-IQ1_S*" # Use "*UD-Q8_K_XL*" for full precision
```

{% endstep %}

{% step %}
Then run the model in conversation mode:

{% code overflow="wrap" %}

```bash
./llama.cpp/llama-cli \
    --model unsloth/Kimi-K3-GGUF/UD-IQ1_S/Kimi-K3-UD-IQ1_S-00001-of-00014.gguf \
    --mmproj unsloth/Kimi-K3-GGUF/mmproj-BF16.gguf \
    --temp 1.0 \
    --top-p 0.95
```

{% endcode %}
{% endstep %}

{% step %}
You will then see:

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FtouOdsj4Tp5WUdcL2cPW%2Fimage.png?alt=media&amp;token=4d0f99e4-a445-4192-9f46-0ccddbef491a" alt=""><figcaption></figcaption></figure>

And I asked "What is the sqrt of -1":

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FT4nvcX4WX5gj2v2Xy9QZ%2Fimage.png?alt=media&amp;token=131a605c-71ea-4d63-8ed4-2c2bcbe3a33d" alt=""><figcaption></figcaption></figure>

Kimi K3 also supports images for eg loading the Unsloth image:

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F6MtRrPbvTC4hJES82tVr%2Fimage.png?alt=media&amp;token=c22702b1-ba97-4daf-8ea2-9c215d63a989" alt=""><figcaption></figcaption></figure>

And then we use the sloth image and ask how it's related:

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FG78fX5KL4c4ua0A0JGv2%2Fimage.png?alt=media&amp;token=26ef7516-7f63-4ad2-932f-fc0b5e6b4f07" alt=""><figcaption></figcaption></figure>
{% endstep %}
{% endstepper %}

### 📊 Benchmarks

You can view further below for benchmarks in table format:

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FD2DjGdyP0gZOWx2aNHql%2Fkimik3%20bench.png?alt=media&amp;token=2d53268a-fb98-486e-a60d-fe187f8bf946" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F04Z9ZT24kAfEmyXYgdrK%2Fkimik3agentbench.png?alt=media&amp;token=a0a23807-ce6d-4ac5-8bd3-e08c547a5cfd" alt=""><figcaption></figcaption></figure></div>

|         Benchmark         | Kimi K3&#xA;(max) | Claude Fable 5&#xA;(max) | GPT-5.6 Sol&#xA;(max) | Claude Opus 4.8&#xA;(max) | GPT-5.5&#xA;(xhigh) | GLM-5.2&#xA;(max) |
| :-----------------------: | :---------------: | :----------------------: | :-------------------: | :-----------------------: | :-----------------: | :---------------: |
| **Reasoning & Knowledge** |                   |                          |                       |                           |                     |                   |
|        GPQA Diamond       |        93.5       |           92.6           |        **94.1**       |            91.0           |         93.5        |        91.2       |
|          HLE-Full         |    43.5 / 56.0    |      **53.3 / 63.0**     |      44.5 / 58.0      |        49.8 / 57.9        |     41.4 / 52.2     |         —         |
|         **Coding**        |                   |                          |                       |                           |                     |                   |
|          DeepSWE          |        67.5       |           70.0           |        **73.0**       |            59.0           |         67.0        |        46.2       |
|     Terminal-Bench 2.1    |        88.3       |           88.0           |        **88.8**       |            84.6           |         83.4        |        82.7       |
|        **Agentic**        |                   |                          |                       |                           |                     |                   |
|         BrowseComp        |      **91.2**     |           88.0           |          90.4         |            84.3           |         84.4        |         —         |
|     GDPval-AA v2 (Elo)    |        1686       |         **1747**         |          1736         |            1593           |         1491        |        1510       |
|        OSWorld 2.0        |        58.3       |         **66.1**         |          62.6         |            55.7           |         49.5        |         —         |
|         **Vision**        |                   |                          |                       |                           |                     |                   |
|          MMMU-Pro         |    81.6 / 83.4    |      81.2 / **86.5**     |    **83.0** / 84.6    |        78.9 / 82.7        |     81.2 / 83.2     |         —         |
|         MathVision        |    94.3 / 97.8    |      94.8 / **98.6**     |    **95.8** / 97.8    |        86.7 / 97.1        |     92.2 / 96.8     |         —         |

DeepSWE Benchmarks show Kimi-K3 doing very efficiently!

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F2CHd2zfDwn6J3kYIwtXq%2Fimage.png?alt=media&amp;token=d8fe50b6-e581-4de1-8c9d-6647280bb8b0" alt=""><figcaption></figcaption></figure>
