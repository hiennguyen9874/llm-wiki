---
type: Model System
title: PP-OCRv6
description: PP-OCRv6 is a 1.5M–34.5M-parameter OCR family that uses a shared reparameterizable MetaFormer-style backbone for text detection and recognition.
tags: [ocr, multilingual, lightweight-models, text-detection, text-recognition]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T21:53:41+07:00 }
sources:
  - id: pp-ocrv6-report
    resource: ../raw/2606.13108_PP-OCRv6/main.tex
    title: "PP-OCRv6: From 1.5M to 34.5M Parameters, Surpassing Billion-Scale VLMs on OCR Tasks"
---

# PP-OCRv6

PP-OCRv6 is a three-tier, two-stage OCR family that shares the LCNetV4 backbone across text detection and recognition. The authors report end-to-end medium, small, and tiny configurations of 34.5M, 7.7M, and 1.5M parameters, respectively; architectural changes complement the PP-OCRv5 data-curation methodology.[^pp-ocrv6-report]

## Architecture

**LCNetV4** separates spatial token mixing from channel mixing in a MetaFormer-style block. Its token mixer is a depthwise convolution with optional squeeze-and-excitation and a residual path; its channel mixer is a residual 2× pointwise expand–GELU–compress path. During training, the depthwise operation has parallel 3×3, 1×1, and batch-normalized identity branches; they are structurally fused into a single 3×3 depthwise convolution for inference. The same backbone uses normal downsampling to produce a four-scale detection pyramid, or asymmetric `(2,1)` strides in its last two recognition stages to preserve sequence width.[^pp-ocrv6-report]

- **Detection:** LCNetV4 feeds RepLKFPN and a DB head. RepLKFPN uses reparameterizable large-kernel depthwise refinement; its reported 7×7 configuration fuses a main depthwise branch and three dilated branches at inference. Training-only auxiliary DB heads on P2–P4 use Dice plus Focal loss; the auxiliary heads are removed for inference.[^pp-ocrv6-report]
- **Recognition:** medium and small tiers use EncoderWithLightSVTR: a 1×7 widthwise depthwise convolution adds local context before global self-attention, and an additive 1×1 skip replaces PP-OCRv5's concatenation-and-projection fusion. A CTC head runs at inference; an NRTR head supplies training-only auxiliary supervision. The tiny tier omits the neck and uses CTC-logit distillation from a dictionary-matched medium teacher.[^pp-ocrv6-report]

Medium and small recognition models support 50 languages, adding 46 Latin-script languages to PP-OCRv5's Simplified Chinese, Traditional Chinese, English, and Japanese set. The tiny model supports 49 languages because it omits Japanese to avoid its roughly 4,000 Kanji/Kana dictionary entries.[^pp-ocrv6-report]

## Reported results

The following are author-reported results on in-house benchmarks:[^pp-ocrv6-report]

- **Detection:** medium, small, and tiny reach 86.2%, 84.1%, and 80.6% average Hmean. Medium exceeds the reported PP-OCRv5 server score by 4.6 points (86.2 vs. 81.6).
- **Recognition:** medium, small, and tiny reach 83.2%, 81.3%, and 73.5% weighted accuracy. Medium exceeds PP-OCRv5 server by 5.1 points (83.2 vs. 78.1).
- **Robustness:** medium's reported detection Hmean averaged across seven resolution scales is 86.67%, with 5.19% coefficient of variation; its recognition prediction consistency across crop margins is 75.32%, compared with 54.82% for PP-OCRv5 server.
- **Efficiency:** on Intel Xeon 8350C with OpenVINO, the tiny end-to-end pipeline is reported at 0.20 s/image, 3.9× faster than PP-OCRv5 mobile (0.78 s/image). At 2048-pixel detection input on a V100, the medium detector is reported at 106.89 ms on GPU and 2327.23 ms on CPU ONNX, versus 253.52 and 3034.93 ms for PP-OCRv5 server.
- **Hallucination evaluation:** medium scores 93.2% on the authors' curated benchmark, versus 80.56% for Qwen3-VL-235B and 78.0% for GPT-5.5. This measures correct outputs without hallucinated content, not a general proof that the system cannot hallucinate.[^pp-ocrv6-report]

## Trust limits

- The bundle contains a technical report, source bibliography, and architecture, result, and qualitative attachments, but no weights, datasets, implementation, evaluation code, outputs, or released benchmark configurations. None of its performance, latency, or training claims are independently reproducible from the bundle.[^pp-ocrv6-report]
- Detection, recognition, hallucination, crop-margin, language, and end-to-end speed results use author-curated or in-house data and protocols. Scenario sizes, sampling, model prompts and settings for VLM comparisons, uncertainty estimates, and evaluated outputs are not supplied.[^pp-ocrv6-report]
- The report's qualitative explanation that CTC-based decoding prevents hallucination overstates its own measured result: medium scores 93.2%, rather than 100%, on its hallucination benchmark.[^pp-ocrv6-report]

## Relationships

- **Builds on:** [PP-OCRv5](pp-ocrv5.md)'s data-curation methodology while replacing its separate LCNetV3 and PPHGNetV2 backbone families with LCNetV4.[^pp-ocrv6-report]
- **Benchmarked by:** [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md), which retains the reported detection, recognition, robustness, multilingual, hallucination, and runtime protocols.

[^pp-ocrv6-report]: Zhang et al., *PP-OCRv6: From 1.5M to 34.5M Parameters, Surpassing Billion-Scale VLMs on OCR Tasks*, local LaTeX source at [main.tex](../raw/2606.13108_PP-OCRv6/main.tex), including the [system overview](../raw/2606.13108_PP-OCRv6/v6_images_v2/01system.jpg), [LCNetV4 diagram](../raw/2606.13108_PP-OCRv6/v6_images_v2/backbone.png), [detection architecture](../raw/2606.13108_PP-OCRv6/v6_images_v2/ppocrv6_det_pip_ori.png), [recognition architecture](../raw/2606.13108_PP-OCRv6/v6_images_v2/rec.png), [accuracy comparison](../raw/2606.13108_PP-OCRv6/v6_images_v2/v6acc_opt.png), and detector-speed plots (accessed 2026-08-17).
