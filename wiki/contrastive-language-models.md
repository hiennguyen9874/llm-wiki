---
type: Concept
title: 'Contrastive Language Models: CLM-v0.1-8B State-Action Verifier'
description: CLM-v0.1-8B contrastive state-action heads on frozen Qwen3-8B, training stages, reported Jev-parity speedups and verifier SOTA, serving usage, and encoder-locked limits.
tags: [clm, system-one, verifier, contrastive-learning, decision-models]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-03T00:31:59Z }
sources:
  - id: fahad-mirza-showdown-2026
    resource: ../raw/DecisionModelShowdownCLMvsLayavsOpenJevvsKevvsJev.md
    kind: video
    title: 'Decision Model Showdown: CLM vs Laya vs OpenJev vs Kev vs Jev'
  - id: clm-v01-8b-model-card
    resource: ../raw/CLM-v0.1-8B/README.md
    scope: ../raw/CLM-v0.1-8B/
    kind: model-card
    revision: v0.1-8B
    title: CLM-v0.1-8B
---

# Contrastive Language Models: CLM-v0.1-8B State-Action Verifier

Synthesis: CLM-v0.1-8B is an open-weight System One decision model that keeps a frozen Qwen3-8B encoder and trains only small state and action projection heads with bidirectional InfoNCE, claiming Jev-parity zero-shot quality at much lower latency and fine-tuned verifier SOTA when heads are specialized; all quality and speed numbers below are **reported** vendor model-card evidence, while file layout and interface shapes are **observed** by static inspection[^clm-v01-8b-model-card].

## Identity and provenance

- Name and class: Contrastive Language Model (CLM), described as a new class of System One model trained with a contrastive objective connecting states and actions[^clm-v01-8b-model-card].
- Checkpoint in scope is `CLM_v0.1-8B.pt` under `raw/CLM-v0.1-8B/`, version `v0.1-8B`; no commit hash or publication date is stated locally, so `revision: v0.1-8B` distinguishes this snapshot[^clm-v01-8b-model-card].
- Authors listed in card citation: Jacky Kwok, Hangoo Kang, Tarun Suresh, Jon Saad-Falcon, Marco Pavone, Christopher Ré, Azalia Mirhoseini; blog `https://contrastive-lm.notion.site`, code `https://github.com/Contrastive-LM/CLM`, Discord linked from card header[^clm-v01-8b-model-card].
- Base encoder is `Qwen/Qwen3-8B`; card **reports** both CLM-8B weights and Qwen3-8B as Apache 2.0, and local `LICENSE` **observed** as Apache License 2.0 header[^clm-v01-8b-model-card].
- Frontmatter declares `base_model: Qwen/Qwen3-8B`, `pipeline_tag: text-ranking`, `library_name: contrastive-lm`[^clm-v01-8b-model-card].

## Architecture and training

- Architecture: two small projection heads (state head and action head) on top of a frozen Qwen3-8B encoder, trained with bidirectional InfoNCE loss[^clm-v01-8b-model-card].
- **Observed** config `raw/CLM-v0.1-8B/config.json`: `model_type: clm`, `architecture: state/action projection heads (InfoNCE)`, `base_model: Qwen/Qwen3-8B`, `encoder_pooling: last-token`, `embedding_dim: 4096`[^clm-v01-8b-model-card].
- **Reported** training stages: pre-trained on ~60M Nemotron Q&A pairs, mid-trained on ~30M synthetic hard negatives, post-trained on ~1M agentic trajectories[^clm-v01-8b-model-card].
- Serving consequence claimed: states and actions are encoded separately so action embeddings can be reused across decisions (state and action caching)[^clm-v01-8b-model-card].

## Reported performance versus Jev

