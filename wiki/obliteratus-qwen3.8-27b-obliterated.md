---
type: Concept
title: OBLITERATUS Qwen3.8-27B OBLITERATED
description: Uncensored Qwen3.8-27B via iterative SVD/LEACE complementary-blend abliteration with greedy plus repetition-penalty serving and GGUF/safetensors packaging.
tags: [qwen3.8, gguf, quantization, llama-cpp, transformers, abliteration, uncensored, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T18:00:00Z }
sources:
  - id: obliteratus
    resource: ../raw/Qwen3.8-27B-OBLITERATED.md
    title: Qwen3.8-27B-OBLITERATED model card (OBLITERATUS)
---

OBLITERATUS `Qwen3.8-27B-OBLITERATED` is a community uncensored redistribution of `Qwen/Qwen3.8-27B` that removes refusals and soft deflections through iterative SVD plus LEACE complementary-blend abliteration, shipping a GGUF ladder and BF16 safetensors with a greedy-decoding plus repetition-penalty serving recipe and a thinking-prefill chat template[^obliteratus]. The card reports V3 at 82.33% MMLU (−2.1pp vs stock) with a STEM-heavy capability cost and 7/8 advanced real-world tasks preserved[^obliteratus]. **Reported** by the model card unless noted; no independent benchmark, fit, or run verification is offered in the source.

## V1 to V3 lineage

- Base is `Qwen/Qwen3.8-27B` by Alibaba; license Apache 2.0; `model_type: qwen3`, `pipeline_tag: text-generation`[^obliteratus]. **Reported**.
- V1 single surgery: one aggressive SVD pass with 5 directions; hard refusals removed at a stated −6pp MMLU cost[^obliteratus]. **Reported**.
- V2 complementary blending: two surgeries that fail differently are blended in weight space — aggressive SVD (3 dirs, reg 0.08) plus LEACE (3 dirs, reg 0.06) at 60/40 LERP — described as cancelling each method's weaknesses; MTP plus vision restored from stock; stated −0.3pp MMLU but soft deflections remained[^obliteratus]. **Reported**.
- V3 iterative refinement plus targeted surgery: refine the V2 champion with gentle 2-dir SVD (reg 0.04), add a targeted 3-dir SVD pass (reg 0.01) on a focused corpus, blend refined plus targeted 50/50, and restore MTP plus vision from stock with corrected tensor naming; stated goal is removing both hard refusals and soft safety-lecture deflections at −2.1pp MMLU[^obliteratus]. **Reported**.
- Card key learnings: complementary blending cancels per-method weight-space damage; always refine the champion rather than restarting from stock; focused corpora find category-specific refusal directions without signal dilution; regex refusal detectors miss soft deflections so manual auditing is required[^obliteratus]. **Reported**; treated as author synthesis, not independently verified.
- Reproduction entry point named by the card is the `OBLITERATUS` ablation-suite repo with the V1/V2/V3 recipe quoted in the source[^obliteratus]. **Reported**; repo code uninspected.

## Serving recipe

Card-stated optimal settings for direct chat and code generation[^obliteratus]. **Reported**:

| Setting | Value | Card rationale |
| --- | --- | --- |
| `temperature` | `0` | Greedy decoding gives the most complete, code-rich outputs; quality degrades significantly above 0.5 |
| `repetition_penalty` | `1.15` | Essential under greedy decoding to avoid loops on imports and boilerplate; 1.10–1.12 for tighter output |
| `max_new_tokens` | `≥ 2048` | Long code outputs need room |
| System prompt | None / empty | A/B tested; system prompts can reintroduce refusals |
| `enable_thinking` | OFF recommended, ON compatible | Bundled template prefills an empty thinking block so the model answers directly; thinking ON works but runs longer |
| `top_p` / `top_k` / `min_p` | Not needed | Greedy plus repetition penalty handles this model best |

