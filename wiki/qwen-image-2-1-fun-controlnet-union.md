---
type: Concept
title: Qwen-Image-2.1-Fun ControlNet-Union Branch
description: Single-checkpoint ControlNet-Union branch for Qwen-Image 2.1 covering 8 structural controls plus inpainting via VideoX-Fun.
tags: [qwen, controlnet, image-generation, inpainting, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T11:40:00Z }
sources:
  - id: fun-union-readme
    resource: ../raw/Qwen-Image-2.1-Fun-Controlnet-Union/README.md
    scope: ../raw/Qwen-Image-2.1-Fun-Controlnet-Union/
    kind: documentation
    title: Qwen-Image-2.1-Fun-Controlnet-Union model card
  - id: fun-union-readme-zh
    resource: ../raw/Qwen-Image-2.1-Fun-Controlnet-Union/README_zh.md
    scope: ../raw/Qwen-Image-2.1-Fun-Controlnet-Union/
    kind: documentation
    title: Qwen-Image-2.1-Fun-Controlnet-Union model card (Chinese)
---

Qwen-Image-2.1-Fun-Controlnet-Union is a **reported** ControlNet-Union branch for the Qwen-Image 2.1 flow-matching text-to-image DiT, where one checkpoint drives 8 structural control conditions plus image inpainting without per-condition weights and loads on top of the frozen base transformer.[^fun-union-readme]

## Checkpoint packaging

- **Reported** identity: ControlNet-Union branch for Qwen-Image 2.1, used via the VideoX-Fun repository (`aigc-apps/VideoX-Fun`, `library_name: videox_fun`).[^fun-union-readme]
- **Reported** contents: `Qwen-Image-2.1-Fun-Controlnet-Union.safetensors` holds only the control branch (`control_img_in` plus 16 `control_blocks`, about 7.0 GB) and is loaded with `strict=False` on top of the base Qwen-Image 2.1 transformer, which must be present separately.[^fun-union-readme]
- **Reported** base behavior: the base model stays frozen while the control branch supplies structural adherence.[^fun-union-readme]
- License frontmatter states `qwen-research`; the body states the model is a derivative of Qwen-Image 2.1 under the Qwen Research License with use restrictions to review before use — a **reported** disclosure boundary, not legal verification.[^fun-union-readme]

## Supported controls

- **Reported** single-checkpoint coverage of 8 conditions for text-to-image generation, with no per-condition checkpoint switching:[^fun-union-readme]

| Condition | Control signal |
|---|---|
| Canny | Canny edge map |
| Depth | Monocular depth map |
| Grayscale | Grayscale (luminance) image |
| HED | HED edge detection map |
| Lineart | Line-art extraction |
| MLSD | Line-segment detection map |
| Pose | DWPose skeleton |
| Scribble | Free-hand / sketch lines |

- **Reported** input tolerance: any ordinary RGB control image at the target canvas works, tolerating different line thickness, thresholds, and crops.[^fun-union-readme]

## Mechanism

- **Reported** dense injection: the control branch attaches a skip to every 2nd of the 32 transformer blocks (`control_layers = [0, 2, 4, …, 30]`, 16 injection points); each skip is added back through zero-gated `before_proj` / `after_proj` projections.[^fun-union-readme]
- **Reported** shared control-plus-inpaint input: `control_in_dim = 129`, composed as control latents (64) plus mask (1) plus masked-image latents (64); pure-control runs zero-pad the mask channels, inpainting re-draws the masked region from the prompt, and the two can be combined so the re-drawn region follows both prompt and structure.[^fun-union-readme]
- **Reported** strength control: `control_context_scale` scales every control skip before adding it back; `1.0` is strongest (used for all published results), lower values weaken guidance, `0.0` switches the control branch off.[^fun-union-readme]
- **Reported** fast sampling: the standalone example scripts run with `guidance_scale = 1.0` (single forward pass per step, no classifier-free guidance needed), described as CFG-distilled.[^fun-union-readme]
- **Reported** encoder and output: Qwen-Image 2.1 encodes the prompt and any condition image with a Qwen3-VL text encoder plus processor, and its VAE decodes to RGBA, so previews are saved as PNG.[^fun-union-readme]
- **Reported** prompting: describe the whole target image; the masked region is conveyed by the mask channel, not the text, and more detailed prompts give better stability.[^fun-union-readme]

## Inpainting behavior

- **Reported** inpainting: a masked region of the source image is re-drawn from the prompt while the rest is preserved; the mask is white where content should be re-generated and black where it should be kept.[^fun-union-readme]
- **Reported** combined use: because control and inpainting share one branch, a control image (the worked example uses a DWPose skeleton) can be fed together with the mask so the re-drawn region also follows the given pose.[^fun-union-readme]

## Inference procedure and constraints

