---
title: "Kimi K3: Architecture and SGLang Day-0 Support"
author: "SGLang Team"
site: "SGLang"
source: "https://www.sglang.io/blog/kimi-k3-day0-support"
domain: "sglang.io"
language: "en"
description: "From MHA to DeltaNet to KDA — how Kimi K3's hybrid architecture supports 2.8T parameters and a 1M context, and how SGLang runs it with a unified memory pool, chunked PP, and DCP."
word_count: 5771
---

Kimi K3 in SGLang

TP8 · 8×GB300

1. BaselineP044.3
2. Launch & copy eliminationP1–P464.2
3. NVIDIA compute kernelsP5–P874.5
4. Communication fusionP9 · P12 · P13102.1
5. Overlap & prologue fusionP10 · P11 · P14 · P15112.5
6. DSpark speculative decodingdraft model~423

## The Kimi K3 architecture

K3 is a 2.8T-parameter MoE model with 104B parameters active per token, and it supports a native 1M-token context. K3 has 93 layers: 69 use KDA linear attention and 24 use gated global MLA. The first layer is a dense FFN; the remaining 92 use Stable LatentMoE. The 93 layers split into 8 blocks of 12, and Attention Residual aggregates across blocks. Click the diagram for the complete structure:

K3 at a glance

AttnRes retrievalResidual path Click a component for detail

