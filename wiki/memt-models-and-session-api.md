---
type: Concept
title: MemT-1.0 models and session API
description: Nano and Flash model-card configurations, example session persistence, licensing, and unverified execution boundaries.
tags: [agent-memory, model-serving, native-memory]
status: draft
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: '2026-11-08T02:52:52Z' }
stale_after: 2027-02-08
sources:
  - id: memt-paper
    resource: ../raw/arXiv-2610.26825v2-MemT-1.0/paper.tex
    scope: ../raw/arXiv-2610.26825v2-MemT-1.0/
    kind: paper
    revision: arXiv-2610.26825v2
    title: 'MemT-1.0: Towards Memory-Native Evolution'
---

The included model cards describe Nano and Flash as Hugging Face Transformers text-generation models with custom code and a session API for persisting latent local memory. The examples are **Reported** documentation, not executed or verified against model implementations or released weights.[^memt-paper]

| Model | Model ID | Example attention implementation | Model-weight license reported |
| --- | --- | --- | --- |
| Nano | `MemTensor/MemT-1.0-Nano` | `sdpa` | Apache-2.0 |
| Flash | `MemTensor/MemT-1.0-Flash` | `eager` | MIT |

Both cards specify Python 3.11+, a CUDA 13 build of PyTorch 2.11.0, Transformers 5.12.1, Accelerate 1.15.0 and Safetensors 0.8.0. Both loading examples set `trust_remote_code=True`, which permits execution of model-supplied code; review and pin the code before use. Backbone and third-party license terms remain applicable.[^memt-paper]

## Session pattern

The cards show `model.create_session(tokenizer)`, `session.chat(..., enable_memory=True)` to write interaction content and clear plaintext context, `session.save_state(path)` to include unsaved turns, then `session.close()` and `model.create_session(tokenizer, state=path)` to restore. Their example reports zero restored messages and answers from memory. A regular Transformers pipeline is also shown without memory enabled. These examples do not establish deletion, encryption, access control, or resistance to reconstruction of sensitive data from saved state.[^memt-paper]

See [architecture](memt-native-memory-architecture.md) for state geometry and [source map](memt-source-map.md) for package and inspection limits.

[^memt-paper]: `MemT-1.0-Nano.md` and `MemT-1.0-Flash.md`, frontmatter and §§ Model Family, Installation, Load the Model, A Conversation with Memory, Save and Resume, Standard Chat, License.
