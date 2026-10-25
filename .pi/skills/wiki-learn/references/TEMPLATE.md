# Wiki Learn — Course Template

Use this domain-neutral template for every `course` written by `wiki-learn`. The course profile selected from `SCOPE.md` (`references/profiles/<profile>.md`) fills the practice, verification, and trade-off blocks and adds domain vocabulary. Write prose and headings in the course prose language from `SCOPE.md`; keep technical keywords as that file specifies. Copy the skeleton, then delete only blocks that have an explicit omission reason.

## Frontmatter

```yaml
---
type: Synthesis
title: "Course title for beginners"
description: One sentence for index retrieval.
tags: [domain-tag, topic-tag, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-12T00:00:00Z
sources:
  - id: short-key
    resource: some-concept.md               # preferred: wiki concept, relative to this file
    title: "Human title of source concept"
  - id: raw-key
    resource: ../raw/Source.md              # only when verifying raw
    title: "Raw source title"
---
```

Prefer wiki concepts as `sources[]`, relative to the course file; cite `raw/` only for claims verified there. Include the primary domain as a tag.

## Body skeleton

```markdown
# Title (same as frontmatter title)

One-paragraph synthesis: what the topic is, what problem it solves or replaces, and why it matters. No uncited claim.

> [!success] Outcomes
> Numbered outcomes: (1) what the reader can explain, (2) what they can do or build, (3) how they can check it.

## 1. Prerequisites
Bullets with links to wiki concepts. State what is not covered.

## 2. Core theory
Definitions, mechanisms, and models. Use formulas, tables, or text diagrams when they clarify; explain every symbol and step for a beginner.
Attribute each non-obvious claim: `[^source-id]`.

## 3. Practice
The profile's hands-on block: runnable code, worked example, procedure, exercise, or case study.

## 4. Verification
Numbered checks the reader can perform to confirm understanding or correctness, as defined by the profile.

## 5. Trade-offs (omit only if no comparative or performance claim)
Alternatives, costs, and limits; state what is NOT concluded.

## 6. Troubleshooting checklist
| Symptom | Cause | First check |
|---|---|---|

## 7. Limits & next steps
What the course does not establish; link to the next course or concept.

## Relationships
- **Depends on:** [Concept](concept.md) — why
- **Uses:** [Concept](concept.md) — why
- **Elaborates:** [Concept or roadmap](concept.md) — why

## Evidence limits
One paragraph: pedagogical synthesis, source limits, and what must be verified in the reader's own context.

[^short-key]: Source title, sections/pages cited. Secondary vs primary noted.
```

## Style constraints

- Relative Markdown links (`[Title](concept.md)`), per the contract.
- Callouts: `> [!success]`, `> [!warning]`, `> [!note]` only; keep titles short.
- Math: inline `$...$`, block `$$...$$`. Mermaid only when it clarifies flow.
- Tags: lowercase, kebab-case, shared with `wiki/index.md` vocabulary.
- File name: `<slug>-beginners-guide.md` for an explanation, `-beginners-course.md` for a sequenced lesson, `-beginners-project.md` for a build-and-verify lab. The slug is the topic in ASCII kebab-case, with no dates or diacritics.
- Every table row, formula, and procedural step cites `[^id]` or sits in a paragraph labeled synthesis.
