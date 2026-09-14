# Unsloth Dynamic GGUFs on Aider Polyglot

Performance of Unsloth Dynamic GGUFs on Aider Polyglot Benchmarks

We’re excited to showcase how Unsloth Dynamic GGUFs makes it possible to quantize LLMs like [DeepSeek-V3.1](/docs/models/tutorials/deepseek-v3.1-how-to-run-locally.md) (671B) down to just **1-bit** or **3-bit**, and still be able to outperform SOTA models like **GPT-4.5, GPT-4.1** (April 2025) and **Claude-4-Opus** (May 2025).

Previously, [we demonstrated](/docs/basics/dynamic-3.0-ggufs.md) how Unsloth Dynamic GGUFs outperform other quantization methods on 5-shot MMLU and KL Divergence. Now, we’re showcasing their performance on independent third-party evaluations using the **Aider Polyglot** **benchmark.**

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-a114143bdd47add988182aabf9313ab40be38d7d%2Faider%20thinking.png?alt=media" alt="" width="563"><figcaption><p>Thinking Aider Benchmarks</p></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-b085c16c7f8351308229f1341846cbf1a2617d0a%2Faider%20non.png?alt=media" alt="" width="563"><figcaption><p>No Thinking Aider Benchmarks</p></figcaption></figure></div>

### ⭐**Key results**

* Our **1-bit** Unsloth Dynamic GGUF shrinks DeepSeek-V3.1 from **671GB → 192GB (-75% size)** and no-thinking mode greatly outperforms GPT-4.1 (Apr 2025), GPT-4.5, and DeepSeek-V3-0324.
* **3-bit** Unsloth DeepSeek-V3.1 (thinking) GGUF: Outperforms Claude-4-Opus-20250514 (thinking).
* **5-bit** Unsloth DeepSeek-V3.1 (non-thinking) GGUF: Matches Claude-4-Opus-20250514 (non-thinking) performance.
* Unsloth Dynamic GGUFs perform consistently better than other non-Unsloth Dynamic imatrix GGUFs
* Other non-Unsloth 1-bit and 2-bit DeepSeek-V3.1 quantizations, as well as standard 1-bit quantization without selective layer quantization, either failed to load or produced gibberish and looping outputs. This highlights how Unsloth Dynamic GGUFs are able to largely retain accuracy whereas other methods do not even function.

