---
license: mit
language:
  - vi
library_name: onnx
pipeline_tag: text-to-speech
tags:
  - text-to-speech
  - tts
  - vietnamese
  - onnx
  - onnxruntime
  - zero-shot
  - speech-synthesis
  - voice-cloning
  - vietnamese-tts
  - tieng-viet
metrics:
  - wer
model-index:
  - name: ZeroTTS
    results:
      - task:
          type: text-to-speech
          name: Zero-Shot Text-to-Speech
        dataset:
          type: zeroweight-ai/ZeroBench-TTS
          name: ZeroBench-TTS
          split: test
        metrics:
          - type: wer
            value: 1.03
            name: WER (%) — raw text
          - type: utmos
            value: 2.91
            name: UTMOSv2 naturalness MOS
          - type: speaker_similarity
            value: 0.936
            name: Speaker similarity (WavLM-SV cosine)
          - type: excess_silence
            value: 0.029
            name: Excess silence (s)
      - task:
          type: text-to-speech
          name: Zero-Shot TTS — monolingual Vietnamese
        dataset:
          type: zeroweight-ai/ZeroBench-TTS
          name: ZeroBench-TTS (vietnamese)
          config: vietnamese
          split: test
        metrics:
          - type: wer
            value: 0.16
            name: WER (%) — raw text
      - task:
          type: text-to-speech
          name: Zero-Shot TTS — Vietnamese/English code-switching
        dataset:
          type: zeroweight-ai/ZeroBench-TTS
          name: ZeroBench-TTS (code_switch)
          config: code_switch
          split: test
        metrics:
          - type: wer
            value: 0.97
            name: WER (%) — raw text
      - task:
          type: text-to-speech
          name: Zero-Shot TTS — cross-lingual voice prompt
        dataset:
          type: zeroweight-ai/ZeroBench-TTS
          name: ZeroBench-TTS (cross_lingual)
          config: cross_lingual
          split: test
        metrics:
          - type: wer
            value: 1.42
            name: WER (%) — raw text
      - task:
          type: text-to-speech
          name: Zero-Shot TTS — acronyms, dates, numbers
        dataset:
          type: zeroweight-ai/ZeroBench-TTS
          name: ZeroBench-TTS (challenging)
          config: challenging
          split: test
        metrics:
          - type: wer
            value: 1.75
            name: WER (%) — raw text
---

<img src="banner.png" alt="ZeroTTS — Vietnamese zero-shot text-to-speech" width="100%">

# ZeroTTS

### Vietnamese Zero-Shot Text-to-Speech (TTS) with real-time streaming and voice cloning from seconds of audio. Fast, natural, and optimised for CPU inference.

**The most accurate open Vietnamese TTS we know of — 4× fewer word errors than
the next best model**, and it runs faster than real time on a laptop CPU.

* 🎯 **Ultra-natural** — 2.91 UTMOS above every other open Vietnamese
  system, with near-zero dead air (0.029 s).
* 🗣️ **Zero-shot voice cloning** — a voice is a small latent array; drop it in
  and the model speaks in it, cloned from as little as 3 seconds of reference
  audio (up to 30 seconds). No fine-tuning, no per-speaker training.
* ⚡ **Real-time on CPU, streaming** — ~2× faster than real time (RTF 0.5×),
  first audio chunk in ~70 ms. No GPU required.
* 🇻🇳 **Built for Vietnamese** — tones, code-switched English, and 
  reads `31/12/2025` and `ZeroTTS` without text normalizer.

* Code, examples, browser demo: **https://github.com/zeroweight-ai/ZeroTTS**
* Benchmark dataset: **https://huggingface.co/datasets/zeroweight-ai/ZeroBench-TTS**
* Blogpost: **https://zeroweight.ai/blog/zero-tts**

## Samples

**Two-speaker conversation**

<audio controls><source src="https://huggingface.co/zeroweight-ai/ZeroTTS/resolve/main/samples/conversation.mp3" type="audio/mpeg"></audio>

