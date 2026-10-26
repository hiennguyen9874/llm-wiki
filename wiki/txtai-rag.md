---
type: Concept
title: txtai LLM generation and RAG references
description: Generation adapters, retrieval-context construction, prompt and streaming contracts, and post-hoc single-context reference selection.
tags: [rag, ml, txtai, llm, citations]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:14:52Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac4
    title: txtai repository
---

**Observed:** txtai's `RAG` composes a retriever or similarity pipeline, context selection, prompt formatting, and a generative/extractive/custom model. Its optional `reference` output selects one context item by post-generation similarity. **Synthesis:** that is a useful attribution heuristic, not evidence-span grounding or verification that the answer follows from the referenced text.[^txtai-repo]

## Generation abstraction

`LLM` delegates to a `Generation` adapter. `GenerationFactory` detects LiteLLM, LiteRT, llama.cpp, OpenCode, or Transformers from model/configuration cues; custom generation implementations can be resolved as trusted Python classes. The shared layer formats messages, normalizes backend response shapes, cleans output, and handles streaming. These adapters are not an identical inference protocol: backend context limits, token parameters, GPU behavior, message handling, and failure/retry behavior differ.[^txtai-repo]

**Observed:** `LLM` defaults to `ibm-granite/granite-4.0-350m`; its call defaults include `maxlength=512`, `stream=False`, and role auto-detection. Role auto-detection uses model chat status plus known instruction-prefix markers. Thinking-text stripping uses textual patterns and defaults differently for streaming versus nonstreaming. It is output processing, not a guarantee that no hidden reasoning text can surface through every backend.[^txtai-repo]

Examples of adapter-specific limits: Hugging Face streaming uses a threaded iterator with a timeout; llama.cpp applies context/GPU defaults with a conditional context fallback; LiteRT may retry engine creation on CPU; OpenCode delegates to an external server/session. None was exercised during ingestion.[^txtai-repo]

## RAG retrieval and context construction

- Default context count is **3**, minimum score **0**, minimum token threshold **0**, separator a space, and template `"{question} {context}"`.
- Inputs can distinguish retrieval query from model question. The retriever can be an embeddings database, `Similarity` over supplied texts, or a compatible callable.
- Search-mode results must carry `id`, `text`, and `score`; ordinary embeddings search therefore needs content enabled. The implementation assumes that shape rather than validating it up front.
- `+required` / `-prohibited` query tokens become case-insensitive substring constraints. Score and minimum-length gates follow. With no tokenizer, the value used by `mintokens` is the original string, so its length counts characters rather than language-model tokens.
- Context takes the top-scoring matches; explicitly supplied texts are reordered into original source order when joined. A configured `system` prompt creates system/user messages. Otherwise the formatted template is passed directly.
- `RAG` is also exported under the compatibility name `Extractor`. The model can be `Questions` for extractive QA, `LLM`, or another compatible pipeline.[^txtai-repo]

## Answer and reference semantics

**Observed:** `default` outputs `(name, answer)`-style results, `flatten` returns answers, and `reference` adds a context identifier, adjusted for input tuple/dict/string shape. Snippet mode returns a context text when it literally contains the answer; it is not semantic span alignment. Streaming model results that are not lists bypass the normal list-output transformation.[^txtai-repo]

For `reference`, the pipeline obtains query terms where supported, concatenates them with the generated answer, and re-scores that text against the selected context chunks. It returns the identifier of the best-scoring chunk. If no context was selected, the reference remains `None`. The function assumes a nonempty score list when nonempty context is re-scored; the full backend-specific edge-case space was not tested.[^txtai-repo]

**Reported:** the RAG tutorial describes comparing the answer to context to find the “most likely reference.” **Observed:** the implementation matches that description; it does not compute sentence-level citations, quoted evidence, or entailment. This is a claim/mechanism qualification, not a contradiction with the tutorial's narrower wording. Sampled `testrag.py` assertions cover output/reference shape, prompt roles, supplied-text/search modes, and snippets; they were not executed or treated as proof of groundedness.[^txtai-repo]

## Relationships and limits

- **Depends on:** [Retrieval](txtai-retrieval.md) and [content persistence](txtai-persistence.md) for search-mode context.
- **Uses:** [Extraction/chunking](txtai-pipelines.md) output as retrieval and reference units.
- **Used by:** [API compatibility routes](txtai-api.md) and [workflow tasks](txtai-agents-workflows.md). Agent retrieval tools are a different orchestration path and do not automatically inherit this reference computation.
- **Part of:** [txtai](txtai.md); see [coverage](txtai-source-map.md).

Static code and sampled-test inspection only. No model inference, answer-quality evaluation, citation-correctness test, latency measurement, or provider compatibility check ran.

[^txtai-repo]: Revision `738aac4`: `src/python/txtai/pipeline/llm/llm.py::LLM.__init__, __call__`; `pipeline/llm/factory.py::GenerationFactory.create, method`; `pipeline/llm/generation.py::Generation.format, clean, cleanthink, cleanstream, response`; `pipeline/llm/huggingface.py::HFLLM, StreamingResponse`; `pipeline/llm/llama.py::LlamaCpp.create`; `pipeline/llm/litert.py::LiteRT.createengine`; `pipeline/llm/opencode.py::OpenCode`; `pipeline/llm/rag.py::RAG.__init__, __call__, load, query, score, batchsearch, tokenize, answers, prompts, apply, snippets, reference, terms`; `pipeline/__init__.py` alias export; `docs/pipeline/llm/rag.md`; `examples/52_Build_RAG_pipelines_with_txtai.ipynb` citation discussion (Markdown cells 18/20/23); `test/python/testpipeline/testllm/testrag.py`. Short module paths are relative to `src/python/txtai/`.
