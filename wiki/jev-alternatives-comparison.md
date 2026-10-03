---
type: Synthesis
title: 'Jev and Alternatives: Decision Model Comparison'
description: Comparison of documented Jev-compatible models by architecture, modalities, deployment, calibration, benchmark evidence, and workload fit.
tags: [jev, decision-models, comparison, model-selection, calibration]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T00:39:30Z }
sources:
  - id: jev-overview
    resource: jev-decision-model.md
    kind: synthesis
    title: 'Jev Decision Model: Positioning and Performance'
  - id: system-one
    resource: system-one-models.md
    kind: synthesis
    title: System One Models and Jev Launch Claims
  - id: api
    resource: jev-api-patterns.md
    kind: synthesis
    title: 'Jev API Patterns: Choice, Noul, and Score'
  - id: calibration
    resource: classifier-calibration.md
    kind: synthesis
    title: Classifier Calibration
  - id: selection
    resource: classifier-selection.md
    kind: synthesis
    title: Classifier Selection
  - id: routing
    resource: conservative-jev-routing.md
    kind: synthesis
    title: Conservative Jev Routing for Coding Agents
  - id: jev-9b
    resource: jev-9b-system1-decisions.md
    kind: synthesis
    title: JEV-9B System 1 Decisions
  - id: jev-27b
    resource: jev-27b-system1-decisions.md
    kind: synthesis
    title: JEV-27B System 1 Decisions
  - id: jev-vl
    resource: jev-27b-vl-multimodal-decisions.md
    kind: synthesis
    title: Jev-27B-VL Vision-Capable Decisions
  - id: kev
    resource: kev-decision-models.md
    kind: synthesis
    title: Kev Decision Models
  - id: clef-flash
    resource: clef-flash-multimodal-decisions.md
    kind: synthesis
    title: Clef-Flash Multimodal Joint-Schema Decisions
  - id: clef
    resource: clef-multimodal-decisions.md
    kind: synthesis
    title: Clef Multimodal Joint-Schema Decisions
  - id: omni
    resource: jev-omni-multimodal-decisions.md
    kind: synthesis
    title: Jev-Omni Multimodal Decision Classifier
  - id: openjev-tuned
    resource: openjev-decision-model.md
    kind: synthesis
    title: OpenJev Open-Weights Typed Decision Model
  - id: nimble
    resource: bespoke-nimble-decision-model.md
    kind: synthesis
    title: Bespoke Nimble Open Typed-Decision Recipe
  - id: julia
    resource: julia-1-decision-model.md
    kind: synthesis
    title: Julia 1 Decision Model
  - id: laya
    resource: laya-decision-models.md
    kind: synthesis
    title: Laya Decision Models
  - id: von
    resource: von-decision-model.md
    kind: synthesis
    title: Von Decision Model
  - id: style-v3
    resource: jev-style-0.8b-decision-v3-gguf.md
    kind: synthesis
    title: Jev-Style-0.8B Decision v3 GGUF
  - id: style-v1
    resource: jev-style-2b-decision-v1-gguf.md
    kind: synthesis
    title: Jev-Style-2B Decision v1 GGUF
  - id: neohorse
    resource: neohorse-jev-4b-decision-model.md
    kind: synthesis
    title: NeoHorse-Jev-4B Structured Decision Model
  - id: contrastive-clm
    resource: contrastive-language-models.md
    kind: synthesis
    title: Contrastive Language Models
  - id: openjev-nli
    resource: openjev-nli-cross-encoder.md
    kind: synthesis
    title: OpenJev NLI Cross-Encoder
  - id: semif
    resource: semif-open-decisions.md
    kind: synthesis
    title: SemIf Open Decisions
  - id: diffusion
    resource: openjev-diffusion-decision-server.md
    kind: synthesis
    title: OpenJev Diffusion Decision Server
  - id: sglang
    resource: openjev-sglang-decision-serving.md
    kind: synthesis
    title: OpenJev-SGLang Decision Serving
  - id: context-clm
    resource: context-language-models.md
    kind: synthesis
    title: Context Language Models
---

# Jev and Alternatives: Decision Model Comparison

