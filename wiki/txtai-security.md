---
type: Concept
title: txtai security boundaries
description: Configuration-dependent authentication, file and network safeguards, executable extensions, agent tools, and artifact trust limits.
tags: [security, txtai, operations]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:18:00Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac498ccbba7c4bff51886e660edd5241d04e
    title: txtai repository
---

**Observed:** txtai includes meaningful targeted controls—hashed-bearer authentication, mutation flags, safe file/URL opening, archive path validation, and gated legacy deserialization—but these do not form a global sandbox or tenant boundary. **Synthesis:** trusted startup configuration, potentially untrusted callers/model outputs, and imported models/indexes must be treated as different trust zones; safe deployment depends on the enabled composition.[^txtai-repo]

## Authentication and exposure

**Reported:** API security documentation describes the default HTTP service as fully open and recommends a TLS edge and authorization. **Observed:** built-in authorization is installed only when `TOKEN` is set; Docker's API entry point binds all interfaces without configuring TLS. The check hashes the raw bearer credential and compares it to the configured digest. It is not pass-the-hash authentication and does not itself implement roles, tenant isolation, or per-user data policy. Custom dependencies can add controls; their effectiveness was not audited.[^txtai-repo]

Configured SQL search exposes the content accessible to that application. `writable` and `reindex` are application-wide gates, not row-level authorization. A suppressed ordinary pipeline route may still be reachable through the enabled OpenAI selector. MCP authentication propagation is unresolved, not proven bypassed; see [API](txtai-api.md).[^txtai-repo]

## Trusted configuration and model loading

**Observed:** environment extension/dependency/API classes, custom factories, pipeline actions, SQL functions, and reindex function strings can resolve Python implementations. Reindex accepts replacement configuration when both mutation gates permit it. Documentation explicitly restricts reindex configuration to trusted sources.[^txtai-repo]

Model arguments can reach Hugging Face `from_pretrained`; opt-in `trust_remote_code` changes the trust boundary. **Synthesis:** permitting untrusted callers to choose reindex models, callable paths, backend classes, or remote-code options can expose process-privileged execution paths. This is a static reachability/risk finding, not a demonstrated exploit, and does not mean default model loading necessarily runs remote code. External vector string transforms have a separate `ALLOW_RESOLVE_TRANSFORM` gate.[^txtai-repo]

## Filesystem and outbound retrieval

`safeopen` constrains local reads to an allowed directory (boolean true selects the temp directory), validates remote destinations, checks redirects, and uses resolved-IP-pinned HTTP/HTTPS connections. URL retrieval defaults include a 30-second timeout and 100 MiB read limit. These controls are specific to the inspected retrieval paths; they are not parser isolation, egress control for every provider, or a complete defense against filesystem races.[^txtai-repo]

Library extraction/retrieval defaults can leave safe opening off; `Application` normally enables it for configured textractor/urlretrieve/retrieve paths. Other readers—CSV/tabular, image caption/object detection, audio transcription—and agent read/write/edit tools are not uniformly protected by that directory policy. The security docs recommend retrieval-task wrapping for otherwise unrestricted components. Review the full invocation graph, including OpenAI routing, rather than just one endpoint.[^txtai-repo]

The upload endpoint writes named temporary files; the inspected handler does not impose its own byte/count quota or expose a cleanup policy. Document backends parse those formats in process or through external tooling, without an inspected sandbox. Apply deployment limits and lifecycle cleanup rather than assuming URL read limits cover uploads.[^txtai-repo]

## Agents, tools, and remote peers

Bash uses an executable allowlist, argument-list execution, closed stdin, and timeout, and explicitly disclaims sandboxing. Allowed commands can still read process-accessible paths. The explicitly selectable default toolkit includes file operations and an external Python tool; code mode delegates execution to smolagents. Sandboxed Jinja only restricts template rendering. **Synthesis:** untrusted prompts/tool output require least-privilege execution, selected tools, and external isolation; prompt-injection resistance was not tested.[^txtai-repo]

