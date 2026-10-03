---
license: other
license_name: qwen-research
license_link: LICENSE
base_model:
- pottokao/Qwen-Image-2.1-PE-T2I-Heretic
tags:
- gguf
- quantized
- llama-cpp
- heretic
- abliterated
- prompt-rewriting
- qwen-image
- comfyui
---

# Qwen-Image-2.1-PE-T2I — Heretic — GGUF

> **Not affiliated with, or endorsed by, Alibaba / Qwen.** Community derivative of
> [`Qwen/Qwen-Image-2.1-PE-T2I`](https://huggingface.co/Qwen/Qwen-Image-2.1-PE-T2I),
> redistributed under the **Qwen Research License** (copy included as `LICENSE`, per §3.a).
> **Non-commercial use only**; commercial use needs a separate licence from Qwen.

**Q4_K_M** build of
[`pottokao/Qwen-Image-2.1-PE-T2I-Heretic`](https://huggingface.co/pottokao/Qwen-Image-2.1-PE-T2I-Heretic)
— the Qwen-Image-2.1 **prompt rewriter** with refusal behaviour removed
(3/100 refusals @ KL 0.036, from 98/100 — best of a 1,600-trial search; dominates the earlier 7/100 @ 0.039, tag `v1-trial384`).

> **`system_prompt.txt` is included and the model is useless without it.** That 10 KB
> document *is* the output contract — structure, register, length, and the JSON shape.
> Load it as the system message.

## Made with a simple node

The sample / showcase images in this repo were generated with the technique behind **[ComfyUI-QwenImage-PhotoStyles](https://github.com/pottokao-dotcom/ComfyUI-QwenImage-PhotoStyles)** — a small ComfyUI node (17 photographic styles; one short prompt becomes a full styled prompt via the PE-T2I rewriter). If you're interested in how the images are made, the node and its recipe are there.

## What this is for

A short request in any language goes in; one JSON line comes out with a detailed
English image prompt and a recommended aspect ratio:

```json
{"rewritten_prompt": "...", "wh_ratio": "3:2"}
```

It is an **LLM, not a text encoder.** In ComfyUI it belongs in an LLM/GGUF node that
rewrites your prompt *before* it reaches the DiT — it does **not** load into
`CLIPLoader`. For the Qwen-Image-2.1 *text encoder*, see
[`…-Text-Encoder-Heretic`](https://huggingface.co/pottokao/Qwen-Image-2.1-Text-Encoder-Heretic).

## Available quantizations

| File | Size | Notes |
|---|---|---|
| `pe_t2i_heretic-Q4_K_M.gguf` | 5.49 GB | smallest; `token_embd` kept at Q6_K |
| `pe_t2i_heretic-Q6_K.gguf` | 7.61 GB | higher quality; `token_embd` kept at Q8_0 |
| `pe_t2i_heretic-Q8_0.gguf` | 9.53 GB | near-lossless |

All load the same way (`llama-server -m <file>`); pick by available VRAM.

## One deviation from stock Q4_K_M

`token_embd` is kept at **Q6_K** instead of Q4_K. Everything else is standard Q4_K_M
(llama.cpp already promotes `output` to Q6_K on its own).

The reason: every official NVIDIA NVFP4 checkpoint for this model family leaves the
token embedding untouched — across `Qwen3-8B`, `Qwen3-32B`, `Qwen3-30B-A3B`,
`Qwen3.5-122B-A10B` and `Qwen3.5-397B-A17B`, and also in the one official
*mixed-precision* recipe (`Qwen3.6-27B`), which quantizes `lm_head` to 4-bit but still
does not touch the embedding. Stock `Q4_K_M` does compress it. Raising it back costs
**0.25 GB** and cannot be worse than leaving it at Q4_K.

| | stock Q4_K_M | this build |
|---|---|---|
| `token_embd` | Q4_K (0.53 GB) | **Q6_K (0.78 GB)** |
| `output` | Q6_K | Q6_K |
| everything else | Q4_K / Q6_K | unchanged |
| total | 5.24 GB | **5.49 GB** |

## Run it

```bash
llama-server -m pe_t2i_heretic-Q4_K_M.gguf --host 0.0.0.0 --port 8080 \
             -ngl 99 -c 16384 --jinja -a pe-t2i
```

Then POST to `/v1/chat/completions` with `system_prompt.txt` as the system message.
Loads in a few seconds; fits on an 8 GB card.

## Conversion

```bash
python convert_hf_to_gguf.py <bf16 model> --outfile pe_bf16.gguf --outtype bf16 --no-mtp
llama-quantize --token-embedding-type q6_K --output-tensor-type q6_K \
               pe_bf16.gguf pe_t2i_heretic-Q4_K_M.gguf Q4_K_M
```

**`--no-mtp` is required.** This model's `config.json` carries
`text_config.mtp_num_hidden_layers` with the value `null`. Without the flag the
converter does `int += None` and dies with a `TypeError`. The key *existing* with a
null value is the trap — `.get(key, 0)` returns `None`, not the default.

## What was checked, and what wasn't

**Checked — it still does its job.** Four requests (three Chinese, one English)
through `llama-server`: 4/4 produced strictly valid JSON with exactly the
`rewritten_prompt` / `wh_ratio` keys, 2053–3351 characters. The bf16 source produces
2450–3320 on the same style of input, so the length discipline survives quantization.

**Not checked — a clean perplexity comparison.** I ran one and it returned
self-contradictory numbers (the unquantized bf16 GGUF scored *worse* than its own
quantizations, which is not physically sensible), so I am not reporting it. Take the
functional check above as the evidence, and nothing more.

**Tried and not shipped — an imatrix build.** I generated an importance matrix from
in-domain data and quantized with it. It passed the same functional check, but the
calibration corpus was badly designed: the 10 KB system prompt appears in every sample,
so ~88% of the 341 KB corpus was one repeated document, which would dominate the
importance statistics. Rather than ship a build I can't justify, it's left out. A
properly diversified corpus would be the way to revisit this.

## 🖼️ Showcase

<table>
<tr><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/01.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/01.jpg" width="100%"></a><br><sub>Warm Documentary</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/02.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/02.jpg" width="100%"></a><br><sub>Candid B&W Street</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/04.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/04.jpg" width="100%"></a><br><sub>Vivid Everyday Color</sub></td></tr>
<tr><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/05.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/05.jpg" width="100%"></a><br><sub>Black Fury</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/06.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/06.jpg" width="100%"></a><br><sub>Geometry of Light</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/07.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/07.jpg" width="100%"></a><br><sub>Frozen Film Still</sub></td></tr>
<tr><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/08.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/08.jpg" width="100%"></a><br><sub>Deadpan Large-Format</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/09.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/09.jpg" width="100%"></a><br><sub>White Leap</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/10.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/10.jpg" width="100%"></a><br><sub>Corner Elegance</sub></td></tr>
<tr><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/11.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/11.jpg" width="100%"></a><br><sub>Raw B&W Fashion</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/12.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/12.jpg" width="100%"></a><br><sub>Color Behind Glass</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/13.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/13.jpg" width="100%"></a><br><sub>High-Contrast Reportage</sub></td></tr>
<tr><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/14.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/14.jpg" width="100%"></a><br><sub>Lyrical Landscape</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/15.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/15.jpg" width="100%"></a><br><sub>Hyper Chic East</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/16.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/16.jpg" width="100%"></a><br><sub>Street in the Mirror</sub></td></tr>
<tr><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/18.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/18.jpg" width="100%"></a><br><sub>Plain Portrait</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/19.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/19.jpg" width="100%"></a><br><sub>Melancholy B&W</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/20.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/20.jpg" width="100%"></a><br><sub>Fairytale Giants</sub></td></tr>
<tr><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/21.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/21.jpg" width="100%"></a><br><sub>Cold Power</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/22.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/22.jpg" width="100%"></a><br><sub>Cold Power</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/23.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/23.jpg" width="100%"></a><br><sub>Hyper Chic East</sub></td></tr>
<tr><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/24.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/24.jpg" width="100%"></a><br><sub>Fairytale Giants</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/25.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/25.jpg" width="100%"></a><br><sub>Hyper Chic East</sub></td><td width="33%"><a href="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/blob/main/showcase_assets/26.jpg"><img src="https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF/resolve/main/showcase_assets/26.jpg" width="100%"></a><br><sub>White Leap</sub></td></tr>
</table>

**This is what Q4_K_M across the board looks like** — every image above was made with:

| Part | File |
|---|---|
| PE-T2I rewriter | [`pe_t2i_heretic-Q4_K_M.gguf`](https://huggingface.co/pottokao/Qwen-Image-2.1-PE-T2I-Heretic-GGUF) |
| Text encoder | [`qwen3vl_8b_heretic-Q4_K_M.gguf`](https://huggingface.co/pottokao/Qwen-Image-2.1-Text-Encoder-Heretic-GGUF) + f16 mmproj |
| DiT | [`qwen_image_2.1-Q4_K_M.gguf`](https://huggingface.co/pottokao/Qwen-Image-2.1-DiT-GGUF) |
| VAE | `qwen_image_2.1_vae_bf16.safetensors` (official) |

<sub>AI-generated. Style homage only — not affiliated with or endorsed by the photographers.</sub>

## Showcase

Outputs from the full pipeline this rewriter drives (rewriter → Qwen-Image-2.1
text encoder → DiT) — the image engine behind a "photography masters" system that
originally ran on DiffusionGemma and has since been moved onto this pipeline. Each
was generated from a one-line prompt; the rewriter expanded it into the scene,
palette and framing below. One seed per cell, no retouching.

<table>
<tr>
<td width="50%"><img src="showcase_assets/black_fury_night_dog.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/black_fury_street_dog.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/deadpan_portrait_pair.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/geometry_of_light_stairs.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/color_behind_glass_rain.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/surreal_bw_street.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/soft_everyday_light_child.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/soft_everyday_light_harbour.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/warm_documentary_portrait.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/pale_light_glass.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/vivid_everyday_diner.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/vivid_garden_goldfish.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/bold_minimal_flower.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/soft_color_slip.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/private_diary_flowers.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/private_diary_portrait.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/private_diary_street.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/lyrical_landscape.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/nocturnal_stage.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/deadpan_industrial_tower.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/minimal_seascape.png" width="100%"></td>
<td width="50%"><img src="showcase_assets/large_format_containers.png" width="100%"></td>
</tr>
<tr>
<td width="50%"><img src="showcase_assets/large_format_retail.png" width="100%"></td>
</tr>
</table>

<sub>AI-generated. Style homage only — not affiliated with or endorsed by the photographers.</sub>

## Other builds

| Repo | Format | Runtime |
|---|---|---|
| [`…-PE-T2I-Heretic`](https://huggingface.co/pottokao/Qwen-Image-2.1-PE-T2I-Heretic) | bf16 safetensors | `transformers` |
| **this repo** | GGUF Q4_K_M | llama.cpp / ComfyUI LLM node |
| [`…-PE-T2I-Heretic-NVFP4`](https://huggingface.co/pottokao/Qwen-Image-2.1-PE-T2I-Heretic-NVFP4) | NVFP4 mixed precision | vLLM |

Results, the Pareto front of other operating points, and the measurement caveats are in
the [base repo](https://huggingface.co/pottokao/Qwen-Image-2.1-PE-T2I-Heretic).