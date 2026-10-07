---
license: gpl-3.0
language: [en, ne, hi, vi, id, zh]
pipeline_tag: text-to-speech
tags: [text-to-speech, tiny, microcontroller, esp32, wasm, piper, distillation]
library_name: sanotts
---

# sanoTTS — a tiny neural voice that runs anywhere

***sano*** (सानो) — Nepali for **"small."** A family of tiny neural
text-to-speech voices — **294k to 2.27M parameters** — that run with
**no cloud and no NPU**: real-time on a ~$3 ESP32-S3 (out a GPIO into an
LM386 and a speaker), or live in the browser via WASM.

![text in → ESP32 → speech out](https://raw.githubusercontent.com/Ampixa/sanoTTS/master/docs/assets/saanotts-mcu-hero.png)

| | |
| --- | --- |
| Parameter range | **294,279 – 2,272,145** |
| Runs real-time on a $3 microcontroller | ESP32-S3, out a GPIO into an LM386 |
| Runs in the browser | WebAssembly, no server |
| Per-voice footprint | **337 KB to 8.7 MB**, zero dependencies (espeak-ng phonemizer included) |
| Coverage | **11 voices** across **6 languages** — English, Nepali (नेपाली), Hindi (हिन्दी), Vietnamese (Tiếng Việt), Indonesian (Bahasa), Chinese (中文) |
| License | open source, **GPL-3.0** |

**Live demo:** [tts.ampixa.com/sanoTTS](https://tts.ampixa.com/sanoTTS) —
every voice synthesizes your text live in the browser, no server, no upload.

## Download

Both packages stream their weights from **this repo** by default.

```python
import sanotts
sanotts.synthesize("Hello world", voice="heart")     # downloads heart/ from here
```

```js
import { SanoTTS } from 'sanotts-web';               // fetches web/voices/ from here
const tts = await SanoTTS.load();
const result = await tts.synthesize('Hello world', { voice: 'heart' });
```

Python needs `sanotts` >= 0.3.0, the browser `sanotts-web` >= 0.3.0. Both fall
back to the GitHub releases or the Pages host if Hugging Face cannot be
reached, so an outage here cannot break an install. Python packages land in
`~/.cache/sanotts/`; set `SANOTTS_VOICE_SOURCE=hf` or `=github` to pin one
host. In the browser, passing `voiceBase` yourself turns the fallback off, so
a self-hosted deployment never quietly reaches back to our servers.

## Samples

Two clips per voice are in this repo's `samples/` folder; one is embedded
below. "Package here" means this repo carries that voice's weights. The three
languages without one currently ship only through the
[browser demo](https://tts.ampixa.com/sanoTTS) and the GitHub repo's
`web/voices/` — their packages haven't been exported yet.

| Voice | Language | Params | SCOREQ | Package here | Sample |
| --- | --- | ---: | :---: | :---: | --- |
| heart | English 🇺🇸 | 2.27 M | 3.48 | [`heart/`](https://huggingface.co/ampixa/sanoTTS/tree/main/heart) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/english-heart-1.mp3"></audio> |
| hfc | English 🇺🇸 | 1.83 M | 3.94 | [`hfc-en-1p8m/`](https://huggingface.co/ampixa/sanoTTS/tree/main/hfc-en-1p8m) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/english-hfc-1.mp3"></audio> |
| amy | English 🇺🇸 | 1.46 M | **4.13** | [`amy-en-1p46m/`](https://huggingface.co/ampixa/sanoTTS/tree/main/amy-en-1p46m) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/english-amy-1.mp3"></audio> |
| kristin | English 🇺🇸 | 1.40 M | 4.09 | [`kristin-en-1p4m/`](https://huggingface.co/ampixa/sanoTTS/tree/main/kristin-en-1p4m) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/english-kristin-1.mp3"></audio> |
| amy-small | English 🇺🇸 | 1.08 M | 3.70 | [`amy-en-1p1m/`](https://huggingface.co/ampixa/sanoTTS/tree/main/amy-en-1p1m) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/english-amy-small-1.mp3"></audio> |
| robot (on-device, int8) | English 🇺🇸 | 567 k | — | not packaged here (int8 MCU format) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/mcu-567k.mp3"></audio> |
| heart-nano | English 🇺🇸 | 294 k | 2.29 | [`heartnano/`](https://huggingface.co/ampixa/sanoTTS/tree/main/heartnano) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/english-heart-nano-1.mp3"></audio> |
| Indonesian | Bahasa | 1.46 M | — | [`id-newstts-1p46m/`](https://huggingface.co/ampixa/sanoTTS/tree/main/id-newstts-1p46m) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/indonesian-1.mp3"></audio> |
| Vietnamese | Tiếng Việt | 1.46 M | — | [`vi-vais1000-1p46m/`](https://huggingface.co/ampixa/sanoTTS/tree/main/vi-vais1000-1p46m) | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/vietnamese-1.mp3"></audio> |
| Nepali | नेपाली | 1.47 M | — | not exported yet — see `web/voices/nepali/` in the GitHub repo | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/nepali-1.mp3"></audio> |
| Hindi | हिन्दी | 1.50 M | — | not exported yet — see `web/voices/hindi/` in the GitHub repo | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/hindi-1.mp3"></audio> |
| Chinese | 中文 | 1.50 M | — | not exported yet — see `web/voices/chinese/` in the GitHub repo | <audio controls src="https://huggingface.co/ampixa/sanoTTS/resolve/main/samples/chinese-1.mp3"></audio> |

SCOREQ is a no-reference naturalness predictor, higher is better; it is only
reported for the English voices, which share one 24-sentence eval set. The
other languages haven't been scored against a comparable reference yet.

**Size does not order this table, and we are not going to pretend it does.**
`amy` at 1.46M scores higher than `heart` at 2.27M because they come from
different teachers and different architectures, not because one is bigger.
`amy` and the voices above it are the **piperlite** lineage, distilled from a
Piper/VITS teacher at 22.05 kHz. `heart` and `heart-nano` are the newer
**nano** lineage — 24 kHz, mel-100 → ConvNeXt1D → iSTFT, distilled from a
Kokoro teacher through a frozen Vocos — which is the one that quantizes to
int8 and runs on a microcontroller. The two are not interchangeable and the
`sanotts` package picks the right runtime for you.

The `heart` and `heart-nano` scores were re-measured on 2026-09-04; the eval
set, checkpoint hashes, exact commands and all 24 per-clip scores are in
[`evidence/heart-diverse24-remeasure-20260904.json`](https://huggingface.co/ampixa/sanoTTS/blob/main/evidence/heart-diverse24-remeasure-20260904.json).
They were scored on the float32 reference render. The shipped `heart-nano`
int8 export tracks that render at 0.981 waveform correlation, and `heart`
ships as float32 because its int8 export reached only 0.951 against a 0.98
gate.

The "robot" row is the 567,008-parameter model that runs on the ESP32-S3.

## Install & use

| Platform | Install | Then |
| --- | --- | --- |
| Python | `pip install sanotts` | `sanotts say "Hello" --voice heart -o hello.wav` |
| Web (npm) | `npm install sanotts-web` | `const tts = await SanoTTS.load(); await tts.synthesize('Hello', {voice:'heart'})` |
| Web (no build) | copy `dist/` + `voices/` | see [Deploy on your own site](https://github.com/Ampixa/sanoTTS#deploy-on-your-own-site) in the GitHub README |
| Arduino / PlatformIO | zip-install or `lib_deps = https://github.com/Ampixa/sanoTTS.git` | [`arduino/README.md`](https://github.com/Ampixa/sanoTTS/blob/master/arduino/README.md) |
| Hugging Face | this repo | the voice packages above, downloaded for you by `pip install sanotts` |
| Browser | nothing | [tts.ampixa.com/sanoTTS](https://tts.ampixa.com/sanoTTS) |

Pip voices: `heart`, `hfc`, `amy-1p8m`, `amy`, `kristin`, `vi`, `id`,
`amy-1p1m`, `heart-nano`. Pure numpy inference, no torch, no onnxruntime.

## How it stacks up

Open small-scale TTS on an honest gate — a diverse 24-sentence set scored
with the **same** no-reference suite (SCOREQ / UTMOS are naturalness
predictors, DNSMOS-SIG is signal quality; higher is better). Parameter
counts are inference-time and exclude the shared external G2P.

| System | Params | SCOREQ | UTMOS | DNS-SIG |
| --- | ---: | :---: | :---: | :---: |
| **sanoTTS (amy)** | **1.46 M** | **4.13** | **4.10** | 3.61 |
| TinyTTS | 1.62 M | 3.94 | 3.65 | **3.62** |
| Inflect Nano | 4.63 M | 3.81 | 3.65 | 3.58 |
| Kitten TTS nano | 15 M | 3.02 | 3.58 | 3.43 |
| _Piper (our teacher)_ | _~15 M_ | _4.71_ | _4.47_ | _3.65_ |
| _Kokoro_ | _82 M_ | _4.89_ | _4.52_ | _3.69_ |

sanoTTS is the **smallest** model here and the **best on naturalness
(SCOREQ and UTMOS) among everything up to 15M params** — beating TinyTTS
while being smaller. On DNSMOS-SIG, TinyTTS edges us by 0.01 — no single
metric tells the whole story. It's the only one that runs a full neural
stack on a $3 MCU. The frontier only pulls ahead at Piper, the ~15M teacher
we distilled from, and Kokoro (82M, 56× larger) — a gap we don't claim to
close. Reproduce it with `tools/eval_mos_all.py` + `tools/eval_scorecard.py`
in the GitHub repo.

Shipped-file sizes: sanoTTS amy 2.8 MB fp16 and TinyTTS 3.5 MB fp16, both
verified from the released files; Kokoro's ~330 MB fp32 is its widely cited
public figure.

## How it works

![text → duration → acoustic → decoder → audio](https://raw.githubusercontent.com/Ampixa/sanoTTS/master/docs/assets/saanotts-signal-path.png)

espeak-ng provides phoneme IDs; a duration model predicts timing; an
acoustic model predicts generator latents; a decoder renders audio. The
piperlite voices (amy, kristin, hfc, and the other languages) use a compact
time-domain decoder running in fp32 at 22.05 kHz. The nano voices (heart,
heart-nano) and the 567,008-parameter on-device model use an iSTFT decoder
at 24 kHz, quantized to int8 where it has to fit and run in real time on the
ESP32-S3. Models are distilled from a Piper/VITS or Kokoro teacher — see
[`docs/distillation-recipe.md`](https://github.com/Ampixa/sanoTTS/blob/master/docs/distillation-recipe.md)
in the GitHub repo for the full recipe.

## Deploy

- **ESP32-S3 talking device** — a standalone WiFi dashboard: type text, the
  board phonemizes (on-chip espeak-ng) and speaks. See
  [`mcu/ports/esp32s3/`](https://github.com/Ampixa/sanoTTS/tree/master/mcu/ports/esp32s3).
  Board-by-board measurements are in
  [`BOARDS.md`](https://github.com/Ampixa/sanoTTS/blob/master/BOARDS.md); the
  silicon figures there are for the `en_us_e12nano` lineage, which is a
  sibling of `heart-nano`, not the same weights.
- **Browser** — the full stack in WASM, no server. **[▶ Hear and synthesize
  all 11 voices live](https://tts.ampixa.com/sanoTTS)**; source in
  [`web/`](https://github.com/Ampixa/sanoTTS/tree/master/web).
- **Other MCUs** — which chips can run it and how well:
  [`docs/mcu-classes-and-porting.md`](https://github.com/Ampixa/sanoTTS/blob/master/docs/mcu-classes-and-porting.md).

## Links

- Source, recipes, eval tooling: [github.com/Ampixa/sanoTTS](https://github.com/Ampixa/sanoTTS)
- Live browser demo: [tts.ampixa.com/sanoTTS](https://tts.ampixa.com/sanoTTS)
- npm package: [sanotts-web](https://www.npmjs.com/package/sanotts-web)
- PyPI package: [sanotts](https://pypi.org/project/sanotts/)

## License

GPLv3 — see [`LICENSE`](https://github.com/Ampixa/sanoTTS/blob/master/LICENSE).
The pipeline builds on GPLv3 components (notably
[espeak-ng](https://github.com/espeak-ng/espeak-ng) for G2P, and
[piper](https://github.com/OHF-Voice/piper1-gpl)), so the project as a
whole is GPLv3.

Copyright (C) 2026 Ampixa.

## Files here

Two package layouts, because there are two graphs.

**piperlite** (`amy-en-1p46m/`, `kristin-en-1p4m/`, `hfc-en-1p8m/`,
`amy-en-1p1m/`, `id-newstts-1p46m/`, `vi-vais1000-1p46m/`) — a flat fp16
blob addressed by manifest offsets:

```
manifest.json                 weights.fp16.bin
piper-phoneme-config.json     (+ sibilant-injection calibration where applicable)
```

**nano** (`heart/`, `heartnano/`) — the mel-100 stack, two blobs plus the
generated offset header:

```
meta.json          lineage, per-file sha256, sample rate, vocab
front_*.bin        duration + acoustic
model_*.bin        decoder
nano_q8_meta.h     tensor offsets
```

`heartnano/` ships `*_q8.bin` (int8, 345,232 bytes total); `heart/` ships
`*_f32.bin` (float32, 9,137,920 bytes) because its int8 export missed the
fidelity gate. Both layouts are consumed by the `sanotts` Python package and
the portable C runtime.

**`web/voices/`** is a third thing and exists for the browser. The piperlite
voices ship there as `front_f32.bin` + `dec_f32.bin`, a different artifact
from the `weights.fp16.bin` the Python package reads, which is why the same
voice appears twice in this repo under two names. It mirrors `web/` in the
GitHub repo byte for byte and is what `sanotts-web` fetches. The nano voices
are not duplicated: `web/voices/heart/` and `heart/` hold the same blobs.

`samples/` holds the audio clips embedded above (mp3, one or two per voice,
plus the on-device `mcu-567k.mp3`), and `evidence/` the eval report behind the
heart scores.
