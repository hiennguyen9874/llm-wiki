---
type: Concept
title: Cosmos3-Super-Text2Image Text-to-Image Model
description: NVIDIA 64B Mixture-of-Transformers text-to-image checkpoint in the Cosmos 3 omnimodal world-model family with vLLM-Omni, SGLang, and Diffusers serving under OpenMDW1.1.
tags: [nvidia, cosmos3, text-to-image, diffusion-transformer, omnimodal, vllm-omni, sglang, diffusers, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T13:50:00Z }
stale_after: 2027-04-03
sources:
  - id: cosmos3-t2i-card
    resource: ../raw/Cosmos3-Super-Text2Image.md
    kind: documentation
    title: Cosmos3-Super-Text2Image model card
---

Cosmos3-Super-Text2Image is NVIDIA's **reported** 64B-parameter text-to-image checkpoint in the Cosmos 3 family of omnimodal world models for Physical AI (robotics, autonomous vehicles, smart/industrial spaces), generating high-fidelity images from text and served via vLLM-Omni, SGLang Diffusion, Hugging Face Diffusers, and PyTorch under OpenMDW1.1.[^cosmos3-t2i-card]

## Identity and release

- **Reported** family: Cosmos 3 omnimodal world models generate video, image, audio, and action commands from text, image, video, and action-trajectory inputs for world understanding, generation, simulation, and embodied policy learning; this checkpoint covers the text-to-image slice.[^cosmos3-t2i-card]
- **Reported** developer: NVIDIA; stated ready for commercial and non-commercial use with global deployment geography.[^cosmos3-t2i-card]
- **Reported** release: 05/31/2026 via the Hugging Face `nvidia/cosmos3` collection and GitHub `nvidia/cosmos`.[^cosmos3-t2i-card]
- **Observed** card frontmatter tags: `nvidia`, `cosmos`, `cosmos3`, `vllm-omni`, `sglang`, `sglang-diffusion`, `diffusers`, `text-to-image`, `image-generation`; license fields state `other` / `openmdw1.1-license`.[^cosmos3-t2i-card]
- **Reported** license: OpenMDW1.1; card links the license and names companion subcards `EXPLAINABILITY.md`, `BIAS.md`, `SAFETY.md`, `PRIVACY.md`, which were not captured locally.[^cosmos3-t2i-card]

## Architecture

- **Reported** architecture type: Transformer; network architecture Mixture-of-Transformers (MoT) with two towers — an autoregressive transformer for discrete token (text) generation and a diffusion transformer for continuous multimodal generation via iterative denoising.[^cosmos3-t2i-card]
- **Reported** size: 64B trainable parameters for Cosmos3-Super-Text2Image.[^cosmos3-t2i-card]
- **Reported** basis: developed on the Cosmos Framework (`nvidia/cosmos-framework`); integration guidance also references the `nvidia/cosmos` repository and the Cosmos 3 technical report, none of which were inspected beyond this card.[^cosmos3-t2i-card]

## Inputs and outputs