**Synthesis:** choose a decision-model category before choosing a checkpoint: hosted generalist, Jev-distilled student, independently trained typed-decision model, specialized verifier, or frozen-model serving baseline. The compiled evidence does not establish a universal winner. Jev is a hosted generalist reference; AutoTrust JEV models target teacher-distribution fidelity; Kev emphasizes customizable open deployment; Clef emphasizes joint multimodal questions; and small encoders, quantized models, and verifiers address distinct workload constraints. API compatibility alone does not establish interchangeable quality, calibration, or execution semantics.[^selection][^api]

## Scope and evidence

This comparison covers the models substantively documented in the maintained wiki at the 2026-10-03 compilation, including secondary model variants and pointer-only alternatives where noted. It is not an exhaustive inventory of every external Jev alternative. Model details below inherit the underlying concepts' reported measurements and static observations; no model benchmarks or live API calls were reproduced for this synthesis. **Workload fits and shortlist recommendations are synthesis, not independently verified rankings.**[^selection]

## Identity and name collisions

The common contract is `state + question + allowed answers → probabilities + typed decision`. TypeSafe Jev is proprietary. AutoTrust JEV-9B/27B/VL are independent students trained partly on Jev distributions; Jev-Omni and Jev-Style explicitly do not use Jev-output training. Kev, Clef, Laya, Julia, Von, and Nimble are distinct alternatives, not official TypeSafe versions.[^api][^jev-9b][^jev-27b][^jev-vl][^omni][^style-v3][^style-v1]

| Ambiguous name | Actual project and mechanism |
|---|---|
| [OpenJev `openjev/openjev`](openjev-decision-model.md) | Tuned Qwen3.8-27B model with option-letter readout.[^openjev-tuned] |
| [OpenJev NLI `AlexWortega/openjev`](openjev-nli-cross-encoder.md) | Qwen3.5 premise–hypothesis entailment cross-encoder.[^openjev-nli] |
| [OpenJev diffusion `razorback16/openjev`](openjev-diffusion-decision-server.md) | DiffusionGemma decision server plus routed models.[^diffusion] |
| [OpenJev-SGLang](openjev-sglang-decision-serving.md) | Qwen3.6-35B-A3B serving experiment using selected-token logprobs.[^sglang] |
| [SemIf, formerly OpenJev](semif-open-decisions.md) | No-training direct-logit baseline over frozen models.[^semif] |

**Synthesis:** never combine these projects' benchmark results, licensing, or deployment requirements. Also distinguish [Contrastive Language Models](contrastive-language-models.md), a candidate-scoring model, from [Context Language Models](context-language-models.md), an editable-context agent approach rather than another typed-decision checkpoint.[^contrastive-clm][^context-clm]

## Jev and larger alternatives

Architecture, modalities, and limits are documented claims; the fit column is synthesis. Context capacity, default serving limits, and demonstrated task accuracy are different quantities.

