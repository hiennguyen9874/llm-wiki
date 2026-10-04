# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** LLM Serving KB
- **Purpose:** Durable, cited knowledge for running large language models in production and locally: serving engines, inference optimizations, kernels, quantization, speculative decoding, and the model architectures and training choices that decide serving cost and behavior.
- **Inclusion test:** a source or question is in scope when it yields durable knowledge that helps understand, choose, deploy, tune, benchmark, or debug LLM inference, or explains a model, kernel, or training choice in terms of its effect on serving (for example KV layout, MoE routing, QAT, draft-model training, or RL rollout infrastructure).
- **Exclusions:** material the human marks as off-limits; general ML unrelated to LLM inference (for example classic CV/tabular, pure research theory with no serving bearing); marketing without technical claims; personal or unrelated subjects, which belong in a separate KB repository.

## Domains

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `serving` | Engines (vLLM, SGLang, llama.cpp, Ollama, TensorRT-LLM), scheduling, KV/prefix caching, disaggregation, parallelism, deployment, observability | `ml` | Record the engine version or commit. Set `stale_after` (≤ 6 months) for flags, APIs, and compatibility matrices. |
| `models` | Model architectures, releases, and model-specific deployment | `ml` | Tie claims to the model card, paper, or config revision. Treat vendor benchmarks as **Reported**. |
| `kernels` | Attention kernels, compilers (torch.compile, Triton, TileLang), CUDA graphs | `ml` | Record the GPU architecture and dtype for performance claims. |
| `quantization` | Weight, activation, and KV quantization formats, toolchains, fidelity evaluation | `ml` | Pair accuracy claims with the benchmark, baseline, and format. |
| `speculative-decoding` | Draft methods (EAGLE, MTP, DFlash, DSpark, n-gram, …) and speculator training | `ml` | Report acceptance length together with workload and target/draft pair. |
| `training` | Pretraining, RL, QAT, and fine-tuning when they bear on served models | `ml` | Include only with a serving link stated in the concept. |

Cross-cutting benchmark rule: every performance comparison states hardware, engine versions, model, workload shape, and metric (TTFT/TPOT/throughput). Without those it is labeled **Reported** with the limit noted.

- Name domains as the human does; they may be broad (`health`) or narrow (`home-network`).
- A concept belongs to its primary domain through tags and, once groups exist, its group path.
- Domain rules cover things like citation style, verification expectations, or staleness windows.
- An unregistered domain uses the defaults below.

## Conventions

| Setting | Value |
| --- | --- |
| Default interaction mode | `autonomous` |
| Concept prose language | Match the human's request; keep technical terms in their original language. |
| Course prose language | Vietnamese, with technical keywords in English and an English gloss on first use. |
| Default course profile | `general` |

Course profiles live in `.pi/skills/wiki-learn/references/profiles/`. A domain without a matching profile uses `general`.

## Governance

- Registering a new domain or course-profile mapping needs no approval; record it here in the same change as the first affected concept.
- Narrowing scope, adding exclusions, or adding domain rules that change meaning, governance, or human control requires human approval, as defined in the base contract's contract evolution section.
