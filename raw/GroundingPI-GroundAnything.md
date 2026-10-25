---
license: other
license_name: apache-2.0-with-upstream-kimi-k3
license_link: LICENSE
language:
  - en
  - zh
library_name: transformers
pipeline_tag: image-text-to-text
tags:
  - visual-grounding
  - object-detection
  - referring-expression-comprehension
  - pointing
  - ocr
  - document-layout
  - custom-code
  - diffusion-language-model
inference: false
---

<!-- model-card-language: en -->

<a id="english"></a>

# <img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/logo.png" width="40" style="display: inline-block; vertical-align: middle; margin: 0;" alt="GroundAnything logo" /> GroundAnything: Reconciling Parallel Decoding with Precise Visual Grounding at Flash Speed

**English** | [简体中文](#chinese)

**Model family:** [GroundAnything — DLM / parallel decoding](https://huggingface.co/GroundingPI/GroundAnything) · [GroundAnything-VLM — autoregressive](https://huggingface.co/GroundingPI/GroundAnything-VLM).

**This repository contains the GroundAnything DLM checkpoint.** Use entropy-guided decoding for the main benchmark setting, or select optional self-speculative decoding.

<p align="center" style="margin: 0;"><img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/d926c66e5f0be4cad6f263fbef5cbcbe98102a42/assets/fig1-teaser.png" width="100%" alt="GroundAnything: broad visual grounding and parallel visual evidence extraction" style="display: block; margin: 0;" /></p>

## 🔗 Quick Links


- <img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/main/assets/modelscope-logo.svg" width="22" height="20" style="display: inline-block; vertical-align: middle; margin: 0;" alt="ModelScope" /> **ModelScope:** [GroundAnything (DLM)](https://www.modelscope.ai/models/GroundingPI/GroundAnything) · [GroundAnything-VLM (VLM)](https://www.modelscope.ai/models/GroundingPI/GroundAnything-VLM).
- 🚀 **Online Demo:** The GroundAnything DLM runtime is not supported on ZeroGPU.
- 🌐 **Project Page:** [GroundAnything](https://groundingpi.github.io/groundanything/).
- 💻 **GitHub Code:** [groundingpi/GroundAnything](https://github.com/groundingpi/GroundAnything).
- 📄 **Paper:** [arXiv:2609.39600](https://arxiv.org/abs/2609.39600).
- 🤗 **HF paper:** <a href="https://huggingface.co/papers/2609.39600"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fhuggingface.co%2Fapi%2Fpapers%2F2609.39600&amp;query=%24.upvotes&amp;label=&amp;prefix=%E2%86%91+&amp;suffix=+upvotes&amp;style=flat&amp;color=fef3c7&amp;cacheSeconds=300" height="20" style="display: inline-block; vertical-align: middle; margin: 0;" alt="Live upvotes" /></a>


# Model Overview

### Description:

Autoregressive (AR) grounding models serialize spatial predictions, introducing sequential latency and imposing a causal order on output tokens. We view grounding as visual evidence extraction: objects, locations, and spatial relations are jointly constrained by the image and query, yet their dependencies do not imply an intrinsic left-to-right generation order. This distinction makes bidirectional diffusion a natural fit, allowing spatial hypotheses to emerge in parallel and be jointly refined through iterative denoising.

We introduce **GroundAnything**, a 4B-parameter grounding foundation model that reconciles fast parallel decoding with precise localization through blockwise denoising. Across 30 grounding benchmarks, the autoregressive variant, **GroundAnything-VLM**, establishes a new overall state of the art among similarly sized models at **72.42%**, remaining competitive with GPT-6 Astra (**71.35%**). With **entropy-guided decoding**, GroundAnything also surpasses the prior state of the art at this scale, averaging **61.75%** versus **53.32%** for the fast MTP-based LocateAnything model.

An optional **self-speculative mode** achieves a **4.51× speedup** over the AR counterpart with a **0.74 percentage-point drop in COCO F1mIoU** at the paper's reported operating point. Infrastructure experiments show that progressive inference optimizations translate parallel decoding into practical speedups. These support efficient visual grounding in latency-sensitive real-world systems.

### Demo Videos

<video controls playsinline preload="none" width="100%" poster="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/demo-poster.jpg" src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/demo.mp4"></video>

**Parallel Decoding**

<video controls playsinline preload="none" width="100%" src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/decoding.mp4"></video>

### License/Terms of Use:

Our original contributions are available under **Apache 2.0**, with no additional restrictions imposed by this project. Third-party material retains its applicable licenses, including the **Kimi K3 License** for Kimi-derived material and applicable derivative works. Its conditions continue to apply when using or redistributing the combined model package. See [LICENSE](LICENSE) for the scope and full license texts.

### Deployment Geography:

Global.

### Use Case:

- Open-vocabulary object localization and dense-scene grounding.
- Referring-expression comprehension and visual-prompt-based localization.
- Point-based localization, spatial reasoning, and GUI element grounding.
- OCR with text localization and document layout understanding.
- Perception research for robotics, embodied agents, and autonomous systems.

### Release Date:

- **ModelScope [10/14/2026]:** Model weights are now available on ModelScope: [GroundAnything (DLM)](https://www.modelscope.ai/models/GroundingPI/GroundAnything) · [GroundAnything-VLM (VLM)](https://www.modelscope.ai/models/GroundingPI/GroundAnything-VLM).
- **HF paper [10/14/2026]:** GroundAnything received strong community recognition on [Hugging Face Papers](https://huggingface.co/papers/2609.39600), reaching **74 upvotes**.
- **Webpage [10/04/2026]:** Project webpage released: [GroundAnything](https://groundingpi.github.io/groundanything/).
- **Code [10/03/2026]:** GitHub code released: [GroundAnything](https://github.com/groundingpi/GroundAnything).
- **Paper [09/30/2026]:** [GroundAnything](https://arxiv.org/abs/2609.39600).


<details>
<summary>Citation</summary>

```bibtex
@misc{yu2026groundanythingreconcilingparalleldecoding,
  title = {{GroundAnything}: Reconciling Parallel Decoding with Precise Visual Grounding at Flash Speed},
  author = {Qize Yu and Lianrui Fan and Bowen Ping and Xini Ding and Zetian Song and Junbo Niu and Kaixuan Wang and Tianxing Chen and Yue Chen and Minghua He and Yuran Wang and Jie Huang and Haojun Zhang and Min Chen and Hao Li and Wenxuan Song and Ruihai Wu and Xianming Liu and Shilong Liu and Shuchang Zhou and Ping Luo and Shiyu Huang},
  year = {2026},
  eprint = {2609.39600},
  archivePrefix = {arXiv},
  primaryClass = {cs.CV},
  url = {https://arxiv.org/abs/2609.39600},
}
```

</details>

## Model Architecture:

**Architecture type:** a shared vision-language backbone supporting an autoregressive checkpoint and a blockwise diffusion checkpoint.

- **Vision encoder:** MoonViT-V2 / Kimi-K3 vision backbone.
- **Language backbone:** Qwen3-4B-Instruct-2507.
- **Multimodal projector:** 2 × 2 spatial aggregation and a two-layer MLP.
- **Spatial vocabulary:** 1,000 coordinate tokens shared with semantic labels and protocol markers.
- **DLM conversion:** the shared decoder and vocabulary head support both causal prediction and bidirectional response-block denoising. A mask token is added for diffusion generation.

<p align="center"><img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/fig2-architecture.png" width="100%" alt="GroundAnything: vision-language architecture and autoregressive-to-diffusion conversion" /></p>

## Input(s):

**Input types:** image and text.

- **Image:** one RGB image per request. The Python client accepts JPEG, PNG, and WebP files; the supplied processor handles image preparation.
- **Text:** a natural-language instruction, category list, referring expression, OCR/layout query, or a prompt containing example boxes.
- **Image encoding for the HTTP API:** an `image_url` content part containing a base64 data URI, alongside a `text` content part.

Use the checkpoint's own tokenizer, processor, and chat template. Multiple categories are separated by `</c>`. Reference boxes use the same 0–999 spatial-token vocabulary as outputs.

## Output(s):

**Output type:** text containing semantic labels and quantized spatial coordinates.

All three released models use the **GAM protocol**: integer coordinate tokens `<0>` through `<999>`, object-reference delimiters, and box delimiters. A bounding box contains `(x1, y1, x2, y2)`; a point contains `(x, y)`. Adjacent coordinate tokens have no intervening spaces. Multiple instances of the same label are comma-separated inside one box wrapper. A missing target is represented by `None`.

Illustrative syntax:

```text
<|object_ref_start|>car<|object_ref_end|><|box_start|><100><200><500><650><|box_end|>
<|object_ref_start|>car center<|object_ref_end|><|box_start|><300><425><|box_end|>
<|object_ref_start|>absent object<|object_ref_end|><|box_start|>None<|box_end|>
```

The client returns parsed predictions together with `raw_output`, `finish_reason`, `usage`, `parse_error`, and `valid`. It maps coordinates back to image pixels for visualization. A truncated or malformed response is marked invalid. For custom API clients, preserve spatial tokens with `skip_special_tokens=false` and avoid inserting spaces between them.

## Software Integration:

**Runtime engines:** the repository's custom **SGLang** integration for the DLM and VLM services, plus a native Transformers reference route for the DLM.

**Default serving environment:** Linux and Python 3.12 with the source package's serving profile. Use `python3 run.py setup serve` to install the bundled custom engine and its pinned dependencies; installing upstream SGLang alone does not provide the same model and decoding integration.

The serving profile pins Torch **2.9.1**, Transformers **5.5.4**, Triton **3.5.1**, sgl-kernel **0.3.20**, and FlashInfer **0.5.3**. Serving and evaluation use separate environments.

**Tested hardware:** NVIDIA **B300, B200, H200, H800**, and **PPU**. The provided SGLang serving installer is a CUDA/GPU recipe; PPU requires its matching platform runtime and is not selected by this GPU installer.

The default DLM service uses **BF16, Triton attention, eager execution, one GPU, one active request, and two queued requests**. Client concurrency queues requests; it does not imply a multi-request model batch. CUDA Graph and selective FP8 are discussed below as separate infrastructure experiments.

## Model Version(s):

| Checkpoint | Generation | Evaluation mode |
|:---|:---|:---|
| [GroundAnything](https://huggingface.co/GroundingPI/GroundAnything) | Entropy-guided blockwise diffusion; optional self-speculation | **GAM** |
| [GroundAnything-VLM](https://huggingface.co/GroundingPI/GroundAnything-VLM) | Autoregressive generation | **GAM** |

GroundAnything's main results use **entropy-guided decoding**; GroundAnything-VLM uses **autoregressive decoding**. Self-speculative decoding is an optional acceleration mode.

## Evaluation

The evaluation toolkit supports **7 modes**:

| Mode | Supported models |
|:---|:---|
| **`GAM`** | **GroundingPI, GroundAnything, GroundAnything-VLM** |
| `VLM` | Generic vision-language baselines |
| `REXOMNI` | Rex-Omni |
| `LOCATEANYTHING` | LocateAnything |
| `GROUNDINGDINO` | GroundingDINO through a compatible service |
| `DLM` | Legacy diffusion checkpoints using the GAM protocol |
| `RLV2` | Legacy RL checkpoints using the GAM protocol |

**All three released checkpoints use GAM mode.**

Evaluation code and instructions: [GitHub](https://github.com/groundingpi/GroundAnything).

## Quantitative Evaluation Benchmarks

<p align="center"><img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/fig7-grounding-performance.png" width="100%" alt="GroundAnything: GroundAnything and GroundAnything-VLM benchmark overview" /></p>

## Inference:

### Installation

Run the commands from the **GroundAnything source repository root** after obtaining the code package, using **Linux x86_64 and Python 3.12**. Use the serving profile in the supplied source bundle so that the custom model adapter, decoding implementation, and dependencies remain aligned.

```bash
python3 -m pip install -r requirements.txt huggingface_hub
python3 run.py setup serve
```

The installer verifies and extracts its bundled frameworks, creates `.venv-serve`, and records resolved packages. It prepares the custom SGLang implementation and applies the serving profile's dependency order. The profile includes the required cuDNN compatibility selection; its dependency-check report records the known Torch/cuDNN metadata exception.

**Choose the checkpoint-specific recipe below.** GroundAnything-VLM users need only the VLM download and launch commands; the DLM commands require the separate GroundAnything weights.

### GroundAnything: Entropy-guided Service

Download the **complete DLM model bundle**, including its custom code and tokenizer, then launch:

```bash
hf download GroundingPI/GroundAnything --local-dir weights/dlm_bundle
python3 run.py serve --decoder denoise
```

The published model package is already a DLM bundle, so `prepare-model` is unnecessary for this download. The endpoint is `http://127.0.0.1:8101/v1`, with model ID `groundinganything`.

### GroundAnything: Self-speculative Service

Stop the existing DLM service before switching its decoder:

```bash
python3 run.py serve --decoder speculative
```

This reuses the same DLM weights and endpoint, with diffusion proposals and greedy causal verification.

### GroundAnything-VLM: Autoregressive Service

Use the separate autoregressive checkpoint and its service recipe:

```bash
hf download GroundingPI/GroundAnything-VLM --local-dir weights/vlm
python3 run.py serve --config configs/release/vlm_sglang.yaml
```

This service uses `http://127.0.0.1:8102/v1`, with model ID `groundinganything-vlm`. The two repositories share the spatial interface but have different loading and generation paths.

### Worker (recommended)

Start the appropriate service once, then reuse the client:

```python
from grounding_anything import GroundingAnything, visualize

client = GroundingAnything(
    base_url="http://127.0.0.1:8101/v1",
    model="groundinganything",
)
result = client.predict("example.jpg", "the red car", task="bbox")
print(result.to_dict())
if result.valid:
    visualize("example.jpg", result).save("prediction.png")

point_result = client.predict(
    "example.jpg", "the center of the red car", task="point"
)
```

The HTTP client retains no model weights.

### Supported Tasks & Prompt Templates

| Task | Prompt example |
|:---|:---|
| Category / dense grounding | `Locate all the instances that match the following categories: car</c>person.` |
| Referring boxes | `Locate the target referred to by the following description: the red car.` |
| Category points | `Point to: car</c>person.` |
| Referring points | `Point to the target referred to by the following description: the red car.` |
| OCR | `OCR task detect all the text in box format.` |
| Layout | `Detect all document layout elements that match the following categories: title</c>text.` |
| GUI | `Point to the UI element to click for the following instruction: open the settings menu.` |
| Visual prompting | Provide reference boxes in the native spatial-token format, then request similar objects. |

```text
Given reference boxes <|box_start|><100><200><500><650><|box_end|> indicating one or more objects, find all similar objects in the image and output their bounding boxes.
```

The convenience client's `predict()` method wraps referring-box and referring-point prompts. Use an OpenAI-compatible request to `/chat/completions` for the other task templates; keep the image and prompt in the same user message.

### Generation Modes

#### Entropy-guided decoding

Image/query prefill creates a causal prefix cache and a known anchor. The release recipe uses **block size 32, sub-block size 4, and entropy threshold 0.8**. A physical block contains the known anchor and 31 masked positions; sub-blocks are completed from left to right while the forward pass evaluates the physical block.

For each still-masked position in the active sub-block, the decoder measures entropy from the unmodified token distribution over the generatable vocabulary, excluding the mask token. Positions at or below the threshold are committed together. If no position qualifies, the lowest-entropy position is committed so decoding makes progress. Committed tokens remain fixed.

After a block is complete, a causal forward reconstructs its authoritative KV cache and supplies the next anchor. This cache-building pass **does not verify or reject the generated block**. A block requiring D denoising passes therefore uses D + 1 model forwards, excluding the initial prefill.

#### Self-speculative decoding

The model uses its own shared weights to draft tokens with bidirectional attention and verify them with causal attention. Verification accepts the **longest consecutive matching prefix**, stops at the first mismatch, applies the causal correction, and discards the rejected suffix cache states. The shipped speculative route uses greedy verification; it is not a general stochastic speculative sampler.

<p align="center"><img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/fig6-self-speculative-decoding.png" width="100%" alt="GroundAnything: linear and quadratic self-speculative schedules with shared model weights" /></p>

The documented `--decoder speculative` service is the linear shared-weight route. Exact greedy verification is relative to the converted model's causal branch; it does not imply identical outputs to the separately trained GroundAnything-VLM checkpoint.

## Inference Infrastructure

### SGLang Execution

The custom SGLang integration coordinates model loading, request scheduling, attention kernels, and KV-cache ownership for blockwise generation. Denoising uses bidirectional attention inside the active block; completed history is retained as causal KV. Self-speculation additionally verifies proposals and removes rejected suffix states. These cache semantics must be preserved when optimizing execution.

The supplied recipe selects **BF16 + Triton attention + eager execution**. DLM recipes record the engine source, decoder, effective settings, and package versions in `outputs/sglang/<decoder>/engine_runtime.json`. The VLM service records its causal model/runtime configuration separately in `outputs/sglang/vlm/engine_runtime.json`. For higher service concurrency, use independent replicas with distinct devices, ports, and output directories; the default queue is not continuous multi-request batching.

### CUDA Graph and Selective FP8

The paper evaluates a progressive infrastructure sequence:

| Layer | Purpose | Status in the supplied default recipe |
|:---|:---|:---|
| Native PyTorch eager | Reference model execution | Reference implementation |
| SGLang eager | Integrated scheduling, attention, and cache execution | **Default serving path** |
| CUDA Graph replay | Replay compatible captured GPU work to reduce repeated launch overhead | Evaluated in the paper; **disabled by the default launcher** |
| Selective FP8 | Reduce arithmetic cost in eligible language-model linear operations while retaining other components in BF16 | Evaluated in the paper; **default serving remains BF16** |

CUDA Graph changes how compatible GPU work is submitted; it does not define a new token-commitment or verification rule. Captured shapes and state updates must remain compatible with the active decoding path. Selective FP8 can change logits and subsequent decoding decisions, so it is a distinct numerical configuration.

The optional graph implementation captures fixed-shape block work. Its FlashInfer path uses persistent attention masks and device-resident buffer updates for bidirectional drafting and causal verification. The Triton verifier path separates draft/verification metadata and input buffers while sharing parameters and the real KV pool. Its supported capture case is B32 with one request and no tensor/pipeline/data parallel expansion; prefill and unsupported shapes use eager execution. Optional shadow checks compare cache states, logits, and token choices against eager execution. These implementation paths are not exposed as a public `run.py serve --cuda-graph` switch in this release.

The paper's cumulative infrastructure speedups compare execution implementations **within the same decoding mode**. They are separate from the headline comparison of self-speculation against the autoregressive checkpoint. The default release commands above do not enable Graph replay or FP8, and no unsupported activation flags are implied.

## Ethical Considerations:

Grounding predictions can miss small or occluded objects, repeat instances, or produce inaccurate text and coordinates. Validate localization quality on the intended task and inspect incomplete responses. GUI points describe image locations; the model does not execute interface actions. Perception outputs require task-specific validation before integration into physical systems.

---

<!-- model-card-language: zh-CN -->

<a id="chinese"></a>

# <img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/logo.png" width="40" style="display: inline-block; vertical-align: middle; margin: 0;" alt="GroundAnything 标志" /> GroundAnything：以极速并行解码实现精准视觉定位

[English](#english) | **简体中文**

**模型系列：** [GroundAnything — DLM / 并行解码](https://huggingface.co/GroundingPI/GroundAnything) · [GroundAnything-VLM — 自回归](https://huggingface.co/GroundingPI/GroundAnything-VLM)。

**本仓库提供 GroundAnything DLM 模型。** 主要基准评测采用熵引导解码，也可选择自推测解码。

<p align="center" style="margin: 0;"><img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/d926c66e5f0be4cad6f263fbef5cbcbe98102a42/assets/fig1-teaser.png" width="100%" alt="GroundAnything：广泛的视觉定位与并行视觉证据提取" style="display: block; margin: 0;" /></p>

## 🔗 快速链接


- <img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/main/assets/modelscope-logo.svg" width="22" height="20" style="display: inline-block; vertical-align: middle; margin: 0;" alt="ModelScope" /> **ModelScope：** [GroundAnything（DLM）](https://www.modelscope.ai/models/GroundingPI/GroundAnything) · [GroundAnything-VLM（VLM）](https://www.modelscope.ai/models/GroundingPI/GroundAnything-VLM)。
- 🚀 **在线演示：** ZeroGPU 不支持 GroundAnything DLM 运行时。
- 🌐 **项目主页：** [GroundAnything](https://groundingpi.github.io/groundanything/)。
- 💻 **GitHub 代码：** [groundingpi/GroundAnything](https://github.com/groundingpi/GroundAnything)。
- 📄 **论文：** [arXiv:2609.39600](https://arxiv.org/abs/2609.39600)。
- 🤗 **HF 论文：** <a href="https://huggingface.co/papers/2609.39600"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fhuggingface.co%2Fapi%2Fpapers%2F2609.39600&amp;query=%24.upvotes&amp;label=&amp;prefix=%E2%86%91+&amp;suffix=+upvotes&amp;style=flat&amp;color=fef3c7&amp;cacheSeconds=300" height="20" style="display: inline-block; vertical-align: middle; margin: 0;" alt="实时赞同票" /></a>


# 模型概述

### 简介：

自回归（AR）视觉定位模型将空间预测串行化，带来顺序生成的延迟，并为输出 token 施加因果顺序。我们将视觉定位视为视觉证据提取：物体、位置和空间关系共同受到图像与查询的约束，但它们之间的依赖关系并不意味着生成过程必须从左到右进行。这一区别使双向扩散成为自然的选择，让空间假设能够并行产生，并通过迭代去噪共同细化。

我们提出 <strong>GroundAnything</strong>，一个拥有 4B 参数的视觉定位基础模型，通过分块去噪兼顾快速并行解码与精确定位。在 30 个视觉定位基准上，自回归版本 <strong>GroundAnything-VLM</strong> 以 <strong>72.42%</strong> 的综合表现刷新了同等规模模型的最佳水平，并与 GPT-6 Astra（<strong>71.35%</strong>）保持竞争力。采用<strong>熵引导解码</strong>的 GroundAnything 同样超越了这一规模下此前的最佳水平，平均达到 <strong>61.75%</strong>，高于基于 MTP 的快速模型 LocateAnything 的 <strong>53.32%</strong>。

在论文报告的运行配置下，可选的**自推测模式**相较自回归版本实现了 **4.51× 加速**，同时 **COCO F1mIoU 下降 0.74 个百分点**。基础设施实验表明，逐步优化推理实现能够将并行解码转化为实际加速，为对延迟敏感的实际系统提供高效的视觉定位能力。

### 演示视频

<video controls playsinline preload="none" width="100%" poster="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/demo-poster.jpg" src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/demo.mp4"></video>

**并行解码**

<video controls playsinline preload="none" width="100%" src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/decoding.mp4"></video>

### 许可证与使用条款：

我们的原创贡献采用 **Apache 2.0** 许可证，本项目不额外施加限制。第三方材料保留其适用的许可证，其中源自 Kimi 的材料及适用的衍生作品遵循 **Kimi K3 License**。使用或再分发组合后的模型包时，这些条款仍然适用。许可范围与完整许可文本请参阅 [LICENSE](LICENSE)。

### 部署地域：

全球。

### 应用场景：

- 开放词汇目标定位与密集场景视觉定位。
- 指代表达理解与基于视觉提示的定位。
- 点定位、空间推理和 GUI 元素定位。
- 文本定位与 OCR，以及文档版面理解。
- 面向机器人、具身智能体和自主系统的感知研究。

### 发布日志：

- **ModelScope [10/14/2026]：** 模型权重已在 ModelScope 发布：[GroundAnything（DLM）](https://www.modelscope.ai/models/GroundingPI/GroundAnything) · [GroundAnything-VLM（VLM）](https://www.modelscope.ai/models/GroundingPI/GroundAnything-VLM)。
- **HF paper [10/14/2026]：** GroundAnything 在 [Hugging Face Papers](https://huggingface.co/papers/2609.39600) 获得巨大认可，收获 **74 个 Upvote**。
- **网页 [10/04/2026]：** 项目网页发布：[GroundAnything](https://groundingpi.github.io/groundanything/)。
- **代码 [10/03/2026]：** GitHub 代码发布：[GroundAnything](https://github.com/groundingpi/GroundAnything)。
- **论文 [09/30/2026]：** [GroundAnything](https://arxiv.org/abs/2609.39600)。


<details>
<summary>引用</summary>

```bibtex
@misc{yu2026groundanythingreconcilingparalleldecoding,
  title = {{GroundAnything}: Reconciling Parallel Decoding with Precise Visual Grounding at Flash Speed},
  author = {Qize Yu and Lianrui Fan and Bowen Ping and Xini Ding and Zetian Song and Junbo Niu and Kaixuan Wang and Tianxing Chen and Yue Chen and Minghua He and Yuran Wang and Jie Huang and Haojun Zhang and Min Chen and Hao Li and Wenxuan Song and Ruihai Wu and Xianming Liu and Shilong Liu and Shuchang Zhou and Ping Luo and Shiyu Huang},
  year = {2026},
  eprint = {2609.39600},
  archivePrefix = {arXiv},
  primaryClass = {cs.CV},
  url = {https://arxiv.org/abs/2609.39600},
}
```

</details>

## 模型架构：

**架构类型：** 共享视觉语言主干，支持自回归模型和分块扩散模型。

- **视觉编码器：** MoonViT-V2 / Kimi-K3 视觉主干。
- **语言主干：** Qwen3-4B-Instruct-2507。
- **多模态投影器：** 2 × 2 空间聚合与两层 MLP。
- **空间词表：** 1,000 个坐标 token，与语义标签和协议标记共用词表。
- **DLM 转换：** 共享解码器与词表输出头同时支持因果预测和双向响应块去噪，并为扩散生成加入掩码 token。

<p align="center"><img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/fig2-architecture.png" width="100%" alt="GroundAnything：视觉语言架构与自回归到扩散的转换" /></p>

## 输入：

**输入类型：** 图像与文本。

- **图像：** 每个请求包含一张 RGB 图像。Python 客户端支持 JPEG、PNG 和 WebP 文件；随模型提供的处理器负责图像预处理。
- **文本：** 自然语言指令、类别列表、指代表达、OCR/版面查询，或包含示例框的提示词。
- **HTTP API 的图像编码：** 在 `image_url` 内容项中提供 base64 data URI，并配合一个 `text` 内容项。

请使用模型自带的分词器、处理器和对话模板。多个类别使用 `</c>` 分隔。参考框与输出使用相同的 0–999 空间 token 词表。

## 输出：

**输出类型：** 包含语义标签和量化空间坐标的文本。

三个已发布模型均采用 **GAM 协议**：使用 `<0>` 至 `<999>` 的整数坐标 token、目标引用分隔符和框分隔符。边界框包含 `(x1, y1, x2, y2)`，点包含 `(x, y)`。相邻坐标 token 之间没有空格。同一标签下的多个实例在同一组框分隔符内以逗号分隔。未找到的目标用 `None` 表示。

语法示例：

```text
<|object_ref_start|>car<|object_ref_end|><|box_start|><100><200><500><650><|box_end|>
<|object_ref_start|>car center<|object_ref_end|><|box_start|><300><425><|box_end|>
<|object_ref_start|>absent object<|object_ref_end|><|box_start|>None<|box_end|>
```

客户端返回解析后的预测结果，以及 `raw_output`、`finish_reason`、`usage`、`parse_error` 和 `valid` 字段，并将坐标映射回图像像素以便可视化。被截断或格式不正确的响应会标记为无效。自定义 API 客户端应使用 `skip_special_tokens=false` 保留空间 token，并避免在这些 token 之间插入空格。

## 软件集成：

**运行引擎：** 仓库定制的 **SGLang** 集成支持 DLM 和 VLM 服务；此外还提供 DLM 的原生 Transformers 参考路径。

**默认服务环境：** Linux、Python 3.12，以及源码包提供的服务配置。使用 `python3 run.py setup serve` 安装随包提供的定制引擎及固定版本依赖；仅安装上游 SGLang 无法获得相同的模型适配与解码集成。

服务配置固定使用 Torch **2.9.1**、Transformers **5.5.4**、Triton **3.5.1**、sgl-kernel **0.3.20** 和 FlashInfer **0.5.3**。服务与评测使用独立环境。

**已测试硬件：** NVIDIA **B300、B200、H200、H800**，以及 **PPU**。提供的 SGLang 服务安装器面向 CUDA/GPU；PPU 需要对应的平台运行时，该 GPU 安装器不会选择 PPU 运行环境。

默认 DLM 服务采用 **BF16、Triton 注意力、eager 执行、单 GPU、一个活动请求和两个排队请求**。客户端并发会使请求进入队列，并不意味着模型以多请求批次运行。CUDA Graph 与选择性 FP8 作为独立的基础设施实验，在下文说明。

## 模型版本：

| 模型 | 生成方式 | 评测模式 |
|:---|:---|:---|
| [GroundAnything](https://huggingface.co/GroundingPI/GroundAnything) | 熵引导分块扩散；可选自推测解码 | **GAM** |
| [GroundAnything-VLM](https://huggingface.co/GroundingPI/GroundAnything-VLM) | 自回归生成 | **GAM** |

GroundAnything 的主要结果使用**熵引导解码**；GroundAnything-VLM 使用**自回归解码**。自推测解码是一种可选加速模式。

## 评测

评测工具包支持 **7 种模式**：

| 模式 | 支持的模型 |
|:---|:---|
| **`GAM`** | **GroundingPI、GroundAnything、GroundAnything-VLM** |
| `VLM` | 通用视觉语言基线模型 |
| `REXOMNI` | Rex-Omni |
| `LOCATEANYTHING` | LocateAnything |
| `GROUNDINGDINO` | 通过兼容服务接入的 GroundingDINO |
| `DLM` | 使用 GAM 协议的旧版扩散模型 |
| `RLV2` | 使用 GAM 协议的旧版 RL 模型 |

**三个已发布模型均使用 GAM 模式。**

评测代码与使用说明：[GitHub](https://github.com/groundingpi/GroundAnything)。

## 定量评测

<p align="center"><img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/fig7-grounding-performance.png" width="100%" alt="GroundAnything：GroundAnything 与 GroundAnything-VLM 的基准表现概览" /></p>

## 推理：

### 安装

获取代码包后，请在 **GroundAnything 源码仓库根目录**中运行以下命令，环境为 **Linux x86_64 和 Python 3.12**。使用源码包提供的服务配置，以确保定制模型适配器、解码实现与依赖保持一致。

```bash
python3 -m pip install -r requirements.txt huggingface_hub
python3 run.py setup serve
```

安装器会校验并解压随包提供的框架，创建 `.venv-serve`，并记录解析后的依赖包。它会准备定制的 SGLang 实现，并按照服务配置指定的依赖顺序完成安装。配置中包含必要的 cuDNN 兼容性选择；依赖检查报告会记录已知的 Torch/cuDNN 元数据例外。

**请根据所用模型选择下方对应的配置。** GroundAnything-VLM 用户只需执行 VLM 的下载和启动命令；DLM 命令需要另外下载 GroundAnything 权重。

### GroundAnything：熵引导服务

下载**完整的 DLM 模型包**，包括定制代码与分词器，然后启动服务：

```bash
hf download GroundingPI/GroundAnything --local-dir weights/dlm_bundle
python3 run.py serve --decoder denoise
```

已发布的模型包本身就是 DLM 模型包，因此本次下载无需运行 `prepare-model`。服务地址为 `http://127.0.0.1:8101/v1`，模型 ID 为 `groundinganything`。

### GroundAnything：自推测服务

切换解码器前，先停止现有 DLM 服务：

```bash
python3 run.py serve --decoder speculative
```

该模式复用相同的 DLM 权重和服务地址，采用扩散候选生成与贪心因果验证。

### GroundAnything-VLM：自回归服务

使用独立的自回归模型及其服务配置：

```bash
hf download GroundingPI/GroundAnything-VLM --local-dir weights/vlm
python3 run.py serve --config configs/release/vlm_sglang.yaml
```

该服务使用 `http://127.0.0.1:8102/v1`，模型 ID 为 `groundinganything-vlm`。两个仓库共用空间输出接口，但模型加载和生成路径不同。

### Worker（推荐）

启动相应服务后，即可重复使用客户端：

```python
from grounding_anything import GroundingAnything, visualize

client = GroundingAnything(
    base_url="http://127.0.0.1:8101/v1",
    model="groundinganything",
)
result = client.predict("example.jpg", "the red car", task="bbox")
print(result.to_dict())
if result.valid:
    visualize("example.jpg", result).save("prediction.png")

point_result = client.predict(
    "example.jpg", "the center of the red car", task="point"
)
```

HTTP 客户端不持有模型权重。

### 支持的任务与提示词模板

| 任务 | 提示词示例 |
|:---|:---|
| 类别 / 密集目标定位 | `Locate all the instances that match the following categories: car</c>person.` |
| 指代表达框定位 | `Locate the target referred to by the following description: the red car.` |
| 类别点定位 | `Point to: car</c>person.` |
| 指代表达点定位 | `Point to the target referred to by the following description: the red car.` |
| OCR | `OCR task detect all the text in box format.` |
| 版面 | `Detect all document layout elements that match the following categories: title</c>text.` |
| GUI | `Point to the UI element to click for the following instruction: open the settings menu.` |
| 视觉提示 | 以原生空间 token 格式提供参考框，再请求定位相似物体。 |

```text
Given reference boxes <|box_start|><100><200><500><650><|box_end|> indicating one or more objects, find all similar objects in the image and output their bounding boxes.
```

便捷客户端的 `predict()` 方法封装了指代表达框定位和点定位提示词。其他任务模板请通过兼容 OpenAI 的请求调用 `/chat/completions`；图像与提示词应放在同一条用户消息中。

### 生成模式

#### 熵引导解码

图像与查询的预填充会建立因果前缀缓存和一个已知锚点。发布配置采用**块大小 32、子块大小 4、熵阈值 0.8**。一个物理块包含已知锚点和 31 个掩码位置；子块从左到右依次完成，而每次前向计算覆盖整个物理块。

对于当前子块中仍被掩码覆盖的每个位置，解码器基于可生成词表上未经修改的 token 分布计算熵，其中不包含掩码 token。熵不高于阈值的位置会被同时确定。如果没有位置满足阈值，则确定熵最低的位置，以保证解码继续推进。已确定的 token 保持不变。

一个块完成后，通过一次因果前向计算重建该块的正式 KV 缓存，并提供下一个锚点。这次缓存构建**不会验证或拒绝已生成的块**。因此，一个需要 D 次去噪的块会执行 D + 1 次模型前向计算，不计最初的预填充。

#### 自推测解码

模型使用自身共享的权重，通过双向注意力生成候选 token，再通过因果注意力进行验证。验证接受**最长的连续匹配前缀**，在首次不匹配处停止，应用因果分支的修正，并丢弃被拒绝后缀的缓存状态。发布的推测路径采用贪心验证，并非通用的随机推测采样器。

<p align="center"><img src="https://huggingface.co/GroundingPI/GroundAnything/resolve/20fda7044a5850df0c773831bd3b94ce9cf1b127/assets/fig6-self-speculative-decoding.png" width="100%" alt="GroundAnything：共享模型权重的线性与二次自推测调度" /></p>

文档中的 `--decoder speculative` 服务采用线性的共享权重路径。精确贪心验证是相对于转换后模型的因果分支而言，并不意味着其输出与单独训练的 GroundAnything-VLM 模型相同。

## 推理基础设施

### SGLang 执行

定制的 SGLang 集成负责协调模型加载、请求调度、注意力内核，以及分块生成过程中的 KV 缓存管理。去噪在当前块内部使用双向注意力，已完成的历史内容则保留为因果 KV。自推测解码还会验证候选并移除被拒绝的后缀状态。优化执行过程时，必须保留这些缓存语义。

提供的配置选择 **BF16 + Triton 注意力 + eager 执行**。DLM 配置将引擎来源、解码器、实际生效设置和依赖包版本记录在 `outputs/sglang/<decoder>/engine_runtime.json` 中。VLM 服务则在 `outputs/sglang/vlm/engine_runtime.json` 中单独记录其因果模型与运行时配置。如需提高服务并发量，可部署使用不同设备、端口和输出目录的独立副本；默认队列并非多请求连续批处理。

### CUDA Graph 与选择性 FP8

论文评估了逐步叠加的基础设施优化：

| 层级 | 目的 | 提供的默认配置中的状态 |
|:---|:---|:---|
| 原生 PyTorch eager | 模型执行参考路径 | 参考实现 |
| SGLang eager | 集成调度、注意力与缓存执行 | **默认服务路径** |
| CUDA Graph 重放 | 重放已捕获且兼容的 GPU 操作，减少重复启动开销 | 论文已评估；**默认启动器禁用** |
| 选择性 FP8 | 降低适用的语言模型线性运算的计算成本，其他组件保留 BF16 | 论文已评估；**默认服务仍使用 BF16** |

CUDA Graph 改变的是兼容 GPU 操作的提交方式，不会定义新的 token 确定或验证规则。捕获的形状与状态更新必须兼容当前解码路径。选择性 FP8 可能改变 logits 以及后续的解码决策，因此属于不同的数值配置。

可选的图实现会捕获固定形状的块计算。其 FlashInfer 路径采用持久化注意力掩码和设备端缓冲区更新，支持双向候选生成与因果验证。Triton 验证器路径将候选生成与验证的元数据和输入缓冲区分开，同时共享参数与实际 KV 池。支持的捕获场景为 B32、单请求，且不扩展张量、流水线或数据并行；预填充和不支持的形状采用 eager 执行。可选的影子检查会将缓存状态、logits 和 token 选择与 eager 执行结果进行对比。本次发布没有通过公开的 `run.py serve --cuda-graph` 开关提供这些实现路径。

论文中的基础设施累计加速是在**同一种解码模式内**比较不同执行实现得到的，与自推测解码相对于自回归模型的主要加速对比相互独立。上方默认发布命令不会启用 Graph 重放或 FP8，也不表示存在未提供的启用参数。

## 伦理考量：

视觉定位预测可能遗漏较小或被遮挡的目标、重复输出实例，或产生不准确的文本与坐标。请针对目标任务验证定位质量，并检查不完整的响应。GUI 点表示图像中的位置，模型本身不会执行界面操作。感知输出在集成到物理系统前，需要进行针对具体任务的验证。

<!-- /model-card-languages -->
