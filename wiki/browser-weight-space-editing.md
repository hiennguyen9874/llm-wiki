---
type: Concept
title: Browser-based weight-space editing
description: A reported WebGPU demo edits and compares language-model weights locally, including embedding-direction injection and model blending.
tags: [ml, interpretability, webgpu]
status: draft
created: 2026-11-09
generated: { by: llm-wiki-agent/1, at: 2026-11-09T08:28:40Z }
sources:
  - id: webweightspace
    resource: ../raw/what-is-weight-space-programming-live-demo-in-a-browser-tab-57dk/index.md
    scope: ../raw/what-is-weight-space-programming-live-demo-in-a-browser-tab-57dk/
    kind: article
    title: "What is Weight-Space Programming? Live Demo in a Browser Tab"
  - id: deep-dive
    resource: ../raw/weight-space-programming-deep-dive-tutorial-live-demo-039ca7f2230a.md
    kind: article
    title: "Weight-space programming deep dive tutorial and live demo"
---

**Reported:** webWeightSpace is a browser-based demonstration of direct neural-weight edits chosen by a user, with side-by-side generation from original and edited models. Its author describes WebGPU edits and WebLLM inference on a laptop; the demo and implementation have not been independently checked here.[^webweightspace]

## Editing interface and delivery

**Reported:** A program line has the form `<selector> <op> [args]`. Selectors target tensors, layers, or submodules; operations include scaling, zeroing, multiplicative noise, blending with a donor, skipping layers, zeroing attention heads, and injecting a word direction. For `mix a`, the article gives `w += a·(donor − w)`. It says a weight map compares corresponding tensors and highlights the selection.[^webweightspace]

**Reported:** The page downloads model files to browser Cache Storage, rewrites files containing edited tensors, and creates a model description that reuses untouched files. The article claims an injection writes roughly 180 MB rather than copying the approximately 1 GB model, and the edited model then loads from cache. It asserts computation is local and no data is uploaded; neither this privacy claim nor network behavior was verified. A WebGPU-capable browser is required, with approximately 1 GB download per example model.[^webweightspace]

## Embedding-direction injection

**Reported mechanism:** In Qwen2.5, the author says each attention layer has a value-projection bias that passes through normalized attention and, after output projection, contributes a fixed hidden-state vector to each token. The demo reportedly solves a small least-squares problem to choose bias values approximating a selected word's embedding direction. For Qwen2.5-0.5B it changes 128 values per selected layer; `layers.14-19 inject wedding 16` therefore changes 768 values across six layers. This is described as activation steering compiled into weights, not an independently verified explanation of the implementation.[^webweightspace]

**Reported example:** With identical prompts and greedy decoding, the injected model introduces weddings into unrelated answers, still answers Paris for France's capital, and answers a Python task in prose rather than code. These few examples illustrate both steering and a possible instruction-following cost; they do not establish broad capability preservation.[^webweightspace]

### Injection math and tuning

**Reported:** For an embedding `e` and strength `c`, the target is `s = c·e / ‖e‖`. With 14 query heads sharing two 64-dimensional key/value heads, the value bias has 128 entries. The tutorial constructs an 896 × 128 matrix `M` by summing the seven output-projection columns associated with each shared value dimension, then solves `argmin_x ‖Mx − s‖²` using normal equations and float64 Cholesky. The resulting `x` is added to the value-bias slice. The author reports that each selected layer expresses roughly 36–39% of the target direction; the capture does not define that percentage's precise metric.[^deep-dive]

**Reported:** On the shown prompts, `ocean` at strength 8 showed no visible effect, 12 produced fluent ocean-themed text, 16 began repeating the word, and 24 largely collapsed into repetition. The author recommends starting at 8 and increasing by 2–4, but also reports different sensitivities for other words. These are illustrative outputs, not a calibrated threshold or systematic evaluation.[^deep-dive]

## Other reported interventions

