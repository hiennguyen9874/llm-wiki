---
license: apache-2.0
datasets:
- pnnbao-ump/VieNeu-TTS-10k-ENVI
language:
- vi
- en
pipeline_tag: text-to-speech
tags:
- voice-cloning
- code-switching
- podcast
- emotion-control
- 48khz
---

# 🦜 VieNeu-TTS v3 Turbo

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/pnnbao97/VieNeu-TTS)
[![Model](https://img.shields.io/badge/Hugging%20Face-Model-yellow)](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo)
[![PyPI](https://img.shields.io/badge/PyPI-vieneu%203.7.1-blue?logo=pypi&logoColor=white)](https://pypi.org/project/vieneu/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-5865F2?logo=discord&logoColor=white)](https://discord.gg/yJt8kzjzWZ)

## Overview

<video controls src="https://cdn-uploads.huggingface.co/production/uploads/68b923a86c86c127a1975eda/paPqSDpwFGrKtIZrqaEg4.mp4" width="100%"></video>

**VieNeu-TTS v3 Turbo** is the next generation of Vietnamese TTS — **48 kHz** high-fidelity speech, **23 built-in preset voices** across three regions (North / Central / South), **instant voice cloning**, **real-time streaming** with an **OpenAI-compatible API** (16 concurrent streams on one RTX 3060), inline **emotion cues**, and seamless **bilingual (En–Vi) code-switching**.

The reference implementation is the **`vieneu` Python SDK (v3.7.1)**. Its minimal install is **torch-free**: on CPU everything runs on **ONNX Runtime** (PyTorch is never imported), and on a CUDA machine it auto-switches to the PyTorch engine with **automatic batching** and a **continuous-batching stream scheduler** — same API, no code change.

> [!IMPORTANT]
> **What's new in SDK v3.7:**
> - **GPU streaming with continuous batching** — `infer_stream` on CUDA runs on one CUDA graph shared by every caller: first audio in **~115 ms**, **16 concurrent streams under 200 ms** on a single RTX 3060 (32 max).
> - **OpenAI-compatible streaming API + Docker** — `POST /v1/audio/speech` (`pcm`/`wav`, chunked or SSE) works with the OpenAI SDK, Pipecat, LiveKit; `docker compose --profile api-gpu` / `api-cpu`. Numbers, sizing and CPU-only notes: [docs/streaming.md](https://github.com/pnnbao97/VieNeu-TTS/blob/main/docs/streaming.md).
> - **23 preset voices** covering North / Central / South, both genders and several reading characters (default: `Minh Quân`).
> - **LoRA fine-tuning** of v3 Turbo on one consumer GPU.
> - Since 3.3: torch-free voice cloning on CPU, optional **int8** CPU backbone (`Vieneu(precision="int8")`, ~2× faster; fp32 is the default), sliding-window repetition penalty.

## 🏗️ Architecture & Credits

The **VieNeu-TTS v3 Turbo architecture is an original design by the author, Phạm Nguyễn Ngọc Bảo**, and is **trained from scratch** on ~10,000 hours of English–Vietnamese speech — it is **not** a fine-tune, distillation, or adaptation of any existing TTS model.

- **Model architecture & training:** designed and trained from scratch by **Phạm Nguyễn Ngọc Bảo** — https://github.com/pnnbao97
- **Audio codec:** [MOSS-Audio-Tokenizer-Nano](https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano) (OpenMOSS-Team) — 48 kHz neural audio codec.
- **Phonemizer:** [sea-g2p](https://github.com/pnnbao97/sea-g2p) — fast Vietnamese/English grapheme-to-phoneme, also by the author.

Tác giả: **Phạm Nguyễn Ngọc Bảo**

---

## 🔥 Quick Start (Web UI)

```bash
git clone https://github.com/pnnbao97/VieNeu-TTS.git
cd VieNeu-TTS
```

- **Option 1: CPU & macOS (minimal, torch-free) — recommended** — runs **v3 Turbo via ONNX**

  ```bash
  uv sync
  ```

  > ⚡ Use `uv sync`, not `pip install`, for the fastest CPU inference — it reproduces the locked environment with the optimized ONNX Runtime build. On Apple Silicon this ONNX/CPU path is **faster** than the MPS/PyTorch build.

- **Option 2: GPU (CUDA ≥ 12.8)** — **v3 Turbo on GPU (PyTorch)**: batched generation + multi-stream real-time streaming

  ```bash
  uv sync --extra cuda
  ```

**Start the Web UI:**

```bash
uv run vieneu-web
```

The UI opens at `http://127.0.0.1:7860` with a **Default voice** tab, a **Voice Cloning** tab, and a **Conversation** tab (batched multi-speaker podcasts).

---

## 📦 Using the Python SDK (`vieneu`)

**CPU (default)** — torch-free, runs v3 Turbo via ONNX Runtime. Most users want this:

```bash
pip install vieneu
```

**GPU (CUDA)** — only if you have an NVIDIA GPU; install a CUDA build of PyTorch yourself first:

```bash
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
pip install "transformers==4.57.6"   # Qwen3 backbone + MOSS codec (pinned — most stable)
pip install vieneu
```

> ℹ️ **When is GPU actually worth it?** Two cases: **bulk / long-form synthesis** (many chunks share one batched forward) and **serving many listeners** (the stream scheduler batches every `infer_stream` call — 16 concurrent real-time streams on an RTX 3060). For a **single short, interactive call** the torch-free **CPU/ONNX** path is fast enough (first audio ~140 ms with int8, ~300 ms with fp32) and needs no GPU.

### Full features guide

```python
from vieneu import Vieneu
from time import time

# Default = v3 Turbo (48 kHz). CPU → ONNX (torch-free, fp32); GPU → PyTorch (auto-detected).
tts = Vieneu()                    # fp32 backbone (default, max fidelity)
# tts = Vieneu(precision="int8")  # CPU only: ~2x faster, needs a CPU with VNNI

text = """[cười] Trời ơi, cái giọng nó tự nhiên mà nó mượt mà dã man, nghe không khác gì người thật luôn. Giờ thì tha hồ mà quẩy content với cả kho giọng nói đa dạng, đủ mọi sắc thái biểu cảm. Mọi người bật loa lên rồi cùng trải nghiệm thử với mình nhé!"""

# 1. Default voice (Minh Quân) — 48 kHz, no reference needed
start = time()
audio = tts.infer(text)
tts.save(audio, "output.wav")
print(f"Time taken: {time() - start:.2f} seconds")

# 2. Built-in voices by name
for label, voice_id in tts.list_preset_voices():
    print(label, voice_id)
audio = tts.infer("Mình là Xuân Vĩnh nè!", voice="Xuân Vĩnh")
tts.save(audio, "output_xuan_vinh.wav")

# 3. Emotion / non-verbal cues — EXPERIMENTAL: [cười] [thở dài] [hắng giọng]
audio = tts.infer("Nghe hay quá đi [cười]. Để mình nói tiếp [hắng giọng].", voice="Phạm Tuyên")

# 4. Instant voice cloning from a 3–8s reference clip (works on the torch-free CPU install too)
audio = tts.infer("Đây là giọng được nhân bản tức thì.", ref_audio="my_voice.wav", denoise=True)
```

> [!TIP]
> A **temperature around 0.8** gives the most stable result for v3 Turbo. Higher values add expressiveness but can be less stable.

### 🔊 Real-time streaming

v3 Turbo streams frame by frame on both backends. **GPU**: first audio in **~115 ms**, and every `infer_stream` call shares one CUDA graph (continuous batching) — **16 concurrent streams stay real-time** on a single RTX 3060 (RTF ≈ 0.5–0.6, 32 streams max). **CPU** (ONNX): first audio ~140 ms (int8) / ~300 ms (fp32), RTF < 1, one stream (two with int8).

```python
vieneu = Vieneu()   # GPU → PyTorch + stream scheduler; no GPU → ONNX/CPU
for chunk in vieneu.infer_stream("Xin chào! Đây là chế độ streaming của VieNeu, phát tới đâu nghe tới đó.", voice="Mai Anh"):
    play(chunk)   # np.float32 @ 48 kHz, play/write as it arrives
```

**OpenAI-compatible API** — `POST /v1/audio/speech` (`pcm`/`wav`, chunked body or SSE), drop-in for the OpenAI SDK, Pipecat, LiveKit:

```bash
uv run python -m apps.openai_speech                                  # → http://localhost:8000
# (or: docker compose -f docker/docker-compose.yml --profile api-gpu up)
```

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="x")
with client.audio.speech.with_streaming_response.create(
    model="vieneu-v3-turbo", voice="Mai Anh", response_format="pcm",
    input="Xin chào! Đây là chế độ streaming của VieNeu, phát tới đâu nghe tới đó.",
) as r:
    for chunk in r.iter_bytes(4096):   # s16le 48 kHz mono, as it is generated
        play(chunk)
```

All measurements (TTFA / RTF / streams vs `max_streams` on an RTX 3060), estimates for smaller GPUs and the CPU-only numbers: [docs/streaming.md](https://github.com/pnnbao97/VieNeu-TTS/blob/main/docs/streaming.md).

### ⚡ Batched generation (GPU)

`infer_batch()` runs many texts in **one batched forward** — same API on every backend (on CPU it still works, just sequentially). The batch caps at `max_batch_size` (default 32); pass `batch_size=1` to disable. A single long `infer()` also auto-batches its own chunks.

```python
audios = vieneu.infer_batch(texts, voice="Mai Anh")   # or infer_batch(..., batch_size=64)
```

### 🦜 Voice cloning & saved voices

```python
# Clone from a 3–8s clip; the reference is auto-denoised and trimmed to ≤ 8s
audio = vieneu.infer("Chào bạn, đây là giọng của tôi.", ref_audio="voice.wav", denoise=True)

# Enroll once, then reuse by name like a built-in voice
vieneu.add_voice("Giọng của tôi", "voice.wav")
audio = vieneu.infer("Câu này dùng giọng đã lưu.", voice="Giọng của tôi")

# Just clean up a clip (no synthesis)
wav, sr = vieneu.denoise("noisy.wav", out_path="clean.wav")
```

> `denoise`, `add_voice` and cloning work on **every** backend, including the torch-free CPU/ONNX install.

### ⚠️ Reading style is deprecated

`style` is **still accepted** by `infer`, `infer_stream`, `infer_batch` and `add_voice` so existing code keeps running, but it is **ignored** on v3 Turbo: the reading style is already baked into the reference itself (the speaker embedding + reference codes of the preset voice or of your cloned clip). Pick the reading character through the **voice** instead.

---

## 🎭 Preset Voices (23)

Call any of them by name via `voice="<name>"` — no reference audio required. Default voice: **Minh Quân**. (Generated from the SDK's `voices_v3_turbo.json`; `vieneu.list_preset_voices()` is authoritative.)

| Voice | Region | Sex | Character | | Voice | Region | Sex | Character |
|---|---|---|---|---|---|---|---|---|
| Anh Khôi | Bắc | M | Storytelling | | Đoan Trang | Bắc | F | Natural |
| Mai Anh | Bắc | F | News | | Ngọc Trân | Trung | F | Natural |
| **Minh Quân** (default) | Bắc | M | Natural | | Quang Sơn | Trung | M | Natural |
| Minh Đức | Bắc | M | News | | Adam | Nam | M | Natural |
| Mạnh Dũng | Bắc | M | Natural | | Kim Thanh | Nam | F | Storytelling |
| Ngọc Huyền | Bắc | F | Natural | | Minh Triết | Nam | M | News |
| Ngọc Linh | Bắc | F | Storytelling | | Mỹ Duyên | Nam | F | Storytelling |
| Phạm Tuyên | Bắc | M | Natural | | Thái Sơn | Nam | M | Storytelling |
| Quỳnh Anh | Bắc | F | Storytelling | | Thùy Dung | Nam | F | News |
| Thanh Bình | Bắc | M | Storytelling | | Thục Đoan | Nam | F | Storytelling |
| Trúc Ly | Bắc | F | Natural | | Đức Trí | Nam | M | Storytelling |
| Xuân Vĩnh | Bắc | M | Natural | |  |  |  |  |

For any other voice, use **voice cloning** with a short reference clip (`ref_audio="..."`).

---

## 🔬 Model Variants

| Model | Format | Device | Sample Rate | Quality | Features |
| --- | --- | --- | --- | --- | --- |
| **VieNeu-TTS-v3-Turbo** *(default)* | ONNX (CPU) / PyTorch (GPU) | CPU/GPU | 48 kHz | ⭐⭐⭐⭐⭐ | **23 preset voices, cloning, streaming (GPU: 16 concurrent streams, OpenAI-compatible API), emotion cues, conversation, LoRA fine-tuning** |
| VieNeu-TTS-v2 | PyTorch | GPU/CPU | 24 kHz | ⭐⭐⭐⭐⭐ | Podcast, En-Vi code-switching |
| VieNeu-TTS-v2 (GGUF) | GGUF Q4 | CPU | 24 kHz | ⭐⭐⭐⭐ | Fastest on CPU, Podcast |
| VieNeu-TTS-v1 | PyTorch | GPU | 24 kHz | ⭐⭐⭐⭐ | Stable (Vi only) |

---

## 📜 Usage Rights & Licensing FAQ

**Does Apache-2.0 cover every artifact in this repository?**
Yes. The license applies to **all** artifacts shipped here — `model.safetensors`, the ONNX exports, configs and tokenizers, and the bundled **preset-voice assets** (speaker embeddings + reference codes in `voices_v3_turbo.json`).

**May I use the preset voices and the generated audio commercially?**
Yes. The bundled preset voices are distributed under the same Apache-2.0 license as the rest of the repository, and audio generated with them **may be used in commercial and monetized content** (voice-over, videos, products, services) — no additional license or fee.

**Did the speakers behind the preset voices consent to AI training and synthetic speech?**
Yes. The speakers (or rightsholders) behind the shipped preset-voice assets granted appropriate rights and consent for their voice data to be used in **AI training and synthetic speech generation**, which is what allows those assets to be distributed under Apache-2.0 for both non-commercial and commercial synthetic audio generation.

**What about the training dataset?**
The detailed internal data-collection and processing pipeline for the training corpus is **not publicly disclosed**, and the [VieNeu-TTS-10k-ENVI](https://huggingface.co/datasets/pnnbao-ump/VieNeu-TTS-10k-ENVI) dataset is gated. The confirmations above cover the **preset voices shipped in this repository** and the model weights released here, which are the artifacts you actually redistribute or generate audio with.

**Which preset list is authoritative?**
`vieneu.list_preset_voices()` at the version you have installed. This card documents **SDK v3.7.1 (23 voices, default `Minh Quân`)**; earlier revisions shipped fewer voices under partly different names (3.3.0: 20 voices, default `Adam`), so pin the SDK version if the exact roster matters to you.

**Third-party components** — all permissively licensed, keep their notices when redistributing:
- [MOSS-Audio-Tokenizer-Nano](https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano) (OpenMOSS-Team) — Apache-2.0.
- [sea-g2p](https://github.com/pnnbao97/sea-g2p) — phonemizer, by the same author as this project.

> [!WARNING]
> **Voice cloning is your responsibility.** The consent confirmation above covers the **bundled preset voices only**. If you clone a voice from your own reference clip, you must have the right to use that person's voice. Do not clone real people without their permission, and do not use this model to impersonate, defraud, or produce misleading content.

---

## License

This model package is distributed under [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), matching the upstream model repository.

When you reuse, redistribute, or convert these assets, please keep the license notice and attribution intact for both:

- the original project: [pnnbao97/VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS)
- this Hugging Face package: [pnnbao-ump/VieNeu-TTS-v3-Turbo](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo)

If you bundle additional third-party assets, their own licenses still apply as well.

---

## 📑 Citation

```bibtex
@misc{vieneutts2026,
  title        = {VieNeu-TTS v3 Turbo: 48kHz Vietnamese Text-to-Speech with Instant Voice Cloning and Emotion Control},
  author       = {Pham Nguyen Ngoc Bao},
  year         = {2026},
  publisher    = {Hugging Face},
  howpublished = {\url{https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo}}
}
```

---

**Made with ❤️ for the Vietnamese TTS community**
