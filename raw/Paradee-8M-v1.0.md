---
base_model: hexgrad/Kokoro-82M
language:
- en
library_name: onnx
license: apache-2.0
pipeline_tag: text-to-speech
tags:
- text-to-speech
- tts
- onnx
- distillation
- kokoro
---

# Paradee-8M v1.0

Paradee is a small English text-to-speech model. It has 8.07M parameters and is distilled from
[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), and it speaks one voice, Kokoro's `af_heart`.

- **Small.** The int8 model is one 9 MB ONNX file, against 325 MB for Kokoro.
- **Fast.** It runs about 18x faster than real time on one CPU thread, with no GPU.
- **Close to its teacher.** It scores 4.41 on UTMOS (Kokoro: 4.52) and has the same word error rate (5.7%).

**Paper:** [Paradee: Distilling Kokoro-82M into an 8M-Parameter Single-Voice Text-to-Speech Model](https://huggingface.co/papers/2610.06817)

**Code, training and the Python package:** [github.com/sahilmahendrakar/paradee](https://github.com/sahilmahendrakar/paradee)

## Samples

Five held-out sentences, read by Paradee and by its teacher. The sentences are in
[`samples/sentences.txt`](samples/sentences.txt).

| # | Paradee | Kokoro-82M (teacher) |
|---|---|---|
| 1 | [listen](samples/1_paradee.wav) | [listen](samples/1_kokoro.wav) |
| 2 | [listen](samples/2_paradee.wav) | [listen](samples/2_kokoro.wav) |
| 3 | [listen](samples/3_paradee.wav) | [listen](samples/3_kokoro.wav) |
| 4 | [listen](samples/4_paradee.wav) | [listen](samples/4_kokoro.wav) |
| 5 | [listen](samples/5_paradee.wav) | [listen](samples/5_kokoro.wav) |

## Usage

```bash
pip install git+https://github.com/sahilmahendrakar/paradee
python -m paradee "Paradee is a small voice that runs anywhere." -o hello.wav
```

```python
from paradee import Paradee, SAMPLE_RATE
import soundfile as sf

tts = Paradee()
sf.write("hello.wav", tts("Paradee is a small voice that runs anywhere."), SAMPLE_RATE)
```

## Files

| File | What it is |
|---|---|
| `onnx/paradee_int8.onnx` | The whole model in one graph, weights in int8 (9.0 MB). Use this one. |
| `onnx/paradee.onnx` | The same graph in fp32 (37 MB). It sounds the same. |
| `config.json` | Kokoro's phoneme vocabulary and the sample rate |
| `tokenizer.json` | The same vocabulary in the format transformers.js and kokoro-js load |
| `pytorch/text_side.pt`, `pytorch/decoder.pt` | PyTorch weights for the two halves, for the training code on GitHub |
| `samples/` | The audio above |

The ONNX graph goes from phoneme ids to audio. It includes the phase-locking filter described below.

- **Inputs:** `input_ids`, int64 `[1, T]`, phoneme ids from `config.json` with a `0` pad token at
  each end, at most 512 in total. The second input is `speed`, float32 `[1]`, where 1.0 is normal speed.
- **Output:** `waveform`, float32 `[1, samples]` at 24 kHz.

Phonemes must be written the way [misaki](https://github.com/hexgrad/misaki), Kokoro's own
grapheme-to-phoneme library, writes them, because that is all Paradee saw in training. In the
browser, kokoro-js phonemizes with eSpeak NG instead. There,
[`web/misaki.js`](https://github.com/sahilmahendrakar/paradee/blob/main/web/misaki.js) converts
eSpeak's spelling to misaki's. Without it, Whisper mishears about 31% of words, and with it about 2%.

## Results

All numbers are on 200 held-out sentences. Speed is on one CPU thread of an Apple M4 Pro.

| Model (voice) | Params | File size | Speed | UTMOS | WER |
|---|---:|---:|---:|---:|---:|
| Kokoro-82M, teacher (af_heart) | 81.8M | 325 MB | 7.6x | 4.52 | 5.7% |
| **Paradee (af_heart)** | **8.07M** | **8.45 MB** | **25.0x** | **4.41** | **5.7%** |
| Kokoro-7M-Distill (af_msa) | 7.48M | 30.1 MB | 35.5x | 4.18 | 7.4% |
| Piper, en_US-lessac-medium | 15.7M | 63.2 MB | 15.4x | 4.36 | 8.8% |
| KittenTTS nano 0.8 (Bella) | 14.0M | 56.8 MB | 10.7x | 4.01 | 5.5% |

UTMOS is a neural network trained on human ratings. It predicts how natural a clip sounds, on a
scale from 1 to 5. WER is the share of words that Whisper (base) transcribes wrongly.

The table is from the paper and measures PyTorch. The released `paradee_int8.onnx` scores UTMOS
4.41 on the same sentences and runs about 18x faster than real time in onnxruntime on one thread.

### Hugging Face Open TTS Leaderboard

As of **October 9, 2026**, on Hugging Face's [Open TTS Leaderboard](https://huggingface.co/spaces/hf-audio/open_tts_leaderboard) — which scores open-source TTS models on [Seed TTS Eval](https://github.com/BytedanceSpeech/seed-tts-eval) and [CV3 Eval](https://github.com/QwenAudio/CV3-Eval) — Paradee-8M-v1.0 ranks:

- 🥈 **2nd on English WER** (1.47%), behind only its own teacher, Kokoro-82M (1.46%).
- On the **Pareto front for model size vs. WER** — no model of comparable size scores a lower WER.
- In the 🗣️ **CPU streaming** benchmark (batch size 1, single CPU thread): **1st on RTFx** (11.48, i.e. ~11.5x faster than real-time) and **4th on time-to-first-audio** (390 ms median).

<p align="center">
  <img width="90%" alt="Top 10 models by English WER" src="https://huggingface.co/datasets/bezzam/tts_leaderboard_screenshots/resolve/main/paradee/top_models_wer_en.png" />
</p>

<p align="center">
  <img width="90%" alt="Model size vs. WER, with Pareto front" src="https://huggingface.co/datasets/bezzam/tts_leaderboard_screenshots/resolve/main/paradee/pareto_size_wer.png" />
</p>

<p align="center">
  <img width="90%" alt="Top 8 models by CPU-streaming RTFx" src="https://huggingface.co/datasets/bezzam/tts_leaderboard_screenshots/resolve/main/paradee/top_models_rtfx_cpu.png" />
</p>

<p align="center">
  <img width="90%" alt="Top 8 models by CPU-streaming TTFA" src="https://huggingface.co/datasets/bezzam/tts_leaderboard_screenshots/resolve/main/paradee/top_models_ttfa_cpu.png" />
</p>

## How it was made

Paradee is Kokoro's own code at smaller widths: a 4.23M text side and a 3.85M decoder. The two
halves were trained separately against the frozen teacher, on 12,000 WikiText-103 sentences
(23.9 hours) read by Kokoro.

1. The text side learns to predict the teacher's phoneme durations, pitch, loudness and phoneme
   features.
2. The decoder learns to turn the teacher's saved values into the teacher's audio, first with
   spectrogram losses and then with adversarial training.
3. The halves are joined with no further training.
4. A filter with no parameters corrects the phase of voiced sound between 2 and 8 kHz. Phase is
   the timing of each frequency's wave. This removes a slight buzz that the small decoder
   otherwise leaves.

All training ran on one MacBook Pro.

## Limitations

- English only, with American pronunciation, and one voice.
- Numbers, abbreviations and unusual words are pronounced only as well as misaki handles them.
- A faint buzz can still be heard on some voiced sounds, though much less than without the filter.

## License

Apache 2.0, the same as Kokoro-82M.

## Citation

```bibtex
@misc{mahendrakar2026paradee,
  title  = {Paradee: Distilling Kokoro-82M into an 8M-Parameter Single-Voice Text-to-Speech Model},
  author = {Mahendrakar, Sahil},
  year   = {2026},
  url    = {https://huggingface.co/sahilmahendrakar/Paradee-8M-v1.0}
}
```