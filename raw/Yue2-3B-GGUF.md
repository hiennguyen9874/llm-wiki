---
license: cc-by-nc-4.0
base_model:
- m-a-p/YuE2-3B
library_name: audio.cpp
tags:
- audio.cpp
- gguf
- music-generation
- yue2
pipeline_tag: text-to-audio
---

# Yue2-3B GGUF for audio.cpp

This repository contains audio.cpp-native GGUF weights for Yue2-3B. The model has been merged into the main branch.

LoRA support added in release 0.8.1.

## Files

| File | Description |
|---|---|
| `yue2-3b-bf16.gguf` | Yue2-3B main model, BF16 weights. |
| `yue2-3b-q8_0.gguf` | Yue2-3B main model, Q8_0 quantized weights. |
| `yue2-3b-q4_0.gguf` | Yue2-3B main model, Q4_0 quantized weights. |
| `yue2-vae-f32.gguf` | Yue2 VAE, F32 weights. |
| `yue2-vae-f16.gguf` | Yue2 VAE, F16 weights. |
| `sidecars/yue2-model-config.json` | Yue2-3B model config. |
| `sidecars/yue2-generation-config.json` | Yue2 generation defaults. |
| `sidecars/yue2-qwen.tiktoken` | Qwen tokenizer used by Yue2. |
| `sidecars/yue2-vae-config.json` | Yue2 VAE config. |
| `examples/demo1.wav` | Direct text-to-music demo, `cot=off`. |
| `examples/demo1_q8.wav` | Same demo generated with `yue2-3b-q8_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/demo1_q4_0.wav` | Same demo generated with `yue2-3b-q4_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/demo2.wav` | Full planning demo, `cot=full`. |
| `examples/demo2_q8.wav` | Same demo generated with `yue2-3b-q8_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/demo2_q4_0.wav` | Same demo generated with `yue2-3b-q4_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/demo3.wav` | Melody-conditioned cover demo, `cot=melody`. |
| `examples/demo3_q8.wav` | Same demo generated with `yue2-3b-q8_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/demo3_q4_0.wav` | Same demo generated with `yue2-3b-q4_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/demo4.wav` | Full score-conditioned demo, `cot=full`. |
| `examples/demo4_q8.wav` | Same demo generated with `yue2-3b-q8_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/demo4_q4_0.wav` | Same demo generated with `yue2-3b-q4_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/tonight-awake-audiocpp-current.wav` | audio.cpp output from the official `tonight-awake` example. |
| `examples/tonight-awake-audiocpp-current_q8.wav` | Same official example generated with `yue2-3b-q8_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/tonight-awake-audiocpp-current_q4_0.wav` | Same official example generated with `yue2-3b-q4_0.gguf` and `yue2-vae-f16.gguf`. |
| `examples/yue2_demo.mp4` | Short audio.cpp Yue2 WebUI demo video. |

## Demos

The demos below were generated with `yue2-3b-bf16.gguf` and `yue2-vae-f32.gguf`.
The `_q8.wav` comparison files were generated with `yue2-3b-q8_0.gguf` and
`yue2-vae-f16.gguf` using the same prompts and seeds. The `_q4_0.wav`
comparison files were generated with `yue2-3b-q4_0.gguf` and
`yue2-vae-f16.gguf`.
Replace `<AUDIOCPP>` with your audio.cpp checkout and `<YUE2_GGUF>` with this
downloaded GGUF repo directory.
To generate the Q4_0 versions, use the same commands and replace
`--session-option yue2.model_gguf=yue2-3b-bf16.gguf` with
`--session-option yue2.model_gguf=yue2-3b-q4_0.gguf`, and use
`--session-option yue2.vae_gguf=yue2-vae-f16.gguf`.

## Longform Performance

Measured with audio.cpp server mode on an RTX 5090, using the official
`tonight-awake` longform example. Each run restarted the server and used one
short warmup request before the measured longform request. Peak VRAM was sampled
continuously during the measured request.

| Combo | Audio duration | Wall time | RTF | Peak VRAM |
|---|---:|---:|---:|---:|
| BF16 main + F32 VAE | 224.96s | 60.46s | 0.2688 | 12535 MiB |
| Q8_0 main + F16 VAE | 194.84s | 38.81s | 0.1992 | 8867 MiB |
| Q4_0 main + F16 VAE | 221.12s | 44.15s | 0.1997 | 7755 MiB |

### WebUI demo video

Sorry if the UI is a bit rough. I’m not a UI person and probably messed up some of the nice community UI work while wiring this up.

<video controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/yue2_demo.mp4"></video>