| Model / family | Architecture and training | Coverage and practical limits | Workload fit and principal caveat |
|---|---|---|---|
| [TypeSafe Jev](jev-decision-model.md) | Proprietary; vendor describes parallel typed decisions and RLCD; detailed architecture/training undisclosed | Hosted Choice/Noul/Score; launch documentation describes cardinality up to 255 | General decisions without hosting or training; closed weights, network dependency, and workload-specific failures.[^jev-overview][^system-one] |
| [JEV-9B](jev-9b-system1-decisions.md) | Frozen Qwen3.5-9B plus LoRA and decision head; distills full Jev distributions | Text; 2–16 Choice options; separate base-model generation path; about 18 GB weights | Short-list routing/moderation; weaker unfamiliar-family and 16-option discrimination.[^jev-9b] |
| [JEV-27B](jev-27b-system1-decisions.md) | Frozen Qwen3.8-27B plus LoRA/head; same distillation approach | Text; 2–256 Choice options through serving adaptation; native 256K context; about 54 GB weights | Local teacher-behavior reproduction and larger option sets; more hardware, with long-context evidence mainly needle retrieval.[^jev-27b] |
| [JEV-27B-VL](jev-27b-vl-multimodal-decisions.md) | JEV-27B decision components with vision; head trained only on text | Text/images; 2–256 options; documented eight-concurrent-sequence serving limit to avoid wrong probabilities | Screenshot/agent judgment; image calibration not systematically established.[^jev-vl] |
| [Kev](kev-decision-models.md) | Qwen pointer-head family; smaller models use LoRA, 27B full fine-tuning; no Jev-output training | 0.8B/4B/9B/27B; text; 1–255 choices; CUDA/MLX; validated context 8K for smaller models, 64K for 27B | Open deployment and domain adaptation; order sensitivity, date arithmetic, and hard knowledge remain weaknesses.[^kev] |
| [Clef-Flash](clef-flash-multimodal-decisions.md) | Qwen3.5-9B plus joint-schema head | Text/JSON/images/video; decision encoder defaults to 16K total input; about 18.8 GB backbone weights | Fast joint tool/workflow decisions; substantial intent-OOS and hallucination-detection gaps.[^clef-flash] |
| [Clef](clef-multimodal-decisions.md) | Qwen3.8-27B plus the same joint-schema mechanism | Text/JSON/images/video; same default encoding limit; about 54.7 GB backbone weights | Intent-OOS, hallucination detection, invoice/security workflows; slower than Flash, not better everywhere.[^clef] |
| [Jev-Omni](jev-omni-multimodal-decisions.md) | Gemma 4 12B multimodal backbone plus 256-output head; independent training | Text/image/audio/video; accepts 256 options but best supported at ≤20; 30-second audio, 16-frame video; CUDA loader | All-four-modality coverage; heavy runtime memory and limited high-cardinality quality evidence.[^omni] |
| [OpenJev tuned 27B](openjev-decision-model.md) | Qwen3.8-27B derivative; first-position option-letter logits and fixed calibration | Text and one image in primary path; 52 options/pass, approximate hierarchy above; 16K served context; FP8/MLX/GGUF variants | Local text and browser/desktop decisions; weights are **CC BY-NC 4.0**, not unrestricted commercial-use weights; MLX/GGUF builds are text-only.[^openjev-tuned] |
| [Bespoke Nimble](bespoke-nimble-decision-model.md) | Qwen3.5-9B LoRA; curated contrastive examples and one-token codes; not Jev-distilled | Text-only flat enum/boolean schema; latest supports 255 choices and 8K input; training used 2K | Inspectable curation/training recipe; narrow synthetic holdout and checkpoint-dependent calibration.[^nimble] |

**Synthesis:** a multi-question API request is not proof of one shared computation. Clef jointly reads the schema, Kev isolates questions, and tuned OpenJev scores one question per forward pass. These choices affect cross-question interaction and shared-state efficiency.[^api][^kev][^clef][^openjev-tuned]

## Small, CPU, and on-device models

| Model | Mechanism and size | Practical envelope | Workload fit and caveat (synthesis) |
|---|---|---|---|
| [Julia 1](julia-1-decision-model.md) | 144.3M mmBERT-small encoder plus per-option marker head | Multilingual text; CPU/CUDA; native 2–20 options; 8K runtime input; about 550.5 MiB FP32 weights | Small local classification/routing; no fitted calibration; hierarchical routing to 4,096 candidates can lose the correct answer, and final probabilities are conditional on survivors.[^julia] |
| [Laya](laya-decision-models.md) | ModernBERT/mmBERT plus marker scorer and proper-scoring-rule RLCD | English 421M, multilingual 322M, typed-workflow 421M; default 512/1,024-token envelopes; multilingual runtime can extend to 8K | Fast multilingual/specialized classification; not established as broad zero-shot Jev replacement; option budgets and label wording matter.[^laya] |
| [Von](von-decision-model.md) | 395M ModernBERT; typed decisions plus deterministic temporal/numeric chains | English-only; CPU/OpenVINO, CUDA/ROCm/MPS; 8K default state limit | CPU deployment with recalibration/escalation; chains add tail latency; default Noul band is not the raw posterior.[^von] |
| [Jev-Style 0.8B v3](jev-style-0.8b-decision-v3-gguf.md) | Qwen3.5-0.8B; per-option yes/no verdict-slot logits | Text; 0.53 GB Q4_K_M; 25,600-token total input budget; option chunking; custom `jev-score` runtime | Tiny download and longer input budget; requires dedicated scorer, not ordinary chat inference.[^style-v3] |
| [Jev-Style 2B v1](jev-style-2b-decision-v1-gguf.md) | Qwen3.5-2B; option-letter readout with temperature folded into weights | Text; 1.3 GB Q4_K_M; 26 letter labels, bundled logprob client limited to 20 | Simpler LM Studio/llama.cpp integration; older generation with weaker typed-workflow results.[^style-v1] |
| [NeoHorse-Jev-4B](neohorse-jev-4b-decision-model.md) | NeoHorse/Qwen3.5-4B unified backbone with Kev-derived pointer-head runtime | Text plus one image; 2K text-state limit; up to 16 text questions; single-question image requests; CUDA/BF16 | Smaller text-plus-vision deployment; no calibration metrics or common-protocol latency comparison reported.[^neohorse] |

