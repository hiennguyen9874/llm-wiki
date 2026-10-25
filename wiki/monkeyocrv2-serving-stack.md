---
type: Software
title: MonkeyOCRv2 serving and deployment stack
description: MonkeyOCRv2 runs encoder, parsing, and document-understanding checkpoints through separate Transformers and vLLM paths, with an optional DFlash speculative-decoding variant, CLI, Gradio, and FastAPI front ends, a CPU path, and RAGFlow integration.
tags: [ocr, document-parsing, deployment, vllm, dflash, speculative-decoding, api]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:32:14Z }
stale_after: 2027-01-25
sources:
  - id: monkeyocrv2-model-card
    resource: ../raw/zenosai-MonkeyOCRv2-B-Parsing.md
    kind: model-card
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI (model card and repository README)"
---

# MonkeyOCRv2 serving and deployment stack

The MonkeyOCRv2 card doubles as the project README and documents three runtimes rather than one: a Transformers path for the vision encoders, a vLLM path for parsing that has an optional DFlash speculative variant, and a vLLM-or-Transformers path for document understanding. Around the parsing server it adds CLI, Gradio, and FastAPI front ends, a CPU path since 2026.08.22, and third-party adoption by RAGFlow since 2026.09.07. This page records card instructions and vendor claims as written: the repository scripts, `docs/`, requirements files, and all checkpoints sit outside the local bundle, so no command here was executed or verified.[^monkeyocrv2-model-card]

## Released artifacts

| Artifact | Total | ViT | LLM | Card-reported MDPBench overall |
| --- | --- | --- | --- | --- |
| MonkeyOCRv2-S | 28M | ViT-S | — | — |
| MonkeyOCRv2-B | 113M | ViT-B | — | — |
| MonkeyOCRv2-AS | 21M | ViTAEv2-S | — | — |
| MonkeyOCRv2-S-Parsing | 0.6B | 0.03B | 0.6B | 82.5 |
| MonkeyOCRv2-B-Parsing | 0.7B | 0.1B | 0.6B | 83.3 |
| MonkeyOCRv2-S-Und | 1.7B | not stated | not stated | — |
| MonkeyOCRv2-B-Und | 1.8B | not stated | not stated | — |

The encoders are pretrained at a resolution the card writes as `1280*28*28` for S and B and `1760*32*32` for AS; the card does not say whether these numbers denote pixels, tokens, or patch counts. The parsing table also reports the B variant as ranked first among the evaluated open-source models on the MDPBench leaderboard, at 83.3 overall (see [MDPBench](mdpbench.md)). Understanding checkpoints are scored on a separate eight-benchmark composite rather than on parsing, and the card's understanding table does not repeat the encoder/LLM parameter split.[^monkeyocrv2-model-card]

## Parsing runtime

Parsing is served from one vLLM process that the front ends call over HTTP. The card gives two install paths:

- **DFlash path:** vLLM 0.25.1, which the card states requires CUDA 12.9 or later, plus a second checkpoint (`MonkeyOCRv2-B-Parsing-DFlash`) downloaded alongside the base model. The card claims up to 2× faster inference and currently supports only B-Parsing.[^monkeyocrv2-model-card]
- **Plain path:** vLLM 0.11.2, which the card presents as the fallback when CUDA 12.9 is unavailable; inference works normally and DFlash acceleration is simply absent.[^monkeyocrv2-model-card]

`serve.py` takes `-m` for the parsing checkpoint, `-d` for the DFlash checkpoint, `--tp` for tensor parallelism across GPUs, and `-p` for the port (the examples use 8888). Client entry points are `parse.py` for directories or single documents (`-i`, `-o`, `-s`, with `--draw-layout` and `--skip-processed` toggles), a Gradio demo on port 8891, and a FastAPI app on port 8000.[^monkeyocrv2-model-card]

The FastAPI surface is documented only partially: `POST /parse` accepts either one multipart `file` field or a repeatable `files` field and returns `application/zip` named `monkeyocrv2_results.zip`, holding one directory of Markdown per document. The card defers remaining endpoints and request fields to the served `/docs`.[^monkeyocrv2-model-card]

## Encoder and understanding runtimes