- **Blending:** `* mix 0.1` moves Qwen2.5-0.5B-Instruct 10% toward Qwen2.5-Coder-0.5B-Instruct. The author reports prompt repetition and broken code, alongside tensor cosine similarities around 0.2–0.45 for main matrices and about 0.99 for norms and biases. The proposed explanation that the interpolation leaves a functional region is an interpretation, not established by these examples alone.[^webweightspace]
- **Layer skipping:** `layers.10-12 skip` is described as zeroing two output matrices per layer. The author reports fluent but less reliable responses, including a prime function that always returns true. Skipping layers 4–6 reportedly caused a response interpreting “capital” as capitalization. These few prompts do not establish a general division of labor between early and later layers, or independently establish exact pass-through behavior.[^webweightspace][^deep-dive]
- **Head ablation:** `layers.*.attn.o_proj zero-heads 0-6` reportedly zeros the output-projection columns for half of the 14 heads in every layer and produces multilingual noise. It changes a different pattern of weights from skipping three layers; the examples do not establish that every head is necessary.[^deep-dive]
- **Noise:** `layers.* noise 0.05` reportedly multiplies selected layer weights by `1 + 0.05·N(0,1)` and preserves fluent answers in the examples, while 0.12 produces off-topic text. The source's “average 5%” is a noise-scale description, not the expected absolute percentage change; the results are not a general robustness threshold.[^deep-dive]
- **Small-tensor graft:** Copying donor layer norms and attention biases with `layers.*.*norm mix 1` and `layers.*.attn.c_attn.bias mix 1` reportedly yields tabs and punctuation despite about 0.99 tensor cosine similarity. The proposed mismatch of scales is the author's hypothesis, not an isolated causal test.[^deep-dive]

## Reported browser implementation

**Reported:** The shader packs two f16 or bf16 values per 32-bit word, processes tensors in row-aligned 16 MB chunks, and implements operations via a mode switch. Noise uses a tensor-name-seeded PCG hash and Box–Muller transform; the author claims reproducible edits. The edit shader itself is described as not requiring `shader-f16`, although the setup asks for a browser displaying `shader-f16` support; this does not establish whether inference has that requirement.[^deep-dive]

**Reported:** A generated `tensor-cache.json` points edited shards to new cached URLs and untouched shards to original absolute URLs; WebLLM reuses the original compiled model library. A program-derived hash names the build, while share URLs encode the program. Claims of zero-network loading after caching and identical rebuilt weights are not independently tested.[^deep-dive]

## Relationships

- [Weight-space programming](weight-space-programming.md) describes the related LLM-directed research; the browser demo instead lets a human choose an embedding direction or preset.
- [LLM-directed neural weight editing](llm-directed-neural-weight-editing.md) covers the separately reported model-diagnosis and targeted-repair experiment, rather than this browser demonstration.

## Evidence and coverage

The English DEV Community article by vishalmysore is dated 2026-11-04. Its local text was inspected; it reports firsthand demo observations but is also a presentation of the author's own tool. The five local screenshots were not inspected because the article text describes the examples used here; their full contents remain unverified.[^webweightspace]

The companion tutorial's local text was inspected; its capture gives no explicit author, publication date, revision, license, or capture date. Screenshot placeholders, selector/operation tables, and the final summary table are present without their visual content, so those details cannot be checked. It reports both 6.9K parameters selected and 768 bias values edited for the wedding example; the count difference is not explained in the capture. The linked live demo, source repository, models, further reading and external research were not inspected or executed. No model, shader, or browser behavior was reproduced. Claims about capabilities, privacy, measurements and results remain source-reported; draft status records these limits.[^deep-dive]

[^webweightspace]: vishalmysore, “What is Weight-Space Programming? Live Demo in a Browser Tab,” sections “Bringing weight-space programming into a browser tab,” “The weight language,” “How inject writes a concept into the weights,” “How the edited model reaches WebLLM,” “The live demo, step by step,” and “How this compares with Astra.”
[^deep-dive]: “Weight-space programming deep dive tutorial and live demo,” Parts 0–8, especially “Read the log,” “Finding the sweet spot,” “Removing parts of the model,” “Noise,” “Blending two models,” and “Under the hood.”