**Long-form narration**

<audio controls><source src="https://huggingface.co/zeroweight-ai/ZeroTTS/resolve/main/samples/storytelling.mp3" type="audio/mpeg"></audio>

**News read, code-switched English**

<audio controls><source src="https://huggingface.co/zeroweight-ai/ZeroTTS/resolve/main/samples/news-code-switch.mp3" type="audio/mpeg"></audio>

**Cross-lingual**

Reference audio (Vietnamese) 

<audio controls><source src="https://huggingface.co/zeroweight-ai/ZeroTTS/resolve/main/samples/cross-lingual-reference-vi.mp3" type="audio/mpeg"></audio>

Output (English) 

<audio controls><source src="https://huggingface.co/zeroweight-ai/ZeroTTS/resolve/main/samples/cross-lingual-english.mp3" type="audio/mpeg"></audio>

## Usage
```python
pip install zerotts
```

```python
from zerotts import ZeroTTS

tts = ZeroTTS.from_pretrained("zeroweight-ai/ZeroTTS")
audio = tts.synthesize("Xin chào các bạn, mình là ZeroTTS.", voice="maichi")
tts.save_audio(audio, "out.wav")
```

Streaming, with first audio in roughly 70 ms:

```python
import queue

import numpy as np
import sounddevice as sd   # pip install sounddevice

TEXT = ("Đây là chế độ phát trực tuyến. Âm thanh được tạo ra và phát ngay lập tức, "
        "không cần chờ toàn bộ đoạn văn hoàn thành. Nhờ vậy, người nghe chỉ mất "
        "khoảng 70 mili giây là đã nghe thấy câu đầu tiên, ngay cả khi mô "
        "hình đang chạy trên CPU của một chiếc laptop bình thường.")

pending, tail = queue.Queue(), np.zeros(0, dtype="float32")

def feed(outdata, frames, _time, _status):
    global tail
    while len(tail) < frames and not pending.empty():
        tail = np.concatenate([tail, pending.get_nowait()])
    n = min(frames, len(tail))
    outdata[:n, 0] = tail[:n]
    outdata[n:] = 0
    tail = tail[n:]

with sd.OutputStream(samplerate=tts.sample_rate, channels=1,
                     dtype="float32", callback=feed):
    for chunk in tts.synthesize_stream(TEXT, voice="maichi"):
        pending.put(chunk.reshape(-1))   # chunk is (1, n) float32 at 48 kHz
    while not pending.empty() or len(tail):
        sd.sleep(50)                     # let the buffer drain before closing
```

## Benchmarks

