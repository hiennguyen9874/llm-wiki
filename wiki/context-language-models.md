---
type: Concept
title: Context Language Models: Context-as-File Self-Management
description: Context Language Models that treat live context as an editable file for zero-shot, learned, and efficiently served long-horizon agency, with ContextBench diagnostics and Suffix Cache Reuse.
tags: [context-management, agents, evaluation, serving, reinforcement-learning]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T18:30:00Z }
sources:
  - id: clm-paper-2609-37725v1
    resource: ../raw/arXiv-2609.37725v1/paper.tex
    scope: ../raw/arXiv-2609.37725v1/
    kind: paper
    revision: 2609.37725v1
    title: Context Language Models
---

# Context Language Models: Context-as-File Self-Management

Synthesis: Context Language Models (CLMs) make live context an agent-editable file instead of an append-only history, so the same model decides what to keep, rewrite, offload, or share across agents; **reported** zero-shot gains at lower prefix-reuse FLOPs, steerable/evolvable/RL-learnable policies, and a serving-side Suffix Cache Reuse optimization are the durable takeaways, while all accuracy and FLOPs figures below remain single-paper **reported** evidence[^clm-paper-2609-37725v1].

## Identity and provenance

- Paper: `Context Language Models` by Rulin Shao et al. (UW, Meta Superintelligence Labs, MIT, Trillium Labs), arXiv `2609.37725v1`; code advertised as `https://github.com/facebookresearch/context-language-models` (uninspected)[^clm-paper-2609-37725v1].
- Canonical entry is `paper.tex` (toplevel per `00README.json`), package scope `raw/arXiv-2609.37725v1/`, revision `2609.37725v1`; appendix `appendix_clean.tex`, math/table inputs, and figure PDFs form the inspected closure[^clm-paper-2609-37725v1].
- Do not conflate with [Contrastive Language Models](contrastive-language-models.md): same `CLM` acronym, different expansion and mechanism (contrastive state-action heads on frozen Qwen3-8B versus editable live context here)[^clm-paper-2609-37725v1].

## Formal definition and context-as-file implementation

- Standard LM transition appends: `c_{t+1} = c_t ⊕ f^LM_θ(c_t)`; CLM transition is model-controlled: `c_{t+1} = f^CLM_θ(c_t)` where `f^CLM` can be an arbitrary context function, subsuming harness-defined compaction/offload/retrieval tools as model-defined behavior[^clm-paper-2609-37725v1].
- **Observed** implementation: mirror live context to a file path given in the system prompt; the model uses Bash to freely edit it, edits synchronize to live context for the next turn, and non-edits default to appending generated tokens[^clm-paper-2609-37725v1].
- Multi-agent extension: multiple context files coexist and stay synchronized; an agent swarm starts with multiple files, subagents are created or terminated by creating or deleting files[^clm-paper-2609-37725v1].
- **Reported** emergent behaviors: in-context scoreboard with 163 in-place edits at 6–8K tokens, new `notes` chat role on rewrite, loops pruning search results or overlong observations, reusable `compact_turns` helper invoked 37 times, and 21K-token compression into answer-relevant summaries while preserving untried ideas[^clm-paper-2609-37725v1].

## Efficiency metric: prefix-reuse FLOPs

- Serving uses prefix-cache reuse; an in-the-middle edit forces re-prefill from the first mismatch onward under standard serving[^clm-paper-2609-37725v1].
- Metric: `FLOPs_prefix-reuse = FLOPs_prefill(unmatched suffix) + FLOPs_decode(generated tokens)`; paper **reports** all main comparisons under standard serving and counts SCR savings separately[^clm-paper-2609-37725v1].

## ContextBench diagnostic

- Purpose: isolate context management from reasoning or knowledge; agent receives operations as user messages in one conversation, controls pacing via `echo READY_FOR_NEXT_OP`, and is graded from its context (file-only answers not credited)[^clm-paper-2609-37725v1].
- Budget: 32,768-token limit with 2,048 reserved (30,720 usable); one operation must fit in one-fifth and required retention in one-half, each with 10% margin; pressure is total pushed input divided by the limit, tested up to 24×[^clm-paper-2609-37725v1].
- Four tasks: Needle Retention (selective verbatim retention over ~4K chunks with 2–8 needles plus 140 filler lines), Sudoku Sketchpad (surgical updates on a 16×16 board, exact board reproduction), KV Store (batches of 100 `SET` with 24-word values, 24 `GET`s), Log Triage (14–54-line log batches, 24 lookup/count queries)[^clm-paper-2609-37725v1].
- Pilot finding with GPT-5.4 at 32K: fixed strategies fail even these simple tasks — summary compaction loses or hallucinates needles and board state, methods without in-place editing must regenerate full Sudoku state per move, and offload-capable tools cannot always evict live context on demand[^clm-paper-2609-37725v1].