<svg viewBox="0 0 960 700" role="img" aria-label="K3 at a glance" style="width: 100%; max-width: 960px; min-width: 760px; --viz-stroke-hairline: 1.2; --viz-stroke-line: 1.7; --viz-stroke-emphasis: 2.9; --viz-stroke-hero: 4.6;"><defs><marker id="arch-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 8 4 L 0 8 z" fill="currentColor"></path></marker></defs><rect x="556" y="60" width="300" height="316" rx="12" fill="none" stroke="#ccc" stroke-width="1.2" stroke-dasharray="6 4"></rect><text x="660" y="30" text-anchor="middle" font-size="13.9" font-weight="650" fill="currentColor">Output</text> <path d="M 660 376 L 660 52" fill="none" stroke="currentColor" stroke-width="1.4"></path><line x1="660" y1="44" x2="660" y2="36" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><g><rect x="770" y="48" width="24" height="16" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="782" y="59.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">w</text></g> <g><circle cx="660" cy="56" r="10" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="660" y="59.6" text-anchor="middle" font-size="13.9" fill="currentColor">α</text></g> <path d="M 770 56 L 670 56" fill="none" stroke="currentColor" stroke-width="1"></path><g><g style="cursor: pointer;"><title>Except for the first dense FFN, each layer selects 16 of 896 routed experts plus 2 shared experts; routing scores the full 7168-d hidden state, while the selected experts compute in a 3584-d latent space.</title><rect x="585" y="96" width="150" height="26" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect> <text x="660" y="112.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">Stable LatentMoE</text></g> <g><circle cx="660" cy="76" r="9" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="660" y="79.6" text-anchor="middle" font-size="13.9" fill="currentColor">+</text></g> <path d="M 660 132 L 568 132 L 568 76 L 651 76" fill="none" stroke="currentColor" stroke-width="1"></path><g><rect x="788" y="75" width="24" height="16" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="800" y="86.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">w</text></g> <path d="M 800 91 L 800 98" fill="none" stroke="currentColor" stroke-width="1"></path><g><circle cx="800" cy="109" r="10" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="800" y="112.6" text-anchor="middle" font-size="13.9" fill="currentColor">α</text></g> <line x1="789" y1="109" x2="735" y2="109" stroke="currentColor" stroke-width="1" marker-end="url(#arch-arrow)"></line><path d="M 811 109 L 872 109 L 872 424 L 740 424" fill="none" stroke="currentColor" stroke-width="1"></path></g><g><g style="cursor: pointer;"><title>Global softmax attention (with an output gate); its KV cache grows with context. One per 3 KDA layers, providing full-context interaction.</title><rect x="585" y="164" width="150" height="26" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect> <text x="660" y="180.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">Gated MLA</text></g> <g><circle cx="660" cy="144" r="9" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="660" y="147.6" text-anchor="middle" font-size="13.9" fill="currentColor">+</text></g> <path d="M 660 200 L 568 200 L 568 144 L 651 144" fill="none" stroke="currentColor" stroke-width="1"></path><g><rect x="788" y="143" width="24" height="16" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="800" y="154.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">w</text></g> <path d="M 800 159 L 800 166" fill="none" stroke="currentColor" stroke-width="1"></path><g><circle cx="800" cy="177" r="10" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="800" y="180.6" text-anchor="middle" font-size="13.9" fill="currentColor">α</text></g> <line x1="789" y1="177" x2="735" y2="177" stroke="currentColor" stroke-width="1" marker-end="url(#arch-arrow)"></line><path d="M 811 177 L 886 177 L 886 458 L 740 458" fill="none" stroke="currentColor" stroke-width="1"></path></g><g><g style="cursor: pointer;"><title>Except for the first dense FFN, each layer selects 16 of 896 routed experts plus 2 shared experts; routing scores the full 7168-d hidden state, while the selected experts compute in a 3584-d latent space.</title><rect x="585" y="232" width="150" height="26" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect> <text x="660" y="248.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">Stable LatentMoE</text></g> <g><circle cx="660" cy="212" r="9" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="660" y="215.6" text-anchor="middle" font-size="13.9" fill="currentColor">+</text></g> <path d="M 660 268 L 568 268 L 568 212 L 651 212" fill="none" stroke="currentColor" stroke-width="1"></path><g><rect x="788" y="211" width="24" height="16" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="800" y="222.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">w</text></g> <path d="M 800 227 L 800 234" fill="none" stroke="currentColor" stroke-width="1"></path><g><circle cx="800" cy="245" r="10" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="800" y="248.6" text-anchor="middle" font-size="13.9" fill="currentColor">α</text></g> <line x1="789" y1="245" x2="735" y2="245" stroke="currentColor" stroke-width="1" marker-end="url(#arch-arrow)"></line><path d="M 811 245 L 900 245 L 900 514 L 740 514" fill="none" stroke="currentColor" stroke-width="1"></path></g><g><g style="cursor: pointer;"><title>Linear attention: a fixed-size recurrent state overwritten in place, O(1) per decode step. The update rule is a delta rule with per-channel gating, covered below.</title><rect x="585" y="300" width="150" height="26" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect> <text x="660" y="316.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">KDA</text></g> <g><circle cx="660" cy="280" r="9" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="660" y="283.6" text-anchor="middle" font-size="13.9" fill="currentColor">+</text></g> <path d="M 660 336 L 568 336 L 568 280 L 651 280" fill="none" stroke="currentColor" stroke-width="1"></path><g><rect x="788" y="279" width="24" height="16" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="800" y="290.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">w</text></g> <path d="M 800 295 L 800 302" fill="none" stroke="currentColor" stroke-width="1"></path><g><circle cx="800" cy="313" r="10" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="800" y="316.6" text-anchor="middle" font-size="13.9" fill="currentColor">α</text></g> <line x1="789" y1="313" x2="735" y2="313" stroke="currentColor" stroke-width="1" marker-end="url(#arch-arrow)"></line><path d="M 811 313 L 914 313 L 914 514 L 740 514" fill="none" stroke="currentColor" stroke-width="1"></path></g><g><path d="M 536 90 L 528 90 L 528 196 L 536 196" fill="none" stroke="currentColor" stroke-width="1.2"></path><text x="516" y="147" text-anchor="middle" font-size="13.9" font-weight="650" fill="currentColor">1×</text></g> <g><path d="M 536 226 L 528 226 L 528 332 L 536 332" fill="none" stroke="currentColor" stroke-width="1.2"></path><text x="516" y="283" text-anchor="middle" font-size="13.9" font-weight="650" fill="currentColor">3×</text></g> <text x="660" y="366" text-anchor="middle" font-size="16.2" fill="#888">⋮</text> <g><g><rect x="590" y="412" width="150" height="24" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="665" y="427.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Block n−1</text></g></g> <g><g><rect x="590" y="446" width="150" height="24" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="665" y="461.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Block n−2</text></g></g> <g><g style="cursor: pointer;"><title>No RoPE anywhere. Position comes implicitly from the KDA recurrence; MLA layers run global attention without position encoding.</title><rect x="590" y="502" width="150" height="24" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect> <text x="665" y="517.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">Embedding</text></g></g> <text x="665" y="482" text-anchor="middle" font-size="16.2" fill="#888">⋮</text> <line x1="660" y1="502" x2="660" y2="400" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><rect x="576" y="548" width="180" height="132" rx="10" fill="none" stroke="#ccc" stroke-width="1.2" stroke-dasharray="6 4"></rect><text x="586" y="566" font-size="13.9" fill="#888">Native vision pathway</text> <g><rect x="600" y="574" width="132" height="24" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="666" y="589.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">MLP</text></g> <g style="cursor: pointer;"><title>K3's native vision tower; images and videos enter the shared embedding space through the encoder and a lightweight projector.</title><rect x="600" y="616" width="132" height="24" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect> <text x="666" y="631.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">MoonViT-V2</text></g> <rect x="654" y="654" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><rect x="654" y="662" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><rect x="654" y="670" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><rect x="662" y="654" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><rect x="662" y="662" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><rect x="662" y="670" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><rect x="670" y="654" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><rect x="670" y="662" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><rect x="670" y="670" width="7" height="7" rx="1" fill="currentColor" stroke="currentColor" stroke-width="1.2"></rect><line x1="666" y1="654" x2="666" y2="642" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="666" y1="616" x2="666" y2="600" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="666" y1="574" x2="666" y2="528" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><rect x="20" y="60" width="470" height="240" rx="12" fill="none" stroke="#ccc" stroke-width="1.2" stroke-dasharray="6 4"></rect><text x="32" y="78" font-size="13.9" fill="#888">The Stable LatentMoE module</text> <path d="M 470 108 L 556 64" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3 3"></path><rect x="352" y="96" width="12" height="12" rx="3" fill="currentColor" stroke="#ccc" stroke-width="1.2"></rect><text x="370" y="106" font-size="13.9" fill="currentColor">shared expert</text> <rect x="352" y="116" width="12" height="12" rx="3" fill="currentColor" stroke="#ccc" stroke-width="1.2"></rect><text x="370" y="126" font-size="13.9" fill="currentColor">routed expert</text> <path d="M 250 292 L 250 268" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 190 268 L 320 268" fill="none" stroke="currentColor" stroke-width="1.4"></path><g><rect x="160" y="244" width="60" height="22" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="190" y="258.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Router</text></g> <rect x="226" y="252" width="3.5" height="10" fill="currentColor" opacity="0.75"></rect><rect x="231" y="248" width="3.5" height="14" fill="currentColor" opacity="0.75"></rect><rect x="236" y="244" width="3.5" height="18" fill="currentColor" opacity="0.75"></rect><g><path d="M 258 244 L 324 244 L 312 266 L 270 266 Z" fill="currentColor" stroke="#ccc" stroke-width="1.2"></path><text x="291" y="258.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">Linear</text></g> <line x1="190" y1="258" x2="190" y2="236" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="291" y1="244" x2="291" y2="236" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><g><rect x="96" y="206" width="26" height="24" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="109" y="221.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">1</text></g> <g><rect x="134" y="206" width="26" height="24" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="147" y="221.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">2</text></g> <g><rect x="206" y="206" width="26" height="24" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1" stroke-dasharray="4 3"></rect><text x="219" y="221.5" text-anchor="middle" font-size="12" font-weight="600" fill="#888">1</text></g> <g><rect x="244" y="206" width="26" height="24" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="257" y="221.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">2</text></g> <g><rect x="282" y="206" width="26" height="24" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1" stroke-dasharray="4 3"></rect><text x="295" y="221.5" text-anchor="middle" font-size="12" font-weight="600" fill="#888">3</text></g> <text x="326" y="222" text-anchor="middle" font-size="13.9" fill="#888">⋯</text> <g><rect x="346" y="206" width="26" height="24" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="359" y="221.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">N</text></g> <path d="M 219 206 L 219 196 L 359 196 L 359 206" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3 3"></path><path d="M 257 206 L 257 184" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 359 206 L 359 184 L 257 184" fill="none" stroke="currentColor" stroke-width="1.4"></path><g><circle cx="257" cy="172" r="9" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="257" y="175.6" text-anchor="middle" font-size="13.9" fill="currentColor">+</text></g> <g><rect x="224" y="132" width="66" height="22" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="257" y="146.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Norm</text></g> <g><path d="M 236 96 L 278 96 L 290 118 L 224 118 Z" fill="currentColor" stroke="#ccc" stroke-width="1.2"></path><text x="257" y="110.5" text-anchor="middle" font-size="13.9" font-weight="600" fill="currentColor">Linear</text></g> <line x1="257" y1="163" x2="257" y2="154" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="257" y1="132" x2="257" y2="118" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="257" y1="96" x2="190" y2="92" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><path d="M 109 206 L 109 84 L 181 84" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 147 206 L 147 92 L 181 88" fill="none" stroke="currentColor" stroke-width="1.4"></path><g><circle cx="190" cy="84" r="9" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="190" y="87.6" text-anchor="middle" font-size="13.9" fill="currentColor">+</text></g> <line x1="190" y1="75" x2="190" y2="66" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><rect x="20" y="330" width="470" height="330" rx="12" fill="none" stroke="#ccc" stroke-width="1.2" stroke-dasharray="6 4"></rect><text x="32" y="348" font-size="13.9" fill="#888">The KDA module</text> <path d="M 470 452 L 556 352" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3 3"></path><path d="M 250 652 L 250 634" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 78 634 L 400 634" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 78 634 L 78 624" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 158 634 L 158 624" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 238 634 L 238 624" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 306 634 L 306 624" fill="none" stroke="currentColor" stroke-width="1.4"></path><path d="M 380 634 L 380 624" fill="none" stroke="currentColor" stroke-width="1.4"></path><g><rect x="48" y="600" width="60" height="22" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="78" y="614.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Linear</text></g> <g><rect x="128" y="600" width="60" height="22" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="158" y="614.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Linear</text></g> <g><path d="M 222 600 L 254 600 L 266 622 L 210 622 Z" fill="currentColor" stroke="#ccc" stroke-width="1.2"></path></g><g><path d="M 280 600 L 332 600 L 320 622 L 292 622 Z" fill="currentColor" stroke="#ccc" stroke-width="1.2"></path></g><g><rect x="350" y="600" width="60" height="22" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="380" y="614.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Linear</text></g> <g><rect x="48" y="560" width="60" height="22" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="78" y="574.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Conv</text></g> <g><rect x="128" y="560" width="60" height="22" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="158" y="574.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Conv</text></g> <line x1="78" y1="600" x2="78" y2="582" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="158" y1="600" x2="158" y2="582" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><g><circle cx="238" cy="574" r="8" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="238" y="577.6" text-anchor="middle" font-size="13.9" fill="currentColor">σ</text></g> <g><circle cx="306" cy="574" r="8" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="306" y="577.6" text-anchor="middle" font-size="13.9" fill="currentColor">σ</text></g> <g><circle cx="380" cy="574" r="8" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="380" y="577.6" text-anchor="middle" font-size="13.9" fill="currentColor">σ</text></g> <line x1="238" y1="600" x2="238" y2="582" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="306" y1="600" x2="306" y2="582" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="380" y1="600" x2="380" y2="582" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><g><circle cx="78" cy="536" r="8" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="78" y="539.6" text-anchor="middle" font-size="13.9" fill="currentColor">⊘</text></g> <g><circle cx="158" cy="536" r="8" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="158" y="539.6" text-anchor="middle" font-size="13.9" fill="currentColor">⊘</text></g> <line x1="78" y1="560" x2="78" y2="544" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="158" y1="560" x2="158" y2="544" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><g><rect x="58" y="500" width="40" height="22" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="78" y="514.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">L2</text></g> <line x1="78" y1="536" x2="78" y2="522" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><text x="70" y="490" text-anchor="middle" font-size="13.9" font-style="italic" font-weight="650" fill="currentColor">q</text> <text x="92" y="490" text-anchor="middle" font-size="13.9" font-style="italic" font-weight="650" fill="currentColor">k</text> <text x="170" y="490" text-anchor="middle" font-size="13.9" font-style="italic" font-weight="650" fill="currentColor">v</text> <text x="250" y="490" text-anchor="middle" font-size="13.9" font-style="italic" font-weight="650" fill="currentColor">α</text> <text x="318" y="490" text-anchor="middle" font-size="13.9" font-style="italic" font-weight="650" fill="currentColor">β</text> <g style="cursor: pointer;"><title>Linear attention: a fixed-size recurrent state overwritten in place, O(1) per decode step. The update rule is a delta rule with per-channel gating, covered below.</title><rect x="48" y="440" width="264" height="26" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect> <text x="180" y="456.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Kimi Delta Attention</text></g> <line x1="78" y1="500" x2="78" y2="466" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="158" y1="536" x2="158" y2="466" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="238" y1="566" x2="238" y2="466" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="306" y1="566" x2="306" y2="466" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><g><rect x="150" y="400" width="60" height="22" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="180" y="414.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Norm</text></g> <line x1="180" y1="440" x2="180" y2="422" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><g><circle cx="180" cy="380" r="9" fill="Canvas" stroke="currentColor" stroke-width="1.2"></circle><text x="180" y="383.6" text-anchor="middle" font-size="13.9" fill="currentColor">⊗</text></g> <line x1="180" y1="400" x2="180" y2="389" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><path d="M 380 566 L 380 380 L 189 380" fill="none" stroke="currentColor" stroke-width="1.4"></path><g><rect x="150" y="344" width="60" height="22" rx="6" fill="currentColor" stroke="#ccc" stroke-width="1"></rect><text x="180" y="358.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">Linear</text></g> <line x1="180" y1="371" x2="180" y2="366" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><line x1="180" y1="344" x2="180" y2="334" stroke="currentColor" stroke-width="1.4" marker-end="url(#arch-arrow)"></line><g style="cursor: pointer;"><title>2.8T total parameters, 104B active per token (≈3.7%); native 1M-token context.</title><rect x="20" y="8" width="132" height="22" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect> <text x="86" y="22.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">2.8T / 104B</text></g> <g style="cursor: pointer;"><title>Quantization-aware training starts at SFT: MoE expert weights use MXFP4 and their input activations use MXFP8; non-expert modules such as attention, LatentMoE projections, shared experts, and routers stay at higher precision.</title><rect x="164" y="8" width="96" height="22" rx="6" fill="Canvas" stroke="#ccc" stroke-width="1"></rect> <text x="212" y="22.5" text-anchor="middle" font-size="12" font-weight="600" fill="currentColor">MXFP4</text></g></svg>

