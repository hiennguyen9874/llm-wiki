---
license: mit
base_model: tencent/AuK
pipeline_tag: text-to-speech
tags:
  - audio
  - speech
  - text-to-speech
  - zero-shot-tts
  - voice-cloning
  - speech-generation
  - speech-editing
  - speech-enhancement
  - source-separation
  - speech-separation
  - instruction-guided
  - diffusion
  - audio.cpp
---

# AuK GGUF for audio.cpp

These GGUF files are for use with [audio.cpp](https://github.com/0xShug0/audio.cpp). The card's `base_model` points to the [Tencent AuK base model](https://huggingface.co/tencent/AuK). This package also includes optional files converted from [AuK-Flash](https://huggingface.co/tencent/AuK-Flash); Flash is a separate distilled variant and is not the pinned base model.

> **Output quality:** We validate parity with upstream Python for the tested configuration, not whether AuK's output meets every quality expectation. If a result is disappointing, listen to the corresponding Python reference WAV linked below first. A similar Python result points to the upstream model's behavior, not necessarily an audio.cpp conversion issue. The quantized component combinations have not received the same 16-task parity validation.

Pass the downloaded directory to `audiocpp_cli --model`. Keep the `config/` and `tokenizer/` directories alongside the GGUF files. The default components are `auk-base-f32.gguf`, `qwen2.5-omni-3b-bf16.gguf`, and `auk-vae-f32.gguf`. AuK-Flash requires `--session-option auk.variant=flash`; its default generator is `auk-flash-f32.gguf`. The Qwen component is Qwen2.5-Omni-3B.

For example, instruction TTS with explicitly selected Base components:

```bash
audiocpp_cli --task tts --family auk \
  --model /path/to/AuK-Base-and-Flash-GGUF --backend cuda \
  --session-option auk.variant=base \
  --session-option auk.model_gguf=auk-base-f32.gguf \
  --session-option auk.qwen_gguf=qwen2.5-omni-3b-bf16.gguf \
  --session-option auk.vae_gguf=auk-vae-f32.gguf \
  --text "The next train leaves in ten minutes." \
  --request-option "instruct=A warm male voice speaking clear English." \
  --request-option duration_sec=4 --seed 42 --log --out speech.wav
```

To use AuK-Flash, select `auk.variant=flash` and an `auk-flash-*.gguf` generator. To use the Qwen Q8_0 component, select `auk.qwen_gguf=qwen2.5-omni-3b-q8_0.gguf`. Keep the F32 VAE in either case.

For editing, use `--task gen --audio input.wav --text "<editing instruction>"`. See the [audio.cpp AuK guide](https://github.com/0xShug0/audio.cpp/blob/main/docs/models/auk.md) and the [AuK cookbook](https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md) for request options and example instructions.

## Sixteen-task validation

The 16-task C++/Python comparison forced FP32 inference and disabled TF32 in both implementations. Input audio and reference voices came from the [upstream AuK demo assets](https://github.com/Tencent-Hunyuan/AuK/tree/main/assets/demo-input-audio). Durations not shown below matched the source recording.

All 16 C++ requests completed and produced 24 kHz WAVs with the same frame counts as the Python outputs. The cosine values compare C++ WAVs with the Python baseline. Waveform cosine alone does not establish whether an edit followed its instruction.

| Task | Tested instruction / setting | C++ vs Python WAV cosine | Listen |
| --- | --- | ---: | --- |
| Zero-shot TTS | Reference voice; target sentence; 6 s | 0.999999992 | [Python](./examples/python/zero_shot.wav) / [C++](./examples/cpp/zero_shot.wav) |
| Instruct TTS | Calm woman speaking clear English; 3 s | 0.999999898 | [Python](./examples/python/instruct.wav) / [C++](./examples/cpp/instruct.wav) |
| Speech content editing | Replace "but accepting what we cannot have" with "and living well with dreams unmet"; 7 s | 0.999999982 | [Python](./examples/python/replace_words.wav) / [C++](./examples/cpp/replace_words.wav) |
| Lyric editing | Replace "rear view" with "like you" in isolated vocals | 1.000000000 | [Python](./examples/python/replace_lyrics.wav) / [C++](./examples/cpp/replace_lyrics.wav) |
| Pitch editing | Raise pitch by 2 semitones | 0.999989991 | [Python](./examples/python/raise_pitch.wav) / [C++](./examples/cpp/raise_pitch.wav) |
| Speed editing | Speed 1.5x; 6.86 s | 0.999999993 | [Python](./examples/python/speed_1_5x.wav) / [C++](./examples/cpp/speed_1_5x.wav) |
| Volume editing | Increase volume by 10 dB | 0.999999997 | [Python](./examples/python/increase_volume.wav) / [C++](./examples/cpp/increase_volume.wav) |
| Emotion editing | Change emotion to happy | 0.999999993 | [Python](./examples/python/happy.wav) / [C++](./examples/cpp/happy.wav) |
| Timbre editing | Change to a deep, calm male voice | 0.999999991 | [Python](./examples/python/deep_voice.wav) / [C++](./examples/cpp/deep_voice.wav) |
| De-accent | Change Sichuan-accented speech to standard Mandarin | 0.999999795 | [Python](./examples/python/standard_mandarin.wav) / [C++](./examples/cpp/standard_mandarin.wav) |
| Nonverbal editing | Add a cough before "We tested"; 10.44 s | 0.999991188 | [Python](./examples/python/add_cough.wav) / [C++](./examples/cpp/add_cough.wav) |
| Whisper conversion | Speak the source in a quiet whisper | 0.999998371 | [Python](./examples/python/whisper.wav) / [C++](./examples/cpp/whisper.wav) |
| Speech enhancement | Preserve speakers; remove noise and reverberation | 0.999999994 | [Python](./examples/python/enhance.wav) / [C++](./examples/cpp/enhance.wav) |
| Speech separation | Keep the second speaker to start talking | 0.999999985 | [Python](./examples/python/second_speaker.wav) / [C++](./examples/cpp/second_speaker.wav) |
| Music separation | Keep the singing voice; remove other audio | 0.999999998 | [Python](./examples/python/vocals_only.wav) / [C++](./examples/cpp/vocals_only.wav) |
| Target speaker extraction | Keep the speaker saying "get what" | 0.999999997 | [Python](./examples/python/get_what_speaker.wav) / [C++](./examples/cpp/get_what_speaker.wav) |

The no-TF32 C++ run matched the Python WAVs at waveform cosine 0.999989991 or higher for all 16 tasks; the files were not byte-identical. These historical results use the original combined GGUF and are **not** a 16-task parity claim for the component GGUFs in this package.

## Dtypes and validation scope

All component smoke tests used CUDA and the F32 VAE. A pass here means the listed task loaded the selected GGUFs and generated a WAV; it does not establish Python parity or task quality.

| Generator | Qwen conditioner | Tested task(s) |
| --- | --- | --- |
| Base F32 | BF16 | Zero-shot TTS; instruct TTS |
| Base F16 or Q8_0 | BF16 | Instruct TTS, one run per dtype |
| Base F32 or Q8_0 | Q8_0 | Zero-shot TTS, one run per combination |
| AuK-Flash F32 | BF16 | Zero-shot TTS; instruct TTS |
| AuK-Flash F16 or Q8_0 | BF16 | Instruct TTS, one run per dtype |
| AuK-Flash F32 | Q8_0 | Zero-shot TTS, one run |
| AuK-Flash F16 | Q8_0 | Instruct TTS, one run |

The Base F16 + Qwen Q8_0 and AuK-Flash Q8_0 + Qwen Q8_0 combinations were **not tested**. 
