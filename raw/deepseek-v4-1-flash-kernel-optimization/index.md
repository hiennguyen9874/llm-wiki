---
title: "DeepSeek-V4.1 Flash on SGLang: from 35 to 873 tokens/s"
author: "SGLang Team"
site: "SGLang"
source: "https://www.sglang.io/blog/deepseek-v4.1-flash-kernel-optimization"
domain: "sglang.io"
language: "en"
description: "From our first working build at 35 tokens/s to 873 tokens/s at BS=1 on 4× GB300: MXFP8 GEMM, small-operator fusion, single-pass mHC overlap, DSpark verify, MoE, indexer and C2 verify kernels, and MoE TP4 with padding."
word_count: 2673
---

From 35 to 873 tokens/s: the kernel optimization journeySGLang · DeepSeek-V4.1 Flash · 4× GB300 · BS=1 · attention TP4

**16** MoE TP4 + padding

hover or click a round

BS=1 **873.6** tokens/s

measured accept length **5.505**

all fusions kept · expert intermediate dim split by TP4 · 576 → 640 per GPU with padding · less waiting between ranks

<svg viewBox="0 0 720 446" role="img" aria-label="From 35 to 873 tokens/s: the kernel optimization journey: BS=1 35.2 → 873.6 tokens/s over 16 rounds" style="width: 100%; height: auto; display: block;"><rect x="462.6" y="32" width="241.39999999999998" height="382" fill="currentColor" rx="6"></rect><text x="56" y="20" font-size="12" font-weight="700" fill="#888" letter-spacing="0.06em">PLAIN DECODE</text> <text x="698" y="20" text-anchor="end" font-size="12" font-weight="700" fill="#888" letter-spacing="0.06em">DSPARK · RANDOM 4K/1K · SIMULATED ACCEPT LENGTH 5.5</text> <text x="56" y="36" font-size="10" font-weight="500" font-style="italic" fill="#888">from the first working build</text> <text x="56" y="54" font-size="10" font-weight="600" fill="currentColor">Output tokens/s</text> <g><line x1="56" x2="698" y1="388" y2="388" stroke="currentColor" stroke-width="1"></line><text x="48" y="391.5" text-anchor="end" font-size="12" fill="#888">0</text></g> <g><line x1="56" x2="698" y1="331.2" y2="331.2" stroke="currentColor" stroke-width="1"></line><text x="48" y="334.7" text-anchor="end" font-size="12" fill="#888">200</text></g> <g><line x1="56" x2="698" y1="274.4" y2="274.4" stroke="currentColor" stroke-width="1"></line><text x="48" y="277.9" text-anchor="end" font-size="12" fill="#888">400</text></g> <g><line x1="56" x2="698" y1="217.6" y2="217.6" stroke="currentColor" stroke-width="1"></line><text x="48" y="221.1" text-anchor="end" font-size="12" fill="#888">600</text></g> <g><line x1="56" x2="698" y1="160.79999999999998" y2="160.79999999999998" stroke="currentColor" stroke-width="1"></line><text x="48" y="164.29999999999998" text-anchor="end" font-size="12" fill="#888">800</text></g> <g><line x1="56" x2="698" y1="104" y2="104" stroke="currentColor" stroke-width="1"></line><text x="48" y="107.5" text-anchor="end" font-size="12" fill="#888">1000</text></g> <polyline points="56,378.0032 98.8,354.5448 141.6,350.086 184.4,347.9276 227.2,346.394 270,345.8544 312.8,344.8036 355.6,335.0624 398.4,335.0056 441.2,330.26279999999997" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"></polyline><line x1="441.2" y1="330.26279999999997" x2="484" y2="229.47119999999998" stroke="#888" stroke-width="1.5" stroke-dasharray="5 5"></line><polyline points="484,229.47119999999998 526.8,183.8608 569.6,171.6772 612.4,160.1184 655.2,145.606 698,139.89759999999998" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"></polyline><g><circle cx="56" cy="378.0032" r="14" fill="transparent"></circle><circle cx="56" cy="378.0032" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>1. First working build: 35.2 tokens/s</title></g> <g><circle cx="98.8" cy="354.5448" r="14" fill="transparent"></circle><circle cx="98.8" cy="354.5448" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>2. MXFP8 GEMM: 117.8 tokens/s</title></g> <g><circle cx="141.6" cy="350.086" r="14" fill="transparent"></circle><circle cx="141.6" cy="350.086" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>3. RoPE + FP4 fusion: 133.5 tokens/s</title></g> <g><circle cx="184.4" cy="347.9276" r="14" fill="transparent"></circle><circle cx="184.4" cy="347.9276" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>4. mHC row tiles by input rows: 141.1 tokens/s</title></g> <g><circle cx="227.2" cy="346.394" r="14" fill="transparent"></circle><circle cx="227.2" cy="346.394" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>5. Reduce + Sinkhorn fusion: 146.5 tokens/s</title></g> <g><circle cx="270" cy="345.8544" r="14" fill="transparent"></circle><circle cx="270" cy="345.8544" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>6. Cross-layer shared scratch: 148.4 tokens/s</title></g> <g><circle cx="312.8" cy="344.8036" r="14" fill="transparent"></circle><circle cx="312.8" cy="344.8036" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>7. C2 pooling fusion: 152.1 tokens/s</title></g> <g><circle cx="355.6" cy="335.0624" r="14" fill="transparent"></circle><circle cx="355.6" cy="335.0624" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>8. mHC statistics overlap: 186.4 tokens/s</title></g> <g><circle cx="398.4" cy="335.0056" r="14" fill="transparent"></circle><circle cx="398.4" cy="335.0056" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>9. Fast paths on by default: 186.6 tokens/s</title></g> <g><circle cx="441.2" cy="330.26279999999997" r="14" fill="transparent"></circle><circle cx="441.2" cy="330.26279999999997" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>10. GEMV / norm / Engram gate: 203.3 tokens/s</title></g> <g><circle cx="484" cy="229.47119999999998" r="14" fill="transparent"></circle><circle cx="484" cy="229.47119999999998" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>11. DSpark on: 558.2 tokens/s</title></g> <g><circle cx="526.8" cy="183.8608" r="14" fill="transparent"></circle><circle cx="526.8" cy="183.8608" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>12. Verify / MoE fusion: 718.8 tokens/s</title></g> <g><circle cx="569.6" cy="171.6772" r="14" fill="transparent"></circle><circle cx="569.6" cy="171.6772" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>13. Small-batch projections / mHC: 761.7 tokens/s</title></g> <g><circle cx="612.4" cy="160.1184" r="14" fill="transparent"></circle><circle cx="612.4" cy="160.1184" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>14. Indexer post-processing / projection fusion: 802.4 tokens/s</title></g> <g><circle cx="655.2" cy="145.606" r="14" fill="transparent"></circle><circle cx="655.2" cy="145.606" r="3.2" fill="Canvas" stroke="currentColor" stroke-width="1.5"></circle><title>15. C2 verify compression fusion: 853.5 tokens/s</title></g> <g><circle cx="698" cy="139.89759999999998" r="14" fill="transparent"></circle><circle cx="698" cy="139.89759999999998" r="6" fill="currentColor" stroke="currentColor" stroke-width="2"></circle><title>16. MoE TP4 + padding: 873.6 tokens/s</title></g> <text x="56" y="356.0032" text-anchor="start" font-size="14" font-weight="700" fill="currentColor">35.2</text> <text x="698" y="117.89759999999998" text-anchor="end" font-size="14" font-weight="700" fill="currentColor">873.6</text> <g><rect x="45" y="410" width="22" height="22" fill="transparent"></rect><text x="56" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">1</text></g> <g><rect x="87.8" y="410" width="22" height="22" fill="transparent"></rect><text x="98.8" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">2</text></g> <g><rect x="130.6" y="410" width="22" height="22" fill="transparent"></rect><text x="141.6" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">3</text></g> <g><rect x="173.4" y="410" width="22" height="22" fill="transparent"></rect><text x="184.4" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">4</text></g> <g><rect x="216.2" y="410" width="22" height="22" fill="transparent"></rect><text x="227.2" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">5</text></g> <g><rect x="259" y="410" width="22" height="22" fill="transparent"></rect><text x="270" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">6</text></g> <g><rect x="301.8" y="410" width="22" height="22" fill="transparent"></rect><text x="312.8" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">7</text></g> <g><rect x="344.6" y="410" width="22" height="22" fill="transparent"></rect><text x="355.6" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">8</text></g> <g><rect x="387.4" y="410" width="22" height="22" fill="transparent"></rect><text x="398.4" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">9</text></g> <g><rect x="430.2" y="410" width="22" height="22" fill="transparent"></rect><text x="441.2" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">10</text></g> <g><rect x="473" y="410" width="22" height="22" fill="transparent"></rect><text x="484" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">11</text></g> <g><rect x="515.8" y="410" width="22" height="22" fill="transparent"></rect><text x="526.8" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">12</text></g> <g><rect x="558.6" y="410" width="22" height="22" fill="transparent"></rect><text x="569.6" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">13</text></g> <g><rect x="601.4" y="410" width="22" height="22" fill="transparent"></rect><text x="612.4" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">14</text></g> <g><rect x="644.2" y="410" width="22" height="22" fill="transparent"></rect><text x="655.2" y="426" text-anchor="middle" font-size="12" font-weight="500" fill="#888">15</text></g> <g><rect x="687" y="410" width="22" height="22" fill="transparent"></rect><text x="698" y="426" text-anchor="middle" font-size="12" font-weight="750" fill="currentColor">16</text></g></svg>