### KV cache memory estimation

Start with memory: both MLA and MHA KV caches grow with context. The Kimi K3 day-0 support blog puts K3's compressed MLA KV cache at about 27KB per token per GPU across all 24 MLA layers, which works out to roughly 1.125KB per layer. If all 93 layers used MLA, a 1M-token request would need about 105GB on one GPU (1.125KB × 93 layers × 1M tokens). Uncompressed MHA at the same shape would store 48KB per layer per token (96 heads × 128 dims × K/V × bf16), more than 40× the MLA latent. Bringing that number down is the first problem to solve, which is why K3 cannot keep context-growing softmax attention in most layers.

K3 therefore interleaves 3 KDA + 1 MLA. KDA is a linear-attention variant whose recurrent state has a fixed size and does not grow with context; the mechanism comes later. It takes about 54MB per request per GPU and updates in place each step, while MLA keeps global attention. The model uses no explicit position encoding (NoPE); position comes implicitly from the KDA recurrence. The diagram below contrasts memory use between all-MLA and the KDA+MLA mix:

KV cache comparison

t = 0/16

K K K M K K K M 3 KDA + 1 MLA interleaved, ×23 blocks, plus one final MLA layer: 93 total

**Hypothetical: all 93 layers MLA** context 0K token · cache 0.0 GB · per token 105 KB

**K3: 24 MLA + 69 KDA layers** context 0K token · cache 0.1 GB · per token 27 KB

The next sections walk from classic MHA to KDA and compare what changes at each step, which makes it clear why Kimi K3 picks KDA, a linear-attention variant.

### Attention mechanisms in detail: classic MHA

In ordinary MHA, decoding token $t$ first appends its own KV to the cache, then reads all $t$ entries in three steps:

1. **Score:** compare against every token $i \le t$ with $z_{t,i} = \frac{q_t \cdot k_i}{\sqrt{d_k}}$. The subscript $t,i$ reads “step $t$ 's query against key $i$”.
2. **Normalize:** compute $Z = \sum_{j=1}^{t} \exp(z_{t,j})$, then assign attention weight $a_{t,i} = \exp(z_{t,i}) / Z$.
3. **Aggregate:** take the weighted sum of values, $o_t = \sum_{i=1}^{t} a_{t,i} \cdot v_i$.

A length- $N$ sequence therefore performs about $N^2/2$ dot products: $O(N^2)$ compute and $O(N)$ cache. In the diagram, every token has a line to each of the tokens before it.

MHA diagram

t = 0/9 SentenceMath

cache 0 cells · dot products this step 0 · cumulative 0

<svg viewBox="0 0 552 205" role="img" aria-label="MHA diagram" style="width: 100%; max-width: 552px; min-width: 500px;"><g><rect x="18" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><g><rect x="65" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><g><rect x="112" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><g><rect x="159" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><g><rect x="206" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><g><rect x="253" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><g><rect x="300" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><g><rect x="347" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><g><rect x="394" y="28" width="30" height="30" rx="5" fill="none" opacity="1" stroke="currentColor" stroke-width="1"></rect></g><text x="213" y="94" text-anchor="middle" font-size="10" fill="#888" font-weight="650">KV cache (after this step)</text><rect x="18" y="118" width="390" height="48" rx="8" fill="none" stroke="currentColor" stroke-opacity="0.4" stroke-width="1"></rect><g><rect x="500" y="125" width="34" height="34" rx="6" fill="currentColor" opacity="0.14" stroke="currentColor" stroke-width="1.5"></rect></g></svg>

Softmax attention buys per-position reads, which gives it the most complete global memory, but the cost is just as clear. Every new token rescans the whole history, so the whole history has to be stored and compute stays at $O(N^2)$.

### Attention mechanisms in detail: linear attention

Linear attention no longer keeps one KV entry per token. It accumulates history into a fixed-size matrix, $S = \sum_i k_i v_i^{\top}$. S is a fixed-size memory matrix, and every new token writes into it once it is computed: k sets the write direction, meaning where the token points in vector space; v is the content written along that direction; and q reads with $o = S^{\top} q$. No matter how long the context becomes, each step reads and writes only S.

The diagram below gives both a math view and the same sentence used earlier, so the difference is visible directly:

Naive linear attention diagram

t = 0/4 SentenceMath

2D teaching slice: the real S is 128×128 per head

2D key space (teaching slice)

<svg viewBox="0 0 230 180" role="img" aria-label="A and B are full key directions spanning both channels" style="width: 100%; max-width: 230px;"><defs><marker id="key-plane-a-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker><marker id="key-plane-b-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker></defs><line x1="24" y1="90" x2="216" y2="90" stroke="currentColor" stroke-width="1.5"></line><line x1="115" y1="164" x2="115" y2="16" stroke="currentColor" stroke-width="1.5"></line><text x="198" y="82" fill="#888" font-size="12">ch₁</text> <text x="123" y="25" fill="#888" font-size="12">ch₂</text> <line x1="115" y1="90" x2="184" y2="31" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#key-plane-a-arrow)"></line><line x1="115" y1="90" x2="184" y2="149" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#key-plane-b-arrow)"></line><text x="171" y="24" fill="currentColor" font-size="12" font-weight="700">kₐ</text> <text x="171" y="167" fill="currentColor" font-size="12" font-weight="700">kᵦ</text><circle cx="115" cy="90" r="4" fill="currentColor"></circle></svg>

`kₐ=(1/√2)[1,1]ᵀ``kᵦ=(1/√2)[1,−1]ᵀ`

arrows = full keys; axes = channels

S entering this step

**ch₁**

0

**ch₂**

0

−0+

S is empty

→ **directly add kvᵀ** S←S+kvᵀ

S after this step

**ch₁**

0

**ch₂**

0

−0+

S is empty

old A contributionB contributionnew contribution from A=4 Colors only trace provenance; the real S stores only the summed values

In MHA, "it" can point directly to "cat" because every historical token has its own KV position. The linear-attention state S has no token-position axis, so its readout mixes all historical writes in one fixed state. The diagram above shows the simplest form of naive linear attention: plain accumulation.

### Attention mechanisms in detail: DeltaNet

Naive linear attention keeps adding to its state and never overwrites an old value. In the simplest case, if the same key direction receives 1 and then 4, both stay in S, and the next read returns $1+4$. Different contexts usually give the same word different keys, but over a sequence as long as 1M tokens a fixed-capacity state can still fail to keep those writes apart. Say the text first says Zhang San lives in Beijing, so the state records Zhang San → Beijing, and later says Zhang San moved to Shanghai. Asked where Zhang San lives, the readout is likely a blend of Beijing and Shanghai rather than Shanghai cleanly overwriting Beijing.

DeltaNet's answer is an error-directed edit to the state. It introduces a dynamically produced scalar gate $\beta_t$ that sets how strong the current update is. Before writing, the model reads the prediction the state already holds along the current key, $r_{\text{old}} = S_{t-1}^{\top} k_t$. It then writes the difference between the target value and that prediction instead of accumulating $v_t$: $S_t = S_{t-1} + \beta_t k_t (v_t - r_{\text{old}})^{\top}$. For a normalized key, the new readout is $r_{\text{new}} = (1-\beta_t)\, r_{\text{old}} + \beta_t v_t$.

The coefficient $\beta_t$ controls rewrite strength: $\beta_t = 1$ fully replaces the old association, smaller $\beta_t$ retains more of the old value, and $\beta_t = 0$ does not rewrite it at all.

DeltaNet diagramAdjust β and see how A=4 rewrites A=1

t = 0/4 β=1β=0.8β=0.5β=0.3β=0

2D key space (teaching slice)

<svg viewBox="0 0 230 180" role="img" aria-label="A and B are full key directions spanning both channels" style="width: 100%; max-width: 230px;"><defs><marker id="key-plane-a-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker><marker id="key-plane-b-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker></defs><line x1="24" y1="90" x2="216" y2="90" stroke="currentColor" stroke-width="1.5"></line><line x1="115" y1="164" x2="115" y2="16" stroke="currentColor" stroke-width="1.5"></line><text x="198" y="82" fill="#888" font-size="12">ch₁</text> <text x="123" y="25" fill="#888" font-size="12">ch₂</text> <line x1="115" y1="90" x2="184" y2="31" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#key-plane-a-arrow)"></line><line x1="115" y1="90" x2="184" y2="149" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#key-plane-b-arrow)"></line><text x="171" y="24" fill="currentColor" font-size="12" font-weight="700">kₐ</text> <text x="171" y="167" fill="currentColor" font-size="12" font-weight="700">kᵦ</text><circle cx="115" cy="90" r="4" fill="currentColor"></circle></svg>

`kₐ=(1/√2)[1,1]ᵀ``kᵦ=(1/√2)[1,−1]ᵀ`

arrows = full keys; axes = channels

S entering this step

**ch₁**

0

**ch₂**

0

−0+

S is empty

→ **waiting for a token**

S after this step

**ch₁**

0

**ch₂**

0

−0+

S is empty

old A contributionB contributionnew contribution from A=4 Colors only trace provenance; the real S stores only the summed values

That fixes same-direction rewriting but leaves a capacity question: once unrelated history keeps entering a fixed-size S, what should decay? Even unrelated key vectors are rarely perfectly orthogonal in practice, so a write in one direction projects into another and creates crosstalk. The longer the context, the larger that effect gets.

