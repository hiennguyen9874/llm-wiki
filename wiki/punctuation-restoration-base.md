---
type: Concept
title: Punctuation Restoration (base, 307M)
description: Apache-2.0 mmBERT-based 307M token classifier that restores full stops, commas, question marks, colons, and dashes in 88 languages on unpunctuated ASR text, with self-reported F1 ahead of punctuate-all on FLORES and TED talks and behind it on Europarl.
tags: [stt, punctuation, punctuation-restoration, asr-postprocessing, multilingual, onnx]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:57:00Z }
stale_after: 2027-04-13
sources:
  - id: punctuation-restoration-base-card
    resource: ../raw/punctuation-restoration-base.md
    kind: documentation
    title: Punctuation Restoration (base, 307M) model card
---

Punctuation Restoration (base, 307M) is an Apache-2.0 token classifier from Horizon Labs, built on mmBERT-base, that inserts `.`, `,`, `?`, `:`, or `-` (or nothing) after each word of unpunctuated text in 88 languages, including the all-lowercase output of many ASR systems (**Reported**).[^punctuation-restoration-base-card] It restores punctuation only and leaves casing and words unchanged, so a separate step is still needed where casing matters (**Synthesis**). The card's own comparison puts it ahead of the 12-language punctuate-all model on FLORES and TED talks and behind it on Europarl, the set punctuate-all was trained on. Every figure is self-reported and was not reproduced (**Reported**).[^punctuation-restoration-base-card]

## Scope and labels

