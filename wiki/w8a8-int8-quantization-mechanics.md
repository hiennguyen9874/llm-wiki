---
type: Concept
title: W8A8 INT8 Quantization Mechanics
description: INT8 W8A8 mechanics for Llama 3.1 8B Instruct where SmoothQuant smooths activation outliers via RMSNorm gamma and GPTQ compensates weight-rounding error to cut 14.9 GB to 8.0 GB.
tags: [quantization, w8a8, smoothquant, gptq, llm-compressor]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: w8a8-mechanics
    resource: ../raw/understanding-w8a8-int8-llm-quantization/index.md
    title: 'Understanding W8A8 INT8 LLM quantization: Half the size, better performance, same accuracy'
---

Llama 3.1 8B Instruct was compressed from about 14.9 GB to 8.0 GB, roughly 46% smaller, with INT8 W8A8 quantization in llm-compressor using SmoothQuant followed by GPTQ and 512 WikiText-2 calibration samples, so weights and activations run as INT8 through matrix multiplication on faster INT8 tensor cores[^w8a8-mechanics].

## Six-step comparison workflow

- Benchmark base accuracy with lm-eval-harness on MMLU, ARC, HellaSwag, and IFeval[^w8a8-mechanics].
- Benchmark base serving performance with vLLM plus GuideLLM for latency, throughput, and concurrency[^w8a8-mechanics].
- Compress with llm-compressor INT8 W8A8 SmoothQuant plus GPTQ[^w8a8-mechanics].
- Repeat the same accuracy benchmarks on the compressed model[^w8a8-mechanics].
- Repeat the same serving load on the compressed model[^w8a8-mechanics].
- Compare side by side; identical benchmarks, hardware, and load isolate compression effects[^w8a8-mechanics].
- Experiment context: single NVIDIA L40S with 46 GB VRAM and `RedHatAI/Llama-3.1-8B-Instruct`[^w8a8-mechanics].

## W8A8 quantization core

- W8A8 means weights and activations are both INT8 during matrix multiplication, enabling GPU INT8 tensor cores versus BF16 tensor cores for the uncompressed model[^w8a8-mechanics].
- Per-column weight quantization core is `scale = max(abs(weight_column)) / 127` and `quantized_weight = round(weight / scale)`; 127 is the largest positive INT8 value[^w8a8-mechanics].
- Rounding is the lossy step; small per-weight errors accumulate across billions of weights and compound layer to layer because each layer output is the next layer input[^w8a8-mechanics].

## Why naive rounding fails

- Weight quantization is offline, so each weight column can have its own scale rather than one tensor-wide scale[^w8a8-mechanics].
- Worked source example with a 3-by-2 matrix gives `scale_ch0 = 0.74 / 127 = 0.005827` and `scale_ch1 = 0.93 / 127 = 0.007323`, quantized to `[[53,112],[127,62],[89,127]]`[^w8a8-mechanics].
- Dequantized reconstruction is approximately `[[0.3088,0.8202],[0.7400,0.4540],[0.5186,0.9300]]` versus original `[[0.31,0.82],[0.74,0.45],[0.52,0.93]]`[^w8a8-mechanics].
- With input `[1.0, 2.0, 0.5]`, original output `[2.050, 2.185]` becomes reconstructed `[2.048, 2.193]`, errors `-0.002` and `+0.008`; the source stresses 3 weights per channel looks small but Llama 3.1 8B has 4,096 weights per channel across 32 layers[^w8a8-mechanics].

## How GPTQ compensates

- After rounding each weight, GPTQ measures the output shift and nudges remaining unquantized weights to bring the layer output back toward the original[^w8a8-mechanics].
- Redistribution is Hessian-guided: the Hessian, computed from calibration activations, marks weights that strongly affect output as unsafe error sinks and low-sensitivity weights as safe absorbers[^w8a8-mechanics].
- Per-layer sequence is feed calibration data and record original output, compute Hessian from layer activations, quantize one weight, measure error, redistribute more error to less important weights, and repeat until the layer is quantized[^w8a8-mechanics].
- Keep `lm_head` in full precision: it maps 4,096 hidden dimensions to about 128,000 vocabulary logits for token selection, so rounding there can flip the chosen token and cascade through the response[^w8a8-mechanics].

## Why activation quantization is hard

- Activations are quantized per token, dynamically at runtime, with one shared scale across all channels of that token[^w8a8-mechanics].
- Per-channel activation scales are impractical because activation channels sit on the inner axis of the dot product and are summed together; individual scales cannot be reversed after accumulation[^w8a8-mechanics].
- Outlier example `activations = [1.32, 0.75, 0.91, 153.0]` gives `scale = 153.0 / 127 = 1.205` and quantized `[1, 1, 1, 127]`: the outlier survives while the other channels are squashed[^w8a8-mechanics].

