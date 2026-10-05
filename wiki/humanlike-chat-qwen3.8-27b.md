---
type: Concept
title: Qwen3.8-27B Humanlike-Chat 2.0
description: Texting-style Qwen3.8-27B finetune built by on-policy distillation on an abliterated base, with tool-asking behavior, capability and "ishuman" evidence, KL-scored GGUF/safetensors ladder, and llama.cpp/vLLM serving.
tags: [qwen3.8, humanlike, on-policy-distillation, lora, gguf, tool-calling, vllm, llama-cpp, training]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-04-06
sources:
  - id: humanlike-card
    resource: ../raw/Qwen3.8-27B-Humanlike-Chat 2.0.md
    title: Qwen3.8-27B-Humanlike-Chat 2.0 model card (LessThanThreeAI)
  - id: humanlike-reddit
    resource: ../raw/qwen3827bhumanlikechat_20_texts_like_a_human_now.md
    title: "r/LocalLLaMA: Qwen3.8-27B-Humanlike-Chat 2.0 announcement thread (u/kvyb)"
---

`LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat` 2.0 is a merged finetune of `huihui-ai/Huihui-Qwen3.8-27B-abliterated` that texts like a person with no system prompt yet keeps tool calling and instruction following, trained with on-policy distillation (OPD) against two teachers. It matters for serving because the weights ship as a KL-scored GGUF ladder and vLLM/SGLang safetensors (GPTQ-Int4 fits 24 GB), and because the tool-asking behavior is a measurable change in function-calling behavior[^humanlike-card]. All figures are **Reported** by the author.

## Behavior

- No system prompt: short lowercase lines reacting to the user; it invents small life details on purpose. A system prompt stating it is an AI makes it say so[^humanlike-card][^humanlike-reddit]. **Reported**.
- A character card sets identity, not writing style; a one-off explicit request (formal email, numbered steps) applies to one reply, a standing one ("from now on write full sentences") persists. Personality words like "formal person" do not count as instructions[^humanlike-card]. **Reported**.
- Multi-bubble "texting" is one ordinary completion with newline-separated short lines; the author suggests splitting on short lines plus a typing delay in client apps[^humanlike-reddit]. **Reported**.
- Tool use: asks when a required argument is missing (flight example without origin) instead of guessing, and declines when no tool fits[^humanlike-card]. Thinking is on by default via `--jinja`; `reasoning_effort` accepts `low`, `medium`, `xhigh` (default), or `enable_thinking: false`[^humanlike-card]. Replies follow the user's language; only English and Russian were tested[^humanlike-card]. **Reported**.
- Text only: GGUFs are text-only; BF16 safetensors keep the base vision tower and MTP head unchanged. A commenter reports the base mmproj loaded and described an image; the author had not tried it[^humanlike-card][^humanlike-reddit]. **Reported**, community claim unverified.

## Training lineage

```text
Qwen/Qwen3.8-27B -> huihui-ai/Huihui-Qwen3.8-27B-abliterated (rev d42ca897)
  -> voice LoRA (SFT, rank 256, strength 0.4) -> 2.0 LoRA (rank 64, OPD, step 106)
  -> merged once into BF16 (= one exact rank-320 adapter over 496 language modules)
```

- v1 voice: SFT on 139,845 messages from 1,396 real plus synthetic conversations[^humanlike-card].
- 2.0: the student samples its own replies from conversation starts; teachers grade every token with exact full-vocabulary reverse KL. Chat/character teacher is the v1 voice model plus a hidden "text like a person" instruction the student never sees; instruction/tool/code teacher is the plain base, which restored capability[^humanlike-card][^humanlike-reddit]. Prompts: 3,208 real openings, 156 characters, 4,200 public tasks (1,200 tool, 1,800 instruction, 1,200 code), tool data half call, half ask-or-decline; four rounds, final run 36 steps on one H100 (~6 h)[^humanlike-card]. **Reported**.
- The author describes a custom loop: vLLM sampling at temperature 1.0, HF forward for student/teacher KL, PyTorch+PEFT AdamW on the LoRA only, adapter synced back to vLLM; TRL's GKD trainer is suggested as an off-the-shelf similar loop[^humanlike-reddit]. **Reported**; code unreleased.
- Merge check: merged BF16 vs base plus runtime rank-320 adapter mean KL 0.0023, top-1 agreement 97%, greedy identical on 11/15 turns[^humanlike-card]. **Reported**.
- Base is abliterated, so refusals are low by design[^humanlike-card]. See [Huihui Qwen3.8-27B Abliterated GGUF](huihui-qwen3.8-27b-abliterated-gguf.md).

