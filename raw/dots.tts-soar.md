---
license: apache-2.0
pipeline_tag: text-to-speech
tags:
  - text-to-speech
  - tts
  - audio
  - speech-synthesis
  - voice-cloning
  - autoregressive
  - flow-matching
  - post-trained
library_name: dots_tts
base_model: dots-studio/dots.tts-base
---

# dots.tts-soar

<p align="left">
  <a href="https://github.com/studio-dots-ai/dots.tts"><img src="https://img.shields.io/badge/GitHub-studio--dots--ai%2Fdots.tts-blue?logo=github" alt="GitHub"></a>
  <a href="https://huggingface.co/spaces/dots-studio/dots.tts"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Spaces-Playground-orange" alt="Playground"></a>
  <a href="https://studio-dots-ai.github.io/dots.tts-demo/"><img src="https://img.shields.io/badge/Demo%20Page-Live-red" alt="Demo Page"></a>
</p>

**dots.tts** is a **2B-parameter fully continuous, end-to-end autoregressive (AR) text-to-speech system**. The backbone pairs a semantic encoder, an LLM, and an autoregressive flow-matching acoustic head over a 48 kHz AudioVAE — no discrete codec tokens anywhere in the pipeline.

This repository hosts **`dots.tts-soar`** — the pretrained backbone further refined with **Self-corrective Alignment (SCA)**, a reward-free flow-matching-native post-training stage. SCA pushes the model to the **highest zero-shot fidelity and speaker similarity** of the three releases and is the **recommended default for production zero-shot voice cloning**.

<table>
  <tr>
    <td align="left" valign="middle"><a href="https://huggingface.co/dots-studio/dots.tts-base"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-dots.tts--base-yellow" alt="dots.tts-base"></a></td>
    <td>Pretrain (~1.5M h). Fine-tuning, full CFG / NFE control.</td>
  </tr>
  <tr>
    <td align="left" valign="middle"><a href="https://huggingface.co/dots-studio/dots.tts-soar"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-dots.tts--soar-yellow" alt="dots.tts-soar"></a></td>
    <td>← <em>you are here</em> — + Self-corrective Alignment. <strong>Highest zero-shot fidelity and speaker similarity</strong>; also recommended for fine-tuning.</td>
  </tr>
  <tr>
    <td align="left" valign="middle"><a href="https://huggingface.co/dots-studio/dots.tts-mf"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-dots.tts--mf-yellow" alt="dots.tts-mf"></a></td>
    <td>+ MeanFlow distillation. Few-step inference (NFE = 4), low latency.</td>
  </tr>
</table>

---

## Quick Start

### Installation

```bash
conda create -n dots_tts python=3.10 -y
conda activate dots_tts

python -m pip install --upgrade pip
python -m pip install "git+https://github.com/studio-dots-ai/dots.tts.git" \
  -c "https://raw.githubusercontent.com/studio-dots-ai/dots.tts/main/constraints/recommended.txt"
```

### CLI

```bash
# Continuation voice cloning (reference audio + transcript) — recommended
dots.tts \
  --model-name-or-path dots-studio/dots.tts-soar \
  --text "Hello, this is a zero-shot voice cloning demonstration." \
  --prompt-audio /path/to/reference.wav \
  --prompt-text "The exact transcript of the reference audio." \
  --output clone.wav
```

### Python API

```python
from dots_tts.runtime import DotsTtsRuntime
import soundfile as sf

runtime = DotsTtsRuntime.from_pretrained(
    "dots-studio/dots.tts-soar",
    precision="bfloat16",
)

result = runtime.generate(
    text="Hello, this is a quick speech synthesis test.",
    prompt_audio_path="/path/to/reference.wav",
    prompt_text="The exact transcript of the reference audio.",
    num_steps=10,
    guidance_scale=1.2,
)

sf.write("output.wav", result["audio"].float().cpu().squeeze().numpy(), result["sample_rate"])
```

### Recommended sampling settings

| Flag | Recommended | Notes |
|---|---:|---|
| `--num-steps` | `10`–`32` | Flow-matching sampling steps; higher = better quality, slower |
| `--guidance-scale` | `1.2` (default) | Standard CFG; SCA already tightens text and timbre adherence so small CFG suffices |

### Fine-tuning

