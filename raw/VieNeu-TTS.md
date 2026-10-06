---
license: apache-2.0
datasets:
- pnnbao-ump/VieNeu-TTS-1000h
- pnnbao-ump/VieNeu-TTS-140h
language:
- vi
base_model:
- neuphonic/neutts-air
pipeline_tag: text-to-speech
---
# 🦜 VieNeu-TTS

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/pnnbao97/VieNeu-TTS)
[![Model](https://img.shields.io/badge/Hugging%20Face-Model-yellow)](https://huggingface.co/pnnbao-ump/VieNeu-TTS)
[![0.3B Model](https://img.shields.io/badge/Hugging%20Face-0.3B-orange)](https://huggingface.co/pnnbao-ump/VieNeu-TTS-0.3B)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-5865F2?logo=discord&logoColor=white)](https://discord.gg/yJt8kzjzWZ)

![Banner](https://cdn-uploads.huggingface.co/production/uploads/68b923a86c86c127a1975eda/vd7kW8h7ooSafcIhEQtyr.png)

## Overview

**VieNeu-TTS** is an advanced on-device Vietnamese Text-to-Speech (TTS) model with **instant voice cloning**.

> [!TIP]
> **Voice Cloning:** All model variants (including GGUF) support instant voice cloning with just **3-5 seconds** of reference audio.

This project features two core architectures trained on the [VieNeu-TTS-1000h](https://huggingface.co/datasets/pnnbao-ump/VieNeu-TTS-1000h) dataset:
- **VieNeu-TTS (0.5B):** An enhanced model fine-tuned from the NeuTTS Air architecture for maximum stability.
- **VieNeu-TTS-0.3B:** A specialized model **trained from scratch**, delivering 2x faster inference and ultra-low latency. [Check it out here](https://huggingface.co/pnnbao-ump/VieNeu-TTS-0.3B).

Tác giả: **Phạm Nguyễn Ngọc Bảo**

## ☕ Support This Project

Training high-quality TTS models requires significant GPU resources. If you find this model useful, please consider supporting the development:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/pnnbao)

---

## 🦜 Voice Cloning Inference

**Reference Voice (Speaker Example):**  
<audio controls src="https://cdn-uploads.huggingface.co/production/uploads/68b923a86c86c127a1975eda/Rpw1V6X1px59SWQKn_W9D.wav"></audio>

**Input Text:**  
> Trên bầu trời xanh thẳm, những đám mây trắng lửng lờ trôi như những chiếc thuyền nhỏ đang lướt nhẹ theo dòng gió. Dưới mặt đất, cánh đồng lúa vàng rực trải dài tới tận chân trời, những bông lúa nghiêng mình theo từng làn gió.

**Generated Output (Cloned Voice):**  
<audio controls src="https://cdn-uploads.huggingface.co/production/uploads/68b923a86c86c127a1975eda/f40t4ueGqmsGDmNIGcU3J.mpga"></audio>

---

## 🔥 Quick Start (Web UI)

### 1. Installation
```bash
git clone https://github.com/pnnbao97/VieNeu-TTS.git
cd VieNeu-TTS
# Install uv (if you haven't)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/macOS: curl -LsSf https://astral.sh/uv/install.sh | sh
# Install dependencies & Run
uv sync
uv run vieneu-web
```

### 2. Demo Video
<video controls src="https://cdn-uploads.huggingface.co/production/uploads/68b923a86c86c127a1975eda/pRsUExICceCh47dgu4P8I.mp4" width="100%"></video>

---

## 📦 Using Python SDK (vieneu)

Install the SDK to integrate VieNeu-TTS-0.3B into your research or applications:

```bash
# Windows (Avoid llama-cpp build errors)
pip install vieneu --extra-index-url https://pnnbao97.github.io/llama-cpp-python-v0.3.16/cpu/
# Linux / MacOS
pip install vieneu
```

### Full Features Guide
```python
from vieneu import Vieneu
import os
# Initialization
tts = Vieneu()  # Default: 0.3B-Q4 GGUF for CPU
os.makedirs("outputs", exist_ok=True)
# 1. List preset voices
available_voices = tts.list_preset_voices()
for desc, name in available_voices:
    print(f"   - {desc} (ID: {name})")
# 2. Use specific voice (dynamically select second voice)
if available_voices:
    _, my_voice_id = available_voices[1] if len(available_voices) > 1 else available_voices[0]
    voice_data = tts.get_preset_voice(my_voice_id)
    audio_spec = tts.infer(text="Chào bạn, tôi đang nói bằng giọng của bác sĩ Tuyên.", voice=voice_data)
    tts.save(audio_spec, f"outputs/standard_{my_voice_id}.wav")
    print(f"💾 Saved synthesis to: outputs/standard_{my_voice_id}.wav")
# 3. Standard synthesis (uses default voice)
text = "Xin chào, tôi là VieNeu. Tôi có thể giúp bạn đọc sách, làm chatbot thời gian thực, hoặc thậm chí clone giọng nói của bạn."
audio = tts.infer(text=text)
tts.save(audio, "outputs/standard_output.wav")
print("💾 Saved synthesis to: outputs/standard_output.wav")
# 4. Zero-shot voice cloning
if os.path.exists("examples/audio_ref/example_ngoc_huyen.wav"):
    cloned_audio = tts.infer(
        text="Đây là giọng nói đã được clone thành công từ file mẫu.",
        ref_audio="examples/audio_ref/example_ngoc_huyen.wav",
        ref_text="Tác phẩm dự thi bảo đảm tính khoa học, tính đảng, tính chiến đấu, tính định hướng."
    )
    tts.save(cloned_audio, "outputs/standard_cloned_output.wav")
    print("💾 Saved cloned voice to: outputs/standard_cloned_output.wav")
# 5. Cleanup
tts.close()
```

### Remote Mode (Ultra-Fast with LMDeploy Server)
For maximum speed, deploy a Docker server first, then connect remotely:

**Step 1: Deploy Docker Server**
```bash
docker run --gpus all -p 23333:23333 pnnbao/vieneu-tts:serve --model pnnbao-ump/VieNeu-TTS --tunnel
```

**Step 2: Connect from Client**
```python
from vieneu import Vieneu
import os
# Configuration
REMOTE_API_BASE = 'http://your-server-ip:23333/v1'  # Or bore.pub:XXXX
REMOTE_MODEL_ID = "pnnbao-ump/VieNeu-TTS"
# Initialization (LIGHTWEIGHT - only loads small codec locally)
tts = Vieneu(mode='remote', api_base=REMOTE_API_BASE, model_name=REMOTE_MODEL_ID)
os.makedirs("outputs", exist_ok=True)
# List remote voices
available_voices = tts.list_preset_voices()
for desc, name in available_voices:
    print(f"   - {desc} (ID: {name})")
# Use specific voice
if available_voices:
    _, my_voice_id = available_voices[1]
    voice_data = tts.get_preset_voice(my_voice_id)
    audio_spec = tts.infer(text="Chào bạn, tôi đang nói bằng giọng của bác sĩ Tuyên.", voice=voice_data)
    tts.save(audio_spec, f"outputs/remote_{my_voice_id}.wav")
    print(f"💾 Saved synthesis to: outputs/remote_{my_voice_id}.wav")
# Standard synthesis
text_input = "Chế độ remote giúp tích hợp VieNeu vào ứng dụng Web hoặc App cực nhanh mà không cần GPU tại máy khách."
audio = tts.infer(text=text_input)
tts.save(audio, "outputs/remote_output.wav")
print("💾 Saved remote synthesis to: outputs/remote_output.wav")
# Zero-shot voice cloning (encodes audio locally, sends codes to server)
if os.path.exists("examples/audio_ref/example_ngoc_huyen.wav"):
    cloned_audio = tts.infer(
        text="Đây là giọng nói được clone và xử lý thông qua VieNeu Server.",
        ref_audio="examples/audio_ref/example_ngoc_huyen.wav",
        ref_text="Tác phẩm dự thi bảo đảm tính khoa học, tính đảng, tính chiến đấu, tính định hướng."
    )
    tts.save(cloned_audio, "outputs/remote_cloned_output.wav")
    print("💾 Saved remote cloned voice to: outputs/remote_cloned_output.wav")
```

---

## 📋 Reference Voices

| File | Gender | Accent | Description |
|---|---|---|---|
| Bình | Male | North | Male voice, North accent |
| Tuyên | Male | North | Male voice, North accent |
| Nguyên | Male | South | Male voice, South accent |
| Hương | Female | North | Female voice, North accent |
| Ngọc | Female | North | Female voice, North accent |
| Đoan | Female | South | Female voice, South accent |

---

## 🔬 Model Variants

| Model                   | Format  | Device  | Quality    | Speed                   |
| ----------------------- | ------- | ------- | ---------- | ----------------------- |
| VieNeu-TTS              | PyTorch | GPU/CPU | ⭐⭐⭐⭐⭐ | Very Fast with lmdeploy |
| VieNeu-TTS-0.3B         | PyTorch | GPU/CPU | ⭐⭐⭐⭐   | **Ultra Fast (2x)**     |
| VieNeu-TTS-0.3B-q4-gguf | GGUF Q4 | CPU/GPU | ⭐⭐⭐     | **Extreme Speed (2x)**  |

---

## 📑 Citation

```bibtex
@misc{vieneutts2026,
  title        = {VieNeu-TTS: Vietnamese Text-to-Speech with Instant Voice Cloning},
  author       = {Pham Nguyen Ngoc Bao},
  year         = {2026},
  publisher    = {Hugging Face},
  howpublished = {\url{https://huggingface.co/pnnbao-ump/VieNeu-TTS}}
}
```

Please also cite the base model:

```bibtex
@misc{neuttsair2026,
  title        = {NeuTTS Air: On-Device Speech Language Model with Instant Voice Cloning},
  author       = {Neuphonic},
  year         = {2026},
  publisher    = {Hugging Face},
  howpublished = {\url{https://huggingface.co/neuphonic/neutts-air}}
}
```

---

**Made with ❤️ for the Vietnamese TTS community**