## Evidence

Base = abliterated Huihui model, not official Qwen. Same run, thinking off, greedy, author's own BFCL/When2Call scorers (not leaderboard-comparable); small sets, so 1–3 points is noise. Hardware and engine for these evals are not stated[^humanlike-card]. **Reported**.

| Test (items) | Base | 2.0 |
| --- | ---: | ---: |
| IFBench strict (300) | 37.3 | 43.7 |
| IFEval strict prompt (541) | 81.9 | 83.5 |
| When2Call (100) | 48 | 58 |
| GSM8K (64) | 89.1 | 89.1 |
| BFCL simple / multiple (100 each) | 97 / 96 | 98 / 96 |
| BFCL irrelevance (100) | 60 | 78 |
| MMLU-Pro (200) | 78.5 | 72.5 |
| LiveCodeBench pass@1 (100) | 56 (earlier run, 30 Sep) | 51 |

Costs: knowledge (MMLU-Pro −6) and competitive code (LiveCodeBench −5) regress[^humanlike-card][^humanlike-reddit].

**ishuman v2** (blind LLM judge picks the real message among two; 50% = indistinguishable; each pair judged in both orders; 147 moments, 97 Russian): base 0.3%, base plus "text like a human" prompt 6.8%, official Qwen3.8-27B 15.1%, 2.0 23.5%. In 16 live simulated chats the judge preferred 2.0 over the base every time and over the prompted base in 96.9% of judgments[^humanlike-card]. **Reported**. Limits: single LLM judge; the voice LoRA trained on other sessions of the same chats, so 2.0 is in-distribution while baselines are not[^humanlike-card].

## Distributions and serving

Mean KL over the reference's top-20 tokens at fixed points in 5 fresh chats (underestimates full KL); reference is base plus adapter at runtime in BF16. tok/s is single-request 256-token decode on one H100 NVL (llama.cpp for GGUF, vLLM 0.27.1 for safetensors)[^humanlike-card]. **Reported**.

| File | Size (GB) | KL | tok/s | Checks |
| --- | ---: | ---: | ---: | --- |
| GGUF IQ4_XS | 15.10 | 0.0219 | 43 | all pass |
| GGUF Q4_K_M | 16.56 | 0.0218 | 50 | all but one tool turn |
| GGUF Q5_K_M | 19.24 | 0.0086 | 56 | all but one tool turn |
| GGUF Q6_K | 22.09 | 0.0047 | 46 | all pass |
| GGUF Q8_0 | 28.60 | 0.0028 | 55 | all pass |
| GGUF BF16 (2 shards) | 53.81 | 0.0017 | 36 | all pass |
| Safetensors GPTQ-Int4 | 20.62 | 0.0274 | 86 | all pass |
| Safetensors FP8 | 30.89 | 0.0079 | 72 | all pass |
| Safetensors BF16 | 55.59 | 0.0032 | 46 | all pass |

Picks: 24 GB → IQ4_XS/Q4_K_M; 32 GB → Q6_K; 48 GB+ → Q8_0. Standalone rank-320 F16 LoRA (4.67 GB) applies at scale 1.0 only to an unadapted text-only Huihui GGUF, never to the merged files[^humanlike-card].

