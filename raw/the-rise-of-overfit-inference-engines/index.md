---
title: "The Rise of Overfit Inference Engines"
author: "Kartikey Chauhan"
site: "Kartikey Chauhan"
published: 2026-09-30
source: "https://carteakey.dev/blog/local-inference/the-rise-of-overfit-inference-engines/"
domain: "carteakey.dev"
language: "en"
description: "Napkin runtimes: why disposable, overfit inference engines are coming."
word_count: 2145
---

![Bell-curve meme. The low-IQ end and the hooded high-IQ end both say: I write inference code for my specific model and hardware. The crying midwit in the middle says: I write inference code that generalizes across all models and all hardware.](assets/M40HEyQ-9w-675.avif)

The whole post, in one meme.

## The surprise

For a week I'd been tuning [Qwen3.8-Flash-Next](https://carteakey.dev/blog/local-inference/running-qwen3-8-flash-next-locally/), a 125B-parameter MoE, on [🧠 yeti-cachy](https://carteakey.dev/devices/yeti-cachy/) (my main homelab node: an i5-12600K with 64 GB DDR5 and an RTX 4070 12GB I paid $500 for). After a lot of flags and two experimental branches, `llama.cpp` reached **27 tok/s**. For an offloaded 125B model on a 12 GB card, that felt like the ceiling.

Then I tried **Strata**, a runtime that supports exactly this model on NVIDIA consumer cards.

```
strata serve: prompt 59787 tokens = 0 reused + 59787 read in 29701 ms (2013.0 tok/s), 512 generated in 9631 ms (53.2 tok/s), drafts accepted 244 of 331
```

Same box, 60,000 tokens of context: **53 tok/s**. About twice my best llama.cpp number, with no hardware changes.

My unfiltered reaction was: *what in the fuck?*

![Line chart of Qwen3.8-Flash-Next decode throughput on an RTX 4070 12GB in tokens per second across nine steps: Powersave 6.5, CPU governor 12.2, SSD mmap 15.2, q8 KV plus fit 18.9, master 19.35, MTP V1 20.65, MTP V2 27.06, Strata dynamic cache 60.3, Strata peak 90.2](assets/3h6wHy2b3G-1109.avif)

The first seven points are tuning steps on llama.cpp, not separate runtimes. 60.3 is Strata's best short-prompt row; at a 60k context it holds 53.2. 90.2 is a warm-draft burst on repetitive code, not sustained throughput.

Quants and settings differ between the two engines, so that's a comparison of complete serving setups, not a controlled experiment. The measurements, memory layout and caveats are in the technical write-up, [Strata on an RTX 4070](https://carteakey.dev/blog/local-inference/strata-on-an-rtx-4070/). This post is about what I think it means.

My bet: for power users on fixed hardware, **disposable, overfit engines are going to beat general-purpose runtimes on speed**, and general runtimes will keep the portability crown.

## The new breed

Strata isn't alone. In the past few months a handful of narrow inference engines have appeared, each built for a short list of models on one hardware family, and each beating general runtimes inside its niche.

