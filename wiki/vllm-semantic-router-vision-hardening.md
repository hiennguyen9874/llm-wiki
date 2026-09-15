---
type: Concept
title: vLLM Semantic Router Vision Signal Hardening
description: Turning vision embeddings into trustworthy routing signals by enforcing reference parity across the Rust/Candle vision path, with pooling, normalization, and preprocessing fixes.
tags: [vllm, semantic-router, multimodal, vision-encoder, routing]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: vsr-vision-hardening
    resource: ../raw/2026-05-28-vllm-sr-vision-encoder-hardening/index.md
    title: "From Text to Multimodal Routing: Hardening Vision Signals in vLLM Semantic Router"
---

vLLM Semantic Router (VSR) extends its Signal-Decision routing fabric from text prompts to full multimodal requests, and this hardening arc shows that a deployed `multi-modal-embed-small` vision path was inverted against its PyTorch reference because of Rust/Candle pooling, normalization, and preprocessing drift rather than encoder capacity[^vsr-vision-hardening].

## Signal-Decision architecture

- VSR extracts independent signals, composes them into decisions with priority and boolean logic, and maps decisions to plugins or model references, enabling policies like "security-sensitive code review gets a stronger reasoning model and jailbreak checks" instead of fixed domain classification[^vsr-vision-hardening].
- Iris introduced this Signal-Decision move beyond a fixed domain classifier, with intent, keywords, embeddings, safety, PII, semantic cache, and plugins participating in routing[^vsr-vision-hardening].
- Athena extended the same direction toward a system-level intelligence layer for mixture-of-models and agentic deployments[^vsr-vision-hardening].
- Multimodal routing keeps that shape but changes the unit of analysis from text prompt to full request, where generic text plus decisive image evidence determines the route[^vsr-vision-hardening].

| Request evidence | Text-only router sees | Multimodal router should see |
| --- | --- | --- |
| "Summarize this" + passport image | Generic summarization | Identifier document, PII risk, restricted handling |
| "What does this show?" + chest X-ray | Vague visual question | Clinical image, medical-domain policy, capable VLM target |
| "Find the bug" + code screenshot | Coding request | Code artifact, possible secret leakage, security review path |
| Medical prompt + unrelated car image | Medical text | Out-of-domain visual evidence, clarification or rejection path |

Table values directly from source probe framing[^vsr-vision-hardening].

## Why vision correctness is a control-plane invariant

- The image embedding becomes a typed signal composed with text intent, PII, jailbreak, domain, semantic similarity, plugins, and model selection, moving VSR from prompt-level routing to request-level policy[^vsr-vision-hardening].
- A weak classifier usually produces uncertainty, while an inverted vision signal produces confidence in the wrong direction, which can be worse than having no image signal[^vsr-vision-hardening].
- Reference parity is therefore framed as a control-plane invariant: the deployed signal path must mean the same thing as the reference model path, or the decision layer composes the wrong evidence while leaving a clean audit trail for the wrong decision[^vsr-vision-hardening].

## Failure symptom

- On an 11-image probe across three verticals and 21 candidate labels, the deployed `multi-modal-embed-small` (mmes) path ranked the wrong vertical highest on 9 of 11 images, an 82% inversion rate[^vsr-vision-hardening].
- Medical X-rays scored closer to semiconductor candidates than medical candidates, and identifier documents did not reliably land near identifier anchors[^vsr-vision-hardening].
- The production surface was the image-modality routing work around `multi-modal-embed-small`, including the E2E routing profile from `vllm-project/semantic-router` PR #1881; the gap became visible once real images flowed through the Candle binding path[^vsr-vision-hardening].
- Decisive reference check on the same passport fixture and conceptual pipeline: PyTorch reference cosine **0.7204** against the passport anchor versus Candle-binding path **0.1576**, a 5–8x magnitude gap that reframed the issue from model selection to production-path divergence[^vsr-vision-hardening].

## Encoder upgrade ruled out

- SigLIP2-base scored 10/10 on the same 21-candidate probe[^vsr-vision-hardening].
- SigLIP-base through Hugging Face Transformers scored 10/10[^vsr-vision-hardening].
- `multi-modal-embed-large` (mmEL), whose vision tower is based on SigLIP2, scored 10/10[^vsr-vision-hardening].
- The mmes model card loaded directly through the PyTorch reference path also scored 10/10, eliminating encoder capacity as the root cause[^vsr-vision-hardening].
- Larger SigLIP2-so400m showed stronger out-of-distribution rejection in the probe, suppressing an accidentally included car-engine image more aggressively than smaller variants; noted as possible future defensive-routing value when memory allows, not the production bug fix[^vsr-vision-hardening].

## Three root causes and fixes

Drift came from Candle-path implementation details, not model weights[^vsr-vision-hardening]:

1. **Wrong pooling head.** `SigLIPVisionEncoder::forward` in `candle-binding/src/model_architectures/embedding/multimodal_embedding.rs` did BERT-style mean + Linear + tanh pooling, while SigLIP uses attentional probe pooling with multi-head attention. PR #1927 mirrors SigLIP multi-head attention pooling in Candle binding[^vsr-vision-hardening].
2. **Incomplete normalization.** The Go image loader produced CHW float32 pixels in `[0, 1]`, while SigLIP expects per-channel `(x - 0.5) / 0.5`. PR #1928 applies that normalization in the Rust encoder path[^vsr-vision-hardening].
3. **Residual preprocessing drift.** The old Go-side resize used a 4-tap bilinear implementation, while the PyTorch reference uses PIL-style preprocessing through `SiglipProcessor`. PR #1943 moves decode, resize, and CHW float32 conversion into Rust using the `image` crate with Catmull-Rom filtering to approximate PIL bicubic + antialias behavior[^vsr-vision-hardening].

