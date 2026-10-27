---
title: "Optimization Tips | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/"
domain: "developer.axis.com"
language: "en"
description: "The model needs to be int8/uint8 quantized. Operators that take in other types are not supported on the DLPU."
word_count: 93
---

The model needs to be int8/uint8 quantized. Operators that take in other types are not supported on the DLPU.

Tensors with up to 4 dimensions are supported.

Batch size >1 is not supported.

NHWC tensors are supported.

Per-channel quantization is supported only for the weights and bias tensors of a limited set of operations.

Prefer the `ReLU6` activation function when possible.

Avoid explicit padding when possible.

Convolution channels are partitioned into groups of 16, so it is optimal to have the number of channels be evenly divisible by 16, to not waste compute.
