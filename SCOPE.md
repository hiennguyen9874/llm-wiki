# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Diffusion image-generation knowledge base
- **Purpose:** Compile durable, comparable knowledge about diffusion and flow-matching image generation and editing models — base checkpoints, fine-tunes, distilled/few-step variants, adapters (LoRA, ControlNet), quantized builds, companion encoders/prompt rewriters — and the local inference tooling that runs them, to support model selection, setup, and compatibility decisions.
- **Inclusion test:** a source or question is in scope when it yields durable knowledge about how an image (or closely related video) generative model works, what a checkpoint, adapter, or quant is and how it relates to its base, its license and hardware needs, or how to run it locally.
- **Exclusions:**
  - Generated images, prompt galleries, and sample prompts beyond the minimum needed to document a usage convention.
  - Sexualized or NSFW prompt/output detail; uncensored or refusal-ablated releases are documented only for technical facts (base, method, packaging, license, risk), never for how to produce restricted content.
  - Real-person identities in likeness/lookalike adapters: names, per-person trigger rosters, and reference images are not reproduced.
  - General LLM, NLP, or ML topics unrelated to image/video generation (keep them for a separate KB).
  - Material the human marks as off-limits.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `image-models` | Base, fine-tuned, distilled, and quantized image generation/editing checkpoints, plus adapters (LoRA, ControlNet) and companion encoders/prompt rewriters | `ml` | State license, parameter size, and base model when the source gives them; derivatives link their base under `## Relationships` (`Depends on`/`Uses`); VRAM, speed, and quality claims are **Reported** unless reproduced; set `stale_after` (~6 months) on release, compatibility, and setup guidance. |
| `inference-tooling` | Local runtimes and frameworks: ComfyUI and custom nodes, stable-diffusion.cpp, diffusers, llama.cpp for rewriters | `ml` | Pin a revision or version when known; set `stale_after` (~6 months) on install steps, CLI flags, and supported-model lists. |
| `diffusion-theory` | How latent diffusion and flow-matching pipelines, schedulers, VAEs, conditioning, and distillation work | `ml` | Prefer papers or primary docs; label analogies and inferences **Synthesis**. |

- Name domains as the human does; they may be broad (`health`) or narrow (`home-network`).
- A concept belongs to its primary domain through tags and, once groups exist, its group path.
- Domain rules cover things like citation style, verification expectations, or staleness windows.
- An unregistered domain uses the defaults below.

## Conventions

| Setting | Value |
| --- | --- |
| Default interaction mode | `autonomous` |
| Concept prose language | English; keep model names, file names, and technical terms verbatim. |
| Course prose language | Vietnamese, with technical keywords in English and an English gloss on first use. |
| Default course profile | `general` |

Course profiles live in `.pi/skills/wiki-learn/references/profiles/`. A domain without a matching profile uses `general`.

## Governance

- Registering a new domain or course-profile mapping needs no approval; record it here in the same change as the first affected concept.
- Narrowing scope, adding exclusions, or adding domain rules that change meaning, governance, or human control requires human approval, as defined in the base contract's contract evolution section.