Math details: A/B in the diagram and the crosstalk term

A and B are two unit directions $k_a, k_b$ in key space $\mathbb{R}^{d_k}$ ($\lVert k_a \rVert = \lVert k_b \rVert = 1$), not token slots or individual channels. $A=1$ is shorthand for “the key points along $k_a$ and the value is the scalar 1.” Colors only trace where each write came from; the real S stores their sum.

Suppose S holds two associations, $S = k_a v_a^{\top} + k_b v_b^{\top}$. Reading with $q_a = k_a$ gives $o_a = S^{\top} q_a = (k_a^{\top} k_a)\, v_a + (k_b^{\top} k_a)\, v_b = v_a + \cos\theta \cdot v_b$, where $\theta$ is the angle between the two keys. The second term is B leaking into A, scaled exactly by the inner product $k_a^{\top} k_b$.

For a general set of writes $\{(k_i, v_i)\}$ the readout is $o(q) = \sum_i (k_i^{\top} q)\, v_i$, and interference between writes is governed by the Gram matrix $G_{ij} = k_i^{\top} k_j$. The readout is crosstalk-free iff all keys are pairwise orthogonal — and $\mathbb{R}^{d_k}$ admits at most $d_k$ such directions, so once more associations are stored, crosstalk in a fixed-size state cannot be eliminated, only managed.

Crosstalk diagramKeep kₐ fixed and drag kᵦ; the example uses qₐ=kₐ and vₐ=vᵦ=1

θ=90°θ=60°θ=30°θ=0° or drag kᵦ in the figure

<svg viewBox="0 0 620 260" role="img" aria-label="Crosstalk diagram" style="width: 100%; max-width: 620px; min-width: 500px; touch-action: none;"><defs><marker id="overlap-blue-arrow" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="7" markerHeight="7" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0 L8 4 L0 8z" fill="currentColor"></path></marker><marker id="overlap-orange-arrow" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="7" markerHeight="7" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0 L8 4 L0 8z" fill="currentColor"></path></marker><marker id="overlap-green-arrow" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="7" markerHeight="7" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0 L8 4 L0 8z" fill="currentColor"></path></marker></defs><line x1="38" y1="155" x2="292" y2="155" stroke="currentColor" stroke-width="1"></line><line x1="145" y1="38" x2="145" y2="224" stroke="currentColor" stroke-width="1"></line><path d="M 179 155 A 34 34 0 0 0 162 125.55513627132909" fill="none" stroke="#888" stroke-width="1"></path><text x="179.64101615137756" y="131" font-size="12" fill="#888">θ=60°</text> <line x1="145" y1="155" x2="237" y2="155" stroke="currentColor" stroke-width="2.5" marker-end="url(#overlap-blue-arrow)"></line><text x="245" y="159" font-size="12" fill="#888" font-weight="700">kₐ = qₐ</text> <line x1="145" y1="155" x2="191" y2="75.32566285183165" stroke="currentColor" stroke-width="2.5" marker-end="url(#overlap-orange-arrow)"></line><text x="199" y="70.32566285183165" font-size="12" fill="#888" font-weight="700">kᵦ</text> <circle cx="191" cy="75.32566285183165" r="10" fill="currentColor" stroke="currentColor" stroke-width="2.5"></circle><text x="191" y="99.32566285183165" text-anchor="middle" font-size="12" fill="#888">drag B</text> <line x1="191" y1="75.32566285183165" x2="191" y2="155" stroke="currentColor" stroke-dasharray="4 3" stroke-width="1.5" opacity="0.7"></line><line x1="145" y1="167" x2="191" y2="167" stroke="currentColor" stroke-width="2.5" marker-end="url(#overlap-orange-arrow)" opacity="0.8"></line><text x="168" y="184" text-anchor="middle" font-size="12" fill="#888">cos θ = 0.50</text> <line x1="145" y1="155" x2="225.04" y2="108.78888445406236" stroke="currentColor" stroke-width="2.5" stroke-dasharray="5 3" marker-end="url(#overlap-green-arrow)"></line><text x="232.04" y="111.78888445406236" font-size="12" fill="#888" font-weight="700">S = kₐ + kᵦ</text> <g transform="translate(350 56)"><text x="0" y="0" font-size="12" fill="currentColor" font-weight="700">kₐᵀkᵦ = cos θ = 0.50</text> <text x="0" y="28" font-size="12" fill="currentColor">S = kₐ·vₐ + kᵦ·vᵦ</text> <text x="0" y="50" font-size="12" fill="currentColor">oₐ = qₐᵀS = 1 + cos θ</text> <rect x="0" y="72" width="210" height="26" rx="5" fill="none" stroke="currentColor"></rect><rect x="2" y="74" width="102" height="22" rx="3" fill="currentColor" opacity="0.85"></rect><rect x="106" y="74" width="51.000000000000014" height="22" rx="3" fill="currentColor" opacity="0.85"></rect><text x="51" y="89" text-anchor="middle" font-size="12" fill="currentColor" font-weight="700">A = 1</text> <text x="131.5" y="89" text-anchor="middle" font-size="12" fill="currentColor" font-weight="700">B = 0.50</text> <text x="0" y="120" font-size="12" fill="#888">A target signal = 1</text> <text x="0" y="140" font-size="12" fill="#888">B leakage into A = 0.50</text> <text x="0" y="168" font-size="12" fill="#888" font-weight="700">smaller angle → more crosstalk</text></g></svg>

### Attention mechanisms in detail: KDA

KDA's gating works per channel, so first, what a channel is. K3's hidden size is 7168; each of the 96 KDA heads uses its own learned projection to compress the model-wide 7168-d hidden state down to 128 dimensions, and a channel is one dimension of that projected 128-d space. Key channel $j$ sets the coefficient with which content is written into row $j$ of S:

Channel diagram

**hidden state**`xₜ ∈ ℝ⁷¹⁶⁸`

**k for one head**

*chⱼ* *…*

`kₜ ∈ ℝ¹²⁸`the highlighted dim = one channel

A fixed state does not grow with context, which is exactly why it saves memory; the cost is that more and more history has to share one S. The delta rule can rewrite the same or a nearby key direction, but it does not proactively clear irrelevant old signal, which is the crosstalk above. KDA therefore adds channel-wise gating: for every token and head, the model produces a vector $\alpha_t$ from the current hidden state, applies $\mathrm{Diag}(\alpha_t)$ to scale the channels of the old state, and then performs the DeltaNet rewrite.

Math details: how KDA gates and rewrites the same S

The full update is $S_t = \big(I - \beta_t k_t k_t^{\top}\big)\,\mathrm{Diag}(\alpha_t)\, S_{t-1} + \beta_t k_t v_t^{\top}$. Term by term: $\alpha_t \in (0,1)^{d_k}$ is a vector gate computed from the current hidden state, and $\mathrm{Diag}(\alpha_t)$ scales row $j$ of S by $\alpha_t[j]$ — every historical contribution in that row decays together; it neither picks A or B apart nor rotates keys toward orthogonality. $\beta_t \in (0,1)$ is a scalar write strength.

Read one update in two steps. Gate first: $\tilde S = \mathrm{Diag}(\alpha_t)\, S_{t-1}$. Then delta-rewrite along the current key: with $r_{\text{old}} = \tilde S^{\top} k_t$ (the decayed state's prediction for this key), $S_t = \tilde S + \beta_t k_t (v_t - r_{\text{old}})^{\top}$. For a unit $k_t$, the post-update readout along the same key is $S_t^{\top} k_t = (1-\beta_t)\, r_{\text{old}} + \beta_t v_t$: $\beta_t = 1$ replaces fully, $\beta_t = 0$ keeps everything.

Unrolling the recurrence shows where position comes from: $S_t = \sum_{s \le t} \Big[\prod_{u=s+1}^{t} \big(I - \beta_u k_u k_u^{\top}\big)\mathrm{Diag}(\alpha_u)\Big]\, \beta_s k_s v_s^{\top}$. Earlier writes pass through more gates and rewrites, so decay accumulates with distance — the mechanism that lets K3 drop RoPE. K3 also pins a lower bound on $\alpha$ 's log-decay with a scaled sigmoid ($g_{\min} = -5$, so every step's retention exceeds $e^{-5} \approx 6.7\times10^{-3}$): chunkwise computation has to rescale keys by the reciprocal cumulative decay, and bounding that numerical range lets both diagonal and off-diagonal tiles run as dense Tensor Core matmuls, removing the position-pair diagonal path Kimi Linear needed. The output gate moves from Kimi Linear's low-rank parameterization to an input-dependent full-rank projection.

The diagram compresses the real 128-d key space into a 2D teaching slice: $k_a = \tfrac{1}{\sqrt{2}}[1,1]^{\top}$ and $k_b = \tfrac{1}{\sqrt{2}}[1,-1]^{\top}$, both spanning $\mathrm{ch}_1$ and $\mathrm{ch}_2$. The gate scales both rows first, then the delta rule writes along the full $k_a$ the residual needed to reach target value 4.

KDA diagramAdjust α₁, α₂, and β to see how the state changes

t = 0/4 **α₁** 10.80.50.30.1 **α₂** 10.80.50.30.1 **β** 10.80.50.30

2D key space (teaching slice)

