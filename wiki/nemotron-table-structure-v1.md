---
type: Model System
title: Nemotron Table Structure v1
description: NVIDIA's YOLOX-based table-structure detector that localizes cells, rows, and columns in table images for downstream OCR-to-Markdown pipelines.
tags: [object-detection, table-structure, yolox, document-parsing, nvidia]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T12:00:00Z }
sources:
  - id: nemotron-table-structure-v1-model-card
    resource: ../raw/nemotron-table-structure-v1.md
    title: Nemotron Table Structure v1 model card
---

# Nemotron Table Structure v1

Nemotron Table Structure v1 is NVIDIA's 54M-parameter YOLOX table-structure detector that localizes cells (including merged cells), rows, and columns in 1024×1024-resized table images and outputs normalized boxes with scores for conversion to Markdown via OCR.[^nemotron-table-structure-v1-model-card]

## Architecture

- **Base:** YOLOX anchor-free single-stage detector, DarkNet53 backbone + FPN with decoupled head (one 1×1 conv + two parallel 3×3 convs for classification and box regression), building on YOLOv3 improvements; developed by complete retraining rather than from pretrained YOLOX weights.[^nemotron-table-structure-v1-model-card]
- **Parameters:** 5.4e7.[^nemotron-table-structure-v1-model-card]
- **Classes:** cell, row, column.[^nemotron-table-structure-v1-model-card]
- **Runtime targets:** NVIDIA GPU-accelerated systems (CUDA); NIM API at `nemoretriever-table-structure-v1`; commented source lists Ampere/Hopper/Lovelace and Linux as integration targets.[^nemotron-table-structure-v1-model-card]

## Input and output

- **Input:** RGB image (2D), resized to 1024×1024.[^nemotron-table-structure-v1-model-card]
- **Output:** Dictionary of dictionaries containing `np.ndarray` objects per sample; after post-processing three arrays `boxes [N×4]` (normalized `x_min, y_min, x_max, y_max`), `labels [N]`, `scores [N]` for classes cell/row/column; NMS thresholds `conf_thresh=0.01`, `iou_thresh=0.25`.[^nemotron-table-structure-v1-model-card]
- **Pipeline role:** Input expected to be a cropped table image (e.g., from [Nemotron Page Elements v3](https://huggingface.co/nvidia/nemotron-page-elements-v3)); designed to pair with OCR (e.g., Nemotron OCR) to preserve row/column/cell relationships and convert tables to Markdown for retrieval.[^nemotron-table-structure-v1-model-card]

## Training and evaluation

- **Pretraining (NVIDIA):** 118,287 images from COCO train2017.[^nemotron-table-structure-v1-model-card]
- **Fine-tuning (NVIDIA):** 23,977 images from Digital Corpora, annotations from Azure AI Document Intelligence layout model `2024-02-29-preview`; 1,828,978 cells, 134,089 columns, 316,901 rows. Automated collection and labeling.[^nemotron-table-structure-v1-model-card]
- **Evaluation set:** Cut of Azure labels / Digital Corpora images (hybrid automated+human collection/labeling, manually selected pages plus visual inspection on public PDFs/slides); 200,840 cells, 13,670 columns, 34,575 rows.[^nemotron-table-structure-v1-model-card]
- **Metrics:** Mean Average Precision (mAP) per class; reported per-class AP/AR:[^nemotron-table-structure-v1-model-card]

| Class | AP (%) | AR (%) |
|---|---:|---:|
| cell | 58.365 | 60.647 |
| row | 76.992 | 81.115 |
| column | 85.293 | 87.434 |

## Usage

- Requires `torch` and repository custom code; clone via `https://huggingface.co/nvidia/nemotron-table-structure-v1` (git-lfs), pip-installable; inference via `define_model`, `model.preprocess`, `model(x, img.shape)`, `postprocess_preds_table_structure(preds, model.threshold, model.labels)`; advanced table-to-text pipeline demonstrated with Nemotron OCR in `Demo.ipynb`.[^nemotron-table-structure-v1-model-card]
- Minimal inference code provided; further training refers to upstream [Megvii YOLOX repo](https://github.com/Megvii-BaseDetection/YOLOX).[^nemotron-table-structure-v1-model-card]

## Limitations and disclaimer

Vendor disclaimer notes known issues to be addressed in v2: lower confidence / missed cells at bottom of table; missing table-title class; lacking support for non-full-page tables; not robust to rotated tables and may not generalize to unknown formats.[^nemotron-table-structure-v1-model-card]

## Trust limits

- Source is a model card, not a paper with code/datasets; weights, evaluation scripts, and exact mAP protocol details beyond thresholds are not in the bundle, so training and metric claims are vendor-reported and not independently reproduced.[^nemotron-table-structure-v1-model-card]
- Referenced `viz.png` preview image was not present alongside the local source and was not inspected; downstream notebook `Demo.ipynb` not in bundle.[^nemotron-table-structure-v1-model-card]
- License described as NVIDIA Open Model License for the model and Apache 2.0 for post-processing scripts; confirm from linked agreements before use.[^nemotron-table-structure-v1-model-card]
- Deployment geography listed as Global; team: Theo Viel, Bo Liu, Darragh Hanley, Even Oldridge; release 2025-10-23 via Hugging Face.[^nemotron-table-structure-v1-model-card]

## Relationships

- **Uses:** YOLOX architecture ([YOLOX paper](https://arxiv.org/abs/2107.08430)) via DarkNet53+FPN decoupled head.[^nemotron-table-structure-v1-model-card]
- **Works with:** Table cropping via Nemotron Page Elements v3 and text extraction via Nemotron OCR / [Nemotron OCR v2](nemotron-ocr-v2.md) for table-to-Markdown retrieval.[^nemotron-table-structure-v1-model-card]
- **Complements:** Modular parsers such as [PP-StructureV3](pp-structurev3.md) and [MinerU](mineru.md) that include separate table-structure stages; differs from generative VLMs that emit Markdown directly.

[^nemotron-table-structure-v1-model-card]: NVIDIA, *Nemotron Table Structure v1 model card*, local [nemotron-table-structure-v1.md](../raw/nemotron-table-structure-v1.md) (accessed 2026-08-22). Referenced `viz.png` was absent locally and not inspected.
