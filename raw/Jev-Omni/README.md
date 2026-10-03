---
license: apache-2.0
base_model: google/gemma-4-12B-it
library_name: transformers
model_name: Jev-Omni
tags: [text-classification, multimodal, merged]
---
# Jev-Omni

A multimodal decision classifier for **text, images, audio and video**. Supply a question and options; receive a probability for each option—not a generated explanation.

Built on Gemma 4 12B IT, with a 30,000-question fine-tuning run.

## Results

| Benchmark | Accuracy¹ | Micro accuracy |
|---|---:|---:|
| DecisionBench Medium · 80 scenarios / 293 questions | **87.57%** | 86.01% |
| JevBench · matched 195 groups / 231 decisions | **86.15%** | 87.45% |
| MMAU · 1,000 questions | — | **63.10%** |
| MVBench · 14 evaluated tasks / 2,786 questions | **53.10%** | 53.09% |

Merged-model results. ¹Equal-weight scenario/group average.

### Open-weight comparison

| Model | Parameters | MMAU | MVBench | Modalities |
|---|---:|---:|---:|---|
| **Jev-Omni** | 12B | **63.10%** | **53.10%** | Text, image, audio, video |
| [Inkling](https://huggingface.co/thinkingmachines/Inkling) | 975B total / 41B active | 77.20% | — | Text, image, audio |
| [Qwen3.5-397B-A17B](https://huggingface.co/Qwen/Qwen3.5-397B-A17B) | 397B total / 17B active | — | 77.60% | Text, image, video |

Reference scores are officially reported by their developers and may use different evaluation protocols.

![DecisionBench Medium accuracy](assets/medium-accuracy.png)

Jev-Omni cost uses its recorded input tokens at OpenRouter's Gemma 3 12B input rate ($0.05/M); its classifier generates no output tokens.

Both classifiers are priced **one call per question**: a classifier answers one question at a time, so the state is re-sent for each of them and there is no discount for asking several at once. The three chat models are priced one call per state, with all of that state's questions together, which is their own cheapest shape. Splitting a state into per-question calls multiplies input tokens by 2.82x on this set, so pricing the chat models the same way would move all three marks right by roughly that factor without changing the order.

[DecisionBench dataset](https://huggingface.co/datasets/akhilaaa3/decision-bench)

## Quick start

CUDA GPU required. FP32 weights use about 50 GB before runtime overhead; inference uses BF16 autocast.

```bash
pip install -r https://huggingface.co/akhilaaa3/Jev-Omni/resolve/main/requirements.txt
# ffmpeg is also required for audio input
```

File: [`requirements.txt`](./requirements.txt)

```python
from huggingface_hub import snapshot_download

path = snapshot_download("akhilaaa3/Jev-Omni")
import sys; sys.path.insert(0, path)
from jev_omni import load_jev_omni

classifier = load_jev_omni()
result = classifier.predict(
    state="The meeting starts at 10 AM. It is now 9 AM.",
    question="Has the meeting started?",
    options=["Yes", "No"],
)
print(result)
```

For an image, audio file or video, add `media="/path/to/file"` and `modality="image"`, `"audio"` or `"video"`. The loader downloads the original Gemma 4 multimodal components automatically. Audio is capped at 30 seconds; video uses 16 frames.

## Speed

Warm H200 inference: **83 ms** (~2k-token text), **26 ms** (image), **31 ms** (13-second audio), **504 ms** (16-frame video). Medians over 20 optimized-backend requests; preprocessing and network time are extra.

## Limits

Best supported at **≤20 options**. The head accepts 256, but quality above 20 is not established.

## License

**Apache-2.0**, following [Gemma 4](https://huggingface.co/google/gemma-4-12B-it). Dataset rights remain separate.

## Calibration

Medium ECE: **0.0400** (10 bins; lower is better). The graph uses five bins for readability.

![DecisionBench Medium calibration](assets/medium-calibration.png)

---

<small>Note: Jev-Omni is an independent open model that implements the typed-decision interface — noul (yes/no), choice and score questions answered with calibrated probabilities. It is not affiliated with, endorsed by, sponsored by, or derived from TypeSafe AI or its Jev model, and nothing in it was trained on Jev output.</small>
