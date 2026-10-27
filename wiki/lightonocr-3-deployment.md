---
type: Software
title: LightOnOCR-3 deployment
description: LightOnOCR-3 serves through two runtime paths — LightOnOcr Transformers classes for the 1B variant and Qwen3.5 classes with thinking disabled for the 0.8B and 4B variants — with variant-specific loader versions, vLLM flags, and PDF render targets.
tags: [ocr, document-parsing, deployment, vllm, transformers, qwen3-5]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-27T10:11:56Z }
stale_after: 2027-01-25
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

# LightOnOCR-3 deployment

LightOnOCR-3 exposes one serving interface — a chat conversation whose user turn carries one page image and either no prompt or the literal prompt `grounding` — but two runtime paths. The 1B variant loads through the `LightOnOcr` Transformers classes that already serve LightOnOCR-2, so an existing deployment changes only the checkpoint identifier. The 0.8B and 4B variants are Qwen3.5 checkpoints: they load through `Qwen3_5ForConditionalGeneration` and `AutoProcessor`, require thinking to be disabled, and need different vLLM flags. These are model-card instructions from three vendor cards; none were executed or verified locally.[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

## Runtime matrix

| Aspect | 0.8B and 4B | 1B |
|---|---|---|
| Transformers classes | `Qwen3_5ForConditionalGeneration`, `AutoProcessor` | `LightOnOcrForConditionalGeneration`, `LightOnOcrProcessor` |
| Stated Transformers requirement | ≥ 5.2, checkpoint saved with 5.5.4; the example pins `transformers>=5.5.4` | "available in Transformers since v5"; the example does not pin a version |
| Thinking mode | Disabled; the cards state training and evaluation used thinking disabled, which is the chat-template default | Not exposed; the card documents no thinking flag |
| vLLM flags | `--trust-remote-code --default-chat-template-kwargs '{"enable_thinking": false}'` | `--limit-mm-per-prompt '{"image": 1}' --mm-processor-cache-gb 0 --no-enable-prefix-caching` |
| Example device and dtype | `bfloat16` with `device_map="auto"` | `float32` on MPS, otherwise `bfloat16`, inputs moved to the selected device |
| Example sampling | `do_sample=True, temperature=0.2`, `max_new_tokens=1024` | Greedy default from `generate`, `max_new_tokens=1024` |
| PDF render target | 400 DPI, then 2,048 px longest edge | 200 DPI, 1,540 px longest edge |

The two paths also differ in how the prompt is attached. The 1B example builds the conversation as an image plus an optional text part, while the 0.8B/4B examples pass `enable_thinking=False` into `apply_chat_template`, so the thinking switch is applied at template time rather than in the payload. In both cases the prompt is omitted entirely for transcription mode instead of being replaced by an empty string part.[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

## vLLM client

All three cards use the same OpenAI-compatible request shape against a locally served endpoint: one `image_url` part carrying a base64 data URL, an optional `text` part holding `grounding`, and `max_tokens: 4096` with `temperature: 0.2` and `top_p: 0.9`. The 1B client renders the PDF page at scale `2.77` (200/72); the 0.8B and 4B clients render at `400/72` and then call `thumbnail((2048, 2048))` to apply the longest-edge cap.[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]

The cards point to the LightOnOCR GitHub repository for a minimal vLLM client, a CLI, and a viewer, plus code to reproduce the authors' benchmarks. That repository is not part of this source bundle and was not inspected, so its tooling behavior is unverified.[^lightonocr-3-1b-card]

## Operational notes and limits

- The variants differ in caching posture: the 1B flags disable the multimodal-processor cache and prefix caching while limiting one image per prompt, and the 0.8B/4B flags enable remote code and set the chat-template kwarg. The cards do not explain why the flag sets diverge, and no throughput measurement accompanies either configuration in the cards. Separate vendor measurements under benchmark settings are summarized in [LightOnOCR-3 evaluation](lightonocr-3-evaluation.md).[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]
- Only two prompts are supported; the cards state other instructions are out of distribution, so a serving stack should not expose a free-form instruction field.[^lightonocr-3-1b-card][^lightonocr-3-4b-card]
- Grounding is reported to add roughly 25% output tokens (1,433 vs 1,158 per page on average, 4B), which affects token budgets and latency planning but is not broken down per variant.[^lightonocr-3-4b-card]
- Sampling settings appear only inside examples (`do_sample=True, temperature=0.2` and, for vLLM, `top_p=0.9`); the cards do not present them as required decoding parameters, and no determinism or accuracy comparison across settings is given.[^lightonocr-3-0-8b-card][^lightonocr-3-4b-card]
- The 1B path's stated compatibility ("since v5") is looser than the 0.8B/4B pin (≥ 5.5.4), so a single environment serving both variants must satisfy the stricter requirement. This follows from the two cards' text rather than from an executed install.[^lightonocr-3-1b-card][^lightonocr-3-0-8b-card]

## Relationships

- **Depends on:** [LightOnOCR-3](lightonocr-3.md) for the family's variants, prompt modes, output format, and label vocabulary.
- **Supersedes:** the LightOnOCR-2 deployment guidance recorded in [LightOnOCR](lightonocr.md) for the 1B checkpoint identifier and the 0.8B/4B runtime path; the LightOnOCR-2 flags remain the reference for that earlier generation.

[^lightonocr-3-1b-card]: LightOn, [*LightOnOCR-3-1B model card*](../raw/lightonai-LightOnOCR-3-1B.md) (accessed 2026-10-25), §§ "Usage with Transformers", "Usage with vLLM", "Rendering and Preprocessing Tips". The referenced GitHub repository is not in the local bundle.
[^lightonocr-3-0-8b-card]: LightOn, [*LightOnOCR-3-0.8B model card*](../raw/lightonai-LightOnOCR-3-0.8B.md) (accessed 2026-10-25), §§ "Usage with Transformers", "Usage with vLLM", "Rendering and Preprocessing Tips".
[^lightonocr-3-4b-card]: LightOn, [*LightOnOCR-3-4B model card*](../raw/lightonai-LightOnOCR-3-4B.md) (accessed 2026-10-25), §§ "Usage with Transformers", "Usage with vLLM", "Rendering and Preprocessing Tips", "Prompt Modes" (token overhead).
