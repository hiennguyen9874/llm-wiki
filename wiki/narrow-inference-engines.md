---
type: Concept
title: Narrow Single-Model Inference Engines
description: Single-model, single-hardware inference engines that trade generality for 2–4x local throughput, with model-lifespan lock-in as the buying risk.
tags: [serving, local-inference, inference-engines, llamacpp, vllm, qwen3.8-flash-next, qwen3.6]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-05T12:00:00Z }
stale_after: 2027-04-04
sources:
  - id: narrow-engines-sf
    resource: ../raw/a-wave-of-narrow-ai-inference-engines-is-beating-vllm-and-llamacpp-at-their-own/index.md
    scope: ../raw/a-wave-of-narrow-ai-inference-engines-is-beating-vllm-and-llamacpp-at-their-own/
    kind: article
    title: "A wave of narrow AI inference engines is beating vLLM and llama.cpp at their own game"
  - id: overfit-post
    resource: ../raw/the-rise-of-overfit-inference-engines/index.md
    scope: ../raw/the-rise-of-overfit-inference-engines/
    kind: article
    title: "The Rise of Overfit Inference Engines"
  - id: strata-thread-sep30
    resource: ../raw/qwen38-flash-next-istadaslab-gguf-50ts-tg-and/index.md
    scope: ../raw/qwen38-flash-next-istadaslab-gguf-50ts-tg-and/
    kind: discussion
    title: "Qwen3.8 flash next ISTA-DASLab GGUF 50t/s TG and 1500t/s PP with 12GB VRAM and 64GB RAM Laptop on 'Strata' engine (r/LocalLLaMA)"
  - id: strata-video-6x
    resource: ../raw/the-new-way-to-run-125b-models-6x-faster-than-llama.cpp-(strata).md
    kind: video
    title: "The New Way to Run 125B Models 6x Faster Than llama.cpp (Strata) (YouTube transcript)"
  - id: strata-thread-bots
    resource: ../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/index.md
    scope: ../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/
    kind: discussion
    title: "Yes bots we get it, Strata is good now please stop (r/LocalLLaMA)"
  - id: ninfer-readme
    resource: ../raw/ninfer.md
    kind: documentation
    title: "NInfer"
  - id: ninfer-4080-thread
    resource: ../raw/i_built_ninfer_4080_for_16gb_class_gpus.md
    kind: discussion
    title: "I built Ninfer 4080 for 16GB class GPUs"
---

A cluster of narrow inference engines built for exactly one model family and one GPU family is outrunning general-purpose runtimes in its lane by roughly 2–4x, by giving up model and hardware generality on purpose; the buying risk is not a fake number but a conditional one — swap the model, change the GPU, or wait for the next release and the engine may not support it[^narrow-engines-sf][^overfit-post]. All figures below are **Reported** as stated by the cited source without independent verification here; the Carteakey firsthand post is now compiled directly alongside the secondhand Startup Fortune summary.

## What counts as narrow

- Named engines are Strata, ninfer, DwarfStar, Splash, llamAmpere, and gufo, collectively called "napkin runtimes" — disposable, overfit engines for the meal in front of you (**Reported**)[^narrow-engines-sf][^overfit-post].
- The stated pattern: one model or a short model list, one hardware family or a narrow hardware set, and optimization passes aimed at those combinations (**Reported**)[^narrow-engines-sf][^overfit-post].
- By normal software standards these can look like bad codebases — tightly coupled, hard to port, built around narrow assumptions — and in inference those trade-offs are part of why they are fast: they shape the compute graph, memory layout and kernels around the chosen model and hardware (**Reported**, author characterization)[^overfit-post].
- The source post is explicit that none of these runtimes are general-purpose (**Reported**)[^narrow-engines-sf][^overfit-post].

### The six-engine set (firsthand table)

