---
type: Concept
title: PaddleOCR model and training architecture
description: PaddleOCR's training toolkit assembles OCR models from configurable transforms, backbones, necks, and heads, with distinct PP-OCRv6 detection and recognition configurations.
tags: [ml, ocr, architecture, training]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T06:53:14Z }
stale_after: 2027-04-29
sources:
  - id: paddleocr-repo
    resource: ../raw/PaddleOCR/README.md
    scope: ../raw/PaddleOCR/
    kind: code
    revision: dab3fe3
    title: PaddleOCR repository
---

# PaddleOCR model and training architecture

**Observed:** The source-tree training toolkit builds OCR models from configuration, composing an optional transform, backbone, neck, and head; it is distinct from the PaddleX-backed [repository pipeline wrappers](paddleocr-repository-pipelines.md). The PP-OCRv6 medium configuration instantiates different detector and recognizer architectures using a shared PPLCNetV4 backbone family.[^paddleocr-repo]

## Composition and concrete configurations

`BaseModel` constructs each configured component in sequence, passing output channels into the next component; its forward method can return intermediate features. Training configuration also specifies dataset, transformations, loss, optimizer, postprocessing and metric. **Observed:** the following are training configurations, not proof of the exact exported model or runtime actually used:[^paddleocr-repo]

| PP-OCRv6 medium | Configured components |
| --- | --- |
| Detection | `PPLCNetV4` detection backbone → `RepLKPAN` neck (256 channels) → `DBHead` with auxiliary channels; `DBLoss` with Dice/Focal and auxiliary weights; `DBPostProcess`. |
| Recognition | `PPLCNetV4` recognition backbone → `MultiHead` with CTC/LightSVTR (192 dimensions, depth 2) and NRTR branches; CTC and NRTR losses, `CTCLabelDecode`, and a character dictionary. |

The detector training configuration uses postprocessing thresholds 0.2 and 0.45; the C++ inference configuration instead specifies 0.3 and 0.6. These different contexts must not be conflated as one universal default.[^paddleocr-repo]

## Boundaries and limitations

The package configuration installs the `paddleocr` wrapper and depends on PaddleX; the checked-in training code is a separate source-tree surface. The VLM tutorial **reports** a NaViT-style dynamic-resolution encoder and ERNIE-4.5-0.3B language model for the initial VL component, and warns that the full layout-plus-VLM pipeline differs from that component alone. See [PP-OCRv6](pp-ocrv6.md) and [PaddleOCR-VL](paddleocr-vl.md) for the paper-based architectures. This inspection did not execute training or inspect weights or external PaddleX model implementation; other architectures and configs remain pending.[^paddleocr-repo]

## Relationships

- **Used by:** [PaddleOCR repository pipelines](paddleocr-repository-pipelines.md), as a source-tree training and classic inference stack.
- **Implements:** configurations for [PP-OCRv6](pp-ocrv6.md).[^paddleocr-repo]

[^paddleocr-repo]: [Repository README](../raw/PaddleOCR/README.md), “Key Features”; revision `dab3fe3`: `ppocr/modeling/architectures/base_model.py::BaseModel`; `configs/det/PP-OCRv6/PP-OCRv6_medium_det.yml::Architecture`, `Loss`, `PostProcess`; `configs/rec/PP-OCRv6/PP-OCRv6_medium_rec.yml::Architecture`, `Loss`, `PostProcess`, `Global.character_dict_path`; `deploy/cpp_infer/src/configs/OCR.yaml::SubModules.TextDetection`; `pyproject.toml::project.dependencies` and `tool.setuptools.packages.find`; `docs/version3.x/pipeline_usage/PaddleOCR-VL.en.md`, introduction.