**Synthesis:** Julia is the smallest encoder in this compared set; Jev-Style v3 targets tiny quantized longer-input deployment; Von targets English CPU serving with refitting; Laya targets script-routed multilingual specialization; NeoHorse targets smaller unified text/image deployment. Those roles do not establish general accuracy parity with Jev.[^julia][^style-v3][^von][^laya][^neohorse]

## Verifiers, baselines, and serving systems

| Alternative | Distinction | Evaluation boundary |
|---|---|---|
| [Contrastive CLM-8B](contrastive-language-models.md) | Frozen Qwen3-8B with separate state/action projection heads and reusable candidate embeddings | Candidate scoring/head-specialized verification; DeepSWE/Terminal-Bench results require fine-tuned heads, not just the released zero-shot checkpoint.[^contrastive-clm] |
| [OpenJev NLI](openjev-nli-cross-encoder.md) | Recommended 4B v5, plus 0.8B/2B and older/MoE variants; independent entailment scoring per option | Reranking/faithfulness/order invariance; per-option compute, no fitted typed-decision calibration, demonstrated injection weakness, explicitly contaminated benchmark panels.[^openjev-nli] |
| [SemIf](semif-open-decisions.md) | Frozen-model direct option logits with shared-state reuse; no training | Auditable baseline; quality depends on model/prompt/backend/quantization; no equivalence to Jev's undisclosed training.[^semif] |
| [OpenJev diffusion server](openjev-diffusion-decision-server.md) | DiffusionGemma 26B total/4B active; masked answer slots, optional repeated reads/thinking | Text/image multi-question NVIDIA/MLX serving; compiled broad matched accuracy/calibration evidence insufficient to declare parity.[^diffusion] |
| [OpenJev-SGLang](openjev-sglang-decision-serving.md) | Qwen3.6-35B-A3B; prefix warmup plus one-token branch calls | Serving pattern, not an established accuracy leader; source recommends native SGLang decisions endpoint instead.[^sglang] |
| Verdict 1.4 | Routed 151M ModernBERT-base/GLiClass-style model; 512-token input, 24 options | Indirect repository coverage only; server removes insufficient-evidence option and renormalizes.[^diffusion] |
| JevK5 0.2 | Routed Qwen3.5-4B distilled-LoRA model with letter readout; 16K limit | Reports 86.6% on 231 public JevBench items and serving parity; evidence here is indirect through server documentation.[^diffusion] |

## Benchmark comparisons and interpretation

All figures are **reported**, not reproduced here. Comparisons are interpretable within their own evaluations, not as a merged leaderboard. Interpretations are synthesis.