For launch coverage and recipes, see the [day-0 support post](https://www.sglang.io/blog/deepseek-v4.1-day0-support) and the [LMSYS post](https://www.lmsys.org/blog/2026-09-10-deepseek-v41).

## Architecture changes and KV cache compression

V4.1 Flash has a larger backbone than V4 Flash but activates fewer parameters per input token, and its KV cache is far smaller. The rows that matter for serving:

|  | V4 Flash | V4.1 Flash |
| --- | --- | --- |
| Backbone | 284B | 552B, plus 196B of Engram memory parameters |
| Active per token | ~13B | ~8B on input, ~16B on output |
| Structure | 43 decoder layers | 20 causal encoder layers + 20 decoder layers |
| Global attention | CSA / HCA | CSA2, KV and indices shared across layers |
| Global KV per token | 3,514 bytes | 890 bytes |

Numbers are from the [model config](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) and the [technical report](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf).

**The causal encoder-decoder structure cuts prefill compute.** The 20 decoder layers get their global KV from the encoder's final output, so a long prompt is mostly processed by the first 20 layers. The decoder still needs a local window, which it rebuilds by replaying the last 128 tokens. That roughly halves prefill work in the backbone. Generated tokens are another matter: each one still runs through all 40 layers.

Encoder-decoder split and the shared KV cachePrompts mostly pass through the first 20 layers; generation still runs all 40.

<svg viewBox="0 0 720 558" role="img" aria-label="Encoder-decoder split and the shared KV cache. 3514 B → 890 B per token, about a quarter of V4 Flash" style="width: 100%; height: auto; display: block;"><defs><marker id="ced-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"></path></marker></defs><g><rect x="0" y="0" width="318" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="159" y="44" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Causal encoder · 20 layers</text> <text x="159" y="70" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">Handles the long prompt</text> <text x="159" y="88" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">Produces the global KV the decoder reads</text></g> <line x1="336" y1="56" x2="384" y2="56" stroke="currentColor" stroke-width="1.5" marker-end="url(#ced-arrow)"></line><g><rect x="402" y="0" width="318" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="561" y="44" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Decoder · 20 layers</text> <text x="561" y="70" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">Reads the shared global KV</text> <text x="561" y="88" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">Local window from the last 128 tokens</text></g> <text x="0" y="196" font-size="12" font-weight="750" fill="currentColor" letter-spacing="0.04em">GLOBAL KV FROM FOUR LAYERS</text> <g><g><rect x="0" y="226" width="153" height="90" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="76.5" y="268" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Layer 2</text> <text x="76.5" y="294" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">2 tokens → 1 entry</text></g> <line x1="76.5" y1="326" x2="76.5" y2="370" stroke="currentColor" stroke-width="1.5" marker-end="url(#ced-arrow)"></line></g><g><g><rect x="189" y="226" width="153" height="90" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="265.5" y="268" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Layer 8</text> <text x="265.5" y="294" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">2 tokens → 1 entry</text></g> <line x1="265.5" y1="326" x2="265.5" y2="370" stroke="currentColor" stroke-width="1.5" marker-end="url(#ced-arrow)"></line></g><g><g><rect x="378" y="226" width="153" height="90" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="454.5" y="268" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Layer 14</text> <text x="454.5" y="294" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">2 tokens → 1 entry</text></g> <line x1="454.5" y1="326" x2="454.5" y2="370" stroke="currentColor" stroke-width="1.5" marker-end="url(#ced-arrow)"></line></g><g><g><rect x="567" y="226" width="153" height="90" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="643.5" y="268" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Layer 20</text> <text x="643.5" y="294" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">1 token → 1 entry</text></g> <line x1="643.5" y1="326" x2="643.5" y2="370" stroke="currentColor" stroke-width="1.5" marker-end="url(#ced-arrow)"></line></g><g><rect x="0" y="378" width="720" height="68" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="360" y="418" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Other layers reuse the cache · some recompute indices · attention reads the top-512 positions</text></g> <text x="0" y="506" font-size="12" font-weight="500" fill="currentColor">FP4: main KV 288 B + indexer K 68 B per entry</text> <text x="0" y="540" font-size="22" font-weight="750" fill="currentColor" letter-spacing="-0.01em">3514 B → 890 B per token</text> <text x="720" y="540" text-anchor="end" font-size="12" font-weight="600" fill="currentColor">about a quarter of V4 Flash</text></svg>

**The KV cache compression comes from sharing, pooling and FP4 storage.** Only four of the 40 layers produce global KV, layers 2, 8, 14 and 20. The rest read those caches, and a few recompute their own indices. The first three of those caches pool every two tokens into a single entry, and only the last keeps one entry per token. The entries themselves are stored in FP4, at 288 bytes for the main KV and 68 bytes for the indexer K. Per original token that comes to

$$
(288 + 68) \times \left(\tfrac{3}{2} + 1\right) = 890\ \text{bytes,}
$$

about a quarter of V4 Flash. Since the local window can always be rebuilt by replay, less state needs to persist, and DeepSeek puts the SSD cache requirement at roughly an eighth of before. One caveat: 890 bytes is the logical size. Some SGLang paths still use a FlashMLA-compatible cache layout, so the memory actually allocated differs.

Two more pieces of the architecture show up throughout the kernel work. CSA2 narrows the indexer's search with a hierarchical candidate filter, so that in the end only the top 512 global positions take part in attention. Engram adds a form of conditional memory through n-gram lookups. They do different jobs in the model, and each brought new indexing, normalization and fusion work of its own.

## Kernel optimizations for plain decode

First, a look back at how plain decode went from 35 tokens/s on our first working build to 203 tokens/s. The numbers in this section are the original measurements; the DSpark section switches to the random 4k/1k workload described at the end.

### FP8 GEMM: 35 → 118 tokens/s

Some of the dense weights ship in FP8, but their quantization block and scale layout did not match what the backend expected, so those GEMMs were taking a slower fallback path. We now rearrange the scale layout once, when the weights are loaded, and they go straight into the Blackwell MXFP8 GEMM.

That alone took BS=1 from **35.2 to 117.8 tokens/s**. When bringing up a new model, checking which kernel a GEMM actually dispatches to is usually worth more than tuning tiles.

### Small-operator fusion and GEMV

Token-by-token decode runs a long chain of short kernels. RoPE, FP4 quantization, compressor pooling, RMSNorm and the cache write feed directly into one another, so fusing neighbors saves a launch and a trip through memory each time.

| Fusion | Implementation | BS=1 tokens/s |
| --- | --- | --- |
| RoPE + FP4 | Rotation, quantization and dequantization in one kernel | 117.8 → 133.5 |
| C2 compressor | Normalization, pooling and the state write for adjacent tokens | 148.4 → 152.1 |
| WO-A, norm, Engram gate | GEMV for single-row projections; fused kernels for the small norms and gates | 186.6 → 203.3 |

We also stopped rebuilding the per-step request indices and scratch buffers in every layer and shared them across layers instead, which cut out a fair amount of repeated conversion and initialization and took BS=1 from **146.5 to 148.4 tokens/s**. Once the fast paths had been validated, we turned them on by default.

### mHC: reduction fusion and overlap

mHC keeps four residual streams instead of one. For every attention and MoE sublayer it has to compute mixing coefficients for them and normalize those coefficients with Sinkhorn. None of it is expensive on its own, but it runs once for attention and once for MoE in every layer, and at small batch that adds up. Picking tile sizes based on the number of input rows, and then fusing the statistics reduction with Sinkhorn, took BS=1 from **133.5 to 141.1 and then to 146.5 tokens/s**.

Overlap in single-pass mHCPre-mix uses the previous sublayer's coefficients; the statistics overlap with attention / MoE.

<svg viewBox="0 0 720 296" role="img" aria-label="Overlap in single-pass mHC. Two streams in parallel, joined before post-mix" style="width: 100%; height: auto; display: block;"><defs><marker id="mhc-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"></path></marker></defs><g><rect x="0" y="92" width="162" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="81" y="145" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Four residual streams</text> <text x="81" y="171" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">current input</text></g> <g><rect x="222" y="0" width="116" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="280" y="53" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Pre-mix + RMSNorm</text> <text x="280" y="79" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">previous pre coefficients</text></g> <g><rect x="382" y="0" width="116" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="440" y="62" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Attention / MoE</text></g> <g><rect x="222" y="184" width="276" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="360" y="237" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Statistics + Sinkhorn</text> <text x="360" y="263" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">this post / comb, and the next pre</text></g> <g><rect x="558" y="92" width="162" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="639" y="154" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Post-mix</text></g> <line x1="174" y1="130" x2="210" y2="68" stroke="currentColor" stroke-width="1.5" marker-end="url(#mhc-arrow)"></line><line x1="174" y1="166" x2="210" y2="228" stroke="currentColor" stroke-width="1.5" marker-end="url(#mhc-arrow)"></line><line x1="346" y1="56" x2="374" y2="56" stroke="currentColor" stroke-width="1.5" marker-end="url(#mhc-arrow)"></line><line x1="510" y1="68" x2="546" y2="130" stroke="currentColor" stroke-width="1.5" marker-end="url(#mhc-arrow)"></line><line x1="510" y1="228" x2="546" y2="166" stroke="currentColor" stroke-width="1.5" marker-end="url(#mhc-arrow)"></line><text x="360" y="152" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Two streams in parallel, joined before post-mix</text></svg>

The larger gain comes from how V4.1's single-pass mHC is defined. The pre-mix uses coefficients produced by the previous sublayer, so the current attention or MoE can run in parallel with this sublayer's statistics. We run the two on separate streams and join them at the post-mix. Combined with the compressor and indexer fusion and overlap, this took BS=1 from about **152 to 186 tokens/s**.

## DSpark adaptation and optimization

DSpark ships with the official checkpoint, including three lightweight draft blocks. They take hidden states from the last few layers of the main model, produce logits for several positions at once, resolve the dependencies between draft tokens with a Markov head, and hand the block to the target model for batched verification.

DSpark: verify several tokens per stepDraft weights ship in the official checkpoint. Measured at block size 5 with a simulated accept length of 5.5.

<svg viewBox="0 0 720 430" role="img" aria-label="DSpark: verify several tokens per step. Rows entering verify ≠ request batch size: 1 request (BS = 1) → verify handles up to 6 rows" style="width: 100%; height: auto; display: block;"><defs><marker id="dspark-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"></path></marker></defs><g><g><rect x="0" y="0" width="200" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="100" y="53" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Main-model hidden states</text> <text x="100" y="79" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">from the last few layers</text></g> <line x1="214" y1="56" x2="246" y2="56" stroke="currentColor" stroke-width="1.5" marker-end="url(#dspark-arrow)"></line></g><g><g><rect x="260" y="0" width="200" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="360" y="44" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">3 draft blocks</text> <text x="360" y="70" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">5 positions at once</text> <text x="360" y="88" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">Markov head resolves dependencies</text></g> <line x1="474" y1="56" x2="506" y2="56" stroke="currentColor" stroke-width="1.5" marker-end="url(#dspark-arrow)"></line></g><g><g><rect x="520" y="0" width="200" height="112" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="620" y="44" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">Target verify</text> <text x="620" y="70" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">batched verification</text> <text x="620" y="88" text-anchor="middle" font-size="12" font-weight="500" fill="currentColor">commits the accepted prefix</text></g></g> <g><rect x="0" y="184" width="108" height="60" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="54" y="220" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">anchor</text></g> <g><rect x="122.4" y="184" width="108" height="60" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="176.4" y="220" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">draft 1</text></g> <g><rect x="244.8" y="184" width="108" height="60" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="298.8" y="220" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">draft 2</text></g> <g><rect x="367.20000000000005" y="184" width="108" height="60" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="421.20000000000005" y="220" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">draft 3</text></g> <g><rect x="489.6" y="184" width="108" height="60" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="543.6" y="220" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">draft 4</text></g> <g><rect x="612" y="184" width="108" height="60" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="666" y="220" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">draft 5</text></g> <text x="360" y="304" text-anchor="middle" font-size="14" font-weight="650" fill="currentColor">Rows entering verify ≠ request batch size</text> <g><rect x="100" y="340" width="520" height="90" rx="12" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="360" y="391" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">1 request (BS = 1) → verify handles up to 6 rows</text></g></svg>

We fix the block size at 5 and simulate acceptance with a target accept length of 5.5. Counting the anchor, target verify handles up to 6 rows for a single request. Plain decode handles one row per request, so the M=1 fast paths had to be reworked for these small batches.

**The first group of optimizations went into verify and MoE.** We wired the mHC overlap into verify and draft, and made the WO-A projection write directly into the layout the next stage needs. The candidate mask fuses the valid-length check with candidate handling, which cuts down on scans over large buffers. On the MoE side, the router now emits the layout the experts need, input quantization overlaps routing, and the expert-weighted reduction, shared-expert add and all-reduce run as one step, which cuts intermediate write-back.

**Next came the small-batch projections and normalization.** WO-A uses split-K so more thread blocks work at once, and mHC fuses the mixing of the four residual streams with RMSNorm. The draft's multiple KV projections now reuse the MXFP8 weights and scales instead of the old FP8 path.

**Next we fused more of the indexer post-processing and the projections.** The post-Top-K score check, invalid-position filtering and KV page address translation are now a single step, and chosen candidate blocks expand straight into a token mask. Q's RoPE is merged into the attention buffer write, and WO-A's split-K reduction does the following MXFP8 quantization itself, skipping an intermediate tensor.

**Then we turned to verify-time compression in L2, L8 and L14 (layers numbered from 0).** These three layers used to run a chain of small operators to find the previous token, handle the mask, then pool and write the cache. Verify positions are contiguous, so within a request the previous row can be read directly; only the first row needs the ring buffer. We fused pair pooling, RMSNorm, RoPE, quantization and the main KV write into a single kernel, and then reused the fused write for index-K.

**Finally, MoE moved from EP4 to TP4 with padding.** Split by TP4, the expert intermediate dimension is 576 per GPU, padded to 640 at load time to fit the kernel. Each GPU computes a different slice of the same experts, so uneven expert load causes less waiting. In a same-round comparison with all of the optimizations above in place, EP4 gives **854.64 tokens/s** and TP4 gives **873.63 tokens/s**, a **2.22%** gain; in the trace, the median gap between ranks arriving at finalize dropped from **11.14 to 3.40 µs**.

| Configuration | BS=1 output speed (tokens/s) | Measured accept length |
| --- | --- | --- |
| DSpark, before optimization | 558.24 | 5.505 |
| \+ verify / MoE fusion and overlap | 718.75 | 5.505 |
| \+ small-batch projections / mHC fusion | 761.71 | 5.505 |
| \+ indexer post-processing / Q RoPE / WO-A quantization | 802.38 | 5.505 |
| \+ C2 verify compression fusion | 853.49 | 5.520 |
| All optimizations, MoE switched to TP4 + padding | **873.63** | **5.505** |

On random 4k/1k with the simulated accept length targeting 5.5, output speed went from **558.24 to 873.63 tokens/s**, a gain of about **56.5%**. The table keeps the 853.49 measured when C2 verify fusion landed; the 2.22% above comes from this round's EP4 / TP4 comparison.

**None of these results use the new kernels DeepSeek released with V4.1.**

## How to reproduce: random 4k/1k, simulated accept length fixed at 5.5

This section reproduces the DSpark points 11 to 16 in the figure: **4,096 random input tokens, a fixed 1,024 output tokens, and a simulated accept length targeting 5.5**. The server configuration controls the accept length, and every version uses the same input.

Use the SGLang code at [BBuf/sglang@835c3909](https://github.com/BBuf/sglang/tree/835c39094ad017c2f54f8ea598002e669e6fa30d) and the official checkpoint at [revision dba1be0a](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/tree/dba1be0a40aa45a94ad051997016db3960a90277), on 4× GB300. We were on PyTorch 2.13.0+cu130, FlashInfer 0.6.18, Triton 3.7.1, sglang-kernel 0.4.6.post1, sgl-deep-gemm 0.1.7 and CUTLASS DSL 4.6.2.

Below is the **TP4 serving command behind the 873.63 tokens/s**, run from the root of that SGLang checkout. `--tp 4 --ep-size 1` means both attention and MoE use TP4; this version applies the padding when it loads the weights.

```
export MODEL_PATH=/path/to/DeepSeek-V4.1-Flash
export SGLANG_RAGGED_VERIFY_MODE=static
export SGLANG_SIMULATE_ACC_LEN=5.5
export SGLANG_SIMULATE_ACC_METHOD=match-expected
CUDA_VISIBLE_DEVICES=0,1,2,3 PYTHONPATH="$PWD/python" MAX_JOBS=16 \
python -m sglang.launch_server \
  --model-path "$MODEL_PATH" \
  --served-model-name deepseek-ai/DeepSeek-V4.1-Flash \
  --tp 4 --ep-size 1 --trust-remote-code \
  --moe-a2a-backend none --moe-runner-backend flashinfer_mxfp4 \
  --mem-fraction-static 0.80 --max-total-tokens 33554432 \
  --chunked-prefill-size 4096 \
  --cuda-graph-bs-decode 1 2 4 8 16 32 64 \
  --max-running-requests 128 \
  --speculative-algorithm DSPARK --speculative-dspark-block-size 5 \
  --skip-server-warmup --reasoning-parser deepseek-v41 \
  --random-seed 42 --decode-log-interval 10 \
  --host 127.0.0.1 --port 30021
```

To reproduce the EP4 comparison, change `--ep-size 1` to `--ep-size 4` and keep everything else. The full TP4 launch script is available as [launch-tp4.sh](https://raw.githubusercontent.com/BBuf/how-to-optim-algorithm-in-cuda/master/large-language-model/sglang/assets/deepseek-v41-kernel-journey/random-dspark/launch-tp4.sh).

The input is generated with the fixed random seed `42`: special tokens are excluded from the model vocabulary, and 4,096 token ids are drawn uniformly. The ids go in directly, with no chat template, and every configuration reuses them.

- [The random input](https://raw.githubusercontent.com/BBuf/how-to-optim-algorithm-in-cuda/master/large-language-model/sglang/assets/deepseek-v41-kernel-journey/random-dspark/prompt.json) (`prompt.json`).
- [Input construction, benchmark script and per-run results](https://github.com/BBuf/how-to-optim-algorithm-in-cuda/tree/master/large-language-model/sglang/assets/deepseek-v41-kernel-journey/random-dspark).

In a second terminal:

```
ASSET_URL=https://raw.githubusercontent.com/BBuf/how-to-optim-algorithm-in-cuda/master/large-language-model/sglang/assets/deepseek-v41-kernel-journey/random-dspark
curl -fL "$ASSET_URL/prompt.json" -o prompt.json
curl -fL "$ASSET_URL/benchmark.py" -o benchmark.py
python -m pip install requests
python benchmark.py bench --prompt prompt.json --max-tokens 1024 --out result --repeat 6
```

The script uses `temperature=0` and `ignore_eos=True`, and checks on every run that the input was **4,096 tokens** and the output **1,024 tokens**. Inputs go through `/generate`; the script calls `/freeze_gc` after startup, clears the cache before each run, and discards one warm-up. Each server launch is measured for 6 runs. The small-batch projection, indexer post-processing / projection fusion, C2 verify and TP4 configurations were each launched twice independently, with the median taken over the 12 runs. For this round's EP4 / TP4 comparison the launches alternated TP, EP, TP, EP, all measurements were kept, and the profiler was off while measuring throughput.

`match-expected` accepts 5 or 6 tokens on each round, so the expected accept length is **5.5**. A finite number of rounds and truncation at the last step move the measured value slightly, and the table keeps the actual values. Acceptance is simulated, so the generated text is not used to judge answer quality; simulation mode also disables the in-graph acceptance path.

Throughput is computed as the number of tokens added after the first streamed event divided by the time from the first event to the last, and does not include full prefill. Accept length counts the token the target model produces, so with block size 5 the ceiling is 6.

The table below puts DSpark off and on side by side, plus the MoE TP4 + padding configuration. All entries use the same code, the same random input, the same output length and the same timing method, with **attention on TP4 throughout**; EP4 / TP4 in the header refer to the MoE configuration.

| Workload and metric | DSpark off · EP4 | DSpark on · EP4 | DSpark on · TP4 + padding |
| --- | --- | --- | --- |
| BS=1, output speed (tokens/s) | 223.50 | 853.49 | **873.63** |
| BS=1, measured accept length (simulated target 5.5) |  | 5.520 | **5.505** |

## Related links

- [LMSYS Blog: SGLang and Miles Add Day-0 Support for DeepSeek-V4.1](https://www.lmsys.org/blog/2026-09-10-deepseek-v41): the team's full day-0 write-up, covering inference and RL training.
- [SGLang DeepSeek-V4.1 deployment guide](https://docs.sglang.io/cookbook/autoregressive/DeepSeek/DeepSeek-V4_1): launch configuration, hardware support and tuning notes.
- [SGLang DeepSeek-V4.1 code](https://github.com/sgl-project/sglang/tree/dsv4.1), the dsv4.1 branch.
- [Miles DeepSeek-V4.1 Flash training guide](https://miles.radixark.com/docs/models/deepseek/deepseek-v4-1-flash): training environment, checkpoint preparation and RL launch configuration.
- [Miles on GitHub](https://github.com/radixark/miles).
- [DeepSeek-V4.1 technical report](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf).

For the kernel implementations, see [C2 verify compression](https://github.com/BBuf/sglang/blob/835c39094ad017c2f54f8ea598002e669e6fa30d/python/sglang/kernels/ops/attention/dsv4/c2.py), [indexer post-processing](https://github.com/BBuf/sglang/blob/835c39094ad017c2f54f8ea598002e669e6fa30d/python/sglang/kernels/ops/attention/dsv4/indexer_postprocess.py), [Q RoPE / store](https://github.com/BBuf/sglang/blob/835c39094ad017c2f54f8ea598002e669e6fa30d/python/sglang/kernels/ops/attention/dsv4/q_rope_store.py) and [WO-A / MXFP8](https://github.com/BBuf/sglang/blob/835c39094ad017c2f54f8ea598002e669e6fa30d/python/sglang/kernels/ops/attention/dsv4/wo_a_bf16_small_batch.py) directly.

## Acknowledgments

Thanks to the DeepSeek team for open-sourcing DeepSeek-V4.1, and to everyone on the SGLang and Miles teams and in the community who helped with the model support, the kernels, testing and review. Some of the kernels were developed with the KDA 0.5 framework, and we are grateful to [Humanize](https://github.com/humanfia/humanize2) and [Kernel Design Agents](https://github.com/NVlabs/kda) for the tools and the workflow.
