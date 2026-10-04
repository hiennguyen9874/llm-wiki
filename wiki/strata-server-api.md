---
type: Concept
title: Strata Server API and Operations
description: Strata's local server for Qwen3.8-Flash-Next — OpenAI Chat/Responses and Anthropic Messages endpoints, thinking controls, conversation checkpoints and parking, vision, validated JSON output, MCP tools, VRAM sharing, network security defaults, and experimental YaRN and control-vector options.
tags: [strata, serving, openai-api, anthropic-api, responses-api, reasoning, prefix-caching, vision, structured-outputs, mcp, security, rope-scaling, qwen3.8-flash-next]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-04T20:00:00Z }
stale_after: 2027-04-04
sources:
  - id: strata-docs
    resource: ../raw/Strata/README.md
    scope: ../raw/Strata/
    kind: documentation
    title: Strata repository documentation (README, HOW_IT_WORKS, MODELS, DETAILS; engine up to 0.1.39b)
  - id: strata-thread-5090
    resource: ../raw/strata-on-a-power-limited-5090-and-96gb-of/index.md
    scope: ../raw/strata-on-a-power-limited-5090-and-96gb-of/
    kind: discussion
    title: "Strata on a power limited 5090 and 96GB of DDR5-6400 (r/LocalLLaMA)"
  - id: strata-thread-bots
    resource: ../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/index.md
    scope: ../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/
    kind: discussion
    title: "Yes bots we get it, Strata is good now please stop (r/LocalLLaMA)"
---

Strata's `serve/server.py` exposes the [tiered offload engine](strata-tiered-moe-offload.md) at `http://127.0.0.1:8080` as a single-user local server: OpenAI Chat Completions, OpenAI Responses, and Anthropic Messages APIs with tools and streaming, a web app (Chat, Monitor, About), prompt checkpoints that make follow-up turns cheap, and opt-in features for agents, sharing the GPU, and network exposure[^strata-docs]. Defaults favor one request at a time and loopback-only binding[^strata-docs]. Flags and endpoints below reflect the docs through engine 0.1.39b.

## Endpoints and clients