## Reported zero-shot results on long-horizon tasks

- Setup: shared Mini-SWE-Agent backbone, no training, versus MEM1, Self-Compact, ACM, and RLM; main model Qwen3.6-27B at 32K with 100-turn cap unless noted[^clm-paper-2609-37725v1].
- Deep research (BrowseComp-Plus, 830 questions): 59.4%, **reported** +11.4% relative over strongest Codex-style summary baseline, with 21.5% fewer prefix-reuse FLOPs than summary and 28.9% fewer than MEM1[^clm-paper-2609-37725v1].
- Coding: matches summary on TerminalBench 2.1 with ~70% of its FLOPs (29.5% fewer), and 73.7% versus 67.0% on TBLite with ~91% of its FLOPs[^clm-paper-2609-37725v1].
- Math optimization (Claude 4.6 Sonnet, 32K, 100 attempts or 5h): highest best-of-run on all four AlphaEvolve/OpenEvolve problems; **reported** up to +16.8% on Heilbronn and +3.0% on circle packing over specialized OpenEvolve workflows with less fixed orchestration[^clm-paper-2609-37725v1].
- Single-repo optimization (EdgeBench-10, 12h): Qwen3.6-27B 44.6 at 179 PFLOPs per trial versus summary 42.3 at 437 PFLOPs; Claude Sonnet 51.0 (50.4 with subagents) versus summary 42.3; subagents add little here[^clm-paper-2609-37725v1].
- Multi-repo swarm (Software World, six agents, 24h+, GPT-5.6-Sol at 272K): **reported** 65% greater downstream geometric-mean speedup on unseen packages at matched spend versus a summary swarm[^clm-paper-2609-37725v1].

## Learning context management in context or in weights

- Steering (`c_{t+1} = f^CLM_θ(c_t; s)`): one appended sentence changes policy — compaction threshold (16K/24K/32K, median first-compaction size), semantic boundaries (compaction within two turns of a subtask boundary), and backup discipline (fraction of edits preceded by full copy)[^clm-paper-2609-37725v1].
- Evolving (`s* = argmax_s E[R(τ(x;s))]`): GEPA-style proposer loop over rollout traces; assisted evolution (Qwen3.6-27B agent plus Claude Fable 5.1 proposer) and self-evolution (Opus 5 both roles) expand the accuracy-cost Pareto frontier on ContextBench; abstract **reports** up to +35.9 held-out points at lower compute[^clm-paper-2609-37725v1].
- Reinforcement learning: stepwise GRPO assigns trajectory outcome advantage to all constituent segments (preserving original inputs across edits); success-gated efficiency advantage `A^eff = clip((c̄_g − c_i)/c̄_g, −1, 1)` for successes else `0`, combined as `A = A^out + w_eff·A^eff` (`w_eff = 0.25` on context-management tokens in the run)[^clm-paper-2609-37725v1].
- RL outcome (Qwen3.5-9B on 3,040 OpenResearcher prompts, held-out BrowseComp-Plus): **reported** 28.8% → 42.5% (+13.7 points, +47.6%), 1.52 → 1.34 PFLOPs per question, matching a same-recipe summary harness (42.1%) at 38.8% fewer FLOPs (1.34 versus 2.19)[^clm-paper-2609-37725v1].

## Suffix Cache Reuse serving

- Idea: when `B` becomes `B'` in `[A B C]`, reuse cached states for surviving suffix `C` and only prefill `B'` plus appends, instead of re-prefilling `B'` and `C`; stale states may even retain useful past information[^clm-paper-2609-37725v1].
- Implementation (**observed** from text): diff against prior prompt, relocate up to `K = 6` longest surviving spans, re-rotate RoPE keys, splice after `B'`; session-private slots with fallback to standard re-prefill; sensitivity over `K ∈ {1,2,3,6,12,64}` on 64 BCP questions is robust with gains saturating by `K = 6`[^clm-paper-2609-37725v1].
- Hybrid models: linear-attention layers keep fixed recurrent state, so snapshot before the edit and continue from it while only full-attention layers recompute `B'` (Qwen3.6-27B noted as 48 of 64 layers linear)[^clm-paper-2609-37725v1].
- **Reported** effect on BCP with Qwen3.6-27B: matched SGLang accuracy at 65.0% of its prefix-reuse FLOPs (35% server-compute saving); of 7.8% prompt tokens reused beyond prefix hits, 5.3 points come from stripped reasoning tokens and 2.5 from other edits, so SCR also helps standard chat serving where reasoning blocks are stripped[^clm-paper-2609-37725v1].
- Remaining limit: much leftover redundant prefill is unchanged prefixes missed by current SGLang hybrid caching (recurrent states stored only at request boundaries), not SCR itself; finer checkpoints such as message boundaries are proposed[^clm-paper-2609-37725v1].

