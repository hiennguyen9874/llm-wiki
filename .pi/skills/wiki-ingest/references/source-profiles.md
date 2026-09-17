# Source profiles

Apply the common profile and every matching source-type profile. For mixed packages, reconcile overlapping findings once. Extract durable material for retrieval, verification, reuse, comparison, or decisions; record an explicit exclusion for an applicable field that cannot be established.

## Common

- Identity: title, creator, publisher, date, language, source kind, canonical entry point, version or revision, upstream URL, and license or disclosure boundary.
- Package: logical root, entry point, material dependencies and attachments, duplicates, and generated, cached, vendored, binary, or unavailable artifacts.
- Coverage: inspected artifacts, inspection method, execution performed, exclusions with reasons, unreadable material, and remaining limits.
- Knowledge: definitions, aliases, entities, claims, assumptions, qualifications, procedures, inputs, outputs, defaults, constraints, side effects, failure modes, and relationships.
- Evidence: measurements, units, protocol, uncertainty, negative results, contradictions, corrections, supersessions, freshness, and the best available claim locator.
- Trust: source authority, privacy, security, reproducibility, licensing, and whether each consequential finding is reported, observed, reproduced, or synthesis.

Exclude boilerplate, decorative assets, repeated examples, exhaustive narrative detail, and generated or vendored material unless they support durable knowledge.

## Code repositories and code files

- Record the fixed revision or snapshot date, license, languages, runtime/framework versions, dependencies, entry points, module architecture, public interfaces, schemas, and data or control flow.
- Capture setup, run, test, and deployment commands; configuration precedence and effective defaults; environment variables; external assets; persistence, networking, concurrency, and security boundaries.
- Inspect validation, assertions, exceptions, randomness, split handling, checkpoint selection, distributed behavior, metrics, tests, CI, and dangerous or irreversible operations.
- Reconcile documentation with implementation. Record hard-coded paths, stale scripts, dead options, missing assets, likely defects, and what static inspection, syntax checks, tests, or execution actually establish.
- Cite an immutable revision plus `path::symbol` or configuration key when available. Inventory generated, minified, cached, binary, and vendored files before excluding them.

## Research papers, LaTeX, PDFs, and books

- Follow material `\input`, `\include`, bibliography, appendix, supplement, table, and figure closure. Use structured text for prose and formulas; inspect visually significant pages and assets for information absent from the text.
- Capture bibliographic identity, version, research question, contributions, definitions, notation, assumptions, architecture, algorithms, equations, complexity, theorem dependencies, and proof limits.
- Capture datasets, splits, preprocessing, baselines, metrics, evaluation protocol, hardware, compute, hyperparameters, model selection, principal results, variance or significance, ablations, sensitivity, negative and qualitative results, and reproducibility artifacts.
- Record limitations, threats to validity, ethics, availability, and internal numerical inconsistencies. Cite sections, pages, equations, algorithms, tables, figures, or appendix labels.

## Articles, web captures, documentation, and specifications

- Capture author or organization, publisher, publication and update dates, canonical URL, local capture date, intended audience, and temporal or version scope.
- Distinguish thesis, factual reporting, opinion, promotion, recommendation, normative requirements, and firsthand evidence. Capture arguments, procedures, examples, commands, configuration, compatibility, deprecations, and migration effects.
- Record cited evidence without promoting it to firsthand verification. Note corrections, sponsorship, conflicts of interest, truncation, paywalls, stale claims, and material linked attachments.
- Cite headings, named sections, archived paragraph ranges, or requirement identifiers.

## Datasets, configurations, and structured data

- Capture producer, release/version, license, collection method, coverage period and population, consent, intended and prohibited uses, transformations, filtering, labeling, quality, bias, and checksums when available.
- Describe schema, dimensions, keys, units, field semantics, missing-value conventions, defaults, valid ranges, special identifiers, compatibility fields, and representative queries.
- Reconcile important values with documentation and consuming code. Cite table, field, key path, row range, or query; describe secrets only in redacted form.

## Images, plots, diagrams, audio, and video

- Capture creator/date, caption or transcript, diagram nodes and boundaries, arrows and data flow, plot axes, units, legends, series, conditions, material values and trends, table footnotes, screenshot state, or audio/video timecodes.
- Inspect architecture diagrams, plots, tables, screenshots, and benchmark figures unless surrounding evidence fully reproduces their material information; record the specific exclusion reason otherwise.
- Record OCR, transcription, accessibility, unreadable-region, and interpretation limits. Cite filename plus page, region, panel, or timestamp.

## Scripts and commands

- Capture invocation, environment, prerequisites, inputs, outputs, generated files, validation, errors, side effects, destructive behavior, and reproducibility requirements.
- Treat execution as a separate safety decision. Static inspection supports an observed finding; a sandboxed command or test supports a reproduced finding only to the extent of the executed conditions.
