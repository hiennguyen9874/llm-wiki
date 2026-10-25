---
type: Model System
title: LightOnOCR-3
description: LightOnOCR-3 is LightOn's Apache-2.0 OCR family in 0.8B, 1B, and 4B sizes that keeps empty-prompt transcription and adds a grounding mode emitting labelled bounding boxes, image descriptions, and chart-to-table extraction.
tags: [ocr, document-parsing, vision-language-models, visual-grounding, chart-extraction, qwen3-5]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:30:23Z }
stale_after: 2027-04-25
sources:
  - id: lightonocr-3-1b-card
    resource: ../raw/lightonai-LightOnOCR-3-1B.md
    kind: model-card
    title: LightOnOCR-3-1B model card
  - id: lightonocr-3-0-8b-card
    resource: ../raw/lightonai-LightOnOCR-3-0.8B.md
    kind: model-card
    title: LightOnOCR-3-0.8B model card
  - id: lightonocr-3-4b-card
    resource: ../raw/lightonai-LightOnOCR-3-4B.md
    kind: model-card
    title: LightOnOCR-3-4B model card
---

# LightOnOCR-3

LightOnOCR-3 is LightOn's Apache-2.0 document-OCR family, released in three sizes (0.8B, 1B, and 4B) that keep the empty-prompt transcription behavior of the previous generation and add an opt-in `grounding` mode. Grounding prefixes every page block with a type label and a bounding box, writes short descriptions for images, and converts charts into HTML tables of their data points. The 1B variant retains the LightOnOCR-2-1B architecture so existing deployments switch without change, while the 0.8B and 4B variants move to a Qwen3.5 vision-language architecture that the cards describe as simpler to integrate and significantly faster. Every capability and speed claim here is vendor-reported model-card text: the cards publish no benchmark table and no LightOnOCR-3 technical report.[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

## Family and variants

| Variant | Architecture | Card positioning | PDF render target |
|---|---|---|---|
| LightOnOCR-3-0.8B | Qwen3.5 VLM | Lightest family member, "same layout and visual understanding features" | 400 DPI, 2,048 px longest edge |
| LightOnOCR-3-1B | LightOnOCR-2-1B (unchanged) | Drop-in upgrade for existing LightOnOCR-2 deployments | 200 DPI, 1,540 px longest edge |
| LightOnOCR-3-4B | Qwen3.5 VLM | "Best OCR model, recommended for most tasks" | 400 DPI, 2,048 px longest edge |

