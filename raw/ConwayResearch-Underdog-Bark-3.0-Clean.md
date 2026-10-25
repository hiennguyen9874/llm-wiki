---
license: cc-by-4.0
base_model: nvidia/parakeet-tdt-0.6b-v3
base_model_relation: finetune
language:
- en
library_name: transformers
pipeline_tag: automatic-speech-recognition
tags:
- speech-to-text
- asr
- stt
- dictation
- disfluency-removal
- low-bit
- on-device
- mlx
- apple-silicon
- parakeet
- underdog
metrics:
- wer
---

# Underdog Bark 3.0 Clean

**Underdog Bark 3.0 Clean is the clean version of [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus)**: a 0.6B English speech recognition model in a **180 MB download**, with speech cleanup built in. It drops "um" and "uh", filler phrases like "you know" and "I mean", false starts and repeated words, turning spoken thoughts into ready-to-use text without a second cleanup model.

Its foundation, **[Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus)**, averages **4.76% word error** across the Open ASR Leaderboard's seven English sets—better than Parakeet TDT 0.6B v3 (4.94%), Qwen3-ASR-0.6B (5.16%) and Whisper large-v3 (6.04%) in the published comparison, at a fraction of their download sizes. Plus reaches 7.76% on meetings (AMI) and 1.92% on parliamentary speech (VoxPopuli). Clean builds on Plus for dictation and readable transcripts rather than preserving every hesitation.

