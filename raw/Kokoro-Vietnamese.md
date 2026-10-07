---
language:
  - vi
pipeline_tag: text-to-speech
tags:
  - kokoro
  - vietnamese
  - text-to-speech
  - onnx
license: apache-2.0
---

# Kokoro Vietnamese

Fine-tuned Vietnamese Kokoro TTS artifacts.

## Files

- `kokoro_vi.pth`: PyTorch Kokoro `KModel` checkpoint for inference.
- `kokoro_vi.onnx`: ONNX Runtime export of the acoustic model.
- `kokoro_vi_voicepack.pt`: default Vietnamese voicepack.
- `config.json`: Kokoro config/vocab used by both PyTorch and ONNX inference.
- `voicepacks/*.pt`: additional Vietnamese voicepacks.

## Install

```bash
git clone https://github.com/iamdinhthuan/Kokoro-Vietnamese.git
cd Kokoro-Vietnamese
pip install -e .
```

For ONNX Runtime:

```bash
pip install -e ".[onnx]"
```

## PyTorch Inference

```bash
kokoro-vietnamese \
  --text "Xin chào, hôm nay tôi đang kiểm tra giọng đọc tiếng Việt." \
  --output outputs/sample.wav \
  --voice diem_trinh \
  --device cuda
```

## ONNX Runtime Inference

```bash
kokoro-vietnamese-onnx \
  --text "Tường nhà khách đã được sơn lại." \
  --output outputs/onnx.wav \
  --device cpu \
  --print-phonemes
```

The ONNX CLI downloads `kokoro_vi.onnx`, `kokoro_vi_voicepack.pt`, and
`config.json` from this repository when local paths are not provided. Install
`onnxruntime-gpu` and pass `--device cuda` to use CUDAExecutionProvider when
available.

## Export ONNX Yourself

```bash
kokoro-vietnamese-export-onnx \
  --output outputs/kokoro_vi.onnx
```

Vietnamese G2P is handled by `vig2p`, matching the GitHub inference and
training code.