- **Reported** text-to-image input: text prompt up to 4096 tokens; the wider Cosmos 3 generator also accepts images (jpg/png/jpeg/webp), video (mp4, 256p/480p/720p, listed aspect ratios 16:9, 4:3, 1:1, 3:4, 9:16, max 5 frames as input), short audio (max 0.5 s, stereo 48 kHz when muxed), and action trajectories for listed embodiments (camera-motion 9D, autonomous-vehicle 9D, egocentric 57D, Franka/UR/Google-robot/WidowX 10D variants, dual-Franka 20D, Agibot 29D, UMI 9D).[^cosmos3-t2i-card]
- **Reported** text-to-image output: image in JPG/JPEG at 256p, 480p, or 720p in the same aspect-ratio set; the family also emits MP4 video (5–400 frames, 189 default), AAC stereo audio muxed in MP4, 1D-list JSON actions, and text strings.[^cosmos3-t2i-card]
- **Reported** reasoner slice (family context, not this checkpoint's path): text / text+image / text+video inputs with up to 256K-token context (4 fps video recommended) producing text, with `max_tokens=4096+` recommended and possible chain-of-thought, point-localization, and bounding-box outputs.[^cosmos3-t2i-card]

## Serving and hardware

- **Reported** runtime engines: PyTorch, vLLM-Omni, Hugging Face Diffusers (`Cosmos3OmniPipeline`), and SGLang / SGLang Diffusion; test hardware GB200 and H100; supported microarchitectures Ampere, Blackwell, Hopper; Linux only (other OSes untested); only BF16 precision tested, FP4/FP8/FP16 not officially supported.[^cosmos3-t2i-card]
- **Reported** vLLM-Omni path: container `vllm/vllm-omni:cosmos3`; 8×H100 serving flags `--omni --cfg-parallel-size 2 --ulysses-degree 4 --tensor-parallel-size 1 --use-hsdp --hsdp-shard-size 8 --init-timeout 1800`; 4×H200/GB200 variant uses `--cfg-parallel-size 2 --ulysses-degree 2 --tensor-parallel-size 1`; `--enable-layerwise-offload` may save memory but is flagged as a significant text-to-image performance penalty.[^cosmos3-t2i-card]
- **Reported** vLLM-Omni request example: OpenAI-compatible `POST /v1/images/generations` with a JSON-upsampled prompt, `size 1024x1024`, `num_inference_steps 50`, `guidance_scale 4.0`, `flow_shift 3.0`, seed 1143, and `extra_args { use_resolution_template: false, guardrails: true }` returning base64 image data.[^cosmos3-t2i-card]
- **Reported** SGLang path: install from SGLang main branch with diffusion extras plus `cosmos-guardrail==0.3.1`, serve with `--model-path nvidia/Cosmos3-Super-Text2Image --num-gpus 4`; example request uses `size 1280x720`, 35 steps, guidance 6.0, `flow_shift 10.0`; a Cosmos3 SGLang cookbook is linked but uninspected.[^cosmos3-t2i-card]
- **Reported** Diffusers path: install `diffusers` from git plus `accelerate`, `cosmos_guardrail`, torch/torchvision/transformers; load `Cosmos3OmniPipeline.from_pretrained("nvidia/Cosmos3-Super-Text2Image", torch_dtype=torch.bfloat16)` with safety checker enabled, override scheduler with `UniPCMultistepScheduler` at `flow_shift=3.0`, generate 1024×1024 single frame at 50 steps and guidance 4.0; card notes GB200-tested and points H100 users at the vLLM-Omni multi-GPU recipe.[^cosmos3-t2i-card]
- **Reported** prompt upsampling: for optimal quality, upsample text prompts into a JSON structure via `cosmos_framework.inference.prompt_upsampling --mode text2image` (worked example uses an Anthropic endpoint with `claude-opus-4-7`, `--resolution 768`, `--aspect-ratio "1,1"`); the pre-upsampled `assets/example_caption.json` is referenced but not captured locally.[^cosmos3-t2i-card]
- **Synthesis:** treat all install commands, container tags, CLI flags, step/guidance/shift defaults, and GPU recipes above as **reported** setup guidance subject to drift; nothing was installed, served, or generated for this concept. Stale boundary recorded in `stale_after`.

## Training data and evaluation pointers

- **Reported** scale: 1.3B data points across 393 dataset entries, all training (testing/validation via separate public benchmarks); collection period 2024–2026; curation spans robotics, driving, industrial, indoor/outdoor, lighting/weather, viewpoint, object, and activity coverage with automated filtering, deduplication, provenance tracking, human review on subsets, and synthetic augmentation for rare interactions.[^cosmos3-t2i-card]
- **Reported** modality counts — reasoning samples: text 22M, image 19M, video 1M; generation samples: image 767M, video 348M, audio 139M, action 8M.[^cosmos3-t2i-card]
- **Reported** named public sources: OpenImage 1.2M, Coyo700M 100M, YouTube Video 340M, UMI 4.5M; private: Egocentric 7M, Nexar 0.6M, AgiBot 0.2M, HOI 0.3M; synthetic: HiDream-I1 images 15M, Qwen-Image-2512 images 14M, Qwen3-VL captions 1115M.[^cosmos3-t2i-card]
- **Reported** safety filtering: hash-matching against known CSAM/NCII references, moderation classifiers, keyword/regex screening, provenance heuristics, embedding anomaly detection, plus action-trajectory plausibility filtering; card notes no large-scale process guarantees complete removal and flags residual edge-case risk.[^cosmos3-t2i-card]
- **Reported** evaluation: technical paper holds detailed base-model evaluations; card embeds a text-to-image benchmark figure and two Artificial Analysis leaderboard snapshots dated 2026/05/28 (open-source and all-models) plus qualitative examples — all image-only locally, so no score, rank, or qualitative claim is transcribed here.[^cosmos3-t2i-card]

## Limitations and ethical boundaries

- **Reported** generation failure modes: temporal inconsistency, unstable camera/object motion, imprecise physical interactions, audio-video sync error, action-state drift (worse for long-horizon/high-resolution outputs); reasoning may misinfer states, causality, geometry, ordering, intent, or outcomes and hallucinate under complex/long-context inputs.[^cosmos3-t2i-card]
- **Reported** physics caveat: no explicit physics simulator — 3D geometry, 4D evolution, object permanence, contact dynamics, and physical law are approximated, with artifacts such as disappearing/morphing objects and implausible collisions; quality degrades out-of-distribution and in underrepresented or safety-critical edge cases.[^cosmos3-t2i-card]
- **Reported** non-certification: outputs are not physically accurate simulation, ground-truth reasoning, or safety-certified decisions; robotics, autonomous, scientific, or safety-critical use requires additional validation, external constraints, system-level safety analysis, and domain guardrails; deployment follows V-model unit/system testing per the card.[^cosmos3-t2i-card]
- **Reported** responsibilities: users need proper rights/permissions for input image/video content and are responsible for inputs, outputs, and pre-deployment guardrails and safety mechanisms.[^cosmos3-t2i-card]

## Relationships

- Uses [Latent Image Generation Pipeline](latent-image-generation.md) concepts (prompt conditioning, denoising iteration, scheduler settings such as steps, guidance, and flow shift) as background for the serving parameters above.
- Complements [Image Model, Library, and Workflow Roles](image-inference-tool-roles.md): this page records the Cosmos3 weights and their Diffusers/vLLM-Omni/SGLang entry points, not a ComfyUI workflow or standalone engine build.
- For a separate ggml-based local engine with no Cosmos support stated in its capture, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md).