| Evaluation | Reported comparison | Supported interpretation and boundary |
|---|---|---|
| IMDb, 25,000 reviews | Jev Choice 96.47%; Noul 96.20% | Strong sentiment result; training contamination unknown.[^jev-overview] |
| AutoTrust six-group text suite | JEV-27B 84.07 vs hosted Jev 83.85 | Near parity in this suite; 0.22-point difference not universal superiority.[^jev-27b] |
| AutoTrust distribution fidelity | JEV-27B KL ≈0.017; JEV-9B ≈0.019 against Jev distributions | Teacher imitation, not independent correctness.[^jev-27b][^jev-9b] |
| 16-option human-gold pressure set | JEV-27B 74.0%; Jev 76.9%; JEV-9B 69.4% | Larger student better preserves teacher accuracy as discrimination gets harder; option-order seeds differ between reruns.[^jev-27b][^jev-9b] |
| OpenJev matched 10,000 text questions | Jev 85.4%; tuned OpenJev 84.0%; base 80.4%; Nimble 75.7% | Useful near-hosted comparison; 3,078 questions development-used, 6,922 fresh.[^openjev-tuned] |
| Nimble 324-example holdout | Jev 93.21%; Nimble 90.12%; base 9B 66.36% | Curation helps on narrow synthetic set: 162 related pairs from six source families.[^nimble] |
| OpenJev NLI, 231 public JevBench items | Jev 86.6%; NLI v5 81.4%; SemIf 4B 81.0% | Competitive public-item result; judge tier unmeasured; v5 contamination excludes other named panel benchmarks from valid ranking.[^openjev-nli] |
| Omni DecisionBench Medium | Jev 90.48%; Omni 87.57% | Some text accuracy traded for modality coverage; cost plot uses proxy pricing, not measured hosting spend.[^omni] |
| Opper Jev vs Kev-4B | Within two points on fresh tasks; PAWS 87.0% vs 74.5% | Overall near parity does not remove task-specific paraphrase gap; vendor-reported comparison, unreproduced.[^jev-overview] |

### Clef, Clef-Flash, and Jev

Cloudflare's **reported** internal Decision Index 0.2.1 and workflow runs show that larger is not uniformly better. Scores are percentages except latency; RAGTruth is F1. Workflows use consensus reference labels, not a new independent human-gold evaluation.[^clef][^clef-flash]

| Metric | Clef-Flash | Clef | Jev |
|---|---:|---:|---:|
| CLINC150 + out-of-scope | 66.8 | **97.4** | 89.3 |
| RAGTruth hallucination F1 | 35.6 | **79.4** | 76.5 |
| MMLU-Pro | 65.3 | 65.9 | **82.7** |
| BBH | 68.9 | 73.7 | **92.9** |
| Invoice exact actions | 57.1 | **64.7** | 61.8 |
| Customer-service exact actions | **77.0** | 76.3 | 76.0 |
| Median request latency, ms | **38.8** | 209.3 | 524.1 |

**Synthesis:** shortlist Clef over Flash for these intent-OOS/hallucination/invoice cases, Flash for lower-latency joint decisions, and Jev for the documented hard-reasoning rows. Do not generalize the latency table to different hardware, request shapes, network locations, or cold starts.[^clef][^clef-flash]

## Calibration and interoperability

**Synthesis:** a field named `confidence` is not automatically calibrated P(correct), and distributions are conditional on supplied options. Distribution concentration, winning-option probability, display formatting, and correctness calibration must be distinguished.[^calibration][^api]

| Family | Calibration boundary |
|---|---|
| Jev | Vendor claim with task-level corroboration, but reported probability bias and repeat variation also exist.[^calibration] |
| JEV-9B/27B | Very small ECE is reported alongside teacher-fidelity evaluation; do not infer near-perfect real-world correctness calibration or transfer it to images/new tasks.[^jev-9b][^jev-27b][^jev-vl] |
| Kev | Fitted per-model temperatures and held-out/domain-refit workflow; local thresholds still required.[^kev] |
| Laya | Type/option buckets and domain fitting; multilingual defaults do not ship the same fitted buckets.[^laya] |
| Jev-Style | v3 global/group temperatures; v1 folded temperature; calibration does not prove new-domain quality.[^style-v3][^style-v1] |
| Nimble | Original release fitted temperature; latest defaults to uncalibrated T=1; merged-weight calibration gap remains.[^nimble] |
| Von | Local refit available; default Noul band output is not raw posterior, so gate on raw values.[^von] |
| Julia / NeoHorse / OpenJev NLI | No fitted calibration established for documented typed-decision outputs.[^julia][^neohorse][^openjev-nli] |
| Clef | Decision-confidence calibration evidence not compiled; ForecastBench Brier is not a substitute for a reliability evaluation of decision confidence.[^clef][^clef-flash] |

