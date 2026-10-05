---
type: Concept
title: ThinkingCap Qwen3.8-27B
description: Thinking-efficient BottleCap finetune of Qwen3.8-27B cutting reasoning tokens ~37% at ~0.8pp accuracy cost with H200 vLLM 0.29.0 evidence and vLLM/SGLang MTP plus five quant serving.
tags: [qwen3.8, thinkingcap, efficient-thinking, reasoning, mtp, serving, quantization]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T22:00:00Z }
stale_after: 2027-04-05
sources:
  - id: thinkingcap-qwen38
    resource: ../raw/ThinkingCap-Qwen3.8-27B.md
    title: ThinkingCap Qwen3.8-27B model card
---

BottleCap AI publishes `bottlecapai/ThinkingCap-Qwen3.8-27B` as a thinking-efficient finetune of `Qwen/Qwen3.8-27B` that cuts mean thinking tokens by about 37% (macro average of per-benchmark reductions) at a macro-average accuracy of 85.8% versus 86.6% for the base, measured on H200 with vLLM 0.29.0 plus MTP self-speculation at `reasoning_effort=xhigh`, with vLLM/SGLang serving recipes and five quantized distributions[^thinkingcap-qwen38]. **Reported** throughout; no weights, commands, or benchmarks were executed here.

## Release identity

- Repository `bottlecapai/ThinkingCap-Qwen3.8-27B`; `base_model: Qwen/Qwen3.8-27B` with `base_model_relation: finetune`; `library_name: transformers`; tags `qwen3_8`, `token-efficient`, `efficient-thinking`; second installment of the ThinkingCap series[^thinkingcap-qwen38]. **Reported**, with static frontmatter presence **Observed**.
- Upstream base is `Qwen/Qwen3.8-27B` (Qwen Team, 2026); model link and blogpost `https://bottlecapai.com/post/thinkingcap-qwen3-8-27b/` are referenced but uninspected[^thinkingcap-qwen38]. **Reported** with that limit.
- License is PolyForm Small Business 1.0.0 plus a BottleCap personal-use grant (see `LICENSE`); upstream Qwen materials are Apache-2.0 (see `NOTICE`); commercial licensing via `enterprise@bottlecapai.com`[^thinkingcap-qwen38]. **Reported**.
- Gated-access form requests Name, Company name, and Work email with an enterprise-upsell prompt; field names preserved as access-boundary evidence, not sensitive values[^thinkingcap-qwen38]. **Observed**.
- Citation is a 2026 `@misc{ThinkingCap-Qwen3.8-27B}` entry with 12 authors (Osusky, Lindauer, Jirkovsky, Mihal, Platek, Herel, Ihnatchenko, Bartek, Jirak, Kubista, Krus, Mikolov)[^thinkingcap-qwen38]. **Reported**.

## Thinking-efficiency headline and 12-benchmark table

Headline figures compare base `Qwen/Qwen3.8-27B` against `bottlecapai/ThinkingCap-Qwen3.8-27B` (shown as Ours): about 37% fewer reasoning tokens on average (11% to 66% by benchmark) at 85.8% versus 86.6% average accuracy; long-context retrieval cuts reasoning 39% with accuracy intact (+2.3pp)[^thinkingcap-qwen38]. **Reported**; per the SCOPE benchmark rule the comparison states hardware (H200), engine (vLLM 0.29.0), model pair, benchmark workloads, and metrics (accuracy plus mean `<think>` tokens), but remains vendor-reported with no independent run.

| Benchmark | Base accuracy | Ours accuracy | Base mean thinking | Ours mean thinking | Reduction |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPQA-Diamond | 89.93 ±0.70 | 88.04 ±1.09 | 12,772 | 7,267 | ↓ 43.1% |
| MMLU-Pro | 85.54 ±0.63 | 84.67 ±0.64 | 3,725 | 1,591 | ↓ 57.3% |
| MMMLU | 85.38 ±0.69 | 84.09 ±0.72 | 1,656 | 571 | ↓ 65.5% |
| AIME 2026 | 98.13 ±0.74 | 94.27 ±1.47 | 15,663 | 10,934 | ↓ 30.2% |
| HMMT (Feb 2026) | 95.83 ±1.16 | 94.70 ±1.50 | 23,211 | 18,099 | ↓ 22.0% |
| HMMT (Nov 2025) | 97.08 ±1.43 | 96.04 ±2.17 | 14,443 | 10,037 | ↓ 30.5% |
| LiveCodeBench v6 | 91.14 ±1.11 | 91.21 ±1.28 | 28,395 | 22,645 | ↓ 20.3% |
| AA-LCR | 81.75 ±1.07 | 84.00 ±0.77 | 2,550 | 1,565 | ↓ 38.6% |
| RealWorldQA | 83.25 ±0.73 | 82.34 ±0.71 | 992 | 492 | ↓ 50.4% |
| IFBench | 79.75 ±0.63 | 79.71 ±0.60 | 7,961 | 4,266 | ↓ 46.4% |
| τ²-bench | 76.16 ±1.52 | 75.15 ±1.67 | 4,584 | 3,168 | ↓ 30.9% |
| Terminal-Bench 2.1 | 75.84 ±4.26 | 75.28 ±4.38 | 72,871 | 65,092 | ↓ 10.7% |
| Macro average | 86.6 | 85.8 | 15,735 | 12,144 | ↓ 37.2% |

