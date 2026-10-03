---
license: other
license_name: qwen-research
base_model: Qwen/Qwen-Image-2.1
library_name: diffusers
pipeline_tag: text-to-image
tags:
  - qwen
  - image-generation
  - image-editing
  - rgba
  - lora
  - distilled
  - few-step
---
<!-- header start -->
<!-- 200823 -->
<p align="center">
  <img src="assets/Pruna-Qwen-Image-2.1.png" width="800">
</p>
<!-- header end -->

<p align="center">
  <a href="https://github.com/PrunaAI/pruna">
    <img src="https://img.shields.io/badge/GitHub-PrunaAI-9334E9?style=plastic&logo=github&logoColor=white" alt="GitHub">
  </a>
  &nbsp;
  <a href="https://twitter.com/PrunaAI">
    <img src="https://img.shields.io/badge/Twitter%2FX-@PrunaAI-9334E9?style=plastic&logo=x&logoColor=white" alt="Twitter/X">
  </a>
  &nbsp;
  <a href="https://www.linkedin.com/company/pruna-ai">
    <img src="https://img.shields.io/badge/LinkedIn-PrunaAI-9334E9?style=plastic&logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
  &nbsp;
  <a href="https://discord.com/invite/JFQmtFKCjd">
    <img src="https://img.shields.io/badge/Discord-Join%20us-9334E9?style=plastic&logo=discord&logoColor=white" alt="Discord">
  </a>
  &nbsp;
  <a href="https://dashboard.pruna.ai/login?utm_source=huggingface&utm_medium=org_card&utm_campaign=hf_traffic">
    <img src="https://img.shields.io/badge/Performance%20Models-Try%20them%20now-9334E9?style=plastic&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MTEiIGhlaWdodD0iNDc3IiBmaWxsPSJub25lIj48cGF0aCBmaWxsPSIjZmZmIiBkPSJNMjMuNzAzIDMwMC41MzJjLTEuODQyLS42NzQtNC4xNDItMS4wNTctNS43MDMtMi4wMjktMTIuNTU4LTcuODQ2LTguODM3LTI1LjE3MiA1LjI1NS0yOC4zNjFhLjY2LjY2IDAgMCAwIC4zNDgtLjIwMS42LjYgMCAwIDAgLjE1Ni0uMzZxNi40OS04MS45ODYgNjguNTc3LTEzNC42MjlhLjM0LjM0IDAgMCAwIC4wOTItLjEyNS4zMy4zMyAwIDAgMC0uMDI2LS4zLjMzLjMzIDAgMCAwLS4xMTItLjEwOGMtNC4xMTUtMi40OTctOC42NC00Ljc1LTEyLjM1My03LjQ0M2ExOTAgMTkwIDAgMCAxLTE4Ljc5NC0xNS41MjJjLTIuOTM2LTIuNzY4LTMuNzAzLTUuODkxLjU4LTcuNzdhLjUuNSAwIDAgMCAuMjgtLjYwOEM1MyA3NS45NSA0OC40MTcgNDguNTk5IDQ1LjUxOCAxOS42NXEtLjM5My0zLjg1Mi0uMjcxLTYuMzJhLjc1Ljc1IDAgMCAxIC4xMzQtLjQuNy43IDAgMCAxIC4zMjQtLjI1NXEyLjEwNC0uODQyIDUuODQ0LTEuNDMxYzU4LjExNC05LjEzNiAxMjcuMDA5IDguNDI1IDE0NC4zMDcgNzIuNjQ1cS4xMDMuMzY0LjE3OCAwIDUuMDk2LTI0LjA5NyA0LjYzOC00OC4xOTMtLjA0Ny0yLjc4NyAxLjg3OS00Ljc4OCAxMC40MDctMTAuOCAyNC43OTgtOC42ODdjNy40NzEgMS4wOTUgNy43NDIgNC42MzggNy4yMDkgMTEuMWEzMzQgMzM0IDAgMCAxLTExLjg4NCA2NC43MDYuMzg4LjM4OCAwIDAgMCAuMTgyLjQ0NC40LjQgMCAwIDAgLjE2NC4wNTFjOTIuNDIxIDguNDUzIDE1OC44NzUgNzkuNDg5IDE2NS4wODQgMTcxLjI3NGExIDEgMCAwIDAgLjEyOS40MjQuODMuODMgMCAwIDAgLjI5MS4yOTZjMy43NSAyLjE3IDYuMiAyLjIxNiA4Ljg1NSA2LjU5MiA1LjA2OCA4LjMzMiAxLjQ1IDIwLjQzMS04LjU5MyAyMi40N2ExLjcxIDEuNzEgMCAwIDAtMS4zNjUgMS40NjhxLTkuMTczIDc1LjM4My02NC43NjIgMTIzLjM3MWMtMjguNjIyIDI0LjcwNC02NS43NDQgMzkuNzQ5LTEwMy40NjQgNDIuMzMtMTAwLjM1OSA2Ljg2My0xODQuNDg2LTY1LjYyMi0xOTUuMDA1LTE2NS41N2EuOC44IDAgMCAwLS4xNTQtLjM5NS43NC43NCAwIDAgMC0uMzMzLS4yNU0xNTEuMzM4IDk3LjY0M2wxOS4wNjYgMTkuMzc1YS41LjUgMCAwIDAgLjE1LjEuNS41IDAgMCAwIC4xNzYuMDMxLjQzLjQzIDAgMCAwIC4zMTktLjE1cTEwLjg0Ny0xMi40NjUgNy40NDMtMjguMTU1Yy00LjUzNS0yMC44Ni0xOC41OTgtMzcuNjY0LTM3LjI3MS00OC4zODktMjEuMDY3LTEyLjY4OS00Ny44NjUtMTUuOTA1LTcyLjI4LTE0Ljg0cS0uNjE3LjAzLS4xNC40MjJsNjMuNDcyIDUzLjMyNmEuNC40IDAgMCAwIC4xNDQuMDcyLjM0LjM0IDAgMCAwIC4zMDEtLjA2OC4zLjMgMCAwIDAgLjA4OC0uMTI2IDQ3IDQ3IDAgMCAwIDMuMjgyLTEzLjA4MXEuMDIzLS4yMzMuMTI0LS40MzN0LjI2OC0uMzM0YzIuOTU1LTIuNDc4IDQuMTE1LjQ1OCA0LjY5NCAyLjg1MnEyLjMyIDkuNTM3LjE4NyAxOS4yNDRhMS40OCAxLjQ4IDAgMCAwIC40NCAxLjQwM3ptLTYuNTI2IDkuMjk1LTkuMDI0LTEwLjI3NmEuNy43IDAgMCAwLS4zNDMtLjIwNy44Ni44NiAwIDAgMC0uNDMzIDBxLTExLjY4IDMuMDIxLTIzLjExNC0uODIyYy01LjgxNi0zLjg1Mi0uNzU4LTUuNTE3IDIuNTktNS44MTZxNS45MTgtLjUzMyAxMS43MzUtMi41MDZhLjMuMyAwIDAgMCAuMTI3LS4wOC4zLjMgMCAwIDAgLjA3My0uMTMzLjM0LjM0IDAgMCAwIC4wMDEtLjE1NC4zNC4zNCAwIDAgMC0uMDctLjEzOGMtMTkuNDU5LTIxLjE1LTQwLjc2LTQwLjI0NS02Mi4yNzUtNTkuMjY0cS0uMzU2LS4zMTgtLjMxOC4xNWEzMDggMzA4IDAgMCAwIDguMzg3IDUxLjgwMmM0LjU5MiAxOC4zMDggMTMuNzU1IDM0LjE1NyAzMS44NDggNDEuODcycTI2LjI0NyAxMS4xODIgNTMuNzI5IDIuODMzYS41ODMuNTgzIDAgMCAwIC4yOTktLjg4OCAyMzUgMjM1IDAgMCAwLTEzLjIxMi0xNi4zNzNtNDUuMTI1IDQ5Ljc0NXEtMTIuNTk1IDEuMzE4LTIzLjQ0MS01LjU4M2MtMy4wNzctNC44OTkgMi4wNjYtOC41OTMgNS40NDItMTEuMTgzYS41ODQuNTg0IDAgMCAwIC4xODctLjcwMSA4LjQ2IDguNDYgMCAwIDAtMy40ODgtMy44NjIuODEuODEgMCAwIDAtLjgyMy4wMDljLTE2LjY5MSA5Ljk3Ny0zNC40ODUgMTAuNzgyLTUzLjE4NiA2Ljk2N3EtMS41Ny0uMzItMi44NTIuNjQ1LTYxLjQ1MSA0Ni4zNy02OS42NyAxMjMuOTEzLS42ODMgNi40MzMtMS44MDYgOC44MjdjLTIuOTQ1IDYuMzAyLTcuNzcgNy44NDUtMTQuMjIyIDkuNDcycS0uNDQ5LjExMyAwIC4yMzRjOS4yNzYgMi4zMSAxNC42OCA2LjE0MyAxNi4wNzQgMTYuNDAxIDguNDYyIDYyLjQ5IDQ4Ljk0IDExNy44NjQgMTEwLjM4MyAxMzguMzQxYTEwNCAxMDQgMCAwIDAgMTEuMDA2IDMuNTA3YzkyLjY0NSAyMy45MDkgMTgxLjIzMi0zMy42NjIgMjAyLjgwNC0xMjUuMDU0cTEuNjA5LTYuNzkgMy40NS0xOS4wODVjMS4xMDQtNy4zOTYgNS42OTUtMTIuMTE4IDEzLjE0Ny0xMy41NjguNDEyLS4wODQgMS45MDgtLjc1Ny4yODEtLjk5MS04LjA1MS0xLjE0MS0xMi4yNC02LjM4Ni0xMi45ODgtMTQuMTI4cS0xLjA3NS0xMS4yNS0yLjUxNi0xOS4wMzhjLTExLjc3Mi02My44OTItNTYuMzgzLTExNC41NzItMTE5LjI4NS0xMzEuNDZxLTE1LjEyLTMuODgtMzAuOTg3LTUuMjQ1YS4zODYuMzg2IDAgMCAwLS40MDIuMjUyIDE2OC42IDE2OC42IDAgMCAxLTExLjM1MiAyNC44NTRjLTQuMTMzIDcuNDA2LTguMTYzIDE1LjQ5NC0xNS43NTYgMTYuNDc2Ii8+PGNpcmNsZSBjeD0iMTQwLjA2NSIgY3k9IjI3My4wMyIgcj0iNTAuNjE4IiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iOS4yMDMiLz48cGF0aCBmaWxsPSIjZmZmIiBkPSJNMTQ2Ljk2NyAyNDIuMDkyYzE1LjY3MiAwIDI4LjM3NiAxMy45NjMgMjguMzc2IDMxLjE4OHMtMTIuNzA0IDMxLjE4OS0yOC4zNzYgMzEuMTg5LTI4LjM3Ny0xMy45NjQtMjguMzc3LTMxLjE4OWMwLTIuNjI1LjI5Ny01LjE3NC44NTItNy42MSAxLjYwNyAzLjcyNyA1LjMxMyA2LjMzOCA5LjYyOSA2LjMzOCA1Ljc4OSAwIDEwLjQ4MS00LjY5MyAxMC40ODItMTAuNDgycy00LjY5My0xMC40ODEtMTAuNDgyLTEwLjQ4MWMtLjc2MSAwLTEuNTA0LjA4My0yLjIxOS4yMzcgNS4xMzktNS42NzYgMTIuMjUzLTkuMTkgMjAuMTE1LTkuMTkiLz48Y2lyY2xlIGN4PSIyNjkuOTMyIiBjeT0iMjczLjAzIiByPSI1MC42MTgiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSI5LjIwMyIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik0yNzYuODM0IDI0Mi4wOTJjMTUuNjcyIDAgMjguMzc2IDEzLjk2MyAyOC4zNzYgMzEuMTg4cy0xMi43MDQgMzEuMTg5LTI4LjM3NiAzMS4xODktMjguMzc3LTEzLjk2NC0yOC4zNzctMzEuMTg5YzAtMi42MjUuMjk3LTUuMTc0Ljg1My03LjYxIDEuNjA2IDMuNzI3IDUuMzEyIDYuMzM4IDkuNjI4IDYuMzM4IDUuNzg5IDAgMTAuNDgyLTQuNjkzIDEwLjQ4Mi0xMC40ODJzLTQuNjkzLTEwLjQ4MS0xMC40ODItMTAuNDgxYy0uNzYxIDAtMS41MDQuMDgzLTIuMjE5LjIzNyA1LjEzOS01LjY3NiAxMi4yNTQtOS4xOSAyMC4xMTUtOS4xOSIvPjxwYXRoIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSI5LjIwMyIgZD0iTTE3Ny4xMzUgMzQ1LjMyOGMuODk5LS4yNCAyLjgwMS0uMTk3IDYuMzA0LjQ2NCA2LjMxMSAxLjE5IDE2LjU4NSA0LjIyMSAyNi4xMjIgNC4yMjEgOS40NTIgMCAxNy4xMTgtMS45MjYgMjEuMzgzLTIuNjAzLjc3LS4xMjMgMS4zODUtLjE5OSAxLjg3OC0uMjM3LS4zNCAxMy44NDMtMTIuODkzIDI3LjcxLTI3Ljg2OCAyNy43MS0xNS4xNzIgMC0yNy44NzYtMTMuODM1LTI3Ljg3Ni0yOC44MTEgMC0uMzU3LjAyOS0uNTk2LjA1Ny0uNzQ0WiIvPjwvc3ZnPg==" alt="Performance Models">
  </a>