**llama.cpp**: `llama-server --hf-repo LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF --hf-file …-IQ4_XS.gguf --jinja --ctx-size 32768 --parallel 1 --n-gpu-layers 99 --temp 1.0 --top-p 0.95 --top-k 20`; `--jinja` is needed for tool calls. Sampling defaults are the base's; voice evals used them, benchmarks used greedy[^humanlike-card].

**vLLM (24 GB, GPTQ-Int4, vLLM 0.27.1 capped at 21.9 GiB)**: `--max-model-len 8192 --max-num-seqs 4 --max-num-batched-tokens 2048 --gpu-memory-utilization 0.91 --language-model-only --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`. FP8 on 48 GB also needs `--max-num-seqs 128`; on H100 add `--linear-backend cutlass`. SGLang: point `--model-path` at the repo; the author tested mostly on vLLM[^humanlike-card][^humanlike-reddit]. **Reported**.

Quantization: all quants from one merged BF16 GGUF with `llama.cpp@95ef7fc1`; imatrix = WikiText-2 train (128×512) plus chat/tool-call mix on merged 2.0 (published); Q8_0 uses none; 96 recurrent gate tensors held at Q8_0 and 353 control tensors at F32. Architecture: dense 27B, 64 layers (48 linear, 16 full attention); context 262,144 native, start at 32,768[^humanlike-card]. **Reported**.

A free rate-limited OpenAI-compatible endpoint (IQ4_XS, scales to zero, ≥300 s client timeout, 32k context per the author) exists; community derivatives include a ninfer build and an IQ2_XXS with MTP tensors for ~12 GB, whose commenter reports a coding-agent run at 70k+ context[^humanlike-card][^humanlike-reddit]. **Reported**, community claims unverified.

## Community reception and risks

Thread reactions are mixed: praise for multi-bubble replies and de-roboted drafting; complaints that it sounds like a teenager, drifts from long persona cards (a 4,000-token corporate card still gave short replies), invents human experiences by default, and that a system prompt could achieve similar style[^humanlike-reddit]. Commenters raise scam/impersonation misuse and companionship dependence; the author's counter is that a system prompt makes it disclose being an AI[^humanlike-reddit]. **Reported** opinion, not evidence.

## Relationships

- Depends on [Huihui Qwen3.8-27B Abliterated GGUF](huihui-qwen3.8-27b-abliterated-gguf.md) — the abliterated base this model is trained on.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) and [Qwen3.8-27B Ecosystem Survey](qwen3.8-27b-survey.md) — same 27B base family.
- Uses [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) and [vLLM Tool Calling](vllm-tool-calling.md) — `qwen3` reasoning parser and `qwen3_coder` tool parser in the serving recipe.

## Coverage limits

- Both entry points inspected statically (**Observed**); no commands executed. Reddit capture is a page dump with unattributed commenters; the r/LocalLLaMA post has 868 votes per capture.
- Uninspected: images (`images/01-cover.png` … `06-benchmarks.png`, Reddit screenshots), HF repos, `SHA256SUMS`, imatrix, LoRA, demo space, ninfer and IQ2 community repos, ishuman benchmark data, and eval harnesses. The card's benchmark and "ishuman" charts are not visually checked; table values come from card text.
- Excluded: commission/contact and Discord promotion, joke and grief comments, a commenter's image-description output, and the "Absolute Mode" prompt as off-topic.
- No credentials or PII found; the commissions contact handle is deliberately omitted.

[^humanlike-card]: Model card `../raw/Qwen3.8-27B-Humanlike-Chat 2.0.md` — frontmatter; "Why download it"; Quick start; Thinking; vLLM and SGLang table; Download table; How to use it; Results (Capability, ishuman v2); How it was made; Technical details; Standalone LoRA.
[^humanlike-reddit]: Reddit thread `../raw/qwen3827bhumanlikechat_20_texts_like_a_human_now.md` — post body ("What 2.0 does now", "How I trained it", Numbers, ishuman, Edit) and author replies in Comments (training method, newline bubbles, system-prompt disclosure, safetensors, imatrix, community quants).
