---
type: Concept
title: AuroraASR-1M
description: 949,073-parameter weight-shared Conformer-CTC English ASR model trained only on LibriSpeech 960 h, reporting 11.43% test-clean and 26.50% test-other WER with greedy decoding and 436x realtime on one CPU thread.
tags: [stt, ctc, conformer, tiny-model, weight-sharing, english, quantization, edge]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T02:38:00Z }
stale_after: 2027-04-21
sources:
  - id: auroraasr-card
    resource: ../raw/AuroraAI-Research-AuroraASR-1M.md
    kind: documentation
    title: AuroraASR-1M Hugging Face model card capture
---

AuroraASR-1M is a sub-1M-parameter English speech recognizer from AuroraAI-Research that reuses four Conformer-lite blocks twice each and decodes with a CTC head over a 256-piece BPE vocabulary, trained only on the 960-hour LibriSpeech corpus. The card reports 949,073 parameters, 11.43% WER on LibriSpeech `test-clean` and 26.50% on `test-other` under greedy decoding with no external language model, and a real-time factor of 0.0007 on a Blackwell RTX PRO 6000 GPU and 0.0023 on one pinned CPU thread. Its value in this wiki is as the compact end of the size/accuracy frontier: roughly 41× smaller than Whisper Tiny while about twice its word error on read English speech, with no punctuation, casing, streaming, or language-model support documented (**Reported**; the ratio arithmetic and position are **Synthesis**).[^auroraasr-card]

## Identity and licensing

