---
type: Concept
title: Qwen-Image-2.1 GGUF Quantized Checkpoints (Leejet)
description: Leejet GGUF quants of Qwen-Image-2.1 converted with stable-diffusion.cpp for sd.cpp and leejet ComfyUI-GGUF use.
tags: [qwen, gguf, quantization, image-generation, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T05:03:52Z }
sources:
  - id: leejet-qwen21-gguf-readme
    resource: ../raw/leejet-Qwen-Image-2.1-GGUF/README.md
    scope: ../raw/leejet-Qwen-Image-2.1-GGUF/
    kind: documentation
    title: Qwen-Image-2.1 GGUF quantized files
---

Leejet's package provides GGUF quantized files of `Qwen/Qwen-Image-2.1` converted with leejet's `stable-diffusion.cpp`, positioned for use in either `stable-diffusion.cpp` or ComfyUI via the leejet `ComfyUI-GGUF` fork, with one linked example text-to-image workflow and one remote example image.[^leejet-qwen21-gguf-readme]

## Quantization and licensing

- **Observed** base declaration: frontmatter states `base_model: Qwen/Qwen-Image-2.1`, with `tags` including `gguf`, `text-to-image`, and `stable-diffusion.cpp` and `language` entries for English and Chinese.[^leejet-qwen21-gguf-readme]
- **Reported** conversion: files are converted using `https://github.com/leejet/stable-diffusion.cpp`.[^leejet-qwen21-gguf-readme]
- **Reported** license boundary: the quantized files follow the original-model license, pointing to the Qwen Research License Agreement at `Qwen/Qwen-Image-2.1/blob/main/LICENSE`; this is a **reported** disclosure boundary, not legal verification.[^leejet-qwen21-gguf-readme]
- **Observed** gap: unlike the Abiray and Unsloth packagings, this capture names no quant filenames, quant types, file sizes, VRAM targets, VAE filenames, or text-encoder filenames, so it gives no basis for a size/quality comparison.[^leejet-qwen21-gguf-readme]

## stable-diffusion.cpp use

- **Reported** host: the model can be used with `stable-diffusion.cpp` at `https://github.com/leejet/stable-diffusion.cpp`.[^leejet-qwen21-gguf-readme]
- **Reported** procedure pointer: setup and usage details are delegated to `Qwen-Image-2.1 Documentation` at `docs/qwen_image_2.1.md` in that repository; that guide was not captured locally and remains uninspected.[^leejet-qwen21-gguf-readme]
- **Observed:** no install, conversion, download, or generation step was executed for this entry; host support is **reported** usage, not reproduced behavior.[^leejet-qwen21-gguf-readme]

## ComfyUI use

- **Reported** prerequisite: install the custom node at `https://github.com/leejet/ComfyUI-GGUF` to use the model in ComfyUI.[^leejet-qwen21-gguf-readme]
- **Reported** fork choice: use the **leejet** version of `ComfyUI-GGUF` rather than the version maintained by `city96`, with the stated reason that the `city96` repository appears to no longer be actively maintained; treat the maintenance claim as **reported** and unverified beyond this source.[^leejet-qwen21-gguf-readme]
- **Reported** example workflow: `qwen_image_2_1_t2i_gguf.json` is linked as the example ComfyUI text-to-image workflow.[^leejet-qwen21-gguf-readme]
- **Observed** workflow limit: that JSON file is not present in `../raw/leejet-Qwen-Image-2.1-GGUF/` and its contents, node set, and encoder/VAE/loader configuration remain uninspected.[^leejet-qwen21-gguf-readme]
- **Reported** example output: a 200x200 remote image at `huggingface.co/leejet/Qwen-Image-2.1-GGUF/resolve/main/Qwen_image_2.1_t2i.png` is shown as the example generation; the image file was not captured locally and no generation claim was verified.[^leejet-qwen21-gguf-readme]

## Relationships

- Uses the upstream `Qwen/Qwen-Image-2.1` base model; this concept records only the Leejet GGUF conversion and dual-host setup, not the base model's own behavior. See [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md) for the base definition.
- Related to [Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)](qwen-image-2-1-gguf-abiray.md), which publishes six size/VRAM options with a ComfyUI placement and workflow procedure, and [Qwen-Image-2.1 GGUF Quantized Checkpoints (Unsloth)](qwen-image-2-1-gguf-unsloth.md), which specifies Dynamic 2.0 per-tensor handling plus a VAE and Qwen3-VL encoder pairing with an `sd-cli` command; this Leejet source makes neither packaging claim and instead ties the quants to the leejet converter and leejet ComfyUI fork.
- For hosts, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md) for the ggml-based engine family named by this source and [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) for the ComfyUI custom-node path; note the fork difference, since the ComfyUI-GGUF concept documents the `city96` install while this source recommends the `leejet` fork.
- Related to [Qwen-Image-2.1 Uncensored GGUF Checkpoints (Abenzerps)](qwen-image-2-1-uncensored-gguf-abenzerps.md), a separate uncensored plus base GGUF packaging that also names the leejet converter and leejet fork; neither source makes a claim about the other's quant set.

## Coverage limits

- **Observed:** only `../raw/leejet-Qwen-Image-2.1-GGUF/README.md` was statically inspected; no code was executed and no conversion, download, install, workflow, or generation claim was reproduced.
- **Observed:** no immutable revision or capture date is present; freshness is unbounded beyond the local capture.
- **Observed:** uninspected material includes the GGUF weights themselves, the linked `qwen_image_2_1_t2i_gguf.json` workflow (absent locally), the remote example PNG, the `docs/qwen_image_2.1.md` setup guide, the upstream `Qwen/Qwen-Image-2.1` base and LICENSE target, and the leejet `stable-diffusion.cpp` and `ComfyUI-GGUF` repositories.

[^leejet-qwen21-gguf-readme]: Model-card README capture in `../raw/leejet-Qwen-Image-2.1-GGUF/README.md`; `Qwen/Qwen-Image-2.1` base, `gguf`/`text-to-image`/`stable-diffusion.cpp` tags, and English/Chinese languages from frontmatter; leejet `stable-diffusion.cpp` conversion claim and Qwen Research License pointer from intro; `stable-diffusion.cpp` host and `docs/qwen_image_2.1.md` pointer from stable-diffusion.cpp section; leejet-fork prerequisite, `city96` maintenance note, `qwen_image_2_1_t2i_gguf.json` workflow link, and 200x200 remote example image from ComfyUI section.
