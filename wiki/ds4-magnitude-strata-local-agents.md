---
type: Concept
title: ds4, Magnitude and Strata Local Agent Engines
description: Self-reported comparison of ds4, Magnitude and Strata against llama.cpp, vLLM, Ollama and SGLang for local agentic workloads, with hardware fit, speed caveats, prefix-cache behavior and hosted-cost arithmetic.
tags: [serving, local-inference, ds4, magnitude, strata, llamacpp, agents, prefix-caching]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-04T15:00:00Z }
stale_after: 2027-04-04
sources:
  - id: stackness-local-agents
    resource: ../raw/llama-cpp-alternatives-for-running-local-agents-ds4-magnitude-and-strata-against/index.md
    scope: ../raw/llama-cpp-alternatives-for-running-local-agents-ds4-magnitude-and-strata-against/
    kind: article
    title: "Llama.cpp alternatives for running local agents: ds4, Magnitude and Strata against llama.cpp, vLLM and Ollama"
---

The three llama.cpp alternatives prominent 24 September–2 October 2026 each optimize for a different local-agent fit — ds4 for one session on a few large MoE models on a big-memory Mac or DGX Spark, Magnitude for device-tuned kernels over small/mid-size models with several sessions, Strata for one-click single-model install on a gaming PC — and every headline speed number behind them is self-reported by its own project, while a worked SWE-Bench example shows hosted APIs remain cheaper on tokens alone and prefix reuse matters more than raw decode speed[^stackness-local-agents].

## Positioning

| Engine | Optimizes for | Models (3 Oct 2026) | Hardware today | Licence | Latest (**Reported**) |
| --- | --- | --- | --- | --- | --- |
| ds4 | One session, a few big models, its own coding agent | DeepSeek V4 and V4.1 Flash, V4 Pro, GLM 5.2 and 5.3, Qwen 3.8 Flash Next | Metal, CUDA, ROCm on Strix Halo | MIT | No releases; last commit 20 September[^stackness-local-agents] |
| Magnitude | Kernels tuned on your device, several sessions | Qwen 3.5–3.8 up to 35B, Gemma 4, LFM2.5, MiniCPM5 | Metal, CUDA, Vulkan, CPU | Apache 2.0 | 0.2.4, 2 October[^stackness-local-agents] |
| Strata | One-click install of one model | Qwen 3.8 Flash Next only | NVIDIA RTX 20–50, selected AMD; Windows and Linux | MIT | v0.1.38, 3 October[^stackness-local-agents] |
| llama.cpp | Any GGUF model on almost any hardware | Most open architectures; V4.1 support still an open PR | Metal, CUDA, HIP, Vulkan, SYCL, CPU and more | MIT | Build b11371, 3 October[^stackness-local-agents] |
| vLLM | Serving throughput, batching, multi-GPU | V4.1 Flash, GLM 5.3 Flash, Flash Next | NVIDIA, AMD, Intel, CPUs | Apache 2.0 | v0.30.0, 22 September[^stackness-local-agents] |
| Ollama | Ease of install and agent integrations | Its library: Qwen 3.8 27B local, GLM 5.3 cloud only | NVIDIA, AMD, Apple silicon | MIT | v0.35.1, 29 September[^stackness-local-agents] |
| SGLang | Agentic and large-scale serving, prefix cache | V4.1 Flash, GLM 5.3 Flash, Flash Next | NVIDIA, AMD Instinct, TPU, Apple | Apache 2.0 | v0.5.21, 2 October[^stackness-local-agents] |

- ds4 is "deliberately narrow, not a general GGUF runner": it loads only GGUF files the project produces, and a model "may be removed when a better replacement arrives" (**Reported** README claim via source)[^stackness-local-agents].
- ds4 is not new: Salvatore Sanfilippo (antirez, creator of Redis) started it in May 2026 in C; the 2 October Hacker News post linked a community site, not the project (**Reported**)[^stackness-local-agents].
- Magnitude's launch post (YC S25) places vLLM and SGLang in the datacenter, llama.cpp and Ollama at broad compatibility, and ds4 as specialised but "lacking engine completeness"; per-device tuning takes "around ~1 minute whenever you download a new model" (**Reported**)[^stackness-local-agents].
- **Synthesis:** this is the same generality-vs-peak-throughput tradeoff as [Narrow Single-Model Inference Engines](narrow-inference-engines.md) — ds4 and Strata trade model/hardware generality for in-lane fit, Magnitude trades a tuning minute for device fit.

## Speed claims and who measured them

All headline numbers come from the projects themselves; the only outside evidence is HN replies and community runs filed in the projects' own repos (**Reported**)[^stackness-local-agents].

