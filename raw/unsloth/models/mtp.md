# How to Run MTP Models: Multi-Token Prediction Guide

MTP, or Multi-Token Prediction, speeds up inference by letting a model predict multiple upcoming tokens at once instead of generating one token per step. It enables faster inference without accuracy loss and is especially effective on GPUs. In this guide, you’ll learn how to use MTP models like [Gemma 4](/docs/models/gemma-4.md) or [Qwen3.8](/docs/models/qwen3.6.md) on your local device.

MTP predicts multiple future tokens, which the main model verifies in parallel. This reduces generation forward passes, speeding output while preserving quality because only verified tokens are kept.

When running [GGUFs](/docs/basics/dynamic-3.0-ggufs.md), MTP can make generation **\~1.4× to 2.2× faster**. Dense models like Gemma-4-31B benefit most, reaching **>1.4× speedup** over the original. Gains are smaller on devices with lower memory bandwidth, such as older Macs. You can run MTP models directly in [Unsloth Studio’s UI](/docs/new/studio.md) or llama.cpp.

{% hint style="info" %}
**MTP uses more memory than standard**, so plan for \~2 GB additional RAM/VRAM headroom.
{% endhint %}

<a href="/docs/models/mtp.md#gemma-4-mtp" class="button primary">Gemma 4 MTP</a><a href="/pages/3PWlU172DOGeqxIflfP7#qwen3.6-mtp" class="button primary">Qwen3.6 MTP</a>

We found `--spec-draft-n-max 2` is the best starting point however, **do not assume `2` is optimal**, as performance is hardware-dependent. Try any value from `1` through `6` and use whichever is fastest for your system. Unsloth Studio automatically sets the ideal MTP settings optimized for your specific hardware (Mac, CPU, GPU etc.) - you can still change it later.

### Gemma 4 MTP