- **Publisher and card:** `AuroraAI-Research/AuroraASR-1M` on Hugging Face, declared `library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, `language: en`, `datasets: librispeech_asr`, tags `ctc`, `conformer`, `custom_code`, and `license: apache-2.0` (**Observed** by static inspection of the capture's frontmatter).[^auroraasr-card]
- **Missing identity evidence:** the capture carries no revision, commit hash, release date, capture date, weight checksum, paper, code repository, or author affiliation. Only the repository name and the training notes identify the work (**Observed**; limits).[^auroraasr-card]
- **Licensing:** Apache-2.0 is declared in frontmatter only; the license text and any bundled third-party notices are not in the capture. Because the model requires `trust_remote_code=True`, using it executes Python shipped in the model repository, which was not inspected here (**Reported**; supply-chain limit is **Synthesis**).[^auroraasr-card]

## Architecture and tokenization

- **Encoder:** a 4× time-subsampling convolutional stem, then four unique Conformer-lite blocks each applied twice, with a separate LayerNorm per pass; width 128, 4 attention heads with rotary position embeddings, feed-forward dimension 384, depthwise convolution kernel 15 (**Reported**).[^auroraasr-card]
- **Weight sharing:** four parameter sets serve eight block applications, so effective depth is twice the unique parameter count. The card reports no ablation isolating what that sharing saves or costs against a fully distinct eight-block model, so the mechanism behind the small size is described but not measured (**Reported**; unablated — **Synthesis**).[^auroraasr-card]
- **Output head:** CTC over 257 classes — 256 SentencePiece BPE pieces plus blank — trained on training-transcript text only, lowercased and restricted to `a-z`, apostrophe, and space, so the model emits no punctuation and no casing (**Reported**).[^auroraasr-card]
- **Size consistency (arithmetic check):** 949,073 weights at 4 and 2 bytes give 3.80 MB and 1.90 MB decimal, matching the card's 3.81 MB FP32 and 1.91 MB FP16 files; the 1.06 MB INT8 file exceeds one byte per weight by about 0.11 MB, consistent with the declared per-output-channel scales (**Observed** recomputation from the card's own figures).[^auroraasr-card]

## Training recipe

- **Data:** LibriSpeech 960 h only — `train-clean-100`, `train-clean-360`, `train-other-500` — with no additional audio, text, noise, speed-perturbation, or external-language-model data. Utterances shorter than 1 s or longer than 16 s were dropped, as were utterances whose token count exceeded one quarter of their feature frames (**Reported**).[^auroraasr-card]
- **Model selection:** `dev-clean` was used for per-epoch monitoring and checkpoint selection, and `test-clean`/`test-other` only for final evaluation, so the reported scores are not the selection split (**Reported**; this avoids the selection-adjacent test-set concern recorded for [Orukeet](orukeet.md) — **Synthesis**).[^auroraasr-card]
- **Features:** 80-bin log-mel at 16 kHz, 25 ms window, 10 ms hop, 512-point FFT, 20 Hz–8 kHz, with per-utterance mean/variance normalization of each mel bin (**Reported**).[^auroraasr-card]
- **Objective:** CTC loss on the final layer at weight 0.7 plus an auxiliary intermediate CTC loss at weight 0.3 after the second unique block; the auxiliary head reuses the final LayerNorm and output layer so it adds no parameters and is discarded at inference. Loss is normalized by the number of target tokens (**Reported**).[^auroraasr-card]
- **Optimizers:** Muon for 2-D weight matrices in the encoder blocks and stem projection (lr 0.03, Nesterov momentum 0.95, 5 Newton–Schulz steps, weight decay 0.01) and AdamW for everything else (lr 5e-3, betas 0.9/0.98, weight decay 0.01 on matrices but none on biases, norms, or depthwise convolutions) (**Reported**).[^auroraasr-card]
- **Schedule and batching:** 100-step linear warmup then cosine decay to 5% of peak, global-norm gradient clipping at 5.0, dynamic batching of 2,400 s of audio per batch that is length-bucketed with random jitter and padded to multiples of 64 frames, and a length-sorted first epoch (SortaGrad) before random order (**Reported**).[^auroraasr-card]
- **Precision and regularization:** bfloat16 autocast, TF32 matmuls, `torch.compile`, EMA of weights with decay 0.9995 and warmup (all reported results use the EMA weights), SpecAugment from epoch 3 with 2 frequency masks up to 8 bins and 3 time masks up to 4% of the utterance each, dropout 0.0, seed 0 (**Reported**).[^auroraasr-card]
- **Compute:** the step count was fixed from a 200-step calibration so the cosine decay would finish inside a wall-clock budget; training ran 379 epochs, about 10 hours, on an RTX PRO 6000. At 960 h per epoch that is roughly 364,000 hours of audio passed in about 10 hours, an aggregate throughput of about 36,000× realtime. No multi-run variance, seed sweep, or learning-rate sensitivity study is reported (**Reported**; throughput is **Synthesis** arithmetic).[^auroraasr-card]

## Reported accuracy

WER (%) on LibriSpeech with greedy CTC decoding and no external language model; competitor figures are relayed by this card from each model's published card or paper, not re-measured (**Reported**):[^auroraasr-card]

| Model | Params | test-clean | test-other |
| --- | ---: | ---: | ---: |
| **AuroraASR-1M** | **950K** | **11.43** | **26.50** |
| Femto-ASR | 2.39M | 10.95 | 25.36 |
| Citrinet-256 CTC | 10M | 3.8 | 9.8 |
| Moonshine Tiny | 27M | 4.58 | not published |
| Whisper Tiny (English only) | 39M | 5.6 | 14.6 |
| Whisper Tiny (multilingual) | 39M | 7.6 | 16.9 |

- **Reading the row against its neighbours (Synthesis):** AuroraASR-1M is 2.52× smaller than Femto-ASR and gives up 0.48 points on `test-clean` and 1.14 on `test-other`; against Whisper Tiny `en` it is 41× smaller but 2.04× / 1.82× worse; against Citrinet-256 it is 10.5× smaller and about 2.7–3.0× worse. The only near-peer at this scale is Femto-ASR, which suggests returns from adding parameters flatten quickly below roughly 2.5M under this training recipe.[^auroraasr-card]
- **Comparability limits:** the card states that WER is scored on normalized text (lowercase, no punctuation) with word-level edit distance and that models reporting on differently normalized text are therefore not strictly comparable. Training data, decode protocol, and language-model use for the competitor rows are not established here, and none of Femto-ASR, Citrinet-256, Moonshine Tiny, or Whisper Tiny has a concept page in this wiki (**Reported**; comparison is **Synthesis**).[^auroraasr-card]
- **Negative result retained:** the card makes no claim of beating any competitor; the model is the least accurate in its own comparison table and its case rests on parameter count and speed, not accuracy (**Observed** from the table).[^auroraasr-card]

## Reported speed and precision

Real-time factor (processing time / audio duration, lower is better) at batch size 1 on 100 `test-clean` utterances, 13.3 min of audio total, with log-mel extraction and CTC decoding included in the end-to-end figure (**Reported**):[^auroraasr-card]

| Device | RTF (end-to-end) | × real-time |
| --- | ---: | ---: |
| NVIDIA RTX PRO 6000 Blackwell Server Edition (GPU) | 0.0007 | 1362× |
| 1 vCPU, single thread pinned to one core | 0.0023 | 436× |

- **Displayed-value mismatch (Observed):** the stated multiples do not reproduce from the rounded RTFs in the same table — 1/0.0007 is about 1429× rather than 1362×, and 1/0.0023 is about 435× rather than 436×. Both are rounding artifacts of the printed RTF, but the GPU row's printed pair implies a true RTF near 0.00073, so neither printed value should be reused as an exact measurement.[^auroraasr-card]
- **Precision files:** FP32 at the repository root is the reference (3.81 MB, the precision used for every WER and RTF figure above); FP16 lives in `subfolder="fp16"` (1.91 MB); INT8 lives in `subfolder="int8"` (1.06 MB) with Linear weights stored as int8 plus per-output-channel scales dequantized on the fly (**Reported**).[^auroraasr-card]
- **Quantization claim is unquantified:** the card says WER is "nearly lossless across precisions, all the way down to INT8 weight-only", but publishes no per-precision WER, no INT8 speed figure, and states that INT8 "does not make the arithmetic faster" — it only shrinks download and memory. Treat the losslessness claim as an untested assertion until per-precision numbers appear (**Reported**; limit is **Synthesis**).[^auroraasr-card]

## Usage and interface

```python
import soundfile as sf
from transformers import AutoModelForCTC, AutoFeatureExtractor

