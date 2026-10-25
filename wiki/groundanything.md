---
type: Model System
title: GroundAnything
description: GroundAnything is a 4B visual-grounding model family whose shared vision-language backbone supports both an autoregressive checkpoint and a blockwise-diffusion checkpoint using the quantized GAM coordinate protocol.
tags: [visual-grounding, object-detection, ocr, document-layout, diffusion-decoding, parallel-decoding, vision-language-models]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T10:37:15+07:00 }
stale_after: 2027-04-25
sources:
  - id: groundanything-card
    resource: ../raw/GroundingPI-GroundAnything.md
    kind: model-card
    title: GroundAnything (DLM) model card
---

# GroundAnything

GroundAnything is a 4B-parameter visual-grounding model family from GroundingPI that treats grounding as visual evidence extraction: object locations and spatial relations are jointly constrained by the image and the query, so their dependencies do not require left-to-right generation. The release ships two checkpoints over one shared backbone — an autoregressive `GroundAnything-VLM` and a blockwise-diffusion `GroundAnything` — with the parallel-decoding checkpoint positioned as the faster mode at a measured accuracy cost.[^groundanything-card]

## Family and checkpoints

| Checkpoint | Generation | Evaluation mode |
|:---|:---|:---|
| [GroundAnything](groundanything-decoding-and-serving.md) (DLM) | Entropy-guided blockwise diffusion, optional self-speculation | GAM |
| GroundAnything-VLM | Autoregressive | GAM |

Both repositories share the same spatial output interface but have different loading and generation paths. All three released checkpoints (the two above plus the earlier GroundingPI model) are evaluated in GAM mode; see [GroundAnything decoding and serving](groundanything-decoding-and-serving.md) for the diffusion procedure and its runtime.[^groundanything-card]

## Architecture

The architecture is one vision-language backbone configured for causal or bidirectional response-block prediction:[^groundanything-card]

- **Vision encoder:** MoonViT-V2 / Kimi-K3 vision backbone.
- **Language backbone:** Qwen3-4B-Instruct-2507.
- **Projector:** 2 × 2 spatial aggregation followed by a two-layer MLP.
- **Spatial vocabulary:** 1,000 coordinate tokens shared with semantic labels and protocol markers.
- **AR-to-DLM conversion:** the same decoder and vocabulary head serve causal prediction and bidirectional response-block denoising, with an added mask token for diffusion generation.

The card gives the 4B figure without stating which components it counts, so whether it covers the vision tower or only the language backbone is a limit of this source.[^groundanything-card]

## Output protocol (GAM)

Outputs are text containing semantic labels plus quantized spatial coordinates. A bounding box is `(x1, y1, x2, y2)` and a point is `(x, y)`; adjacent coordinate tokens carry no intervening spaces, multiple instances of one label are comma-separated inside a single box wrapper, and a missing target is emitted as `None`.[^groundanything-card]

```text
<|object_ref_start|>car<|object_ref_end|><|box_start|><100><200><500><650><|box_end|>
<|object_ref_start|>absent object<|object_ref_end|><|box_start|>None<|box_end|>
```

Prompts use the same 0–999 token vocabulary for reference boxes and separate multiple categories with `</c>`. The supplied client returns parsed predictions together with `raw_output`, `finish_reason`, `usage`, `parse_error`, and `valid`, maps coordinates back to image pixels, and marks truncated or malformed responses invalid; custom clients must keep `skip_special_tokens=false` and must not insert spaces between spatial tokens.[^groundanything-card]

## Prompt-selected tasks

| Task | Prompt shape |
|:---|:---|
| Category / dense grounding | `Locate all the instances that match the following categories: car</c>person.` |
| Referring boxes | `Locate the target referred to by the following description: …` |
| Category or referring points | `Point to: car</c>person.` / `Point to the target referred to by …` |
| OCR | `OCR task detect all the text in box format.` |
| Document layout | `Detect all document layout elements that match the following categories: title</c>text.` |
| GUI | `Point to the UI element to click for the following instruction: …` |
| Visual prompting | Reference boxes in native spatial tokens, then “find all similar objects” |

