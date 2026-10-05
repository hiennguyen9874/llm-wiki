---
license: apache-2.0
base_model: Qwen/Qwen3.8-27B
base_model_relation: quantized
language:
- en
- zh
library_name: gguf
pipeline_tag: image-text-to-text
tags:
- gguf
- llama.cpp
- quantized
- qwen3.8
- qwen3.5
- ridge
- gated-deltanet
- imatrix
- reasoning
- multimodal
- vision
- mtp
- long-context
---

# Qwen3.8-27B-Ridge-3.7bpw

**Developed by [Empero](https://empero.org)**

A Gated-DeltaNet-aware mixed GGUF of official
**[Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B)** (`1d4bf0f2`)
for [llama.cpp](https://github.com/ggml-org/llama.cpp), Ollama, LM Studio,
jan, KoboldCpp, and other stock GGUF runtimes.

This is a quantization of the Qwen3.8-27B checkpoint. Ridge is a probed mix of types
written for this architecture: 64 layers =
16 × `(3 × GatedDeltaNet → FFN + 1 × GatedAttn → FFN)`. Generic `IQ2_XS`
and UD-IQ2 do not treat GDN state (`ssm_alpha` / `ssm_beta`) or
the GDN mixers as first-class. We fixed that.

Nothing was stripped to make the file fit. The native MTP draft head
(`blk.64` / `nextn`) stays in the GGUF. Vision is a separate BF16
`mmproj`.

> [!Note]
> This card is about choosing the file and running it. The official
> capability writeup lives on the
> **[base model card](https://huggingface.co/Qwen/Qwen3.8-27B)**.

---

## Files

The repository is `Qwen3.8-27B-Ridge-GGUF`. Use the exact filenames below
when downloading or passing `-m`.

| File | Quant | Size | Notes |
|---|---|---:|---|
| `Qwen3.8-27B-Ridge-3.7bpw.gguf` | Ridge mix, **3.69 bpw** | **11.73 GiB / 12.59 GB** | **this release** — text + native MTP |
| `mmproj-Qwen3.8-27B-BF16.gguf` | BF16 | 0.87 GiB / 0.93 GB | vision encoder + projector; **required for images** |

If you only want text, download the Ridge GGUF. Add the `mmproj` for image input.

### What fits on a GPU?

These are practical **weight-size-based estimates**, not a VRAM benchmark.
They assume a modest context and leave room for runtime and the KV cache.
Image input adds the 0.87 GiB `mmproj`. The native 262k window and the
1M YaRN extension — make KV the dominant cost and may need offload
regardless of weight quant.

**Measured:** `Qwen3.8-27B-Ridge-3.7bpw.gguf` fully offloaded to a single
**RTX PRO 6000 Blackwell (96 GB)** runs at **~54 tok/s generation,
~130 tok/s prompt** (llama.cpp CUDA, `-ngl 99`, short smoke). One data
point on one card, not a sweep — but a 27B at 11.7 GiB is comfortably
interactive on a 16–24 GB card at modest context.

| File | Approximate hardware guidance at modest context |
|---|---|
| Ridge-3.7bpw | The practical 16 GB starting point; 24 GB is comfortable once you add KV and (optionally) the mmproj. |
| + mmproj | Add ~1 GiB. Still a 24 GB card for everyday use. |

---

## Recipe

Qwen3.8 is a hybrid: three Gated-DeltaNet layers for every full-attention
layer. GDN state is disproportionately sensitive to low-bit quantization,
so Ridge holds that path high and spends the saved bits by dropping
mid-stack FFN.

**The Gated-DeltaNet state path is Q8_0.** Mixers are Q4_K, not IQ2.
That is the difference between this file and a flat 2-bit dump of the
same model.

Built with llama.cpp `adb55e5`, CUDA, importance matrix on 80 × 512-token
chunks (`--process-output`, wikitext + code). MTP tensors are unused
during calibration and have **no** imatrix — IQ2/IQ3 on `blk.64` will
abort, so the draft head stays Q6_K.

---

## Measured

Same box, same calibration file, `llama-perplexity`, 80 chunks,
`-c 512 -b 512`. BF16 is our convert of the same official checkpoint.

| Candidate | Size | BPW | Wiki-style PPL | vs BF16 |
|---|---:|---:|---:|---|
| BF16 GGUF (this convert) | 50.89 GiB | 16.00 | **7.15 ± 0.12** | — |
| **Ridge-3.7bpw** | **11.73 GiB** | **3.69** | **7.82 ± 0.14** | **+9.3 %** |

---

## Comparison

Published Hugging Face file sizes as of 2026-08-15. PPL is filled only
where we measured the file ourselves.

| File | Publisher | Size | Nominal band | PPL vs this BF16 |
|---|---|---:|---|---|
| BF16 | this convert | 50.89 GiB | 16 bpw | **7.15** |
| `UD-IQ2_XXS` | [unsloth](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) | 8.39 GiB | ~2.1 bpw | *not measured here* (Unsloth quotes 82.5 % top-1 vs BF16) |
| `UD-IQ2_M` | unsloth | 9.61 GiB | ~2.4 bpw | *not measured* |
| `IQ2_XXS` | [bartowski](https://huggingface.co/bartowski/Qwen3.8-27B-GGUF) | 8.75 GiB | ~2.2 bpw | *not measured* |
| `Q3_K_S` | unsloth | 11.71 GiB | ~3.1 bpw | *not measured* |
| **Ridge-3.7bpw** | **empero-ai** | **11.73 GiB** | **3.69 bpw** | **7.82 (+9 %)** |
| `IQ3_XXS` | bartowski | 11.76 GiB | ~2.9 bpw | *not measured* |
| `UD-Q3_K_XL` | unsloth | 12.52 GiB | ~3.4 bpw | *not measured* |

---

## Quick start

### llama.cpp (`llama-cli`)

Sampling from the official Qwen3.8 card. Thinking is on by default.

```bash
# thinking
llama-cli \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  -ngl 99 -n 16384 \
  --temp 1.0 --top-p 0.95 --top-k 20 \
  -p "Explain the design tradeoffs in a Gated-DeltaNet hybrid model."

# instruct (thinking off)
llama-cli \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  -ngl 99 --reasoning off \
  --temp 0.7 --top-p 0.80 --top-k 20 --presence-penalty 1.5 \
  -p "Say hello in one short sentence."
```

### llama.cpp (`llama-server`)

```bash
llama-server \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  -c 16384 --port 8080
```

### Ollama

```bash
ollama run hf.co/empero-ai/Qwen3.8-27B-Ridge-GGUF
```

Or a local Modelfile:

```
FROM ./Qwen3.8-27B-Ridge-3.7bpw.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER top_k 20
```

```bash
ollama create qwen38-ridge -f Modelfile
ollama run qwen38-ridge
```

### LM Studio / jan / KoboldCpp

Download `Qwen3.8-27B-Ridge-3.7bpw.gguf` and load it. Preserve the
embedded Qwen3.8 chat template if the runtime asks you to select one.

### llama.cpp with MTP draft speculation

The Ridge GGUF keeps the native MTP head. Use a recent llama.cpp build
that supports `--spec-type draft-mtp`:

```bash
llama-server \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  --spec-type draft-mtp \
  --spec-draft-n-max 6 \
  -c 16384 --port 8080
```

If your runtime does not support MTP, the file still runs as a normal
27B — you just will not get the draft speedup.

---

## Vision (image input)

Download the text GGUF and `mmproj-Qwen3.8-27B-BF16.gguf`.

### llama.cpp (`llama-mtmd-cli`)

```bash
llama-mtmd-cli \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  --mmproj mmproj-Qwen3.8-27B-BF16.gguf \
  --image ./photo.jpg \
  -p "Describe this image in detail." \
  --temp 0.7 --top-p 0.80 --top-k 20 \
  -c 16384
```

### llama.cpp server

```bash
llama-server \
  -m Qwen3.8-27B-Ridge-3.7bpw.gguf \
  --mmproj mmproj-Qwen3.8-27B-BF16.gguf \
  -c 16384 --port 8080
```

---

## Sampling

Qwen3.8 is a hybrid thinking model. Responses open with a
`<think>…</think>` block unless thinking is disabled.

| Mode | temperature | top_p | top_k | presence_penalty |
|---|---|---|---|---|
| Thinking (default) | 1.0 | 0.95 | 20 | 0.0 |
| Instruct (thinking off) | 0.7 | 0.80 | 20 | 1.5 |

Use the runtime chat/completions path rather than hand-rolling a
different prompt format. The embedded template is Qwen3.8's, including
tool-use (`<tool_call>…</tool_call>`).

## Long context

Native context is **262,144** tokens, extensible to **1,000,000** with
YaRN. Set `-c` to what you actually need — the KV cache, not the
11.7 GiB weights, is what blows up a 16–24 GB card at long context.

---

## Limitations

- **Not lossless.** +9 % wiki-style PPL vs our BF16 convert
- **Context costs memory.** Weight size is only part of the hardware
  budget.
- **MTP is runtime-dependent.** The head is in the file; the speedup
  needs a runtime that knows `draft-mtp`.

## Stay in the loop

Sign up for the Empero newsletter at **[empero.org](https://empero.org)**
for releases, evals, and research notes.

## Support / Donate

If this model helped you, consider supporting the project:

- **BTC**: `bc1qx6zepu6sfkvshgdmc4ewu6pk6rpadvpgffpp7v`
- **LTC**: `ltc1qv2mefzps2vtjcpwfx8xxdrpplrcvltswm68r7x`
- **XMR**: `42Dbm5xg5Nq26fdyzfEU7KBnAJfhi7Cvz5J2ex5CzHXkfKuNEJzYCcmJ1GTbgjFZ5MBx72sdG1G9239Cd6rsZfv4QeDkYJY`

---

## Provenance & licensing

Quantization of **[Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B)**
@ `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`. Weights are **Apache-2.0**,
inherited from the Qwen base, shared as-is.

## Acknowledgements

- Developed and released by [Empero](https://empero.org)
- Base model: [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) (Alibaba Qwen team)
- GGUF quantization: [llama.cpp](https://github.com/ggml-org/llama.cpp) (ggml-org)