This WebUI demo uses the official Yue2
[`examples/tonight-awake.json`](https://huggingface.co/m-a-p/YuE2-3B/blob/main/examples/tonight-awake.json)
test case.

### Demo 1: direct generation

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo1.wav"></audio>

Q8 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo1_q8.wav"></audio>

Q4_0 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo1_q4_0.wav"></audio>

```bash
<AUDIOCPP>/build/debug/bin/audiocpp_cli \
  --task gen \
  --family yue2 \
  --model <YUE2_GGUF> \
  --backend cuda \
  --threads 8 \
  --text $'[Verse]\nSoft morning light is touching the window.\nI hear the city waking below.\n[Chorus]\nStay with the rhythm, let it carry us home.\nSing with the sunrise, we are never alone.' \
  --request-option 'style=English, indie pop, bright acoustic guitar, soft drums, warm lead vocal, polished demo mix' \
  --request-option cot=off \
  --request-option seed=20260920 \
  --request-option num_inference_steps=8 \
  --session-option yue2.model_gguf=yue2-3b-bf16.gguf \
  --session-option yue2.vae_gguf=yue2-vae-f32.gguf \
  --out demo1.wav \
  --log
```

### Demo 2: full planning

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo2.wav"></audio>

Q8 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo2_q8.wav"></audio>

Q4_0 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo2_q4_0.wav"></audio>

```bash
<AUDIOCPP>/build/debug/bin/audiocpp_cli \
  --task gen \
  --family yue2 \
  --model <YUE2_GGUF> \
  --backend cuda \
  --threads 8 \
  --text $'[Verse]\nA quiet piano opens the evening.\nWarm city lights are starting to glow.\n[Chorus]\nLift every voice into the skyline.\nLet the melody carry us home.' \
  --request-option 'style=English, piano pop, clear lead vocal, gentle bass, soft drums, warm chorus harmonies' \
  --request-option cot=full \
  --request-option seed=20260921 \
  --request-option num_inference_steps=8 \
  --session-option yue2.model_gguf=yue2-3b-bf16.gguf \
  --session-option yue2.vae_gguf=yue2-vae-f32.gguf \
  --out demo2.wav \
  --log
```

### Demo 3: melody-conditioned cover

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo3.wav"></audio>

Q8 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo3_q8.wav"></audio>

Q4_0 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo3_q4_0.wav"></audio>

This demo uses the upstream
[`examples/melody.abc`](https://huggingface.co/m-a-p/YuE2-3B/blob/main/examples/melody.abc).

```bash
<AUDIOCPP>/build/debug/bin/audiocpp_cli \
  --task gen \
  --family yue2 \
  --model <YUE2_GGUF> \
  --backend cuda \
  --threads 8 \
  --text $'[Verse]\nWe follow the melody line.\nThe rhythm keeps everything fine.\n[Chorus]\nHold that shape and make it new.\nChange the color, keep the view.' \
  --request-option 'style=English, jazz funk cover, warm Rhodes, round bass, light drums, relaxed vocal, clean live band feel' \
  --request-option cot=melody \
  --request-option abc_file=<AUDIOCPP>/reference/YuE/examples/melody.abc \
  --request-option seed=20260922 \
  --request-option num_inference_steps=8 \
  --session-option yue2.model_gguf=yue2-3b-bf16.gguf \
  --session-option yue2.vae_gguf=yue2-vae-f32.gguf \
  --out demo3.wav \
  --log
```

### Demo 4: full score conditioning

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo4.wav"></audio>

Q8 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo4_q8.wav"></audio>

Q4_0 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/demo4_q4_0.wav"></audio>

This demo uses the upstream
[`examples/score-jazz.abc`](https://github.com/multimodal-art-projection/YuE/blob/main/examples/score-jazz.abc).

```bash
<AUDIOCPP>/build/debug/bin/audiocpp_cli \
  --task gen \
  --family yue2 \
  --model <YUE2_GGUF> \
  --backend cuda \
  --threads 8 \
  --text $'[Verse]\nThe room begins with a gentle phrase.\nThe harmony turns through a golden haze.\n[Chorus]\nHold the note and let it rise.\nMorning opens up the sky.' \
  --request-option 'style=English, piano pop with jazz harmony, clear lead vocal, gentle bass, tasteful drum fills' \
  --request-option cot=full \
  --request-option abc_file=<AUDIOCPP>/reference/YuE/examples/score-jazz.abc \
  --request-option seed=20260923 \
  --request-option num_inference_steps=8 \
  --session-option yue2.model_gguf=yue2-3b-bf16.gguf \
  --session-option yue2.vae_gguf=yue2-vae-f32.gguf \
  --out demo4.wav \
  --log
```

### Official example: tonight-awake

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/tonight-awake-audiocpp-current.wav"></audio>

Q8 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/tonight-awake-audiocpp-current_q8.wav"></audio>

Q4_0 + F16 VAE:

<audio controls src="https://huggingface.co/audio-cpp/Yue2-3B-GGUF/resolve/main/examples/tonight-awake-audiocpp-current_q4_0.wav"></audio>

This WAV was generated using audio.cpp from the official Yue2 example:
[`examples/tonight-awake.json`](https://huggingface.co/m-a-p/YuE2-3B/blob/main/examples/tonight-awake.json).

## Upstream

These GGUF files are converted from:

- Upstream HF repo: [`m-a-p/YuE2-3B`](https://huggingface.co/m-a-p/YuE2-3B)
- Upstream revision used for this package:
  `1a96eca688d6ae5d7f0feb88573fec89920fcd19`

## License

The upstream model is released under `cc-by-nc-4.0`. This GGUF package follows
the same license. See the upstream repository for the full license terms and
model card details.