- Accuracy is fraction correct; τ²-bench is an unweighted mean over airline, retail, and telecom domains, not pooled over tasks[^thinkingcap-qwen38]. **Reported**.
- Thinking tokens are the mean `<think>`-trace length excluding the answer; τ²-bench and Terminal-Bench 2.1 sum reasoning over every turn of the episode (about 15 and 40 turns on average), not a single trace[^thinkingcap-qwen38]. **Reported**.
- Reduction is `(Ours − Base) / Base` on the two mean columns; the macro-average bottom row is the equal-weight mean of the per-benchmark reductions, not the ratio of the two token figures beside it[^thinkingcap-qwen38]. **Reported**.
- Deltas favoring Ours: AA-LCR +2.25pp (84.00 − 81.75) and LiveCodeBench v6 +0.07pp; all other rows favor the base by 0.04pp (IFBench) to 3.86pp (AIME 2026) (**Synthesis** arithmetic on the reported table).
- Trace-quality failure modes both stay below 1% and improve on an equal-weight basis: truncation 0.51% → 0.34% and looping 0.06% → 0.05%; single-turn truncation means the `<think>` trace never closes before the generation cap, while multi-turn truncation is episode-level (any capped turn flags τ²-bench; a three-hour budget exhaustion flags Terminal-Bench and scores 0), and looping is a compression-ratio test on single-turn rows plus the harness stalled-turn rule on Terminal-Bench[^thinkingcap-qwen38]. **Reported**.

## Evaluation protocol

- Serving: NVIDIA H200, vLLM 0.29.0 with MTP speculative decoding (`num_speculative_tokens=3`); thinking on at `reasoning_effort=xhigh` (chat-template default); base-model recommended sampling `temperature=1.0, top_p=0.95, top_k=20, min_p=0.0` used unchanged for Ours[^thinkingcap-qwen38]. **Reported**; engine-version snapshot covered by `stale_after`.
- Generation caps: 253,952 tokens for most benchmarks; 131,072 for AA-LCR and 65,536 for τ²-bench because documents and multi-turn transcripts occupy the rest of the window[^thinkingcap-qwen38]. **Reported**.
- Completeness: eleven benchmarks run the complete set (AIME 2026: 30 problems; HMMT Feb 2026: 33; HMMT Nov 2025: 30; GPQA-Diamond: 198; IFBench: 300; RealWorldQA: 765; AA-LCR: 100; τ²-bench: 278 tasks; Terminal-Bench 2.1: 89 tasks under the Terminus-2 agent in Harbor; LiveCodeBench v6: 175; MMLU-Pro: 12,032, the whole test split); MMMLU is the one subset, a 10,000-question random sample drawn with a fixed seed so every condition sees the same questions[^thinkingcap-qwen38]. **Reported**.
- Seeds and intervals: 32 seeds on AIME 2026; 16 on GPQA-Diamond, both HMMTs, and IFBench; 8 on LiveCodeBench v6, AA-LCR, RealWorldQA, and τ²-bench; 4 on Terminal-Bench 2.1; single seed on MMLU-Pro and MMMLU; multi-seed rows show 95% t-intervals across seeds at temperature 1.0, while the two single-seed rows show 95% Wilson intervals over question outcomes, and the card warns the two variance sources should not be read against each other[^thinkingcap-qwen38]. **Reported**.

## Thinking-mode guidance

- The card recommends `xhigh` for the best accuracy-versus-token balance; at lower efforts the ThinkingCap treatment amplifies the effort setting while keeping its original trade-off, and improving individual thinking modes is planned for a future release[^thinkingcap-qwen38]. **Reported**.
- The per-benchmark effort-frontier chart (`effort-frontier-per-benchmark-light/dark.png`) is referenced but absent from `raw/` and excluded as uninterpretable from text alone[^thinkingcap-qwen38]. **Reported** with that limit.

## Serving and MTP speculation