The encoder path uses plain Transformers rather than vLLM. The stated environment pins PyTorch 2.8.0 with CUDA 12.6 wheels, `transformers==4.57.1`, `accelerate==1.11.0`, `qwen_vl_utils==0.0.14`, and `flash-attn==2.8.3` built with `--no-build-isolation`, and models load through `AutoModel.from_pretrained(..., trust_remote_code=True, dtype="auto", device_map="auto")`.[^monkeyocrv2-model-card] `trust_remote_code=True` means the checkpoint repository executes its own Python at load time; the card points to `docs/trust_remote_code.md` for what that code does, and that file is not in the bundle, so the execution surface cannot be audited from local evidence.

Document understanding offers both paths, with an explicit accuracy caveat: vLLM 0.11.2 is described as faster, while Transformers with `flash_attention_2` is described as aligned with the paper's reported performance. The serving example uses `serve.py` on port 8889 and `infer.py` with a question flag (`-q`).[^monkeyocrv2-model-card]

## Access paths and lifecycle

- **CPU:** the News entry dated 2026.08.22 announces CPU support for MonkeyOCRv2-Parsing and points to `docs/cpu_support.md`, which is not in the bundle; no CPU latency, throughput, or supported-instruction-set details are given.[^monkeyocrv2-model-card]
- **Third-party integration:** the News entry dated 2026.09.07 states that RAGFlow supports MonkeyOCRv2-Parsing as a PDF parser. The card claims the integration but documents neither version constraints nor how RAGFlow's layout handling interacts with the parsing pipeline.[^monkeyocrv2-model-card]
- **Fine-tuning:** the card routes parsing and understanding fine-tuning to `parsing/train/README.md` and `understanding/train/README.md`, and the News entry dated 2026.08.17 announces training and evaluation instructions for recognition, detection, overlapping-text segmentation, and formula tasks. Detection is split into DPText-DETR and MMOCR (DBNet, PSENet) trees, segmentation defers to an external MOTS repository, and tampering detection has its own `forensics/readme.md`. None of these paths exist locally.[^monkeyocrv2-model-card]
- **License:** Apache License 2.0, stated as free for research and commercial use, matching the card's `license: apache-2.0` frontmatter. No separate weights license, acceptable-use clause, or training-data restriction is published in the bundle.[^monkeyocrv2-model-card]

## Trust limits

- Every version pin, CUDA constraint, and speed multiplier here is vendor documentation: no install, server start, or timing run was reproduced, and the "up to 2×" DFlash figure has no stated hardware, batch size, resolution, or quality comparison.[^monkeyocrv2-model-card]
- The DFlash requirement couples a framework version to a CUDA major version, which makes this guidance the most perishable content on the page; `stale_after` marks operational freshness, not a source claim.[^monkeyocrv2-model-card]
- The card is a Hugging Face model card for a single variant (`MonkeyOCRv2-B-Parsing`) whose body covers the whole family; section headers therefore describe the release, not the repository that hosts this file.[^monkeyocrv2-model-card]

## Relationships

- **Depends on:** released [MonkeyOCRv2](monkeyocrv2.md) encoders, parsing checkpoints, and understanding checkpoints, which this stack serves.[^monkeyocrv2-model-card]
- **Uses:** DFlash speculative decoding, the same decoding family whose draft-model training is documented for [HunyuanOCR-1.5](hunyuanocr-training-and-inference-stack.md); the MonkeyOCRv2 card states only the checkpoint pairing and speed claim, not the mechanism.[^monkeyocrv2-model-card]
- **Integrates with:** RAGFlow as an external PDF-parser backend, a vendor-reported adoption rather than a tested integration here.[^monkeyocrv2-model-card]

[^monkeyocrv2-model-card]: Liu et al., *MonkeyOCRv2: A Visual-Text Foundation Model for Document AI*, model card and repository README captured at [zenosai-MonkeyOCRv2-B-Parsing.md](../raw/zenosai-MonkeyOCRv2-B-Parsing.md), locators: § News entries dated 2026.07.24, 2026.08.17, 2026.08.22, and 2026.09.07; § Model Zoo tables 1–3; § Quick Start › Vision Encoder, Document Parsing, and Document Understanding; § Copyright (accessed 2026-10-25).
