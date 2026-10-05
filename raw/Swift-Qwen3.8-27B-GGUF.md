---
license: other
license_name: swift-open-license-1.0
license_link: https://huggingface.co/ukisai/Swift-Qwen3.8-27b#license-and-access
base_model: ukisai/Swift-Qwen3.8-27b
base_model_relation: quantized
pipeline_tag: image-text-to-text
library_name: gguf
tags:
- gguf
- llama.cpp
- qwen3_8
- qwen3_5
- efficient-thinking
- reasoning
- token-efficient
---

<div align="center">
  <a href="https://ukisai.com"><img src="ukisai-banner.png" alt="UkisAI" style="width:100%;max-width:100%;height:auto;display:block;margin-bottom:0.6em;" /></a>
  <div style="display:flex;justify-content:center;gap:0.6em;margin-bottom:1em;">
    <a href="https://ukisai.com"><strong>Website</strong></a> &nbsp;&bull;&nbsp;
    <a href="https://ukisai.com/products/swift"><strong>Learn more</strong></a> &nbsp;&bull;&nbsp;
    <a href="https://huggingface.co/ukisai/Swift-Qwen3.8-27b"><strong>BF16 model</strong></a> &nbsp;&bull;&nbsp;
    <a href="#license-and-access"><strong>Enterprise licensing</strong></a>
  </div>
</div>

# Swift-Qwen3.8-27B GGUF

Swift-Qwen3.8-27B is UkisAI's reasoning-efficient derivative of Qwen3.8-27B,
using **58.3% fewer thinking tokens** while maintaining near-identical performance
(**&lt;1% loss**) and as a result getting a **x1.95 speed-up** on several tasks.

<video controls autoplay muted loop playsinline style="width:100%;max-width:100%;height:auto;display:block;border-radius:12px;margin:0.8em 0 1.4em;" src="https://huggingface.co/ukisai/Swift-Qwen3.8-27B-GGUF/resolve/main/swift-speed-demo.mp4"></video>
<p align="center" style="font-size:13px;color:#8C94A8;margin:-0.6em 0 1.4em;">The prompt is a sample from LiveCodeBench v6</p>

