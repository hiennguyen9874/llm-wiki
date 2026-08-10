---
type: Concept
title: Kimi K3 XTML chat and tool encoding
description: Kimi K3’s released tokenizer renders chats as segmented XTML, isolates control tokens from user and tool text, and deterministically normalizes tools and matched tool results before tokenization.
tags: [kimi-k3, chat-template, tool-calling, tokenizer, prompt-injection]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T14:03:17Z }
sources:
  - id: kimi-k3-xstatus-2026
    resource: ../raw/KimiK3XStatus.md
    title: "深入 Kimi-K3：Hugging Face 仓库分析"
  - id: kimi-k3-tokenizer-2026
    resource: ../raw/kimi-k3-sources/tokenization_kimi.py
    title: "Kimi K3 tokenizer reference code"
  - id: kimi-k3-xtml-2026
    resource: ../raw/kimi-k3-sources/encoding_k3.py
    title: "Kimi K3 XTML chat-encoding reference code"
  - id: kimi-k3-tokenizer-config-2026
    resource: ../raw/kimi-k3-sources/tokenizer_config.json
    title: "Kimi K3 tokenizer configuration"
  - id: kimi-k3-model-card-2026
    resource: ../raw/kimi-k3-sources/README.md
    title: "Kimi K3 Hugging Face model card"
---

# Kimi K3 XTML chat and tool encoding

The released Kimi K3 tokenizer renders conversations in Python as segmented XTML rather than through a static Jinja template. It reserves four structural markers—open, close, separator, and end-of-message—and encodes only structural segments with special-token permission; message text, tool text, and attribute values are ordinary BPE text. This prevents those inputs from closing an XTML scope merely by spelling a control marker, but it does not prevent semantic prompt injection through ordinary content.[^kimi-k3-tokenizer-2026][^kimi-k3-xtml-2026]

## Rendered protocol

Messages use `message` tags with textual role and optional name attributes. Assistant messages contain `think` and `response` subtrees, with optional typed `tools`/`call`/`argument` subtrees; normal message completion is `<|end_of_msg|>` (token 163586), which is also the released generation EOS token.[^kimi-k3-xtml-2026][^kimi-k3-tokenizer-config-2026] The open, close, and separator markers are deliberately not marked as Hugging Face “special” tokens in `tokenizer_config.json`, so decoding with `skip_special_tokens` leaves the XTML skeleton visible.[^kimi-k3-tokenizer-config-2026]

When `thinking=True` (the default), every rendered assistant turn contains a `think` subtree even if no reasoning text is supplied. The model card instructs callers to preserve both prior `reasoning_content` and `tool_calls` in multi-turn history; dropping them changes the serialized context rather than merely hiding presentation data.[^kimi-k3-xtml-2026][^kimi-k3-model-card-2026]

## Deterministic tool context

Tool declarations and JSON schemas are recursively key-sorted before rendering, making equivalent mappings serialize identically. `tool_choice` and response-format constraints are added as internal system messages after the supplied conversation and before the generation prompt, so they affect the current request rather than becoming persistent history by themselves.[^kimi-k3-xtml-2026]

Before rendering a consecutive run of tool-result messages, the encoder tries to match each opaque `tool_call_id` to the most recent assistant call list. Only when all messages in that run match does it reorder them by call position and replace a supplied tool name with the matched call’s name. The implementation shallow-copies rewritten messages and is idempotent; an unmatched run remains in caller order.[^kimi-k3-xtml-2026]

## Integration boundary

This is a tokenizer-side wire format, not a guarantee that every serving engine exposes streaming tool calls or validates generated XTML. Client parsers must still validate generated names, argument types, and tool authorization. The supplied repository analysis identified these public implementation details; the compiled claims above were checked against the released tokenizer and encoder code.[^kimi-k3-xstatus-2026][^kimi-k3-tokenizer-2026][^kimi-k3-xtml-2026]

## Relationships

- **Supports:** [Kimi K3 agentic post-training](kimi-k3-agentic-post-training.md) by defining the released multi-turn and tool-call serialization boundary.
- **Uses:** [Kimi K3 native multimodal pre-training](kimi-k3-native-multimodal-pre-training.md) through the same chat path’s media placeholders.

[^kimi-k3-xstatus-2026]: “深入 Kimi-K3：Hugging Face 仓库分析,” supplied repository analysis, [raw source](../raw/KimiK3XStatus.md).

[^kimi-k3-tokenizer-2026]: Moonshot AI Team and Hugging Face, “Kimi K3 tokenizer reference code,” [source](../raw/kimi-k3-sources/tokenization_kimi.py), especially `TikTokenTokenizer._encode_text_piece` and `apply_chat_template`.

[^kimi-k3-xtml-2026]: Moonshot AI Team and Hugging Face, “Kimi K3 XTML chat-encoding reference code,” [source](../raw/kimi-k3-sources/encoding_k3.py), especially `EncodeSegment`, `build_chat_segments`, and `normalize_xtml_tool_result_messages`.

[^kimi-k3-tokenizer-config-2026]: Moonshot AI Team and Hugging Face, “Kimi K3 tokenizer configuration,” [source](../raw/kimi-k3-sources/tokenizer_config.json), `added_tokens_decoder`.

[^kimi-k3-model-card-2026]: Moonshot AI Team, “Kimi K3 Hugging Face model card,” [source](../raw/kimi-k3-sources/README.md), “Model Usage.”