| Engine | Target hardware | Models | Notable trick |
| --- | --- | --- | --- |
| [Strata](https://github.com/Niko1221/Strata) | Consumer NVIDIA RTX, 12 GB+ | Qwen3.8-Flash-Next | Per-expert VRAM cache across all layers, native MTP |
| [ninfer](https://github.com/Neroued/ninfer) | One RTX 5090 (community forks for 3090) | A closed list of Qwen checkpoints | Scratch-written C++/CUDA, no offloading, no multi-GPU |
| [DwarfStar](https://github.com/antirez/ds4) (`ds4`) | Metal, CUDA, ROCm; two Macs over RDMA | DeepSeek V4/V4.1 Flash and V4 Pro first, plus GLM 5.x and Qwen3.8-Flash-Next | Aggressive routed-expert quants, compressed KV cache on SSD |
| [Splash](https://github.com/incoai/splash) | Apple Silicon M3+ | Qwen family | DFlash 2 speculation, per-model kernels and memory plans |
| [llamAmpere](https://github.com/JakeATX/llamAmpere) | RTX 3090 / 3090 Ti (SM86) | Mainly Qwen3.8-27B | llama.cpp fork with TurboQuant KV and custom verify kernels |
| [gufo](https://github.com/gufo-org/gufo) | AMD Strix Halo (Ryzen AI MAX+ 395) | A small curated set | Custom HIP kernels, DFlash2 + MTP, continuous batching |

By normal software standards, these can look like bad codebases: tightly coupled, hard to port, built around narrow assumptions. In inference, those trade-offs are part of why they're fast. They shape the compute graph, memory layout and kernels around their chosen models and hardware.

## A prediction you can check

Most of these will be abandoned soon, and that's fine.

When the next model generation changes its routing scheme or attention layout, an engine built around the old one won't refactor. It'll stall, and a new one-off will show up for the new model within days or weeks.

To make that testable: **by April 2027, at least four of the six engines above will have gone 60 days without a commit to their default branch**. I'll count upstream commits, not activity in forks, and I'll check back and report either way.

## Why now: three reasons

### 1\. Generality is a performance tax

The more a codebase supports, the harder it is to make changes that break assumptions. `llama.cpp` is one of the best pieces of open-source engineering around, and it runs dozens of model families across CUDA, ROCm, Metal, Vulkan, SYCL and a long list of CPU architectures.

That breadth has a cost. A change to how experts move across PCIe can't break Metal's unified memory path. A CUDA optimization can't break older cards. A per-expert VRAM cache like Strata's has to be threaded through the shared graph scheduler and allocator that every backend depends on. Each of those is solvable, but slowly, and through review.

A small codebase with one target doesn't have those constraints. It can make the radical change on a Tuesday.

### 2\. AI coding made engines cheap to write

A high-performance CUDA runtime used to need a senior systems engineer and months of profiling. Today a capable developer with a coding agent can write, benchmark and fix kernels far faster. A fixed model and machine make that work easier to scope: hand the agent one tensor layout or one fusion, then measure.

There's at least one public data point. [DwarfStar's README](https://github.com/antirez/ds4) says it's developed "with strong assistance from AI coding agents," with humans leading the ideas, testing and debugging. I don't know how much of Strata was agent-written. My guess is that the cost of a purpose-built runtime has dropped from months of specialist time to weeks or less, but I don't have hard numbers.

### 3\. "Make tok/s go up" is an unusually crisp objective

Most software resists automation because the goal is fuzzy. Inference optimization is closer to machine-checkable:

1. **Input:** a fixed weights file and token IDs.
2. **Constraint:** outputs stay within a tolerance of a reference, for example greedy-token agreement or low KL divergence on reference logits.
3. **Objective:** more tokens per second in less memory.

You can point an agent loop at that and let it iterate against hardware counters.

It isn't fully specified, though. Prefill latency, power, concurrency, context length, sampling behavior and reliability all matter, and a loose tolerance invites the loop to trade away quality it doesn't measure, such as long-context accuracy or rare tokens. The tighter the parity check, the more you can trust the result. That's also why the quality check is the most important open item in my Strata write-up.

## The twist: general engines become the parts bin

It would be easy to frame this as napkin runtimes versus general runtimes. The engines themselves suggest something messier.

DwarfStar borrows kernels and quant formats from llama.cpp's GGML. llamAmpere is a llama.cpp fork. The GGUF format, the quant types and many of the kernels these projects start from came out of years of general-purpose work.

So the more likely future isn't one replacing the other. General engines keep doing the slow, broad work: formats, quantization research, correct reference kernels for every backend. Napkin runtimes take those parts, bolt them into something overfit for one model and one card, and throw the assembly away when the next model arrives.

General engines become the parts bin. Napkin runtimes are what power users build from it.

## The console analogy

Game developers already know this pattern. A console studio targets one exact chip, one memory bus and one cache hierarchy, and that fixed target gives it permission to specialize aggressively. PC developers can't, because their engine has to run on whatever hardware shows up, so they pay a generality tax in abstraction layers and defensive code paths.

![Two-column comparison. PC Model, Generality Tax: a stack of llama.cpp / vLLM / Ollama, Graph schedulers, Multi-OS, CUDA / ROCm / CPU and 50+ model families. Console Model, Direct-to-Metal: Strata / ninfer / Splash pointing straight at Ada SM89 / PCIe 4.0.](assets/9-2LucQHfr-1173.avif)

PC model vs console model of inference runtimes. A generalist runtime pays for graph schedulers, multi-OS and multi-vendor support, and dozens of model families. An overfit runtime is tuned for one target and drops everything else.

For years nobody wrote console-style engines for a single PC configuration, because no one could justify the engineering cost for an audience of one card. Cheaper engine-writing changes that math. If a runtime for one model on one GPU costs weeks instead of years, your desktop can be treated like a console: a fixed target worth specializing for.

## What survives the churn

If runtimes are disposable, the layers around them have to be stable. Nobody wants a new CLI, UI and SDK every time an engine dies.

### The HTTP API

The OpenAI Chat Completions API and the Anthropic Messages API are what clients speak. As long as a napkin runtime exposes one of them, it plugs into Cursor, [Cline](https://github.com/cline/cline), Open WebUI, Aider and the rest without anyone noticing what's underneath.

### Model routers

Running several one-off engines means juggling processes and ports. That's what [`llama-swap`](https://github.com/mostlygeek/llama-swap) and my [L3MS](https://github.com/carteakey/l3ms) supervisor are for. My current tiers:

| Model name | Engine | Role | Decode |
| --- | --- | --- | --- |
| `qwen38-flash-next-plat` | Strata v0.1.30 | Fast default, 128k context | ~53–60 tok/s |
| `qwen38-flash-next-plat-vision` | Strata v0.1.30 + CPU vision encoder | Fast image tasks | Untested with images; the CPU encoder mostly adds time to first token |
| `qwen38-flash-next` | llama.cpp master | Stable fallback, 96k context | 20.8 tok/s |
| `qwen38-flash-next-vision` | llama.cpp master + mmproj | Image tasks fallback, 16k context | 18.2–18.6 tok/s |
| `qwen38-flash-next-mtp` | llama.cpp MTP branch | Experimental | 25.3–27.1 tok/s |
| `gemma-4-26b-qat-mtp` | llama.cpp + MTP assistant | Smaller MoE, mostly on the GPU | [~100 tok/s](https://carteakey.dev/blog/local-inference/gemma-4-26b-qat-mtp/) |

llama-swap listens on one port. When a client asks for a model, it stops whatever was loaded, starts the right engine with its flags, proxies the request, and shuts it down after 10 idle minutes. The client sees one endpoint; engines swap underneath like cartridges. Trying Strata didn't mean replacing my workflow, and llama.cpp is still one model name away when the experiment breaks.

### Hardware-specific communities (speculative)

I'd expect tuning groups to form around exact hardware combinations rather than broad forums. Think a community for a 24 GB card with 64 GB of DDR5, or for one Mac memory tier, trading engine builds, expert routing profiles and placement recipes for their exact setup. This is extrapolation; I haven't seen it happen yet.

## The cost: trust

The same properties that make napkin runtimes fast make them risky to run. They're young, maintained by one person or a small group, change daily, and ship native code that pins memory and talks straight to the GPU driver. Few people review them, and nobody issues security advisories for a project that will be abandoned in six months.

If this becomes the normal way to run local models, power users take on a supply-chain problem they didn't have with a well-reviewed general runtime. A source build and a pinned revision make the work inspectable; they don't make it audited. The minimum I'd suggest: build from source, pin a commit, skim the diff before updating, and don't run them on machines that hold anything you can't afford to lose. Hardware communities that share vetted builds could help here, or make it worse.

## How general engines could win back the lead

I don't think general engines go away. Three ways they could close the gap:

**Recipes as plugins.** Alongside a model file, you download a recipe for your hardware: fused kernels, an expert placement mask and a speculation schedule built for, say, an RTX 4070 with DDR5. The general engine becomes a thin, trusted host that loads it. This is the parts-bin idea run in reverse, and it would also ease the trust problem, since the host stays reviewed. It's a proposed design; I'm not aware of a project that ships this today.

**Agents maintaining the variants upstream.** The same agents that write one-off engines could generate and test hardware-specialized kernel variants inside a general repo, for every GPU generation, without maintainers hand-writing each one. The bottleneck shifts from writing code to reviewing it.

**Compilers finally deliver.** If Mojo/MAX, Triton or MLIR-based stacks get good enough to take a high-level model graph and a hardware description and emit near-optimal code automatically, hand-overfit engines lose their edge overnight. Until then, a person or agent writing for one exact GPU will usually beat compiler output.

## Don't marry your inference engine

For two years, running local models meant one playbook: install llama.cpp or vLLM, pick a context size, offload what fits. That playbook still works, and for most people it's still the right one.

But when a runtime written for one model and one GPU doubles your best decode speed and holds it flat across 60,000 tokens, the generality tax gets hard to ignore. So keep your serving layer stable, treat the engine underneath as replaceable, and don't expect this year's fastest runtime to support next year's model.

Napkin software: cheap to write, very good at the meal in front of you, and fine to throw away when the next course arrives.

> [!note] Note
> What this argument rests on
> 
> One model and one machine that I measured myself, with a missing ablation and no quality A/B yet, plus five other projects whose claims I'm taking at face value. The trend is real enough to notice. Whether it lasts is what the April 2027 check is for. I'd like to hear where you think it breaks.

## Changelog

| Date | Note |
| --- | --- |
| 2026-10-03 | Moved the benchmarks, memory layout and reproduction details to a separate [Strata post](https://carteakey.dev/blog/local-inference/strata-on-an-rtx-4070/). Reframed the headline speedup against the best llama.cpp setup (about 2×), added a checkable prediction, the parts-bin section and a trust section, softened the objective-function claim, trimmed the console analogy, updated the DwarfStar description, and dropped an unverified reference. |
| 2026-10-01 | Corrected the bandwidth arithmetic and removed the double-counted cache and MTP gain, aligned the hardware specs, linked all six engines, hedged the unsourced claims, moved the IQ3\_S and NAS-archive notes to the Flash-Next post, and tightened the prose. |
| 2026-09-30 | Initial post. |