Measured on **[ZeroBench-TTS](https://huggingface.co/datasets/zeroweight-ai/ZeroBench-TTS)**

Every system reads **raw text** — dates, numbers and acronyms verbatim, exactly
as they appear in the wild, with no text frontend in front of the model. 

| | **ZeroTTS** | OmniVoice | XTTS-v2-vietnamse | viXTTS |
|---|:-:|:-:|:-:|:-:|
| **WER** ↓ | **1.03 %** | 4.13 % | 16.42 % | 18.40 % |
| **Naturalness** (UTMOS) ↑ | **2.91** | 2.76 | 2.43 | 2.35 |
| **Voice similarity** (SSIM) ↑ | 0.936 | **0.950** | 0.940 | 0.935 |
| **Dead air** (excess silence) ↓ | **0.029 s** | 0.340 s | 0.532 s | 0.233 s |
| **RTF, CPU** ↓ | **0.50×** | 6.12× | 0.71× | 0.73× |
| **Time to first audio, CPU** ↓ | **~70 ms** | ~34 s | ~6.1 s | ~5.1 s |
| **Parameters**  ↓ | **202 M** | 775 M | 467 M | 467 M |

**4× fewer word errors than the next-best system**, and the fastest of the four
on CPU. The gap is much wider in latency than in throughput: the two XTTS
fine-tunes also beat real time (0.71×) but need seconds to emit their first
sample, while OmniVoice is 6× *slower* than real time. All three are sized and
tuned for a GPU, and it shows.

Full comparison tables, per-subset breakdowns, and CPU speed methodology:
**[docs/BENCHMARKS.md](https://github.com/zeroweight-ai/ZeroTTS/blob/main/docs/BENCHMARKS.md)**

### Speed — CPU

RTF (realtime factor, wall-clock synthesis time ÷ output audio duration — lower
is faster; below 1× is faster than real time) and time-to-first-audio, all
measured **on CPU**, single request, 8 inference threads pinned to a dedicated
core pool (no other synthesis running concurrently). Three Vietnamese samples —
short (26 chars), medium (77 chars), long (227 chars) — each run 6 times with
the first 2 (cold-cache) discarded; figures below are the mean of the
remaining 4.

| | **ZeroTTS** | OmniVoice | XTTS-v2-vietnamse | viXTTS |
|---|:-:|:-:|:-:|:-:|
| RTF — short | **0.51×** | 10.87× | 0.70× | 0.71× |
| RTF — medium | **0.47×** | 4.82× | 0.70× | 0.70× |
| RTF — long | **0.53×** | 2.67× | 0.71× | 0.78× |
| TTFA — short | **53 ms** | 21.7 s | 4.02 s | 2.45 s |
| TTFA — medium | **66 ms** | 28.9 s | 4.02 s | 3.72 s |
| TTFA — long | **89 ms** | 52.3 s | 10.3 s | 9.22 s |

ZeroTTS's time-to-first-audio comes from its real streaming path — first audio frame,
not first full utterance. The three baselines have no working CPU streaming
path, so their TTFA is the time to the complete utterance. 

## Voices, and voice cloning

A voice is a small array of speaker latents, `(1, n_voice_queries, d_model)`,
shipped as a `.npz` under `voices/`. That array is the entire speaker
conditioning — no reference transcript, no audio prompt.

> **Voice cloning is not available in this release.** Those latents come from a
> voice encoder that reads a reference clip, and that encoder is not published.
> This repository ships ready-to-use voices; it cannot create new ones from
> audio.
>
> To get latents for your own speaker, see **[zeroweight.ai](https://zeroweight.ai)**
> or get in touch.

Because a voice is just an array, latents obtained that way drop into
`voices/<name>/voice.npz` and work with no code change.

## Intended use and limitations

Built for **Vietnamese**. It handles English words embedded in Vietnamese text
(`code_switch`), but it is not an English TTS system and is not evaluated as one.

Do not use it to impersonate a real person, to generate speech attributed to
someone without their consent, or to produce audio intended to deceive. The
shipped voices are for evaluation and demos.

Synthetic speech should be disclosed as synthetic wherever a listener might
reasonably assume otherwise.

## Credits

Speech codec: **MOSS-Audio-Tokenizer-Nano** by the OpenMOSS team, Apache-2.0.
Its ONNX **decoder** graphs are redistributed under `onnx/codec/` so ZeroTTS has
no external runtime dependency; the encoder is not included. See
`onnx/codec/LICENSE-Apache-2.0.txt`.

```bibtex
@misc{gong2026mossaudiotokenizerscalingaudiotokenizers,
  title={MOSS-Audio-Tokenizer: Scaling Audio Tokenizers for Future Audio Foundation Models},
  author={Yitian Gong and Kuangwei Chen and Zhaoye Fei and Xiaogui Yang and Ke Chen
          and Yang Wang and Kexin Huang and Mingshu Chen and Ruixiao Li
          and Qingyuan Cheng and Shimin Li and Xipeng Qiu},
  year={2026}, eprint={2602.10934}, archivePrefix={arXiv}, primaryClass={cs.SD}
}
```

## License

ZeroTTS weights and code: **MIT**.

The ZeroBench-TTS *dataset* is CC-BY-NC-4.0 because it redistributes reference
audio from VIVOS, viVoice, phoaudiobook and Emilia. That license applies to the
benchmark dataset only — **not** to these weights.
