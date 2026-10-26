---
type: Concept
title: UltraRAG pipeline DSL and configuration
description: YAML dataflow, generated MCP metadata, parameter resolution, branching, and server extension contracts.
tags: [ml, ultrarag, mcp, orchestration]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e2032d9f1
    title: UltraRAG repository
---

**Observed:** UltraRAG's YAML DSL combines a `servers` mapping with ordered `pipeline` steps. Server registrations describe tool input/output wiring; `UltraData` resolves that wiring into a shared variable pool, while the client interprets sequences, loops, and router-controlled branches. Consequently pipeline order and generated metadata are part of correctness, not just presentation.[^ultrarag]

## Build and run lifecycle

Run these from a separate working checkout, not the immutable wiki source copy:

```sh
ultrarag build examples/experiments/sayhello.yaml
ultrarag run examples/experiments/sayhello.yaml
```

These commands were **observed in configuration/code, not executed**. Build invokes each server's metadata builder and writes server-local `server.yaml` plus pipeline-local `server/<stem>_server.yaml` and `parameter/<stem>_parameter.yaml`. Run loads compiled configuration; an unbuilt pipeline can fail on missing files. Build is not pure validation: it launches server processes and writes files.[^ultrarag]

## Variable and parameter semantics

- A normal `server.tool` step consumes declared inputs and registers outputs. Mapping-form steps can remap `input` and `output` names.
- `$name` resolves against that server's parameter block. Ordinary names refer to pipeline variables; an ordinary input must have been introduced by an earlier output, otherwise `_extract_io` raises `ValueError`.
- `mem_` aliases canonicalize to `memory_`; history variables accumulate deep-copied values. These histories are distinct from the persistent user-memory server.
- Defaults load from each server's `parameter.yaml`; then `self.local_vals.update(all_local_vals)` applies the pipeline parameter file at the **server-block level**. A supplied block replaces that default block; this is not a recursive per-key merge.
- Explicit `--param` resolution considers absolute paths, current-working-directory paths, then pipeline-directory paths. Without it, the expected file is `parameter/<pipeline-stem>_parameter.yaml` beside the pipeline; if that default parameter file is absent, loading yields an empty mapping and server defaults remain. An explicitly requested missing parameter file raises an error.
- Multiple aliases can use the same server implementation with separate runtime blocks, but the server-local metadata/default files remain shared.[^ultrarag]

The UI/runtime override path is different from file loading: `override_params` shallow-merges keys into each existing server block. The UI override builder can replace a nested `backend_configs` mapping wholesale and force OpenAI-compatible backends for demo/chat. Thus file-block replacement is not the only precedence rule; see [generation demo overrides](ultrarag-generation.md).[^ultrarag]

## Control flow

`loop` specifies integer `times` and a `steps` list. `branch` specifies a router sequence and a mapping of branch state names to step lists. The last router step determines states; router outputs wrap data as records containing `data` and `state`. Names must agree with the YAML branch keys. The engine filters wrapped data by branch context and can stop loops when no data remains for the active branch; this is not a general arbitrary-expression language.[^ultrarag]

**Observed implementation caveat:** loop termination updates differ for string-form and mapping-form steps (`=` versus `&=` on the depth's terminal flag). The consequences for complex mixed pipelines have not been executed or verified. Prefer the bundled loop/branch examples as structural references, not a guarantee of arbitrary composition.[^ultrarag]

## Extending an MCP server

`UltraRAG_MCP_Server` subclasses FastMCP, records tool/prompt metadata, and registers its own `build` tool. A registration's `output=` specification can provide `input1,input2 -> output1,output2`; matching keys in the parameter YAML become `$` references. With no arrow, the nonempty specification names **outputs**, while inputs default to function parameter names. `None` suppresses output names. `_make_io_mapping` uses positional `zip`, so a too-short explicit input specification can silently omit parameters; the only arrow-count guard is an assertion. Inspect generated metadata when changing signatures.[^ultrarag]

The wrapper filters unsupported constructor and decorator options against the installed FastMCP signatures. This compatibility strategy does not independently establish compatibility with every allowed dependency version.[^ultrarag]

## Outputs and interface differences

The engine records per-step snapshots, writes `output/memory_<benchmark>_<pipeline>_<timestamp>.json`, can stream step/token/source events, and attempts `vllm_shutdown` cleanup in a `finally` path. If a memory server is detected, explicit `save_memory` steps are skipped in favor of automatic end-of-turn saving. Memory-save and shutdown failures are warnings.[^ultrarag]

`ToolCall` wraps individual tools after `initialize`; `PipelineCall` reuses the client runtime with `return_all=True`. Both select synchronous execution versus returning an asyncio task based on whether an event loop is running. Unlike CLI local launch, `initialize` uses bare `python`. `script/api_usage_example.py` also references an example location that does not match the current `examples/experiments/` layout.[^ultrarag]

## Documentation discrepancies

**Observed:** the packed documentation's quick-start path uses plural `parameters/`, whereas implementation writes singular `parameter/` and also requires compiled `server/` configuration. Its alias discussion should not be read as promising separate server-local files. `show` owns `--log_level` in argparse, so that option belongs before `ui`/`case`, not after it as shown in the packed CLI documentation.[^ultrarag]

## Relationships

- **Depends on:** [deployment dependencies](ultrarag-deployment.md), including Node for the remote MCP bridge.
- **Uses:** [router and prompt workflows](ultrarag-research-workflows.md) for data-dependent iteration.
- **Used by:** [the UI](ultrarag-ui.md), which imports the same engine.

[^ultrarag]: Revision `185e2032d9f1`: `src/ultrarag/client.py::UltraData.__init__`, `_extract_io`, `get_data`, `save_data`, `write_memory_output`, `build`, `load_pipeline_context`, `_execute_steps`, `execute_pipeline`, `_auto_save_memory_turn`, `main`; `ui/backend/pipeline_manager.py` runtime/backend override builder; `src/ultrarag/server.py::UltraRAG_MCP_Server._make_io_mapping`, `_build_entry`, `build`, `__init__`; `src/ultrarag/api.py::_CallWrapper`, `initialize`, `PipelineCall`; `examples/experiments/{sayhello,rag_loop,rag_branch,hybrid_search}.yaml`; `script/api_usage_example.py`; `docs/llms.txt` embedded `quick_start.mdx`, `rag_client/multi_agents.mdx`, `api/cli.mdx` sections. All behavior here is static observation; examples were not run.