## How SmoothQuant fixes outliers

- In Llama 3.1 8B the outlier source traced in the source is RMSNorm `gamma`: RMS division stabilizes overall magnitude but learned per-channel `gamma` is fixed at inference, so a large `gamma` such as 100 on channel 3 turns balanced normalized `[1.32, 0.75, 0.91, 1.53]` into `[1.32, 0.75, 0.91, 153.0]`[^w8a8-mechanics].
- SmoothQuant only modifies weights, namely RMSNorm `gamma` divided down plus a compensating scale-up of the matching input row of the next linear layer; smoother activations follow from smoothed `gamma` without touching activations directly[^w8a8-mechanics].
- Smoothed example gives activation `[1.32, 0.75, 0.91, 1.53]`, scale `1.53 / 127 = 0.012`, and quantized `[110, 63, 76, 127]` versus unsmoothed `[1, 1, 1, 127]`[^w8a8-mechanics].
- Magnitude preservation comes from moving scale from normalization to the next linear layer; inflating those weights is safe because GPTQ uses per-channel weight scales where one large column does not corrupt other columns[^w8a8-mechanics].

## Smoothing-factor formula

- Per-channel factor is `S_j = max(abs(A_j))^alpha / max(abs(W_j))^(1-alpha)` with `alpha = 0.8`, shifting most difficulty from activations to weights[^w8a8-mechanics].
- `max(abs(A_j))` is the largest observed activation in channel `j` across calibration samples; `max(abs(W_j))` is the largest weight in receiving row `j`[^w8a8-mechanics].
- Large `S_j` strongly scales down outlier channels while near-1 `S_j` leaves normal channels almost unchanged, so smoothing is proportional to outlier severity[^w8a8-mechanics].
- Order is SmoothQuant in BF16 first, then GPTQ quantizes the smoothed weights to INT8; in llm-compressor both stages are defined together in one recipe and run automatically in sequence[^w8a8-mechanics].

## Calibration-data guidance

- Both stages feed the same calibration inputs and collect per-layer activations but use them differently: SmoothQuant finds outlier channels and severity for `S_j`, while GPTQ computes Hessian sensitivity to steer rounding-error redistribution[^w8a8-mechanics].
- Mismatched calibration can smooth the wrong channels and protect the wrong weights, adding avoidable accuracy loss[^w8a8-mechanics].
- Prefer deployment-matched domain and style: UltraChat-style conversation for chat, code for code generation, medical text for medical QA[^w8a8-mechanics].
- This experiment used general encyclopedia-style WikiText-2 for instruction-tuned Llama 3.1 8B Instruct evaluated on MMLU, ARC, HellaSwag, and IFeval; domain overlap was reasonable for general-knowledge tasks but style was prose versus questions, scenario completions, and direct commands, yet accuracy held, so the source treats WikiText-2 as a conservative lower bound and recommends matched calibration for production[^w8a8-mechanics].

## Size result

- BF16 accounting is about `8,000,000,000 × 2 bytes = 16,000,000,000 bytes ≈ 14.9 GB`; INT8 accounting is about `8,000,000,000 × 1 byte ≈ 7.5 GB`[^w8a8-mechanics].
- The shipped 8.0 GB rather than 7.5 GB reflects unquantized parts such as `lm_head` in BF16 plus stored quantization scales[^w8a8-mechanics].

## Relationships

- Complements [W8A8 INT8 Accuracy and Performance Results](w8a8-int8-accuracy-performance-results.md) — part 2 of the same series reports accuracy deltas, GuideLLM serving numbers, and load-dependent activation-quantization overhead.
- Uses [vLLM LLM Compressor Quantization Workflows](vllm-llm-compressor-workflows.md) — provides the offline SmoothQuant-plus-GPTQ INT8 W8A8 recipe, `lm_head` exclusion, and calibration-size context.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — broader format and hardware context for choosing W8A8 INT8 versus W8A16 or FP8.

## Coverage limits

- Local figure and formula images were covered through surrounding prose, alt text, captions, and the transcribed smoothing-factor equation rather than independent pixel-level verification.
- Numerical examples, hardware behavior, and accuracy or speedup expectations are source-reported and were not independently reproduced.
- Serving benchmarks and accuracy tables belong to part 2 and are compiled separately; see the part-2 concept for those results.

[^w8a8-mechanics]: Sana Fayyaz, Understanding W8A8 INT8 LLM quantization: Half the size, better performance, same accuracy — `../raw/understanding-w8a8-int8-llm-quantization/index.md`, six-step workflow, W8A8 definition, naive-quantization worked example, GPTQ Hessian compensation, activation-outlier problem, SmoothQuant gamma smoothing with worked example and alpha-0.8 formula, calibration-dataset guidance, WikiText-2 limits, and 14.9-GB to 8.0-GB size accounting.
