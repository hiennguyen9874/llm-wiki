---
license: apache-2.0
language:
- vi
base_model:
- k2-fsa/OmniVoice
- Qwen/Qwen3-0.6B
pipeline_tag: text-to-speech
library_name: omnivoice
tags:
- text-to-speech
- tts
- voice-cloning
- voice-design
- zero-shot
- vietnamese
- omnivoice
---

# G-OmniVoice

**G-OmniVoice** is a Vietnamese-optimized text-to-speech model with zero-shot **voice cloning** and **voice design**, fine-tuned from [k2-fsa/OmniVoice](https://huggingface.co/k2-fsa/OmniVoice) (Qwen3-0.6B backbone + Higgs Audio 2 codec) on a large-scale Vietnamese speech corpus.

Its defining strength is doing **two hard things at once**: it **reads Vietnamese accurately** *and* **preserves the reference speaker's voice** — the lowest WER of any public OmniVoice model, combined with top-tier speaker similarity.

- 🇻🇳 Optimized for natural Vietnamese speech
- 🎯 **Accurate pronunciation *and* faithful voice** — best-in-class WER without sacrificing speaker similarity
- 🎙️ Zero-shot voice cloning from a 3–10 second reference clip

## Benchmark

Evaluated on a held-out Vietnamese test set. WER ↓ (intelligibility), SIM ↑ (speaker similarity), MOS ↑ (naturalness).

| Model name                            | WER ↓  | SIM ↑ | MOS ↑ |
| :------------------------------------ | :----- | :---- | :---- |
| k2-fsa/OmniVoice                      | 0.0712 | 0.892 | 7.709 |
| kjanh/KhanhTTS-OmniVoice              | 0.0375 | 0.888 | 7.678 |
| VietNeu/v3turbo                       | 0.0551 | 0.778 | 7.570 |
| g-group-ai-lab/g-omnivoice (ours)     | 0.0259 | 0.890 | 7.685 |

![WER vs SIM across Vietnamese TTS models](wer_vs_sim.png)

The scatter above plots accuracy (WER) against voice fidelity (SIM). Every other model has to compromise: k2-fsa keeps the voice but reads least accurately, VietNeu drifts on both. **G-OmniVoice sits alone in the top-left "best of both worlds" corner** — it reads the most accurately (lowest WER, ≈31% better than the next model) *while* staying faithful to the original voice (SIM 0.890, essentially tied with the best). Accurate and faithful, at the same time.

## Installation

```bash
# 1. PyTorch (NVIDIA GPU, CUDA 12.8)
pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 \
    --extra-index-url https://download.pytorch.org/whl/cu128

# 2. OmniVoice runtime
pip install omnivoice
```

## Usage

```python
import torch
import soundfile as sf
from omnivoice import OmniVoice

model = OmniVoice.from_pretrained(
    "g-group-ai-lab/g-omnivoice",
    device_map="cuda:0",
    dtype=torch.float16,
)

# --- Voice cloning (from a reference clip) ---
audio = model.generate(
    text="Xin chào, đây là giọng nói được nhân bản bằng G-OmniVoice.",
    ref_audio="reference.wav",
    ref_text="Transcript of the reference audio.",
)
sf.write("clone.wav", audio[0], 24000)

# --- Voice design (no reference audio) ---
audio = model.generate(
    text="Đây là một giọng nói được tạo từ mô tả thuộc tính.",
    instruct="female, young adult, medium pitch, northern Vietnamese accent",
)
sf.write("design.wav", audio[0], 24000)
```

### Tips

- Apply **text normalization** (numbers, dates, symbols, abbreviations) before synthesis.
- Split long inputs into sentence-sized **chunks** for stable prosody.
- Use 3–10 s of clean, single-speaker **reference audio** for the best clone.

## Supported Languages

Optimized for **Vietnamese**. The underlying OmniVoice base supports 600+ languages in zero-shot mode; performance on other languages follows the base model.

## Citation

```bibtex
@misc{gomnivoice2026,
    title  = {G-OmniVoice: Natural Vietnamese Zero-Shot Text-to-Speech},
    author = {G-Group AI Lab},
    year   = {2026},
    url    = {https://huggingface.co/g-group-ai-lab/g-omnivoice}
}

@article{zhu2026omnivoice,
    title   = {OmniVoice: Towards Omnilingual Zero-Shot Text-to-Speech with Diffusion Language Models},
    author  = {Zhu, Han and Ye, Lingxuan and Kang, Wei and Yao, Zengwei and Guo, Liyong and Kuang, Fangjun and Han, Zhifeng and Zhuang, Weiji and Lin, Long and Povey, Daniel},
    journal = {arXiv preprint arXiv:2604.00688},
    year    = {2026}
}
```

## License

Apache 2.0, following the base [k2-fsa/OmniVoice](https://huggingface.co/k2-fsa/OmniVoice) model. The bundled audio tokenizer is derived from Higgs Audio 2 and remains subject to the **Boson Higgs Audio 2 Community License** (see `audio_tokenizer/LICENSE`).

## Acknowledgments

- [k2-fsa / Next-gen Kaldi](https://github.com/k2-fsa/OmniVoice) — OmniVoice base model and runtime
- [Boson AI](https://huggingface.co/bosonai) — Higgs Audio 2 tokenizer
- [Qwen Team](https://github.com/QwenLM) — Qwen3 backbone
- [G-Group AI Lab](https://huggingface.co/g-group-ai-lab) — Vietnamese fine-tuning and release
