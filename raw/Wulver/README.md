---
license: other
library_name: diffusers
license_name: krea-2-community-license
license_link: https://krea.ai/krea-2-licensing
base_model: Comfy-Org/Krea-2
pipeline_tag: text-to-image
tags:
  - text-to-image
  - furry
  - anthro
  - kemono
  - anime
  - krea2
---

<div align="center">
  <img src="assets/vaelico-logo.png" width="72" alt="Vaelico">

  # Krea 2 - Wulver <sub>v0.5</sub>

  **Full fine-tune of Krea 2 Raw (12.8B DiT)** — anthro & furry, with strong anime / kemono range,<br>
  true multi-character composition and **1,113 artist styles** you can call by name.

  [Civitai page](https://civitai.com/models/2881657/wulver-krea-2-v01-alpha) · [vaelico.ai](https://vaelico.ai)
</div>

> In Shetland folklore, the Wulver is a wolf-headed being that was never cruel —
> it fished the lochs and left its catch on the windowsills of those in need.

## What's new in v0.5

- **Much longer training.** 13 full epochs over the curated corpus at 512 px
  (384,672 samples per epoch, about 156k steps at batch 32), the 13th with the learning rate
  annealed to zero. Then an artist-focused pass at 512 px and a final curated pass at **1024 px**.
- **Artist tokens work.** 1,113 `@artist` tokens, listed in [ARTISTS.md](ARTISTS.md).
  In v0.1 the `@` prefix was ignored.
- **Turbo from the official Krea 2 Turbo LoRA**, merged into the Turbo files at strength 1.0
  (8 steps, CFG 1). The Non-Turbo files ship too, so you can pick your own strength or skip it.

## What it does

- **Anthro / furry** as its home turf — species knowledge far beyond generalist models
- **Anime & kemono styles** — not the usual western-model anime approximation
- **Multi-character scenes** — characters interacting, not merged into one blob
- **Artist styles** via `@artistname` — see prompting tips below

## Files

| File | Size | Use |
|---|---|---|
| `Wulver_v0.5_fp8_e4m3fn.safetensors` | 12.8 GB | ComfyUI — the one most people want (Turbo, 8 steps) |
| `Wulver_v0.5_int8_convrot.safetensors` | 13.5 GB | forge-neo and other int8 runtimes (Turbo) |
| `Wulver_v0.5_w4a8-convrot.safetensors` | 7.7 GB | Smallest. ComfyUI ≥ 0.31 native W4A8 (Turbo) |
| `Wulver_v0.5_bf16.safetensors` | 25.6 GB | Turbo-merged, full precision — merging, quantizing |
| `Wulver_v0.5_non_turbo_bf16.safetensors` | 25.6 GB | **Non-Turbo — base for LoRA training / further fine-tuning**, or your own Turbo LoRA strength |
| `Wulver_v0.5_non_turbo_int8-convrot.safetensors` | 13.5 GB | Non-Turbo, int8 |
| `Wulver_workflow.json` | — | Drag-and-drop ComfyUI workflow (fp8, 8 steps) |
| [`ARTISTS.md`](ARTISTS.md) | — | The 1,113 artist tokens |

GGUF quants are on the [Civitai page](https://civitai.com/models/2881657/wulver-krea-2-v01-alpha).

## Settings (Turbo files)

| | |
|---|---|
| Steps | **8** |
| CFG | **1.0** |
| Sampler / Scheduler | **euler / simple** |
| Shift | 1.15 (ComfyUI default for Krea 2 — no extra node needed) |
| Resolution | 1024 native |
| CLIPLoader type | **krea2** |

## Other recipes (Non-Turbo file)

The Turbo LoRA is `krea2_turbo_lora_rank_64_bf16.safetensors` from
[Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) (`loras/`), loaded with a LoraLoaderModelOnly node.

| Recipe | Turbo LoRA strength | Steps | CFG |
|---|---|---|---|
| Same as the Turbo files | 1.0 | 8 | 1.0 |
| No LoRA | — | 52 | 3.5 |
| Advanced: lighter Turbo | 0.6 | 14 | 1.0 |

Sampler euler / simple in all three. Without the LoRA (CFG above 1) use an empty `CLIPTextEncode`
as the negative, not `ConditioningZeroOut`.

## ComfyUI setup

1. `Wulver_v0.5_fp8_e4m3fn.safetensors` → `ComfyUI/models/diffusion_models/`
2. Text encoder `qwen3vl_4b_bf16.safetensors` from [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) → `models/text_encoders/`
3. VAE `qwen_image_vae.safetensors` from the same repo → `models/vae/`
4. Drag `Wulver_workflow.json` into ComfyUI and hit queue.

## Prompting tips

Training captions start with a rating tag, then the artist token if there is one, then the description.
Prompting the same way gets you the most out of it:

> *sfw, @artistname, A digital painting of [subject & species, appearance details]. [What they are doing,
> pose, expression]. [Clothing / body details]. The background features [setting, lighting, atmosphere].*

- Detailed descriptive prose works best; booru-style tag lists also work
- Artist tokens must match [ARTISTS.md](ARTISTS.md) exactly, `@` included. Put them right after the rating tag
- One- or two-word prompts sample the model's whole range, so expect random styles. Describe what you want
- At CFG 1.0 the negative prompt has no effect

## Compatibility notes

- Same architecture as Krea 2 Raw: Qwen3-VL-4B text encoder, Qwen Image VAE, stock ComfyUI loaders
- `w4a8-convrot` needs ComfyUI ≥ 0.31.0 (native W4A8 loader), an SM 8.0+ GPU and PyTorch cu130+
- LoRAs trained on base Krea 2 or on Wulver v0.1 may behave differently on v0.5 (weights have moved)

## Checksums and provenance

| File | SHA256 |
|---|---|
| `Wulver_v0.5_fp8_e4m3fn.safetensors` | `ef8b8e1cf596e9564df79d9688af3c6faf85772b3226f1ba880db9970271619e` |
| `Wulver_v0.5_int8_convrot.safetensors` | `e3d89a4faa32633374f00ed37a9a0b49663a9a243725f39573a119c8c7009877` |
| `Wulver_v0.5_w4a8-convrot.safetensors` | `905af7686bb48d4f40dc80117f6839f6a9491b1af13e46b6242ecaadda6bf996` |
| `Wulver_v0.5_bf16.safetensors` | `c8f2b29749cee4386f2215033bca5e26af0cc8fd0fd0c49f4c1d55b35b3ebde3` |
| `Wulver_v0.5_non_turbo_bf16.safetensors` | `84012bb362249e15efd18fa46034d98be74f180e8decaf858e127c07f8a6700f` |
| `Wulver_v0.5_non_turbo_int8-convrot.safetensors` | `97417e247e3bea10fc8e5a023e4bbb2f075a9a363430a01681c529955bf602b3` |
| `Wulver_workflow.json` | `3040420f4aa830a2611fb5d202ae9b227f6e87ed4ca3c6657fd00312b26ebd07` |

All v0.5 files, including the Civitai-only GGUF (Q8_CR / Q5_0 / Q4_0) and plain int8 files, with sizes:
[SHA256SUMS_v0.5.txt](SHA256SUMS_v0.5.txt).
The v0.5 Non-Turbo checkpoint and how each file was made: [NON_TURBO_v0.5.md](NON_TURBO_v0.5.md).

## Previous version

The v0.1 files (`Wulver_v0.1_*`) stay in this repository unchanged. See [NON_TURBO.md](NON_TURBO.md)
for the v0.1 Non-Turbo checkpoint.

## License

This is a modified version of the **Krea 2** model by Krea.
Krea 2 is licensed under the [Krea 2 Community License Agreement](https://krea.ai/krea-2-licensing) —
by using this model you agree to its terms (including the [Acceptable Use Policy](https://www.krea.ai/krea-2-use-policy)).
The full license text is included as `LICENSE.md` and the attribution notice as `NOTICE` in this repository.
Not affiliated with or endorsed by Krea.

<div align="center">
  <img src="assets/vaelico-logo.png" width="40" alt="Vaelico"><br>
  <em>by Vaelico — generate online shortly at <a href="https://vaelico.ai">vaelico.ai</a></em>
</div>
