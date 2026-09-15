---
type: Concept
title: vLLM Disaggregated Prefill
description: Separate prefill and decode vLLM instances with connector-mediated KV transfer to tune TTFT and ITL independently and control tail ITL without improving throughput.
tags: [vllm, disaggregated-prefill, kv-cache, inference-serving]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T16:30:00Z }
sources:
  - id: disagg-prefill
    resource: ../raw/vllm/features/disagg_prefill.md
    title: Disaggregated Prefilling (experimental)
  - id: moriio-single-node
    resource: ../raw/2026-04-07-moriio-kv-connector/index.md
    title: "Next-Level Inference: Why Your Single-Node vLLM Setup Needs Prefill-Decode Disaggregation"
  - id: hybrid-ssm-disagg
    resource: ../raw/2026-04-21-hybrid-ssm-disagg/index.md
    title: Disaggregated Serving for Hybrid SSM Models in vLLM
---

Disaggregated prefilling (experimental) runs prefill and decode in separate vLLM instances and uses a KV-transfer connector to move prefill KV caches and results from the prefill instance to the decode instance[^disagg-prefill].

## Goals and non-goal

- **Tune TTFT and ITL separately:** prefill and decode live in different instances, so different parallel strategies (e.g. `tp` and `pp`) can tune time-to-first-token without affecting inter-token latency, or vice versa[^disagg-prefill].
- **Control tail ITL:** without disaggregation, vLLM may insert prefill work during decoding of another request and inflate tail latency; disaggregation avoids this more reliably than hand-tuning chunked-prefill chunk size[^disagg-prefill].
- **Throughput:** disaggregated prefill DOES NOT improve throughput[^disagg-prefill]. Single-node MORI-IO evidence qualifies this: raw throughput is not the claim, but SLO-compliant goodput (max req/s with TTFT < 1 s and ITL < 50 ms) rose ~2.5× on the same 8 GPUs because ITL violations were removed at the cost of higher TTFT[^moriio-single-node].

## Deployment shape

- Two instances: one prefill instance and one decode instance[^disagg-prefill].
- Implementation lives under `vllm/distributed/kv_transfer`[^disagg-prefill].
- Single-node variant runs both instances on one 8-GPU MI300X box (GPUs 0–3 prefill TP=4, GPUs 4–7 decode TP=4) behind a proxy that routes to prefill first, then decode; it needs no multi-node cluster and holds total GPU count constant for fair comparison with collocated baselines[^moriio-single-node].

## Connectors

The source states 9 connector types but enumerates 8 named connectors; preserved as documented[^disagg-prefill]:

- **ExampleConnector:** reference example; see `examples/disaggregated/example_connector/run.sh`[^disagg-prefill].
- **LMCacheConnectorV1:** NIXL-backed KV transmission; see `examples/disaggregated/lmcache/disagg_prefill_lmcache_v1/disagg_example_nixl.sh`; LMCache also offers multi-process mode via `LMCacheMPConnector` with a standalone `lmcache server` holding KV shared by vLLM instances[^disagg-prefill].
- **NixlConnector:** fully async send/recv over NIXL with one or multiple backends[^disagg-prefill]:

  ```bash
  --kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_both", "kv_buffer_device":"cuda", "kv_connector_extra_config":{"backends":["UCX", "GDS"]}}'
  ```

- **MooncakeConnector:** see `examples/disaggregated/mooncake_connector/run_mooncake_connector.sh`[^disagg-prefill].
- **MoRIIOConnector** (ROCm only)[^disagg-prefill].
- **MultiConnector:** ordered list of connectors stashed in `kv_connector_extra_config`[^disagg-prefill]:

  ```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"ExampleConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```

- **OffloadingConnector:** offloads KV to CPU memory with configurable block size and CPU bytes[^disagg-prefill]:

  ```bash
  --kv-transfer-config '{"kv_connector":"OffloadingConnector","kv_role":"kv_both","kv_connector_extra_config":{"block_size": 64, "cpu_bytes_to_use": 1000000000}}'
  ```

- **FlexKVConnectorV1:** distributed KV store and multi-level cache for ultra-large-scale inference[^disagg-prefill]:

  ```bash
  --kv-transfer-config '{"kv_connector":"FlexKVConnectorV1","kv_role":"kv_both"}'
  ```

## Reusing prefill token ids on decode

For disaggregated `/v1/chat/completions`, prefill and decode both render the chat prompt from `messages` and tokenize it; the decode stage can reuse the token ids already produced by prefill to skip its own templating and tokenization[^disagg-prefill].

- Output is otherwise identical: detokenized text with tool and reasoning parsing, streaming, and structured-output constraints still applied[^disagg-prefill].
- Transport is `kv_transfer_params`, the dict already attached to the decode request[^disagg-prefill].
- Procedure: send prefill with `return_token_ids` and `do_remote_decode`, read `prompt_token_ids` from the response, then set `kv_transfer_params["prompt_token_ids"]` on the decode request with `do_remote_prefill`; `messages` is still required but not re-tokenized[^disagg-prefill]:

  ```python
  prefill = client.chat.completions.create(
      model=model,
      messages=messages,
      extra_body={"return_token_ids": True, "kv_transfer_params": {"do_remote_decode": True}},
  )
  ids = prefill.prompt_token_ids

  decode = client.chat.completions.create(
      model=model,
      messages=messages,
      stream=True,
      extra_body={"kv_transfer_params": {"do_remote_prefill": True, "prompt_token_ids": ids}},
  )
  ```

## Implementation abstractions

