---
type: Concept
title: vLLM Endpoint Plugins
description: Out-of-tree HTTP routes for the vLLM OpenAI-compatible server via two-phase EndpointPlugin loading and EngineClient access.
tags: [vllm, plugins, server]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: endpoint-plugins
    resource: ../raw/vllm/design/endpoint_plugins.md
    title: Endpoint Plugins
  - id: plugin-system
    resource: ../raw/vllm/design/plugin_system.md
    title: Plugin System
---

Endpoint plugins let out-of-tree packages add HTTP routes to the OpenAI-compatible API server[^endpoint-plugins]. Their scope is the HTTP surface only — registering routes and optionally per-app state used by those routes[^endpoint-plugins]. A plugin reaches the engine the same way an in-tree serving handler does, through the `EngineClient` handed at startup (e.g. `engine_client.collective_rpc(...)`); no new engine access path is introduced[^endpoint-plugins].

## EndpointPlugin protocol

Plugins implement the runtime-checkable `EndpointPlugin` protocol[^endpoint-plugins]:

- `name`: unique identifier used in logs and for `VLLM_PLUGINS` allowlisting[^endpoint-plugins].
- `required_tasks`: tasks the server must support for the plugin to load; `None` means no task requirement[^endpoint-plugins].
- `attach_router(app: FastAPI)`: registers routes on `app`[^endpoint-plugins].
- `init_state(engine_client, state, args)`: initializes per-app state the routes read at request time[^endpoint-plugins].

## Two-phase lifecycle

Routes are registered before the engine exists, so startup is split[^endpoint-plugins]:

| Phase | Called from | `engine_client` available? | Work |
| --- | --- | --- | --- |
| A. Route registration | `build_app()` | No | `attach_router(app)` adds routes; do not touch the engine here[^endpoint-plugins]. |
| B. State init | `init_app_state()` | Usually, but `None` on CPU-only render server | Build a serving handler holding `engine_client` and store it on `state`[^endpoint-plugins]. |

Because `app.state` is the `state` object passed to `init_app_state()`, objects stored in phase A are visible in phase B, and objects stored in phase B are visible to route handlers via `request.app.state`[^endpoint-plugins]. This is the same pattern in-tree endpoints use[^endpoint-plugins].

## Engine-less render server

The CPU-only render server (`init_render_app_state()`) has no `EngineClient` but still runs both phases for plugins eligible for the `render` task (`required_tasks` is `None` or includes `"render"`)[^endpoint-plugins]. `attach_router` runs as usual; `init_state` receives `engine_client=None`[^endpoint-plugins].

A plugin that needs an engine has two options[^endpoint-plugins]:

- Exclude `"render"` from `required_tasks` so it never loads on the render server.
- Accept loading on `render` and check for `None` in `init_state` or the route handler, returning e.g. HTTP 503 instead of dereferencing a missing client.

`tests/plugins/vllm_add_dummy_endpoint_plugin` demonstrates the `None`-check option by returning 503 when `state.dummy_engine_client` is `None`[^endpoint-plugins].

## Reaching the engine

`init_state` captures `engine_client` into a small serving handler and stashes it on `state`; the route reads it from `request.app.state` at request time and calls the engine, typically via `collective_rpc(...)`[^endpoint-plugins]. A complete tested version is in-repo as `tests/plugins/vllm_add_dummy_endpoint_plugin`, exercised end-to-end including a real HTTP request in `tests/plugins_tests/test_endpoint_plugins.py`[^endpoint-plugins].

## Registration and gating

Register a zero-argument factory (class or function) under the `vllm.endpoint_plugins` group; the entry-point name is independent of the plugin's `name` attribute[^endpoint-plugins]:

```toml
[project.entry-points."vllm.endpoint_plugins"]
my_admin_api = "my_pkg.endpoints:MyAdminEndpointPlugin"
```

Discovery and gating by `load_endpoint_plugins` is stricter than for other plugin groups[^endpoint-plugins]:

- Nothing loads unless `VLLM_PLUGINS` is set and names the plugin; other groups load everything unless `VLLM_PLUGINS` narrows the set[^endpoint-plugins]. Endpoint plugins invert the default because they add network-exposed surface[^endpoint-plugins].
- `required_tasks` must intersect the server's supported tasks unless it is `None`; use this to avoid attaching routes on a server that cannot service them (e.g. pooling-only deployment)[^endpoint-plugins].
- A factory that raises during instantiation is logged and skipped without aborting startup[^endpoint-plugins].
- `VLLM_PLUGINS` allowlisting matches the entry-point name, following the same convention as `vllm.general_plugins`[^endpoint-plugins][^plugin-system].
- Only the front-end API-server process loads endpoint plugins; no worker or engine-core guard is needed[^endpoint-plugins].

Endpoint plugins are not loaded by default and must be explicitly allowlisted[^endpoint-plugins].

## Pairing with general_plugins

Endpoint plugins cover the HTTP surface only[^endpoint-plugins]. New engine-side behavior (worker-side RPC method, custom stat) ships separately through `vllm.general_plugins`, which loads in worker processes[^endpoint-plugins][^plugin-system]. The two entry points are registered and loaded independently; neither implies the other[^endpoint-plugins]. The recommended shape is one package exposing both, and a route needing a nonexistent worker-side method must add it via a paired `general_plugins` entry point rather than expecting the endpoint plugin to mutate engine/worker state[^endpoint-plugins].

## Path-prefix convention

There is currently no route-conflict enforcement (tracked as follow-up to RFC #46565)[^endpoint-plugins]. A plugin's `attach_router` can collide with a core route, with later-attached routes winning[^endpoint-plugins]. To avoid surprising operators[^endpoint-plugins]:

- Namespace routes under a distinct prefix, e.g. `/plugins/<plugin-name>/...`, rather than `/v1/...` or other core prefixes.
- Only use a core prefix if specifically intending to override or extend existing behavior, and document that clearly for operators allowlisting the plugin.

## Compatibility

`FastAPI`, `EngineClient`, and the `EndpointPlugin` protocol itself are the supported surface[^endpoint-plugins]. `state` / serving-handler internals such as the shape of in-tree `OpenAIServing*` classes are not a stable public contract; treat them as use-at-your-own-risk and expect change across versions[^endpoint-plugins].

## Coverage limits

- The referenced Endpoint Plugins security posture (`../usage/security.md#endpoint-plugins`) was not present in `raw/` and was not inspected; trust-model detail beyond explicit allowlisting and the route-shadowing warning was not compiled[^endpoint-plugins].
- In-repo example and test paths (`tests/plugins/vllm_add_dummy_endpoint_plugin`, `tests/plugins_tests/test_endpoint_plugins.py`) and external RFC #46565 were cited but not inspected[^endpoint-plugins].

## Relationships

- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — only the front-end API-server process loads endpoint plugins.
- Uses [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — engine access is via `EngineClient`, with worker-side extensions paired through `general_plugins`.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — routes attach to the OpenAI-compatible server built by `build_app()` / `init_app_state()`.

[^endpoint-plugins]: Endpoint Plugins — `../raw/vllm/design/endpoint_plugins.md`.
[^plugin-system]: Plugin System — `../raw/vllm/design/plugin_system.md`, Types of supported plugins.