All three cards list Apache-2.0 for research and commercial use and name the 4B as the largest and most accurate variant. The cards claim greater speed and transcription quality than the previous generation and position the family as a single-model replacement for multi-stage document-understanding pipelines, listing tables, receipts, forms, charts, multi-column layouts, and math notation as handled content.[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

## Prompt modes

The cards document exactly two supported prompts and warn that other instructions are out of distribution:[^lightonocr-3-1b-card][^lightonocr-3-4b-card]

- **Transcription:** an empty prompt (`""`, image only) returns all textual elements as Markdown. This is the default and is unchanged from LightOnOCR-2, so migration adds no call-site change.
- **Grounding:** the literal prompt `grounding` returns the new per-block labels and boxes alongside the transcribed text.

The only quantitative claim in the cards is that grounding adds about 25% output tokens over plain transcription — 1,433 versus 1,158 tokens per page on average, measured for the 4B. Per-variant output overhead is not reported.[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

## Grounding output contract

Each block is introduced by a placeholder line `![label](x1,y1,x2,y2)` in page coordinates normalized to 0–1000, followed by the block's content. Text blocks carry the transcription, image blocks pair the box with a short description, and chart blocks carry an HTML table of the extracted data points. The cards give this one-page example, which also shows that the same placeholder syntax serves headings and paragraphs:[^lightonocr-3-1b-card][^lightonocr-3-4b-card]

```markdown
![title](80,70,920,140)
# Company report 2025

![text](80,175,920,225)
Revenue rose 20%.

![image](80,285,460,545)
A solar-powered factory.

![chart](540,285,920,545)
<table>
  <tr><th>Year</th><th>Revenue</th></tr>
  <tr><td>2024</td><td>€10M</td></tr>
  <tr><td>2025</td><td>€12M</td></tr>
</table>
```

This placeholder scheme differs from the LightOnOCR-2 bounding-box format recorded in [LightOnOCR](lightonocr.md), where boxes attach to embedded images only (`![image](image_N.png)x1,y1,x2,y2`); in LightOnOCR-3 grounding the box is the primary payload and every block is labelled. Both use 0–1000 normalized coordinates.[^lightonocr-3-1b-card]

## Label vocabulary

The cards define sixteen block labels plus a continuation marker:[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

| Label | Cards' definition |
|---|---|
| `text` | Ordinary body text and paragraphs |
| `title` | Document, section, or paragraph headings |
| `list` | Bulleted or numbered list content |
| `header` | Text in the page header |
| `footer` | Text in the page footer |
| `page_number` | Page-number regions |
| `footnote` | Footnote text |
| `caption` | Captions of figures, tables, or other visuals |
| `formula` | Mathematical formulas and equations |
| `code` | Code blocks or code-like text |
| `table` | Table regions and their content |
| `image` | Illustrations, photographs, and other image regions |
| `chart` | Charts, graphs, and plotted visual data |
| `header_image` | Image regions in page headers, such as logos |
| `footer_image` | Image regions in page footers |
| `aside_text` | Marginal or side text outside the main text flow |
| `+` suffix | Marks a continuation block, not a separate semantic class |

## Preprocessing

The 1B variant keeps LightOnOCR-2's rendering guidance: 200 DPI with a 1,540-pixel target longest dimension. The 0.8B and 4B variants require 400 DPI with a 2,048-pixel target longest dimension. All three cards ask for the aspect ratio to be preserved so that text geometry and therefore the emitted boxes stay consistent.[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

## Limits and trust

The evidence is three vendor model cards, all **reported** and none reproduced locally. Consequential coverage gaps are:[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

- No benchmark results, dataset names, or comparison tables appear in any of the three cards, so the "significant improvements in speed and transcription quality" and the 4B's "most accurate" positioning are unquantified vendor claims.
- No parameter counts beyond the model names, no architecture diagrams, training data, compute, or ablations. The cards' citation block still points at the LightOnOCR-2 paper (arXiv 2601.14251, key `lightonocr2_2026`), so the grounding, image-description, and chart-extraction outputs have no first-party evaluation document behind them.
- Prompt behavior is tuned instruction-following, not a constrained decoder; the cards document no schema validation for the emitted placeholders or HTML tables.
- Language coverage is undocumented for the family. Only the 0.8B card's frontmatter declares `language: en`; the 1B and 4B cards declare none, and the LightOnOCR-2 paper's European/Latin-script scope in [LightOnOCR](lightonocr.md) is not restated.
- The 1B card's capability bullet lists handwriting while the 0.8B and 4B bullets omit it, although the family paragraph says all variants carry the same features. The per-variant handwriting scope is therefore unclear from these cards.
- The `lightonocr3_logo.png` referenced by all three cards is remotely hosted and was not inspected; no weights, processor code, or inference run were available locally.

## Relationships

- **Supersedes:** [LightOnOCR](lightonocr.md) as the generation to deploy — the 1B variant keeps that architecture and the LightOnOCR-2 paper remains the source for its architecture, training recipe, and benchmark evidence.
- **Uses:** a Qwen3.5 vision-language architecture in the 0.8B and 4B variants. [OvisOCR3](ovisocr3.md) is also Qwen3.5-based at 0.8B, but neither card relates the two projects, so this is synthesis rather than a stated dependency.
- **Operationalized by:** [LightOnOCR-3 deployment](lightonocr-3-deployment.md) for per-variant loaders, serving flags, and rendering settings.
- **Compared with:** other single-prompt page-to-Markdown systems in [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md).

[^lightonocr-3-1b-card]: LightOn, [*LightOnOCR-3-1B model card*](../raw/lightonai-LightOnOCR-3-1B.md) (accessed 2026-10-25), §§ "About LightOnOCR-3", "Highlights", "Model Variants", "Prompt Modes", "Rendering and Preprocessing Tips". The logo image is remote and was not inspected.
[^lightonocr-3-0-8b-card]: LightOn, [*LightOnOCR-3-0.8B model card*](../raw/lightonai-LightOnOCR-3-0.8B.md) (accessed 2026-10-25), §§ "About LightOnOCR-3", "Highlights", "Model Variants", "Prompt Modes", "Rendering and Preprocessing Tips"; frontmatter declares `language: en` and an added `pdf` tag.
[^lightonocr-3-4b-card]: LightOn, [*LightOnOCR-3-4B model card*](../raw/lightonai-LightOnOCR-3-4B.md) (accessed 2026-10-25), §§ "About LightOnOCR-3", "Highlights", "Model Variants", "Prompt Modes", "Rendering and Preprocessing Tips", including the reported 1,433 vs 1,158 tokens-per-page grounding overhead.