MCP servers, shard URLs, service workflow endpoints, OpenCode, LLM providers, and cloud storage are configured peers with distinct credentials and data flows. SafeOpen should not be assumed to wrap all these clients. Cluster auth forwarding and timeout policies need explicit deployment validation; runtime library defaults remain relevant.[^txtai-repo]

## Serialized artifacts and archives

`Pickle.allow` blocks general pickle unless enabled per instance or through `ALLOW_PICKLE`; fallback/legacy configuration, reducer, array, graph, and object paths still exist. The environment override broadens trust process-wide; internally created staging pickle is a separate controlled path. Keep arbitrary shared artifacts outside that trusted set.[^txtai-repo]

Tar rejects links and validates extraction destinations; Zip also validates member destinations. Cloud storage checks download-path containment. These controls do not establish an expansion-size/compression-ratio budget or safe behavior for every native model/index format. No archive exploit or resource-exhaustion experiment ran.[^txtai-repo]

## Credential screening and limits

Two separate heuristic passes established no likely live credential in their reviewed inputs: the curator's tested private-key/provider-token patterns returned no matches, while a broader API-agent screen found two token-shaped matches and classified them as embedded-image noise and an explicitly dummy tutorial parameter. Values are not reproduced; these are distinct scans, not contradictory results from one scan. Tutorial/test placeholders are not recommended deployment secrets. This is not complete PII/secret clearance, penetration testing, vulnerability certification, or proof that no exploitable issue exists.

## Relationships

- **Constrains:** [API/MCP](txtai-api.md), [agents/workflows](txtai-agents-workflows.md), [pipelines](txtai-pipelines.md), and [persistence](txtai-persistence.md).
- **Depends on:** [Operations](txtai-operations.md) for runtime isolation, TLS/auth edge, artifact pinning, limits, and cleanup.
- **Part of:** [txtai](txtai.md); coverage and pending evidence are recorded in the [source map](txtai-source-map.md).

[^txtai-repo]: Revision `738aac498ccbba7c4bff51886e660edd5241d04e`: `docs/api/security.md`, `docs/api/configuration.md` reindex warning; `docker/api/Dockerfile`; `src/python/txtai/api/application.py::create, lifespan, createmcp`; `api/authorization.py::Authorization`; `api/routers/openai.py::chat`, `api/routers/upload.py::upload`, `api/routers/embeddings.py::reindex`; `app/base.py::Application.reindex, function, resolvetask, createpipelines`; `util/resolver.py::Resolver`; `embeddings/index/functions.py::Functions`; `vectors/dense/huggingface.py::HFVectors.loadmodel`; `models/pooling/base.py::Pooling.__init__`; `models/models.py::Models.load`; `vectors/dense/external.py::External.resolve`; `pipeline/data/safeopen.py::SafeOpen`, `pipeline/data/urlretrieve.py` URL/IP/redirect handlers; `pipeline/data/tabular.py::Tabular.__call__`, `pipeline/image/caption.py::Caption.__call__`, `pipeline/image/objects.py::Objects.__call__`, `pipeline/audio/transcription.py::Transcription.read`; `agent/tool/factory.py`, `agent/tool/bash.py`, `agent/tool/read.py`, `agent/tool/write.py`, `agent/tool/edit.py`; `agent/base.py`, `agent/factory.py`; `serialize/pickle.py::Pickle.allow`, `serialize/serializer.py::Serializer`; `archive/tar.py::Tar.unpack`, `archive/zip.py::Zip.unpack`, `archive/compress.py::Compress.validate`; `cloud/storage.py::ObjectStorage.load`; `workflow/task/service.py::ServiceTask`, `pipeline/llm/opencode.py::OpenCode`; credential-match contexts in `examples/25_Generate_image_captions_and_detect_objects.ipynb` embedded image payload and `examples/28_Push_notifications_with_workflows.ipynb` explicitly dummy commented parameter (redacted). Short module paths are relative to `src/python/txtai/`.