- GGUF template note: V3 GGUFs ship a chat template that prefills an empty thinking block; use the bundled template with `--jinja` in llama.cpp or the model's built-in template in Ollama and LM Studio[^obliteratus]. **Reported**.
- Transformers recipe uses empty messages, `apply_chat_template` with `enable_thinking=False`, and `do_sample=False` with `repetition_penalty=1.15` and `max_new_tokens=2048`[^obliteratus]. **Reported**:

```python
text = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True,
    enable_thinking=False
)
outputs = model.generate(
    **inputs,
    max_new_tokens=2048,
    do_sample=False,
    repetition_penalty=1.15,
)
```

- Agentic and long-context guidance when the model loops on repeated tool calls or boilerplate[^obliteratus]. **Reported**:

| Setting | Value | Card rationale |
| --- | --- | --- |
| `repetition_penalty` | `1.15` | Critical for agents |
| `temperature` | `0.1–0.3` | Slight randomness breaks deterministic loops; pure greedy can stick |
| `max_tokens` per turn | `1024–2048` | Shorter turns keep the agent focused |
| Context management | Summarize after ~10 turns | History fills with repeated actions |

## Packaging

- GGUF ladder for llama.cpp, Ollama, and LM Studio[^obliteratus]. **Reported**:

| File | Quant | Size |
| --- | --- | --- |
| `Qwen3.8-27B-OBLITERATED-Q8_0.gguf` | Q8_0 | ~27 GB |
| `Qwen3.8-27B-OBLITERATED-Q6_K.gguf` | Q6_K | ~21 GB |
| `Qwen3.8-27B-OBLITERATED-Q5_K_M.gguf` | Q5_K_M | ~18 GB |
| `Qwen3.8-27B-OBLITERATED-Q4_K_M.gguf` | Q4_K_M | ~16 GB |
| `Qwen3.8-27B-OBLITERATED-IQ4_XS.gguf` | IQ4_XS | ~14 GB |
| `Qwen3.8-27B-OBLITERATED-Q3_K_M.gguf` | Q3_K_M | ~13 GB |
| `Qwen3.8-27B-OBLITERATED-Q2_K.gguf` | Q2_K | ~11 GB |

- Safetensors path is full bfloat16 weights in 29 shards at ~54 GB via `OBLITERATUS/Qwen3.8-27B-OBLITERATED`[^obliteratus]. **Reported**.
- MLX support is stated as pending upstream `mlx_lm` adding the Qwen3.5 architecture[^obliteratus]. **Reported**.

## Reported evaluation

All figures are card-reported with no stated independent protocol beyond the named harness; per the SCOPE benchmark rule they stay **Reported** with hardware, sampling (beyond the recipe above), and significance details missing[^obliteratus].

- MMLU via lm-eval-harness, 0-shot, 100 per subject and 5700 questions[^obliteratus]. **Reported**:

| Model | MMLU | Stderr | vs stock |
| --- | --- | --- | --- |
| Stock Qwen3.8-27B | 84.46% | ±0.46 | — |
| V1 | 81.4% | — | −6.0pp |
| V2 | 84.32% | ±0.65 | −0.28pp |
| V3 | 82.33% | ±0.48 | −2.12pp |

- MMLU by category for V3 vs stock[^obliteratus]. **Reported**:

| Category | V3 | Stock | Delta |
| --- | --- | --- | --- |
| Humanities | 83.3% | 84.3% | −1.0pp |
| Social Sciences | 87.4% | 89.2% | −1.8pp |
| Other | 82.3% | 84.1% | −1.8pp |
| STEM | 78.5% | 81.8% | −3.3pp |

- Card notes the cost is non-uniform: philosophy and European history improved (+6pp and +4pp), while abstract algebra and formal logic saw larger drops, interpreted by the card as refusal directions partially overlapping structured-reasoning pathways[^obliteratus]. **Reported**; sub-subject deltas are stated without absolute scores.
- Liberation quality is scored by manual audit for real substance rather than regex absence of refusal phrases; the card reports hard refusals removed in all versions, soft deflections remaining in V2 and removed in V3, 20/20 on its 20-prompt code-generation set for V3, and thinking-mode compatibility restored in V3[^obliteratus]. **Reported**; prompt contents excluded (see coverage limits).
- Advanced real-world tasks: V3 and stock both 7/8; the only failure for both is multi-tool chain, with ReAct loop, async refactoring, JSON extraction, K8s debugging, adversarial instruction following, security review, and distributed design passing[^obliteratus]. **Reported**.