The convenience client wraps only referring-box and referring-point prompts; other templates require OpenAI-compatible `/chat/completions` calls with image and prompt in one user message.[^groundanything-card] These OCR and layout tasks emit localized text and layout boxes rather than a reconstructed document, so the model complements rather than replaces document-to-Markdown parsers.

## Reported results

All figures below are author-reported model-card claims from the companion paper, not independently reproduced here:[^groundanything-card]

- **Autoregressive variant:** 72.42% overall across 30 grounding benchmarks, claimed state of the art among similarly sized models and competitive with GPT-6 Astra at 71.35%.
- **Entropy-guided diffusion variant:** 61.75% average, versus 53.32% for the fast multi-token-prediction model LocateAnything.
- **Self-speculative mode:** 4.51× speedup over the autoregressive counterpart with a 0.74-percentage-point drop in COCO F1-mIoU at the paper's reported operating point.

The card does not state whether the 72.42% and 61.75% averages share a benchmark set or aggregation rule, and the per-benchmark matrix exists only in a remote figure (`assets/fig7-grounding-performance.png`) that is not retained in `raw/`. The roughly ten-point gap between the two numbers therefore cannot be attributed to decoding mode alone from this source.[^groundanything-card]

## License and intended use

Original contributions are Apache 2.0, but the combined package carries third-party terms: Kimi-derived material and applicable derivative works remain under the Kimi K3 License, and those conditions continue to apply on use or redistribution of the packaged model. Deployment geography is stated as global.[^groundanything-card]

The card's stated uses are open-vocabulary localization and dense-scene grounding, referring-expression and visual-prompt localization, point localization and GUI element grounding, OCR with text localization and document layout understanding, and perception research for robotics and embodied agents. Its ethical section notes that small or occluded objects may be missed, instances may repeat, text and coordinates may be inaccurate, and GUI points describe image locations without executing interface actions.[^groundanything-card]

## Coverage and trust limits

- **Evidence class:** the architecture, protocol, dependency, and runtime details are **observed** from static inspection of the card; every benchmark and speedup figure is **reported** only.
- The card links [arXiv:2609.39600](https://arxiv.org/abs/2609.39600), the GitHub repository, the project page, a `LICENSE` file, a separate GroundAnything-VLM model card, and ModelScope mirrors; none are retained under `raw/`, so the paper's protocols, baselines, and per-benchmark results could not be inspected.[^groundanything-card]
- All illustration, teaser, architecture, decoding, and benchmark-overview assets, plus two demo videos, are remote CDN references absent from the local bundle; no figure content is reflected in this synthesis.[^groundanything-card]
- No training data, compute budget, training recipe, evaluation scripts, or weights are described in the card beyond the serving commands recorded in [GroundAnything decoding and serving](groundanything-decoding-and-serving.md).[^groundanything-card]
- The card reports a 74-upvote Hugging Face Papers milestone on 2026-10-14; community attention is not evidence of quality.[^groundanything-card]

## Relationships

- **Uses:** [GroundAnything decoding and serving](groundanything-decoding-and-serving.md) documents the entropy-guided denoising, self-speculative verification, and SGLang runtime for this family.
- **Shares task interface with:** [Rex-Omni](rex-omni.md), which also casts detection, grounding, OCR, and keypoints as quantized coordinate sequences, but decodes autoregressively; the GroundAnything evaluation toolkit exposes a `REXOMNI` mode alongside `LOCATEANYTHING`, `GROUNDINGDINO`, and `VLM` baselines.
- **Contrasts with:** [MinerU-Diffusion](mineru-diffusion.md), which applies block-level parallel diffusion to page OCR rather than visual grounding.
- **Belongs to:** [Task: Unified perception and grounding](task-unified-perception-grounding.md), and is listed among adjacent unified perception systems in [Current OCR approaches](current-ocr-approaches.md).

[^groundanything-card]: GroundingPI, *GroundAnything (DLM) model card*, local capture at [GroundingPI-GroundAnything.md](../raw/GroundingPI-GroundAnything.md), § Model Overview, § Model Architecture, § Input(s)/Output(s), § Software Integration, § Model Version(s), § Evaluation, § Quantitative Evaluation Benchmarks, § Supported Tasks & Prompt Templates, § Ethical Considerations, and release log (accessed 2026-10-25).