- **Reported** setup: clone `https://github.com/aigc-apps/VideoX-Fun.git`, create `models/Diffusion_Transformer`, and place the base `Qwen-Image-2.1` model plus `Qwen-Image-2.1-Fun-Controlnet-Union/Qwen-Image-2.1-Fun-Controlnet-Union.safetensors` underneath it.[^fun-union-readme]
- **Reported** entry points: edit the settings at the top of `examples/qwenimage21_fun/predict_t2i_control.py` (or `predict_i2i_inpaint.py` for inpainting) — `model_name`, `config_path`, `transformer_path`, `control_image`, plus `inpaint_image` / `mask_image` and `prompt` for inpainting — then run the script.[^fun-union-readme]
- **Reported** hard constraint: `config_path` must be `config/qwenimage21/qwenimage21_control.yaml` because it builds the branch exactly as the checkpoint expects (`control_layers: [0, 2, 4, …, 30]`, `control_in_dim: 129`); a mismatched config silently drops or misplaces control weights and produces wrong outputs.[^fun-union-readme]
- **Reported** canvas and caching: `sample_size` sets the output canvas (e.g. `[1728, 992]`); `use_kv_cache = True` caches the text / condition-image keys after the first denoising step for a speedup at fixed resolution.[^fun-union-readme]
- **Reported** memory: the transformer plus the Qwen3-VL text encoder do not fit a single consumer GPU fully loaded; use `model_group_offload` (fastest) or `model_cpu_offload_and_qfloat8` on a single high-memory GPU.[^fun-union-readme]

## Example protocol and limits

- **Reported** example protocol: all control samples use `num_inference_steps = 40`, `control_context_scale = 1.0`, seed 43, with control image on top and output below per condition; the inpainting example shows source, mask, pose control, and output.[^fun-union-readme]
- **Synthesis:** treat the embedded control/inpainting grids as illustrative **reported** outputs, not reproduced measurements; the remote `asset/` and `results/` images were not captured locally and no generation was executed.[^fun-union-readme]

## Contradictions

- Canvas multiple: the English card instructs keeping both `sample_size` sides as multiples of 16 so the control map is not distorted, while the Chinese card instructs keeping width and height as multiples of 32 to avoid stretching the control map.[^fun-union-readme][^fun-union-readme-zh] No basis for choosing one is given in either capture; record both and prefer the stricter (32) only as **synthesis** until the config or code is inspected.

## Relationships

- Uses the upstream Qwen-Image 2.1 base model and VideoX-Fun control pipeline; this concept records only the Fun ControlNet-Union branch packaging and settings, not the base model's own behavior.
- Related to [Qwen-Image-2.1-Fix LoRA Adapter](qwen-image-2-1-fix.md), which targets generation consistency on the same base-model family, and to [Pruna Qwen-Image-2.1 Few-Step LoRA Adapters](pruna-qwen-image-2-1.md), which targets fewer-step speed; neither source claims structural control or inpainting, a distinct capability axis from this branch.
- Related to [Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)](qwen-image-2-1-gguf-abiray.md), which targets lower VRAM via quantization for ComfyUI; this branch adds control/inpainting structure and carries its own ~7.0 GB branch weights plus offload requirements.
- For a separate ggml-based local engine that also reports Qwen-Image support, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md); the Fun ControlNet-Union card claims only the VideoX-Fun script path.

## Coverage limits

- **Observed:** `../raw/Qwen-Image-2.1-Fun-Controlnet-Union/README.md` and `../raw/Qwen-Image-2.1-Fun-Controlnet-Union/README_zh.md` were statically inspected; no code was executed and no control, inpainting, timing, or VRAM claim was reproduced.
- **Observed:** outside-scope or uncaptured material includes the `Qwen-Image-2.1` base weights, the `.safetensors` branch checkpoint, the VideoX-Fun code and `qwenimage21_control.yaml` config, the `predict_t2i_control.py` / `predict_i2i_inpaint.py` scripts, and all remote `asset/` control/mask/source and `results/` output images.
- Freshness is unbounded by any date or immutable revision in either capture; future weight, config, or card updates would be a new revision.

[^fun-union-readme]: Model-card capture in `../raw/Qwen-Image-2.1-Fun-Controlnet-Union/README.md`; branch identity and 8-condition plus inpainting headline from Overview; branch-only weights, ~7.0 GB size, `strict=False`, and frozen-base behavior from Overview and Model Card table; VideoX-Fun repo link and frontmatter tags/tasks from header; dense `control_layers`, zero-gated projections, `control_in_dim = 129` channel split, `control_context_scale`, `guidance_scale = 1.0`, Qwen3-VL/RGBA, whole-image prompting, 8-row condition table, mask white/black convention, VideoX-Fun clone/model-dir/script/config/canvas/cache/offload procedure and mismatch warning, and 40-step/scale-1.0/seed-43 example protocol from Model Features, Supported control conditions, Results, Inpainting, and Inference sections; Qwen Research License boundary from License section.
[^fun-union-readme-zh]: Chinese model-card capture in `../raw/Qwen-Image-2.1-Fun-Controlnet-Union/README_zh.md`; materially mirrors the English card, inspected to confirm parity except the canvas-multiple wording (32 vs 16) recorded under Contradictions.
