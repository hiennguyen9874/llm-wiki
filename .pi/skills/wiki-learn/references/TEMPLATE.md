# Wiki Learn — Course Template

Use this template for every `course` written by `wiki-learn`. Keep Vietnamese prose, keep keywords in English (`RoPE`, `GQA`, `KV cache`, `prefill`, `decode`, `shared experts`, `top-k`). Copy the skeleton, then delete only blocks that have an explicit omission reason in the draft PR description.

## Frontmatter

```yaml
---
type: Synthesis
title: "Tên khóa học cho người mới"
description: One English sentence for index retrieval.
tags: [kebab-tag, another-tag, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-12T00:00:00Z
sources:
  - id: short-key
    resource: wiki/some-concept.md          # preferred: wiki concept
    title: "Human title of source concept"
  - id: raw-key
    resource: ../raw/Source.md              # only when verifying raw
    title: "Raw source title"
---
```

Rules: `type`/`title`/`description` required. `created` never changes. `sources[].resource` must be stable and resolvable. One footnote key per source; footnotes use `[^short-key]` matching `id`.

## Body skeleton

```markdown
# Title (same as frontmatter title)

One-paragraph synthesis: what the mechanism is, what it replaces, and why it matters. No uncited claim.

> [!success] Kết quả cần đạt / Sau bài này
> Numbered outcomes: (1) what the reader can explain, (2) what they can implement, (3) what they can verify.

## 1. Điều cần biết trước
Prerequisites as bullets with links to wiki concepts. State what is not covered.

## 2. Lý thuyết cốt lõi
Formulas in $$, tables for variants, text diagrams for data flow.
Attribute each non-obvious claim: `[^source-id]`.

## 3. Implementation (PyTorch tối thiểu)
Short, inspectable code. Comment pairing convention, rotary_dim, position_ids, cache shape `(B, H_KV, S, d_h)` per layer when relevant.
Note where toy code diverges from serving (e.g., `torch.cat` vs paged blocks).

## 4. Xác minh trước khi benchmark
Numbered tests: identity/norm, matrix match, cache-vs-full logits, future-leakage.
Each test shows `torch.testing.assert_close` with explicit `rtol/atol` and dtype note.

## 5. Benchmark / Trade-offs (omit only if no performance claim)
Separate prefill and decode, report raw KV bytes `M_KV = 2 L B S H_KV d_h p`, state what is NOT concluded.

## 6. Debug checklist
| Triệu chứng | Nguyên nhân | Check đầu tiên |
|---|---|---|

## 7. Giới hạn & bước tiếp theo
What the lab does not establish; link to next course in roadmap.

## Relationships
- **Depends on:** [Concept](concept.md) — why
- **Uses:** [Concept](concept.md) — why
- **Elaborates:** Stage N of [Roadmap](llm-architecture-learning-roadmap.md)

## Evidence limits
One paragraph: pedagogical synthesis, source limits, what must be verified on target hardware/dtype.

[^short-key]: Source title, sections/pages cited. Secondary vs primary noted.
```

## Style constraints

- Portable relative links: `[Title](concept.md)` not `[[Wikilink]]` under `wiki/` (per `LLM-WIKI.md` contract).
- Callouts: `> [!success]`, `> [!warning]`, `> [!note]` only; keep titles short.
- Math: inline `$...$`, block `$$...$$`. Mermaid only when it clarifies flow.
- Tags: lowercase, kebab-case, shared with `wiki/index.md` vocabulary.
- Filename: `wiki/<slug>-beginners-guide.md` (or `-beginners-course.md` / `-beginners-project.md`). Slug from topic, no dates, no Vietnamese diacritics in slug.

## Provenance audit before save

- Every table row or formula either cites `[^id]` or is marked "synthesis" in the paragraph.
- `generated.at` updated only on meaningful content change.
- No credentials, tokens, or PII in prose, code, footnotes, or log.