Both `dots.tts-base` and `dots.tts-soar` are valid fine-tuning starting points. Pick `dots.tts-soar` when you want to inherit its tightened text/timbre alignment on top of the pretrained backbone. See the [training script](https://github.com/studio-dots-ai/dots.tts/blob/main/scripts/train_dots_tts.py) and [smoke config](https://github.com/studio-dots-ai/dots.tts/blob/main/configs/dots_tts.yaml) in the source repository:

```bash
accelerate launch scripts/train_dots_tts.py --config configs/dots_tts.yaml
```

---

## Architecture

A frozen **AudioVAE** encodes 48 kHz mono waveform into a continuous latent and decodes it back via a BigVGAN-style causal decoder. An **autoregressive backbone** predicts that latent one patch at a time:

- **Semantic encoder** — re-encodes each newly generated VAE patch into a compact embedding for the LLM, stripping high-variance acoustic detail.
- **LLM** — initialized from **Qwen2.5-1.5B-Base**, consumes BPE text directly (no phonemes), emits one hidden state per audio step.
- **AR flow-matching head** — a DiT that conditions on the LLM hidden state and the AR prefix to denoise the next VAE patch, with a frozen CAM++ speaker x-vector as side input.

**Self-corrective Alignment** is a reward-free, flow-matching-native post-training stage applied on top of `dots.tts-base`. It improves text and speaker adherence without changing inference cost or sampling schedule.

---

## Performance — `dots.tts-soar`

### Seed-TTS-Eval — **state-of-the-art average SIM (79.2)**

| Model | Params | test-en WER↓ / SIM↑ | test-zh WER↓ / SIM↑ | test-zh-hard WER↓ / SIM↑ | **Avg WER↓ / SIM↑** |
|---|---:|:---:|:---:|:---:|:---:|
| Seed-TTS | — | 2.25 / 76.2 | 1.12 / 79.6 | 7.59 / 77.6 | 3.65 / 77.8 |
| Qwen3-TTS | 1.7B | **1.23** / 71.7 | 1.22 / 77.0 | 6.76 / 74.8 | 3.07 / 74.5 |
| VoxCPM 2 | 2B | 1.84 / 75.3 | 0.97 / 79.5 | 8.13 / 75.3 | 3.65 / 76.7 |
| dots.tts-base | 2B | 1.34 / 76.8 | 0.96 / 80.5 | **6.46** / 79.2 | **2.92** / 78.8 |
| **dots.tts-soar** | **2B** | 1.30 / **77.1** | **0.94** / **81.0** | 6.60 / **79.5** | 2.95 / **79.2** |

### MiniMax Multilingual — **highest average SIM (83.9) across 24 languages**

| Model | Avg WER↓ | Avg SIM↑ |
|---|:---:|:---:|
| MiniMax | **2.8** | 76.6 |
| Fish-Audio S2 | 3.7 | 78.0 |
| VoxCPM 2 | 5.7 | 82.3 |
| dots.tts-base | 6.6 | 83.5 |
| **dots.tts-soar** | 6.8 | **83.9** |

### CV3-Eval — **leads both cross-lingual SIM subsets**

| Model | en→zh SIM↑ | zh→en SIM↑ |
|---|:---:|:---:|
| CosyVoice 3 (1.5B) | 66.9 | 66.4 |
| dots.tts-base | 74.6 | 71.9 |
| **dots.tts-soar** | **75.0** | **72.8** |

### EmergentTTS-Eval — **top Syntactic Complexity in the table (65.7%)**

On head-to-head judging vs. `gpt-4o-mini-tts`, `dots.tts-soar` posts **65.7% on Syntactic Complexity — above every closed-source system listed**, while keeping competitive Emotions / Questions scores.

See the [project README](https://github.com/studio-dots-ai/dots.tts#-performance) for full benchmark tables.

---

## Risks and Limitations

- **Misuse risk.** High-fidelity zero-shot voice cloning can produce highly realistic synthetic speech. This checkpoint is intended for research and authorized deployment. Do **not** use it for impersonation, fraud, or disinformation. Combine downstream use with consent-aware reference-audio policies, robust synthetic-speech detection, and content watermarking. Clearly mark AI-generated audio.
- **Low-resource WER gap.** A BPE backbone inherits the text LLM's language coverage at the cost of a higher data appetite. On script-divergent and under-represented languages (Arabic, Hindi, Turkish, Vietnamese) WER is higher than on high-resource languages; speaker similarity is preserved.
- **Speech-heavy training.** The backbone is trained on a speech-heavy mixture. Singing and unified speech + sound generation are not covered.

---

## Citation

```bibtex
@article{dotstts2026,
  title   = {dots.tts Technical Report},
  author  = {dots.tts Team},
  journal = {arXiv preprint},
  year    = {2026},
}
```

## License

Released under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
