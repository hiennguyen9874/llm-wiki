---
license: apache-2.0
base_model: Qwen/Qwen3.8-27B
base_model_relation: quantized
pipeline_tag: text-generation
library_name: llama.cpp
language:
  - en
  - zh
tags:
  - gguf
  - uncensored
  - qwen3.8
  - mtp
  - speculative-decoding
  - imatrix
  - quantized
---

# Qwen3.8-27B-Uncensored-GGUF

Uncensored [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), published as GGUF
quantizations with the multi token prediction (MTP) head retained and verified.

Refusal behaviour has been **substantially reduced**, not eliminated. See Measured
behaviour for the numbers. Capabilities, training data, and architecture are otherwise
unchanged.


## Table of Contents

- [Method](#method)
- [Whats here](#whats-here)
- [Overview](#overview)
- [Files](#files)
- [Perplexity](#perplexity)
  - [Baseline against the unmodified base model](#baseline-against-the-unmodified-base-model)
  - [How the baseline was measured](#how-the-baseline-was-measured)
- [Importance matrix](#importance-matrix)
- [Building other low bit quants yourself](#building-other-low-bit-quants-yourself)
  - [Third party quants](#third-party-quants)
- [Usage](#usage)
  - [ComfyUI](#comfyui)
  - [llama cpp](#llama-cpp)
- [Verification](#verification)
- [Measured behaviour](#measured-behaviour)
  - [How to read these](#how-to-read-these)
  - [Caveats that matter](#caveats-that-matter)
- [Requirements](#requirements)
- [Limitations](#limitations)
- [License](#license)
- [Speculative decoding, measured on this model](#speculative-decoding-measured-on-this-model)
  - [IQ2_M](#iq2_m)


## Method

- Refusal directions removed with [Heretic](https://github.com/p-e-w/heretic), which
  co minimizes refusal count against KL divergence from the base model. No handwritten
  refusal removal code, no finetuning, no additional training data.
- Abliteration runs at bf16 (no 4 bit quantization). the resulting LoRA is merged into the
  bf16 base, so the published weights are not a quantized round trip.
- `mtp.*` tensors are copied verbatim from the base checkpoint after merging. Abliteration
  never touches them. Instead abliteration modifies `attn.o_proj` and `mlp.down_proj` in the main stack.
- The draft head was trained against the unmodified model, so acceptance rate may fall
  slightly. Speculative decoding verifies every token against the target, so output quality
  is unaffected.
- imatrix is computed directly from the f16, not from an intermediate quantization, so
  calibration sees the real weights.

## Whats here

| Family | Files | Use when |
|---|---|---|
| Fused | `Qwen3.8-27B-Uncensored-<QUANT>.gguf` | One file. MTP rides inline as a built-in draft. |
| Target + draft | `Qwen3.8-27B-Uncensored-noMTP-<QUANT>.gguf` + `Qwen3.8-27B-Uncensored-draft-<QUANT>.gguf` | Your runtime wants an explicit `--model-draft`. |
| Vision | `mmproj-Qwen3.8-27B-Uncensored-F16.gguf` | Image input with a compatible vision runtime. |
| MTP Head for llama server | `Qwen3.8-27B-Uncensored-draft-<QUANT>.gguf` | MTP head for llama-server, specifically for the flag `--model-draft`

The draft head ships at Q8_0 and Q4_0, the same weights at two precisions. Q8_0 is the
default and is what the speculative decoding tables below were measured with. Q4_0 saves
1.5 GB for tight VRAM budgets, and its acceptance rate has not been measured here.

The F16 vision projector uses the standard `mmproj` prefix for automatic discovery by
compatible runtimes.

## Overview

| | |
|---|---|
| Base | Qwen/Qwen3.8-27B |
| Architecture | `Qwen3_5ForConditionalGeneration` |
| Layers | 64 |
| Vocab | 248320 |
| MTP layers | 1 |
| Vision | yes |
| Context | 262144 |
| Quants | IQ2_M, IQ4_XS, Q4_K_M, Q5_K_M, Q6_K, Q8_0 |
| imatrix | wikitext-2 raw, 200 chunks, [published](#importance-matrix) |
| Converted with | llama.cpp `a94d563ed` |

## Files

| File | Size | MTP | PPL (wikitext-2) |
|---|---|---|---|
| `Qwen3.8-27B-Uncensored-IQ2_M.gguf` | 10.6 GB | yes | PPL = 7.8581 +/- 0.27481 |
| `Qwen3.8-27B-Uncensored-IQ4_XS.gguf` | 15.3 GB | yes | PPL = 7.1583 +/- 0.25019 |
| `Qwen3.8-27B-Uncensored-Q4_K_M.gguf` | 16.8 GB | yes | PPL = 7.1814 +/- 0.25227 |
| `Qwen3.8-27B-Uncensored-Q5_K_M.gguf` | 19.5 GB | yes | PPL = 7.1573 +/- 0.25055 |
| `Qwen3.8-27B-Uncensored-Q6_K.gguf` | 22.4 GB | yes | PPL = 7.1689 +/- 0.25149 |
| `Qwen3.8-27B-Uncensored-Q8_0.gguf` | 29.0 GB | yes | PPL = 7.1764 +/- 0.25195 |
| `Qwen3.8-27B-Uncensored-draft-Q4_0.gguf` | 1.7 GB | - | - |
| `Qwen3.8-27B-Uncensored-draft-Q8_0.gguf` | 3.2 GB | - | - |
| `Qwen3.8-27B-Uncensored-noMTP-IQ2_M.gguf` | 10.2 GB | no | PPL = 7.8581 +/- 0.27481 |
| `Qwen3.8-27B-Uncensored-noMTP-IQ4_XS.gguf` | 15.1 GB | no | - |
| `Qwen3.8-27B-Uncensored-noMTP-Q4_K_M.gguf` | 16.5 GB | no | - |
| `Qwen3.8-27B-Uncensored-noMTP-Q5_K_M.gguf` | 19.2 GB | no | - |
| `Qwen3.8-27B-Uncensored-noMTP-Q6_K.gguf` | 22.1 GB | no | - |
| `Qwen3.8-27B-Uncensored-noMTP-Q8_0.gguf` | 28.6 GB | no | - |
| `mmproj-Qwen3.8-27B-Uncensored-F16.gguf` | 0.9 GB | - | - |
| `Qwen3.8-27B-Uncensored-imatrix.dat` | 13.6 MB | - | - |

## Perplexity

Measured on this build, every quant in one session against the same f16 baseline, so the
rows are comparable to each other.

| File | PPL (wikitext-2) | vs f16 |
|---|---|---|
| `Qwen3.8-27B-Uncensored-f16.gguf` (baseline, not shipped) | 7.1557 +/- 0.25104 | |
| `Qwen3.8-27B-Uncensored-Q5_K_M.gguf` | 7.1573 +/- 0.25055 | +0.0016 |
| `Qwen3.8-27B-Uncensored-IQ4_XS.gguf` | 7.1583 +/- 0.25019 | +0.0026 |
| `Qwen3.8-27B-Uncensored-Q6_K.gguf` | 7.1689 +/- 0.25149 | +0.0132 |
| `Qwen3.8-27B-Uncensored-Q8_0.gguf` | 7.1764 +/- 0.25195 | +0.0207 |
| `Qwen3.8-27B-Uncensored-Q4_K_M.gguf` | 7.1814 +/- 0.25227 | +0.0257 |
| `Qwen3.8-27B-Uncensored-IQ2_M.gguf` | 7.8581 +/- 0.27481 | +0.7024 |

**Read the error bars before reading the ordering.** Every row except IQ2_M sits inside a
span of 0.026 against a standard error of roughly 0.25, so those quants are not separable
from the f16 or from each other, and their ordering here is noise. Do not conclude that Q8_0
is worse than Q5_K_M. The only difference this measurement actually resolves is IQ2_M, which
is about 2.8 standard errors above the baseline.

The `noMTP-*` twins are not listed because they measure identically to their fused
counterparts. The MTP block is inert during a normal forward pass, which was confirmed here:
fused and noMTP IQ2_M both return 7.8581, and fused and noMTP f16 both return 7.1557.

Corpus is [`Salesforce/wikitext`](https://huggingface.co/datasets/Salesforce/wikitext),
`wikitext-2-raw-v1`, `test-00000-of-00001.parquet`, `text` column joined with `\n`. This is
the same file used for the importance matrix, described in full below.

```bash
llama-perplexity -m Qwen3.8-27B-Uncensored-IQ2_M.gguf \
  -f calibration.txt -ngl 99 --chunks 20
```

### Baseline against the unmodified base model

Every row above is this model, so that table shows what quantization costs and nothing more.
It does not show what the abliteration costs. That needs the unmodified base model run on the
same harness, which is what follows.

| Model | File | PPL (wikitext-2) | vs base bf16 |
|---|---|---|---|
| Qwen/Qwen3.8-27B | `Qwen3.8-27B-BF16.gguf` | 6.5129 +/- 0.04209 | baseline |
| Qwen/Qwen3.8-27B | `Qwen3.8-27B-Q8_0.gguf` | 6.5122 +/- 0.04208 | -0.0007 |
| This model | `Qwen3.8-27B-Uncensored-BF16.gguf` (not shipped) | 6.5563 +/- 0.04248 | +0.0434 |

Base files come from [`ggml-org/Qwen3.8-27B-GGUF`](https://huggingface.co/ggml-org/Qwen3.8-27B-GGUF).
The bf16 GGUF of this model was converted locally from the published bf16 weights and is not
shipped here, for the same reason the f16 is not.

The weight edit costs 0.0434 perplexity, about 0.7% relative. Measured as a paired difference
over the same tokens rather than as two independent runs, the gap is 0.0437 +/- 0.0163, so it
is a real cost rather than noise. The base Q8_0 row is the control: it lands 0.0007 from the
base bf16, well below the gap being reported.

Distribution overlap was measured directly rather than inferred from the perplexity gap:

| | |
|---|---|
| Mean KL divergence, base bf16 against this model at bf16 | 0.0141 +/- 0.0025 |
| Maximum KL divergence | 19.956 |
| Same top token | 96.72% |
| Tokens compared | 20480 |

This is a different measurement from the first token KL under Measured behaviour, which is
the figure Heretic optimizes against. This one runs over ordinary corpus text and covers
every position, not just the first.

### How the baseline was measured

One session, one machine, one binary, the same corpus file and the same settings for every
row, with each model fully offloaded:

```bash
llama-perplexity -m Qwen3.8-27B-BF16.gguf \
  -f calibration.txt -c 2048 -b 2048 -ngl 99
```

| | |
|---|---|
| Corpus | `calibration.txt`, byte identical to the file under Importance matrix, md5 `d998c24b049cf7c009dbf2672da70b5a` |
| Coverage | whole file, 145 chunks of 2048 tokens |
| Built with | llama.cpp `a94d563ed` |
| Hardware | NVIDIA H200 NVL, full offload at `-ngl 99` |

**These numbers do not line up with the table above.** That table stops at 20 chunks and this
one reads the whole file, so the two cover different amounts of text and cannot be compared
directly. Rows within each table are comparable to each other. The whole file run carries a
standard error of roughly 0.042 against 0.25 for the 20 chunk run, which is why a gap this
small is worth reporting at all.

Perplexity detects gross quantization damage and nothing else. It does not measure
reasoning, code, multilingual ability, or refusal behaviour. See Caveats that matter.

## Importance matrix

`Qwen3.8-27B-Uncensored-imatrix.dat` is the importance matrix every quantization in this
repo was built with. All twelve of the `IQ2_M`, `IQ4_XS`, `Q4_K_M`, `Q5_K_M`, `Q6_K` and
`Q8_0` files, fused and `noMTP` alike, record it in their own metadata. The standalone
`draft-Q8_0` head and the `mmproj-Qwen3.8-27B-Uncensored-F16.gguf` projector do not,
because neither was built with one.

It is published so the files here can be reproduced, and so you can build quants that are
not in this repo.

| | |
|---|---|
| Corpus | [`Salesforce/wikitext`](https://huggingface.co/datasets/Salesforce/wikitext), `wikitext-2-raw-v1`, `test-00000-of-00001.parquet` |
| Assembly | `text` column joined with `\n`, giving 1,292,013 bytes, md5 `d998c24b049cf7c009dbf2672da70b5a` |
| Chunks | 200 x 512 tokens |
| Computed from | the f16 GGUF, not an intermediate quantization |
| Built with | llama.cpp `a94d563ed` |

Two things to know before you use it:

- **It is GGUF format despite the `.dat` extension** (`general.type = imatrix`). llama.cpp
  builds predating GGUF imatrix support will not load it.
- **It contains no entries for `blk.64`**, the MTP block. `llama-imatrix` never activates the
  draft head during a normal forward pass, so no activations are collected for it. This
  matters below.

Provenance is checkable rather than asserted: requantizing the f16 to Q4_K_M with this file
reproduces the published `Qwen3.8-27B-Uncensored-Q4_K_M.gguf` to byte-identical tensors
across all 866 tensors.

## Building other low bit quants yourself

The floor here is IQ2_M at 10.6 GB. If you want something smaller, or a type that is not
published, the imatrix above lets you build it.

You will need the f16 GGUF, which is not published here because it is 54 GB. Build it from
the bf16 weights, which are public:

```bash
hf download JonathanColetti/Qwen3.8-27B-Uncensored --local-dir Qwen3.8-27B-Uncensored
python convert_hf_to_gguf.py Qwen3.8-27B-Uncensored \
  --outfile Qwen3.8-27B-Uncensored-f16.gguf --outtype f16
```

Add `--no-mtp` to that command for the `noMTP` variant. The MTP shard is already grafted
into the bf16 repo, so nothing needs restoring first.

**The MTP block must be pinned.** Because the imatrix has no `blk.64` entries, and because
IQ3_XXS, IQ2_XXS, IQ2_S and IQ2_M require per-tensor importance data, a fused low-bit build
without a pin does not merely degrade the draft head. `llama-quantize` refuses to run at all.
Pinning `blk.64` to `q8_0` sidesteps the requirement and keeps the draft head intact:

```bash
llama-quantize \
  --imatrix Qwen3.8-27B-Uncensored-imatrix.dat \
  --tensor-type 'blk\.64\.=q8_0' \
  --token-embedding-type q4_K \
  Qwen3.8-27B-Uncensored-f16.gguf Qwen3.8-27B-Uncensored-IQ2_XXS.gguf IQ2_XXS
```

`--token-embedding-type q4_K` is the largest size lever on this model. llama.cpp force-bumps
`token_embd` to Q5_K on every IQ2/IQ1 ftype, and at 248320 vocab that is roughly 8 to 10% of
parameters. Do not go below `q4_K`. Omit the `--tensor-type` pin for `noMTP-*` builds, since
there is no block to pin.

Verify afterwards that the block survived, rather than assuming it did:

```bash
python quantize.py inspect Qwen3.8-27B-Uncensored-IQ2_XXS.gguf   # expect 65/65, has_mtp: true
```

> **2 bit warning.** IQ2_M is the most degraded file in this repo, and anything you build
> below it will be worse. Expect the loss to land hardest on the thing this model is used
> for. Behaviour near the old refusal boundary is already its least stable property (see
> Caveats that matter), and 2 bit compounds exactly that. Perplexity will tell you the model
> is not broken. It will not tell you the refusal boundary still behaves the way it does at
> Q6_K, and nothing in this repo measures that at 2 bit.

### Third party quants

A third party publishes a range of mixed-precision variants derived from this model:

- [zerodigest/Qwen3.8-27B-Uncensored-YMQ-MTP-GGUF](https://huggingface.co/zerodigest/Qwen3.8-27B-Uncensored-YMQ-MTP-GGUF)

**Not produced by or affiliated with this repo.** It is not built by me, I have not verified
its files or its published numbers, and any metrics quoted there were not measured on the
harness used here, so they are not comparable to the perplexity figures in this card. Linked
because people ask for sizes I do not ship, not as an endorsement.

## Usage

### ComfyUI

Tested versions:

* ComfyUI commit `0a33ed6c28f926d14536235771c222f9e6d1026b`
* ComfyUI QwenVL commit `e79582111e5835787574bcc17adc4bf4cf3a07f4`
* llama cpp python version `0.3.48` at commit `c57b174711166b889f06a35a30af95a75db24705`

```bash
# Install ComfyUI and the QwenVL nodes
git clone https://github.com/comfyanonymous/ComfyUI.git
git -C ComfyUI checkout 0a33ed6c28f926d14536235771c222f9e6d1026b
git clone https://github.com/1038lab/ComfyUI-QwenVL.git ComfyUI/custom_nodes/ComfyUI-QwenVL
git -C ComfyUI/custom_nodes/ComfyUI-QwenVL checkout e79582111e5835787574bcc17adc4bf4cf3a07f4

# Install dependencies
uv pip install -r ComfyUI/requirements.txt
uv pip install -r ComfyUI/custom_nodes/ComfyUI-QwenVL/requirements.txt
CMAKE_ARGS="-DGGML_CUDA=on -DLLAMA_CPP_PYTHON_VISION=on" \
  uv pip install \
  "llama-cpp-python @ git+https://github.com/JamePeng/llama-cpp-python.git@c57b174711166b889f06a35a30af95a75db24705"

# Download the language model and F16 vision projector
hf download JonathanColetti/Qwen3.8-27B-Uncensored-GGUF \
  Qwen3.8-27B-Uncensored-Q4_K_M.gguf \
  mmproj-Qwen3.8-27B-Uncensored-F16.gguf \
  --local-dir \
  ComfyUI/models/LLM/GGUF/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF

# Start ComfyUI
cd ComfyUI
python main.py --listen 127.0.0.1 --port 8188
```

Add the model to `ComfyUI/custom_nodes/ComfyUI-QwenVL/custom_models.json`:

```json
{
  "hf_models": {},
  "gguf_models": {
    "Qwen3.8 27B Uncensored Q4 K M": {
      "author": "JonathanColetti",
      "repo_name": "Qwen3.8-27B-Uncensored-GGUF",
      "repo_id": "JonathanColetti/Qwen3.8-27B-Uncensored-GGUF",
      "model_files": [
        "Qwen3.8-27B-Uncensored-Q4_K_M.gguf"
      ]
    }
  }
}
```

The projector is discovered automatically because its filename starts with `mmproj`.

### llama cpp

```bash
llama-server -m Qwen3.8-27B-Uncensored-Q4_K_M.gguf \
  --spec-type draft-mtp --spec-draft-n-max 2 \
  -ngl 99 -c 8192
```

Target plus explicit draft:

```bash
llama-server -m Qwen3.8-27B-Uncensored-noMTP-Q4_K_M.gguf \
  --spec-type draft-mtp \
  --model-draft Qwen3.8-27B-Uncensored-draft-Q8_0.gguf \
  -ngl 99 -c 8192
```

`--spec-draft-n-max` defaults to 3. Throughput depends on your hardware, so sweep it —
measurements across draft lengths are in
[qwen3.8-spec-decode-bench](https://huggingface.co/datasets/JonathanColetti/qwen3.8-spec-decode-bench).

## Verification

Each artifact was checked post-quantization for MTP tensor survival rather than inferred from
the conversion flag:

```bash
python quantize.py inspect Qwen3.8-27B-Uncensored-Q4_K_M.gguf
```

This reports metadata keys, declared `block_count`, and blocks actually present. A fused file
whose present-block count does not exceed its declared count did not retain the MTP block.

| File | MTP | blocks |
|---|---|---|
| `Qwen3.8-27B-Uncensored-f16.gguf` | True | 65/65 |
| `Qwen3.8-27B-Uncensored-noMTP-f16.gguf` | False | 64/64 |
| `Qwen3.8-27B-Uncensored-IQ2_M.gguf` | True | 65/65 |
| `Qwen3.8-27B-Uncensored-noMTP-IQ2_M.gguf` | False | 64/64 |
| `Qwen3.8-27B-Uncensored-IQ4_XS.gguf` | True | 65/65 |
| `Qwen3.8-27B-Uncensored-noMTP-IQ4_XS.gguf` | False | 64/64 |
| `Qwen3.8-27B-Uncensored-Q4_K_M.gguf` | True | 65/65 |
| `Qwen3.8-27B-Uncensored-noMTP-Q4_K_M.gguf` | False | 64/64 |
| `Qwen3.8-27B-Uncensored-Q5_K_M.gguf` | True | 65/65 |
| `Qwen3.8-27B-Uncensored-noMTP-Q5_K_M.gguf` | False | 64/64 |
| `Qwen3.8-27B-Uncensored-Q6_K.gguf` | True | 65/65 |
| `Qwen3.8-27B-Uncensored-noMTP-Q6_K.gguf` | False | 64/64 |
| `Qwen3.8-27B-Uncensored-Q8_0.gguf` | True | 65/65 |
| `Qwen3.8-27B-Uncensored-noMTP-Q8_0.gguf` | False | 64/64 |

## Measured behaviour

Benchmarked against the unmodified base model on identical settings. The delta is the
figure that matters: it isolates what the weight edit cost.

| Task | Base | Uncensored | Δ |
|---|---|---|---|
| MMLU | 83.4 | 83.3 | -0.2 |
| ARC-Challenge | 58.9 | 57.7 | -1.2 |
| HellaSwag | 82.8 | 82.9 | +0.1 |
| Winogrande | 76.1 | 75.3 | -0.8 |
| **Mean** | | | **-0.5** |

zero shot via [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness),
bf16, both models scored in the same session. Every delta is within or close to the
reported standard error (MMLU +/- 0.30, ARC +/- 1.44, HellaSwag +/- 0.38, Winogrande +/- 1.21), so
none is clearly separable from run-to-run noise.

**These are 0-shot and are not comparable to Qwen's published scores**, which use few-shot
prompting. They are directly comparable to each other, which is the point. Note also that
ARC-Challenge is low for a model at this MMLU. The base scores 58.9 under the same
settings, so that is format sensitivity in a reasoning-tuned model, not abliteration
damage.

What the benchmarks do **not** cover: no generative evaluation (GSM8K, HumanEval), no
math or code, no multilingual, and the harness loads the text stack only. Nothing here
measures the vision tower or MTP speculative decoding.

| Measurement | Base model | This model |
|---|---|---|
| Refusals (100 held-out harmful prompts) | 98/100 | **12/100** |
| KL divergence vs base (first-token) | 0 | 0.1191 |

Search: 200 Heretic trials, 23 non-dominated points. The published model is the marked row.

| refusals | KL divergence | |
|---|---|---|
| 12/100 | 0.1191 | <= published |
| 13/100 | 0.1052 | |
| 19/100 | 0.0722 | |
| 23/100 | 0.0635 | |
| 26/100 | 0.0507 | |
| 27/100 | 0.0410 | |
| 35/100 | 0.0406 | |
| 36/100 | 0.0387 | |
| 41/100 | 0.0366 | |
| 44/100 | 0.0352 | |
| 46/100 | 0.0334 | |
| 48/100 | 0.0331 | |
| 51/100 | 0.0321 | |
| 52/100 | 0.0294 | |
| 60/100 | 0.0290 | |
| 76/100 | 0.0280 | |
| 77/100 | 0.0247 | |
| 83/100 | 0.0204 | |
| 86/100 | 0.0193 | |
| 91/100 | 0.0170 | |
| 96/100 | 0.0146 | |
| 97/100 | 0.0044 | |
| 98/100 | 0.0004 | |

### How to read these

**Refusal rate** is the count of refusals over 100 heldout prompts from
[`mlabonne/harmful_behaviors`](https://huggingface.co/datasets/mlabonne/harmful_behaviors)
(test split) - explicitly harmful requests, not benign ones. So this number is not an
over-refusal rate: it does not tell you how often the model declines legitimate work. It
tells you how much of the original safety behaviour on harmful requests remains.

**KL divergence** is measured against the unmodified base model over first-token
distributions, and is the optimizers proxy for "how much did we damage the model". Lower is
closer to base. It is a proxy, not a capability measurement. A low KL does not certify that
reasoning or coding ability survived, and nothing here does certify that.

The two trade off against each other. Heretic searches a Pareto front between them; the
published point is one choice on that front, not a global optimum.

### Caveats that matter

- **Refusals were measured in non-thinking mode.** This models chat template opens a
  `<think>` block, so the evaluation closes it explicitly to score answers rather than
  reasoning traces. With thinking enabled the refusal rate may differ, in either direction.
- **The measurement is 100 prompts from one dataset.** It generalizes to that distribution
  of harmful requests and no further. Refusal behaviour on other topics is uncharacterized.
- **Perplexity is wikitext-2 only** (see the Files table). It detects gross quantization
  damage. It does not detect capability loss on reasoning, code, or multilingual work.
- **Quantization compounds everything above.** The measurements were taken on the bf16
  merge; the files you download are quantized.

## Requirements

MTP speculative decoding landed in llama.cpp PR #22673. Builds older than that will load
these files and silently ignore the MTP tensors.

## Limitations

- Refusals are reduced, not eliminated, and not redirected. This model attempts many requests
  the original declines, but a meaningful fraction still get refused — see Measured behaviour.
- Behaviour near the old refusal boundary is less stable than the base model.
- Lower quants compound that, and IQ2_M compounds it most. Evaluate behaviour on Q6_K or
  Q8_0, not on IQ2_M or IQ4_XS. Nothing here measures the refusal boundary at 2-bit.
- Capability benchmarks show a 0.5-point mean drop vs base across MMLU, ARC-Challenge,
  HellaSwag and Winogrande. See Measured behaviour. No generative, math, code, or
  multilingual evaluation was run.

## License

Apache 2.0, inherited from Qwen/Qwen3.8-27B. The base model's license and acceptable use
policy still apply to your use of this derivative.

## Speculative decoding, measured on this model

| prompt | spec_type | n_max | tok/s | vs baseline |
|---|---|---|---|---|
| prose | none | - | 74.8 | 1.00x |
| prose | draft-mtp | 1 | 89.0 | 1.19x |
| prose | draft-mtp | 2 | 85.7 | 1.15x |
| prose | draft-mtp | 3 | 72.0 | 0.96x |
| prose | draft-mtp | 4 | 71.1 | 0.95x |
| prose | draft-mtp | 5 | 62.9 | 0.84x |
| prose | draft-mtp | 6 | 53.8 | 0.72x |
| prose | draft-mtp | 7 | 49.9 | 0.67x |
| prose | draft-mtp | 8 | 59.9 | 0.80x |
| code | none | - | 74.7 | 1.00x |
| code | draft-mtp | 1 | 95.4 | 1.28x |
| code | draft-mtp | 2 | 92.9 | 1.24x |
| code | draft-mtp | 3 | 82.6 | 1.11x |
| code | draft-mtp | 4 | 74.9 | 1.00x |
| code | draft-mtp | 5 | 67.4 | 0.90x |
| code | draft-mtp | 6 | 59.4 | 0.80x |
| code | draft-mtp | 7 | 55.6 | 0.74x |
| code | draft-mtp | 8 | 70.9 | 0.95x |
| chat | none | - | 74.7 | 1.00x |
| chat | draft-mtp | 1 | 90.6 | 1.21x |
| chat | draft-mtp | 2 | 84.2 | 1.13x |
| chat | draft-mtp | 3 | 76.1 | 1.02x |
| chat | draft-mtp | 4 | 70.4 | 0.94x |
| chat | draft-mtp | 5 | 64.3 | 0.86x |
| chat | draft-mtp | 6 | 55.2 | 0.74x |
| chat | draft-mtp | 7 | 50.2 | 0.67x |
| chat | draft-mtp | 8 | 54.1 | 0.72x |

### IQ2_M

Measured on this build: NVIDIA H200 NVL, 256 generated tokens, median of 3 repetitions,
`n_max` swept 1 to 3. The table above dates from the original release and its hardware is
not recorded, so compare the ratios rather than the absolute rates.

| prompt | spec_type | n_max | tok/s | vs baseline |
|---|---|---|---|---|
| prose | none | - | 75.4 | 1.00x |
| prose | draft-mtp | 1 | 85.2 | 1.13x |
| prose | draft-mtp | 2 | 83.2 | 1.10x |
| prose | draft-mtp | 3 | 77.4 | 1.03x |
| code | none | - | 75.5 | 1.00x |
| code | draft-mtp | 1 | 95.8 | 1.27x |
| code | draft-mtp | 2 | 99.8 | 1.32x |
| code | draft-mtp | 3 | 96.0 | 1.27x |
| chat | none | - | 75.3 | 1.00x |
| chat | draft-mtp | 1 | 87.4 | 1.16x |
| chat | draft-mtp | 2 | 81.3 | 1.08x |
| chat | draft-mtp | 3 | 78.4 | 1.04x |

The MTP head survives 2-bit quantization because it is pinned to `q8_0` rather than
quantized with the rest of the stack, so speculative decoding still pays here.

Pairing `noMTP-IQ2_M` with the published `draft-Q8_0` reaches 97.7 tok/s on the prose prompt
at `n_max` 2, or 1.30x, which beats the fused file on that prompt. The reason is that the
fused MTP head shares the low-bit `token_embd` (q4_K) and `output` (Q5_K) tensors with the
main model, while the standalone draft carries its own Q8_0 copies. The split setup needs
13.3 GB of weights against 10.6 GB for the fused file, so it is the better option only if
you have the VRAM to spare.