repo = "AuroraAI-Research/AuroraASR-1M"
model = AutoModelForCTC.from_pretrained(repo, trust_remote_code=True).eval()  # FP32
# model = AutoModelForCTC.from_pretrained(repo, subfolder="int8", trust_remote_code=True).eval()  # INT8
# model = AutoModelForCTC.from_pretrained(repo, subfolder="fp16", trust_remote_code=True).half().cuda().eval()  # FP16
fe = AutoFeatureExtractor.from_pretrained(repo, trust_remote_code=True)

wav, sr = sf.read("audio.wav", dtype="float32")
print(model.transcribe(wav)[0])
```

- Runtime requires `torch`, `transformers`, and `sentencepiece`; `trust_remote_code=True` is required because the repository ships custom code (**Reported**; commands were read, not run — **Observed** documentation, **Unverified** execution).[^auroraasr-card]
- **Undocumented interface surface:** only `model.transcribe(wav)[0]` is shown. The card does not define the return tuple, confidence scores, timestamps, batching, chunked or streaming input, resampling behavior for non-16 kHz audio, or any HTTP/server wrapper. Nothing here establishes a callable realtime ASR service (**Observed**; absence is **Synthesis**).[^auroraasr-card]

## Fit for a voice pipeline

**Synthesis from the card's own numbers; no voice-loop measurement exists in the source.**

- **Not a streaming slot candidate as documented.** There is no chunking, partial-result, endpointing, timestamp, or VAD integration, and the architecture is a full-utterance CTC encoder. Its 436× CPU realtime factor is aggregate throughput over 13.3 min of short utterances, not per-turn latency, and excludes model load and Python/Transformers call overhead — do not read it as a voice-agent latency budget.[^auroraasr-card]
- **Accuracy is below conversational tolerance on this evidence.** 26.50% WER on `test-other` means roughly one word in four is wrong, the output has no casing or punctuation, and no language model, beam search, or rescoring hook is documented. Any dialogue LLM downstream would see degraded, unpunctuated text.[^auroraasr-card]
- **Where it does fit:** an English-only offline transcription floor, a size/accuracy reference point when scoping a tiny on-device recognizer, and a worked example of Muon-plus-AdamW optimization and intermediate CTC supervision at sub-1M scale. It does not serve this wiki's Vietnamese focus, since the card declares English and a `a-z`+apostrophe vocabulary only.[^auroraasr-card]
- **Evaluation gap for deployment decisions:** all evidence is clean read speech (LibriSpeech) with no noise, reverberation, far-field, telephony, accent, or domain-shift testing, so the effect of adding a speech-enhancement front end or of real call audio is unknown.[^auroraasr-card]

## Relationships

- Compiled into and compared against the [ASR/STT Model Survey](asr-stt-model-survey.md), which holds the cross-model catalog, licensing table, and edge-deployment comparison (**Synthesis**).[^auroraasr-card]
- Smallest-footprint peer compiled separately: [Whistle](whistle.md) covers a 16.9 MB single-file multilingual on-device model with word timestamps and keyword biasing on a shared CPU engine; read the two together to contrast a packaged runtime artifact with this research checkpoint at similar scale (**Synthesis**).[^auroraasr-card]
- Same output convention as [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md) — greedy CTC producing lowercase text without punctuation — at roughly 600× fewer parameters, which makes the pair a concrete illustration of what that parameter gap buys in WER (**Synthesis**).[^auroraasr-card]
- Depends on downstream text normalization for a usable voice-loop transcript: the unpunctuated, uncased output needs a step such as [Punctuation Restoration (base, 307M)](punctuation-restoration-base.md) (**Synthesis**).[^auroraasr-card]
- Excluded from the realtime shortlist in [Phân nhóm ASR/STT và shortlist realtime](realtime-asr-selection.md) because its documented interface is offline full-utterance decoding only (**Synthesis**).[^auroraasr-card]

## Coverage and limits

- **Coverage ledger:** the single entry point `raw/AuroraAI-Research-AuroraASR-1M.md` (6,299 bytes) was read in full and statically inspected. It is a flattened Hugging Face model card: frontmatter, prose, three tables, one code fence, and the training-methodology list. There is no package root, include, attachment, or linked local artifact to reconcile — the card's external links (`huggingface.co/igorktech/femto-asr`, `nvidia/stt_en_citrinet_256_ls`, `UsefulSensors/moonshine-tiny`, `openai/whisper-tiny.en`, `openai/whisper-tiny`, and the model repository itself) are URLs, not captured files, and were not fetched (**Observed**).[^auroraasr-card]
- **Not inspected:** model repository code and `trust_remote_code` Python, tokenizer files, weights or their hashes, training scripts, evaluation logs, license text, and every competitor card and paper behind the WER table. No generated, cached, or vendored material exists in this capture to exclude.[^auroraasr-card]
- **Not executed:** no installation, weight download, inference, or benchmark run; the WER, RTF, precision-size, and training-cost figures are all the card's own and are **Reported**, not **Reproduced**. The only independent checks performed are arithmetic on the card's published numbers (**Observed**) (**Synthesis**).[^auroraasr-card]
- **Open unknowns:** release date, revision, intended use, author identity, per-precision WER, elapsed-time or latency percentiles, streaming feasibility, noise robustness, language-model attachment point, and whether the weight-sharing and Muon choices were ablated (**Observed** from the capture's silences).[^auroraasr-card]

[^auroraasr-card]: [AuroraASR-1M model card capture](../raw/AuroraAI-Research-AuroraASR-1M.md) — locators: frontmatter (`library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, `tags` incl. `ctc`/`conformer`/`custom_code`, `language: en`, `datasets: librispeech_asr`, `license: apache-2.0`); intro paragraph (four unique blocks applied twice, 256-piece BPE, 379 epochs, English only, 16 kHz mono, greedy CTC, no external LM, under 1M parameters); section `Word error rate (LibriSpeech, greedy decoding)` (6-row table, competitor attribution note); paragraph `Quantization` ("nearly lossless ... all the way down to INT8 weight-only", figures are FP32); section `Speed (FP32, full end-to-end pipeline)` (RTF definition, batch 1, 100 `test-clean` utterances / 13.3 min, GPU and pinned-CPU rows); section `Usage` (Python fence with `trust_remote_code`, FP16/INT8 subfolder comments, `transcribe(wav)[0]`, `torch`/`transformers`/`sentencepiece`); section `Precisions` (FP32 3.81 MB root, FP16 1.91 MB, INT8 1.06 MB, per-output-channel scales, on-the-fly dequantization, "does not make the arithmetic faster"); section `Training methodology` → `Data` (LibriSpeech 960 h, 1 s/16 s and token-to-frame filters, `dev-clean` selection, held-out test sets), `Text and tokenization` (lowercase `a-z`/apostrophe/space, 256-piece SentencePiece on training transcripts, 257 CTC classes), `Features` (80-bin log-mel, 25 ms/10 ms, 512 FFT, 20 Hz–8 kHz, per-utterance mean/variance), `Architecture` (4× stem, four blocks × two passes, width 128, 4 heads with rotary embeddings, FFN 384, kernel 15, 949,073 parameters), `Objective` (0.7 final + 0.3 auxiliary CTC, shared LayerNorm/output, token-normalized), `Optimization` table (Muon and AdamW settings, warmup/cosine, clipping, 2,400 s dynamic batches, SortaGrad, bf16/TF32/`torch.compile`, EMA 0.9995, SpecAugment, dropout 0, seed 0), and the closing schedule paragraph (200-step calibration, 379 epochs, ~10 h on an RTX Pro 6000); `Evaluation protocol` (greedy collapse-and-blank decoding, no LM, normalized word-level edit distance, normalization comparability caveat, no augmentation or external data).
