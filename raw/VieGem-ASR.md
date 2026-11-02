---
language:
- vi
- en
license: cc-by-nc-sa-4.0
library_name: pytorch
pipeline_tag: automatic-speech-recognition
base_model: google/embeddinggemma-2
tags:
- ctc
- vietnamese
- code-switching
- streaming
- embeddinggemma
- asr
metrics:
- wer
---

# VieGem-ASR 🇻🇳💎

<p align="center"><img src="assets/cover.jpg" width="460" alt="VieGem-ASR"></p>

Fast Vietnamese and Vietnamese–English speech recognition: a 359M-parameter streaming CTC model on Google's
**EmbeddingGemma 2** audio encoder. Inspired by Quan Nguyen's **QUAN-Transcribe-1.0**.

- **Fast:** about **3,500× real time** on one H100 (batched, greedy); streams in 0.48 s chunks with no look-ahead.
- **Vietnamese:** mean WER **6.34** over 8 common test sets (**5.29** with the included n-gram LM).
- **Code-switching:** ViMedCSS WER **14.3**; **66%** of English terms written exactly.

## Demo

<video controls width="540" src="https://huggingface.co/5CD-AI/VieGem-ASR/resolve/main/demo/viegem_asr_promo.mp4"></video>

## Results

### Vietnamese test sets

WER %, lower is better, greedy unless marked "+ LM". VieGem-ASR, QUAN-Transcribe-1.0 and Qwen3-ASR-0.6B were run by
us with one normalizer; † = reported in the QUAN-Transcribe-1.0 model card (our scorer matches its numbers within 0.1).

| Test set | What it contains | VieGem-ASR | VieGem-ASR + LM | QUAN-Transcribe-1.0 | Qwen3-ASR-0.6B | Gemini-Flash-3.8 † | ElevenLabs Scribe v2 † | PhoWhisper-large † | Whisper large-v3 † |
|---|---|---|---|---|---|---|---|---|---|
| VIVOS | read speech, quiet room | 6.63 | _4.78_ | 7.52 | 10.22 | 9.36 | 9.14 | **4.52** | 9.18 |
| FLEURS vi | read Wikipedia sentences | 7.33 | _5.85_ | 7.88 | 8.40 | 5.90 | 5.60 | **5.31** | 7.09 |
| Common Voice 17 | read, crowd-sourced microphones | 8.61 | **6.21** | 9.69 | 16.07 | 10.30 | 10.50 | 9.12 | 18.43 |
| PhoAudiobook | audiobooks | 1.39 | 1.04 | 1.39 | 3.23 | 1.60 | 1.45 | **0.87** | 1.85 |
| LSVSC | large mixed-domain corpus | 5.16 | **4.71** | 5.35 | 7.78 | 5.70 | 6.25 | 6.81 | 13.96 |
| Bud500 | mixed domains, tightly cut clips | 3.08 | 2.75 | 1.82 | 6.79 | **1.80** | 3.15 | 9.51 | 64.03 |
| GigaSpeech2 vi | YouTube, spontaneous | 9.50 | **8.52** | 11.60 | 11.37 | 10.70 | 10.50 | 10.14 | 14.19 |
| ViMD | dialects of 63 provinces | 9.05 | **8.46** | 9.84 | 13.98 | 10.00 | 10.05 | 11.38 | 15.56 |
| **Mean of the 8** | | 6.34 | **5.29** | 6.89 | 9.73 | 6.92 | 7.08 | 7.21 | 18.04 |

Bold = best greedy result per row. Text is lowercased, without punctuation, numbers as words.

### Vietnamese–English code-switching (ViMedCSS)

| System | Test WER | Hard WER |
|---|---|---|
| Whisper-large-v3 (paper) | 34.47 | 39.35 |
| PhoWhisper-large (paper) | 31.24 | 37.37 |
| PhoWhisper-small + AG, fine-tuned (paper) | 23.67 | 33.73 |
| QUAN-Transcribe-1.0 | 22.26 | 26.56 |
| **VieGem-ASR** | **14.30** | **21.08** |
| **VieGem-ASR + LM** | **13.00** | **19.84** |

"Paper" = numbers from the ViMedCSS paper (its own normalization, so approximate).

