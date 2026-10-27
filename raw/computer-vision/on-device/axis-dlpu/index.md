---
title: "Axis Deep Learning Processing Unit (DLPU)"
site: "Axis developer documentation"
source: "https://developer.axis.com/computer-vision/on-device/axis-dlpu/"
domain: "developer.axis.com"
language: "en"
description: "Some Axis products are equipped with a Deep Learning Processing Unit (DLPU)."
word_count: 223
---

Some Axis products are equipped with a Deep Learning Processing Unit (DLPU).

The DLPU is designed to accelerate the execution of models, making inference significantly faster compared to the CPU. The drawback, however, is that the DLPU is more limited in what it can process compared to the more general-purpose CPU.

## Axis products with DLPU

Use the [Product Selector](https://www.axis.com/support/tools/product-selector/shared/%5B%7B%22index%22%3A%5B10%2C1%5D%2C%22value%22%3A%22DLPU%22%7D%5D) to find products with a DLPU. (Use the filters under "Hardware platform")

Not all products have the same DLPU. Which DLPU a product has is found by checking the System on Chip (SoC) name. There are currently 5 different kinds of SoCs that support acceleration with DLPU:

- ARTPEC-7
- ARTPEC-8
- ARTPEC-9
- CV25
- CV75

These SoCs work and perform differently, and the process of getting your model to run on the DLPU is different depending on which SoC your product has. Here is a brief overview:

| SoC | Speed | Ease of use | Conversion from source model |
| --- | --- | --- | --- |
| CPU | 🐢 | Easy | ─>.tflite |
| ARTPEC-7 | 🚲 | Easy | ─> quantized.tflite ─> edge-tpu.tflite |
| ARTPEC-8 | 🚙 | Medium | ─> quantized.tflite |
| ARTPEC-9 | 🚀 | Medium | ─> quantized.tflite |
| CV25 | 🚙 | Hard | ─>.onnx ─> native.bin   └>.tflite ─> native.bin |
| CV75 | 🚀 | Hard | ─>.onnx -> native.bin |

The table is deliberately vague for "Speed" because the speed varies depending on the model, how optimized the model is for the SoC, and variations in hardware configurations for the product (e.g. clock speed, memory).
