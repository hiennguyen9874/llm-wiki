---
type: Concept
title: vLLM Disaggregated Encoder
description: Separate vision-encoder and prefill/decode instances with EC-connector embedding transfer for independent scaling, lower TTFT, and shared encoder-cache reuse.
tags: [vllm, multimodal, disaggregated-inference, vision-encoder]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:06:38Z }
sources:
  - id: disagg-encoder
    resource: ../raw/vllm/features/disagg_encoder.md
    title: Disaggregated Encoder
---

A disaggregated encoder runs the vision-encoder stage of a multimodal LLM in a separate process from the prefill/decode stage, with an encoder-cache (EC) connector transferring embeddings from the encoder instance to the prefill/decode instance to enable independent scaling, lower time-to-first-token, and cross-process encoder-output reuse[^disagg-encoder].

## Benefits

- **Independent, fine-grained scaling:** vision encoders are lightweight while language models are orders of magnitude larger; the language model can be parallelised without affecting the encoder fleet, and encoder nodes can be added or removed independently[^disagg-encoder].
- **Lower TTFT:** language-only requests bypass the vision encoder entirely, and encoder output is injected only at required attention layers, shortening the prefill critical path[^disagg-encoder].
- **Cross-process reuse and caching:** in-process encoders confine reuse to a single worker, while a remote shared cache lets any worker retrieve existing embeddings and eliminates redundant computation[^disagg-encoder].

## Deployment shapes

- **Encoder + combined prefill/decode (E→PD):** one encoder instance plus one PD instance, illustrated by `examples/disaggregated/disaggregated_encoder/disagg_1e1pd_example.sh`[^disagg-encoder].
- **Encoder + split prefill and decode (E→P→D):** one encoder instance plus separate prefill and decode instances, illustrated by `examples/disaggregated/disaggregated_encoder/disagg_1e1p1d_example.sh`[^disagg-encoder].
- The development section names the same shapes as `disagg_encoder_example.sh` (E→PD) for a single normal PD instance and `disagg_epd_example.sh` (E→P→D) for disaggregated P/D instances; both naming variants are preserved as documented[^disagg-encoder].
- The current reference pathway is **ExampleConnector**[^disagg-encoder].

## Implementation

- **Encoder instance:** a vLLM instance that performs vision encoding[^disagg-encoder].
- **Prefill/decode instance(s):** run language prefill and decode, either combined or split[^disagg-encoder].
- **EC transfer:** a connector transfers EC embeddings from the encoder instance to the PD instance; all related code is under `vllm/distributed/ec_transfer`[^disagg-encoder].
- **ECConnector:** interface for retrieving EC caches produced by the encoder[^disagg-encoder].
  - *Scheduler role:* checks cache existence and schedules loads[^disagg-encoder].
  - *Worker role:* loads the embeddings into memory[^disagg-encoder].

## Prefill-to-decode leg in E→P→D

- The prefill instance receives encoder cache the same way as the disaggregated-encoder flow, executes one step (prefill → 1 token output), then transfers KV cache to the decode instance for the remaining execution; KV transfer happens after execution of the PD/prefill instance[^disagg-encoder].
- The example setup uses **NixlConnector** from `vllm/distributed/kv_transfer/kv_connector/v1/nixl/`, referring to `tests/v1/kv_connector/nixl_integration/toy_proxy_server.py` to facilitate KV transfer between P and D[^disagg-encoder].
- Test coverage is pointed at `tests/v1/ec_connector`[^disagg-encoder].

## Relationships

- Uses [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — placeholder-to-input correspondence and processor-output caching cover the in-process multimodal path that disaggregation moves to a remote encoder instance.
- Uses [vLLM NIXL Push-Mode KV Transfer](vllm-nixl-kv-push-connector.md) — the E→P→D variant reuses NIXL KV transfer for the P→D leg; this concept covers only the E→PD encoder-cache transfer.

## Coverage limits

- The linked Google design doc was not fetched and was not compiled[^disagg-encoder].
- The flow figure at `../assets/features/disagg_encoder/disagg_encoder_flow.png` was not present under `raw/assets/` and was not inspected[^disagg-encoder].
- Example scripts, `tests/v1/ec_connector`, `vllm/distributed/ec_transfer`, the NIXL connector path, and `toy_proxy_server.py` were cited as locations but their code was not inspected in this ingest[^disagg-encoder].
- Connector configuration options, cache keys and eviction policy, and performance or TTFT measurements are outside the verified scope of this source[^disagg-encoder].

[^disagg-encoder]: Disaggregated Encoder — `../raw/vllm/features/disagg_encoder.md`, covering definition and three benefits, ExampleConnector reference pathway, E→PD and E→P→D example scripts, `tests/v1/ec_connector`, encoder versus PD roles, `vllm/distributed/ec_transfer` and scheduler/worker `ECConnector` roles, one-step prefill before P→D KV transfer, and NIXL plus toy-proxy example for the P→D leg.
