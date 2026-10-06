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
  - meanflow
  - distillation
  - low-latency
library_name: dots_tts
base_model: dots-studio/dots.tts-soar
---

# dots.tts-mf

<p align="left">
  <a href="https://github.com/studio-dots-ai/dots.tts"><img src="https://img.shields.io/badge/GitHub-studio--dots--ai%2Fdots.tts-blue?logo=github" alt="GitHub"></a>
  <a href="https://huggingface.co/spaces/dots-studio/dots.tts"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Spaces-Playground-orange" alt="Playground"></a>
  <a href="https://studio-dots-ai.github.io/dots.tts-demo/"><img src="https://img.shields.io/badge/Demo%20Page-Live-red" alt="Demo Page"></a>
</p>

**dots.tts** is a **2B-parameter fully continuous, end-to-end autoregressive (AR) text-to-speech system**. The backbone pairs a semantic encoder, an LLM, and an autoregressive flow-matching acoustic head over a 48 kHz AudioVAE — no discrete codec tokens anywhere in the pipeline.

This repository hosts **`dots.tts-mf`** — the **CFG-aware MeanFlow distillation** of `dots.tts-soar`. MeanFlow collapses the per-patch ODE to **as few as 2–4 NFE** with a **single model evaluation per step** (CFG is fused into the student — no separate unconditional pass, and `guidance_scale` has no effect at inference time). This is the **recommended checkpoint for low-latency / few-step inference**.

<table>
  <tr>
    <td align="left" valign="middle"><a href="https://huggingface.co/dots-studio/dots.tts-base"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-dots.tts--base-yellow" alt="dots.tts-base"></a></td>
    <td>Pretrain (~1.5M h). Fine-tuning, full CFG / NFE control.</td>
  </tr>
  <tr>
    <td align="left" valign="middle"><a href="https://huggingface.co/dots-studio/dots.tts-soar"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-dots.tts--soar-yellow" alt="dots.tts-soar"></a></td>
    <td>+ Self-corrective Alignment. Highest zero-shot fidelity and speaker similarity; also recommended for fine-tuning.</td>
  </tr>
  <tr>
    <td align="left" valign="middle"><a href="https://huggingface.co/dots-studio/dots.tts-mf"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-dots.tts--mf-yellow" alt="dots.tts-mf"></a></td>
    <td>← <em>you are here</em> — + MeanFlow distillation. <strong>Few-step inference (NFE = 4), low latency</strong>.</td>
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
# Few-step inference — NFE = 4 is the recommended quality / latency trade-off.
# Note: --guidance-scale is a no-op on this checkpoint (CFG is fused into the
# distilled student); leave it at the CLI default or set it to anything.
dots.tts \
  --model-name-or-path dots-studio/dots.tts-mf \
  --text "Hello, this is a zero-shot voice cloning demonstration." \
  --prompt-audio /path/to/reference.wav \
  --prompt-text "The exact transcript of the reference audio." \
  --num-steps 4 \
  --output clone.wav
```

### Python API

```python
from dots_tts.runtime import DotsTtsRuntime
import soundfile as sf

runtime = DotsTtsRuntime.from_pretrained(
    "dots-studio/dots.tts-mf",
    precision="bfloat16",
)

result = runtime.generate(
    text="Hello, this is a quick speech synthesis test.",
    prompt_audio_path="/path/to/reference.wav",
    prompt_text="The exact transcript of the reference audio.",
    num_steps=4,           # NFE = 4 is the recommended setting
    # guidance_scale is a no-op on dots.tts-mf — CFG is fused into the student
)

sf.write("output.wav", result["audio"].float().cpu().squeeze().numpy(), result["sample_rate"])
```

### Recommended sampling settings

| Flag | Recommended | Notes |
|---|---:|---|
| `--num-steps` | `4` | NFE = 4 is the recommended quality / latency trade-off; NFE = 2 / 3 work but regress on WER / SIM (see table below) |
| `--guidance-scale` | *ignored* | CFG is fused into the distilled student; this flag is a no-op here |

---

## Architecture

A frozen **AudioVAE** encodes 48 kHz mono waveform into a continuous latent and decodes it back via a BigVGAN-style causal decoder. An **autoregressive backbone** predicts that latent one patch at a time:

- **Semantic encoder** — re-encodes each newly generated VAE patch into a compact embedding for the LLM, stripping high-variance acoustic detail.
- **LLM** — initialized from **Qwen2.5-1.5B-Base**, consumes BPE text directly (no phonemes), emits one hidden state per audio step.
- **AR flow-matching head** — a DiT that conditions on the LLM hidden state and the AR prefix to denoise the next VAE patch, with a frozen CAM++ speaker x-vector as side input.

**CFG-aware MeanFlow distillation** trains the flow-matching head as a MeanFlow student over the SCA teacher's velocity field, with classifier-free guidance directly absorbed into the student. The result is a 2–4 NFE sampler that retains the bulk of the teacher's quality with a single model evaluation per step.

---

## Performance — `dots.tts-mf`

### Seed-TTS-Eval (zero-shot, ~3 s reference)

| Model | NFE | test-en WER↓ / SIM↑ | test-zh WER↓ / SIM↑ | test-zh-hard WER↓ / SIM↑ | **Avg WER↓ / SIM↑** |
|---|:---:|:---:|:---:|:---:|:---:|
| dots.tts-soar (teacher) | 10 | 1.30 / **77.1** | **0.94** / **81.0** | **6.60** / **79.5** | 2.95 / **79.2** |
| **dots.tts-mf** | **4** | **1.29** / 76.2 | **0.94** / 80.0 | **6.60** / 78.5 | **2.94** / 78.2 |
| **dots.tts-mf** | **3** | 1.41 / 75.9 | 1.02 / 79.9 | 7.19 / 78.6 | 3.21 / 78.1 |
| **dots.tts-mf** | **2** | 1.51 / 75.2 | 1.04 / 79.1 | 7.74 / 76.7 | 3.43 / 77.0 |

At NFE = 4, `dots.tts-mf` essentially matches its teacher on average WER (2.94 vs. 2.95) with **~2.5× fewer model evaluations per patch** and a single conditional pass per step.

### CV3-Eval

| Model | NFE | hard-en WER↓ |
|---|:---:|:---:|
| Fish-Audio S2 | — | 4.40 |
| dots.tts-soar | 10 | 4.49 |
| **dots.tts-mf** | **4** | **4.37** |

See the [project README](https://github.com/studio-dots-ai/dots.tts#-performance) for full benchmark tables including MiniMax Multilingual and EmergentTTS-Eval.

---

## Risks and Limitations

- **Misuse risk.** High-fidelity zero-shot voice cloning can produce highly realistic synthetic speech. This checkpoint is intended for research and authorized deployment. Do **not** use it for impersonation, fraud, or disinformation. Combine downstream use with consent-aware reference-audio policies, robust synthetic-speech detection, and content watermarking. Clearly mark AI-generated audio.
- **Few-step trade-off.** At NFE = 2/3 there is a measurable WER and SIM regression vs. NFE = 4 (see table above). Pick the NFE that matches your latency budget.
- **CFG fused.** Unlike `base` / `soar`, `--guidance-scale` is ignored by the MeanFlow sampler — guidance is baked into the student at distillation time and cannot be adjusted at inference.
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
