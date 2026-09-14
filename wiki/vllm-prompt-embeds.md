---
type: Concept
title: vLLM Prompt Embedding Inputs
description: Passing precomputed prompt/token embeddings directly to vLLM offline and via OpenAI-compatible Completions and Chat APIs.
tags: [vllm, embeddings, inference]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: prompt-embeds
    resource: ../raw/vllm/features/prompt_embeds.md
    title: Prompt Embedding Inputs
---

vLLM accepts precomputed prompt embeddings that bypass the token-ID to embedding-matrix lookup, for both decoder-only text flows and multimodal data, with offline input via `vllm.inputs.EmbedsPrompt` and online input via Completions and Chat Completions APIs gated by `--enable-prompt-embeds`[^prompt-embeds].

## Concept

- The standard text flow goes text to token IDs via a tokenizer, then token IDs to prompt embeddings; for a decoder-only model such as `meta-llama/Llama-3.1-8B-Instruct` the second step is normally a lookup in a learned embedding matrix, but the model can process embeddings beyond its token vocabulary[^prompt-embeds].
- Hugging Face Transformers model outputs can be passed into the `prompt_embeds` field of the prompt-embedding dictionary[^prompt-embeds].

## Offline inference

- Multimodal-style input follows the schema in `vllm.inputs.EmbedsPrompt`[^prompt-embeds].
- `prompt_embeds` is a torch tensor of shape `(sequence_length, hidden_size)`, where sequence length is the number of token embeddings and hidden size is the model embedding size[^prompt-embeds].

## Online serving

- The OpenAI-compatible server accepts prompt-embedding inputs through both the Completions API and the Chat Completions API, enabled by the `--enable-prompt-embeds` flag to `vllm serve`[^prompt-embeds].
- Example launch: `vllm serve meta-llama/Llama-3.2-1B-Instruct --runner generate --max-model-len 4096 --enable-prompt-embeds`[^prompt-embeds].

### Completions API

- Prompt-embedding inputs are added via a `prompt_embeds` key in the JSON request body, passed as base64-encoded torch tensors[^prompt-embeds].
- When a single request mixes `prompt_embeds` and `prompt` inputs, the prompt embeds are always returned first[^prompt-embeds].
- The Completions endpoint does not apply a chat template to `prompt_embeds`; when the model assumes a chat template, the caller must produce embeddings for the full already-templated prompt, baking in anything the model needs such as system prompt, role markers, and generation prompt[^prompt-embeds].

### Chat Completions API

- Prompt embeddings are included as `prompt_embeds` content parts inside chat messages, interleaved with text parts[^prompt-embeds].
- Each part carries a `data` field with a base64-encoded `torch.Tensor` of shape `(num_tokens, hidden_size)`; multiple parts may appear in any message and in any position relative to text parts[^prompt-embeds].
- The server expands each part into the correct number of placeholder tokens during chat-template rendering, then splices the precomputed embeddings into the model input at the corresponding positions[^prompt-embeds].
- Unlike the Completions API, a Chat `prompt_embeds` part should encode only the content, not a templated conversation; the server wraps the chat template around the embedded content at request time the same way as for a plain-text content string, so embedding a full templated conversation would double-apply the template and produce incorrect model inputs[^prompt-embeds].

## Trust boundary

- The vLLM engine may crash if embeddings with an incorrect shape are passed, so only enable this flag for trusted users[^prompt-embeds].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — offline `LLM` versus `vllm serve` online paths for the same prompt-embedding inputs.
- Uses [vLLM Multimodal Inputs](vllm-multimodal-inputs.md) — adjacent input path for per-modality media and cached inputs; see that concept when the input is modality data rather than direct prompt embeddings.

## Coverage limits

- Referenced example clients `examples/features/prompt_embed/prompt_embed_offline.py` and `examples/features/prompt_embed/prompt_embed_inference_with_openai_client.py`, the `vllm.inputs.EmbedsPrompt` symbol, and the linked OpenAI Completions and Chat Completions API docs were absent from `raw/` or are external code/API paths and were not inspected[^prompt-embeds].

[^prompt-embeds]: Prompt Embedding Inputs — `../raw/vllm/features/prompt_embeds.md`, covering prompt-embedding concept and decoder-only lookup bypass, offline `EmbedsPrompt` `(sequence_length, hidden_size)` schema and Hugging Face inputs, online `--enable-prompt-embeds` Completions `prompt_embeds` key with base64 tensors and no chat template versus Chat `prompt_embeds` content parts with server-side template wrapping, mixed-input ordering, example serve command, and trusted-user shape warning.