## Limitations and safety

- Gains grow with model capability: Qwen3.5-9B edits 1.4 times per TerminalBench task (no edit in half) with median peak 30.2K of 32K, versus Qwen3.6-27B at 2.6 edits and 17.6K peak[^clm-paper-2609-37725v1].
- Context-length awareness is weak at long contexts (recurring bucketed estimates such as 6.2K/9.8K/10.4K; Sonnet underestimates; GPT-5.4 aligns best); paper uses a 2,048-token pre-budget editing reminder as temporary augmentation[^clm-paper-2609-37725v1].
- Safety: editable context is a new persistence channel for prompt injection or self-generated instructions; paper cites prior compaction-summary injection observations and calls for integrity defenses that preserve flexibility[^clm-paper-2609-37725v1].
- Future: scale CLM RL and distill existing harnesses into CLM actions, framing harnesses as procedural memory or skills to be internalized[^clm-paper-2609-37725v1].

## Relationships

- Contrasts with [Conservative Jev Routing for Coding Agents](conservative-jev-routing.md): harness-isolated routing context versus intrinsic model-owned context transitions.
- Complements [Jev-Evaluated Agent Memory: Beacon Pattern](jev-evaluated-agent-memory.md): Beacon evolves reusable cross-run corrections while CLM evolves reusable context-management skill documents.
- Uses [System One Models and Jev Launch Claims](system-one-models.md) framing that fast low-cost decisions need explicit workflow-eval methodology and stated limits.
- Informs [Classifier Selection](classifier-selection.md) build-versus-harness choice where long-horizon agency cost is dominated by context re-prefill rather than single-call accuracy.

## Contradictions

- No internal numerical contradiction was resolved here; the 11.4% BrowseComp-Plus lift, 21.5%/28.9% FLOP savings, 59.4% accuracy, EdgeBench 44.6 versus 42.3, 65% swarm speedup, 35% SCR saving, and RL 28.8% → 42.5% figures are all **reported** paper claims without independent reproduction in this wiki.

## Coverage limits

- Inspected by static reading: `paper.tex` (§Intro through Discussion), `appendix_clean.tex` (related work, SCR, FLOPs, ContextBench, eval configs, RL, context awareness), `tables/open_problems_main_compact.tex`, and `00README.json` toplevel scope[^clm-paper-2609-37725v1].
- Excluded with reason: figure pixels and PDFs beyond captions and text-referenced values; `paper.bib`/`paper.bbl`, `fairmeta.cls`, `plainnat.bst`, fonts (`Optimistic.ttf`, `optimistic.tfm`), and `math_commands.tex` as formatting or generated bibliography; external code URL and model endpoints as unavailable without execution[^clm-paper-2609-37725v1].
- No code execution, benchmark reproduction, latency measurement, or image OCR was performed; serving and RL numbers are trajectory-level prefix-reuse FLOPs with o200k token counting and Qwen3.5-27B grading at temperature 0 where stated[^clm-paper-2609-37725v1].
- No credentials, private keys, tokens, or PII were found; `token` hits are language-model token counts, not secrets[^clm-paper-2609-37725v1].

[^clm-paper-2609-37725v1]: Rulin Shao et al., “Context Language Models,” arXiv 2609.37725v1, canonical local entry `../raw/arXiv-2609.37725v1/paper.tex`, package scope `../raw/arXiv-2609.37725v1/`, revision `2609.37725v1`. Locators in text: Abstract and §1 zero-shot deltas and RL/SCR headlines; §2 related-work ladder; §3 ContextBench pilot and Fig. livectxbench; §4.1 formal Eq. `c_{t+1}=f^CLM` and context-as-file plus multi-agent paragraphs with Fig. clm-examples; §4.2 steering/evolving/RL including success-gated `A^eff`; §4.3 SCR Fig. scr; §5 BCP/TB2.1/TBLite Pareto Fig. pareto_q36_main, open-problems Table open_problems_main_compact, EdgeBench/Software World Fig. long_horizon, steering/evolution Figs. steering and selfevo, RL Table rl_main, SCR Fig. suffix_cache_reuse_wip; §6 safety and harness-to-CLM future; App. extended related work, SCR full/linear and K/strip/prefix analyses, prefix-reuse FLOPs, ContextBench tasks/skills, eval configs, RL curves, and context-awareness probe.
