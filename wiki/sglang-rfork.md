---
type: Concept
title: SGLang R-Fork
description: Zero-copy GPU-to-GPU weight loading for SGLang via R-Fork with NCCL and TransferEngine backends for seconds-scale boot-up.
tags: [sglang, r-fork, weight-loading, nccl, transfer-engine]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:37:22Z }
sources:
  - id: sgl-rfork
    resource: ../raw/sglang/advanced_features/rfork.mdx
    title: R-Fork
  - id: sgl-p2p-update
    resource: ../raw/2026-04-29-p2p-update/index.md
    title: "Updating 1T parameters in seconds — P2P weight transfer in Large Scale Distributed RL"
---

R-Fork (Tensor Remote Fork) loads model tensors from a running SGLang seed instance to a new client instance over an inter-node GPU-to-GPU path with zero-copy, reducing weight-loading boot-up time from minutes to seconds[^sgl-rfork].

## Configuration options

Set on the client to enable R-Fork[^sgl-rfork]:

- `--load-format remote_instance`: enables R-Fork.
- `--remote-instance-weight-loader-backend`: `nccl` or `transfer_engine`; default is `nccl`.
- `--remote-instance-weight-loader-seed-instance-ip`: IP address of the seed instance providing weights.
- `--remote-instance-weight-loader-seed-instance-service-port`: port the seed instance HTTP server listens on.
- `--remote-instance-weight-loader-send-weights-group-ports`: list of available ports on the seed instance for building NCCL communication groups between seed and client; NCCL backend only.
- `--remote-instance-weight-loader-start-seed-via-transfer-engine`: starts the seed service supporting TransferEngine; needed on seed instances when using `transfer_engine`.

## NCCL backend usage

Seed instance runs normally[^sgl-rfork]:

```bash
python -m sglang.launch_server [args]
```

Client instance pulls weights from the seed[^sgl-rfork]:

```bash
python -m sglang.launch_server [args] \
  --load-format remote_instance \
  --remote-instance-weight-loader-seed-instance-ip [seed_instance_ip] \
  --remote-instance-weight-loader-seed-instance-service-port [seed_instance_service_port] \
  --remote-instance-weight-loader-send-weights-group-ports [send_weights_nccl_group_ports_list] \
  --remote-instance-weight-loader-backend nccl
```

## TransferEngine backend usage

Seed instance must start the TransferEngine-capable seed service[^sgl-rfork]:

```bash
python -m sglang.launch_server [args] \
  --remote-instance-weight-loader-start-seed-via-transfer-engine
```

Client instance pulls weights from the seed without NCCL group ports[^sgl-rfork]:

```bash
python -m sglang.launch_server [args] \
  --load-format remote_instance \
  --remote-instance-weight-loader-seed-instance-ip [seed_instance_ip] \
  --remote-instance-weight-loader-seed-instance-service-port [seed_instance_service_port] \
  --remote-instance-weight-loader-backend transfer_engine
```

## Relationships

- Related to [SGLang P2P Weight Transfer for RL](sglang-p2p-weight-transfer.md) — P2P RL update path reuses R-Fork weight-registration info and TransferEngine seed-service mechanism[^sgl-p2p-update].
- Uses [SGLang Checkpoint Engine Integration](sglang-checkpoint-engine.md) — alternative fast weight-loading path that shards disk reads and pushes weights via checkpoint-engine workers, versus R-Fork's running-instance GPU-to-GPU transfer.

## Coverage limits

- No parallelism, model-compatibility, versioning, failure-handling, security, or measured speedup numbers beyond the minutes-to-seconds claim were in the source[^sgl-rfork].
- Linked R-Fork blog was not inspected[^sgl-rfork].

[^sgl-rfork]: R-Fork — `../raw/sglang/advanced_features/rfork.mdx`.

[^sgl-p2p-update]: Updating 1T parameters in seconds — P2P weight transfer in Large Scale Distributed RL — `../raw/2026-04-29-p2p-update/index.md`, covering R-Fork registration-info reuse for RDMA P2P weight updates.
