---
name: read-arxiv-paper
description: Fetch an arXiv paper's TeX source into raw/ and compile it into the wiki. Use when the user gives an arXiv URL or ID to read or ingest.
---

# Read arXiv Paper

Capture the paper's TeX source as immutable evidence in `raw/`, then compile it through `wiki-ingest`. Prefer TeX over PDF because equations, figures, and sections stay addressable for locators.

## Steps

1. **Normalize the ID.** Extract the arXiv ID and version from forms such as `https://arxiv.org/abs/2601.07372`, `https://www.arxiv.org/pdf/2601.07372v2`, or `2601.07372`. Resolve the latest version when none is given and record it. The source URL is `https://arxiv.org/src/<id><version>`. This step is complete when the ID and version are explicit.

2. **Reconcile before fetching.** The source package is `raw/arxiv-<id><version>/`. If it already exists, do not re-download or modify it: `raw/` is immutable. A newer version is a new package. Search `wiki/` for concepts citing the package scope; complete prior coverage makes the ingest a no-op per `AGENTS.md` idempotency. This step is complete when the package is known to be new, already present, or already compiled.

3. **Fetch and unpack.** Download the source archive and unpack it into `raw/arxiv-<id><version>/`. arXiv may serve a gzipped tarball, a single gzipped `.tex` file, or a PDF when no TeX exists; handle each and fall back to the PDF only when TeX is unavailable. Do not execute anything in the package. Add a `README.md` to the package recording title, authors, arXiv ID, version, abstract URL, source URL, and capture date. This step is complete when the package and its README exist.

4. **Locate the entry point.** Find the main file (the `.tex` containing `\documentclass`, often `main.tex`) and record it in the package README. This step is complete when the canonical entry point is known.

5. **Compile into the wiki.** Follow `wiki-ingest` with the package README as `sources[].resource`, the package directory as `scope`, `kind: paper`, and the arXiv version as `revision`. Recurse through `\input`/`\include` files, bibliography, and figures as the research-paper source profile requires. This step is complete when `wiki-ingest` reports a validated mutation or a no-op.

Report the concepts created or updated. When the user asks only for a summary without filing knowledge, write it to `outputs/arxiv-<id>-summary.md` instead and leave `wiki/` unchanged.