<svg viewBox="0 0 230 180" role="img" aria-label="A and B are full key directions spanning both channels" style="width: 100%; max-width: 230px;"><defs><marker id="key-plane-a-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker><marker id="key-plane-b-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker></defs><line x1="24" y1="90" x2="216" y2="90" stroke="currentColor" stroke-width="1.5"></line><line x1="115" y1="164" x2="115" y2="16" stroke="currentColor" stroke-width="1.5"></line><text x="198" y="82" fill="#888" font-size="12">ch₁</text> <text x="123" y="25" fill="#888" font-size="12">ch₂</text> <line x1="115" y1="90" x2="184" y2="31" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#key-plane-a-arrow)"></line><line x1="115" y1="90" x2="184" y2="149" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#key-plane-b-arrow)"></line><text x="171" y="24" fill="currentColor" font-size="12" font-weight="700">kₐ</text> <text x="171" y="167" fill="currentColor" font-size="12" font-weight="700">kᵦ</text><circle cx="115" cy="90" r="4" fill="currentColor"></circle></svg>

`kₐ=(1/√2)[1,1]ᵀ``kᵦ=(1/√2)[1,−1]ᵀ`

arrows = full keys; axes = channels

S entering this step

**ch₁**

0

**ch₂**

0

−0+

S is empty

→ **Diag(α)** α=1

② S after Diag(α)

**ch₁**

0

**ch₂**

0

−0+

S is empty

→ **delta along full kₐ** first write

③ S after delta along kₐ

**ch₁**

0

**ch₂**

0

−0+

S is empty

old A contributionB contributionthis step's residual update along kₐ Colors only trace provenance; the real S stores only the summed values

So Kimi K3 needs no RoPE, because the KDA state update already carries position. An earlier token passes through more decay steps and state transforms before it reaches the current position, while a nearer token passes through fewer, and the model reads order and distance from that. Where RoPE encodes position explicitly with a fixed rotation, KDA models it implicitly through learnable, input-dependent decay. K3 also lower-bounds that decay to keep the chunkwise numerical range in check, so every causal tile in the KDA kernel can run on Tensor Cores; the output gate becomes a full-rank projection.

### Attention Residual

An ordinary Transformer's residual stream is like one draft passed from the bottom layer to the top, with every layer editing the same page. This keeps information moving upward, but by layer 90, shallow details are mixed with dozens of later updates; a deep layer cannot reopen an earlier version directly.

Attention Residual keeps a few historical versions on the side. K3 splits its 93 layers into 8 blocks — 12 layers each for the first seven, 9 for the last — and each block sums its own layer outputs into one block representation. No layer has to rely only on the current draft: each one uses its own learned pseudo-query to weight the embedding, every preceding block's summary, and its own block's partial sum so far, and the mixture is that layer's input — the once-accumulating residual is taken over inside a block by that partial sum:

Attention Residual diagram

**Standard residual**`hℓ = hℓ₋₁ + Fℓ(hℓ₋₁)`

<svg viewBox="0 0 760 230" role="img" aria-label="Standard residual" style="width: 100%; max-width: 760px;"><defs><marker id="attnres-chain-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker></defs><text x="380" y="34" text-anchor="middle">One residual stream: Emb + F₁ + F₂ + …</text> <g><line x1="110" y1="105" x2="148" y2="105" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#attnres-chain-arrow)" opacity="0.62"></line><rect x="28" y="76" width="82" height="58" rx="12" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="69" y="111" text-anchor="middle">Emb</text></g> <g><line x1="236" y1="105" x2="274" y2="105" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#attnres-chain-arrow)" opacity="0.62"></line><rect x="154" y="76" width="82" height="58" rx="12" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="195" y="111" text-anchor="middle">L1</text> <text x="195" y="156" text-anchor="middle">h1=h0+F1</text></g> <g><line x1="362" y1="105" x2="400" y2="105" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#attnres-chain-arrow)" opacity="0.62"></line><rect x="280" y="76" width="82" height="58" rx="12" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="321" y="111" text-anchor="middle">L2</text> <text x="321" y="156" text-anchor="middle">h2=h1+F2</text></g> <g><line x1="488" y1="105" x2="526" y2="105" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#attnres-chain-arrow)" opacity="0.62"></line><rect x="406" y="76" width="82" height="58" rx="12" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="447" y="111" text-anchor="middle">L3</text> <text x="447" y="156" text-anchor="middle">h3=h2+F3</text></g> <g><line x1="614" y1="105" x2="652" y2="105" stroke="currentColor" stroke-width="4" stroke-linecap="round" marker-end="url(#attnres-chain-arrow)" opacity="0.62"></line><rect x="532" y="76" width="82" height="58" rx="12" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="573" y="111" text-anchor="middle">…</text></g> <g><rect x="658" y="76" width="82" height="58" rx="12" fill="Canvas" stroke="#ccc" stroke-width="1"></rect><text x="699" y="111" text-anchor="middle">L93</text></g> <path d="M72 184H688" stroke="currentColor" stroke-width="1" stroke-dasharray="5 5"></path><text x="380" y="210" text-anchor="middle">Layer ℓ directly receives only the aggregate hℓ₋₁ from the previous layer</text></svg>

Shallow information must survive every intervening addition; a deep layer cannot retrieve one earlier output on its own.

**Attention Residual**`hℓ = Σᵢ αℓᵢ bᵢ`