Google DeepMind trained MTP separately from the original [Gemma 4](/docs/models/gemma-4/qat.md) models, including for [QAT variants](/docs/models/gemma-4/qat.md). Unlike Qwen, Google released specific MTP variants under the `assistant` name. For best results, we only upload 3 precision options: **8-bit** and **16-bit** (BF16, F16). For QAT - we applied the [smart 4-bit recovery process](/docs/models/gemma-4/qat.md#qat-analysis) like we did for Gemma 4 QAT quants, and so the MTP quants are also smart 4-bit derived.

We uploaded `mtp-` prefixed GGUFs to each repo, so you only need to use the **regular original Gemma 4 GGUFs**, no separate repo is needed. You can access Gemma [MTP models here](https://huggingface.co/collections/unsloth/gemma-4) and they can now run in [Unsloth](#unsloth-studio-mtp-guide). We benchmarked Gemma 4 QAT with MTP, and it runs 1.5x - 2.2x faster:

<div data-with-frame="true"><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FbFaiVrra3iTZQvZjAeoR%2Fgemma%204%20mtp.png?alt=media&amp;token=c32a50d3-36ef-47b6-a9c0-5ca0b1d1549b" alt="" width="563"><figcaption></figcaption></figure></div>

**Table: MTP hardware requirements** (units = total memory: RAM + VRAM, or unified memory)

| Gemma 4 variant |    4-bit |    8-bit | BF16 / FP16 |
| --------------- | -------: | -------: | ----------: |
| **E2B**         |     5 GB |   6–9 GB |       11 GB |
| **E4B**         | 6.5–7 GB | 10–13 GB |       17 GB |
| **12B Unified** |   8–9 GB | 14–15 GB |       26 GB |
| **26B A4B**     | 17–18 GB | 29–31 GB |       53 GB |
| **31B**         | 18–21 GB | 35–39 GB |       63 GB |

{% hint style="warning" %}
**Gemma 4 MTP is automatically enabled in** [**Unsloth Studio**](#unsloth-studio-mtp-guide)**. You only need to download the regular original Gemma 4 GGUFs.** We updated the Gemma 4 GGUF files to include an additional MTP file inside a separate folder within the GGUF package, so there is no need to download a separate Gemma 4 assistant GGUF.

The only model that still requires a separate MTP GGUF is Qwen3.6.
{% endhint %}

To run the Gemma 4 MTP models, follow the steps either for [Unsloth Studio](#unsloth-studio-mtp-guide) or [llama.cpp](#llama.cpp-mtp-guide).

<a href="/docs/models/mtp.md#unsloth-studio-mtp-guide" class="button primary">🦥 Run in Unsloth Studio</a><a href="/pages/3PWlU172DOGeqxIflfP7#llama.cpp-mtp-guide" class="button primary">🦙 Run in llama.cpp</a>

so the below just works (this uses the 8-bit one)

{% code overflow="wrap" %}

```bash
llama-server \
    -hf unsloth/gemma-4-31B-it-GGUF \
    --spec-type draft-mtp \
    --spec-draft-n-max 4
```

{% endcode %}

### Qwen3.6 MTP

Qwen directly trained MTP inside of the [Qwen3.6](/docs/models/qwen3.6.md) and [Qwen3.5](/docs/models/qwen3.5.md) models. This enables Qwen3.6 27B MTP to reach 160 tokens/s and Qwen3.6 35B-A3B reach 240 tokens/s on an RTX 6000 GPU. GGUF uploads:

| [Qwen3.6-27B-MTP-GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF) | [Qwen3.6-35B-A3B-MTP-GGUF](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-MTP-GGUF) |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |

**Table: MTP hardware requirements** (units = total memory: RAM + VRAM, or unified memory)

<table><thead><tr><th>Qwen3.6</th><th>3-bit</th><th>4-bit</th><th width="128">6-bit</th><th>8-bit</th><th>BF16</th></tr></thead><tbody><tr><td><strong>27B</strong></td><td>16 GB</td><td>19 GB</td><td>25 GB</td><td>31 GB</td><td>56 GB</td></tr><tr><td><strong>35B-A3B</strong></td><td>18 GB</td><td>24 GB</td><td>31 GB</td><td>39 GB</td><td>71 GB</td></tr></tbody></table>

Below are graphs of inference throughput for MTP vs. no MTP:

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FMYn1g7MDeVRAUa6i2oOk%2Fthroughput%20mpt.png?alt=media&amp;token=aff44c0a-3cc3-493e-b6b4-e3279dfb90c1" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F4CvUpxr0xdxCR1lTGUbS%2Fmtp%20benchmarks%20landscape.png?alt=media&amp;token=d6579f47-a196-408b-a013-329e09705251" alt=""><figcaption></figcaption></figure></div>

We also [uploaded MTP GGUFs](https://huggingface.co/unsloth/models?search=mtp) for the [Qwen3.5](/docs/models/qwen3.5.md) **model family** including: 0.8B, 2B, 4B, 9B, 27B, 35B-A3B, 122B-A10B and 397B-A17B. Llama.cpp is continually improving MTP performance, so expect it to get faster overtime!

To run the Qwen MTP models, follow the steps either for [Unsloth Studio](#unsloth-studio-mtp-guide) or [llama.cpp](#llama.cpp-mtp-guide).

### 🦥 Unsloth Studio MTP Guide

Unsloth Studio automatically sets the ideal MTP settings optimized for your specific hardware (Mac, CPU, GPU etc.) - you can still change it later.

{% stepper %}
{% step %}

#### Install Unsloth

Run in your terminal:

**MacOS, Linux, WSL:**

```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```

**Windows PowerShell:**

```bash
irm https://unsloth.ai/install.ps1 | iex
```

{% endstep %}

{% step %}

#### Launch Unsloth

**MacOS, Linux, WSL and Windows:**

```bash
unsloth studio -H 127.0.0.1 -p 8888
```

Then open `http://127.0.0.1:8888` (or your specific URL) in your browser.
{% endstep %}

{% step %}

#### Search and download your desired model

On first launch you will need to create a password to secure your account and sign in again later. Then go to the [Unsloth Chat](/docs/new/studio/chat.md) tab and search for Qwen3.6 MTP or Gemma 4 in the search bar and download your desired model and quant.

{% hint style="warning" %}
**Gemma 4 MTP is automatically enabled in Unsloth. You only need to download the regular original Gemma 4 GGUF.** We updated the Gemma 4 GGUF files to include an additional MTP file inside a separate folder within the GGUF package, so there is no need to download a separate Gemma 4 assistant GGUF.

The only model that still requires a separate MTP GGUF is Qwen3.6.
{% endhint %}

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FdtEdYQfmVn80wEC6rw5P%2FScreenshot%202026-06-11%20at%208.37.44%E2%80%AFAM.png?alt=media&amp;token=288c2c95-9ddc-41c8-aefe-4ce81af16ff1" alt="" width="375"><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F2zQdtdNf0CRBrnTOXBZa%2FScreenshot%202026-05-16%20at%207.10.39%E2%80%AFPM.png?alt=media&amp;token=d1f2e482-5cb7-4e41-97ed-f2905a81f262" alt="" width="375"><figcaption></figcaption></figure></div>
{% endstep %}

{% step %}

#### Run your MTP model

Inference, MTP and speculative **decoding settings** should be auto-set when using Unsloth Studio, however you can still change it manually. You can also edit speculative decoding, the context length, chat template and other settings in the right side bar.

<div data-with-frame="true"><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F6OmL5f4aDMFPFCqUcfsN%2FScreenshot%202026-06-11%20at%208.39.48%E2%80%AFAM.png?alt=media&amp;token=3d6fc88a-e275-4a07-bb84-4305f9ba1089" alt="" width="149"><figcaption></figcaption></figure></div>

For more information, you can view our [Unsloth Studio inference guide](/docs/new/studio/chat.md). Below, the 2-bit Qwen3.6 MTP GGUF made 10+ tool calls, searched 10 sites and executed Python code:

<div data-with-frame="true"><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FsERzR65n4jc1UtuSHozZ%2Fwedefrwfwe.gif?alt=media&amp;token=e303ed9e-0d90-456d-8d57-874a06803903" alt=""><figcaption></figcaption></figure></div>
{% endstep %}
{% endstepper %}

### 🦙 Llama.cpp MTP Guide

{% stepper %}
{% step %}
Install the latest version of `llama.cpp` on [**GitHub here**](https://github.com/ggml-org/llama.cpp/pull/22673). You can follow the build instructions below as well. Change `-DGGML_CUDA=ON` to `-DGGML_CUDA=OFF` if you don't have a GPU or just want CPU inference. **For Apple Mac / Metal devices**, set `-DGGML_CUDA=OFF` then continue as usual - Metal support is on by default.

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
If you want to use `llama.cpp` directly to load models, you can do the below: (:`Q4_K_XL`) is the quantization type. You can also download via Hugging Face (point 3). This is similar to `ollama run` . Use `export LLAMA_CACHE="folder"` to force `llama.cpp` to save to a specific location. The model has a maximum of 256K context length.

Follow one of the commands for the specific models:

<a href="/docs/models/mtp.md#gemma-4-mtp-1" class="button primary">Gemma 4</a><a href="/pages/3PWlU172DOGeqxIflfP7#qwen3.6-mtp-1" class="button primary">Qwen3.6</a>

#### Gemma 4 MTP:

Don't forget to **change the model name** to your desired Gemma 4 model size like Gemma-4-26B-A4B etc. as the instructions below are for Gemma-4-12B. Notice we provided a `mtp-` prefixed GGUF, so the below `-hf` command should auto download and use MTP.

**Thinking mode:**

```bash
export LLAMA_CACHE="unsloth/gemma-4-12b-it-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/gemma-4-12b-it-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64  \
    --spec-type draft-mtp --spec-draft-n-max 2
```

{% hint style="info" %}
Please see Gemma 4's new [Preserved Thinking](#thinking-enable-disable--preserve-thinking).
{% endhint %}

**Non-thinking mode**:

```bash
export LLAMA_CACHE="unsloth/gemma-4-12b-it-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/gemma-4-12b-it-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64  \
    --spec-type draft-mtp --spec-draft-n-max 2 \
    --chat-template-kwargs '{"enable_thinking":false}'
```

#### Qwen3.6 MTP:

Don't forget to **change the model name** to your desired Qwen3.6 variant like Qwen3.6-35B-A3B or Qwen3.5 etc. as the instructions below are for Qwen3.6-27B:

**Thinking mode** (General tasks)**:**

```bash
export LLAMA_CACHE="unsloth/Qwen3.6-27B-MTP-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/Qwen3.6-27B-MTP-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.00 \
    --spec-type draft-mtp --spec-draft-n-max 2
```

For precise coding tasks, change: `temperature=0.6`

{% hint style="info" %}
Please see Qwen3.6's new [Preserved Thinking](#thinking-enable-disable--preserve-thinking).
{% endhint %}

**Non-thinking mode** (General tasks):

```bash
export LLAMA_CACHE="unsloth/Qwen3.6-27B-MTP-GGUF"
./llama.cpp/llama-server \
    -hf unsloth/Qwen3.6-27B-MTP-GGUF:UD-Q4_K_XL \
    --temp 0.7 \
    --top-p 0.8 \
    --top-k 20 \
    --presence-penalty 1.5 \
    --min-p 0.00 \
    --spec-type draft-mtp --spec-draft-n-max 2 \
    --chat-template-kwargs '{"enable_thinking":false}'
```

{% endstep %}

{% step %}

#### Manually downloading quants

If you want to manually download the quants and the MTP quants, you can also do that! Download the model via the code below (after installing `pip install huggingface_hub hf_transfer`). You can choose Q4\_K\_M or other quantized versions like `UD-Q4_K_XL` . We recommend using at least 2-bit dynamic quant `UD-Q2_K_XL` to balance size and accuracy. If downloads get stuck, see: [Hugging Face Hub, XET debugging](/docs/basics/troubleshooting-and-faqs/hugging-face-hub-xet-debugging.md)

#### Gemma 4 MTP:

```bash
hf download unsloth/gemma-4-12B-it-qat-GGUF \
    --local-dir unsloth/gemma-4-12B-it-qat-GGUF \
    --include "*mmproj-F16*" \
    --include "mtp-*" \
    --include "*UD-Q4_K_XL*" # Use "*UD-Q2_K_XL*" for Dynamic 2bit
```

#### Qwen3.6 MTP:

```bash
hf download unsloth/Qwen3.6-27B-MTP-GGUF \
    --local-dir unsloth/Qwen3.6-27B-MTP-GGUF \
    --include "*mmproj-F16*" \
    --include "*UD-Q4_K_XL*" # Use "*UD-Q2_K_XL*" for Dynamic 2bit
```

{% endstep %}

{% step %}
Then run the model in conversation mode:

#### Gemma 4 MTP:

{% code overflow="wrap" %}

```bash
./llama.cpp/llama-cli \
    --model unsloth/gemma-4-12B-it-qat-GGUF/gemma-4-12B-it-qat-UD-Q4_K_XL.gguf \
    --mmproj unsloth/gemma-4-12B-it-qat-GGUF/mmproj-F16.gguf \
    --model-draft unsloth/gemma-4-12B-it-qat-GGUF/mtp-gemma-4-12B-it.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64  \
    --spec-type draft-mtp --spec-draft-n-max 2
```

{% endcode %}

And you will see the below - ignore the error messages as well

<img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FxvFX69qVxC4PBQ5CyzrN%2Fimage.png?alt=media&amp;token=0ac706d9-1492-4224-be7f-a6876aa488ca" alt="" data-size="original">

#### Qwen3.6 MTP:

{% code overflow="wrap" %}

```bash
./llama.cpp/llama-cli \
    --model unsloth/Qwen3.6-27B-MTP-GGUF/Qwen3.6-27B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Qwen3.6-27B-MTP-GGUF/mmproj-F16.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --min-p 0.00 \
    --top-k 20 \
    --spec-type draft-mtp --spec-draft-n-max 2
```

{% endcode %}
{% endstep %}

{% step %}

#### Llama-server deployment

To deploy Gemma-4 on llama-server, use:

{% code overflow="wrap" %}

```bash
./llama.cpp/llama-server \
    --model unsloth/gemma-4-12B-it-qat-GGUF/gemma-4-12B-it-qat-UD-Q4_K_XL.gguf \
    --mmproj unsloth/gemma-4-12B-it-qat-GGUF/mmproj-F16.gguf \
    --model-draft unsloth/gemma-4-12B-it-qat-GGUF/mtp-gemma-4-12B-it.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64 \
    --alias "unsloth/gemma-4-12b-it-qat-GGUF" \
    --port 8001 \
    --chat-template-kwargs '{"enable_thinking":true}'
```

{% endcode %}
{% endstep %}
{% endstepper %}