Recipes are **Reported** and unrunnable here; engine versions are snapshots covered by `stale_after`[^thinkingcap-qwen38].

### Transformers

```python
from transformers import AutoModelForImageTextToText, AutoProcessor
model = AutoModelForImageTextToText.from_pretrained("bottlecapai/ThinkingCap-Qwen3.8-27B", dtype="bfloat16")
proc = AutoProcessor.from_pretrained("bottlecapai/ThinkingCap-Qwen3.8-27B")
```

- Card defers to `https://huggingface.co/Qwen/Qwen3.8-27B` for recommended usage and sampling parameters[^thinkingcap-qwen38]. **Reported**.

### vLLM and SGLang

```bash
# vLLM — standard
vllm serve bottlecapai/ThinkingCap-Qwen3.8-27B \
  --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_xml
# vLLM — with MTP self-speculative decoding
vllm serve bottlecapai/ThinkingCap-Qwen3.8-27B \
  --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_xml \
  --speculative-config '{"method":"mtp","num_speculative_tokens":3}'

# SGLang — standard
python -m sglang.launch_server --model-path bottlecapai/ThinkingCap-Qwen3.8-27B --trust-remote-code \
  --reasoning-parser qwen3 --tool-call-parser qwen3_coder
# SGLang — with MTP self-speculative decoding
python -m sglang.launch_server --model-path bottlecapai/ThinkingCap-Qwen3.8-27B --trust-remote-code \
  --reasoning-parser qwen3 --tool-call-parser qwen3_coder \
  --speculative-algorithm EAGLE --speculative-num-steps 3 \
  --speculative-eagle-topk 1 --speculative-num-draft-tokens 4
```