This is presented as a cross-language serving-stack failure: Go, Rust FFI, Candle implementation, and PyTorch reference can each look reasonable while mismatching end to end[^vsr-vision-hardening].

## Validation status — branch-stack, not released

- Numbers below are branch-stack measurements for PRs #1927, #1928, and #1943; until all three merge they validate the proposed hardening path rather than released production behavior[^vsr-vision-hardening].
- Three-vector isolation on canonical passport fixture `inrule_identifier_passport.jpg`:

| Comparison | Cosine | Max abs diff | What it isolates |
| --- | --- | --- | --- |
| Python vs Candle-PIL | **0.999989** | 0.000911 | Model-forward only |
| Candle-PIL vs Candle-Go | **0.999916** | 0.001992 | Preprocessing only |
| Python vs Candle-Go | **0.999902** | 0.002120 | Full branch-stack pipeline |

[^vsr-vision-hardening]

- First row shows the Rust model-forward path matching PyTorch at fp32-level noise; remaining drift lived in preprocessing, motivating moving preprocessing across the FFI boundary[^vsr-vision-hardening].
- Across a 20-image corpus covering identifier, ambient, code, adversarial, and out-of-distribution examples: cosine min **0.999557**, mean **0.999919**, max **0.999978**; **20/20 images at cosine >= 0.999 vs PyTorch reference**; pre-fix preprocessing cosine on the canonical fixture was **0.990145**[^vsr-vision-hardening].
- Durable method lesson: compare the production embedding path against the model card's reference loader first, split model-forward drift from preprocessing drift, then make production use the same preprocessing semantics in tests and serving[^vsr-vision-hardening].

## What trustworthy vision unlocks

Once the vision path matches reference, image and text evidence participate in the same fabric rather than routing image requests to an image model as a side path[^vsr-vision-hardening]:

| Combined signal pattern | Example decision |
| --- | --- |
| Clinical text + clinical image + PHI/PII signal | Route to protected medical VLM path with privacy plugins |
| Generic text + identifier image | Block, redact, or route to identity-document handling before invocation |
| Code/security prompt + code screenshot | Route to security-specialized model, keep jailbreak checks on |
| In-domain text + out-of-domain image | Ask for clarification or reject image evidence instead of forcing a bad route |

[^vsr-vision-hardening]

## Performance and demo context

- Classifier signals can run concurrently through `runSignalDispatchers`, so wall-clock latency is bounded by the slowest enabled classifier rather than the sum; a representative CPU trace completes the full classification decision in roughly 1.3 seconds[^vsr-vision-hardening].
- The public demo at `shrader.dev` demonstrates the text-routing policy shape — domain relevance checks, privacy-sensitive routing, blocked outcomes before invocation — before images are added; the multimodal path is intended as the same policy engine with a larger evidence surface, including replay, metrics, and debugging visibility[^vsr-vision-hardening].

## Next steps

- Land and review hardening PRs #1927, #1928, #1943, then keep the validation corpus in the loop as multimodal routing evolves[^vsr-vision-hardening].
- Make reference-driven checks a normal part of VSR multimodal serving[^vsr-vision-hardening].
- Expose image-derived signals in the same decision layer as text signals; keep multimodal decisions visible in replay, metrics, and debugging; make model selection aware of policy fit and modality capability; preserve high-fidelity inspection for PII and jailbreak; extend the fabric toward agentic workflows where tool calls, memory writes, and invocations route through one decision layer[^vsr-vision-hardening].
- Project repository: `vllm-project/semantic-router`[^vsr-vision-hardening].

## Relationships

- Related to [vLLM Multimodal Inputs](vllm-multimodal-inputs.md) — that concept covers the vLLM serving path for image/video/audio inputs, while this concept covers the Semantic Router control-plane path that turns image evidence into routing signals before serving-model invocation.
- Related to [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — processor replay and normalization there is serving-side context for the same class of preprocessing-parity risk fixed here on the router side.
- Related to [vLLM Disaggregated Encoder](vllm-disaggregated-encoder.md) — disaggregated vision encoding scales serving encoders, while VSR vision hardening makes router-side embeddings trustworthy enough to select those downstream paths.

## Coverage limits

- Ten local `assets/*.png` diagrams were enumerated but not pixel-inspected; numerical and architectural claims above come from the `index.md` prose and tables[^vsr-vision-hardening].
- PRs #1881, #1927, #1928, and #1943, the `shrader.dev` demo, and linked GitHub code paths were cited as locations but their live code and demo behavior were not inspected[^vsr-vision-hardening].
- Accuracy numbers are branch-stack validation, not merged-release behavior; corpus composition beyond the stated identifier/ambient/code/adversarial/OOD split and fixture licensing are outside the verified scope[^vsr-vision-hardening].

[^vsr-vision-hardening]: From Text to Multimodal Routing: Hardening Vision Signals in vLLM Semantic Router — `../raw/2026-05-28-vllm-sr-vision-encoder-hardening/index.md`, covering Signal-Decision/Iris/Athena framing, request-evidence table, 9/11 inversion symptom and 0.7204 vs 0.1576 reference gap, encoder-elimination probes, pooling/normalization/preprocessing fixes in PRs #1927/#1928/#1943, three-vector and 20-image validation, combined-signal patterns, `runSignalDispatchers` concurrency and demo context, and next-step architecture.
