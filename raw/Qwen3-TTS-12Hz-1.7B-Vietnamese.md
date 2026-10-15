---
license: apache-2.0
language:
- vi
base_model:
- Qwen/Qwen3-TTS-12Hz-1.7B-Base
pipeline_tag: text-to-speech
tags:
- tts
- vietnamese
- style-control
- instruct-tts
- distillation
---

# Qwen3-TTS-12Hz-1.7B-Vietnamese

Vietnamese TTS fine-tuned from [Qwen/Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base),
two-stage on 1× H200:

1. **Phonology stage** — 3 epochs on TTSDistil-Phonology (no user turn: pure assistant text → codec)
2. **Style stage** — 5 epochs on TTSDistil2 (samples carry an `instruct` user turn, e.g. "nói giọng vui vẻ")

Final weights: `checkpoint-epoch-4/` (style stage, 5 epochs; mid-training comparison: `checkpoint-epoch-2/`). `phonology/checkpoint-epoch-0` + `phonology/checkpoint-epoch-2` = the stage-1 Phonology model (no user turn, 3 epochs) — also the init checkpoint of the style stage.

## Usage

Requires the vendored `qwen_tts` package (included under `vendor/qwen_tts`):

```python
import sys, torch
sys.path.append("/path/to/repo/vendor")
from qwen_tts import Qwen3TTSModel

tts = Qwen3TTSModel.from_pretrained(
    "/path/to/repo/checkpoint-epoch-4",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",  # "sdpa"
)
wavs, sr = tts.generate_custom_voice(
    text="Xin chào, đây là giọng tiếng Việt được fine-tune.",
    language="Vietnamese",
    speaker="Zephyr",
    instruct="trung tính",
    non_streaming_mode=True,
)
```

30 built-in speakers (Zephyr, Puck, Charon, Kore, Fenrir, Leda, Orus, Aoede, Callirrhoe, Autonoe, Enceladus, Iapetus, Umbriel, Algieba, Despina, Erinome, Algenib, Rasalgethi, Laomedeia, Achernar, lnilam, Schedar, Gacrux, Pulcherrima, Achird, Zubenelgenubi, Vindemiatrix, Sadachbia, Sadaltager, Sulafat). Speech tokenizer is frozen
(kept identical to the base model); only the talker stack was trained.
