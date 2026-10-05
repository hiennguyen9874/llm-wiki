---
type: Concept
title: Huihui Qwen3.8-27B Abliterated GGUF
description: Uncensored Qwen3.8-27B GGUF family using layer-selective abliteration with non-standard K_L mixed quantization and llama.cpp/Ollama serving.
tags: [qwen3.8, gguf, quantization, llama-cpp, ollama, abliteration, uncensored, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T16:00:00Z }
sources:
  - id: huihui
    resource: ../raw/Huihui-Qwen3.8-27B-abliterated-GGUF.md
    title: Huihui-Qwen3.8-27B-abliterated-GGUF model card
---

Huihui is a community redistribution of `Qwen/Qwen3.8-27B` as abliterated GGUFs that removes refusals with a crude proof-of-concept abliteration without TransformerLens, keeping MTP and vision unmodified while ablating only selected middle-to-late layers and shipping non-standard `K_L`/`Q8_0_L` mixed-precision quants for llama.cpp and Ollama local serving[^huihui]. **Reported** by the model card unless noted; no independent benchmark, fit, or run verification is offered in the source.

## What Huihui changes

- Base is `Qwen/Qwen3.8-27B`; the card presents itself as an uncensored version created with abliteration and points to `Sumandora/remove-refusals-with-transformers` for background[^huihui]. **Reported**.
- Method is described as a crude, proof-of-concept refusal removal without TransformerLens[^huihui]. **Reported**.
- MTP and vision are stated as not modified across the series[^huihui]. **Reported**.
- The card carries explicit use warnings: significantly reduced safety filtering with risk of sensitive or controversial outputs, unsuitable for all audiences, user-bears legal and ethical responsibility, research and experimental use recommended over production or public-facing commercial use, real-time monitoring and manual review advised, and no default safety guarantees with huihui.ai disclaiming responsibility[^huihui]. **Reported**.

## Variant series and ablation scope

- `UD` series from `unsloth/Qwen3.8-27B-GGUF`: layers 17–52 (0-based) ablated in the latest update, previously the first 15 layers retained; converted size may differ from the original GGUF; `bf16.gguf` also updated; stated goal is retaining more original-model performance[^huihui]. **Reported**.
- `UD-DW` series from `unsloth/Qwen3.8-27B-GGUF`: only layers 22–52 ablated, other layers unablated, with a possible small disclaimer warning; converted size may differ[^huihui]. **Reported**.
- `GSQ-RCO` series from `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF`: only layers 22–52 ablated, remainder unablated, with a possible small disclaimer warning; converted size may differ[^huihui]. **Reported**.
- `Ternary` series from `prism-ml/Ternary-Bonsai-2-27B-gguf`: only layers 22–52 ablated, remainder unablated, with a possible small disclaimer warning; some weights converted from PTQ1 to Q2_K or Q3_K so size may differ; ternary hybrid-attention kernels live in the `PrismML-Eng/llama.cpp` fork and stock llama.cpp will not run these files[^huihui]. **Reported**.
- `Swift` series from `ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF`: only layers 22–52 ablated, remainder unablated, with a possible small disclaimer warning; described as test/validation[^huihui]. **Reported**.
- Older general note also states the first 15 layers were retained without ablation[^huihui]. **Reported**; preserved alongside the newer per-series 17–52 and 22–52 scopes without reconciling which files the older note covers.

## Non-standard K_L quantization

- For versions below Q8_0, the weights targeted for ablation (`token_embd`, `output`, `ffn_down`, `ssm_out`, `attn_output`) are converted from Q2_K, Q3_K, Q4_K, Q5_K, and Q6_K to Q8_0 to improve response quality, with filenames changed to `K_L`[^huihui]. **Reported**.
- In the Q8_0 version, the same ablation-targeted Q8_0 weights are changed to BF16 and the file renamed `Q8_0_L`[^huihui]. **Reported**.
- The card warns this is not standard quantization, so `Q2_K_L` may be larger than Q3_K and Q4_K[^huihui]. **Reported**.
- Reproduction entry points named by the card are `Qwen3.8-27B-tensor_types-Q6_K_L.txt` for Q2_K_L–Q6_K_L and `Qwen3.8-27B-tensor_types-Q8_0_L.txt` for Q8_0_L, consumed via `llama-quantize --allow-requantize --tensor-type-file` from `Huihui-Qwen3.8-27B-abliterated-bf16.gguf`[^huihui]. **Reported**; tensor-type files were not in `raw/` and are uninspected.