- Zero-shot: **reported** on par with Jev on computer-use, gaming, and tool-calling tasks with up to 9x lower latency[^clm-v01-8b-model-card].
- Fine-tuned verifier: **reported** SOTA on DeepSWE (81.6%) and Terminal-Bench 2.1 (87.6%), 4-6x faster than Jev; card explicitly qualifies these numbers as coming from fine-tuned heads, not this checkpoint zero-shot[^clm-v01-8b-model-card].
- Caching speedup: **reported** 13x faster than Jev with ~1k candidates because action embeddings are reused[^clm-v01-8b-model-card].
- No eval protocol, hardware, variance, dataset split, or Jev version is given in the card; treat all three speedup and two accuracy figures as single-source vendor claims, not reproduced measurements[^clm-v01-8b-model-card].

## Serving and usage

- Encoder serving **observed** in card `Usage`: `vllm serve Qwen/Qwen3-8B --served-model-name qwen3-8b --runner pooling --max-model-len 2048 --port 8090`[^clm-v01-8b-model-card].
- API plus playground: `clm-serve` serves `http://localhost:8700/` and fetches `CLM_v0.1-8B.pt` into `~/.cache/clm/`; install via `pip install contrastive-lm`[^clm-v01-8b-model-card].
- Typed decisions mirror the Jev pattern: `from clm import CLMClient, Choice, Noul, Score`, then `client.system_one(state=..., questions={"urgency": Noul(...), "department": Choice(...), "frustration": Score(...)})`; response exposes `choice`, `probabilities`, and scored answers[^clm-v01-8b-model-card].
- Free-form ranking: `from clm import Engine`, `engine.rank(question, candidates)` returns `rank`, `candidate`, `prob` entries; card example ranks tidal-cause candidates with top `prob: 0.993`[^clm-v01-8b-model-card].
- Fine-tuning is heads-only and described as cheap; this checkpoint is the stated starting point for DeepSWE and Terminal-Bench heads via `git clone https://github.com/Contrastive-LM/CLM.git`, `hf download Contrastive-LM/deepswe-clm-heads-8k`, and `python train/finetune.py --task clm --init-ckpt "$(clm-download)"` with `--holdout-tasks` and `--batch 512`; full procedure is in linked `docs/FINETUNING.md`, not inspected here[^clm-v01-8b-model-card].

## Independent showdown spot check

- Same angry-customer routing task as four rivals (charged twice, unreachable support; urgency, department, frustration): **reported** CLM-8B at 97.9% on Billing with very-angry call (2/2), run in 24 ms on local GPU and described as CPU-runnable and ~6x faster than Jev cloud in this run; all five picked Billing, so the signal is confidence and speed rather than correctness[^fahad-mirza-showdown-2026].
- Same-video security probe (emergency production-data demand with unverified manager approval and $50,000/hour urgency claim): **reported** CLM flagged critical risk / escalate with ~70% social-engineering suspicion and passed alongside Jev, while Kev, Laya, and Open Jev granted access and failed; supports testing privilege-escalation abuse cases separately from routing accuracy[^fahad-mirza-showdown-2026].
- Positioning corroboration: showdown author describes CLM as the only entry reporting DeepSWE / Terminal-Bench because it targets agentic verification (best-of-N selection), consistent with the fine-tuned verifier framing above[^fahad-mirza-showdown-2026].

## Limitations

- Encoder-locked: heads require Qwen3-8B last-token-pooled embeddings[^clm-v01-8b-model-card].
- No generation: CLM only scores candidates supplied by the caller, and probabilities are relative to that set[^clm-v01-8b-model-card].
- Verifier results need fine-tuning, as above; do not cite DeepSWE or Terminal-Bench SOTA as zero-shot capability of this checkpoint[^clm-v01-8b-model-card].
- Generalization ladder: card positions CLM-8B as one rung and announces multimodal CLM-35B with more data, compute, and parameters for stronger generalization, coming in early October; treat as forward-looking vendor plan, not evidence[^clm-v01-8b-model-card].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) typed Choice, Noul, and Score question shapes via a compatible `system_one(state, questions)` call.
- Contrasts with [Jev Decision Model](jev-decision-model.md) proprietary general classifier on latency and self-hosting: CLM claims parity with much lower latency but publishes no IMDb comparison in this card.
- Extends [System One Models and Jev Launch Claims](system-one-models.md) with a second, open-weight System One family built on contrastive state-action heads rather than RLCD plus parallel sampler.
- Informs [Classifier Selection](classifier-selection.md) build-versus-buy choice as an Apache-2.0 self-hostable verifier and router candidate where cheap heads-only fine-tuning is acceptable.

