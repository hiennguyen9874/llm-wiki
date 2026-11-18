---
type: Concept
title: Pydantic AI capability model control
description: How a Pydantic AI capability chooses, resolves and wraps the model — get_model with ModelSelectionContext, the four-level precedence, the bootstrap lifecycle and its durable-execution limits, first-wins resolve_model_id, and the per-attempt WrapperModel hook with its batch caveat.
tags: [pydantic-ai, capabilities, models, agents]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:35:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-custom-capabilities
    resource: ../raw/capabilities/custom/index.md
    scope: ../raw/capabilities/custom/
    kind: documentation
    revision: sha256:8266876f368fff0ff3cccd0d01daa125794d6d17a79ba31ecaeb85278603fe84
    title: "Building Custom Capabilities"
---

A capability controls which model answers through three configuration slots that run at three different timescales: `get_model()` **selects** once per run or, through a selector callable, before every logical model request step; `resolve_model_id()` **resolves** an application-specific model string when no ordinary `<provider>:<model>` parsing applies, first among the capabilities that offer one; and `get_wrapper_model()` **wraps** the model that serves each individual attempt[^pydantic-docs-custom-capabilities] Together they are the fifth thing a [capability](pydantic-ai-capability-primitive.md) bundles, and the reason [models and providers](pydantic-ai-models-and-providers.md) describes resolution as a pipeline rather than a constructor.

## Selecting a model

`get_model()` returns a `Model`, a model ID string, or a sync or async callable — a `ModelSelector` — that receives a `ModelSelectionContext`[^pydantic-docs-custom-capabilities] A model or id returned directly is resolved once per run; a selector is evaluated before every logical model-request step, which is what lets one capability route a run's early steps to a cheap model and its later ones elsewhere:

```python
class AdaptiveModel(AbstractCapability[Deps]):
    def get_model(self) -> ModelSelector[Deps]:
        return self.select_model

    def select_model(self, ctx: ModelSelectionContext[Deps]) -> str:
        return 'openai:gpt-6.1-sol' if ctx.deps.task_complexity == 'complex' else 'openai:gpt-6-luna'
```

`ModelSelectionContext` is deliberately not a `RunContext`: a complete run context requires the model currently being selected, so the selection context carries what a choice can depend on without it — dependencies, the request step, the run's prompt, the messages the selected model will be sent (ending with the request being routed), usage, the run's output retry count and budget, its usage limits, deadline, `run_id` and `conversation_id`[^pydantic-docs-custom-capabilities] `get_model()` itself is a synchronous configuration method and should stay cheap; I/O belongs in an async selector.

## Precedence

A capability's model sits below the run's own arguments and above the agent constructor[^pydantic-docs-custom-capabilities]:

```
run()/iter() model argument  ›  run spec= model  ›  capability get_model()  ›  agent constructor
```

An `override(model=...)` still wins over all of these, an explicit model skips capability selection entirely, and later model contributions override earlier ones — so capability order decides which selector is consulted last, per the ordering rules in [custom capabilities](pydantic-ai-custom-capabilities.md). Fallback is complementary rather than competing: `ModelFallback` retries on another model whichever model was selected, and that fallback model is what the per-attempt wrapper below receives.

## The bootstrap lifecycle and its limits

Model selection is the one configuration that runs *before* an ordinary `RunContext` exists, and the documentation is explicit about the order because of it: bootstrap resolution uses the capability tree after `for_agent()` binding but before `for_run()`, since resolving the first model is what makes a full `RunContext` possible[^pydantic-docs-custom-capabilities] Five consequences follow:

- **A replacement can change step one.** If `for_run()` returns a replacement with a different selector, that selector makes a new step-one selection; if it returns the capability unchanged, the bootstrap selection is reused.
- **Deferred capabilities never select.** Selection and resolution are eager hooks, so a `defer_loading=True` capability contributes neither, even after it is loaded. Run-spec capabilities are known during bootstrap and can supply the first model.
- **A model-less agent cannot be bootstrapped from `for_run()`.** A `CapabilityFunc`, or any capability whose model is introduced only by `for_run()`, needs an existing bootstrap model because `for_run()` receives a full `RunContext`; it may replace that model from step one onward.
- **Durable execution cannot use a dynamic selector.** Durable runs need model IDs registered before execution and must recreate the same selected model during replay or cross-run resumption, so a durable run takes an explicit registered model, and resuming a suspended provider request in a separate ordinary run likewise requires an explicit model when the previous one came from a selector. The four durable identity and clock slots in [custom capabilities](pydantic-ai-custom-capabilities.md)' configuration table exist for the same replay requirement.
- **One step, one model.** Continuation polling within one logical step remains pinned to that step's selected model.

## Resolving a model ID

`resolve_model_id()` exists for an application-specific string that needs custom provider construction, credentials or a registry lookup — a per-user credential, say[^pydantic-docs-custom-capabilities] Unlike selection it is **first-wins**: capabilities are tried in order, and normal `infer_model()` behaviour is used only if every resolver returns `None`.

The constructor id stays a string through `for_agent()`, which is what makes the arrangement possible: a bound capability can install a resolver without default inference first constructing a provider with a different configuration or credentials[^pydantic-docs-custom-capabilities] Resolution results are cached by model id and resolver tree for the duration of one run, so a per-step selector returning the same string reuses the same model, provider and client — deliberately resolving differently on a later step means selecting a different id, or returning a `Model` instance directly from the selector.

