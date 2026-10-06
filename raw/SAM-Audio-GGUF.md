---
license: other
license_name: sam-license
license_link: LICENSE
base_model: facebook/sam-audio-large
library_name: audio.cpp
pipeline_tag: audio-to-audio
tags:
  - audio.cpp
  - gguf
  - audio-separation
---

# SAM Audio GGUF

GGUF weights for native inference with
[audio.cpp](https://github.com/0xShug0/audio.cpp). SAM Audio separates a sound
described by text, a masked image or video, or positive and negative time spans
from an input recording.

## Upstream

These packages use the original Meta checkpoints, not the separate `-tv` variants.

| Variant | GGUF | Pinned checkpoint |
|---|---|---|
| Small | `sam-audio-small-f32.gguf` | [facebook/sam-audio-small](https://huggingface.co/facebook/sam-audio-small/tree/20b65f56888142eebe7c37448c6f6b3b32600e9b) |
| Base | `sam-audio-base-f32.gguf` | [facebook/sam-audio-base](https://huggingface.co/facebook/sam-audio-base/tree/81f64008f9f957c2b57a45923fb5299c66e9d186) |
| Large | `sam-audio-large-f32.gguf` | [facebook/sam-audio-large](https://huggingface.co/facebook/sam-audio-large/tree/5f2cd3a9471a08c7282c06036be6893e18de8b70) |

The [official SAM Audio implementation](https://github.com/facebookresearch/sam-audio) is pinned to
[bb4c699](https://github.com/facebookresearch/sam-audio/tree/bb4c6999d2677c7402360e426afc01ddfad6dce0).

Each GGUF contains SAM weights, T5 text encoder, tokenizer, configuration, and
audio.cpp model spec. No separate text encoder is needed. F32 packages retain
the original weights, checked byte-for-byte against the source tensors.
BF16 and Q8_0 packages are also available for each variant; both were converted
directly from the source safetensors. Biases, normalization vectors, and
scale/shift tables remain F32. Q8_0 denotes mixed quantized storage, not that
every tensor is quantized.

## Usage

```bash
audiocpp_cli --task s2s --family sam_audio \
  --model /path/to/SAM-Audio-GGUF/sam-audio-small-f32.gguf --backend cuda \
  --audio input.wav --text "man speaking" --seed -1 \
  --out-dir outputs/separation --log
```

Outputs are `target.wav` and `residual.wav`, mono 48 kHz. Optional temporal
prompts use `--request-option 'anchors=[["+",0.5,2.0],["-",3.0,4.0]]'`.
The runtime also accepts a masked static image with
`--request-option reference_image_path=masked.png`, or a masked video with
`--request-option reference_video_path=masked.mp4`. Video decoding requires
FFmpeg/libav runtime libraries. Use one visual option at a time and keep the
video and input audio time origins aligned. Automatic span prediction and
candidate ranking are not included.

See the [model usage guide](https://github.com/0xShug0/audio.cpp/blob/main/docs/models/sam_audio.md)
for all request options. Code tested on CUDA/Vulkan/Metal.

> [!WARNING]
> All parity, performance, and VRAM results below were measured with watermarking enabled to match the official Python implementation, which adds a watermark to its output. The final audio.cpp version will return audio WITHOUT the added watermark, so these results do not describe the final implementation.

## Controlled Parity With Python

Parity was tested separately from performance on CUDA with F32 weights and
TF32 disabled in both implementations (`NVIDIA_TF32_OVERRIDE=0`). Python used
seed 42; C++ replayed its exact diffusion noise and watermark bits. Both used
the same 14.975-second office recording, `man speaking` prompt, and 16 midpoint
steps. C++ computed its own encoder features, diffusion, and decoded audio.

Each row compares the final C++ waveforms directly against official Python,
including bounded-memory mode. Higher cosine similarity is better; 1 is exact
directional agreement, not a claim of byte-identical waveforms.

| Variant | C++ mode | Target cosine | Residual cosine |
|---|---|---:|---:|
| Small F32 | Normal | 0.99999945 | 0.99999864 |
| Small F32 | Bounded memory | 0.99999968 | 0.99999896 |
| Base F32 | Normal | 0.99999956 | 0.99999558 |
| Base F32 | Bounded memory | 0.99999950 | 0.99999753 |
| Large F32 | Normal | 0.99999980 | 0.99999888 |
| Large F32 | Bounded memory | 0.99999984 | 0.99999936 |

All rows exceeded 0.9999 for both outputs. Repeating each controlled C++ run
within the same session produced byte-identical outputs. 

## Ordinary CUDA Performance With Python

Measured on an NVIDIA RTX 5090 (32 GB), using a 14.975-second recording from the
[official office example](https://github.com/facebookresearch/sam-audio/blob/bb4c6999d2677c7402360e426afc01ddfad6dce0/examples/assets/office.mp4)
and the text prompt `man speaking`.

- Both implementations use the original weights, 16 midpoint steps, one
  candidate, and no visual or span prompts. Optional ranking and span-prediction
  models are not loaded in Python.
- Ordinary inference: no fixed or replayed random noise, no TF32 override, and
  no forced precision/autocast changes. C++ uses `--seed -1`; Python does not
  set a seed. Python uses PyTorch 2.11.0+cu128; C++ uses a debug build and 8 threads.
- Warm inference time is the median of the last three of five sequential
  requests in one session. It excludes model loading and file I/O. RTF is
  inference time divided by input duration; lower is faster.
- Peak VRAM is process memory sampled with `nvidia-smi` every 50 ms across
  loading and all five requests, using the same method for Python and C++.

| Variant | C++ warm time | C++ RTF | C++ peak VRAM | Python warm time | Python RTF | Python peak VRAM |
|---|---:|---:|---:|---:|---:|---:|
| Small F32 | 684 ms | 0.0456 | 8,500 MiB | 746 ms | 0.0498 | 10,972 MiB |
| Base F32 | 918 ms | 0.0613 | 11,010 MiB | 1,105 ms | 0.0738 | 13,414 MiB |
| Large F32 | 1,542 ms | 0.1030 | 17,826 MiB | 2,103 ms | 0.1405 | 20,568 MiB |

These are text-conditioned, single-recording measurements, not a benchmark of
visual prompting, automatic span prediction, or candidate ranking.

**Outputs from these independent-randomness performance runs are not used for
parity comparisons.**

## BF16 and Q8 Compared With C++ F32

The following are a separate C++-only comparison on the same RTX 5090 and
14.975-second input. Ordinary performance uses the five-request methodology
above, `--seed -1`, and no TF32 or precision overrides. F32 was remeasured for
this comparison; no Python model was run.

| Variant | Storage | Warm time | RTF | Peak VRAM |
|---|---|---:|---:|---:|
| Small | F32 | 700 ms | 0.04673 | 8,500 MiB |
| Small | BF16 | 674 ms | 0.04501 | 7,366 MiB |
| Small | Q8_0 | 673 ms | 0.04493 | 6,834 MiB |
| Base | F32 | 960 ms | 0.06408 | 11,010 MiB |
| Base | BF16 | 785 ms | 0.05241 | 8,644 MiB |
| Base | Q8_0 | 794 ms | 0.05302 | 7,524 MiB |
| Large | F32 | 1,566 ms | 0.10457 | 17,826 MiB |
| Large | BF16 | 1,146 ms | 0.07652 | 12,092 MiB |
| Large | Q8_0 | 1,051 ms | 0.07018 | 9,378 MiB |

Output drift was measured in **separate controlled C++ runs**, using seed 42
and `NVIDIA_TF32_OVERRIDE=0` for every dtype. Each output is compared against
that variant's C++ F32 waveform, not Python. These runs supply no performance
or VRAM figures.

| Variant | Storage | Target cosine vs F32 | Residual cosine vs F32 |
|---|---|---:|---:|
| Small | BF16 | 0.999940 | 0.999763 |
| Small | Q8_0 | 0.999476 | 0.999095 |
| Base | BF16 | 0.999918 | 0.999788 |
| Base | Q8_0 | 0.999623 | 0.999069 |
| Large | BF16 | 0.999743 | 0.999712 |
| Large | Q8_0 | 0.999590 | 0.999273 |

BF16 reduced peak VRAM by 13-32%; Q8_0 reduced it by 20-47% in this workload.
Drift is expected. These short text-conditioned checks do not establish equal
quality for every recording or validate reduced-precision visual prompting
and bounded-memory long-form execution. F32 remains available as the reference.

## Bounded-Memory Mode

Enable the experimental session option to reduce long-recording GPU workspace:

```bash
--session-option sam_audio.memory_bounded=true
```

The option defaults to `false`, and its name is provisional. The existing Small
GGUF predates this option; add `--model-spec-override model_specs/sam_audio.json`
from a checkout that includes bounded-memory support. The Base and Large GGUFs
include the option in their embedded specs.

The mode retains full-recording diffusion and attention. Codec convolutions
use tiles with receptive-field context, and watermark LSTM state carries
between tiles. It does not separate independent audio chunks and crossfade
them. Intermediate sequences reside in host RAM, which still grows with input
length. Transfers and overlap computation can make it slower on short inputs;
small numerical differences are possible. The configured model context limit
remains 400 seconds.

The following CUDA tests used a **180-second input** made by repeating the same
example to 180 seconds, with the same prompt and inference settings as above.
Each C++ result is the first inference in a fresh session, including graph
setup but excluding model loading and file I/O. Peak VRAM includes loading
and inference. These are not warm medians.

| Variant | C++ bounded time | C++ RTF | C++ peak VRAM | Official Python, same input |
|---|---:|---:|---:|---|
| Small F32 | 8.768 s | 0.0487 | 6,550 MiB | CUDA out of memory |
| Base F32 | 11.109 s | 0.0617 | 9,212 MiB | CUDA out of memory |
| Large F32 | 17.038 s | 0.0947 | 16,244 MiB | CUDA out of memory |

All three C++ runs produced the complete target and residual recordings.
Python ran out of memory in its audio encoder on the same 32 GB GPU, using
its default precision and allocator settings. This demonstrates completion
and memory usage for this workload, **not 180-second parity against Python**:
Python did not produce a full-length reference. Other hardware or Python
memory-saving configurations may behave differently.

## License

SAM Audio weights are distributed under the [SAM License](LICENSE), dated
November 19, 2025. The included T5 encoder is from
[Google T5 Base](https://huggingface.co/google-t5/t5-base) and retains its
[Apache-2.0 license](LICENSE-T5). Conversion does not replace the upstream license terms.