| Engine | Target hardware | Models | Notable trick |
| --- | --- | --- | --- |
| Strata | Consumer NVIDIA RTX, 12 GB+ | Qwen3.8-Flash-Next | Per-expert VRAM cache across all layers, native MTP (**Reported**)[^overfit-post] |
| ninfer | One RTX 5090 plus community 16 GB `SM_89` port (4080 validated, 4060Ti at 92K) and 3090 forks | A closed list of Qwen checkpoints | Scratch-written C++/CUDA, no offloading, no multi-GPU (**Reported**)[^overfit-post][^ninfer-readme][^ninfer-4080-thread] |
| DwarfStar (`ds4`) | Metal, CUDA, ROCm; two Macs over RDMA | DeepSeek V4/V4.1 Flash and V4 Pro first, plus GLM 5.x and Qwen3.8-Flash-Next | Aggressive routed-expert quants, compressed KV cache on SSD (**Reported**)[^overfit-post] |
| Splash | Apple Silicon M3+ | Qwen family | DFlash 2 speculation, per-model kernels and memory plans (**Reported**)[^overfit-post] |
| llamAmpere | RTX 3090 / 3090 Ti (SM86) | Mainly Qwen3.8-27B | llama.cpp fork with TurboQuant KV and custom verify kernels (**Reported**)[^overfit-post] |
| gufo | AMD Strix Halo (Ryzen AI MAX+ 395) | A small curated set | Custom HIP kernels, DFlash2 + MTP, continuous batching (**Reported**)[^overfit-post] |

### Firsthand measurement that started the thesis