- **Connector:** lets the KV consumer retrieve a batch of requests' KV caches from the KV producer[^disagg-prefill].
- **LookupBuffer:** `insert` plus `drop_select` with SQL-like semantics; `insert` is non-blocking while `drop_select` is blocking[^disagg-prefill].
- **Pipe:** single-direction FIFO tensor pipe with `send_tensor` and `recv_tensor`[^disagg-prefill].
- Every vLLM process has a connector: the **scheduler connector** lives with the scheduler process and schedules transfer ops, while **worker connectors** live in worker processes and execute them[^disagg-prefill].
- Worker connectors cooperate with the attention module for layer-by-layer KV store and load[^disagg-prefill].

## Third-party extension paths

Disaggregated prefilling is infrastructure-sensitive, so production use relies on third-party connectors[^disagg-prefill]:

- **Fully-customized connector:** implement `Connector` with third-party send/recv libraries and optional model-input edits; most control, highest future-incompatibility risk[^disagg-prefill].
- **Database-like connector:** implement `LookupBuffer` with `insert` and `drop_select`[^disagg-prefill].
- **Distributed P2P connector:** implement `Pipe` with `send_tensor` and `recv_tensor`, analogous to `torch.distributed`[^disagg-prefill].

## Relationships

- Uses [vLLM Mooncake Connector](vllm-mooncake-connector.md) — RDMA zero-copy prefill-to-decode KV transfer with producer/consumer roles and proxy fan-out; this concept covers only the general split and catalog.
- Uses [vLLM MoRI-IO Connector](vllm-moriio-connector.md) — ROCm MoRI-IO prefill-to-decode KV transfer with WRITE/READ modes, RDMA/xGMI transports, and proxy routing; single-node READ/WRITE orchestration, scheduler wait, and 2.5× goodput evidence are compiled there[^moriio-single-node].
- Uses [vLLM NIXL Connector Usage](vllm-nixl-connector-usage.md) — NixlConnector install, transport, P/D deployment, bidirectional multi-turn, and metrics operation; this concept covers only the general split and catalog.
- Uses [vLLM NIXL Push-Mode KV Transfer](vllm-nixl-kv-push-connector.md) — push WRITE is one NixlConnector transfer mode for the prefill-to-decode leg; this concept covers the general prefill/decode split and connector catalog.
- Uses [vLLM Hybrid SSM Disaggregated Serving](vllm-hybrid-ssm-disaggregation.md) — hybrid Mamba-attention NIXL extension with dual descriptors and DS-layout conv transfer in `v0.20.0`; this concept covers only the general split and catalog[^hybrid-ssm-disagg].
- Uses [vLLM NIXL KV Cache Lease Renewal](vllm-nixl-kv-lease.md) — heartbeat-renewed prefill-side leases bound KV retention for the transfer; this concept covers only the general transfer need, not lease mechanics.
- Uses [vLLM Disaggregated Encoder](vllm-disaggregated-encoder.md) — sibling disaggregation pattern separating vision encoding from prefill/decode; this concept covers only the prefill/decode split.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — disaggregation decision rule, 1:3 to 1:5 pool sizing, connector selection, and NIXL failure modes for this split.

## Coverage limits

- Flow and abstraction figures at `raw/vllm/assets/features/disagg_prefill/` (`abstraction.jpg`, `overview.jpg`, `high_level_design.png`, `workflow.png`) were present but not visually inspected; synthesis follows the text alone[^disagg-prefill].
- Referenced example and test scripts under `examples/disaggregated/` and `tests/v1/kv_connector/` were not present under `raw/` and were not inspected[^disagg-prefill].
- Linked guides `nixl_connector_usage.md`, `nixl_connector_compatibility.md`, `kv_offloading_usage.md`, LMCache examples, and LMCache docs were not compiled here; connector-specific setup beyond the quoted `--kv-transfer-config` snippets is outside verified scope[^disagg-prefill].
- MooncakeConnector setup is now compiled in [vLLM Mooncake Connector](vllm-mooncake-connector.md).
- MoRIIOConnector setup is now compiled in [vLLM MoRI-IO Connector](vllm-moriio-connector.md).
- Single-node MORI-IO goodput, GPU split, and throughput-versus-goodput qualification above use the 2026-04-07 blog text plus inspected request-flow and SLO-attainment figures; KV-transfer sequence diagrams follow the text formulas[^moriio-single-node].
- NixlConnector compatibility is now compiled in [vLLM NIXL Connector Compatibility](vllm-nixl-connector-compatibility.md).
- NixlConnector usage is now compiled in [vLLM NIXL Connector Usage](vllm-nixl-connector-usage.md).

[^disagg-prefill]: Disaggregated Prefilling (experimental) — `../raw/vllm/features/disagg_prefill.md`, covering TTFT/ITL and tail-ITL rationale with no-throughput caveat, two-instance plus connector deployment, 8 enumerated connectors with config snippets, `return_token_ids` / `prompt_token_ids` reuse flow, `vllm/distributed/kv_transfer` abstractions (Connector, LookupBuffer, Pipe), scheduler versus worker connectors with layer-by-layer attention transfer, and three third-party implementation paths.

[^moriio-single-node]: AMD / Embedded LLM, Next-Level Inference: Why Your Single-Node vLLM Setup Needs Prefill-Decode Disaggregation — `../raw/2026-04-07-moriio-kv-connector/index.md` (2026-04-07), covering single-node 1P+1D on 8× MI300X, DistServe goodput with TTFT < 1 s and ITL < 50 ms (73/100 WRITE versus 26/100 1×TP8 at 8 req/s), and throughput-versus-goodput qualification.

[^hybrid-ssm-disagg]: Disaggregated Serving for Hybrid SSM Models in vLLM — `../raw/2026-04-21-hybrid-ssm-disagg/index.md` (2026-04-21), covering hybrid-SSM NIXL dual views, physical/logical bridging, DS-layout 3-descriptor transfer, and Nemotron Pareto evidence; general split and catalog remain above.