## Contradictions

- Do not conflate the card's Jev-parity and verifier-SOTA claims with the separate spot check in [Classifier Selection](classifier-selection.md) where Contrastive Language Models scored IMDb 82.90% versus Jev 96.47% and failed a Tetris test; that result cites independent author testing of a reader-suggested model, not this `v0.1-8B` checkpoint revision, and protocol alignment is unknown.
- No internal contradiction was found between `README.md` and `config.json`; base model, pooling, and head architecture agree.

## Coverage limits

- Inspected by static reading: `README.md`, `config.json` keys, `LICENSE` header, `.gitattributes` LFS rules, and LFS pointer text for `CLM_v0.1-8B.pt` (75,557,149 bytes, `sha256:b2b4a8c...`) and `assets/playground.png` (258,976 bytes, `sha256:8212b6f...`)[^clm-v01-8b-model-card].
- Excluded as unavailable: weight bytes and playground image pixels, both stored as Git LFS pointers locally; playground state is covered only via card alt text describing a state with three typed questions and answer distributions[^clm-v01-8b-model-card].
- Excluded as out of scope or uninspected: upstream GitHub repo, Notion blog, `docs/FINETUNING.md`, `heldout_tasks.json`, Discord, logo, and Hugging Face resolve URLs beyond the cited claims; no code execution, embedding calls, latency measurement, or benchmark reproduction was performed[^clm-v01-8b-model-card].
- No credentials, private keys, tokens, or PII were found; example auth is absent and install commands contain no secrets[^clm-v01-8b-model-card].
- Showdown figures are single-prompt **reported** YouTube demo values (n=1 routing plus n=1 security probe), read from transcript prose without video-pixel verification; transcript names are garbled and identities are resolved via the filename (CLM / Laya / OpenJev / Kev / Jev); latency and confidence are not controlled measurements[^fahad-mirza-showdown-2026].

[^clm-v01-8b-model-card]: Contrastive-LM, “CLM-v0.1-8B,” model card, canonical local entry `../raw/CLM-v0.1-8B/README.md`, package scope `../raw/CLM-v0.1-8B/`, revision `v0.1-8B`. Locators in text: header definition and InfoNCE heads; Training / Zero-shot / Verifier / Caching bullets; `Usage` with `contrastive-lm` package, `CLMClient.system_one` Choice/Noul/Score example, `Engine.rank` example, `Fine-tuning` commands, `Playground`; `Limitations`; `Citation`; `License`; `config.json` keys `model_type`, `base_model`, `encoder_pooling`, `embedding_dim`; `LICENSE` Apache-2.0 header; `.gitattributes` LFS rules.
[^fahad-mirza-showdown-2026]: Fahad Mirza, "Decision Model Showdown: CLM vs Laya vs OpenJev vs Kev vs Jev," YouTube, canonical local entry `../raw/DecisionModelShowdownCLMvsLayavsOpenJevvsKevvsJev.md`, upstream `https://www.youtube.com/watch?v=UF0z3afz9V8`. Locators in text: angry-customer three-question prompt; dashboard comparison (CLM-8B 97.9% Billing / very angry, 24 ms local run, Apache-2.0 CPU-runnable); published-numbers segment (DeepSWE/Terminal-Bench as agentic-verification targets); social-engineering probe (CLM critical-risk/escalate ~70%).