<svg viewBox="0 0 760 230" role="img" aria-label="Attention Residual" style="width: 100%; max-width: 760px;"><defs><marker id="attnres-bank-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker></defs><text x="315" y="26" text-anchor="middle">Prior block summaries remain separate</text> <g><path d="M62 153 Q366 56.28 664 79" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" opacity="0.55" marker-end="url(#attnres-bank-arrow)"></path><text x="62" y="102" text-anchor="middle">α=0.22</text> <rect x="24" y="138" width="76" height="50" rx="11" fill="currentColor" stroke="#ccc"></rect><text x="62" y="169" text-anchor="middle">Emb</text></g> <g><path d="M168 153 Q419 52.57 664 79" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" opacity="0.55" marker-end="url(#attnres-bank-arrow)"></path><text x="168" y="102" text-anchor="middle">α=0.03</text> <rect x="130" y="138" width="76" height="50" rx="11" fill="currentColor" stroke="#ccc"></rect><text x="168" y="169" text-anchor="middle">B₁</text></g> <g><path d="M274 153 Q472 48.86 664 79" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity="0.55" marker-end="url(#attnres-bank-arrow)"></path><text x="274" y="102" text-anchor="middle">α=0.05</text> <rect x="236" y="138" width="76" height="50" rx="11" fill="currentColor" stroke="#ccc"></rect><text x="274" y="169" text-anchor="middle">B₂</text></g> <g><path d="M380 153 Q525 45.15 664 79" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" opacity="0.55" marker-end="url(#attnres-bank-arrow)"></path><text x="380" y="102" text-anchor="middle">α=0.10</text> <rect x="342" y="138" width="76" height="50" rx="11" fill="currentColor" stroke="#ccc"></rect><text x="380" y="169" text-anchor="middle">B₃</text></g> <g><path d="M486 153 Q578 41.44 664 79" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" opacity="0.55" marker-end="url(#attnres-bank-arrow)"></path><rect x="448" y="138" width="76" height="50" rx="11" fill="currentColor" stroke="#ccc"></rect><text x="486" y="169" text-anchor="middle">…</text></g> <g><path d="M592 153 Q631 37.730000000000004 664 79" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" opacity="0.55" marker-end="url(#attnres-bank-arrow)"></path><text x="592" y="102" text-anchor="middle">α=0.22</text> <rect x="554" y="138" width="76" height="50" rx="11" fill="currentColor" stroke="#ccc"></rect><text x="592" y="169" text-anchor="middle">B₇</text></g> <circle cx="684" cy="68" r="30" fill="currentColor"></circle><text x="684" y="76" text-anchor="middle">Σα</text> <line x1="684" y1="99" x2="684" y2="131" stroke="currentColor" stroke-width="4" marker-end="url(#attnres-bank-arrow)"></line><rect x="646" y="138" width="76" height="50" rx="11" fill="currentColor" stroke="currentColor"></rect><text x="684" y="169" text-anchor="middle">B₈</text> <text x="684" y="211" text-anchor="middle">input to B₈'s first layer</text></svg>

A deep layer forms a softmax-weighted mixture of saved summaries rather than selecting one exact layer, creating shorter paths for information and gradients.

Math and cost: why K3 saves one summary every 12 layers

Let $b_0$ be the embedding, $b_n$ the summary of block $n$ (the accumulated outputs of its layers), and $b_n^{\,i-1}$ the partial sum over the first $i-1$ layers of block $n$. Retrieval is done **per layer**: layer $i$ of block $n$ has its own learned pseudo-query $q$, and its candidate set is $\{b_0, b_1, \ldots, b_{n-1}\}$ when $i = 1$, plus $b_n^{\,i-1}$ when $i \ge 2$. Scoring $\alpha = \mathrm{softmax}\big(s(q, \cdot)\big)$ with a dot-product-style score $s$, the mixture $h = \sum \alpha \cdot b$ *is* that layer's input. Note that AttnRes does not add a term on top of a residual; it replaces layer-by-layer accumulation itself. Weight can concentrate on one summary, but the choice is never hard.

Cost: full AttnRes stores every layer output — $L$ vectors of width $d$ per token, i.e. $O(Ld)$. The block version stores $N = \lceil L/12 \rceil$ summaries plus the embedding, i.e. $O(Nd)$. With $L = 93$ and block size 12, K3 keeps $N = 8$ summaries, i.e. $9 \times 7168$ numbers per token. These summaries also travel with activations through the pipeline, so $N$ enters communication volume directly. Note that blocking shrinks the candidate set (93 → 9), not the number of retrievals: all 93 layers still retrieve once each. The kernel just batches the cross-block reads per block and lets each layer merge in its own intra-block partial sum with an online softmax.

Granularity vs. cost: smaller blocks (one layer per block in the limit) give finer depth-wise retrieval but grow state, memory bandwidth, and pipeline traffic linearly in $N$; larger blocks are cheaper, but layers inside a block are already summed and cannot be retrieved separately. The AttnRes paper reports the cost as: end-to-end inference latency overhead below 2% on typical inference workloads; on the training side, negligible without pipeline parallelism and a measured end-to-end overhead below 4% with it.

### LatentMoE

Every FFN except the first uses MoE: each token selects 16 of 896 routed experts, while 2 shared experts are always active. The routed-pool selection rate is therefore $16/896 \approx 1.8\%$; the separate whole-model ratio is $104\text{B}/2.8\text{T} \approx 3.7\%$ active parameters per token.

Routing still scores the full 7168-d hidden state, but the selected experts compute in a 3584-d latent space and project back to full width. This halves both the 16-way all-to-all dispatch traffic and expert weight volume:

LatentMoE diagram

**16** / 896 1.8%

At this point we have seen how KDA, MLA, Attention Residual, and LatentMoE form K3's hybrid architecture. But the model design only answers how to compute. In production, SGLang still has to answer how these different states fit in memory and how prefill is parallelized. The next half starts from those system questions.

## SGLang's day-0 adaptations

K3's hybrid architecture creates two inference states with completely different lifecycles:

|  | MLA (24 layers) | KDA (69 layers) |
| --- | --- | --- |
| State shape | KV cache, appends per token | Recurrent state, fixed size |
| Growth | ~27KB per token per GPU, append-only | ~54MB per request per GPU (`TP=8`), overwritten in place each step |

MLA appends KV per token, while KDA reserves a fixed amount per request and overwrites it every step. That difference propagates into memory allocation, prefill parallelism, and decode scaling—the three parts of SGLang's day-0 work.

### RadixAttention: prefix caching for KDA state

Traditional RadixAttention can share a prefix across requests because attention KV only appends as tokens arrive and never rewrites history. KDA's recurrent state $S$ is different: every token it reads overwrites the state in place. Suppose D and E both hit the prefix ABC. If they shared one $S(\text{ABC})$, D's next step would turn it into $S(\text{ABCD})$, so E could no longer start from the state after ABC — the mechanism rules prefix caching out. So how do we keep RadixAttention's cache tree?

SGLang's answer is to never let a request mutate the shared state in the radix tree. A KDA state stored in the tree is a read-only checkpoint: after a prefix hit, copy-on-write restores it into the request's private working slot, and the forward pass mutates only that copy. Copying and forking are what keep an overwrite from destroying the prefix. Below, the first view compares how the KDA and MLA radix cache grow under two workload changes; the second steps through copy-on-write, snapshot, donate, and checkpoint eviction:

**Which workload dimension makes each state grow?**The four plots compare growth direction only; they do not share a y-axis.

**Workload change** **KDA state** **MLA KV cache**

**One request gets longer**

~54MB / active request (TP=8), independent of token count

~27KB / token, linear in context length

**Same cached-token total, more active branches**

Every active branch needs its own mutable working state

Depends on total cached tokens; branch topology itself adds no KV

One prefix reuse follows 1 → 2 → 3 → 4. As generation continues, 3 → 4 repeats at later checkpoint boundaries.

Every branch shown hits ABC. S(ABC) in the tree is a read-only checkpoint, not a live request's working state.

<svg viewBox="61 0 603 360" role="img" aria-label="S(ABC) in the tree is read-only; every active request starts from this shared checkpoint." style="width: 100%; max-width: 603px;"><path stroke="currentColor" fill="none" d="M400 30V55"></path><path stroke="currentColor" fill="none" d="M400 95V100"></path><path stroke="currentColor" fill="none" d="M388 136C340 155 245 160 190 174"></path><path stroke="currentColor" fill="none" d="M180 210V230"></path><path stroke="currentColor" fill="none" d="M168 265L115 305"></path><path stroke="currentColor" fill="none" d="M192 265L245 305"></path><path stroke="currentColor" fill="none" d="M400 140V170"></path><path stroke="currentColor" fill="none" d="M400 210V230"></path><path stroke="currentColor" fill="none" d="M388 265L340 305"></path><path stroke="currentColor" fill="none" d="M412 265L460 305"></path><path stroke="currentColor" fill="none" d="M412 136C460 155 555 160 610 174"></path><path stroke="currentColor" fill="none" d="M620 210V230"></path><g transform="translate(400 30)"><circle r="20"></circle><text y="5" text-anchor="middle">A</text></g> <g transform="translate(400 75)"><circle r="20"></circle><text y="5" text-anchor="middle">B</text></g> <g transform="translate(400 120)"><circle r="20"></circle><text y="5" text-anchor="middle">C</text></g> <g transform="translate(180 190)"><circle r="20"></circle><text y="5" text-anchor="middle">D</text></g> <g transform="translate(180 250)"><circle r="20"></circle><text y="5" text-anchor="middle">E</text></g> <g transform="translate(105 320)"><circle r="20"></circle><text y="5" text-anchor="middle">F</text></g> <g transform="translate(255 320)"><circle r="20"></circle><text y="5" text-anchor="middle">X</text></g> <g transform="translate(400 190)"><circle r="20"></circle><text y="5" text-anchor="middle">G</text></g> <g transform="translate(400 250)"><circle r="20"></circle><text y="5" text-anchor="middle">H</text></g> <g transform="translate(330 320)"><circle r="20"></circle><text y="5" text-anchor="middle">I</text></g> <g transform="translate(470 320)"><circle r="20"></circle><text y="5" text-anchor="middle">Q</text></g> <g transform="translate(620 190)"><circle r="20"></circle><text y="5" text-anchor="middle">J</text></g> <g transform="translate(620 250)"><circle r="20"></circle><text y="5" text-anchor="middle">K</text></g></svg>

S(ABC) in the tree is read-only; every active request starts from this shared checkpoint.

### Memory management for two state types

Because K3 mixes KDA and MLA layers, memory management has to carve out two kinds of region as well. The old approach preallocates a KDA region and an MLA region at startup. KDA demand follows concurrency while MLA demand follows total context length, so once the workload differs from the estimate, one region fills while the other sits idle. The fix is direct: SGLang puts both in one pool, with fixed KDA blocks allocated from the left, MLA pages from the right, and the free space in the middle shared. When a request finishes, aborts or is retracted and leaves a hole in the middle, a block from the end is moved into it, so the free region stays contiguous and both ends stay packed — which is what lets a 54MB KDA block and a 27KB MLA page draw from the same bytes with no common page size forced on them. Day-0 makes this opt-in with `--enable-unified-memory`:

Memory pool comparisonBoth states allocate on admission; KDA then stays fixed while MLA grows with tokens

t = 0/32

**Static split pools (fixed at startup)**

active requests 0

**KDA 0** \= 0 requests × 3 pages **MLA 0** accumulates page by page with tokens **free 44 pages** unused capacity **failures 0**

**Unified pool (SGLang)**

active requests 0

**KDA 0** \= 0 requests × 3 pages **MLA 0** accumulates page by page with tokens **free 44 pages** unused capacity **failures 0**

In the baseline, allocations pick free slots inside two statically sized regions. When the MLA region fills, free KDA slots cannot be borrowed. The unified layout instead packs KDA from the left and MLA from the right, so every request keeps running.

### Chunked pipeline prefill

Prefill processes many prompt tokens at once, which gives it enough work to cut into chunks and fill a pipeline. TP8 puts all eight GPUs on the same prefill work, but the problem is that every layer needs a lockstep AllReduce before the full result can enter the next layer. Chunked PP8 works differently: PP8 assigns ranges of the 93 layers to G1–G8 and lets different GPUs process different chunks. GPUs pass only the activation from the preceding stage, and those P2P transfers overlap with computation on the next chunk. As the diagram shows, G1–G8 each run a run of complete layers rather than splitting one layer eight ways, so no AllReduce is needed between layers. The cost is that filling and draining the pipeline takes some steps, so it cannot run full from the start; over a long-context prefill that overhead is diluted, so throughput still comes out ahead.

Chunked pipeline prefill diagramThe same 8 GPUs; TP8 above, chunked PP8 below

Problem **TP8: all 8 GPUs sync after every layer**

Every layer is split eight ways. After compute, every rank must finish an AllReduce before any rank can enter the next layer.

**G1** *compute* *AllReduce* *compute* *AllReduce* *compute* *AllReduce*

**G2** *compute* *AllReduce* *compute* *AllReduce* *compute* *AllReduce*

**G3** *compute* *AllReduce* *compute* *AllReduce* *compute* *AllReduce*

**G4** *compute* *AllReduce* *compute* *AllReduce* *compute* *AllReduce*

**G5** *compute* *AllReduce* *compute* *AllReduce* *compute* *AllReduce*

**G6** *compute* *AllReduce* *compute* *AllReduce* *compute* *AllReduce*

**G7** *compute* *AllReduce* *compute* *AllReduce* *compute* *AllReduce*

**G8** *compute* *AllReduce* *compute* *AllReduce* *compute* *AllReduce*

✓ A barrier after each of 93 layers✓ Communication stays on the critical path✓ Eight-way slicing makes GEMMs narrower

Solution **Chunked PP8: 8 layer stages, prompt in chunks**

G1–G8 each execute a run of complete layers. The long prompt becomes multiple chunks; after one chunk, a GPU sends its activation directly to the next GPU.

****G1** L1–12** *C1* *C2* *C3* *C4* *C5*

****G2** L13–24** *C1* *C2* *C3* *C4* *C5*

****G3** L25–36** *C1* *C2* *C3* *C4* *C5*

****G4** L37–48** *C1* *C2* *C3* *C4* *C5*

****G5** L49–60** *C1* *C2* *C3* *C4* *C5*

****G6** L61–72** *C1* *C2* *C3* *C4* *C5*

****G7** L73–84** *C1* *C2* *C3* *C4* *C5*

****G8** L85–93** *C1* *C2* *C3* *C4* *C5*

**Measured 8K prefill (2×4 GB300; topology is the only variable)**

Prefill capacity per node

*TEP8*

1.00×

*PP8×TP1*

1.45–1.72× (representative point: 1.64×)

Exposed critical-path communication / 1K tokens

*TP8 · 9.38 ms*

*PP8 · 0.88 ms*

about 91% lower

Decode is another story. It usually has only one new token per step, not enough work to fill a pipeline as deep as PP8, so TP8 remains the better fit. A common PD-disaggregated split is `PP8 prefill → TP8 / DCP8 decode`. As noted above, PP also pays fill and drain overhead, so it does not win when requests or chunks are too few.

### Decode context parallelism (DCP)

MLA has multiple attention heads, but they all share one compressed KV latent, so unlike MHA there is no clear axis to shard when TP splits by head. Every TP8 rank therefore has to replicate the complete MLA KV latent. That means the same MLA KV latent sits on every GPU, and adding GPUs does not increase logical context capacity. SGLang uses DCP to shard by token position instead: each GPU computes partial attention over its local $1/N$ KV, split as the diagram shows, then one packed all-to-all merges the result exactly:

DCP diagramThe same 12-token MLA context; naive TP above, DCP below

Parallel GPUs N

Each GPU scans about 1/4 of KV

Problem **Naive TP: every GPU stores the full KV**

MLA has multiple attention heads, but they all share the same compressed KV latent, leaving no cache head axis for TP to shard. TP4 therefore replicates this KV latent on all 4 GPUs: more GPUs do not increase logical context capacity.

**T1** **T2** **T3** **T4** **T5** **T6** **T7** **T8** **T9** **T10** **T11** **T12**

**GPU 1**

**GPU 2**

**GPU 3**

**GPU 4**

The same 12-token context **Physical KV cells: 48 (4× replicated)**

Solution **DCP: KV striped across GPUs by token position**

The small query is replicated to all GPUs; the long, memory-heavy KV is striped round-robin by token position, with each position stored once.

**T1** **T2** **T3** **T4** **T5** **T6** **T7** **T8** **T9** **T10** **T11** **T12**

**GPU 1**

**GPU 2**

**GPU 3**

**GPU 4**

Physical KV cells: 12 (one copy per position) **With the same 48-cell memory: 12 → 48 logical tokens**

**Why one MLA decode step remains exact**

<svg viewBox="0 0 128 80" aria-hidden="true"><g transform="translate(0 3)"><rect x="6" y="0" width="116" height="15" rx="3" fill="Canvas" stroke="#ccc"></rect><text x="12" y="11" font-size="10" fill="#888">G1</text> <rect x="104" y="2" width="11" height="11" rx="2" fill="currentColor"></rect><text x="109.5" y="11" font-size="10" fill="currentColor" text-anchor="middle">q</text></g> <g transform="translate(0 22)"><rect x="6" y="0" width="116" height="15" rx="3" fill="Canvas" stroke="#ccc"></rect><text x="12" y="11" font-size="10" fill="#888">G2</text> <rect x="104" y="2" width="11" height="11" rx="2" fill="currentColor"></rect><text x="109.5" y="11" font-size="10" fill="currentColor" text-anchor="middle">q</text></g> <g transform="translate(0 41)"><rect x="6" y="0" width="116" height="15" rx="3" fill="Canvas" stroke="#ccc"></rect><text x="12" y="11" font-size="10" fill="#888">G3</text> <rect x="104" y="2" width="11" height="11" rx="2" fill="currentColor"></rect><text x="109.5" y="11" font-size="10" fill="currentColor" text-anchor="middle">q</text></g> <g transform="translate(0 60)"><rect x="6" y="0" width="116" height="15" rx="3" fill="Canvas" stroke="#ccc"></rect><text x="12" y="11" font-size="10" fill="#888">G4</text> <rect x="104" y="2" width="11" height="11" rx="2" fill="currentColor"></rect><text x="109.5" y="11" font-size="10" fill="currentColor" text-anchor="middle">q</text></g></svg> **① Project the full q locally** q is small; no broadcast *→* <svg viewBox="0 0 128 80" aria-hidden="true"><g transform="translate(0 3)"><rect x="6" y="2" width="11" height="11" rx="2" fill="currentColor"></rect><text x="11.5" y="11" font-size="10" fill="currentColor" text-anchor="middle">q</text> <g><path d="M17 6 Q 23.5 -4 38 1" fill="none" stroke="currentColor" stroke-width="1" opacity="0.55"></path><rect x="30" y="1" width="17" height="13" rx="2" fill="currentColor" stroke="none" opacity="0.85"></rect></g><g><rect x="54" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><rect x="78" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><rect x="102" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g></g><g transform="translate(0 22)"><rect x="6" y="2" width="11" height="11" rx="2" fill="currentColor"></rect><text x="11.5" y="11" font-size="10" fill="currentColor" text-anchor="middle">q</text> <g><rect x="30" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><path d="M17 6 Q 35.5 -4 62 1" fill="none" stroke="currentColor" stroke-width="1" opacity="0.55"></path><rect x="54" y="1" width="17" height="13" rx="2" fill="currentColor" stroke="none" opacity="0.85"></rect></g><g><rect x="78" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><rect x="102" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g></g><g transform="translate(0 41)"><rect x="6" y="2" width="11" height="11" rx="2" fill="currentColor"></rect><text x="11.5" y="11" font-size="10" fill="currentColor" text-anchor="middle">q</text> <g><rect x="30" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><rect x="54" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><path d="M17 6 Q 47.5 -4 86 1" fill="none" stroke="currentColor" stroke-width="1" opacity="0.55"></path><rect x="78" y="1" width="17" height="13" rx="2" fill="currentColor" stroke="none" opacity="0.85"></rect></g><g><rect x="102" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g></g><g transform="translate(0 60)"><rect x="6" y="2" width="11" height="11" rx="2" fill="currentColor"></rect><text x="11.5" y="11" font-size="10" fill="currentColor" text-anchor="middle">q</text> <g><rect x="30" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><rect x="54" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><rect x="78" y="1" width="17" height="13" rx="2" fill="none" stroke="currentColor" opacity="1"></rect></g><g><path d="M17 6 Q 59.5 -4 110 1" fill="none" stroke="currentColor" stroke-width="1" opacity="0.55"></path><rect x="102" y="1" width="17" height="13" rx="2" fill="currentColor" stroke="none" opacity="0.85"></rect></g></g></svg> **② Local attention per GPU** scan only 1/N of KV *→* <svg viewBox="0 0 128 80" aria-hidden="true"><g><text x="2" y="13" font-size="10" fill="currentColor">o₁</text> <rect x="13" y="4" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="25" y="4" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="37" y="4" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="49" y="4" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="84" y="3" width="40" height="15" rx="3" fill="Canvas" stroke="#ccc"></rect><text x="87" y="14" font-size="10" fill="#888">G1</text> <rect x="98" y="5" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.95"></rect><rect x="104.5" y="5" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.73"></rect><rect x="111" y="5" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.51"></rect><rect x="117.5" y="5" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.2899999999999999"></rect></g><g><text x="2" y="32" font-size="10" fill="currentColor">o₂</text> <rect x="13" y="23" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="25" y="23" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="37" y="23" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="49" y="23" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="84" y="22" width="40" height="15" rx="3" fill="Canvas" stroke="#ccc"></rect><text x="87" y="33" font-size="10" fill="#888">G2</text> <rect x="98" y="24" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.95"></rect><rect x="104.5" y="24" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.73"></rect><rect x="111" y="24" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.51"></rect><rect x="117.5" y="24" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.2899999999999999"></rect></g><g><text x="2" y="51" font-size="10" fill="currentColor">o₃</text> <rect x="13" y="42" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="25" y="42" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="37" y="42" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="49" y="42" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="84" y="41" width="40" height="15" rx="3" fill="Canvas" stroke="#ccc"></rect><text x="87" y="52" font-size="10" fill="#888">G3</text> <rect x="98" y="43" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.95"></rect><rect x="104.5" y="43" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.73"></rect><rect x="111" y="43" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.51"></rect><rect x="117.5" y="43" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.2899999999999999"></rect></g><g><text x="2" y="70" font-size="10" fill="currentColor">o₄</text> <rect x="13" y="61" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="25" y="61" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="37" y="61" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="49" y="61" width="11" height="13" rx="1.5" fill="currentColor" opacity="0.85"></rect><rect x="84" y="60" width="40" height="15" rx="3" fill="Canvas" stroke="#ccc"></rect><text x="87" y="71" font-size="10" fill="#888">G4</text> <rect x="98" y="62" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.95"></rect><rect x="104.5" y="62" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.73"></rect><rect x="111" y="62" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.51"></rect><rect x="117.5" y="62" width="5.5" height="11" rx="1" fill="currentColor" opacity="0.2899999999999999"></rect></g><path d="M 18.5 17 C 40 33, 70 11, 83 11" fill="none" stroke="currentColor" stroke-width="1" opacity="0.75"></path><path d="M 30.5 17 C 50 33, 70 30, 83 30" fill="none" stroke="currentColor" stroke-width="1" opacity="0.75"></path><path d="M 42.5 17 C 60 33, 70 49, 83 49" fill="none" stroke="currentColor" stroke-width="1" opacity="0.75"></path><path d="M 54.5 17 C 70 33, 70 68, 83 68" fill="none" stroke="currentColor" stroke-width="1" opacity="0.75"></path></svg> **③ One packed all-to-all** each segment is 1/N of o *→* <svg viewBox="0 0 128 80" aria-hidden="true"><defs><marker id="dcp-merge-arrow" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L8 4L0 8Z" fill="currentColor"></path></marker></defs><g><rect x="6" y="3" width="24" height="14" rx="3" fill="currentColor" stroke="#ccc"></rect><text x="18" y="13.5" font-size="10" fill="currentColor" text-anchor="middle">o₁</text> <line x1="32" y1="10" x2="68" y2="33.5" stroke="currentColor" stroke-width="1" opacity="0.8"></line><text x="36" y="8" font-size="10" fill="currentColor">×w₁</text></g> <g><rect x="6" y="22" width="24" height="14" rx="3" fill="currentColor" stroke="#ccc"></rect><text x="18" y="32.5" font-size="10" fill="currentColor" text-anchor="middle">o₂</text> <line x1="32" y1="29" x2="68" y2="36.5" stroke="currentColor" stroke-width="1" opacity="0.8"></line><text x="36" y="27" font-size="10" fill="currentColor">×w₂</text></g> <g><rect x="6" y="41" width="24" height="14" rx="3" fill="currentColor" stroke="#ccc"></rect><text x="18" y="51.5" font-size="10" fill="currentColor" text-anchor="middle">o₃</text> <line x1="32" y1="48" x2="68" y2="39.5" stroke="currentColor" stroke-width="1" opacity="0.8"></line><text x="36" y="46" font-size="10" fill="currentColor">×w₃</text></g> <g><rect x="6" y="60" width="24" height="14" rx="3" fill="currentColor" stroke="#ccc"></rect><text x="18" y="70.5" font-size="10" fill="currentColor" text-anchor="middle">o₄</text> <line x1="32" y1="67" x2="68" y2="42.5" stroke="currentColor" stroke-width="1" opacity="0.8"></line><text x="36" y="65" font-size="10" fill="currentColor">×w₄</text></g> <circle cx="79" cy="38" r="10" fill="currentColor" stroke="currentColor" stroke-width="1"></circle><text x="79" y="41.5" font-size="10" fill="currentColor" text-anchor="middle">Σ</text> <line x1="90" y1="38" x2="99" y2="38" stroke="currentColor" stroke-width="1" marker-end="url(#dcp-merge-arrow)"></line><rect x="101" y="30" width="17" height="16" rx="3" fill="currentColor" opacity="0.85"></rect><text x="109.5" y="41.5" font-size="10" fill="currentColor" font-weight="700" text-anchor="middle">o</text></svg> **④ LSE-weighted merge** matches the full softmax result

filled = stored on this GPUoutline = owned by another GPU

DCP primarily increases capacity and concurrency, not latency for one short request. Keeping more long sessions on the GPU avoids host offload, re-prefill, and throughput collapse. DCP groups are built inside the TP group, so TP8 with DCP8 is still just 8 GPUs: on K3 logical capacity goes from about 1.5M to 12.2M tokens (roughly 7.9×) and reaches 541 tok/s at 48 agent sessions. It costs one all-to-all per MLA layer. The KDA state S, meanwhile, does not grow with context and has no token-position axis, so it stays TP/head-sharded.

### Performance numbers and benchmark results

BS=1 decode, aggregate system throughput, and per-user speed are three distinct metrics. Single-request speed first: 15 kernel and communication optimizations raise non-speculative BS=1 decode from 44.3 to 112.5 tok/s, and DSpark's speculative decoding is a separate line at ~423 tok/s:

BS=1 decode optimization8×GB300 · TP8 · BF16 KV cache · non-speculative

<svg viewBox="0 0 430 184" role="img" aria-label="44.3 → 112.5 tok/s" style="width: 100%; max-width: 430px;"><title>44.3 → 112.5 tok/s</title> <g><line stroke-opacity="0.2" stroke="currentColor" x1="34" x2="402" y1="148" y2="148"></line><text fill="currentColor" x="5" y="152">40</text></g> <g><line stroke-opacity="0.2" stroke="currentColor" x1="34" x2="402" y1="90" y2="90"></line><text fill="currentColor" x="5" y="94">80</text></g> <g><line stroke-opacity="0.2" stroke="currentColor" x1="34" x2="402" y1="32" y2="32"></line><text fill="currentColor" x="5" y="36">120</text></g> <polyline stroke-opacity="0.2" stroke="currentColor" points="34,141.76500000000001 58,128.85999999999999 82,116.245 106,115.52000000000001 130,112.91 154,111.315 178,103.05 202,101.6 226,97.975 250,83.765 274,82.46 298,75.21 322,72.6 346,49.400000000000006 370,44.47 394,42.875"></polyline><polyline stroke-opacity="0.2" stroke="currentColor" points="34,141.76500000000001 58,128.85999999999999 82,116.245 106,115.52000000000001 130,112.91 154,111.315 178,103.05 202,101.6 226,97.975 250,83.765 274,82.46 298,75.21 322,72.6 346,49.400000000000006 370,44.47 394,42.875"></polyline><circle stroke="currentColor" fill="none" cx="34" cy="141.76500000000001" r="4.2"></circle><circle stroke="currentColor" fill="none" cx="58" cy="128.85999999999999" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="82" cy="116.245" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="106" cy="115.52000000000001" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="130" cy="112.91" r="4.2"></circle><circle stroke="currentColor" fill="none" cx="154" cy="111.315" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="178" cy="103.05" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="202" cy="101.6" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="226" cy="97.975" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="250" cy="83.765" r="4.2"></circle><circle stroke="currentColor" fill="none" cx="274" cy="82.46" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="298" cy="75.21" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="322" cy="72.6" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="346" cy="49.400000000000006" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="370" cy="44.47" r="2.3"></circle><circle stroke="currentColor" fill="none" cx="394" cy="42.875" r="5.5"></circle><text fill="currentColor" x="34" y="131.76500000000001" text-anchor="middle">44.3</text> <text fill="currentColor" x="394" y="32.875" text-anchor="end">112.5</text> <text fill="currentColor" x="34" y="174" text-anchor="middle">P0</text> <text fill="currentColor" x="394" y="174" text-anchor="middle">P15</text> <text fill="currentColor" x="215" y="181" text-anchor="middle">44.3 → 112.5 tok/s</text></svg>

**Add DSpark** **112.5 tok/s** *→* **~423 tok/s**

Cluster metrics are a different question: under PD disaggregation, aggregate throughput trades against per-user speed, and each deployment goal maps to a different parallel layout:

Deployment trade-offsGB300 · 8K input / 1K output · PD disaggregation

Deployment goal

#### System efficiency (tok/s/GPU)

**Total throughput** PP8 prefill → TP8 decode · FP4

2,808

**Long context** 2×PP8 prefill → 2×DCP8 decode

2,633

#### Per-user speed (tok/s/user)

**Total throughput** throughput configuration

18.7

**Per user** add independent TP8 decode instances

116+

throughput first **add decode instances →** per-user speed first

**Throughput:** 2,808 tok/s/GPU; 18.7 tok/s/user.

## Acknowledgments

Kimi K3 day-0 support was a collaboration between the SGLang & Miles team at RadixArk and the Moonshot AI team, together with NVIDIA, AMD, Approaching AI, Baseten, and Modal.

- **AMD:** Wun-guo Huang, Xinyi Song, Hai Xiao, Soga Lin, Duyi Wang, Thomas Wang
- **Approaching AI:** Huanming Shen, Xiaohao Zhang, Nan Li, Mingxing Zhang

Thanks to DigitalOcean for providing AMD instances for testing. Thanks also to Google Cloud, DigitalOcean, Nebius, fal, RunPod, DeepInfra, and GMI Cloud for serving Kimi K3 on SGLang.

## Further reading

- [Kimi K3 Technical Report](https://arxiv.org/abs/2607.24653)
- [LMSYS Blog: Kimi K3 Day-0 Support](https://www.lmsys.org/blog/2026-07-27-kimi-k3-day0-support/)
- [Kimi Linear: An Expressive, Efficient Attention Architecture](https://arxiv.org/abs/2510.26692)
- [Attention Residuals Technical Report](https://arxiv.org/abs/2603.15031)

*The visualized tutorial was written by [Yichi Zhang](https://github.com/Ccyest) and the SGLang Team.*