**Synthesis:** do not transfer a threshold such as 0.8 between models. Evaluate retained coverage, error rate, and calibration on held-out workload labels; measure downstream success and fallback/retry cost, not only argmax accuracy.[^calibration][^selection]

## Workload shortlist

These are **synthesis recommendations for evaluation**, not universal endorsements or independent verification.

| Requirement | Shortlist | Decision basis |
|---|---|---|
| Avoid model infrastructure | Jev | Hosted generalist reference.[^jev-overview] |
| Reproduce Jev locally | JEV-27B; JEV-9B for smaller short lists | Distribution distillation plus documented speed/memory tradeoff.[^jev-27b][^jev-9b] |
| Customizable permissive model family | Kev | Reported Apache-2.0 family and fine-tune/refit workflow; dataset rights remain separate.[^kev] |
| Fast joint text/image/video decisions | Clef-Flash | Joint head and reported latency; evaluate intent-OOS and hallucination weaknesses.[^clef-flash] |
| Intent-OOS/hallucination detection | Clef | Stronger than Flash on documented rows.[^clef] |
| Audio plus text/image/video | Jev-Omni | Explicit four-modality support; check memory and ≤20-option best support.[^omni] |
| Screenshot/agent judging | JEV-27B-VL; tuned OpenJev | Relevant applied results; image calibration, serving constraints, and non-commercial OpenJev licensing matter.[^jev-vl][^openjev-tuned] |
| Tiny laptop model with longer input budget | Jev-Style 0.8B v3 | 0.53 GB quantization and 25.6K budget; dedicated runtime required.[^style-v3] |
| Small multilingual encoder | Julia; Laya multilingual | Local multilingual paths; evaluate exact labels, language, and calibration.[^julia][^laya] |
| English CPU deployment with recalibration | Von | OpenVINO path and frozen-weight refit; raw/band distinction and chain latency matter.[^von] |
| Faithfulness/reranking | OpenJev NLI; contrastive CLM | Candidate-judgment mechanisms; task-specific training, contamination, and security boundaries apply.[^openjev-nli][^contrastive-clm] |
| No-training baseline | SemIf | Separates serving-system gains from training gains.[^semif] |

**Synthesis:** no compared model should be the sole authority for high-stakes authorization, shell execution, destructive actions, or irreversible evidence deletion. Preserve deterministic permissions and action validation, test adversarial states, and keep abstention/fallback outside the model. Conservative routing provides an advisory-versus-executive boundary; documented NLI injection failures show why candidate-scoring quality alone is not a security guarantee.[^routing][^openjev-nli]

## Partial coverage and unresolved comparisons

- Pointer-only or comparator-level coverage includes djev, Simplejev Qwen variants, Reflex-4B, Decider-2B/4B, AutoJev-27B, Mica, Deem, hopper, jeff, GLiNER/GLiClass, DeBERTa/NLI/reranker baselines, and OpenAI Decisions API. These are not sufficiently documented here for a complete architecture/deployment ranking; AutoTrust JEV-27B is distinct from `denis-pplx/autojev-27b`.[^selection][^jev-27b][^von]
- Older Kev generations and Jev-Style 2B v2 are partially covered, not independently compared in this synthesis.[^kev][^style-v1]
- Classifier.dev, Jev Ultrafast, compaction, routing, and Beacon are services/application patterns, not separate base models.[^selection]
- **Synthesis:** claims of broad Jev parity, narrow specialist wins, and fine-tuned workflow wins answer different questions. No common controlled benchmark across every listed model resolves a universal winner; teacher fidelity, human correctness, order robustness, calibration, and safety need separate evaluation.[^selection][^jev-27b][^openjev-nli][^calibration]

## Relationships

- Uses [Classifier Selection](classifier-selection.md) for the build/buy/specialize decision framework; this page adds a model-by-model comparison surface.
- Uses [Jev API Patterns](jev-api-patterns.md) to distinguish compatible wire formats from computation semantics.
- Uses [Classifier Calibration](classifier-calibration.md) to constrain threshold transfer and confidence interpretation.
- Uses [Conservative Jev Routing](conservative-jev-routing.md) as the advisory-versus-executive deployment boundary.
- Compares the linked model concepts; checkpoint-specific provenance, contradictions, and setup detail remain maintained there rather than duplicated here.

