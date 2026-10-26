---
type: Concept
title: Ragas synthetic testsets and query synthesis
description: Graph-compatible query distributions combine personas, styles and single/multi-hop contexts to produce single-turn references without exact-size or quality guarantees.
tags: [rag, ml, synthetic-data, evaluation]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:28:37Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b682
    title: Ragas repository
---

**Observed:** TestsetGenerator ingests LangChain/LlamaIndex documents or prechunked content into a [knowledge graph](ragas-testset-graph.md), then generates personas, scenarios and samples through Executor-backed stages. The inspected shipped synthesizers produce SingleTurnSample questions, references and reference contexts with scenario metadata. Generated outputs are source-conditioned examples, not independently verified answers.[^ragas-298b682]

## Scenario families

| Synthesizer | Context selection | Conditioning |
| --- | --- | --- |
| Single-hop specific | Entity-bearing document/chunk nodes | Term, persona, query style and length |
| Multi-hop specific | `entities_overlap` node pairs and `overlapped_items` | Shared concepts and diverse persona/style/length combinations |
| Multi-hop abstract | `summary_similarity` clusters, replacing parents with child chunks where present | Cross-node concepts, persona/style/length |

`default_query_distribution` probes each candidate's compatible graph clusters, warns/skips exceptions and returns equal weights over surviving kinds, or raises when none survive. This contradicts the quickstart's stated 0.5/0.25/0.25 default. Inputs lacking required properties/edges change the available distribution.[^ragas-298b682]

## Personas, counts and randomness

Persona generation groups summary-bearing embeddings by a raw dot-product threshold of 0.75, picks representative summaries and may sample padding before LLM role generation. Facade default is three personas; supplied lists are shuffled and sliced. No per-persona coverage quota is enforced by this mechanism.[^ragas-298b682]

Requested sample allocation uses ceiling-rounded distribution shares; scenario availability and failures can further change output. **Synthesis:** testset_size is a target, not a guaranteed exact cardinality. Retain realized counts per synthesizer/persona, failed scenarios, prompt/model choices and graph snapshot. RunConfig.seed does not seed every Python/global NumPy random operation or graph-identity-based shuffle; deterministic regeneration is unestablished.[^ragas-298b682]

Prompts request context-only answers and multi-segment reasoning where applicable, but a prompt instruction is not validation that a generated query genuinely needs multiple hops. Persona-theme matching and hard-coded graph-property expectations are additional failure points requiring targeted tests.[^ragas-298b682]

## Outputs and capability boundary

Testset converts to EvaluationDataset, pandas/HuggingFace and CSV/JSONL forms; annotation import can retain only approved samples. Token/cost helpers require callbacks/parsers. **Synthesis:** generated reference contexts are the synthesizer's supporting passages, not measured retrieval output from the application under test; run that application separately to obtain its response and retrieved contexts. The agent/tool test-data documentation explicitly describes tools being worked on, while the inspected synthesizers return single-turn RAG samples. Do not infer general agent-conversation synthesis from the existence of MultiTurnSample in shared schemas.[^ragas-298b682]

## Relationships and limits

- Depends on [graph construction](ragas-testset-graph.md) and [prompt/model configuration](ragas-prompt-optimization.md).
- Supplies potential references for [RAG metrics](ragas-rag-metrics.md), which still inherit generator/reference/judge biases.
- No samples generated, no requested-vs-realized count measured, no provider spend incurred and no human validation of synthetic answers performed.

[^ragas-298b682]: Ragas `298b682`, `src/ragas/testset/synthesizers/generate.py::TestsetGenerator.generate_with_langchain_docs/generate_with_llamaindex_docs/generate_with_chunks/generate`; `synthesizers/__init__.py::default_query_distribution`; `synthesizers/utils.py::calculate_split_values`; `synthesizers/single_hop/specific.py::SingleHopSpecificQuerySynthesizer`; `synthesizers/multi_hop/specific.py::MultiHopSpecificQuerySynthesizer`; `synthesizers/multi_hop/abstract.py::MultiHopAbstractQuerySynthesizer`; `persona.py::generate_personas_from_kg`; `synthesizers/testset_schema.py::Testset` (paths relative to `src/ragas/testset/`); `docs/getstarted/rag_testset_generation.md::Testset Generation`; `docs/concepts/test_data_generation/agents.md`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
