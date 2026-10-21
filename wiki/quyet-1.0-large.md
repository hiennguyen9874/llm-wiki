---
type: Concept
title: Quyet-1.0-Large
description: Gemma-4-31B-it-based decision model for typed choice, score, and boolean questions with package-managed probability calibration, English/Vietnamese tuning, and reported bf16 deployment on an 80 GB GPU.
tags: [llm, classification, decision-model, calibration, vietnamese]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T15:18:45Z }
stale_after: 2027-04-21
sources:
  - id: quyet-large-card
    resource: ../raw/Quyet-1.0-Large.md
    kind: model-card
    title: Quyet-1.0-Large model card capture
---

Quyet-1.0-Large maps a text, JSON, or conversation state plus typed questions to decisions and probabilities, rather than presenting a free-form dialogue-generation API. The card describes a merged rank-16 LoRA fine-tune of `google/gemma-4-31B-it`, with option-letter next-token readout and calibrated temperatures supplied by the `quyet` package (**Reported**).[^quyet-large-card] In a voice loop, it is a candidate adjunct for intent routing, urgency flags, or ordered ratings after STT, not an established replacement for the conversational reply generator (**Synthesis**). Calibration quality, Vietnamese accuracy, and realtime suitability remain **Unverified**.

## Identity and model envelope

The following are card claims (**Reported**).[^quyet-large-card]

| Item | Card statement |
| --- | --- |
| Publisher / checkpoint | Chinh Nguyen; `chinhnc/Quyet-1.0-Large` |
| Family | Quyet 1.0: Large, Medium, Small, Small-EN, Tiny; sibling specifications are not supplied |
| Parameters | 31.3B total, 30.7B text |
| Languages | English; also tuned for Vietnamese; other languages claimed to work with lower accuracy |
| Input budget | State up to 6,000 tokens within an 8,000-token prompt |
| Weight size | 62.5 GB bf16; not a measurement of peak runtime VRAM |
| License | Apache-2.0; card requires retaining NOTICE when redistributing the model or derivatives |
| Source identity | Citation names the Hugging Face checkpoint URL and year 2026; exact publication/capture date and immutable upstream revision are unavailable |

## Typed decisions and truncation

- `choice`: choose one label; answer includes the choice, confidence, and label probabilities.
- `score`: ordered criteria; answer includes the expected level, probabilities, and legend.
- `noul`: boolean true/false question; answer is P(true).
- One or more questions per state; at most 10 options per question. The card says answers follow the TypeSafe `/v1/systemone` shape, not that this checkpoint ships an HTTP server implementing that endpoint.
- Only the state is truncated: conversation lists retain the most recent turns; other states retain their beginning. Do not assume an overlong question definition is automatically shortened.

These schemas and policies are **Reported**; the final truncation implication is **Synthesis** from the stated state-only rule.[^quyet-large-card]

## Inference mechanism and package dependency

The model reads next-token probabilities for option letters (`A`, `B`, …) after a fixed decision prompt. The package builds that prompt and applies calibrated temperatures. Prompt version 2 removes the system message and closing line from the trained prompt, serializes structured states as compact JSON, and is claimed to save about 68 input tokens per decision; temperatures were refit for that prompt (**Reported**).[^quyet-large-card]

The card says the checkpoint also loads with Transformers and serves with vLLM as a standard Gemma-4-31B-it-architecture checkpoint. However, the decision prompt and temperatures live in the package and `quyet_config.json`; generic checkpoint loading alone does not establish equivalent calibrated decisions (**Reported** compatibility; **Synthesis** equivalence warning).[^quyet-large-card]

## Documented usage and deployment

Install `quyet` with `pip install quyet`. The card's `quyet.load` / `predict` pattern, shortened to two questions below, is documentation only; it was not executed (**Reported**).[^quyet-large-card]

```python
import quyet

m = quyet.load("chinhnc/Quyet-1.0-Large")
r = m.predict(
    {"message": "Please close my card, I lost it yesterday."},
    {
        "intent": {
            "type": "choice",
            "instructions": "What does the customer want?",
            "criteria": {"cancel": "close the card", "limit": "change the limit", "other": None},
        },
        "urgent": {"type": "noul", "instructions": "The request is urgent."},
    },
)
print(r["answers"])
```

Loading downloads weights from Hugging Face. The card reports bf16 inference on one 80 GB GPU, or multiple GPUs using `device_map="auto"` and the `quyet[multi-gpu]` install extra. It supplies no package/runtime version pins, measured peak VRAM, latency, throughput, concurrency, streaming protocol, quantization, CPU, or GGUF results (**Reported** deployment; **Observed** evidence gaps in the capture).[^quyet-large-card]

## Voice-agent relationship and evaluation limits

- Related to the [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md): consider structured decisions alongside the conversational LLM path, not as speech synthesis or a spoken reply. This is a proposed relationship, not a documented integration (**Synthesis**).[^quyet-large-card]
- The card's intent/urgency/mood example motivates routing and classification experiments, but provides no accuracy table, calibration metric, held-out data, calibration dataset, temperature values, uncertainty estimate, training recipe beyond the merged LoRA rank, or Vietnamese benchmark. Treat “calibrated” as a publisher claim rather than evidence that confidence thresholds transfer to noisy ASR transcripts (**Observed** omissions; **Synthesis** evaluation caution).[^quyet-large-card]

## Coverage and trust limits

- **Inspected:** the entire single Markdown capture, including YAML, introductory model table, `How to use` code and prose, Credits, Citation, and License. Static text inspection only; no installation, package import, download, model/server execution, API request, or benchmark reproduction.
- **Uninspected dependencies:** `quyet` implementation and its prompt/temperature handling; `quyet_config.json`; model weights/tokenizer/architecture configuration; `LICENSE` and `NOTICE` referenced by the card. They were not supplied with this single-file capture, so implementation behavior and full redistribution terms were not independently checked.
- **External context not fetched:** the Google base-model card/weights, Hugging Face checkpoint repository, `quyet.ai` homepage/live demo, Transformers/vLLM compatibility implementation, and TypeSafe schema. The capture contains no material image, audio, local include, test suite, or benchmark attachment.
- **Excluded:** promotional demo invitation, support contact, and verbatim BibTeX; bibliographic identity and licensing obligation are retained. No sensitive values were found in the inspected capture.
- `stable` denotes a complete synthesis of this card, not verified calibration or deployed voice-loop performance. Upstream implementation/evaluation would be a new evidence contribution, not evidence already inspected.

[^quyet-large-card]: [Quyet-1.0-Large model card capture](../raw/Quyet-1.0-Large.md) — locators: YAML (`license`, `library_name`, `base_model`, `base_model_relation`); opening paragraph (typed questions, family, publisher); opening specification table (architecture, parameters, languages, input, weights, license); `## How to use` → installation fence and `quyet.load` / `m.predict` / `r["answers"]` example; paragraphs beginning “Runs in bf16” (GPU placement, letter readout, package/config dependency, prompt v2) and “Answers follow” (schemas, option limit, truncation); `## Credits`; `## Citation` (`quyet2026`, upstream URL, author, year); `## License` (NOTICE retention).