- The reasoning parser separates thinking into `reasoning` (`reasoning_content` on SGLang) instead of inline `content` before `</think>`; the tool-call parser turns XML tool calls into structured `tool_calls` with the same flags as the base-model recipes[^thinkingcap-qwen38]. **Reported**.
- The native MTP (multi-token-prediction / NextN) head gives self-speculative decoding with no separate draft model; it preserves the sampling distribution on average while individual sampled outputs can differ[^thinkingcap-qwen38]. **Reported**.
- Per the speculative-decoding domain rule, acceptance is stated with workload and pair: on bf16 weights under vLLM 0.29.0 with `num_speculative_tokens=3`, Ours accepted 53% of drafted tokens across the xhigh evaluation runs (about 2.6 tokens per decoding step, identical to the base's 54% and 2.6), ranging from 2.5 on LiveCodeBench to 2.9 on τ²-bench and AA-LCR; shorter `medium`/`low` traces lift this to 3.2–3.3[^thinkingcap-qwen38]. **Reported**.

### OpenAI-compatible request with effort knob

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="-")   # SGLang: port 30000
r = client.chat.completions.create(
    model="bottlecapai/ThinkingCap-Qwen3.8-27B",
    messages=[{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": "https://example.com/photo.jpg"}},
        {"type": "text", "text": "What is happening in this picture?"},
    ]}],
    temperature=1.0, top_p=0.95,
    extra_body={"top_k": 20,
                "chat_template_kwargs": {"reasoning_effort": "xhigh"}},   # xhigh (default) | medium | low
)
print(r.choices[0].message.reasoning)               # the thinking (`reasoning_content` on SGLang)
print(r.choices[0].message.content)                 # the answer
```

- One request covers text, images, and the thinking-effort knob; a text-only request uses a plain string as `content`[^thinkingcap-qwen38]. **Reported**.

## Quantized distributions

Same checkpoint, chat template, and license; no accuracy-versus-BF16 table is given for these quants in this card, so per the quantization domain rule only size, format, engine, and hardware fit are recorded[^thinkingcap-qwen38]. **Reported**.

| Distribution | Format and serving | Size and hardware |
| --- | --- | --- |
| FP8 (`ThinkingCap-Qwen3.8-27B-FP8`) | FP8 block-wise, vLLM | 31 GB; Hopper and Blackwell |
| GGUF (`ThinkingCap-Qwen3.8-27B-GGUF`) | IQ4_XS to f16; llama.cpp / LM Studio / Ollama | 16–55 GB; CUDA, Apple Metal, Vulkan, or CPU |
| NVFP4 (`ThinkingCap-Qwen3.8-27B-NVFP4`) | NVFP4 weight-only, vLLM | 21 GB; Hopper (Marlin kernel) and Blackwell |
| NVFP4 W4A4 (`ThinkingCap-Qwen3.8-27B-NVFP4A4-AWQ`) | NVFP4 weights and activations (AWQ), vLLM | 23 GB; Blackwell only |
| MLX 4-bit DWQ (`ThinkingCap-Qwen3.8-27B-MLX-4bit-DWQ`) | Mixed 4/8-bit DWQ; mlx-vlm / oMLX | 22.5 GB; Apple Silicon (32 GB Mac) |

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense-family local path; this page is the thinking-efficient BottleCap finetune alternative with its own 12-benchmark Base-vs-Ours evidence and MTP plus five-quant serving.
- Related to [Swift-Qwen3.8-27B GGUF](swift-qwen3.8-27b-gguf.md) — sibling thinking-efficient Qwen3.8-27B line reporting 58.3% fewer tokens at under 1% loss; Swift's card states its transfer component derives from BottleCap's `ThinkingCap-Qwen3.6-27B`, a different ThinkingCap generation from the Qwen3.8 finetune compiled here (**Synthesis** from the two cards).
- Uses [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native MTP self-speculation shape (`method: mtp`, no separate draft model) shared with the vLLM `num_speculative_tokens=3` runs reported here.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — EAGLE-path MTP serving shape (`EAGLE`, 3 steps, topk 1, 4 draft tokens) shared with the SGLang MTP runs reported here.
- Uses [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) — `qwen3` reasoning-parser separation behind the `reasoning` versus `content` split used here.
- Uses [SGLang Reasoning Parser](sglang-reasoning-parser.md) — `qwen3` reasoning-parser separation behind the `reasoning_content` versus `content` split used here.

## Coverage limits

- Entry point `../raw/ThinkingCap-Qwen3.8-27B.md` inspected statically (**Observed**); no commands executed, so install/serve recipes, token counts, scores, acceptance figures, and picks are **Reported**, not reproduced.
- Referenced local artifacts absent from `raw/` and uninspected: `cap_header.png`, `thinkingcap_demo.mp4`, effort-frontier light/dark PNGs, and social icons; demo-video content is excluded beyond its existence.
- External evidence uninspected: BottleCap blogpost, `Qwen/Qwen3.8-27B` base card, five quantized HF repositories, `LICENSE`/`NOTICE` texts, vLLM 0.29.0 and SGLang builds, H200 evaluation harness, and UkisAI/Swift transfer lineage.
- No file revision or snapshot hash is stated; hardware beyond the H200 evaluation runs, harness version, variance beyond the stated seed/Wilson intervals, and significance tests are unstated, so benchmark-rule figures stay **Reported**.
- No credentials, keys, or PII were found in the source; the gated-access name/company/email fields are access boundaries, not sensitive values (**Observed**).

[^thinkingcap-qwen38]: ThinkingCap Qwen3.8-27B model card — `../raw/ThinkingCap-Qwen3.8-27B.md` (BottleCap AI; base `Qwen/Qwen3.8-27B`; frontmatter `base_model_relation: finetune`, `library_name: transformers`, PolyForm Small Business 1.0.0; sections intro headline, Token efficiency and benchmark performance 12-row plus macro-average table, Evaluation details with Models / Metrics / Serving / Benchmarks / Seeds-and-intervals collapsible, Thinking mode comparison, Usage with Transformers plus vLLM/SGLang MTP commands plus OpenAI effort-knob example, Quantized versions five-row table, Where to find us, License, Citation): 37% (11–66%) fewer reasoning tokens at 85.8% vs 86.6% with AA-LCR 39% / +2.3pp note; per-benchmark accuracy ± intervals plus mean thinking-token and reduction columns with truncation 0.51→0.34% and looping 0.06→0.05% limits; H200 / vLLM 0.29.0 / MTP-3 / xhigh / temp-1.0-top_p-0.95-top_k-20-min_p-0.0 protocol with 253,952 (AA-LCR 131,072; τ² 65,536) caps, 11-complete-plus-MMMLU-10k-fixed-seed scope, and 32/16/8/4/1-seed t-versus-Wilson interval method; xhigh recommendation with lower-effort amplification and future-modes note plus uninterpretable frontier chart; bf16 Transformers loader, qwen3/qwen3_xml/qwen3_coder parser commands, lossless-on-average MTP with 53% vs 54% and 2.6 tokens/step (2.5–2.9 by workload, 3.2–3.3 at medium/low) acceptance, and xhigh/medium/low effort-knob API; FP8 31 GB, GGUF 16–55 GB, NVFP4 21 GB, NVFP4-W4A4-AWQ 23 GB, and MLX-4bit-DWQ 22.5 GB distributions with engine plus hardware fit and no quant-fidelity table; PolyForm-plus-personal-grant with Apache-2.0 upstream and enterprise contact, gated name/company/email fields, and 12-author 2026 citation.
