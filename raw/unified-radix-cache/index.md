---
title: "Unified Radix Cache in SGLang: one tree for hybrid model prefix caching"
author: "SGLang Team"
site: "SGLang"
source: "https://www.sglang.io/blog/unified-radix-cache"
domain: "sglang.io"
language: "en"
description: "One radix tree for hybrid models: FULL, SWA, and MAMBA reuse decided per component, multi-turn hit rates near 98% across GPU, host, and Mooncake tiers, and lower TTFT from session-aware eviction and the Rust tree core."
word_count: 1734
---

Unified Radix Cache in SGLang

One radix tree, one slot per component, the same prefix identity across GPU, host, and external tiers

TP4 · 4×H200

Effective input throughput (tok/s) · DeepSeek-V4-Flash15.5× with L3

9.4K

L1

GPU only

14.3K

L1 + L2

\+ host

145.5K

L1 + L2 + L3

\+ Mooncake

Prefix cache hit rate, later rounds · DeepSeek-V4-Flashnear 98%

~98%

L1 + L2 + L3

\+ Mooncake

Adapted from the [LMSYS article on Unified Radix Cache](https://www.lmsys.org/blog/2026-08-11-unified-radix-cache/).

## Background

Prefix caching reuses KV when requests share a token prefix. Under full attention, a later request can reuse the cached prefix and compute only the new tokens.

Hybrid models combine three kinds of data with different reuse rules: FULL (full attention) needs KV along the matched prefix, SWA (sliding window attention) needs a continuous window immediately before the reuse boundary, and MAMBA needs a snapshot of the recurrent state, or checkpoint, at that boundary.

Reuse semantics diagramCandidate boundary t8 · SWA window W = 4 · gray cells are outside the required range

Matched token prefixt1t2t3t4t5t6t7t8t9t10t11t12

FULL · whole path

SWA · required window

MAMBA · exact checkpoint

DeepSeek-V4 pairs FULL with SWA, Kimi-K3 pairs FULL with MAMBA for its KDA recurrent state, and Inkling uses all three. SGLang handles these combinations on one shared tree, with each component defining its own reuse rule.

Class matrix vs components diagramSWAMAMBAHiCache

Before: one specialized cache class per combination × capability · **2 in total**

**FULL** *match* *insert* *lock* *evict*

**FULL + SWA** *match* *insert* *lock* *evict*

After: one tree plus pluggable components · **components ×2** UnifiedTreeCore: shared matching, split, insert, lock, evict mechanicsUnifiedRadixCache: pool orchestration

Components:FULLSWAsidecar ×N

## Unified Radix Cache

### Design and mechanism

Each radix node stores a token span and a slot for each component. FULL and SWA slots hold KV page indices; MAMBA holds a checkpoint at the prefix endpoint. SWA data outside the required window can stay cached or be evicted independently, leaving an empty slot called a tombstone.

Components handle their own splits, inserts, locks, and evictions. Reclaiming part of a node's SWA data starts by splitting the node at the retention boundary. A MAMBA checkpoint stays at its original prefix endpoint; a request reusing it obtains a private copy through copy-on-write, then continues updating its state.

Unified radix tree replayWindow W = 4 · one token per cell · earlier CSFA retained after request 2

t = 0/8Request 1 · ABCSFARequest 2 · ABCSFAAPSDRequest 3 · ABDWA

Request 1 · token streamABCSFA

<svg viewBox="0 0 400 218" role="img" aria-label="Unified radix tree replay"><defs><pattern id="urc-rt-hatch" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M0 5 L5 0" stroke="currentColor" stroke-width="1"></path></pattern></defs><circle cx="52" cy="16" r="5" fill="none" stroke="currentColor"></circle><text x="62" y="20" font-size="10" fill="#888">root</text> <text x="100" y="20" font-size="10" fill="#888">reuse boundary: 0</text></svg>

### The safe reuse boundary

Matching walks the matched path, and each component checks its data at every candidate boundary. Each candidate is evaluated independently. Computation resumes from the deepest boundary accepted by all components.

Reuse-boundary voting diagramScenario: n3 has tombstoned SWA window slots; n4 has no MAMBA checkpoint

t = 0/5FULL onlyFULL + SWAFULL + SWA + MAMBA

n1

n2

n3

n4

FULL

SWA

MAMBA

▲ Safe boundary▲ Safe boundary▲ Safe boundary▲ Safe boundary

Reused directlyRecomputed from here

## HiCache across memory tiers

HiCache extends Unified Radix Cache across GPU L1, host memory L2, and external storage L3. See [HiCache in SGLang](https://yichizhang.dev/AI-Infra-Visualized/en/lessons/hicache/) for its tiering and data transfers.

### Components and sidecars

DeepSeek-V4's FULL and SWA use separate page indices, mapped by the allocator. Auxiliary pools for compressed KV, indexer buffers, and compressor states act as sidecars: they share their component's indices and transfers. Three follow FULL and two follow SWA.

Index reuse diagramThe blog's normalized six-page case · only the final two SWA pages retained here

FULL pages (component)

sidecars ×3 follow FULL

↓↓allocator translates

SWA window slots (component)

sidecars ×2 follow SWA

Page 4: FULL's F4 and its three sidecars share page number 4. The allocator translates F4 to SWA's S0, and SWA's two sidecars copy page number 0.

### Multi-turn benchmark

Multi-turn conversations keep extending the reusable prefix. A comparison of L1 only, L1+L2, and an additional 500 GiB Mooncake L3 tier shows DeepSeek-V4-Flash reaching 145.5K effective input tokens/s with L3, up from 9.4K with L1 only, with average TTFT below 9 seconds.

Multi-turn benchmark results diagramEffective input throughput = total full prompt length ÷ wall-clock time; cache-hit prefix tokens count

DeepSeek-V4-Flash FULL+SWA · 4×H200 TP4 · 48 clients · 60 rounds · 4,096 in + 16 out per turn Effective input throughput (tokens/s)

L1

9.4K

L1+L2

14.3K

L1+L2+L3

145.5K

Cache hit rate by round <svg viewBox="0 0 440 245" role="img" aria-label="DeepSeek-V4-Flash · Cache hit rate by round"><title>DeepSeek-V4-Flash · Cache hit rate by round</title> <desc>Hit rate = cached prefix tokens ÷ complete prompt tokens, summed per round. Curves use approximate samples read from the source figure.</desc><g font-size="12.6"><g><line x1="40" x2="428" y1="201" y2="201"></line> <text x="32" y="205" text-anchor="end">0%</text></g> <g><line x1="40" x2="428" y1="153.75" y2="153.75"></line><text x="32" y="157.75" text-anchor="end">25%</text></g> <g><line x1="40" x2="428" y1="106.5" y2="106.5"></line><text x="32" y="110.5" text-anchor="end">50%</text></g> <g><line x1="40" x2="428" y1="59.25" y2="59.25"></line><text x="32" y="63.25" text-anchor="end">75%</text></g> <g><line x1="40" x2="428" y1="12" y2="12"></line><text x="32" y="16" text-anchor="end">100%</text></g> <g><line x1="40" x2="40" y1="201" y2="206"></line><text x="40" y="221" text-anchor="middle">0</text></g> <g><line x1="110.54545454545455" x2="110.54545454545455" y1="201" y2="206"></line><text x="110.54545454545455" y="221" text-anchor="middle">10</text></g> <g><line x1="181.0909090909091" x2="181.0909090909091" y1="201" y2="206"></line><text x="181.0909090909091" y="221" text-anchor="middle">20</text></g> <g><line x1="251.63636363636363" x2="251.63636363636363" y1="201" y2="206"></line><text x="251.63636363636363" y="221" text-anchor="middle">30</text></g> <g><line x1="322.1818181818182" x2="322.1818181818182" y1="201" y2="206"></line><text x="322.1818181818182" y="221" text-anchor="middle">40</text></g> <g><line x1="392.7272727272727" x2="392.7272727272727" y1="201" y2="206"></line><text x="392.7272727272727" y="221" text-anchor="middle">50</text></g> <g><line x1="428" x2="428" y1="201" y2="206"></line><text x="428" y="221" text-anchor="middle">55</text></g> <text x="234" y="242" text-anchor="middle">Round (zero-based)</text></g> <polyline fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round" points="40,201 75.27272727272728,44.13000000000001 110.54545454545455,29.009999999999994 145.8181818181818,23.34000000000001 181.0909090909091,21.45000000000001 216.36363636363635,19.560000000000006 251.63636363636363,17.670000000000005 286.9090909090909,17.670000000000005 322.1818181818182,15.780000000000003 357.4545454545455,15.780000000000003 392.7272727272727,15.780000000000003 428,15.780000000000003"><title>L1+L2+L3</title></polyline> <polyline fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="8 5" stroke-linejoin="round" points="40,201 75.27272727272728,44.13000000000001 110.54545454545455,29.009999999999994 145.8181818181818,23.34000000000001 181.0909090909091,21.45000000000001 216.36363636363635,19.560000000000006 251.63636363636363,17.670000000000005 286.9090909090909,17.670000000000005 322.1818181818182,201 357.4545454545455,201 392.7272727272727,201 428,201"><title>L1+L2</title></polyline> <polyline fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="2 5" stroke-linejoin="round" points="40,201 75.27272727272728,44.13000000000001 110.54545454545455,29.009999999999994 145.8181818181818,23.34000000000001 181.0909090909091,201 216.36363636363635,201 251.63636363636363,201 286.9090909090909,201 322.1818181818182,201 357.4545454545455,201 392.7272727272727,201 428,201"><title>L1</title></polyline> <rect x="35" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 0 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈0%</title></rect> <rect x="70.27272727272728" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 5 L1: ≈83% L1+L2: ≈83% L1+L2+L3: ≈83%</title></rect> <rect x="105.54545454545455" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 10 L1: ≈91% L1+L2: ≈91% L1+L2+L3: ≈91%</title></rect> <rect x="140.8181818181818" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 15 L1: ≈94% L1+L2: ≈94% L1+L2+L3: ≈94%</title></rect> <rect x="176.0909090909091" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 20 L1: ≈0% L1+L2: ≈95% L1+L2+L3: ≈95%</title></rect> <rect x="211.36363636363635" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 25 L1: ≈0% L1+L2: ≈96% L1+L2+L3: ≈96%</title></rect> <rect x="246.63636363636363" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 30 L1: ≈0% L1+L2: ≈97% L1+L2+L3: ≈97%</title></rect> <rect x="281.9090909090909" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 35 L1: ≈0% L1+L2: ≈97% L1+L2+L3: ≈97%</title></rect> <rect x="317.1818181818182" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 40 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈98%</title></rect> <rect x="352.4545454545455" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 45 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈98%</title></rect> <rect x="387.7272727272727" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 50 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈98%</title></rect> <rect x="423" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 55 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈98%</title></rect></svg>

Final metrics with L3 hit rate **~98%** avg TTFT **< 9 s**

Inkling-Small FULL+SWA+MAMBA · 8×H200 TP8 · 64 clients · 30 rounds · 1,216 in + 64 out per turn Effective input throughput (tokens/s)

L1

15.5K

L1+L2

21.1K

L1+L2+L3

67.1K

Cache hit rate by round <svg viewBox="0 0 440 245" role="img" aria-label="Inkling-Small · Cache hit rate by round"><title>Inkling-Small · Cache hit rate by round</title> <desc>Hit rate = cached prefix tokens ÷ complete prompt tokens, summed per round. Curves use approximate samples read from the source figure.</desc><g font-size="12.6"><g><line x1="40" x2="428" y1="201" y2="201"></line> <text x="32" y="205" text-anchor="end">0%</text></g> <g><line x1="40" x2="428" y1="153.75" y2="153.75"></line><text x="32" y="157.75" text-anchor="end">25%</text></g> <g><line x1="40" x2="428" y1="106.5" y2="106.5"></line><text x="32" y="110.5" text-anchor="end">50%</text></g> <g><line x1="40" x2="428" y1="59.25" y2="59.25"></line><text x="32" y="63.25" text-anchor="end">75%</text></g> <g><line x1="40" x2="428" y1="12" y2="12"></line><text x="32" y="16" text-anchor="end">100%</text></g> <g><line x1="40" x2="40" y1="201" y2="206"></line><text x="40" y="221" text-anchor="middle">0</text></g> <g><line x1="106.89655172413794" x2="106.89655172413794" y1="201" y2="206"></line><text x="106.89655172413794" y="221" text-anchor="middle">5</text></g> <g><line x1="173.79310344827587" x2="173.79310344827587" y1="201" y2="206"></line><text x="173.79310344827587" y="221" text-anchor="middle">10</text></g> <g><line x1="240.6896551724138" x2="240.6896551724138" y1="201" y2="206"></line><text x="240.6896551724138" y="221" text-anchor="middle">15</text></g> <g><line x1="307.58620689655174" x2="307.58620689655174" y1="201" y2="206"></line><text x="307.58620689655174" y="221" text-anchor="middle">20</text></g> <g><line x1="374.48275862068965" x2="374.48275862068965" y1="201" y2="206"></line><text x="374.48275862068965" y="221" text-anchor="middle">25</text></g> <g><line x1="428" x2="428" y1="201" y2="206"></line><text x="428" y="221" text-anchor="middle">29</text></g> <text x="234" y="242" text-anchor="middle">Round (zero-based)</text></g> <polyline fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round" points="40,201 53.37931034482759,104.61 66.75862068965517,72.47999999999999 80.13793103448276,57.36 93.51724137931035,47.90999999999999 106.89655172413794,42.24000000000001 120.27586206896552,38.46 133.6551724137931,34.68 147.0344827586207,32.79 160.41379310344828,30.899999999999995 173.79310344827587,29.009999999999994 187.17241379310343,27.11999999999999 200.55172413793105,25.22999999999999 213.93103448275863,25.22999999999999 227.31034482758622,23.34000000000001 240.6896551724138,23.34000000000001 254.06896551724137,23.34000000000001 267.44827586206895,21.45000000000001 280.82758620689657,21.45000000000001 294.2068965517241,21.45000000000001 307.58620689655174,21.45000000000001 320.9655172413793,19.560000000000006 334.34482758620686,19.560000000000006 347.7241379310345,19.560000000000006 361.1034482758621,19.560000000000006 374.48275862068965,19.560000000000006 387.86206896551727,19.560000000000006 401.2413793103448,17.670000000000005 414.62068965517244,17.670000000000005 428,17.670000000000005"><title>L1+L2+L3</title></polyline> <polyline fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="8 5" stroke-linejoin="round" points="40,201 53.37931034482759,104.61 66.75862068965517,72.47999999999999 80.13793103448276,57.36 93.51724137931035,47.90999999999999 106.89655172413794,42.24000000000001 120.27586206896552,38.46 133.6551724137931,34.68 147.0344827586207,32.79 160.41379310344828,30.899999999999995 173.79310344827587,29.009999999999994 187.17241379310343,27.11999999999999 200.55172413793105,25.22999999999999 213.93103448275863,25.22999999999999 227.31034482758622,23.34000000000001 240.6896551724138,23.34000000000001 254.06896551724137,23.34000000000001 267.44827586206895,21.45000000000001 280.82758620689657,83.82000000000001 294.2068965517241,201 307.58620689655174,201 320.9655172413793,201 334.34482758620686,201 347.7241379310345,201 361.1034482758621,201 374.48275862068965,201 387.86206896551727,201 401.2413793103448,201 414.62068965517244,201 428,201"><title>L1+L2</title></polyline> <polyline fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="2 5" stroke-linejoin="round" points="40,201 53.37931034482759,189.66 66.75862068965517,201 80.13793103448276,201 93.51724137931035,201 106.89655172413794,201 120.27586206896552,201 133.6551724137931,201 147.0344827586207,201 160.41379310344828,201 173.79310344827587,201 187.17241379310343,201 200.55172413793105,201 213.93103448275863,201 227.31034482758622,201 240.6896551724138,201 254.06896551724137,201 267.44827586206895,201 280.82758620689657,201 294.2068965517241,201 307.58620689655174,201 320.9655172413793,201 334.34482758620686,201 347.7241379310345,201 361.1034482758621,201 374.48275862068965,201 387.86206896551727,201 401.2413793103448,201 414.62068965517244,201 428,201"><title>L1</title></polyline> <rect x="35" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 0 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈0%</title></rect> <rect x="48.37931034482759" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 1 L1: ≈6% L1+L2: ≈51% L1+L2+L3: ≈51%</title></rect> <rect x="61.758620689655174" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 2 L1: ≈0% L1+L2: ≈68% L1+L2+L3: ≈68%</title></rect> <rect x="75.13793103448276" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 3 L1: ≈0% L1+L2: ≈76% L1+L2+L3: ≈76%</title></rect> <rect x="88.51724137931035" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 4 L1: ≈0% L1+L2: ≈81% L1+L2+L3: ≈81%</title></rect> <rect x="101.89655172413794" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 5 L1: ≈0% L1+L2: ≈84% L1+L2+L3: ≈84%</title></rect> <rect x="115.27586206896552" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 6 L1: ≈0% L1+L2: ≈86% L1+L2+L3: ≈86%</title></rect> <rect x="128.6551724137931" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 7 L1: ≈0% L1+L2: ≈88% L1+L2+L3: ≈88%</title></rect> <rect x="142.0344827586207" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 8 L1: ≈0% L1+L2: ≈89% L1+L2+L3: ≈89%</title></rect> <rect x="155.41379310344828" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 9 L1: ≈0% L1+L2: ≈90% L1+L2+L3: ≈90%</title></rect> <rect x="168.79310344827587" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 10 L1: ≈0% L1+L2: ≈91% L1+L2+L3: ≈91%</title></rect> <rect x="182.17241379310343" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 11 L1: ≈0% L1+L2: ≈92% L1+L2+L3: ≈92%</title></rect> <rect x="195.55172413793105" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 12 L1: ≈0% L1+L2: ≈93% L1+L2+L3: ≈93%</title></rect> <rect x="208.93103448275863" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 13 L1: ≈0% L1+L2: ≈93% L1+L2+L3: ≈93%</title></rect> <rect x="222.31034482758622" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 14 L1: ≈0% L1+L2: ≈94% L1+L2+L3: ≈94%</title></rect> <rect x="235.6896551724138" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 15 L1: ≈0% L1+L2: ≈94% L1+L2+L3: ≈94%</title></rect> <rect x="249.06896551724137" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 16 L1: ≈0% L1+L2: ≈94% L1+L2+L3: ≈94%</title></rect> <rect x="262.44827586206895" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 17 L1: ≈0% L1+L2: ≈95% L1+L2+L3: ≈95%</title></rect> <rect x="275.82758620689657" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 18 L1: ≈0% L1+L2: ≈62% L1+L2+L3: ≈95%</title></rect> <rect x="289.2068965517241" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 19 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈95%</title></rect> <rect x="302.58620689655174" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 20 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈95%</title></rect> <rect x="315.9655172413793" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 21 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈96%</title></rect> <rect x="329.34482758620686" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 22 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈96%</title></rect> <rect x="342.7241379310345" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 23 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈96%</title></rect> <rect x="356.1034482758621" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 24 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈96%</title></rect> <rect x="369.48275862068965" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 25 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈96%</title></rect> <rect x="382.86206896551727" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 26 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈96%</title></rect> <rect x="396.2413793103448" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 27 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈97%</title></rect> <rect x="409.62068965517244" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 28 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈97%</title></rect> <rect x="423" y="8" width="10" height="197" fill="transparent"><title>Round (zero-based) 29 L1: ≈0% L1+L2: ≈0% L1+L2+L3: ≈97%</title></rect></svg>

Final metrics with L3 hit rate **96.8%** avg TTFT **1.23 s**

## Session-aware eviction

Applications use a stable `session_id` to identify requests from the same conversation. SGLang tracks that session's references to cached entries. Calling `/close_session` removes its references; shared prefixes keep those from other sessions.

FULL orders unlocked, eligible entries by reference presence, reference count, and then the base eviction policy, usually reclaiming unreferenced data first. Session retention applies to L1/L2; the storage backend manages L3 eviction.

Session-aware eviction diagramFULL entries · unlocked and eligible for eviction · AB is shared by A and B

t = 0/5

Ordinary LRU

**A1** **AB** **B1** **C1** **C2** recently used

Session-aware eviction

**A1** A · active **AB** A + B · 2 **B1** B · active **C1** unreferenced **C2** unreferenced

A and B retain session references, AB is shared by both, and C1/C2 are unreferenced.

### SWE-bench results

On SWE-bench, enabling Unified Radix Cache together with session-aware eviction lowers TTFT by up to 11.0% on DeepSeek-V4-Pro and 16.6% on Qwen3.5-397B-A17B, compared with HiRadixCache and LRU.

SWE-bench session-aware results diagram

DeepSeek-V4-Pro · TP8TTFT reduction vs baseline

batch 128

−11%

batch 256

−2.9%

Hit-ratio changebatch 128 · device hits 42% → **51%**

Qwen3.5-397B-A17B · TP8TTFT reduction vs baseline

batch 32

−13.5%

batch 64

−16.6%

Hit-ratio changebatch 32 · device hits 5% → **34%** batch 64 · device+host hits 58% → **67%**

## Rust tree core

SGLang runs tree traversal, lock bookkeeping, and LRU updates in Rust to reduce their CPU overhead on the scheduler. Python handles physical KV allocation and cache orchestration, applying the operations Rust returns to the pools.

Rust and Python ownership diagramOwnership of tree structure and pool operations

**Python owns**
- request-to-token mappings
- physical KV allocation
- pool ops and orchestration

match / insert / evict calls→←deferred actions

**Rust tree core owns**
- radix topology
- per-component lock accounting
- intrusive LRU lists
- eviction walks

The L1-only Rust prototype [#29074](https://github.com/sgl-project/sglang/pull/29074) reduced TTFT by 38% for SWA, 10% for full attention, and 5% for hybrid SSM against the Python tree in a [200-turn conversation benchmark](https://github.com/lm-sys/lm-sys.github.io/tree/main/scripts/rust_radix_cache/multi_turn).

Rust prototype benchmark diagramPrototype #29074 · L1 only · 200 turns · 100 in + 100 out per turn · 6 trials · sequential runs on the same GPUs

SWA gpt-oss-20b · TP2

All 200 turns

−38%

Turns 176–200

−42%

Full attention Qwen3-32B · TP2

All 200 turns

−10%

Last 25 turns

−18%

Hybrid SSM Qwen3-Next-80B-A3B · TP4

All 200 turns

−5%

Last 25 turns

−7%

The subsequently merged [Rust TreeCore #32710](https://github.com/sgl-project/sglang/pull/32710) supports FULL, SWA, and MAMBA combinations and HiCache. Session-aware caching continues to use the Python tree core.

## Further reading

- [LMSYS Blog: Unified Radix Cache: One Tree for Hybrid Model Prefix Caching](https://www.lmsys.org/blog/2026-08-11-unified-radix-cache/)
- [sglang#32710: \[Radix Cache\] Add Rust TreeCore backend with shared parity tests](https://github.com/sgl-project/sglang/pull/32710)
- [sglang#20415: \[Roadmap\] Unified Hybrid Radix Cache Refactor](https://github.com/sgl-project/sglang/issues/20415)
- [sglang#21846: \[Roadmap\]: SGLang Distributed KVCache System For Agentic Workload](https://github.com/sgl-project/sglang/issues/21846)
- [sglang#29074: \[WIP\] Rust Unified Radix Cache (L1 only)](https://github.com/sgl-project/sglang/pull/29074)
- [Rust prototype: reproduction scripts](https://github.com/lm-sys/lm-sys.github.io/tree/main/scripts/rust_radix_cache/multi_turn)
- [SGLang HiCache system design](https://docs.sglang.io/docs/advanced_features/hicache_design)

*The visualized tutorial was written by [Yichi Zhang](https://github.com/Ccyest) and the SGLang Team.*
