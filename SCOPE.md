# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Vision–language research KB
- **Purpose:** A research knowledge base on vision–language models and visual representation learning: how they are pretrained, adapted, scaled, evaluated, and applied, and how methods relate across papers.
- **Inclusion test:** a source or question is in scope when it yields durable knowledge about models that learn from or reason over visual data. That includes the visual side of multimodal models (image, video, document pages), together with the encoders, training data, objectives, adaptation methods, benchmarks, and deployment constraints that shape them. A non-visual ML source (for example a text-only LLM, a loss, or an architecture) qualifies only when an in-scope concept depends on it.
- **Exclusions:** text-only NLP/LLM work, speech-only work, and general ML unrelated to visual or multimodal models; marketing or news without technical substance; transient leaderboard snapshots unless the human asks for them; material the human marks as off-limits.
- **Typical sources:** arXiv papers (LaTeX packages under `raw/<arxiv-id>_<Name>/` or Markdown conversions under `raw/<arxiv-id>_<Name>.md`), model cards, and technical reports.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `vl-pretraining` | Image–text pretraining: CLIP-style contrastive/sigmoid dual encoders, captioning and unified encoder–decoder objectives, data curation, multilingual and scaling studies | `ml` | Cite the paper section, table, or equation for each objective and result. Benchmark numbers are **Reported** unless reproduced. |
| `vl-adaptation` | Adapting pretrained VL models: prompt learning, adapters, test-time adaptation, robust fine-tuning | `ml` | State the evaluation protocol (base-to-novel, few-shot k, cross-dataset, domain shift) next to any comparison. |
| `vision-encoders` | Visual backbones and foundation encoders: self-supervised, native-resolution, codec-native, MoE, and efficient CNN/ViT designs | `ml` | Record parameter count, input resolution, and the initialization or teacher lineage when the source gives them. |
| `multimodal-llms` | VLMs that connect vision to LLMs, including video, streaming, and real-time interaction | `ml` | Use `stale_after` for model releases, checkpoints, and comparisons against current models. |
| `visual-document-retrieval` | Page-image retrieval, late interaction, and VDR benchmarks | `ml` | Use `stale_after` for leaderboard-dependent claims. Name the benchmark version (for example ViDoRe v1/v2). |
| `multimodal-safety` | Image and multimodal content moderation and policy-conditioned classifiers | `ml` | Name the policy taxonomy and threshold assumptions. Do not quote harmful example content verbatim. |
| `ml` | Supporting ML architecture and general ML concepts that in-scope concepts depend on | `ml` | Use `stale_after` for framework APIs, model releases, and benchmarks. |

- Name domains as the human does; they may be broad (`health`) or narrow (`home-network`).
- A concept belongs to its primary domain through tags and, once groups exist, its group path.
- Domain rules cover things like citation style, verification expectations, or staleness windows.
- An unregistered domain uses the defaults below.
- Cross-cutting tags (`contrastive-learning`, `zero-shot-transfer`, `multilingual`, `efficient-inference`) link concepts across domains; they are not domains themselves.
- `type: Synthesis` pages may span several domains. They cite the underlying papers and label inferred claims **Synthesis**.

## Conventions

| Setting | Value |
| --- | --- |
| Default interaction mode | `autonomous` |
| Concept prose language | English (matches all existing concepts). Keep model names, method names, and technical terms in their original form. |
| Course prose language | Vietnamese, with technical keywords in English and an English gloss on first use. |
| Default course profile | `ml` |
| Source citation convention | `sources[].id` uses the arXiv ID or model-card name. Locators name the LaTeX file plus section, table, equation, or figure. |

Course profiles live in `.pi/skills/wiki-learn/references/profiles/`. A domain without a matching profile uses the default profile.

## Governance

- Registering a new domain or course-profile mapping needs no approval; record it here in the same change as the first affected concept.
- Narrowing scope, adding exclusions, or adding domain rules that change meaning, governance, or human control requires human approval, as defined in the base contract's contract evolution section.