| Claim | Setup (**Reported**) | Outside check (**Reported**) |
| --- | --- | --- |
| Magnitude "92% faster decode on Metal, 19% on CUDA" than llama.cpp — i.e. 1.9x decode, 1.09x prefill | Qwen 3.6 35B-A3B, 4-bit, 64K context. M4 Pro: decode 30→57 tok/s, prefill 466→507. DGX Spark: decode 49→58. llama.cpp on 16-bit KV cache vs Magnitude on 8-bit keys / 4-bit values | Four HN users saw llama.cpp or MLX engines match or beat it on other hardware[^stackness-local-agents] |
| ds4 DeepSeek V4 Flash Q2 | M5 Max 128 GB: 39.4 tok/s generation at 2K context, 27.6 at 64K. DGX Spark: 18.1 and 13.8. Described by ds4 as "a baseline, not a fresh benchmark of every commit" | Volunteers ran 76 of 100 random SWE-Bench Verified instances on an M5 Max (issue #389)[^stackness-local-agents] |
| Strata Qwen 3.8 Flash Next "94 tok/s" writing, 2,650 tok/s reading a 32K prompt, MTP speculative decoding on | RTX 5070 12 GB | Community RTX 5090 run: 179 tok/s at 4K prompt, 165 at 128K[^stackness-local-agents] |

Catches on the Magnitude comparison (**Reported**)[^stackness-local-agents]:

- Its "27% less memory per agent" comes from the same lighter KV cache, not just the engine.
- Its own engine was days old at measurement: release 0.2.0, about four hours before the Launch HN, replaced "the llama.cpp-based inference engine with Magnitude's own engine".
- HN counter-reports: one RTX 5070 Ti user found llama.cpp "about 20–30% faster at decode"; one M5 Max user found it "roughly 2x faster"; a third measured Rapid-MLX at 175 tok/s against Magnitude's 161; founders attributed the M5 gap to unused Metal 4 matrix units.

Per the SCOPE benchmark rule these are **Reported** snapshots, not comparable benchmarks: engine versions and hardware are partly stated but quantization, KV-cache precision, batch/concurrency and protocol differ across projects.

## Hardware fit

- **ds4:** README says Metal is "the primary target, on Macs with 96 GB or more"; its Qwen 3.8 file is "the starting option for 64 GB Macs" with weights streamed from SSD; DeepSeek V4.1 Flash does not fit on one 128 GB machine — needs SSD streaming, two machines over RDMA, or a 512 GB Mac; no Vulkan, no Intel GPUs (**Reported**)[^stackness-local-agents].
- **Magnitude:** Metal on macOS 15, CUDA from Ampere up, Vulkan, CPU; docs say "not currently ship a ROCm backend", multi-GPU "on our near-term roadmap" (**Reported**)[^stackness-local-agents].
- **Strata:** keeps hottest experts in VRAM, rest in RAM, n-gram table on SSD; stated minimum VRAM moved 8 GB (28 Sep HN title) → 12 GB (README) → "a 6 GB card starts" (v0.1.38); no Mac support (**Reported**)[^stackness-local-agents].
- llama.cpp still runs on the widest range (**Reported**)[^stackness-local-agents].
- Qwen 3.8 Flash Next parameter counting differs: 125B with 6B active, ~180B counting n-gram embeddings plus draft layer per its model card; Strata quotes the first, Magnitude's catalog the second (**Reported**)[^stackness-local-agents].
- No single model runs on all three new engines today: Magnitude's catalog switches off the big MoE models including Qwen 3.8 Flash Next and DeepSeek V4 Flash, marked "not implemented yet" (**Reported**)[^stackness-local-agents].

## Agent economics: local vs hosted

On cost alone hosted is cheaper for almost everyone; local pays for privacy, offline work, no rate limits and research, not the token bill (**Reported** source conclusion)[^stackness-local-agents].

Worked example from a volunteer run of 20 SWE-Bench Verified instances (ds4 issue #389, 27 July): per instance 653 s, 45 model calls, 1,147,283 prompt tokens (98.6% cached), 13,873 output tokens (**Reported** run data via source)[^stackness-local-agents].

Source arithmetic at DeepSeek prices per million tokens on 3 October (**Reported**)[^stackness-local-agents]:

| Model, hosted | Input | Cached input | Output | That task |
| --- | --- | --- | --- | --- |
| DeepSeek V4.1 Flash, peak | $0.30 | $0.006 | $1.20 | $0.028 |
| DeepSeek V4.1 Flash, off-peak | $0.15 | $0.003 | $0.60 | $0.014 |

- A machine running such tasks around the clock finishes ~132/day, worth ~$3.72/day at peak hosted prices (~$1,360/year before electricity); a 128 GB Framework Desktop lists at $3,449 (out of stock) and a DGX Spark Founders Edition reseller lists at $4,699 (**Reported** prices via source)[^stackness-local-agents].
- **Synthesis:** comparison is rough — the local run used V4 Flash at 2-bit while DeepSeek serves V4.1 Flash — so treat payback as directional, not a quote.
- Agent implication: with 98.6% of prompt tokens repeated, prefix reuse matters more than raw decode speed, and a local engine must keep KV cache warm across turns — ds4 keeps it on disk across restarts, Magnitude shares prefixes across sessions, Strata caches one conversation at a time (**Reported**)[^stackness-local-agents].

## Feature gaps

| Need | ds4 | Magnitude | Strata | llama.cpp (**Reported**) |
| --- | --- | --- | --- | --- |
| OpenAI and Anthropic APIs | Yes | Yes | Yes | Yes[^stackness-local-agents] |
| Responses API (Codex) | Yes | Yes | No, requested in #451 | Yes[^stackness-local-agents] |
| Several requests at once | Native on Metal; in order on one CUDA GPU | Yes, sharing prefixes | "One request at a time" | Yes[^stackness-local-agents] |
| Releases | None, "beta quality" | Since 0.2.0, own engine | 38 in nine days | Rolling builds[^stackness-local-agents] |

- **ds4:** Qwen 3.8 Flash Next lacks tensor parallelism, SSD streaming and ROCm; open issues include a stall when a tool call follows an unclosed think block (**Reported**)[^stackness-local-agents].
- **Strata:** one model, one request, no Mac; first start can freeze the PC 1–3 minutes while 35–55 GB loads (**Reported**)[^stackness-local-agents].
- **llama.cpp:** DeepSeek V4.1 support is an open pull request (#28696, opened 10 September) (**Reported**)[^stackness-local-agents].

## Decision-model runtime slot

Different output, unit and model size: these engines serve chat completions and tool calls from ~1B–750B models in tokens/s, while a decision-model runtime such as Ollaya serves typed questions from small encoders in ms/question (**Reported** framing via source)[^stackness-local-agents].

- Overlap: Ollama 0.35.0 (28 September) added decision models via `/v1/systemone`, "based on TypeSafe's Jev API", so a chat engine and decision runtime can now be the same daemon (**Reported**)[^stackness-local-agents].

## Relationships

- Related to [Narrow Single-Model Inference Engines](narrow-inference-engines.md) — ds4/Strata as deliberately narrow engines trading generality for in-lane fit; this concept adds the Magnitude device-tuning position plus versions, licences and agent-cost arithmetic.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — the general-purpose baseline (llama.cpp for consumer single-user, vLLM for high-concurrency GPU serving) these three alternatives position against.
- Related to [Ollama vs vLLM vs SGLang Serving Choice](ollama-vs-vllm-vs-sglang.md) — Ollama-easiest / vLLM-throughput / SGLang-prefix-cache framing complementary to the per-engine agent table here.
- Related to [Strata Tiered MoE Offload Engine](strata-tiered-moe-offload.md) — the VRAM/RAM/SSD tiering behind Strata's single-model fit; see also [Strata Qwen3.8-Flash-Next Quants and Measured Speed](strata-qwen3.8-flash-next-quants-performance.md) and [Strata MTP and Prompt-Lookup Speculation](strata-speculative-decoding.md) for the 94 tok/s MTP-on context.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — Unsloth GGUF plus llama.cpp route for the same model Strata and ds4's Qwen file target.
- Related to [Qwen3.6 Local Deployment](qwen3.6.md) — the Qwen 3.6 35B-A3B model in the Magnitude-vs-llama.cpp comparison.

## Coverage limits

- Source identity is the Stackness article capture `raw/llama-cpp-alternatives-for-running-local-agents-ds4-magnitude-and-strata-against/` (entry `index.md` plus decorative hero `assets/image.png`, excluded); linked GitHub repos, HN threads (#49936575, #49911995), model cards, DeepSeek/Z.ai/Qwen pricing pages, ds4 issue #389, llama.cpp PR #28696 and Strata issue #451 were not inspected beyond the article's account.
- All speed, memory-saving, price and version figures are **Reported** as of 3–4 October 2026 with `stale_after` set per the serving domain rule; no command was executed here.
- Stackness profile-count snapshot (1 profile lists Ollama, 1 LM Studio, 0 list llama.cpp/vLLM/MLX/Magnitude) excluded as transient directory data with no serving-decision reuse value.
- No sensitive values found.

[^stackness-local-agents]: Sergei Gordeichuk, "Llama.cpp alternatives for running local agents: ds4, Magnitude and Strata against llama.cpp, vLLM and Ollama" — `../raw/llama-cpp-alternatives-for-running-local-agents-ds4-magnitude-and-strata-against/index.md` (Stackness, published 2026-10-04), sections "What does each local inference engine optimize for, and for whom?", "Which speed claims are published, and who measured them?", "Which hardware does each engine support today?", "When is a local engine worth it for an agent workload, and when is a hosted API still cheaper?", "How is this slot different from the decision-model runtime slot?", "What is missing from each engine right now?", "Key numbers" and "Quick answers", covering the 7-engine comparison table (licences, versions to 3 Oct 2026), Magnitude 1.9x/1.09x with KV-cache and HN counter-report caveats, ds4 39.4 tok/s and Strata 94 tok/s self-reported figures, ds4/Magnitude/Strata hardware and API/concurrency gaps, 98.6%-cached SWE-Bench cost arithmetic ($0.028/task vs $3,449/$4,699 hardware), and Ollama 0.35.0 `/v1/systemone` overlap.