| API | Endpoint |
| --- | --- |
| OpenAI Chat Completions | `POST /v1/chat/completions` |
| Anthropic Messages | `POST /v1/messages` |
| OpenAI Responses (stateless, 0.1.39, #451) | `POST /v1/responses` |
| Models / health / props | `GET /v1/models`, `/models`, `/health`, `/props` |
| Live state / monitor | `GET /status`, `/slots`, `/metrics`, `/mcp` |
| Load control | `POST /load`, `/unload`, `/v1/load`, `/v1/unload`; `POST /v1/vram` |

Endpoint list from the API table and load-control sections[^strata-docs].

- Any API key and model name work by default; Claude Code uses `ANTHROPIC_BASE_URL=http://127.0.0.1:8080` with a Claude model name it accepts; Codex CLI uses `wire_api = "responses"` with a long `stream_idle_timeout_ms`; OpenCode uses `@ai-sdk/openai-compatible`[^strata-docs].
- Responses API is stateless: `previous_response_id`, `conversation`, `background`, and retrieve/delete/cancel are refused; hosted tools are dropped; `tool_choice` cannot force a tool; reasoning returns as `reasoning_text` with empty `summary`[^strata-docs].
- Codex CLI 0.160.0 with Q2_0 on RTX 5070: first prompt 9,443 tokens read in 10 s; later tool-loop turns reused ~96% of the prompt and read the rest in 1–2 s (**Reported**)[^strata-docs].
- Requests exceeding the configured context are refused, never truncated; `"fit_max_tokens": true` shrinks oversized `max_tokens` instead of returning 400[^strata-docs].

## Thinking controls

- Levels `none`/`low`/`medium`/`high` via `reasoning_effort` or Anthropic `output_config.effort` / `thinking`; default is the model's own, `high`; levels are trained instructions, not hard limits[^strata-docs]. Compare [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) and [SGLang Reasoning Parser](sglang-reasoning-parser.md).
- `reasoning_budget_tokens` is an opt-in hard cap that injects a wrap-up line and `</think>` without re-reading the prompt[^strata-docs].
- `"effort_position": "end"` (0.1.39, #458) moves non-default effort to a short system turn before the answer so changing effort keeps the prompt-cache prefix; how well the model follows effort there is unmeasured[^strata-docs].
- `"anthropic_thinking": "on_request"` (0.1.32, #278) disables thinking for Anthropic requests that do not ask for it, matching Anthropic semantics for Claude Code helper calls[^strata-docs].
- A reply repeating one token 256 times is ended with `finish_reason: "length"` (0.1.39, #606; `repeat_stop_tokens`)[^strata-docs].

## Conversation cache

- Up to 6 RAM checkpoints (~118 MB each) taken at each new assistant turn and every 16K prompt tokens; reused only on an exact token-and-image prefix match; the oldest (system-prompt end) is pinned while the rest rotate LRU, so new chats sharing a system prompt skip it; since 0.1.20 a ≥2,048-token system prompt is checkpointed on first read[^strata-docs].
- Opt-in parking (`--conversation-cache-mib 8192 --conversation-cache-slots 4`) snapshots running state, checkpoints, used K/V pages, and draft-layer K/V into bounded host RAM so alternating agent conversations are restored rather than re-read; not concurrent execution; requires `--conversation-cache-min-free-mib` headroom (default 2560); not persisted across restarts[^strata-docs].
- Layer-split verification: a 9,276-token conversation restored in 51 ms on 4 GPUs with identical follow-up tokens (**Reported**); Windows/HIP and multi-GPU runtime coverage is called out as needing separate reporting[^strata-docs].
- **Synthesis:** this is exact-prefix checkpoint reuse for a single-slot recurrent/hybrid model rather than block-granular sharing as in [vLLM Prefix Caching](vllm-prefix-caching.md) or [SGLang Unified Radix Cache](sglang-unified-radix-cache.md).
- Concurrency: one request at a time unless `"parallel": N` batch slots are set (BATCHING.md, not inspected); on a 12 GB card parallelism slows each answer[^strata-docs]. A 2026-10-03 thread reporter on a two-GPU Strata fork confirms no concurrency — one session/slot at a time with no aggregate-decode behavior to report (**Reported**)[^strata-thread-5090].
- Independent concurrency confirmations from a 2026-10-03 complaint thread (**Reported**)[^strata-thread-bots]: Strata's weak point named as no parallel-request support (one 2×16 GB + 192 GB user keeps vLLM for 27B concurrency); lack of continuous batching framed as one conversation / one KV cache with speed crashing under concurrent use, limiting agentic-swarm roles but leaving fast single-chat use; counter-pointer that opt-in conversation parking (`--conversation-cache-mib`, `--conversation-cache-slots`, server default 0 = off) restores parked conversations rather than executing concurrently. Setup notes from the same thread: `llama-swap` wiring, podman containment for untrusted setup scripts, and Claude-assisted setup on 32 GB DDR5 + 5090 (**Reported**). One 2×3060 crash (GPU error, guessed expert-streaming cause) and one over-context handling note (requests queuing well but over-window requests needing harness/server changes) stay single-reporter **Reported** limits[^strata-thread-bots].

## Sampling

- Temperature, top_p, top_k (capped at 64 candidates), min_p, seed, and penalties honored per request; a config `sampling` block sets defaults; with none, requests decode greedily[^strata-docs].

## Vision

- Optional 0.9 GB BF16 mmproj (27-layer ViT plus projector) run by a `strata-vision` helper built on llama.cpp `mtmd`; GPU encoding 0.1–0.5 s per picture (up to 1,024 tokens) with ~1.4 GB VRAM reserved, CPU 10–30 s at ~300 tokens[^strata-docs].
- Image tokens get 2-D interleaved M-RoPE positions; answers match llama.cpp multimodal token for token on project test images (**Reported**); repeated pictures are encoded once[^strata-docs].
- `--vision-tokens N` and a user-supplied Q8_0 mmproj (accuracy unmeasured) are 0.1.39 options (#625); `"cuda_device"` puts the encoder on a spare GPU (0.1.33, #408); AMD on Windows cannot read pictures yet[^strata-docs].

## Structured output

- `response_format` `json_object` / `json_schema` is schema prompting plus server-side validation (`jsonschema` when installed), **not** grammar-constrained decoding; one generation, no retry; failures return 502 `structured_output_failed`; combining with tools/MCP is refused; streaming buffers until validated[^strata-docs]. Contrast [vLLM Structured Outputs](vllm-structured-outputs.md) and [SGLang Structured Outputs](sglang-structured-outputs.md), which constrain decoding.

## MCP

- The web chat can call tools from MCP servers configured in `mcp_servers` (Claude Desktop `mcpServers` shape; stdio or Streamable HTTP, not SSE-only), with `timeout_s`, `max_result_chars`, and `max_rounds`; API clients opt in with `"strata_mcp": true`[^strata-docs].
- `tools/strata_mcp.py` is a separate MCP server letting assistants install, start, stop, and inspect Strata; install shows a plan and waits for approval[^strata-docs].
- Security: MCP tools run with the user's rights and the model chooses when to call them, including under prompt injection from read content; the docs advise least-privilege folders and trusted servers only[^strata-docs].

## GPU sharing and lifecycle

- `--idle-unload`, `--min-free-vram-mib` (503 when VRAM is busy), `--before-load`, and `--lazy` start release VRAM for games or other model servers; unload took ~0.3 s and reload answered in 4.6 s (text) on an RTX 5060 Ti in low-RAM mode (**Reported**)[^strata-docs].
- `"vram_elastic": true` (#533, one NVIDIA GPU) allocates the expert cache in 512 MiB segments resizable via `POST /v1/vram`; RTX 5070 Q2_0: freeing 4.3 GiB took 78 ms and cut decode 44 → 33 tok/s; regrowing restored identical tokens (**Reported**)[^strata-docs]. Compare [vLLM Sleep Mode](vllm-sleep-mode.md).

## Network security defaults

- Binds `127.0.0.1`; LAN or tunnel exposure should set `api_key`; without a key, a Host allowlist blocks DNS rebinding (403) and browser `POST`s with foreign `Origin` are refused; CORS is off by default (`cors_origins`); settings, unload, and MCP never open to CORS[^strata-docs].
- The opt-in API request monitor (`"api_monitor": true`) keeps the newest 100 requests' prompts and outputs in memory and should be treated as sensitive[^strata-docs].

## Experimental options

- **Context past 262K:** rope scaling with llama.cpp flags; on one contributor setup (RTX 5080, IQ3_S, PR #84) `yarn` factor 2 lowered NLL at 293K by 0.18 nats vs `none`/`linear` (2.04 vs 2.22), `yarn` 4 answered 8/8 long-document Q&A at 714K, and a 1M-token run completed; setup derives factor = context / 262,144 and refuses `none` past the trained range; scaling is fixed per run and slightly changes the model even inside 262K (**Reported**)[^strata-docs]. See [vLLM Context Extension](vllm-context-extension.md) and the official YaRN guidance in [Qwen3.8-Flash-Next HF Release and Serving](qwen3.8-flash-next-hf-release.md).
- **"Experimental speed projection":** a 480 KB per-layer control vector projected out of residual streams at layers 4–44; its package describes it as a refusal-direction projection (1/50 vs 50/50 refusals), so it removes a safety behaviour; it is not a speed optimization (costs 0.2–0.4% per token) and shifts outputs (top-1 changes at 10% of positions, mean KL 0.063 nats, code perplexity +15%) (**Reported**); off by default, per-request switchable[^strata-docs].

## Relationships

- Uses [Strata Tiered MoE Offload Engine](strata-tiered-moe-offload.md) — the native engine this server drives.
- Uses [Strata MTP and Prompt-Lookup Speculation](strata-speculative-decoding.md) — decode path behind every endpoint.
- Related to [Qwen3.8-Flash-Next HF Release and Serving](qwen3.8-flash-next-hf-release.md) — upstream thinking controls and chat template this server renders.
- Related to [vLLM Tool Calling](vllm-tool-calling.md) — server-engine counterpart for tool-call APIs.

## Coverage limits

- `BATCHING.md`, `MCP_SERVER.md`, `INSTALL.md`, `TROUBLESHOOTING.md`, and `MULTI_GPU.md` are referenced but absent; batching semantics and per-client MCP configuration are therefore not covered.
- Placeholder secrets in examples were not reproduced; no real credentials present.

[^strata-thread-5090]: r/LocalLLaMA thread "Strata on a power limited 5090 and 96GB of DDR5-6400" — `../raw/strata-on-a-power-limited-5090-and-96gb-of/index.md` (comment 2026-10-03): two-GPU fork reporter confirms no concurrent sessions/slots.

[^strata-thread-bots]: r/LocalLLaMA thread "Yes bots we get it, Strata is good now please stop" — `../raw/yes-bots-we-get-it-strata-is-good-now-please-stop/index.md` (comments 2026-10-03–2026-10-04): no-parallel-requests weak point (fdrch), no-continuous-batching limit (txgsync), parking-flag counter (jmager with DETAILS.md link), llama-swap wiring (Tylnesh), podman setup (jmager), Claude-assisted 32 GB setup (mysoor2000), 2×3060 crash (LemesoftNostalgic), and over-context queue note (explorer-9).

[^strata-docs]: Strata docs — `../raw/Strata/DETAILS.md` "Using it" (API table, thinking levels, budget, repeat stop, effort_position, anthropic_thinking, streaming, clients, context, aliases, network/CORS/Host/Origin), "Conversation cache", "Multiple conversations (opt-in)", "Current limits (v1)", "The Responses API and Codex CLI", "Tools from MCP servers", "Context extension past 262K", "Manage Strata from your AI assistant (MCP server)", "Images (vision)", "Experimental speed projection", "Sharing the GPU with other programs", "Start the text API without occupying the GPU", "JSON response formats", "API request monitor"; `../raw/Strata/README.md` "Using it".