</p>
<div align="center">

<h1 style="color: #9334E9;">⚡ Pruna-Qwen-Image-2.1</h1>

<h2>Few-step LoRA adapters for Qwen-Image-2.1</h2>

<h3>
  <span style="color: #9334E9;">5 or 8 steps</span>
  &nbsp;·&nbsp;
  <span style="color: #9334E9;">Up to 6.3x faster</span>
  &nbsp;·&nbsp;
  <span style="color: #9334E9;">No CFG</span>
  &nbsp;·&nbsp;
  Text-to-image and image editing
</h3>

</div>

**Pruna-Qwen-Image-2.1 is a set of LoRA adapters that let
[`Qwen/Qwen-Image-2.1`](https://huggingface.co/Qwen/Qwen-Image-2.1) generate
and edit images in only 5 or 8 steps. The adapters load on top of the base
model, so the pipeline, text encoder, and VAE stay unchanged. Training is based
on DMD. Improved using Qwen.**

> **v0.1: first release, work in progress.** Pruna-Qwen-Image-2.1 does not yet match the
> visual quality of the base model. We are still improving the distillation and
> will update this repository as new versions become available.

## Variants

Both adapters are v0.1. Pick one based on whether you need **quality** or **speed**.

| File | Steps | Trade-off |
|---|:---:|---|
| `p_qwen_image_2.1_8step_v0.1.safetensors` | 8 | **Higher quality.** Recommended as the default. |
| `p_qwen_image_2.1_5step_v0.1.safetensors` | 5 | **Higher speed**, with noticeably lower visual quality. |

Each adapter is trained for its own sigma schedule. Load only one at a time.

## Prompts, editing, and resolution

The adapters were trained at **1K resolution only**, with a mix of simple and
upsampled prompts, text-to-image generation, and single- and multi-image editing
with **up to 3 reference images**. Prompt upsampling is optional; detailed prompts
usually give better results.

Start at **1024 × 1024** and use at most **3 reference images** for editing.
Higher resolutions (including 2K) and more reference images may work, but are
outside the training coverage, and quality may vary. The 2K timings below show
inference speed, not a guarantee of quality at that resolution.

## Benchmarking

Use a table; Hugging Face can otherwise render the `<img>` elements as separate blocks.

<table>
  <tr>
    <td width="50%">
      <img src="assets/Pruna-Qwen-Image-2.1-t2i-1024.png" width="100%">
    </td>
    <td width="50%">
      <img src="assets/Pruna-Qwen-Image-2.1-t2i-2048.png" width="100%">
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="assets/Pruna-Qwen-Image-2.1-i2i-1024.png" width="100%">
    </td>
    <td width="50%">
      <img src="assets/Pruna-Qwen-Image-2.1-i2i-2048.png" width="100%">
    </td>
  </tr>
</table>

Text-to-image with the official Qwen model-card example prompt, BF16, batch size 1,
on one NVIDIA H100 80GB. Median of 3 requests after one warmup per configuration.
Includes prompt encoding, denoising, and decoding; excludes PNG saving, model
loading, and warmup. Base: 40 steps with KV cache on; Pruna-Qwen-Image-2.1: 5 or 8 steps with
KV cache off, as configured for this benchmark. The examples below enable KV caching for
Pruna-Qwen-Image-2.1; the chart has not been remeasured with that setting. LoRAs were unmerged;
no CFG, compilation, or CPU offload. These timings do not imply equal image quality.

## Quickstart

Runs text-to-image and image editing with the same pipeline. Needs a **CUDA GPU**.

```bash
pip install 'torch>=2.4.0' 'transformers>=5.17' accelerate peft pillow
pip install git+https://github.com/huggingface/diffusers@6256aa7666cedd47443adc8f82da9a10e110b09c
```

```python
import torch
from PIL import Image
from diffusers import FlowMatchEulerDiscreteScheduler, QwenImage21Pipeline

STEPS = 8  # 8 for higher quality, 5 for higher speed

# The terminal sigma 0 is appended by the scheduler.
SIGMAS = {
    5: [1.0, 0.94, 6 / 7, 2 / 3, 0.4],
    8: [1.0, 14 / 15, 6 / 7, 10 / 13, 2 / 3, 6 / 11, 0.4, 2 / 9],
}[STEPS]

pipe = QwenImage21Pipeline.from_pretrained(
    "Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16
).to("cuda")
pipe.load_lora_weights(
    "PrunaAI/Pruna-Qwen-Image-2.1",
    weight_name=f"p_qwen_image_2.1_{STEPS}step_v0.1.safetensors",
)

# Use the sigmas exactly as given: no extra shifting.
pipe.scheduler = FlowMatchEulerDiscreteScheduler.from_config(
    pipe.scheduler.config,
    use_dynamic_shifting=False,
    shift=1.0,
    shift_terminal=None,
)
```

## For Text-to-Image

Longer, more descriptive prompts give better results.

```python
image = pipe(
    prompt=(
        'A glowing neon shop sign that reads "QWEN IMAGE 2.1", mounted on a brick wall '
        "in a narrow city alley at night. Heavy rain, wet pavement reflecting pink and "
        "blue light, shallow depth of field, cinematic photograph."
    ),
    width=1024,
    height=1024,
    generator=torch.Generator("cuda").manual_seed(42),
    num_inference_steps=STEPS,
    sigmas=SIGMAS,
    true_cfg_scale=1.0,
    use_kv_cache=True,
).images[0]
```

### For Image Editing

```python
image = pipe(
    prompt="Change the background to a sunset beach",
    image=Image.open("input.png").convert("RGB"),
    generator=torch.Generator("cuda").manual_seed(42),
    num_inference_steps=STEPS,
    sigmas=SIGMAS,
    true_cfg_scale=1.0,
    use_kv_cache=True,
).images[0]
```

### Recommended settings

- **Use the sigma schedule that matches your adapter**, and keep the scheduler
  at `shift=1.0` with dynamic shifting off so the sigmas are not shifted twice.
  - 8-step: `1 → 14/15 → 6/7 → 10/13 → 2/3 → 6/11 → 0.4 → 2/9 → 0`
    (shift 2, computed as `σ = 2t / (1 + t)` on evenly spaced `t`)
  - 5-step: `1 → 0.94 → 6/7 → 2/3 → 0.4 → 0`
- **No CFG.** Keep `true_cfg_scale=1.0` and do not pass a negative prompt.
- **Keep the LoRA strength at 1.0.**
- **Write detailed prompts for text-to-image.** Longer prompts that describe
  the subject, setting, lighting, and style work noticeably better than short
  ones.

## Limitations

- This is a first version. Quality is below that of the base model.
- The 5-step adapter is faster than the 8-step one, but its images are
  visibly worse.
- Short or vague text-to-image prompts give weaker results.
- The adapters are only intended for the settings above. Other step counts,
  schedules, or CFG values are not supported.

## What this is not

- Not a standalone model. It needs the `Qwen/Qwen-Image-2.1` base weights.
- Not a replacement for the base model when you need its full quality.
- Not a finished release. Expect the weights to change in future versions.

## License

Pruna-Qwen-Image-2.1 is a derivative of Qwen-Image-2.1 and is distributed
under the **Qwen RESEARCH LICENSE AGREEMENT**. Review its use restrictions
before using or redistributing the adapters.

Qwen is licensed under the Qwen RESEARCH LICENSE AGREEMENT, Copyright (c) 2026
Hangzhou Tongyi Laboratory Technology Co., Ltd. All Rights Reserved.

## What's next?

- **Use Pruna-Qwen-Image-2.1 to generate and edit images with Qwen-Image-2.1 in a few steps.**
- Compress your own models with [Pruna](https://github.com/PrunaAI/pruna) and give us a ⭐️ for more efficiency!
- Want to use our optimized image models right away?  Check [P-Image-Ideogram](https://www.pruna.ai/p-image-ideogram) and [P-Image-Edit](https://www.pruna.ai/p-image-edit).

<style>
.model-button {
  display: inline-flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 8px;

  padding: 8px 20px;
  border: none;
  border-radius: 8px;

  background: #9334e9;
  color: #ffffff;

  font-size: 14px;
  font-weight: 400;
  line-height: 1;
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;

  box-sizing: border-box;
  overflow: visible;
  opacity: 1;
}
</style>

<a href="https://dashboard.pruna.ai/login?utm_source=huggingface&utm_medium=model_card&utm_campaign=hf_traffic" class="model-button">Try our models</a>