**Why the** [**Aider Polyglot**](https://aider.chat/docs/leaderboards/) **benchmark?** Aider is one of the most comprehensive measures of how well LLMs can write, code, follow instructions, and apply changes without human intervention, making it one of the hardest and most valuable benchmarks for real-world use.

{% hint style="success" %}
The **key advantage** of using the Unsloth package and models is our active role in ***fixing critical bugs*** in major models. We've collaborated directly with teams behind [Qwen3](https://www.reddit.com/r/LocalLLaMA/comments/1kaodxu/qwen3_unsloth_dynamic_ggufs_128k_context_bug_fixes/), [Meta (Llama 4)](https://github.com/ggml-org/llama.cpp/pull/12889), [Mistral (Devstral)](https://app.gitbook.com/o/HpyELzcNe0topgVLGCZY/s/xhOjnexMCB3dmuQFQ2Zq/~/changes/618/basics/tutorials-how-to-fine-tune-and-run-llms/devstral-how-to-run-and-fine-tune), [Google (Gemma 1–3)](https://news.ycombinator.com/item?id=39671146) and [Microsoft (Phi-3/4)](https://simonwillison.net/2025/Jan/11/phi-4-bug-fixes), contributing essential fixes that significantly boost accuracy.
{% endhint %}

## 🦥Unsloth Dynamic Quantization

{% hint style="success" %}
**Dynamic 1 bit makes important layers in 8 or 16 bits and un-important layers in 1,2,3,4,5 or 6bits.**
{% endhint %}

In Nov 2024, our [4-bit Dynamic](https://unsloth.ai/blog/dynamic-4bit) Quants showcased how you could largely restore QLoRA fine-tuning & model accuracy by just <mark style="background-color:green;">**selectively quantizing layers**</mark>. We later studied [DeepSeek-R1](/docs/models/tutorials/deepseek-r1-how-to-run-locally.md)'s architecture and applied this similar methodology, where we quantized some layers to as low as 1-bit and important layers to higher bits (6, 8-bit). This approach quickly gained popularity and has proven especially effective for MoE models, making dynamic quantization the de facto for MoE quantization.

Our Dynamic GGUFs are even more effective when paired with our [imatrix calibration dataset](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs/pages/QznsvWxKKvrY6PdiByzz#whats-new-in-dynamic-v2.0), designed for chat and coding performance. All of this enabled extreme LLM compression without catastrophic loss in quality.

For example in Qwen2-VL-2B-Instruct, naively quantizing all layers to 4bit causes the model to fail understanding the image below. It's a train, not a coastal scene!

{% columns %}
{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-379bd5cc72a8f8e9acb4b6a6ad9fe847bf1ec296%2FTrain_NPovU814oJVjqy9Gu3BSm.avif?alt=media" alt=""><figcaption></figcaption></figure>
{% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-38f5ea51c343a79bde7996d678761944f1dedaa7%2Fimage.png?alt=media" alt=""><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

We also showed dynamic benchmarks in <https://docs.unsloth.ai/basics/unsloth-dynamic-2.0-ggufs> for Gemma 3 and Llama 4 Scout, showing how effective our methodology is:

{% columns %}
{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-28c5aa4355f5c09aef43217f2a02131aa6e3517f%2Fimage.avif?alt=media" alt=""><figcaption></figcaption></figure>
{% endcolumn %}

{% column %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-db47ebf519863f334f58c925dd6b39d0e01c359b%2Fimage.avif?alt=media" alt=""><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

### ⚙️Benchmark setup

For our DeepSeek-V3.1 experiments, we compared different bits of **Unsloth Dynamic GGUFs** against:

* **Full-precision, unquantized LLMs** including GPT 4.5, 4.1, Claude-4-Opus, DeepSeek-V3-0324 etc.
* ***Other*****&#x20;dynamic imatrix V3.1 GGUFs**
* ***Semi-*****dynamic** (some selective layer quantization) imatrix V3.1 GGUFs for **ablation purposes**.

Benchmark experiments were mainly conducted by [David Sluys](https://www.linkedin.com/in/david-sluys-231348208/) (neolithic5452 on [Aider Discord](https://discord.com/channels/1131200896827654144/1408293692074360914)), a trusted community contributor to Aider Polyglot evaluations. Tests were run \~3 times and averaged for a median score, and the Pass-2 accuracy is reported as by convention. There are some reproducible benchmark code snippets in Aider's Discord.

<details>

<summary>Expand for Reasoning model Aider benchmarks</summary>

| Model                             | Accuracy |
| --------------------------------- | -------- |
| GPT-5                             | 86.7     |
| Gemini 2.5 Pro (June)             | 83.1     |
| o3                                | 76.9     |
| DeepSeek V3.1                     | 76.1     |
| **(3 bit) DeepSeek V3.1 Unsloth** | **75.6** |
| Claude-4-Opus (May)               | 72       |
| o4-mini (High)                    | 72       |
| DeepSeek R1 0528                  | 71.4     |
| **(2 bit) DeepSeek V3.1 Unsloth** | **66.7** |
| Claude-3.7-Sonnet (Feb)           | 64.9     |
| **(1 bit) DeepSeek V3.1 Unsloth** | **57.8** |
| DeepSeek R1                       | 56.9     |

</details>

<details>

<summary>Expand for Non Reasoning model Aider benchmarks</summary>

| Model                             | Accuracy |
| --------------------------------- | -------- |
| DeepSeek V3.1                     | 71.6     |
| Claude-4-Opus (May)               | 70.7     |
| **(5 bit) DeepSeek V3.1 Unsloth** | **70.7** |
| **(4 bit) DeepSeek V3.1 Unsloth** | **69.7** |
| **(3 bit) DeepSeek V3.1 Unsloth** | **68.4** |
| **(2 bit) DeepSeek V3.1 Unsloth** | **65.8** |
| Qwen3 235B A22B                   | 59.6     |
| Kimi K2                           | 59.1     |
| **(1 bit) DeepSeek V3.1 Unsloth** | **55.7** |
| DeepSeek V3-0324                  | 55.1     |
| GPT-4.1 (April, 2025)             | 52.4     |
| ChatGPT 4o (March, 2025)          | 45.3     |
| GPT-4.5                           | 44.9     |

</details>

DeepSeek V3.1 has both a reasoning and a non reasoning mode, and we test both. For non reasoning, we see a clear trend of how our dynamic quantizations perform below. dynamic 5-bit attains 70.7% on Aider Pass-2, whilst dynamic 1-bit attains 55.7%. In terms of size and accuracy, the 3 and 4bit are extremely powerful!

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-b085c16c7f8351308229f1341846cbf1a2617d0a%2Faider%20non.png?alt=media" alt=""><figcaption></figcaption></figure>

## :sparkler:Comparison to other quants

We also run the Aider Polyglot benchmark on other dynamic imatrix GGUFs from the community and compare it to ours. To ensure a **fair comparison**, we do the following:

1. We select similar sized files and bit types to each Unsloth quant.
2. We use our **fixed chat template** if the community quant fails to execute the benchmark. We found some community quants `{"code":500,"message":"split method must have between 1 and 1 positional arguments and between 0 and 0 keyword arguments at row 3, column 1908"}`, and this gets fixed by using our fixed chat template.

We see Unsloth dynamic quants doing remarkably well when compared to other community quantization for the same model size and quant type!

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-bbebbacfa75126d246c3ca1ed2ca269bc815b028%2FOther%20quants.png?alt=media" alt=""><figcaption></figcaption></figure>

<details>

<summary>Expand for raw numerical data comparison to other quants</summary>

<table><thead><tr><th width="109.25">Quant</th><th width="171.25006103515625">Quant Size (GB)</th><th>Unsloth Accuracy %</th><th>Comparison Accuracy %</th></tr></thead><tbody><tr><td>IQ2_XXS</td><td>164</td><td></td><td>43.6</td></tr><tr><td>TQ1_0</td><td>170</td><td>50.7</td><td></td></tr><tr><td>IQ1_M</td><td>206</td><td>55.7</td><td></td></tr><tr><td>IQ2_M</td><td>215</td><td></td><td>56.6</td></tr><tr><td>IQ2_XXS</td><td>225</td><td>61.2</td><td></td></tr><tr><td>IQ2_M</td><td>235</td><td>64.3</td><td></td></tr><tr><td>Q2_K_L</td><td>239</td><td></td><td>64.0</td></tr><tr><td>Q2_K_XL</td><td>255</td><td>65.8</td><td></td></tr><tr><td>IQ3_XXS</td><td>268</td><td>65.6</td><td>65.6</td></tr><tr><td>IQ3_XXS</td><td>279</td><td>66.8</td><td></td></tr><tr><td>Q3_K_S</td><td>293</td><td></td><td>65.2</td></tr><tr><td>Q3_K_XL</td><td>300</td><td>68.4</td><td></td></tr><tr><td>IQ4_XS</td><td>357</td><td>69.2</td><td></td></tr><tr><td>IQ4_XS</td><td>360</td><td></td><td>66.3</td></tr><tr><td>Q4_K_XL</td><td>387</td><td>69.7</td><td></td></tr><tr><td>Q4_K_M</td><td>405</td><td>69.7</td><td></td></tr><tr><td>Q4_K_M</td><td>409</td><td></td><td>67.7</td></tr><tr><td>Q5_K_M</td><td>478</td><td></td><td>68.9</td></tr><tr><td>Q5_K_XL</td><td>484</td><td>70.7</td><td></td></tr></tbody></table>

</details>

### :cake:Dynamic quantization ablations

We did some ablations as well to confirm if our calibration dataset and our dynamic quantization methodology actually works. The trick of Unsloth's dynamic method is to quantize **important layers to higher bits** say 8bits, whilst **un-important layers are left in lower bis like 2bits**.

To test our method, we leave specific tensors in lower precision like 4bit vs higher precision. For example below we leave `attn_k_b` tensors in 4bit (semi-dynamic) vs 8bit (Unsloth current), and by increasing the quant size by only \~100MB or so (<0.1%), accuracy shoots up dramatically!

{% hint style="success" %}
`attn_k_b` and other tensors in DeepSeek V3.1 are highly important / sensitive to quantization and should left in higher precision to retain accuracy!
{% endhint %}

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-3b4f8ac3af4ec8d09763c2e5f5d7de912d0b042e%2FSemi%20Dynamic.png?alt=media" alt=""><figcaption></figcaption></figure>

### :bug:Chat Template Bug Fixes

During testing of DeepSeek-V3.1 quants, we found some lower bit quants not enclosing `<think> </think>` properly or doing some weird formatting. This caused some community quants to not work on lower bits, and so this caused unfair comparisons. We found llama.cpp's usage of minja (a simpler version of jinja) does not accept positional argument in `.split`. We had to change:

```
{%- set content = content.split("</think>", 1)[1] -%}
```

to the below:

```
{%- set splitted = content.split("</think>") -%}
{%- set content = splitted[1:] | join("</think>") -%}
```

See [here](https://huggingface.co/unsloth/DeepSeek-V3.1-GGUF?chat_template=default\&format=true) for our fixed chat template or [here](https://huggingface.co/unsloth/DeepSeek-V3.1/raw/main/chat_template.jinja) for a raw jinja file.

### :bar\_chart:Pass Rate 1

Aider is reported mainly on pass rate 2. We also report pass rate 1 to compare community quants of the same size. We see our dynamic quants do much better than other community quants of similar sizes especially on smaller than 2 bit and larger than 4bits. 3 and 4 bit perform similarly well.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fgit-blob-dfea83b4ef3e0d1a1c835476270eeb4f3f6db798%2FPass%20Rate%201%20Non%20Thinking.png?alt=media" alt=""><figcaption></figcaption></figure>

## :computer:Run DeepSeek V3.1 Dynamic quants

Head over to our [DeepSeek V3.1 guide](/docs/models/tutorials/deepseek-r1-how-to-run-locally/deepseek-r1-dynamic-1.58-bit.md) or to quickly get the dynamic 2bit version, do:

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone https://github.com/ggml-org/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON -DLLAMA_CURL=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-quantize llama-cli llama-gguf-split llama-mtmd-cli llama-server
cp llama.cpp/build/bin/llama-* llama.cpp
```

then use `llama.cpp` to directly download the weights. We set the optimal suggested parameters like temperature, the chat template etc already as well:

```bash
export LLAMA_CACHE="unsloth/DeepSeek-V3.1-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/DeepSeek-V3.1-GGUF:Q2_K_XL \
    --jinja \
    --n-gpu-layers 99 \
    --temp 0.6 \
    --top-p 0.95 \
    --min-p 0.01 \
    --ctx-size 8192 \
    --seed 3407 \
    -ot ".ffn_.*_exps.=CPU"
```
