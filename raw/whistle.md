---
library_name: cactus-needle
pipeline_tag: automatic-speech-recognition
license: apache-2.0
language:
  - en
  - de
  - fr
  - es
  - it
  - nl
  - pl
tags:
  - speech-recognition
  - speech-to-text
  - on-device
  - edge
  - quantization
  - webassembly
---

![Cactus Whistle](assets/whistle-banner.svg)

A speech-to-text model for mobiles, wearables, robots, smart home, automotive and microcontrollers. The whole model is a single 16.9 MB file, and it runs on the same CPU engine as [Needle](https://huggingface.co/Cactus-Compute/needle3), from the same container and the same quantisation, with no dependencies and no GPU.

Whistle does three jobs, all of them on the device:

- **Transcription**: 16 kHz mono audio, up to 30 seconds in one pass, in English, German, French, Spanish, Italian, Dutch and Polish. The language is detected unless you name it, and silence returns an empty transcript rather than an invented sentence.
- **Word timestamps**: every word with its start, end and probability, aligned from the decoder's own attention, so an app can highlight, seek or cut on a word.
- **Speech embedding**: the encoder output, one row per 80 ms frame, for matching and retrieval without decoding a transcript at all.

Keyword biasing takes the names, places and product words your users actually say and favours them during the search, so the ones that matter survive.

## Model

![Whistle at a glance](assets/whistle-model.svg)

Whistle is a log-mel front end and a convolutional stem feeding an audio encoder, read by a Needle-shaped decoder through gated cross attention at every layer. It reuses Needle's `.cact` container, Cactus Quants, SIMD kernels and KV cache, so a device that already runs Needle runs Whistle in the same binary with no second runtime. The decoder is laddered the way Needle's is: every depth from 2 layers up is a deployable model, picked at load time with `--audio-depth`. This repo holds `whistle.cact`; the engine and its platform folders are in [Cactus-Compute/needle3](https://huggingface.co/Cactus-Compute/needle3).

## Benchmarks

Word error rate on the full test splits, scored with the Whisper normalizers. Whisper and Moonshine figures are the ones their authors published.

![Whistle against Whisper and Moonshine](assets/whistle-benchmarks.svg)

- **Speed**: 10 s of audio on an Apple M4 Pro, each model on its official runtime at its defaults: Whistle's C++ engine at 5 beams, `openai-whisper`, and `moonshine-voice` non-streaming over whole audio. Time to first token is audio in to first token. Decode is tokens divided by the wall time after it, so the encoder is not counted twice.
- **Precision**: Whistle 2 to 4 bit, Whisper fp32 in memory on the CPU, Moonshine int8.
- **WER**: Whistle measured over 86,174 utterances. Whisper and Moonshine as published (Whisper paper Tables 9, 10 and 13, Moonshine paper Table 3). The Whisper row is the multilingual checkpoint, not `base.en`.
- **A missing bar** means that model's authors never published that benchmark. Moonshine is English only; Whisper reports no SPGISpeech, Earnings-22 or AMI cleaned.
- **AMI** includes empty references, per the Open ASR Leaderboard convention. Whisper's figure is AMI-IHM. **TED-LIUM** excludes the corpus's `ignore_time_segment_in_scoring` regions, as its scoring protocol specifies.
- **FLEURS and MLS** are averaged over Whistle's seven languages (MLS over six, no English), the same set for every model.
- **No test audio appears in Whistle's training or validation data**, verified by comparing audio checksums and speaker IDs across every reported test set.

## Get started

```sh
pip install cactus-needle
```

The Python package and the source are on [GitHub](https://github.com/cactus-compute/needle). A 16 kHz WAV or raw samples need nothing beyond the base install; other sample rates and microphone capture need the `[mic]` extra.

```python
import needle

print(needle.transcribe("clip.wav")["text"])
# turn off the kitchen lights
```

Every call returns the text, the language, the milliseconds to the first token and the decoder's tokens per second after it. `word_timestamps=True` adds each word with its start, end and probability, `keywords=[...]` favours the names your users say, and `language="de"` forces the language instead of detecting it. The engine and the weights are fetched once and cached. `needle.Whistle()` is the same model as an object, for `embed(audio)` or to hold one tuned `.cact`. `needle whistle playground` transcribes from the microphone, and `needle whistle compare` puts Whistle next to Whisper and Moonshine on the same clip.

## With Needle

![One engine, three ways to load it](assets/whistle.svg)

One engine runs both models. `needle_load` reads whichever model a `.cact` carries, so the same binary transcribes on its own, answers text on its own, or does both at once: it transcribes the clip, answers the transcript against your tools, and returns one JSON object with the tool calls and the speech fields, the speech ones prefixed `audio_`. The transcription stays inside the engine, so audio in and tool calls out is one call.

```sh
needle --model whistle.cact --audio clip.wav

needle --model needle3.cact --model whistle.cact --tools tools.json --audio clip.wav
```

## Deploy

The engine and its platform folders live in [Cactus-Compute/needle3](https://huggingface.co/Cactus-Compute/needle3); every folder holds a `needle` binary, `libneedle.a` and `needle.h`, and loads any `.cact` you hand it, this model or Needle or both.

![One engine per platform folder](assets/deploy.svg)

```sh
needle download macos-arm64
needle download whistle
./macos-arm64/needle --model whistle.cact --audio clip.wav --audio-word-timestamps
```

`needle_load`, `needle_transcribe` and `needle_embed` are the whole speech C API, declared in `needle.h` beside Needle's own, and `needle_complete` takes the clip directly and does the transcription for you. The engine reads no environment variables: every behaviour is a compiled default or an explicit flag, so every run of the same blob scores the same.

The [devices guide](https://cactuscompute.com/blog/needle-supported-devices) covers the runner flags, the C API, the WASI component and air-gapped setup.

## Citation

Whistle is built by the Cactus Compute team. If you use it in your work, please cite:

```bibtex
@misc{whistle_2026,
  title        = {Whistle: Speech Recognition for Tiny Devices},
  author       = {Mroz, Jakub and Ndubuaku, Henry and Mosoyan, Karen and Cylich, Noah and
                  Kumar, Satyajit and Sandhu, Parkirat and Shemet, Roman and Lee, Justin H.},
  year         = {2026},
  organization = {Cactus Compute, Inc.},
  howpublished = {\url{https://github.com/cactus-compute/needle}}
}
```

Reach out on founders@cactuscompute.com for partnerships, collaborations, synergies and deploying Whistle in your product.