<style>
.swift-table { width:100%; table-layout:fixed; border-collapse:separate; border-spacing:0; overflow:hidden; border:1px solid #27344A; border-radius:20px; background:#0D111B; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; font-size:14px; color:#BFBDBD; }
.swift-table th { padding:13px 8px; text-align:center; font-weight:700; color:#AEB5C7; background:#0D111B; border-right:1px solid #27344A; border-bottom:1px solid #27344A; }
.swift-table td { padding:14px 8px; text-align:center; color:#BFBDBD; background:#0D111B; border-right:1px solid #27344A; border-bottom:1px solid #27344A; vertical-align:middle; overflow-wrap:break-word; }
.swift-table tr > :last-child { border-right:0; }
.swift-table tbody tr:last-child td { border-bottom:0; }
.swift-table .benchmark-heading { color:#B7BDCD; background:#0D111B; border-bottom:3px solid #7D45B5; }
.swift-table .score-heading { color:#F0C5FF; background:#52239E; border-bottom:3px solid #7D45B5; }
.swift-table .tokens-heading, .swift-table .median-heading { color:#D4E8FF; background:#304FC2; border-bottom:3px solid #5687E6; }
.swift-table .benchmark { padding-left:18px; text-align:left; color:#FFFFFF; font-weight:600; }
.swift-table strong { color:#FFFFFF; }
.swift-table .section { padding:12px 18px; text-align:left; color:#B489FF; background:#2A2541; font-weight:700; letter-spacing:.08em; text-transform:uppercase; border-top:1px solid #3A3159; border-bottom:1px solid #3A3159; }
.swift-table .swift { background:#171127; }
.swift-table thead tr:nth-child(2) .swift { color:#D3A0FF; }
.swift-table .reduction { color:#69BFFF; background:#101B2C; font-weight:700; }
.swift-table .detail { color:#8C94A8; font-size:12px; font-weight:500; }

@media (max-width: 640px) {
  .swift-table { display:block !important; width:100% !important; max-width:100%; overflow-x:auto !important; -webkit-overflow-scrolling:touch; table-layout:auto !important; }
  .swift-table th, .swift-table td { min-width:100px; }
  .swift-table th:first-child, .swift-table td:first-child { min-width:160px; }
}
</style>

## Evaluation scope

> All results below compare the Qwen3.8-27B BF16 base with the same base plus the
> Swift adapter.

## Benchmarks

<table class="swift-table">
  <thead>
    <tr>
      <th rowspan="2" class="benchmark-heading" style="width:32%;text-align:left;padding-left:18px;vertical-align:bottom;">Benchmark</th>
      <th colspan="2" class="score-heading">Score</th>
      <th colspan="3" class="tokens-heading">Mean tokens</th>
      <th class="median-heading" style="width:14%;">Median tokens</th>
    </tr>
    <tr>
      <th>Base</th>
      <th class="swift">Swift</th>
      <th>Base</th>
      <th class="swift">Swift</th>
      <th class="reduction">Reduction</th>
      <th class="reduction">Reduction</th>
    </tr>
  </thead>
  <tbody>
    <tr><td class="section" colspan="7">General reasoning</td></tr>
    <tr><td class="benchmark">GPQA-Diamond</td><td>88.38%</td><td class="swift">88.28%</td><td>15,014</td><td class="swift"><strong>8,855</strong></td><td class="reduction">&darr; 41.0%</td><td class="reduction">&darr; 58.3%</td></tr>
    <tr><td class="benchmark">MMLU-Pro</td><td>85.47%</td><td class="swift">84.95%</td><td>2,980</td><td class="swift"><strong>1,603</strong></td><td class="reduction">&darr; 46.2%</td><td class="reduction">&darr; 28.3%</td></tr>
    <tr><td class="benchmark">C-Eval</td><td>90.00%</td><td class="swift">90.62%</td><td>1,492</td><td class="swift"><strong>804</strong></td><td class="reduction">&darr; 46.1%</td><td class="reduction">&darr; 19.3%</td></tr>
    <tr><td class="benchmark">IFBench</td><td>73.53%</td><td class="swift">71.80%</td><td>8,052</td><td class="swift"><strong>4,657</strong></td><td class="reduction">&darr; 42.2%</td><td class="reduction">&darr; 50.5%</td></tr>
    <tr><td class="section" colspan="7">Mathematics</td></tr>
    <tr><td class="benchmark">AIME 2026</td><td>98.67%</td><td class="swift">94.00%</td><td>22,014</td><td class="swift"><strong>16,143</strong></td><td class="reduction">&darr; 26.7%</td><td class="reduction">&darr; 50.2%</td></tr>
    <tr><td class="benchmark">HMMT (Nov 2025)</td><td>99.33%</td><td class="swift">96.00%</td><td>22,032</td><td class="swift"><strong>15,189</strong></td><td class="reduction">&darr; 31.1%</td><td class="reduction">&darr; 45.9%</td></tr>
    <tr><td class="section" colspan="7">Multimodal</td></tr>
    <tr><td class="benchmark">ERQA</td><td>67.45%</td><td class="swift">66.30%</td><td>4,137</td><td class="swift"><strong>2,045</strong></td><td class="reduction">&darr; 50.6%</td><td class="reduction">&darr; 54.6%</td></tr>
    <tr><td class="section" colspan="7">Agentic coding</td></tr>
    <tr><td class="benchmark">Terminal-Bench 2.1</td><td>66.74%</td><td class="swift">65.84%</td><td>37,086</td><td class="swift"><strong>27,272</strong></td><td class="reduction">&darr; 26.5%</td><td class="reduction">&darr; 38.7%</td></tr>
    <tr><td class="benchmark">LiveCodeBench v6</td><td>76.76%</td><td class="swift">81.55%</td><td>11,374</td><td class="swift"><strong>8,615</strong></td><td class="reduction">&darr; 24.3%</td><td class="reduction">&darr; 45.8%</td></tr>
  </tbody>
</table>

<details>
<summary><strong>How to reproduce</strong></summary>

<p style="font-size:13px;line-height:1.5;margin:8px 0;"><strong>Serving:</strong> BF16 · vLLM 0.27.1 · Qwen3 parser · context 262,144 · thinking xhigh.<br>
<strong>Sampling:</strong> temperature 1.0 · top_p 0.95 · top_k 20 · min_p 0 · presence_penalty 0 · repetition_penalty 1.<br>
<strong>Benchmarks:</strong> averages over five seeds (0–4) per model; five trials per task for Terminal-Bench.</p>

<table style="display:table;width:100%;border-collapse:collapse;font-size:13px;line-height:1.3;margin:8px 0;">
  <thead><tr><th style="padding:4px 8px;text-align:left;">Benchmark</th><th style="padding:4px 8px;text-align:right;">Output cap</th></tr></thead>
  <tbody>
    <tr><td style="padding:3px 8px;">GPQA-Diamond</td><td style="padding:3px 8px;text-align:right;">100,000</td></tr>
    <tr><td style="padding:3px 8px;">MMLU-Pro</td><td style="padding:3px 8px;text-align:right;">100,000</td></tr>
    <tr><td style="padding:3px 8px;">C-Eval</td><td style="padding:3px 8px;text-align:right;">16,384</td></tr>
    <tr><td style="padding:3px 8px;">IFBench</td><td style="padding:3px 8px;text-align:right;">81,920</td></tr>
    <tr><td style="padding:3px 8px;">AIME 2026</td><td style="padding:3px 8px;text-align:right;">250,000</td></tr>
    <tr><td style="padding:3px 8px;">HMMT Nov 2025</td><td style="padding:3px 8px;text-align:right;">250,000</td></tr>
    <tr><td style="padding:3px 8px;">ERQA</td><td style="padding:3px 8px;text-align:right;">100,000</td></tr>
    <tr><td style="padding:3px 8px;">Terminal-Bench 2.1</td><td style="padding:3px 8px;text-align:right;">Agent/task limits</td></tr>
    <tr><td style="padding:3px 8px;">LiveCodeBench v6</td><td style="padding:3px 8px;text-align:right;">32,768</td></tr>
  </tbody>
</table>

</details>

## Quantized evaluations

Quantized deployment is the intended use for Swift: lower-memory weights paired with
shorter reasoning. The INT4 evaluations below come from the
[source model card](https://huggingface.co/ukisai/Swift-Qwen3.8-27b) and were run on
W4A16 and AWQ checkpoints, not on this F16 GGUF. They retain token savings across GPQA,
IFBench, and AIME. On AIME, Swift matches or improves accuracy and reduces output-cap
failures by **31–33%**.

<table class="swift-table" style="display:table;width:100%;table-layout:fixed;">
  <thead><tr>
    <th class="benchmark-heading" style="width:32%;text-align:left;padding-left:18px;white-space:normal;">Benchmark / quantization</th>
    <th class="score-heading" style="width:16%;white-space:normal;">Base accuracy</th>
    <th class="score-heading" style="width:16%;white-space:normal;">Swift accuracy</th>
    <th class="tokens-heading" style="width:18%;white-space:normal;">Mean token reduction</th>
    <th class="median-heading" style="width:18%;white-space:normal;">Median token reduction</th>
  </tr></thead>
  <tbody>
    <tr><td class="benchmark">GPQA-Diamond<br><span class="detail">Mixed-precision quant W4A16 · thinking tokens</span></td><td>88.69%</td><td class="swift">88.38%</td><td class="reduction">&darr; 32.1%</td><td class="reduction">&darr; 50.2%</td></tr>
    <tr><td class="benchmark">IFBench<br><span class="detail">Mixed-precision quant W4A16 · completion tokens</span></td><td>72.58%</td><td class="swift">71.25%</td><td class="reduction">&darr; 30.1%</td><td class="reduction">&darr; 38.0%</td></tr>
    <tr><td class="benchmark">AIME 2026<br><span class="detail">Mixed-precision quant W4A16 · completion tokens</span></td><td>84.00%</td><td class="swift">84.00%</td><td class="reduction">&darr; 19.0%</td><td class="reduction">&darr; 37.5%</td></tr>
    <tr><td class="benchmark">AIME 2026<br><span class="detail">AWQ INT4 · completion tokens</span></td><td>82.67%</td><td class="swift">84.00%</td><td class="reduction">&darr; 22.8%</td><td class="reduction">&darr; 34.8%</td></tr>
  </tbody>
</table>

<details>
<summary><strong>Quantized evaluation settings</strong></summary>

Each row compares the same quantized base with and without the Swift adapter.
GPQA and AIME use five seeds; IFBench uses four samples per prompt and strict scoring.
Output caps: GPQA 100,000; IFBench 81,920; AIME 32,768. GPQA and IFBench use saved
historical base runs. AIME uses template-default effort and counts truncated answers
as incorrect. Its shorter cap makes it a separate comparison from the BF16 table.

</details>

## GGUF quantizations

<table class="swift-table" style="display:table;width:100%;table-layout:fixed;">
  <thead><tr>
    <th class="benchmark-heading" style="width:20%;text-align:left;padding-left:18px;white-space:normal;">File</th>
    <th class="score-heading" style="width:12%;white-space:normal;">Size</th>
    <th class="score-heading" style="width:17%;white-space:normal;">KLD wikitext @512</th>
    <th class="tokens-heading" style="width:17%;white-space:normal;">KLD wikitext @32k</th>
    <th class="tokens-heading" style="width:17%;white-space:normal;">KLD held-out @32k</th>
    <th class="median-heading" style="width:17%;white-space:normal;">Top-p @32k</th>
  </tr></thead>
  <tbody>
    <tr><td class="benchmark">Q8_0</td><td>29.1 GB</td><td class="swift">0.0009</td><td class="reduction">0.0035</td><td class="reduction">0.0579</td><td>97.92%</td></tr>
    <tr><td class="benchmark">Q6_K_L<br><span class="detail">new tier</span></td><td>25.2 GB</td><td>0.0015</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>98.24%</td></tr>
    <tr><td class="benchmark">Q6_K_S<br><span class="detail">new tier</span></td><td>23.1 GB</td><td>0.0018</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>98.09%</td></tr>
    <tr><td class="benchmark">Q6_K</td><td>22.9 GB</td><td>0.0020</td><td class="reduction">0.0069</td><td class="reduction">0.0782</td><td>96.85%</td></tr>
    <tr><td class="benchmark">Q5_K_M</td><td>20.2 GB</td><td>0.0056</td><td class="reduction">0.0135</td><td class="reduction">0.1251</td><td>95.60%</td></tr>
    <tr><td class="benchmark">Q5_K_S<br><span class="detail">new tier</span></td><td>19.8 GB</td><td>0.0057</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>96.70%</td></tr>
    <tr><td class="benchmark">Q4_K_L<br><span class="detail">new tier</span></td><td>19.0 GB</td><td>0.0102</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>95.77%</td></tr>
    <tr><td class="benchmark">Q4_K_M</td><td>18.0 GB</td><td>0.0120</td><td class="reduction">0.0211</td><td class="reduction">0.1496</td><td>94.30%</td></tr>
    <tr><td class="benchmark">IQ4_NL<br><span class="detail">new tier</span></td><td>17.6 GB</td><td>0.0141</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>95.11%</td></tr>
    <tr><td class="benchmark">Q4_1<br><span class="detail">new tier</span></td><td>17.5 GB</td><td>0.0194</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>94.09%</td></tr>
    <tr><td class="benchmark">Q4_K_S<br><span class="detail">new tier</span></td><td>16.6 GB</td><td>0.0150</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>94.95%</td></tr>
    <tr><td class="benchmark">Q4_0<br><span class="detail">new tier</span></td><td>16.0 GB</td><td>0.0278</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>92.59%</td></tr>
    <tr><td class="benchmark">IQ4_XS<br><span class="detail">new tier</span></td><td>15.7 GB</td><td>0.0165</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>94.66%</td></tr>
    <tr><td class="benchmark">IQ3_M<br><span class="detail">new tier</span></td><td>15.1 GB</td><td>0.0390</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>91.76%</td></tr>
    <tr><td class="benchmark">Q3_K_L<br><span class="detail">new tier</span></td><td>14.3 GB</td><td>0.0412</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>91.26%</td></tr>
    <tr><td class="benchmark">Q3_K_M<br><span class="detail">new tier</span></td><td>13.6 GB</td><td>0.0552</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>89.91%</td></tr>
    <tr><td class="benchmark">IQ3_XS<br><span class="detail">new tier</span></td><td>13.0 GB</td><td>0.0555</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>89.91%</td></tr>
    <tr><td class="benchmark">Q3_K_S<br><span class="detail">new tier</span></td><td>12.9 GB</td><td>0.0631</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>89.30%</td></tr>
    <tr><td class="benchmark">IQ3_XXS<br><span class="detail">new tier</span></td><td>12.5 GB</td><td>0.0724</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>88.81%</td></tr>
    <tr><td class="benchmark">Q2_K<br><span class="detail">new tier</span></td><td>11.0 GB</td><td>0.1617</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>84.05%</td></tr>
    <tr><td class="benchmark">IQ2_M<br><span class="detail">new tier</span></td><td>10.7 GB</td><td>0.1469</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>84.47%</td></tr>
    <tr><td class="benchmark">IQ2_S<br><span class="detail">new tier</span></td><td>9.9 GB</td><td>0.2060</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>81.29%</td></tr>
    <tr><td class="benchmark">IQ2_XS<br><span class="detail">new tier</span></td><td>9.3 GB</td><td>0.2354</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>80.04%</td></tr>
    <tr><td class="benchmark">IQ2_XXS<br><span class="detail">new tier</span></td><td>9.1 GB</td><td>0.2852</td><td class="reduction">&mdash;</td><td class="reduction">&mdash;</td><td>78.09%</td></tr>
  </tbody>
</table>

Mean KL divergence against the BF16 source, lower is better. Tiers marked *new tier* were added on 2026-09-13 and carry the wikitext @512 measurement and 512-token top-token agreement; their 32k columns will be filled as those runs complete. `wikitext` is wikitext-2 test; `held-out`
is our own chat and long-document set, reserved before the importance matrix was fitted. `Top-p` is
top-token agreement with BF16 at 32k on the held-out set.

**Read the two 32k columns together.** On this hybrid architecture (48 of 64 blocks are recurrent), a
small fraction of positions (about 0.1%) diverge sharply at long context for every tier, including `Q8_0`,
and the same is true of the public `Q4_K_M` and `Q8_0` builds of the base Qwen3.8-27B measured on the same
harness. Those rare positions dominate the held-out mean; the median divergence at 32k is within 10% of the
512-token value for every tier. Typical-token quality does not degrade with context. The pick below follows
the 99th-percentile tail on the held-out set: 2.60 for `Q4_K_M`, 1.75 for `Q5_K_M`, 0.46 for `Q6_K`,
0.23 for `Q8_0`.

<table class="swift-table" style="display:table;width:100%;table-layout:fixed;">
  <thead><tr>
    <th class="benchmark-heading" style="width:55%;text-align:left;padding-left:18px;white-space:normal;">Use case</th>
    <th class="score-heading" style="width:45%;white-space:normal;">Pick</th>
  </tr></thead>
  <tbody>
    <tr><td class="benchmark">24 GB cards, everyday use</td><td class="swift">Q4_K_M</td></tr>
    <tr><td class="benchmark">Long agentic runs, strict tool-call formatting</td><td class="swift">Q6_K or higher</td></tr>
    <tr><td class="benchmark">Maximum fidelity</td><td class="swift">Q8_0</td></tr>
  </tbody>
</table>

<details>
<summary><strong>Recipe</strong></summary>

All tiers use the same importance matrix (8,016 chunks of domain, prompt and long-document text) and pin
the recurrent gate projections `ssm_alpha` and `ssm_beta` to F32 and the MTP head to Q8_0. `Q4_K_M`
additionally lifts `ssm_out`, `attn_gate`, `output` and `token_embd` to Q6_K; `Q5_K_M` and `Q6_K` lift
`attn_gate` to Q8_0. The lifts cost about 1.1 GB on `Q4_K_M` and reduce its KL divergence by roughly 20%
against a plain llama.cpp `Q4_K_M` of the same model.

The tiers added on 2026-09-13 (`IQ2_XXS` through `Q6_K_L`) use the same importance matrix and the same
`ssm_alpha`/`ssm_beta` F32 and MTP Q8_0 pins, with per-tensor type layouts computed for this model by
[bartowski's quantization-config](https://github.com/bartowski1182/quantization-config) instead of
llama.cpp's built-in heuristic (`--tensor-type-file`). `Q4_K_L`, `Q6_K_S` and `Q6_K_L` are the large and
small layouts of `Q4_K_M` and `Q6_K`. All files were built with llama.cpp release b10896 from a BF16
conversion of the published safetensors and checked against BF16 on the harness above.

</details>

### KV cache

Only 16 of the 64 blocks are full attention, so the cache stays small for a 27B:

```
16 layers x 4 kv-heads x 256 head_dim x 2 (K+V) x 2 bytes = 64 KiB per token
```

<table class="swift-table" style="display:table;width:100%;table-layout:fixed;">
  <thead><tr>
    <th class="benchmark-heading" style="width:55%;text-align:left;padding-left:18px;white-space:normal;">Context</th>
    <th class="tokens-heading" style="width:45%;white-space:normal;">KV cache</th>
  </tr></thead>
  <tbody>
    <tr><td class="benchmark">8k</td><td>0.5 GB</td></tr>
    <tr><td class="benchmark">32k</td><td>2.0 GB</td></tr>
    <tr><td class="benchmark">64k</td><td class="reduction">4.0 GB</td></tr>
    <tr><td class="benchmark">128k</td><td class="reduction">8.0 GB</td></tr>
  </tbody>
</table>

## Training approach

We built Swift by identifying reasoning-marker tokens that, in our analysis, trigger overthinking in Qwen’s
reasoning rollouts. We then fine-tuned Qwen by penalizing usage of those tokens while it reasons.

Swift produces shorter reasoning traces. In our testing, we also observe fewer overthinking errors.

For maximum gains, Swift also includes a transfer component derived from
[BottleCap AI's ThinkingCap-Qwen3.6-27B](https://huggingface.co/bottlecapai/ThinkingCap-Qwen3.6-27B).

## How to use

### llama.cpp

These files run with [llama.cpp](https://github.com/ggml-org/llama.cpp), installable in one line via [llama.app](https://llama.app/).
The command below is the llama.cpp counterpart of the vLLM configuration on the source card: full
262,144 context, thinking on at reasoning effort `xhigh`, reasoning and tool calls parsed from the
embedded chat template, and Qwen3.8's thinking-mode sampling.

```
curl -LsSf https://llama.app/install.sh | sh

llama-server -hf ukisai/Swift-Qwen3.8-27B-GGUF:Q4_K_M \
  --jinja -fa on -ngl 99 \
  -c 262144 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0 \
  --presence-penalty 0 --repeat-penalty 1.0 \
  --port 8000
```

llama-server exposes an OpenAI-compatible API and a built-in chat web UI on the port above.
Swap `Q4_K_M` for any tier in the table above (`IQ2_XXS` up to `Q8_0`) or `F16`; `-hf` fetches the tier and
the vision projector automatically. The KV cache costs 64 KiB per token (16 GB at the full
262,144 context), so lower `-c` if it does not fit. Use a recent llama.cpp release with
Qwen3.5/Qwen3.8 architecture support. The same sampling values are stored in the GGUF header
and `xhigh` is the template default; the flags above make the configuration explicit.

They also work in [LM Studio](https://lmstudio.ai/), [koboldcpp](https://github.com/LostRuins/koboldcpp)
and [Jan AI](https://www.jan.ai/). In those apps set the same sampling values by hand and a
context length of at least 65,536 tokens; the default 4,096-token window overflows on long
reasoning and looks like an endless loop.

#### Multimodal

This model supports image input. Alongside the quants, this repo includes the multimodal
projector file [mmproj-Swift-Qwen3.8-27B-F16.gguf](https://huggingface.co/ukisai/Swift-Qwen3.8-27B-GGUF/blob/main/mmproj-Swift-Qwen3.8-27B-F16.gguf),
which pairs with any tier above. llama.cpp downloads the mmproj automatically when using
`-hf` as shown above; if you are loading files manually, pass it with `--mmproj`.

#### MTP

This model has MTP (Multi-Token Prediction) layers, and they are included in every tier,
stored at Q8_0. MTP layers act as a built-in draft model, letting llama.cpp run speculative
decoding for faster generation. To use them, add the following flag to your llama.cpp command:

```
--spec-type draft-mtp --spec-draft-n-max 3
```

This is the counterpart of the vLLM `--speculative-config '{"method":"mtp","num_speculative_tokens":3}'` option.

### Ollama

```
ollama create swift -f <(curl -fsSL https://huggingface.co/ukisai/Swift-Qwen3.8-27B-GGUF/resolve/main/Modelfile) && ollama run swift
```

Use Ollama 0.33 or newer. The [`Modelfile`](https://huggingface.co/ukisai/Swift-Qwen3.8-27B-GGUF/blob/main/Modelfile)
in this repo pulls the `Q4_K_M` tier together with the vision projector, applies the sampling
values above, and sets Ollama's built-in Qwen3.8 renderer and parser, which separate reasoning
from the answer and parse tool calls. Swift's embedded chat template is identical to Qwen3.8's.
For another tier, download the Modelfile, change the tag after `FROM`, and run
`ollama create swift -f Modelfile`.

`ollama run hf.co/ukisai/Swift-Qwen3.8-27B-GGUF:Q4_K_M` also works without a Modelfile. It
runs the embedded chat template through llama.cpp and reads the sampling values from the
[`params`](https://huggingface.co/ukisai/Swift-Qwen3.8-27B-GGUF/blob/main/params) file.
Hugging Face cannot set Ollama's renderer and parser, so in this mode reasoning may appear
inline with the answer.

Ollama sizes the context window from VRAM: 262,144 tokens with 48 GB or more, 32,768 with
24 GB, and 4,096 below that, which is too short for long reasoning. To raise it, start the
server with `OLLAMA_CONTEXT_LENGTH=65536 ollama serve` or run `/set parameter num_ctx 65536`
in the chat. To use the MTP layers, run `/set parameter draft_num_predict 3`.

### UkisAI API

If you would rather not run the weights yourself, Swift is served through an
OpenAI-compatible API at `https://ukisai.com/api/swift/v1`. It is **free for research
purposes** and needs no API key. The model id is `swift`.

```bash
curl https://ukisai.com/api/swift/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "swift", "messages": [{"role": "user", "content": "Hello, Swift."}]}'
```

## Validation

The converted files passed a finite-tensor check and a CPU text-generation smoke test.
Multimodal generation and the full benchmark suite have **not** been re-evaluated on
this GGUF release. The results above and on the
[source model card](https://huggingface.co/ukisai/Swift-Qwen3.8-27b) come from the BF16
and INT4 checkpoints named there, not from these files.

## License and access

Swift weights are distributed through gated access under the **Swift Open License v1.0**.
Personal, research, educational, evaluation, and commercial use are free for individuals
and organizations with annual recurring revenue, including affiliates, of up to
US$1,000,000. Above that threshold, commercial use requires a separate **Swift Enterprise
License**. Contact [UkisAI](https://ukisai.com/contact) for terms.


## Citation

```bibtex
@misc{swift-qwen3.8-27b,
  title  = {Swift-Qwen3.8-27B},
  author = {UkisAI},
  year   = {2026},
  url    = {https://huggingface.co/ukisai/Swift-Qwen3.8-27b}
}
```