## Safety and intended use

- The card states safety guardrails are surgically removed and the model complies with requests stock would refuse[^obliteratus]. **Reported**.
- Intended audience named by the card: alignment researchers studying refusal geometry, red-teamers evaluating post-training safety against weight surgery, safety evaluators needing an unrestricted baseline, and local-first users wanting full control of their hardware[^obliteratus]. **Reported**.
- Card-stated boundaries: not for causing real-world harm, not for users without the technical understanding to use uncensored models responsibly, and the user is solely responsible for use and generated content[^obliteratus]. **Reported**.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the official Unsloth GGUF/NVFP4 local path while OBLITERATED is the iterative-refinement abliterated alternative with its own greedy plus repetition-penalty recipe and GGUF ladder.
- Related to [Huihui Qwen3.8-27B Abliterated GGUF](huihui-qwen3.8-27b-abliterated-gguf.md) — another abliterated community GGUF family for the same base; Huihui uses layer-selective ablation with non-standard `K_L` requantization while OBLITERATED uses SVD/LEACE complementary blending with MTP plus vision restored.
- Related to [RVN Qwen3.8-27B Heretic Abliterated Uncensored GGUF](rvn-qwen3.8-27b-heretic-abliterated-gguf.md) — another refusal-removal lineage for the same base; RVN reports a three-pass ARA recipe with multilingual calibration while OBLITERATED reports V1/V2/V3 SVD/LEACE blending with manual-audit liberation scoring.
- Related to [Dirk Qwen3.8-27B Sharp-Template GGUF](dirk-qwen3.8-27b-gguf.md) — another community repackaging of the same base; Dirk changes only the chat template while OBLITERATED changes weights plus a thinking-prefill template.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — OBLITERATED is a llama.cpp-side local-inference artifact with a `--jinja` bundled-template requirement and a transformers `do_sample=False` path.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-OBLITERATED.md` inspected statically (**Observed**); no commands executed, so surgery effects, MMLU figures, liberation scores, and run recipes are **Reported**, not reproduced.
- Harmful-prompt contents, restricted-query substance, and attack-chain detail excluded as non-durable for serving decisions and disclosure-sensitive; only aggregate scores, method parameters, packaging, and serving settings are compiled.
- External artifacts uninspected: `OBLITERATUS/Qwen3.8-27B-OBLITERATED` weights and GGUF/safetensors files, `Qwen/Qwen3.8-27B` base, `OBLITERATUS` surgery repo, upstream `mlx_lm`, and llama.cpp/Ollama/LM Studio/transformers releases.
- No GPU architecture, dtype, harness revision, or significance protocol beyond lm-eval 0-shot with 5700 questions is stated; V1 stderr and per-subject absolute scores are absent.
- Decorative emoji, vibe column, and donation-adjacent credit links excluded as non-durable.

[^obliteratus]: Qwen3.8-27B-OBLITERATED model card — `../raw/Qwen3.8-27B-OBLITERATED.md` (OBLITERATUS/Pliny; Apache-2.0; base `Qwen/Qwen3.8-27B`; frontmatter plus sections V3 comparison table; Optimal Settings with temperature/repetition-penalty/token/system-prompt/thinking/sampling rows and GGUF `--jinja` note; Agentic/Long-Context table; transformers `enable_thinking=False`, `do_sample=False` snippet; How It Works V1/V2/V3 with SVD dirs/regs and 60/40 and 50/50 blends plus MTP/vision restore; Numbers MMLU overall/category/liberation/advanced tables; Refusal Removal 1000+ manually audited prompts; Research Context audience/boundary; Downloads GGUF size ladder, 29-shard 54 GB safetensors, pending MLX; Surgery Recipe code block; Key Learnings; Credits/License).