## Wrapping the model around each attempt

`get_wrapper_model()` receives the model that will serve a model request and returns a `WrapperModel` around it, to change how the request is sent — the mechanism behind `BatchModelRequests` sending through a provider's batch API[^pydantic-docs-custom-capabilities] Two timing facts distinguish it from `get_wrapper_toolset()`:

- It is called for **every attempt at a model request**, with the model that will send that attempt: the one chosen after selection and after every `before_model_request` and `prepare_model_request` hook has run. A run that switches models partway through, or falls back to another one, therefore gets each attempt wrapped around the model serving it, whatever the capability order.
- The returned model is **entered** (`async with`) around each attempt it serves and exited when that attempt finishes or fails, the way a model passed to the agent is around a run. Per-request resources belong in its `__aenter__`; long-lived ones belong on the capability.

A wrapper's `request()` is *not* always called once per model request[^pydantic-docs-custom-capabilities] Around `BatchModelRequests`, a wrapper from a capability listed before it is called for the submission and for every check of the batch, receiving a response with `state='suspended'` until the result arrives, while one listed after it is not called at all — so counting or metering model requests belongs in a `wrap_model_request` hook instead — the capability itself is in [batch processing](pydantic-ai-batch-processing.md).

Under durable execution the request is sent from a durable unit — an activity, step or task — so the hook is called there with the model that unit rebuilds, and the wrapper sends the request[^pydantic-docs-custom-capabilities] The wrapper applied in workflow code only answers questions such as `continuation_delay`, so wrappers should be created without I/O.

## Limits

- The capture names **no Pydantic AI or model-provider version, date, author or licence**, so every method name, default and precedence rule here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-docs-custom-capabilities]
- The two samples pin `openai:gpt-6.1-sol`, `openai:gpt-6-luna` and `user:openai:gpt-6.1-sol`, aliases no other capture in this wiki corroborates; `OpenAIProvider(api_key=...)` and the `provider_factory` signature appear only as printed code.
- Unstated: what a selector should do when the model it picks has a smaller context window than the messages already assembled, whether a hook that swaps `request_context.model` mid-step re-runs capability selection for later steps, how a `ModelFallback` chain interacts with a selector's cache entry, and what per-attempt wrapping costs on a retry-heavy run.
- Nothing was installed, no capability subclassed, no selector or resolver invoked, no wrapper entered and no provider called, so every claim is **Reported** and none **Observed** or **Reproduced**. One reading is **Synthesis**: selection is last-wins and resolution is first-wins, so a string selected by the last capability is still built by whichever earlier capability offers a resolver for it — the source states the two rules separately and never combines them.

## Relationships

- **Extends** [custom capabilities](pydantic-ai-custom-capabilities.md), which owns the configuration-method contract, `for_agent` binding, per-run replacement and ordering; this page is the model half of that surface.
- **Depends on** [models and providers](pydantic-ai-models-and-providers.md) for what a resolved model string becomes: a model class, a provider and a profile.
- **Is complemented by** [model fallback](pydantic-ai-model-fallback.md): selection picks a model, fallback retries on another, and the per-attempt wrapper encloses whichever model the attempt actually uses.
- **Is constrained by** [durable execution](pydantic-ai-durable-execution.md): a registered model id is required wherever replay has to recreate the same choice.
- **Is disabled for** [on-demand capabilities](pydantic-ai-on-demand-capabilities.md): a deferred capability contributes no model even after it is loaded.
- **Is ordered by** the capability ordering rules in [custom capabilities](pydantic-ai-custom-capabilities.md), since the last capability's model contribution wins.
- **Pairs with** [prompt caching](pydantic-ai-prompt-caching.md) through the cache key: a different model is a different cache, so a per-step selector that alternates models gives each one its own prefix.

[^pydantic-docs-custom-capabilities]: Pydantic Docs, "Building Custom Capabilities" (https://pydantic.dev/docs/ai/capabilities/custom/; 13,581 words as declared, 13,832 by local `wc -w`; language `en`; no publication date, author, licence or Pydantic AI version), §"Selecting the model" (raw lines 560–606) for `get_model`'s three return forms, the per-run versus per-step timing, the `ModelSelectionContext` fields and why it is not a `RunContext`, the cheap-configuration/async-selector rule, the precedence chain, `override(model=...)`, the explicit-model skip, later-contributions-win, and the complementary `ModelFallback`; §"Resolving model IDs" (607–654) for the custom-construction use case, first-wins ordering with `infer_model` last, the string-through-`for_agent` guarantee, and the per-run cache keyed by model id and resolver tree; §"Wrapping the model" (655–712) for the per-attempt call with the model that will serve the attempt, the entered-around-attempt lifecycle, the `BatchModelRequests` submission-and-poll behaviour with `state='suspended'`, the `wrap_model_request` alternative for metering, and the durable-unit wrapper constraints; §"Model selection lifecycle and limitations" (713–720) for bootstrap-before-`for_run`, replacement step-one selection, the deferred-capability exclusion, the model-less bootstrap requirement, the durable-execution incompatibility, suspended-request resumption, and continuation polling pinned to its step; §"Providing model settings" (526–559) for the per-step settings callable that shares the attempt timing. Local capture: `raw/capabilities/custom/index.md`, content digest sha256:8266876f. Evidence class: **Reported** — vendor documentation naming no release version; no capability, selector, resolver, wrapper or provider was constructed.