- Rig: author's homelab node "yeti-cachy" — i5-12600K, 64 GB DDR5, RTX 4070 12 GB — running Qwen3.8-Flash-Next (125B-parameter MoE) (**Reported**)[^overfit-post].
- After tuning flags plus two experimental llama.cpp branches the author reached 27 tok/s decode on llama.cpp; Strata on the same box at ~60,000 tokens of context logged `prompt 59787 tokens = 0 reused + 59787 read in 29701 ms (2013.0 tok/s), 512 generated in 9631 ms (53.2 tok/s), drafts accepted 244 of 331` — about 2x the author's best llama.cpp number with no hardware change (**Reported**)[^overfit-post].
- Tuning-ladder chart for the same model and box, decode tok/s (**Reported**)[^overfit-post]: Powersave 6.5, CPU governor 12.2, SSD mmap 15.2, q8 KV plus fit 18.9, master 19.35, MTP V1 20.65, MTP V2 27.06, Strata dynamic cache 60.3, Strata peak 90.2 — where the first seven points are llama.cpp tuning steps not separate runtimes, 60.3 is Strata's best short-prompt row (53.2 held at 60K context), and 90.2 is a warm-draft burst on repetitive code, not sustained throughput.
- **Synthesis:** per the SCOPE benchmark rule this is a complete-setup comparison, not a controlled experiment — the author states quants and settings differ between the two engines — so the ~2x (author's best llama.cpp MTP V2 27.06 vs Strata 53.2 at 60K) and ~2.6x (upstream master 19.35–20.8 vs Strata 53.2) bands describe different baselines on one box; Strata and llama.cpp versions are unstated in this post except the router table's Strata v0.1.30, and batch/concurrency plus measurement protocol are absent.

## Reported performance snapshots

| Pair | Workload | Result |
| --- | --- | --- |
| Strata vs upstream llama.cpp master | Qwen3.8-Flash-Next (125B MoE) on one consumer rig, 60K context | Strata 53.2 tok/s decode and 2,013 tok/s prefill vs llama.cpp master 20.8 tok/s decode, about 2.6x (**Reported**)[^narrow-engines-sf] |
| Strata vs best MTP-assisted llama.cpp | Same model and box, updated technical write-up | Sustained gap closer to 2x (**Reported**)[^narrow-engines-sf] |
| Splash | Qwen3.6-35B-A3B on 48 GB M5 Pro | 210 tok/s (**Reported**)[^narrow-engines-sf] |
| Strata vs stock llama.cpp, firsthand user reports | Qwen3.8-Flash-Next ISTA-DASLab quants on RTX 3060–5090 and RX 7900XTX/9070 XT, up to 262K context | Roughly 2–3x decode on matched quants (e.g. 51 vs 23 tok/s on a 5070 Ti laptop, 70 vs 25 tok/s on a 3090) and up to an order of magnitude faster prefill (1,500 vs 100 tok/s at 32K), self-reported with no shared protocol (**Reported**)[^strata-thread-sep30] |
| Video-explainer deconstruction of the viral "6x" | Qwen3.8-Flash-Next on an RTX 5070-class consumer PC, 3-bit llama.cpp-tool baseline vs 2-bit Strata headline | 93/15 ≈ 6.2x slowest-vs-fastest but ~2.1x matched 3-bit-vs-3-bit and ~2.4x on an RTX 3090 matched-quant report — fair band 2–2.5x, no shared protocol (**Reported**)[^strata-video-6x] |

- **Synthesis:** per the SCOPE benchmark rule these are not comparable benchmarks yet — the article names the model and decode/prefill metrics but not the consumer GPU model, llama.cpp or Strata versions, quantization, batch size, or measurement protocol — so treat the 2–2.6x and 210 tok/s figures as directional **Reported** snapshots with the limit noted.
- The firsthand reports carry the same limit plus one more: commenters note Strata's published tables used greedy decoding (best case), so sampled generation should read lower, and output parity with llama.cpp is still open — detail in [Strata Qwen3.8-Flash-Next Quants and Measured Speed](strata-qwen3.8-flash-next-quants-performance.md)[^strata-thread-sep30].
- Strata's earlier milestone repeated in the article: running the 125B-parameter model on a single gaming GPU with as little as 8 GB VRAM (**Reported**)[^narrow-engines-sf].
- Hype assessment from a 2026-10-03 complaint thread that mostly corroborated the engine (**Reported**)[^strata-thread-bots]: reporters reframe "overhyped" as "oversaturated" — performance real (2–5x bands restated across 3090/4070/5060Ti/5080/5090/P40 rigs) but discussion volume exhausting; astroturfing suspicion countered by firsthand `llama-swap`/podman/Claude-assisted setups and the author not promoting the repo. Competitive notes: HyperQwen keeps a vLLM batch/concurrency edge over Strata/ninfer for concurrent agents, and FreeToken is positioned as catching up once it gains MTP while covering more models (DeepSeek V4 Flash, GLM 5.3 Flash) (**Reported** positions)[^strata-thread-bots].

## Why specialization helps

- Strata's example mechanism is a per-expert VRAM cache across all layers of Qwen3.8-Flash-Next — described as a trick that only makes sense when the whole engine is built around one model's architecture (**Reported**)[^narrow-engines-sf][^overfit-post].
- **Synthesis:** this is model-specific capacity planning rather than a general scheduler win; it connects to [Strata Tiered MoE Offload Engine](strata-tiered-moe-offload.md), which places dense weights plus hot experts on GPU, all experts in RAM for CPU compute, and the n-gram table on SSD.
- The claim about Splash is structural: a general engine chasing cross-platform support has no path to matching an Apple-Silicon-only optimization (**Reported**, author assertion rather than measured comparison)[^narrow-engines-sf].
- Generality-as-tax mechanism stated firsthand (**Reported**)[^overfit-post]: llama.cpp runs dozens of model families across CUDA, ROCm, Metal, Vulkan, SYCL and many CPU architectures, so a PCIe expert-movement change cannot break Metal unified-memory paths, a CUDA optimization cannot break older cards, and a per-expert VRAM cache must be threaded through the shared graph scheduler and allocator every backend depends on — each solvable, but slowly and through review — while a one-target codebase can make the radical change immediately.

## Why now: three reasons

1. **Generality is a performance tax** (above): breadth slows radical changes; narrow codebases skip the review and compatibility surface (**Reported**)[^overfit-post].
2. **AI coding made engines cheap to write:** a high-performance CUDA runtime used to need senior systems time and months of profiling; a capable developer with a coding agent can now write, benchmark and fix kernels far faster on a fixed model-plus-machine scope — author guess: months of specialist time down to weeks or less, with no hard numbers (**Reported** as guess)[^overfit-post]. The one public data point cited is DwarfStar's README saying it is developed "with strong assistance from AI coding agents," humans leading ideas, testing and debugging; the author does not know how much of Strata was agent-written (**Reported**)[^overfit-post].
3. **"Make tok/s go up" is an unusually crisp objective:** fixed weights file plus token IDs as input; outputs stay within a tolerance of a reference (e.g. greedy-token agreement or low KL divergence on reference logits); objective is more tokens per second in less memory — iterable against hardware counters by an agent loop (**Reported**)[^overfit-post]. Limit stated in the source: the objective is not fully specified — prefill latency, power, concurrency, context length, sampling behavior and reliability all matter, and a loose tolerance invites trading away unmeasured quality such as long-context accuracy or rare tokens; the tighter the parity check, the more the result can be trusted, which is why the quality check is the most important open item in the author's Strata write-up (**Reported**)[^overfit-post].

## Checkable prediction

- By April 2027, at least four of the six engines above will have gone 60 days without a commit to their default branch — counting upstream commits, not fork activity — with the author committing to check back and report either way (**Reported**)[^overfit-post].
- Rationale: when the next model generation changes routing or attention layout, an engine built around the old one will stall rather than refactor, and a new one-off will appear for the new model within days or weeks (**Reported**, prediction rather than finding)[^overfit-post].
- **Synthesis:** this gives the thesis a falsification date; `stale_after` above (2027-04-04) aligns with re-checking this prediction.

## General engines as the parts bin

- DwarfStar borrows kernels and quant formats from llama.cpp's GGML; llamAmpere is a llama.cpp fork; the GGUF format, quant types and many starting kernels came from years of general-purpose work (**Reported**)[^overfit-post].
- Likely future is not replacement but layering: general engines do the slow broad work (formats, quantization research, correct reference kernels for every backend) while napkin runtimes bolt those parts into something overfit for one model and one card and discard the assembly when the next model arrives (**Reported**, author forecast)[^overfit-post].
- Console analogy: a console studio targets one exact chip, memory bus and cache hierarchy and may specialize aggressively, while PC developers pay a generality tax in abstraction layers and defensive paths; cheaper engine-writing lets a fixed desktop be treated like a console — one RTX 4070 plus PCIe 4.0 plus DDR5 as the fixed target — with Strata/ninfer/Splash as direct-to-metal versus the llama.cpp/vLLM/Ollama plus schedulers plus multi-OS plus multi-vendor plus 50-model-family stack (**Reported**)[^overfit-post].

## What survives the churn

- **HTTP API:** OpenAI Chat Completions and Anthropic Messages APIs are what clients speak; as long as a napkin runtime exposes one, it plugs into Cursor, Cline, Open WebUI and Aider without clients noticing the engine underneath (**Reported**)[^overfit-post].
- **Model routers:** running several one-off engines means juggling processes and ports — the author uses `llama-swap` plus a personal L3MS supervisor; `llama-swap` listens on one port, stops whatever is loaded, starts the right engine with its flags, proxies the request, and shuts it down after 10 idle minutes, so the client sees one endpoint while engines swap like cartridges (**Reported**)[^overfit-post]. Author tiers at post time (Strata v0.1.30 engine version stated; **Reported**)[^overfit-post]: `qwen38-flash-next-plat` Strata fast default 128K ~53–60 tok/s; `qwen38-flash-next-plat-vision` Strata plus CPU vision encoder (untested with images; CPU encoder mostly adds time to first token); `qwen38-flash-next` llama.cpp master stable fallback 96K 20.8 tok/s; `qwen38-flash-next-vision` llama.cpp plus mmproj 16K 18.2–18.6 tok/s; `qwen38-flash-next-mtp` llama.cpp MTP branch experimental 25.3–27.1 tok/s; `gemma-4-26b-qat-mtp` llama.cpp plus MTP assistant mostly on GPU ~100 tok/s.
- **Hardware-specific communities (speculative):** author expects tuning groups to form around exact hardware combinations (e.g. 24 GB card with 64 GB DDR5, or one Mac memory tier) trading builds, routing profiles and placement recipes — flagged as extrapolation not yet observed (**Reported**)[^overfit-post].

## Trust cost and how general engines could win back

- Napkin properties that make them fast make them risky: young, one-person or small-group maintained, changing daily, shipping native code that pins memory and talks to the GPU driver, few reviewers, no security advisories for a project abandoned in six months (**Reported**)[^overfit-post].
- If this becomes the normal local path, power users inherit a supply-chain problem they did not have with a well-reviewed general runtime; the author's minimum: build from source, pin a commit, skim the diff before updating, and do not run them on machines holding anything unaffordable to lose; hardware communities sharing vetted builds could help or make it worse (**Reported**, recommendation)[^overfit-post].
- Three win-back paths proposed for general engines (**Reported** as proposals)[^overfit-post]: (1) recipes as plugins — alongside a model file download a hardware-specific recipe (fused kernels, expert placement mask, speculation schedule for e.g. RTX 4070 with DDR5) loaded by a thin trusted host — no project ships this today; (2) agents maintaining variants upstream — generating and testing hardware-specialized kernel variants inside a general repo for every GPU generation, shifting the bottleneck to review; (3) compilers delivering — Mojo/MAX, Triton or MLIR stacks from high-level graph plus hardware description to near-optimal code — until then a person or agent writing for one exact GPU usually beats compiler output.

## Not benchmark gaming

- The article corrects the Reddit "overfit" framing: these engines are not tuning for a test set and falling apart on real traffic; they give up generality on purpose (**Reported**)[^narrow-engines-sf].
- The real risk for infrastructure spend is conditionality: the throughput number is real but conditional on one model plus one hardware class, and little else (**Reported**)[^narrow-engines-sf].
- Concretely: swap the model, change the GPU, or wait for the next Qwen release and the serving layer may simply be unsupported (**Reported**)[^narrow-engines-sf].

## Buying calculus

- Hobbyist on one model and one card (the article's example: one 3090 for personal use) has almost nothing to lose because the narrow fit is exactly the use case (**Reported**)[^narrow-engines-sf].
- Startup needs model-swappability as better models ship, or running on whatever cloud GPU is cheapest that quarter; locking the serving layer to a single model-hardware pair for throughput that may be obsolete on the next model drop is a real bet either way (**Reported**)[^narrow-engines-sf].
- The cost comparison that matters is not launch-day tokens per second but tokens per second averaged over the model's actual lifespan, including the version after this one when a narrow engine's support list may not have caught up (**Reported**)[^narrow-engines-sf].
- vLLM and llama.cpp lag on peak throughput precisely because they carry generality forward; whether that is worth paying for depends on how often the operator expects to change models (**Reported**)[^narrow-engines-sf].
- Durable-vs-transient split stated in a video explainer (**Reported**)[^strata-video-6x]: the Strata-vs-llama.cpp engine gap is two features being chased in public (llama.cpp merged MTP for this model on October 1st; the expert-cache PR is still open), so it closes with pull requests — while the model being designed for offloading as a first-class goal is the lasting shift. **Synthesis:** lifespan-averaged throughput here depends as much on the architecture meeting consumer hardware where it lives as on which engine is ahead this month.

## Relationships

- Uses [Strata Tiered MoE Offload Engine](strata-tiered-moe-offload.md) — the single-model tiering design behind the Strata numbers quoted here.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — the general-purpose baseline this source compares against; narrow engines sit outside that two-way choice.
- Related to [ds4, Magnitude and Strata Local Agent Engines](ds4-magnitude-strata-local-agents.md) — per-engine versions, licences, self-reported speed caveats, hardware fit and agent-cost arithmetic for ds4, Magnitude and Strata.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — the Unsloth GGUF plus llama.cpp route for the same 125B model Strata specializes in.
- Related to [Qwen3.6 Local Deployment](qwen3.6.md) — the general local route for the Qwen3.6-35B-A3B model in the Splash report.
- Related to [Qwen3.8-Flash-Next Architecture and Evaluation](qwen3.8-flash-next-architecture.md) — the 125B/6B-active plus n-gram architecture that makes per-expert caching pay off.
- Related to [HyperQwen Qwen3.8-27B Serving Stack](hyperqwen-serving-stack.md) — the pinned-vLLM Qwen3.8-27B stack that keeps the batch/concurrency edge cited in the complaint-thread competitive notes.
- Related to [NInfer Single-GPU Inference Engine](ninfer-single-gpu-inference-engine.md) — NInfer's own README grounding for the row above: five Qwen3.6/3.8 v3 artifacts, RTX-5090-only `sm_120a` build, 1–8 startup-fixed lanes, MTP/DFlash speculation, and RTX 5090 decode/prefill plus EvalScope figures (**Reported**)[^ninfer-readme].
- Related to [NInfer 4080 16GB Port](ninfer-4080-16gb-port.md) — community `SM_89` port behind the updated ninfer row: Qwen3.8-27B-GSQ at ~100K on 16 GB RTX 4080 with Q3 kernels, DFlash2/MTP, compressed KV, and 4060Ti 92K confirmation (**Reported**)[^ninfer-4080-thread].

## Coverage limits

- The Carteakey post is compiled firsthand here (published 2026-09-30, changelog 2026-10-01 and 2026-10-03); the Startup Fortune summary remains secondhand[^overfit-post][^narrow-engines-sf]. The author's companion technical write-up (Strata on an RTX 4070), linked Qwen3.8-Flash-Next post, device page, engine repos, DwarfStar README, `llama-swap`/L3MS repos, and Gemma post were not inspected — engine-version, quant, and protocol gaps above follow.
- The three `assets/*.avif` files in scope (bell-curve meme, Qwen3.8-Flash-Next decode-throughput ladder chart, PC-vs-console comparison diagram) were inventoried; chart and diagram values are captured above from the post text and alt text, and the meme was excluded as decorative restating the thesis.
- No sensitive values found.

[^overfit-post]: Kartikey Chauhan, "The Rise of Overfit Inference Engines" — `../raw/the-rise-of-overfit-inference-engines/index.md` (carteakey.dev, published 2026-09-30; changelog 2026-10-01, 2026-10-03): yeti-cachy rig (i5-12600K, 64 GB DDR5, RTX 4070 12 GB), Qwen3.8-Flash-Next llama.cpp 27 tok/s vs Strata 53.2 tok/s decode / 2,013 tok/s prefill at ~60K context with 244/331 drafts accepted, nine-step tuning ladder (6.5 → 90.2 burst), six-engine table (Strata, ninfer, DwarfStar, Splash, llamAmpere, gufo), April-2027 four-of-six abandonment prediction, generality-tax / AI-coding-cost / crisp-objective reasons, parts-bin and console-model framing, HTTP-API plus llama-swap/L3MS stable layers with six-tier table (Strata v0.1.30), trust minimums, three general-engine win-back proposals, and one-model-one-machine plus no-quality-A/B caveats.

[^narrow-engines-sf]: Elroy Fernandes, "A wave of narrow AI inference engines is beating vLLM and llama.cpp at their own game" — `../raw/a-wave-of-narrow-ai-inference-engines-is-beating-vllm-and-llamacpp-at-their-own/index.md` (Startup Fortune, published 2026-10-04), covering the Strata/ninfer/DwarfStar/Splash/llamAmpere/gufo narrow-engine set, Carteakey Qwen3.8-Flash-Next consumer-rig numbers (llama.cpp master 20.8 vs Strata 53.2 tok/s decode at 60K context plus 2,013 tok/s prefill, ~2x sustained vs MTP-assisted llama.cpp), Strata 5.04 GiB / 3,086-expert cache across 48 layers and 8 GB-VRAM milestone, ninfer CUDA-only and Splash Apple-Silicon-only (210 tok/s on Qwen3.6-35B-A3B, 48 GB M5 Pro) scope, overfit-vs-generality correction, hobbyist-vs-startup lock-in calculus, and lifespan-averaged throughput argument.
[^strata-thread-sep30]: r/LocalLLaMA thread "Qwen3.8 flash next ISTA-DASLab GGUF 50t/s TG and 1500t/s PP ..." — `../raw/qwen38-flash-next-istadaslab-gguf-50ts-tg-and/index.md` (original post plus comments, 2026-09-30–2026-10-04): OP laptop measurements (IQ3_XXS, 51 tok/s at 43K, 1,500 tok/s PP at 32K), community rig reports (RTX 3060–5090, RX 7900XTX/9070 XT), matched-quant llama.cpp baselines, greedy-decoding methodology note, and open output-parity status.

[^strata-video-6x]: "The New Way to Run 125B Models 6x Faster Than llama.cpp (Strata)" — `../raw/the-new-way-to-run-125b-models-6x-faster-than-llama.cpp-(strata).md` (YouTube transcript, English; channel, URL, and publish date not captured — content places it after the 2026-10-01 llama.cpp MTP merge): 6x headline deconstruction (6.2x slowest-vs-fastest, 2–2.5x fair band) and transient-engine-lead vs durable-offload-architecture split.

[^strata-thread-bots]: r/LocalLLaMA thread "Yes bots we get it, Strata is good now please stop" — `../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/index.md` (comments 2026-10-03–2026-10-04): oversaturated-vs-overhyped reframing (kimhaneol, CtrlAltDelve), astroturfing-vs-excitement dispute (danieln1212, vacon04, Fortyseven), HyperQwen concurrency edge (catch23), FreeToken MTP gap (trying4k), and llama.cpp hot-expert fork pointer (zyxciss).

[^ninfer-readme]: NInfer — `../raw/ninfer.md` (README capture): from-scratch C++/CUDA single-RTX-5090 engine with 1–8 startup-fixed lanes, five Qwen3.6/3.8 v3 artifacts, `sm_120a`/CUDA-13.1 build, MTP 1–5 plus 35B-A3B DFlash and Qwen3.8 DFlash2 paths, and RTX 5090 decode/prefill plus EvalScope capability figures.
[^ninfer-4080-thread]: u/roofkid, "I built Ninfer 4080 for 16GB class GPUs" — `../raw/i_built_ninfer_4080_for_16gb_class_gpus.md` (r/LocalLLaMA post plus 54 comments: `SM_89` 4080 port for `ISTA-DASLab-Qwen-3.8-27B-GSQ` at ~100K with Q3 kernels, GSQ conversion, DFlash2/MTP and `rk4v4-e8` KV figures, plus 4060Ti 92K confirmation and 4070Ti/5xxx compatibility notes; full synthesis in [NInfer 4080 16GB Port](ninfer-4080-16gb-port.md)).
