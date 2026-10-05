---
license: apache-2.0
base_model: philbert440/Qwen3.8-27B-Uncensored-Cyber
tags: [uncensored, abliterated, qwen3, cyber, gguf, llama.cpp]
pipeline_tag: image-text-to-text
---

# Qwen3.8-27B-Uncensored-Cyber — GGUF

llama.cpp GGUF quants of **Qwen3.8-27B-Uncensored-Cyber** (v2 recipe), with the **vision projector**
(`mmproj-*`) for image input and the **MTP head** (`mtp-*`) for speculative decoding.

## Files
| file | notes |
|---|---|
| `*-Q8_0` / `*-Q6_K` / `*-Q5_K_M` / `*-Q4_K_M` | weight quants (Q4_K_M smallest, Q8_0 ≈ lossless) |
| `mmproj-*-{BF16,Q8_0}` | vision projector (`--mmproj` for image input) |
| `mtp-*-{BF16,Q8_0,Q4_0}` | MTP speculative-decoding head (optional) |

Full BF16 is not shipped as a single GGUF (exceeds the 50GB per-file limit) — use `Q8_0` (≈lossless) or the
bf16 [safetensors repo](https://huggingface.co/philbert440/Qwen3.8-27B-Uncensored-Cyber).

## Evaluation (bf16, Claude-judged; cyber = 100 held-out cyber-offensive prompts, regex refusal harness)

| | cyber-open ↑ | confab ↓ | factual ↑ | gsm8k ↑ | degen ↓ |
|---|---|---|---|---|---|
| **Cyber v2 (this line)** | **100/100** | **0.867** | **1.00** | 0.80 | 0.00 |
| previous Cyber build | 93/100 | 1.00 | 0.933 | 0.825 | 0.00 |

## Note
Uncensored / de-refused, tuned to fully answer cyber and offensive-security questions. Use responsibly and in compliance with applicable law.