- After each word it predicts one of `.`, `,`, `?`, `:`, `-`, or no mark. This is the same label set as [oliverguhr fullstop-punctuation-multilang-large](https://huggingface.co/oliverguhr/fullstop-punctuation-multilang-large) and kredor punctuate-all, so the card presents it as a drop-in for the `deepmultilingualpunctuation` package (**Reported**).[^punctuation-restoration-base-card]
- Chinese and Japanese need no word segmentation. The helper `punctuate.py` writes full-width marks there, `।` for Hindi and Bengali, `، ؟` for Arabic script, `;` for Greek questions, and `። ፣` for Amharic (**Reported**).[^punctuation-restoration-base-card]
- Not restored: `!`, `;` (except the Greek output mapping above), quotes, brackets, and Spanish inverted marks (**Reported**).[^punctuation-restoration-base-card]
- A smaller sibling, punctuation-restoration-small (140M, Apache-2.0, 88 languages), is named in the card but not captured here (**Reported**).[^punctuation-restoration-base-card]

## Usage paths

- **Helper:** `Punctuator("Horizon-Labs/punctuation-restoration-base")` from the downloaded `punctuate.py`; long texts are processed in overlapping chunks (code fence **Observed**; helper behavior **Reported**).[^punctuation-restoration-base-card]
- **Drop-in:** `PunctuationModel` from `deepmultilingualpunctuation`, space-separated languages only. That package needs transformers 4.x because it passes `grouped_entities`, which transformers 5 removed (**Observed** in the card's fence and note).[^punctuation-restoration-base-card]
- **Plain transformers:** `pipeline("token-classification")`. A word's label is the label of its last token, and `"0"` means no mark (**Observed**).[^punctuation-restoration-base-card]
- **Browser:** transformers.js with `dtype: "q8"` (**Observed**).[^punctuation-restoration-base-card]
- **Quantized ONNX:** `onnx/model_quantized.onnx` (int8 embeddings, 641 MB) predicts the same label as fp32 for 99.93% of tokens on held-out text (**Reported**).[^punctuation-restoration-base-card]

## Evaluation

Metric: micro-F1 over the five marks, where a predicted mark counts only if it is the correct mark at the correct position, averaged over languages. Every model gets the same input: the paragraph with `. , ? : ; ! -` removed, once cased and once lowercased. The test sets are FLORES-200 devtest (about 280 paragraphs per language), TED talks (TED2020 via OPUS; 200 paragraphs in each of 25 languages), and Europarl (200 paragraphs in each of 12 languages). Europarl was used to train punctuate-all and the fullstop models (**Reported**).[^punctuation-restoration-base-card]

| Model | Licence | Languages | FLORES 12 EU (cased / lower) | FLORES 88 (cased / lower) | TED 25 (cased / lower) | Europarl 12 (cased / lower) |
| --- | --- | --- | --- | --- | --- | --- |
| **This model (307M)** | Apache-2.0 | 88 | 0.922 / 0.891 | 0.847 / 0.804 | 0.795 / 0.722 | 0.881 / 0.839 |
| punctuation-restoration-small (140M) | Apache-2.0 | 88 | 0.920 / 0.883 | 0.842 / 0.796 | 0.786 / 0.706 | 0.878 / 0.830 |
| punctuate-all | MIT | 12 | 0.879 / 0.873 | 0.667 / 0.657 | 0.664 / 0.654 | 0.885 / 0.884 |
| fullstop-punctuation-multilang-large | MIT | 4 | 0.841 / 0.838 | 0.669 / 0.663 | 0.648 / 0.642 | 0.826 / 0.824 |
| fullstop-punctuation-multilingual-base | MIT | 6 | 0.846 / 0.829 | 0.668 / 0.652 | 0.657 / 0.636 | 0.826 / 0.822 |
| xlm-roberta_punctuation_fullstop_truecase | Apache-2.0 | 47 | — / 0.818 | — / 0.689 | — / 0.643 | — / 0.751 |
| punct_cap_seg_47_language | Apache-2.0 | 47 | — / 0.565 | — / 0.448 | — / 0.510 | — / 0.504 |

- The two 1-800-BAD-CODE models were scored only on lowercased input, through re-alignment of their output. The card says about 2% of words (truecase model) and 11% (punct_cap_seg) could not be aligned and count as "no mark", which lowers their scores (**Reported**).[^punctuation-restoration-base-card]
- The 88-language FLORES column also scores punctuate-all and the fullstop models on languages they were not built for, so that column mainly shows coverage (**Synthesis**).
- Per mark, FLORES cased F1 is `.` 0.948, `,` 0.730, `?` 0.777, `:` 0.451, and `-` 0.187. On TED cased input, `:` is 0.599 and `-` is 0.075 (**Reported**).[^punctuation-restoration-base-card]
- Per-language FLORES rows are in a collapsed table in the card. Their mean, computed for this page, matches the headline 0.847 cased and 0.804 lowercased (**Reproduced** arithmetic on the card's numbers only).[^punctuation-restoration-base-card]

## Training data and method

- Data: 1,168,626 text windows (119M words) in 88 languages from FineWeb-2 and FineWeb (ODC-BY). Labels come from the text's own full stops. Windows hold 1–4 snippets of up to 230 words, 30% are cut mid-sentence, and 70% of inputs are lowercased (**Reported**).[^punctuation-restoration-base-card]
- Spoken-style v1.1 adds 49,144 windows of edited everyday-speech transcripts in 69 languages. The card says a model named "Qwen3.8-27B" (Apache-2.0) wrote them; the name is copied as printed and was not checked. Transcripts sharing a sentence with any test set were removed (**Reported**).[^punctuation-restoration-base-card]
- Label normalisation: `!`, `;`, `…`, and script full stops count as `.`; `，、،` as `,`; `？؟` (and Greek `;`) as `?`; a free-standing dash as `-`; a `.` before a lowercase word counts as no mark (**Reported**).[^punctuation-restoration-base-card]
- Method: mmBERT-base token classification, one label per word on its last token, 1 epoch, learning rate 3e-5. The checkpoint was chosen on held-out web text, not on the test sets (**Reported**).[^punctuation-restoration-base-card]

## Limitations

- Lowercased input scores lower than cased, because capitals mark sentence starts (**Reported**).[^punctuation-restoration-base-card]
- `:` and especially `-` are much less reliable than `.`, `,`, and `?` (**Reported**).[^punctuation-restoration-base-card]
- Disfluent speech (fillers, false starts, repetitions) is harder, and punctuation conventions vary by writer. Thai, Lao, Khmer, Burmese, and Tibetan are unsupported, and low-resource or out-of-set languages score lower (**Reported**).[^punctuation-restoration-base-card]
- On Europarl, which punctuate-all was trained on, this model is slightly behind when cased and clearly behind when lowercased (**Reported**).[^punctuation-restoration-base-card]
- The authors chose the protocol and the comparison set, and the card is their own publication. Its comparison is not independent verification (**Synthesis**).

## Contradictions

- The v1.1 changelog reports TED-talk F1 of .796 cased, .723 lowercased, and `:` .605 across two training seeds. The evaluation tables report 0.795 and 0.722 for TED, and `:` 0.599 cased and 0.519 lowercased. The card does not say which run the tables show. Neither value is chosen (**Observed** by static cross-check of the card's own numbers).[^punctuation-restoration-base-card]

## Coverage and limits

- Inspected by static reading: the whole model card, covering frontmatter, prose, usage fences, both evaluation tables, the per-language table, training notes, changelog, and limitations (**Observed**).[^punctuation-restoration-base-card]
- Executed: arithmetic only, on the card's per-language table. No model was downloaded, no helper was run, and no benchmark was reproduced.
- Not captured: `punctuate.py`, the evaluation `code/` the card cites, the ONNX weights, the demo Space, the sibling small card, the compared models' own cards, and the FineWeb, FineWeb-2, FLORES, TED, and Europarl data. Claims that depend on them stay **Reported**.
- No revision is recorded. The newest changelog entry is v1.1 (2026-10-09). Re-ingest when the card or its revision changes.
- Licence: the card's frontmatter gives Apache-2.0. Its training sources are ODC-BY (**Reported**).[^punctuation-restoration-base-card]

## Relationships

- Related: [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md). That page lists `punctuate-all`, `fullstop`, and `pcs` as `--punc-model` shortcuts, and this model is not among them (**Synthesis**).
- Complements: it restores punctuation only, so casing needs a separate truecasing step, such as the options on the same CrispASR page (**Synthesis**).
- Context: [ASR/STT Model Survey](asr-stt-model-survey.md) compares which ASR outputs arrive punctuated or lowercased, which is the case this model addresses (**Synthesis**).

[^punctuation-restoration-base-card]: [Punctuation Restoration (base, 307M) model card](../raw/punctuation-restoration-base.md) — locators: frontmatter (`license`, `language`, `base_model`, `datasets`, `tags`, `widget`); title and intro paragraphs (label set, 88 languages, mmBERT-base, ONNX, transformers.js Space); `Usage` fences (`punctuate.py` helper, `deepmultilingualpunctuation` drop-in, transformers pipeline, transformers.js `q8`); `Evaluation` paragraphs, the FLORES/TED/Europarl table, the per-mark table, and the collapsed per-language table; `Training` bullets (data, spoken-style v1.1, normalisation, model); `Changelog` v1.1 and v1.0; `Limitations` bullets.