## Coverage limits

- Compiled from the cited maintained concepts, not from transient conversation as evidence; the saved response supplied the editorial outline only. No new raw-source inspection, external research, weight loading, model execution, or API calls were performed for this synthesis.
- Inherits source-level coverage limits: unavailable weights/LFS attachments, uninspected linked harnesses, project-reported results, unequal hardware/network timing, synthetic or teacher labels, development-used examples, and contaminated benchmark panels. Structural validation is not model verification.
- The intended comparison coverage is the documented families above plus explicitly partial pointers, not every checkpoint or every external alternative. Device/option/context claims are snapshot-specific; capacity or smoke-test success does not establish task accuracy.
- Recommendations are conditional on task, label wording/count, context, hardware, licensing, calibration, robustness, and fallback cost. Consult each linked concept and live release documentation before deployment.

[^jev-overview]: [Jev Decision Model](jev-decision-model.md), “Identity and positioning,” “IMDb measurement,” “Opper side-by-side: Kev-4B vs Jev,” and “Coverage limits”; reported benchmarks and architecture uncertainty.
[^system-one]: [System One Models](system-one-models.md), “What System One means,” “Workflow eval methodology,” and “Side-by-side, hallucination, and fun demos”; vendor architecture/cardinality claims, not independent correctness guarantees.
[^api]: [Jev API Patterns](jev-api-patterns.md), “Common invocation,” “Choice API,” “Score API,” and “DIY single-head retrofit”; interface and per-family execution distinctions.
[^calibration]: [Classifier Calibration](classifier-calibration.md), “What calibration means,” “Temperature scaling,” “Field calibration corroboration,” and “Coverage limits”; differing metrics, confidence semantics, and workload validation.
[^selection]: [Classifier Selection](classifier-selection.md), “Decision rule,” “Agent-harness and practical uses,” “Clones and alternatives,” and “Coverage limits”; decision framework, partial pointers, and downstream-success metrics.
[^routing]: [Conservative Jev Routing](conservative-jev-routing.md), “Routing boundary,” “Abstention-preserving fallback,” and “Safe rollout defaults”; advisory classification versus local executive control.
[^jev-9b]: [JEV-9B](jev-9b-system1-decisions.md), “Identity and provenance,” “Blocks-of-Experts recipe,” “System 1 fidelity,” “Benchmarks and JEV-9B vs JEV-27B,” and “Serving mechanics”; teacher labels, 16-option pressure scores, memory, calibration and execution limits.
[^jev-27b]: [JEV-27B](jev-27b-system1-decisions.md), “System 1 fidelity,” “JEV-27B vs JEV-9B,” “Public and independent benchmarks,” “Choice scale, prompts, context,” and “Coverage limits”; teacher-distribution match versus human-gold correctness and wide-label/context boundaries.
[^jev-vl]: [JEV-27B-VL](jev-27b-vl-multimodal-decisions.md), “Zero-shot vision claim,” “Reported applied results,” “Serving mechanics,” and “Coverage limits”; text-trained head, image-calibration gap, eight-sequence serving constraint.
[^kev]: [Kev](kev-decision-models.md), “Models and owner-reported accuracy,” “Kev 1.0 pinning,” “API and question isolation,” “Architecture,” “Training and fine-tuning on own data,” and “Limitations”; size ladder, validated context, calibration, license, and isolated execution.
[^clef-flash]: [Clef-Flash](clef-flash-multimodal-decisions.md), “Architecture,” “Record encoding and decision API,” “Reported Decision Index results,” “Reported workflow evals,” and “Coverage limits”; joint schema, modalities, default length, benchmark/latency/calibration boundaries.
[^clef]: [Clef](clef-multimodal-decisions.md), “Architecture,” “Record encoding and decision API,” “Reported Decision Index results,” “Reported workflow evals,” and “Coverage limits”; larger-sibling comparisons, memory, and missing confidence-calibration evidence.
[^omni]: [Jev-Omni](jev-omni-multimodal-decisions.md), “Identity and provenance,” “Architecture,” “Multimodal input handling,” “Reported benchmarks,” and “Speed, requirements and limits”; independence, modalities, option envelope, Medium figures and proxy pricing.
[^openjev-tuned]: [OpenJev tuned weights](openjev-decision-model.md), “Identity and license,” “Mechanism,” “Reported accuracy,” “Serving recipe,” and “Formats”; 10,000-item protocol, 52-letter/hierarchical readout, one-image/16K serving and text-only quantized variants.
[^nimble]: [Bespoke Nimble](bespoke-nimble-decision-model.md), “Serving and schema interface,” “Dataset,” “Held-out evaluation,” “Probability temperature,” and “What it cannot do”; non-distillation recipe, narrow paired synthetic holdout, latest versus original calibration.
[^julia]: [Julia 1](julia-1-decision-model.md), “Identity and lineage,” “Typed interface,” “Resident runtime,” “Reported evaluation,” and “Limits”; 144.3M model, 2–20 native options, conditional hierarchical probabilities and calibration null.
[^laya]: [Laya](laya-decision-models.md), “Identity and checkpoints,” “Architecture,” “Router and inference controls,” “Calibration,” and “Honest limits and failure modes”; script routing, budgets, fitted buckets, and specialization versus zero-shot boundaries.
[^von]: [Von](von-decision-model.md), “Identity and distribution,” “Confidence gating,” “Wire protocol and serving,” “Chain-of-options,” “Local recalibration,” and “Benchmarks”; English-only CPU model, raw/band semantics, chains, and indirectly documented comparators.
[^style-v3]: [Jev-Style v3](jev-style-0.8b-decision-v3-gguf.md), “Identity and lineage,” “Readout, budgets, and calibration,” “GGUF files and parity,” “Runtime and serving,” and “License and trust limits”; independent 0.8B verdict readout, 0.53 GB quantization, input budget, scorer and data-rights caveats.
[^style-v1]: [Jev-Style v1](jev-style-2b-decision-v1-gguf.md), “Identity and lineage,” “Readout, prompt, and calibration,” “GGUF files and reported parity,” and “Scope, training data, and limits”; 2B letter readout, folded temperature, option cap and partially covered v2.
[^neohorse]: [NeoHorse-Jev-4B](neohorse-jev-4b-decision-model.md), “Architecture and composition,” “Text interface and serving,” “Vision,” and “Limitations and trust boundaries”; unified backbone, Kev-derived runtime, input constraints and uncalibrated distribution statistics.
[^contrastive-clm]: [Contrastive CLM](contrastive-language-models.md), “Architecture and training,” “Reported performance versus Jev,” and “Limitations”; state/action embeddings, candidate reuse, heads-only fine-tuning and zero-shot versus specialized verifier results.
[^openjev-nli]: [OpenJev NLI](openjev-nli-cross-encoder.md), “Mechanism,” “Typed decisions,” “Checkpoints,” “Reported accuracy,” “Determinism and order invariance,” and “Weaknesses and trust limits”; per-option entailment, public-item results, train-on-test panels and injection failures.
[^semif]: [SemIf](semif-open-decisions.md), “Mechanism,” “Quality,” “Calibration,” and “Coverage limits”; frozen-model baseline, shared-prefix reuse, workload temperatures and interface-pattern versus model reproduction.
[^diffusion]: [OpenJev diffusion server](openjev-diffusion-decision-server.md), “Identity, license, and models,” “Mechanism,” “Backends and reported latency,” and “Routed models: serving notes and limits”; DiffusionGemma, Verdict and JevK5 mechanisms and indirect evidence.
[^sglang]: [OpenJev-SGLang](openjev-sglang-decision-serving.md), “Identity and freshness,” “Inference mechanism,” and “Limits and configuration”; distinct Qwen3.6 model, N+1 readout, non-calibrated entropy confidence and native-endpoint recommendation.
[^context-clm]: [Context Language Models](context-language-models.md), “Identity and provenance” and “Formal definition and context-as-file implementation”; acronym disambiguation and editable-context rather than typed-decision scope.