```bash
llama-quantize \
  --allow-requantize \
  --tensor-type-file huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF/Qwen3.8-27B-tensor_types-Q6_K_L.txt \
  huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF/Huihui-Qwen3.8-27B-abliterated-bf16.gguf \
  huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF/Huihui-Qwen3.8-27B-abliterated-Q6_K_L.gguf Q6_K
```

```bash
llama-quantize \
  --allow-requantize \
  --tensor-type-file huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF/Qwen3.8-27B-tensor_types-Q8_0_L.txt \
  huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF/Huihui-Qwen3.8-27B-abliterated-bf16.gguf \
  huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF/Huihui-Qwen3.8-27B-abliterated-Q8_0_L.gguf Q8_0
```

## Running

- Ollama path uses the latest Ollama release and `huihui_ai/Qwen3.8-abliterated` directly[^huihui]. **Reported**:

```bash
ollama run huihui_ai/Qwen3.8-abliterated
```

- llama.cpp path uses the latest llama.cpp; text example given[^huihui]. **Reported**:

```bash
llama-cli -m huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF/Huihui-Qwen3.8-27B-abliterated-Q4_K.gguf -c 262144
```

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the official Unsloth GGUF/NVFP4 local path while Huihui is the abliterated community GGUF alternative with its own layer scopes and `K_L` quant handling.
- Related to [Dirk Qwen3.8-27B Sharp-Template GGUF](dirk-qwen3.8-27b-gguf.md) — another community repackaging of the same 27B base preserving MTP; Dirk changes only the chat template while Huihui ablates refusal-related layers across UD/GSQ-RCO/Ternary/Swift sources.
- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — the UD and UD-DW tiers derive from `unsloth/Qwen3.8-27B-GGUF` before Huihui ablation and `K_L` requantization.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — Huihui is a llama.cpp-side local-inference artifact with a fixed `-c 262144` recipe, except the Ternary tier which needs the PrismML fork.
- Related to [Ollama vs vLLM vs SGLang Serving Choice](ollama-vs-vllm-vs-sglang.md) — the `huihui_ai/Qwen3.8-abliterated` Ollama tag is the single-user local entry point for this family.

## Coverage limits

- Entry point `../raw/Huihui-Qwen3.8-27B-abliterated-GGUF.md` inspected statically (**Observed**); no commands executed, so ablation effect, quality claims, and run recipes are **Reported**, not reproduced.
- Tensor-type files `Qwen3.8-27B-tensor_types-Q6_K_L.txt` and `Qwen3.8-27B-tensor_types-Q8_0_L.txt` are linked in the source but absent from `raw/` and uninspected.
- External bases and tools uninspected: `Qwen/Qwen3.8-27B`, `unsloth/Qwen3.8-27B-GGUF`, `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF`, `prism-ml/Ternary-Bonsai-2-27B-gguf`, `ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF`, `PrismML-Eng/llama.cpp` fork, `Sumandora/remove-refusals-with-transformers`, stock llama.cpp and Ollama releases, and the Ollama `huihui_ai/Qwen3.8-abliterated` tag.
- No VRAM, throughput, perplexity, or benchmark figures are stated in the source; per the SCOPE benchmark rule there is nothing to promote beyond **Reported**.
- Donation Bitcoin address and Ko-fi link excluded as non-durable solicitation with no serving reuse value.

[^huihui]: Huihui-Qwen3.8-27B-abliterated-GGUF model card — `../raw/Huihui-Qwen3.8-27B-abliterated-GGUF.md` (huihui-ai; Apache-2.0; base `Qwen/Qwen3.8-27B`; frontmatter plus sections Latest update 7 / 6 / 5 / 4 / Latest update / Note / Specific Quantification Method / Q2_K_L–Q6_K_L / Q8_0_L / ollama / llama.cpp / Usage Warnings): crude PoC abliteration without TransformerLens with MTP/vision unmodified; UD 17–52, UD-DW/GSQ-RCO/Ternary/Swift 22–52 scopes with disclaimer and size-difference notes and PrismML-fork-only Ternary constraint; ablation-target tensors (`token_embd`, `output`, `ffn_down`, `ssm_out`, `attn_output`) upconverted to Q8_0/BF16 as `K_L`/`Q8_0_L` with non-standard-size warning; `llama-quantize --allow-requantize --tensor-type-file` Q6_K_L and Q8_0_L commands from `bf16.gguf`; `ollama run huihui_ai/Qwen3.8-abliterated` and `llama-cli -m ...-Q4_K.gguf -c 262144` recipes; six-bullet safety/legal/research-use warnings.
