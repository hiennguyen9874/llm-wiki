---
type: Concept
title: Headroom reported benchmarks and tests
description: Reported context-compression savings, benchmark methodology differences, and unexecuted test coverage.
tags: [agent-memory, benchmarks]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:19:57Z }
stale_after: 2027-05-06
sources:
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
---

**Reported:** the README's four seeded agent-output scenarios report input-token savings of 21%, 57%, 42%, and 30%, and supply `uv run python benchmarks/index_proof_table.py --seed 20260902` as a reproduction command. These are project results for those scenarios, not a general guarantee of savings or answer equivalence.[^headroom]

**Observed:** a committed proof-table result and multiple benchmark scripts exist; `benchmarks/conftest.py` includes a mock token counter, so results from different scripts need not use the same measurement method. Python, Rust, TypeScript, parity and end-to-end test surfaces are present. None of the project's tests, benchmarks, builds, or external-provider evaluations was run in this ingest.[^headroom]

The documentation and older unpublished source wiki contain different benchmark versions and scenario figures; compare the dataset and procedure before interpreting them as contradictions. QA evaluation requires external credentials according to the benchmark documentation.[^headroom]

[^headroom]: `README.md` § Proof; `benchmarks/index_proof_table.py`; `benchmarks/results/index_proof_table.txt`; `benchmarks/conftest.py::MockTokenCounter`; `docs/content/docs/benchmarks.mdx` methodology and evaluation callout; `.github/workflows/ci.yml` pytest shards; `sdk/typescript/package.json` scripts; `Cargo.toml` workspace; revision `2b0315b`.