## Coverage limits

- **Observed:** only `../raw/Cosmos3-Super-Text2Image.md` was statically inspected; no command was executed and no install, serving, generation, benchmark, or data claim was reproduced.
- **Observed:** locally missing material includes all `assets/` attachments (benchmark figures, leaderboard snapshots, qualitative examples, `example_caption.json`, `original_prompt.txt`, example output image) and every remote target: Hugging Face collection, `nvidia/cosmos` and `cosmos-framework` repos, prompt-upsampling doc, technical report, training-content PDF, OpenMDW license text, vLLM-Omni/SGLang/Diffusers upstreams, SGLang cookbook, and the EXPLAINABILITY/BIAS/SAFETY/PRIVACY subcards.
- All capability, scale, dataset, compatibility, performance, and quality statements above are **reported** by the card, not independently verified; benchmark and leaderboard content is existence-only because the figures carry no transcribed values.
- No immutable weight revision or snapshot hash is present in the capture; future weight or card updates are a new revision.

[^cosmos3-t2i-card]: Model-card capture in `../raw/Cosmos3-Super-Text2Image.md`; family purpose, T2I variant identity, NVIDIA developer, commercial-readiness, OpenMDW1.1 license, global deployment, and 05/31/2026 release from Model Overview, License, Use Case, and Release Date; MoT two-tower architecture, 64B parameters, Cosmos Framework basis, and frontmatter tags/license from Model Architecture and YAML frontmatter; generator/reasoner I/O, formats, resolutions, frame/audio/action limits, and embodiment list from Input/Output Specifications; engines, Ampere/Blackwell/Hopper support, Linux-only, BF16-only, and GB200/H100 testing from Software Integration and Inference; training scale, modality table, public/private/synthetic dataset tables, curation and safety-filtering narrative, and training-content pointer from Training, Testing, and Evaluation Datasets; benchmark-paper pointer, T2I figure, 2026/05/28 leaderboard snapshots, and qualitative examples from Benchmarks; prompt-upsampling, vLLM-Omni, SGLang, and Diffusers commands and parameters from Usage; artifact, physics-simulator, OOD, non-certification, V-model, and user-responsibility statements from Limitations, Software Integration note, and Ethical Considerations.
