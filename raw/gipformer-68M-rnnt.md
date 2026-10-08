---
license: mit
language:
- vi
library_name: onnxruntime
tags:
- automatic-speech-recognition
- gipformer
- speech-to-text
- vietnamese
- rnnt
- rnn-transducer
- zipformer
- onnx
- int8
- quantized
- edge-ai
- edge-device
pipeline_tag: automatic-speech-recognition
metrics:
- wer
---

# Gipformer - Efficient Vietnamese Speech Recognition

**Demo:** [Try gipformer in your browser](https://huggingface.co/spaces/g-group-ai-lab/gipformer-demo)

## Highlights

- **State-of-the-art accuracy** — Demonstrates top-tier performance across major Vietnamese ASR benchmarks, delivering highly precise and reliable transcription quality.
- **Robust handling of telephonic domains** — Excels in processing challenging, noisy real-world call center recordings across all major Vietnamese regional accents.
- **Outstanding parameter efficiency** — Ranks among the smallest ASR models currently available.
- **Seamless edge deployment** — Its naturally low resource requirements enable ultra-fast inference on mobile and embedded systems, making it perfectly suited for offline, on-device applications.
- **Built-in data privacy** — By supporting full local execution, the model ensures sensitive audio data is processed securely on-device, eliminating the need for third-party cloud services.
- *gipformer-68M-rnnt* is based on Zipformer Transducer architecture.

## Benchmark Results

We evaluate gipformer-68M-rnnt against 12 established Vietnamese ASR models across 12 benchmarks spanning call center, medical, broadcast, read speech, etc. All numbers are **Word Error Rate (WER %) — lower is better**.

> **Normalization:** Both predictions and labels are normalized before computing WER — lowercased, punctuation removed, and numbers converted to spoken form.

| Model | Params | tele-medium | tele-diff-north | tele-diff-middle | tele-diff-south | MultiMED | VietMed | vlsp-t1 | vlsp-t2 | LSVSC | Fleurs | ViMD | vivos |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| vinai/PhoWhisper-small | 244M | 33.96 | 55.88 | 65.41 | 62.35 | 26.02 | 25.50 | 15.99 | 34.20 | 11.23 | 16.11 | 14.09 | 6.23 |
| vinai/PhoWhisper-medium | 769M | 26.46 | 51.20 | 59.04 | 55.39 | 24.76 | 24.90 | 14.06 | 26.38 | 10.25 | 14.44 | 11.34 | 4.93 |
| vinai/PhoWhisper-large | 1.5B | 26.82 | 50.39 | 59.44 | 56.70 | 24.47 | 24.37 | 13.70 | 27.45 | 10.08 | 12.62 | 11.18 | 4.73 |
| khanhld/chunkformer-large-vie | 110M | 27.60 | 46.30 | 51.91 | 49.09 | 22.60 | 19.59 | 14.09 | 25.81 | **8.85** | 14.17 | 11.77 | 4.18 |
| nguyenvulebinh/wav2vec2-base-vi | 95M | 23.71 | 40.49 | 48.90 | 46.33 | 23.03 | 22.96 | 13.14 | 37.33 | 9.89 | 20.09 | 11.42 | 6.60 |
| hynt/Zipformer-30M-RNNT-6000h | 30M | 19.95 | 38.77 | 45.19 | 43.89 | 19.85 | 19.93 | **11.76** | 28.63 | 9.12 | 13.16 | 7.28 | 4.60 |
| VietASR-zipformer | 68M | 20.30 | 42.21 | 49.01 | 47.86 | 22.05 | 21.90 | 14.54 | 31.18 | 10.23 | 14.76 | 10.15 | 6.92 |
| Qwen/Qwen3-ASR-1.7B | 1.7B | 26.34 | 46.80 | 59.85 | 51.84 | 20.11 | 20.21 | 16.29 | 34.26 | 9.64 | **10.13** | 11.16 | 7.17 |
| Qwen/Qwen3-ASR-0.6B | 600M | 32.29 | 48.57 | 61.88 | 55.43 | 22.65 | 22.51 | 18.62 | 43.44 | 10.96 | 13.11 | 14.37 | 10.23 |
| nvidia/parakeet-ctc-0.6b-Vietnamese | 600M | 31.82 | 55.33 | 61.65 | 56.70 | 23.79 | 23.53 | 17.00 | 37.94 | 10.46 | 16.11 | 12.95 | 7.76 |
| **g-group-ai-lab/gipformer-68M-rnnt** | **68M** | **15.53** | **25.10** | **32.27** | **32.62** | **19.35** | **19.41** | 13.39 | **20.40** | 8.96 | 12.92 | **7.17** | **4.12** |

### Rankings Summary

| Rank | Count | Benchmarks |
|:---:|:---:|:---|
| **#1** | **9 / 12** | tele-medium, tele-difficult-north, tele-difficult-middle, tele-difficult-south, MultiMED, VietMed, vlsp-2020-task-2, ViMD, vivos |
| #2 | 1 / 12 | LSVSC (8.96) |
| #3 | 2 / 12 | vlsp-2020-task-1 (13.39), Fleurs (12.92) |

<details>
<summary><b>Dataset Descriptions</b></summary>

**Private test sets (call center domain):**
- **tele-medium** — Call center recordings with medium difficulty
- **tele-difficult-north** — Low-quality call center audio, hard-to-hear speakers — Northern Vietnamese accent
- **tele-difficult-middle** — Low-quality call center audio, hard-to-hear speakers — Central Vietnamese accent
- **tele-difficult-south** — Low-quality call center audio, hard-to-hear speakers — Southern Vietnamese accent

**Public test sets:**
- **MultiMED** — Multi-domain medical conversations
- **VietMed** — Vietnamese medical domain
- **vlsp-2020-task-1** — VLSP 2020 ASR Shared Task 1
- **vlsp-2020-task-2** — VLSP 2020 ASR Shared Task 2
- **LSVSC** — Large-Scale Vietnamese Speech Corpus
- **Fleurs** — Google's Few-shot Learning Evaluation of Universal Representations of Speech (Vietnamese subset)
- **ViMD** — Vietnamese Multi-Domain
- **vivos** — Vietnamese read speech corpus

</details>

### Call Center Domain: Where It Matters Most

Call center ASR is one of the most challenging real-world domains — noisy phone lines, overlapping speech, diverse regional accents, and spontaneous conversation. gipformer-68M-rnnt delivers **dominant performance** across all call center test sets.

## Resources

- **Source code**: [github.com/ggroup-ai-lab/gipformer](https://github.com/ggroup-ai-lab/gipformer)
- **AI Skills**: [clawhub.ai/ai-ggroup/gipformer](https://clawhub.ai/ai-ggroup/gipformer)

## Usage

See the [Quick Start guide](https://github.com/ggroup-ai-lab/gipformer?tab=readme-ov-file#quick-start) for detailed usage instructions.

## Citation

```bibtex
@misc{gipformer,
  title={Gipformer - Efficient Vietnamese Speech Recognition},
  author={G-Group AI Lab},
  year={2026},
  url={https://huggingface.co/g-group-ai-lab/gipformer-68M-rnnt}
}
```

## License

This model is released under the [MIT License](LICENSE).

## Acknowledgments

Developed by **G-Group AI Lab**. For questions, issues, or collaboration inquiries, please visit our [HuggingFace organization page](https://huggingface.co/g-group-ai-lab).