**Clean reaches 4.08% WER against cleaned [DisfluencySpeech](https://arxiv.org/abs/2406.08820) transcripts**, and matches Plus's 1.71% on LibriSpeech clean, with 3.78% on LibriSpeech other. These are Clean's results; the 4.76% seven-set average above belongs to Plus, the verbatim model.

It is the speech model in [Underdog](https://underdog.ai), where it turns what you say into text for Speak and for meeting notes, on your Mac or iPhone. Your audio never leaves the device.

![Bark family: reported verbatim speech recognition accuracy versus model download size](bark_frontier.png)

*The Bark family's accuracy–size comparison for verbatim transcription. [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus) is the foundation of Clean; this chart shows Plus, Pro and the standard model, not Clean's cleanup scores. See the separate Clean and family benchmark tables below.*

## Highlights

- The clean version of [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus): the same 180 MB download class, with built-in disfluency removal for dictation and notes.
- Built-in cleanup: no "um", no false starts, no second model to clean up after it.
- More accurate than [Bark 2.0](https://huggingface.co/ConwayResearch/bark-0.6B-4bit-v2.0) on all seven Open ASR Leaderboard English sets (5.83 % against 7.48 %), from a download less than half the size.
- As accurate as the verbatim [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus) on clean read speech (1.71 % on LibriSpeech clean).
- Small enough for a phone: 180 MB to download, 1.25 GB in memory once unpacked.

## Benchmarks

### Cleanup

[DisfluencySpeech](https://arxiv.org/abs/2406.08820) test set (250 clips of unscripted conversation), word error rate (%), lower is better. Fillers count as errors.

| Model | Download | Against cleaned transcripts | Against verbatim transcripts |
|---|--:|--:|--:|
| **Bark 3.0 Clean** | **180 MB** | 4.08 | 13.85 |
| [Bark 2.0](https://huggingface.co/ConwayResearch/bark-0.6B-4bit-v2.0) | 472 MB | **3.83** | 13.01 |
| Bark 3.0 (verbatim) | 163 MB | 16.53 | **3.15** |

A cleanup model should score low in the first column. A verbatim model scores low in the second.

### Ordinary speech

| Model | Download | LS clean | LS other | AMI | Earnings-22 | GigaSpeech | SPGISpeech | VoxPopuli | Average |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| **Bark 3.0 Clean** | **180 MB** | **1.71** | **3.78** | **12.12** | **8.55** | **9.76** | **2.66** | **2.23** | **5.83** |
| [Bark 2.0](https://huggingface.co/ConwayResearch/bark-0.6B-4bit-v2.0) | 472 MB | 2.94 | 5.21 | 16.16 | 11.08 | 10.56 | 3.47 | 2.90 | 7.48 |

Word error rate (%) on the full test sets of the Open ASR Leaderboard's seven English sets, scored with its code. Their references are verbatim, so every filler or repeat that Bark 3.0 Clean removes on purpose counts against it on AMI, GigaSpeech and Earnings-22. For verbatim transcription, use Bark 3.0 (4.94) or [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus) (4.76).

### The Plus foundation: accuracy in a small download

Clean comes from [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus). The table below reproduces the family's reported **verbatim-recognition** results and selected baselines, showing the accuracy and compact size behind the Clean version. Clean's own seven-set result is **5.83%**, as shown above; cleanup deliberately changes the output style.

| Model | Download | LS clean | LS other | AMI | Earnings-22 | GigaSpeech | SPGISpeech | VoxPopuli | Average |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| [Bark 3.0 Pro](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Pro) | 1,254 MB | 1.38 | 3.11 | 7.16 | 5.65 | 7.46 | 3.54 | 1.70 | 4.29 |
| **[Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus)** | **180 MB** | 1.71 | 3.82 | 7.76 | 6.70 | 7.77 | 3.64 | 1.92 | 4.76 |
| Bark 3.0 | 163 MB | 1.89 | 4.08 | 7.82 | 7.05 | 7.95 | 3.72 | 2.05 | 4.94 |
| Phonon-2† | 164 MB | 1.73 | 3.92 | 9.32 | 6.96 | 8.35 | 3.70 | 2.46 | 5.21 |
| Parakeet TDT 0.6B v3† | 2,508 MB | 1.52 | 3.13 | 9.42 | 5.85 | 7.99 | 3.63 | 3.05 | 4.94 |
| Qwen3-ASR-0.6B† | 1,876 MB | 1.70 | 4.01 | 9.33 | 7.83 | 7.62 | 2.74 | 2.90 | 5.16 |
| Whisper large-v3† | 9,261 MB | 1.56 | 3.52 | 13.63 | 7.99 | 8.35 | 2.71 | 4.53 | 6.04 |
| Whisper large-v3-turbo† | 1,618 MB | 2.13 | 3.71 | 13.88 | 8.09 | 8.47 | 2.79 | 7.02 | 6.58 |

WER (%), lower is better, on the full test sets of the seven English datasets used by the [Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard), including its cleaned versions of AMI, Earnings-22, GigaSpeech and VoxPopuli. Average is the seven-set mean. † Published leaderboard results as of 9 October 2026; the Bark rows use its scoring code and were reported separately, not submitted leaderboard entries. Download sizes are weight-file sizes, not runtime memory. These figures reproduce the Plus model card's comparison and are not a new evaluation of this Clean release.

## In Underdog

Underdog runs this file as it is, with no Python. A native Swift runtime reads `model.bark`, unpacks it in memory in about 2 seconds on Apple silicon, and runs the model on MLX. The unpacked weights are bit-identical to what `bark_loader.py` produces. Underdog downloads two files, `model.bark` and `mlx/config.json`, and checks each against a pinned size and SHA-256 before using it.

On an M5 Max, a 136-second recording transcribes in about 4 seconds, model load included.

## Run it yourself

```bash
pip install "transformers>=5.19" torch constriction numpy soundfile soxr
python bark_loader.py model.bark recording.wav
```

```python
from bark_loader import load_model, transcribe
import soundfile as sf

model = load_model("model.bark", device="cuda")          # or "cpu", "mps"
wave, sr = sf.read("recording.wav", dtype="float32", always_2d=True)
print(transcribe(model, wave.mean(1), sr))
```

On Apple silicon with MLX:

```bash
pip install mlx mlx-audio constriction numpy soundfile soxr
python bark_mlx.py recording.wav
```

The first run unpacks the weights into an MLX folder and caches it. Unpacking is exact: the weights you load are the weights that were measured. Bark 3.0 Clean was measured with no silence added before the audio, which is what `transcribe` does.

## Files

| File | What it is |
|---|---|
| `model.bark` | The weights, entropy coded (format `bark-levels-v3`) |
| `mlx/config.json` | Model configuration and vocabulary |
| `mlx/tokenizer.*`, `mlx/vocab.txt` | Tokenizer files for mlx-audio |
| `bark_loader.py` | Unpacks `model.bark` into a transformers `ParakeetForTDT` |
| `bark_mlx.py` | Unpacks `model.bark` into an mlx-audio Parakeet folder |

## Notes

Based on parakeet-tdt-0.6b-v3 by NVIDIA, through moondream/parakeet-ultra and [Bark 3.0 Plus](https://huggingface.co/ConwayResearch/Underdog-Bark-3.0-Plus); the tokenizer and output conventions (punctuation, casing, numerals) are the original's. Licence CC-BY-4.0, same as the original; `NOTICE` lists the attribution. English only.