### Streaming and speed

- Streaming (0.48 s chunks): VIVOS 8.73, CV17 10.84, FLEURS 9.02, LSVSC 5.84, ViMD 10.00, ViMedCSS 15.99.
- A 10-minute video is transcribed in **0.49 s** on one H100 (median of 20 runs, ~1,220× real time).

## Usage

```python
import torch, soundfile as sf
from transformers import AutoTokenizer
from asr.model import CTCModel, ModelConfig, greedy_decode     # asr/ folder of this repo
from asr.text import Units

ck = torch.load("viegem_asr.pt", map_location="cpu")
cfg = ModelConfig.from_dict(ck["model_config"])
units = Units(ck["gemma_ids"])
tok = AutoTokenizer.from_pretrained(cfg.encoder_id)               # google/embeddinggemma-2 (accept its terms)
model = CTCModel(cfg, units.gemma_ids)
model.load_state_dict(ck["model"], strict=False)
model = model.cuda().eval()

wav, sr = sf.read("audio.wav", dtype="float32")                  # 16 kHz mono, ≤ 30 s
x = torch.from_numpy(wav)[None].cuda()
with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
    logits, lens = model(x, torch.tensor([x.shape[1]], device="cuda"), streaming=False)  # streaming=True: 0.48 s chunks
print(units.decode(tok, greedy_decode(logits, lens)[0]))
```

With the LM (`pip install kenlm`):

```python
from asr.lm_decode import LMDecoder

words = open("lm/viegem_lm.unigrams.txt", encoding="utf-8").read().split()
dec = LMDecoder("lm/viegem_lm.bin", unigrams=words, alpha=0.35, beta=1.5)
pieces = ["", ""] + tok.convert_ids_to_tokens(units.gemma_ids)
lp = torch.log_softmax(logits[0, : lens[0]].float(), -1).cpu().numpy()
print(units.decode(tok, dec.decode(lp, pieces, beam_width=32)))
```

## Model

- **Encoder:** EmbeddingGemma 2 audio tower (12 conformer layers, 25 frames/s); top 4 layers fine-tuned.
- **Reader:** layer mix + 6 transformer blocks (d=768) with chunked attention, so one model serves offline and streaming.
- **Head:** 21,031 Gemma tokens (Vietnamese, English, single characters), initialized from Gemma's text embeddings.
- **Files:** `viegem_asr.pt` (fp16 weights, 311 MB), `asr/` (code), `lm/` (4-gram KenLM from our training transcripts, 71 MB), `demo/`.

## Training data

About **5,800 hours**, every set filtered against all test and dev sentences.

| Type | Sources | Hours |
|---|---|---|
| Audiobooks | PhoAudiobook, InfoRe2 | ~1,900 |
| Social media and YouTube | VietSpeech, viVoice, GigaSpeech2 (subset), VietSuperSpeech | ~2,820 |
| Mixed domains | Bud500, VLSP2020, LSVSC, ViMD, FPT FOSD, InfoRe1, FLEURS, Common Voice 17 | ~780 |
| English | LibriSpeech-100 | ~100 |
| Vietnamese–English (medical) | ViMedCSS | ~23 |

## Limitations

- Output is lowercase, without punctuation; numbers are written as words.
- Clips cut in the middle of a word (as in Bud500) lose the last word more often.
- English is meant for terms mixed into Vietnamese; plain English is weak (LibriSpeech test-clean 10.7).

## License

Non-commercial research use (**CC-BY-NC-SA-4.0**), because the training data includes Bud500, viVoice and PhoAudiobook.
Use must also follow the **Gemma Terms of Use** and Prohibited Use Policy.

## Credits

Google DeepMind (EmbeddingGemma 2); Quan Nguyen (QUAN-Transcribe-1.0, the inspiration for this work); the authors of
VIVOS, Common Voice, FLEURS, LSVSC, ViMD, Bud500, PhoAudiobook, VietSpeech, viVoice, GigaSpeech2, VietSuperSpeech,
VLSP2020, FPT FOSD, InfoRe, ViMedCSS and LibriSpeech. ViMedCSS baselines: Nguyen et al., LREC 2026.
