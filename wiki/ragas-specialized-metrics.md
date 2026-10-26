---
type: Concept
title: Ragas agent, SQL, lexical and multimodal metrics
description: Rule-based tool and citation checks coexist with LLM goal/SQL judges, CSV result comparison and network-capable multimodal scoring.
tags: [rag, ml, evaluation, agents, multimodal]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:20:38Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b68274234
    title: Ragas repository
---

**Observed:** Ragas collections expose agent/tool, SQL/data, lexical, quoted-span and multimodal metric families in addition to RAG scores. These differ in whether they invoke an LLM, inspect structured messages, compare already-produced data, or fetch image inputs. Their existence is not evidence of an agent runtime or database execution engine.[^ragas-298b682]

## Mechanisms and constraints

| Family | Inspected behavior | Interpretation |
| --- | --- | --- |
| ToolCallAccuracy | Extract AIMessage tool calls, compare names/arguments, strict_order=True by default | Order/length penalties and reference-key string comparisons matter |
| ToolCallF1 | Convert calls/arguments to hashable set representation and compute F1 | Duplicate identical calls collapse; not a sequential trajectory check |
| AgentGoalAccuracyWithReference | Infer end state from formatted messages, judge against reference | Goal success is an LLM verdict, not independent task execution |
| SQLSemanticEquivalence | Judge SQL strings plus supplied schema context | Does not run queries against a database |
| DataCompyScore | Parse response/reference CSV strings to pandas, compare with datacompy | Compares results supplied by caller, does not execute SQL; optional dependencies required |
| ExactMatch / StringPresence | String equality / substring membership | Deterministic textual checks, not semantic correctness |
| NonLLMStringSimilarity | RapidFuzz normalized-distance family | Optional dependency; default Levenshtein |
| QuotedSpansAlignment | Extract quoted spans and compare to reference text, default casefold and minimum three words | Quote alignment only, not general citation entailment |

SemanticSimilarity uses embeddings; BLEU/CHRF/ROUGE delegate to optional lexical-metric libraries. TopicAdherence and rubric families are exported, but this pass did not inspect every scoring/prompt body, so their presence is a catalogue observation only.[^ragas-298b682]

## Multimodal input boundary

The inspected multimodal faithfulness implementation constructs image/text messages and calls the underlying provider client directly rather than the ordinary structured-generation wrapper. Its helper tries data URIs, HTTP(S) URLs and local files; downloaded/local bytes must meet size and PIL-image checks before base64 inclusion. Failed image processing becomes text context rather than a hard failure. **Synthesis:** image access failures can change what the judge evaluates without making the whole score fail.[^ragas-298b682]

The collection helper's local/URL policy differs from the older guarded multimodal prompt path. Valid local image bytes or reachable image resources can leave the process in judge requests. See [security boundaries](ragas-security.md); do not evaluate untrusted datasets with unrestricted filesystem/network/provider access.

## Relationships and limits

- Uses [message schemas and API contracts](ragas-metric-contracts.md) and [model adapters](ragas-model-adapters.md).
- Agent metrics are distinct from [synthetic test generation](ragas-testset-generation.md), whose inspected shipped synthesizers produce single-turn RAG samples.
- No SQL engine, tool trajectory, image fetch, quote check or provider judge was run. No metric-quality or security exploit conclusion was reproduced.

[^ragas-298b682]: Ragas `298b68274234`, `src/ragas/metrics/collections/__init__.py::__all__`; `collections/tool_call_accuracy/metric.py::ToolCallAccuracy.ascore` and `util.py::exact_match_args`; `collections/tool_call_f1/util.py::tool_call_to_hashable/calculate_f1_score`; `collections/agent_goal_accuracy/metric.py::AgentGoalAccuracyWithReference`; `collections/sql_semantic_equivalence/metric.py::SQLSemanticEquivalence`; `collections/datacompy_score/metric.py::DataCompyScore`; `collections/_string.py`; `collections/quoted_spans/metric.py`; `collections/multi_modal_faithfulness/metric.py` and `util.py::build_multimodal_message_content/_try_process_url/_try_process_local_file` (collection paths relative to `src/ragas/metrics/`); `src/ragas/metrics/quoted_spans.py::_extract_quoted_spans`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
