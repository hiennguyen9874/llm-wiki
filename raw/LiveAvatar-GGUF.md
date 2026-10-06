---
license: apache-2.0
base_model: Wan-AI/Wan2.2-S2V-14B
library_name: audio.cpp
pipeline_tag: image-to-video
tags:
  - audio.cpp
  - gguf
  - audio-to-video
  - liveavatar
  - wan2.2
---

# LiveAvatar GGUF for audio.cpp

Native GGUF package of [Wan-AI/Wan2.2-S2V-14B](https://huggingface.co/Wan-AI/Wan2.2-S2V-14B)
with the official [Quark-Vision/Live-Avatar](https://huggingface.co/Quark-Vision/Live-Avatar)
LoRA merged for [audio.cpp](https://github.com/0xShug0/audio.cpp). LiveAvatar
generates an audio-driven avatar video from a reference image, speech audio,
and a text description.

## Files

| File | Description |
|---|---|
| `Wan2.2-S2V-Support-Q4_K_S-F16.gguf` | UMT5 text encoder, Wav2Vec2 audio encoder, tokenizer, and embedded audio.cpp model specification. |
| `Wan2.2-S2V-VAE-F16.gguf` | Wan video VAE in F16 with the embedded audio.cpp model specification. |
| `Wan2.2-S2V-14B-NVFP4-LORA.gguf` | LiveAvatar Wan2.2 S2V denoiser with the official LiveAvatar adapter. |

All three files are required.

## Low-VRAM mode

LiveAvatar can keep the denoiser transformer blocks in pinned host memory and
stage one layer group at a time. This makes 720p generation possible near a
16 GiB VRAM limit, at the cost of additional host-to-device transfers.

The validated 1280x720 run generated 93 frames at 16 FPS (5.81 seconds of
video) in **276 seconds wall time** (4 minutes 36 seconds) and peaked at
**15,993 MiB VRAM** on an RTX 5090.

| Control | Value |
|---|---:|
| `liveavatar.denoiser_weight_streaming` | `true` |
| `denoiser_layerwise` | `true` |
| `denoiser_layerwise_batch` | `16` |
| `target_cache_blocks` | `1` |
| `vae_cache_f16` | `true` |
| `vae_encoder_chunk_size` | `4` |
| `vae_decoder_tile_size` | `320` |

Weight streaming is slower than the normal resident-weight path. In a matched
240p comparison, model time increased from 13.33 to 21.73 seconds, or about
**1.63x slower**. The exact slowdown depends on resolution, hardware, and host
memory bandwidth.

### Full-duration 720p example

This example uses the official LiveAvatar
[Cyclops Baker image](examples/cyclops/reference.jpg) and
[speech audio](examples/cyclops/reference.wav). The official reference image is
only **720x400**, so this example also shows 1280x720 generation from a
lower-resolution image condition. The complete 11.6-second WAV is retained in
the generated video.

![Official Cyclops Baker reference](examples/cyclops/reference.jpg)

<video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/cyclops/output-720p-weight-streaming.mp4"></video>

[Download the generated video](examples/cyclops/output-720p-weight-streaming.mp4)

| Measurement | Result |
|---|---:|
| Reference image | 720x400 |
| Reference audio | 11.60 s, 24 kHz mono |
| Output | 1280x720, 16 FPS, 11.60 s |
| Generated frames | 189 before audio-length muxing |
| LiveAvatar clips | 4 |
| Peak VRAM | 16,126 MiB (15.75 GiB) |
| Session time | 543.03 s (9 min 3 s) |
| Full CLI wall time | 557.33 s (9 min 17 s) |

The run used the low-VRAM controls above with denoiser weight streaming,
layerwise batch size 16, one target-cache block, F16 VAE cache, VAE encoder
chunk size 4, and VAE decoder tile size 320. Measurements were collected with
the CUDA debug build on an NVIDIA GeForce RTX 5090.

### 480p cache trade-off

These two videos use the same Cyclops Baker inputs, prompt, seed, four clips,
and complete 11.6-second audio. Only `target_cache_blocks` changes. A longer
cache retains more temporal context from preceding video blocks and can improve
continuity across clip boundaries, but it does not directly increase per-frame
resolution or detail.

| Target cache | Peak VRAM | Peak host RAM | Session time | Practical trade-off |
|---:|---:|---:|---:|---|
| 2 blocks | 15,311 MiB | 43.33 GiB | 317.92 s | Lower memory and faster; recommended for iteration. |
| 3 blocks | 19,357 MiB | 56.94 GiB | 512.69 s | More temporal history, but nearly exhausts a 64 GB host and uses swap. |

<table>
<tr>
<td width="50%"><strong>Two cache blocks</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/cyclops/output-480p-cache2.mp4"></video><br><code>target_cache_blocks=2</code></td>
<td width="50%"><strong>Three cache blocks</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/cyclops/output-480p-cache3.mp4"></video><br><code>target_cache_blocks=3</code></td>
</tr>
</table>

480p is the better starting point for prompt, identity, motion, and cache-window
experiments. Iterate at 480p, select the strongest result, and upscale that
video afterward instead of paying the 720p generation cost for every attempt.

## Quality comparison

Each clip uses the same reference image, audio, prompt, seed `420`, four Euler
steps, guidance `0`, scheduler shift `3`, `416x240` resolution, 16 FPS, and 84
requested frames (81 output frames, 5.06 seconds). The reference uses
SageAttention, `memory_saver=true`, full target cache, F32 VAE cache, no VAE
tiling, and non-layerwise denoising. Each other cell changes only the parameter
shown below the video.

Inputs: [reference speech](examples/dwarven_blacksmith.wav) and
[reference image](examples/dwarven_blacksmith.jpg).

Prompt: `A stout, cheerful dwarf with a magnificent braided beard adorned with
metal rings, wearing a heavy leather apron. He is standing in his fiery,
cluttered forge, laughing heartily as he explains the mastery of his craft,
holding up a glowing hammer. Style of Blizzard Entertainment cinematics, warm,
dynamic lighting from the forge.`

Measured with the CUDA debug build on an NVIDIA GeForce RTX 5090. Wall time
includes model loading and output generation. Peak VRAM is total device memory
used during the run.

| Case | Controlled option | Peak VRAM (MiB) | Wall time (s) |
|---|---|---:|---:|
| Reference | Reference controls | 25,586 | 24.44 |
| FlashAttention | `sage_attention=false` | 25,990 | 24.90 |
| F16 VAE cache | `vae_cache_f16=true` | 22,896 | 25.16 |
| VAE decoder tiling | `vae_decoder_tile_size=320` | 25,566 | 24.51 |
| Target cache: 1 block | `target_cache_blocks=1` | 19,935 | 23.28 |
| Target cache: 4 blocks | `target_cache_blocks=4` | 22,761 | 24.40 |
| Layerwise denoising | `denoiser_layerwise=true`, `denoiser_layerwise_batch=16` | 25,333 | 26.62 |

<table>
<tr>
<td width="50%"><strong>Reference</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/quality/reference.mp4"></video><br><code>reference controls</code></td>
<td width="50%"><strong>FlashAttention</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/quality/flash-attention.mp4"></video><br><code>sage_attention=false</code></td>
</tr>
<tr>
<td width="50%"><strong>F16 VAE cache (current default)</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/quality/vae-cache-f16.mp4"></video><br><code>vae_cache_f16=true</code></td>
<td width="50%"><strong>VAE decoder tiling</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/quality/vae-tile-320.mp4"></video><br><code>vae_decoder_tile_size=320</code></td>
</tr>
<tr>
<td width="50%"><strong>Target cache: 1 block</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/quality/target-cache-1.mp4"></video><br><code>target_cache_blocks=1</code></td>
<td width="50%"><strong>Target cache: 4 blocks</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/quality/target-cache-4.mp4"></video><br><code>target_cache_blocks=4</code></td>
</tr>
<tr>
<td width="50%"><strong>Layerwise denoising</strong><br><video controls playsinline preload="metadata" width="100%" src="https://huggingface.co/audio-cpp/LiveAvatar-GGUF/resolve/main/examples/quality/layerwise-16.mp4"></video><br><code>denoiser_layerwise=true</code>, <code>denoiser_layerwise_batch=16</code></td>
<td width="50%"></td>
</tr>
</table>

## Run

```bash
audiocpp_cli \
  --task gen \
  --family liveavatar \
  --model /path/to/LiveAvatar-GGUF \
  --backend cuda \
  --threads 8 \
  --audio /path/to/reference.wav \
  --text "A detailed description of the speaker and scene." \
  --request-option generation_mode=liveavatar \
  --request-option reference_image_path=/path/to/reference.jpg \
  --request-option height=240 \
  --request-option width=416 \
  --out-dir outputs/liveavatar \
  --log
```

The default LiveAvatar configuration uses four Euler steps, scheduler shift 3,
guidance scale 0, seed 420, 48 frames per clip, SageAttention, and 16 FPS.

For lower VRAM use, add:

```bash
--session-option liveavatar.denoiser_weight_streaming=true \
--request-option denoiser_layerwise=true \
--request-option denoiser_layerwise_batch=16
```

See the [audio.cpp LiveAvatar documentation](https://github.com/0xShug0/audio.cpp/blob/main/docs/community_models/liveavatar.md)
for resolution, duration, and memory-control options.

## License

LiveAvatar and its Wan2.2 base model are released under the Apache License 2.0.
This repository includes the upstream license in `LICENSE`. The GGUF conversion
is a packaging format for audio.cpp and is not an official upstream release.
