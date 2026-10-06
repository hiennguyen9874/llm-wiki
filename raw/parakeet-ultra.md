---
license: cc-by-4.0
language: [en, de, fr, es, it, pt, ru, uk, hr, sl, lv, lt, et, fi, sv, da, nl, pl, cs, sk, hu, ro, bg, el, mt]
pipeline_tag: automatic-speech-recognition
tags: [parakeet, tdt, speech-recognition]
---

# Moondream Parakeet Ultra

A post-trained version of [parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3). Same
architecture, same tokenizer, same 0.6B parameters in full precision. It is better than the original on every
benchmark group below, by a wide margin on the 25-language FLEURS set, in background noise and on long-form audio,
and it runs faster than the original does in NeMo.

| | parakeet-tdt-0.6b-v3 | parakeet-ultra |
|---|---|---|
| Open ASR Leaderboard, 7 English sets (WER %) | 6.26 | **5.80** |
| FLEURS, 25 languages (WER %) | 11.62 | **9.55** |
| Business speech, AA-WER style (WER %) | 6.15 | **5.79** |
| Background noise, 9 MUSAN conditions (WER %) | 6.72 | **5.82** |
| TED-LIUM long-form (WER %) | 2.71 | **1.94** |

Its sibling [Parakeet Redux](https://huggingface.co/moondream/parakeet-redux) is the ternary version of the same
architecture, 178 MB, built for CPUs and Apple silicon. Read the
[release post](https://moondream.ai/blog/introducing-parakeet-redux-and-ultra) for the story behind both models.

## Usage

Run it with [Photon](https://moondream.ai/photon). Every accuracy number on this page is Photon on an NVIDIA GPU.

```python
# pip install moondream
import moondream as md

with md.photon("moondream/parakeet-ultra") as speech:
    result = speech.transcribe(audio="speech.wav")
    print(result["text"])

    # timestamps="segment": one entry per sentence, with its start
    # and end in seconds; "word" adds the start and end of every word
    result = speech.transcribe(audio="speech.wav", timestamps="word")
    for segment in result["segments"]:
        print(segment["start"], segment["end"], segment["text"])
        for word in segment["words"]:
            print(word["start"], word["end"], word["word"])
```

## Performance

Real-time factor: seconds of audio transcribed per second of wall clock, higher is faster. One NVIDIA B200, 128
requests in flight, the same files on both sides; NeMo 3.0 runs the original checkpoint with its own transcribe
call at batch 128, Photon runs parakeet-ultra.

| | NeMo, parakeet-tdt-0.6b-v3 | Photon, parakeet-ultra |
|---|---|---|
| LibriSpeech test-clean, 2,620 utterances, 5.4 hours | 6,005× | **9,743×** |
| AMI test, 12,643 utterances, 8.7 hours | 4,394× | **6,688×** |

## Benchmarks

Word error rate in percent, lower is better. Both models are scored on the same files with the Open ASR
Leaderboard's own pipeline as of September 2026 (its normalizers and compound-merging alignment, with the FLEURS
references prepared as the leaderboard's text column is). parakeet-ultra runs in Photon on an NVIDIA GPU, the
original in NeMo in bf16.

### Open ASR Leaderboard

The seven English test sets of the Hugging Face Open ASR Leaderboard: audiobooks (LibriSpeech), meetings (AMI),
earnings calls (Earnings-22), podcasts and YouTube (GigaSpeech), financial calls (SPGISpeech) and parliament
(VoxPopuli).

| set | parakeet-tdt-0.6b-v3 | parakeet-ultra |
|---|---|---|
| LibriSpeech test-clean | 1.52 | 1.41 |
| LibriSpeech test-other | 3.13 | 2.98 |
| AMI | 10.86 | 9.77 |
| Earnings-22 | 10.75 | 9.76 |
| GigaSpeech | 8.05 | 7.71 |
| SPGISpeech | 3.63 | 3.34 |
| VoxPopuli | 5.88 | 5.65 |
| **average** | **6.26** | **5.80** |

### FLEURS

The FLEURS test split: read Wikipedia sentences, a few hundred per language, for all 25 languages the model
supports.

| language | parakeet-tdt-0.6b-v3 | parakeet-ultra |
|---|---|---|
| Bulgarian | 11.90 | 10.09 |
| Croatian | 10.93 | 9.65 |
| Czech | 10.85 | 9.97 |
| Danish | 16.78 | 14.31 |
| Dutch | 6.18 | 5.46 |
| English | 4.25 | 3.55 |
| Estonian | 13.23 | 9.69 |
| Finnish | 11.05 | 9.19 |
| French | 4.81 | 4.32 |
| German | 4.13 | 3.61 |
| Greek | 35.71 | 32.25 |
| Hungarian | 13.65 | 10.76 |
| Italian | 2.61 | 2.00 |
| Latvian | 21.38 | 15.95 |
| Lithuanian | 21.09 | 16.36 |
| Maltese | 19.13 | 14.92 |
| Polish | 6.70 | 5.54 |
| Portuguese | 4.65 | 3.96 |
| Romanian | 11.54 | 9.18 |
| Russian | 5.91 | 5.21 |
| Slovak | 9.46 | 7.03 |
| Slovene | 21.76 | 16.64 |
| Spanish | 3.12 | 2.72 |
| Swedish | 13.75 | 11.57 |
| Ukrainian | 5.94 | 4.75 |
| **average** | **11.62** | **9.55** |

### Business speech (AA-WER style)

The AMI and VoxPopuli test sets with the Artificial Analysis cleaning applied, and Earnings-22 scored in 30-second
chunks joined per call, the way the AA-WER benchmark does it.

| set | parakeet-tdt-0.6b-v3 | parakeet-ultra |
|---|---|---|
| AMI (cleaned) | 9.52 | 8.48 |
| VoxPopuli (cleaned) | 3.02 | 3.10 |
| Earnings-22, 30-second chunks | 5.90 | 5.78 |
| **average** | **6.15** | **5.79** |

### Background noise

The clean sets with MUSAN noise (the half of the corpus not used for training) mixed in at a fixed signal-to-noise
ratio; 0 dB means the noise is as loud as the speech.

| set | parakeet-tdt-0.6b-v3 | parakeet-ultra |
|---|---|---|
| LibriSpeech test-other, 10 dB | 4.12 | 3.87 |
| LibriSpeech test-other, 5 dB | 5.49 | 5.10 |
| LibriSpeech test-other, 0 dB | 9.06 | 8.31 |
| FLEURS German, 10 dB | 5.78 | 4.98 |
| FLEURS German, 5 dB | 8.07 | 6.91 |
| FLEURS German, 0 dB | 14.45 | 12.08 |
| FLEURS Spanish, 10 dB | 3.99 | 3.13 |
| FLEURS Spanish, 5 dB | 4.12 | 3.38 |
| FLEURS Spanish, 0 dB | 5.44 | 4.64 |
| **average** | **6.72** | **5.82** |

### Long-form

Eleven complete TED-LIUM 3 talks of 10-20 minutes each. parakeet-ultra transcribes them through Photon, whose
segmenter cuts each talk at pauses found by the model's VAD head into segments of at most 30 seconds; the original
runs NeMo's own long-audio path.

| set | parakeet-tdt-0.6b-v3 | parakeet-ultra |
|---|---|---|
| TED-LIUM 3, 11 full talks of 10-20 minutes | 2.71 | 1.94 |

## Notes

- Based on [parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) by NVIDIA. Languages,
  tokenizer and output conventions (punctuation, casing, numerals) are the original's.
- Runs with [Photon](https://moondream.ai/photon).
- Long audio is segmented by the model itself: the weights carry a small voice-activity head on the encoder's
  subsampler, and Photon uses it to cut recordings at pauses into segments of at most 30 seconds. No external VAD
  model is needed.
- License is CC-BY-4.0, same as the original.
