---
title: "Generate images with Pydantic AI"
author: "David Sanchez"
site: "Pydantic"
published: 2026-09-14T09:00:00.000Z
source: "https://pydantic.dev/articles/image-generation"
domain: "pydantic.dev"
language: "en"
description: "Generate images with OpenAI, Google, or xAI through Pydantic AI. Use ImageGenerator directly or from an agent, with OpenTelemetry tracing."
word_count: 1398
---

The news upfront: you can now use dedicated image-generation models through Pydantic AI! Previously, our image-generation support went through conversational models with [image-generation abilities](https://pydantic.dev/docs/ai/tools-toolsets/native-tools/#image-generation-tool). The new [`ImageGenerator`](https://pydantic.dev/docs/ai/guides/image-generation/) gives you a direct API, without an agent run.

The same interface supports OpenAI GPT Image, Google Gemini, and xAI Grok Imagine. Google works through both the Gemini Developer API and Vertex AI. You can also give an agent access to a dedicated image model through the [`ImageGeneration` capability](https://pydantic.dev/docs/ai/capabilities/image-generation/).

If you're building your own [agent harnesses](https://pydantic.dev/docs/ai/harness/) or using Pydantic AI at your company, we'd love to hear from you on [Slack](https://pydantic.dev/docs/logfire/join-slack/). Conversations with users helped this feature happen. More on that below.

## Generate an image

Install the OpenAI extra and set your API key:

```bash
uv add 'pydantic-ai-slim[openai]>=2.41.0'
export OPENAI_API_KEY='your-api-key'
```

Then generate an illustration for a cafe's acoustic music night:

```python
from pathlib import Path

from pydantic_ai import ImageGenerator

images = ImageGenerator('openai:gpt-image-2')
result = images.generate_sync(
    'A warm, painterly illustration of acoustic live music at a cafe. '
    'No lettering or logos.'
)
Path('cafe.png').write_bytes(result.image.data)
```

`result.image` is a `BinaryImage`, with the bytes and media type available directly. For asynchronous code, use `await images.generate(...)`. You can also pass reference images through `images=` to edit or transform them.

The [image-generation guide](https://pydantic.dev/docs/ai/guides/image-generation/) covers provider setup, editing, output formats, and settings. For Google, use the `google:` prefix for the Gemini Developer API or `google-cloud:` for Vertex AI; for xAI, use `xai:`. Each provider needs its own optional dependency and credentials.

## Let an agent generate the image

The direct API leaves your application in charge of when to generate an image. With the [`ImageGeneration` capability](https://pydantic.dev/docs/ai/capabilities/image-generation/), the agent decides instead, and you get the image back in the run's messages.

This example defines an image generator and supplies it as the capability's local implementation:

```python
from pathlib import Path

from pydantic_ai import Agent, ImageGenerator
from pydantic_ai.capabilities import ImageGeneration
from pydantic_ai.messages import BinaryImage, ToolReturnPart

images = ImageGenerator('openai:gpt-image-2')
agent = Agent(
    'openai:gpt-5-mini',
    capabilities=[ImageGeneration(native=False, local=images)],
)

result = agent.run_sync(
    'Generate an illustration of acoustic live music at a cafe.'
)

generated = [
    file
    for message in result.all_messages()
    for part in message.parts
    if isinstance(part, ToolReturnPart)
    for file in part.files
    if isinstance(file, BinaryImage)
]
Path('cafe.png').write_bytes(generated[0].data)
```

`result.output` is the model's text, and the generated image comes back as a tool result, so you read it off `result.all_messages()`. The image stays in the conversation too, which is what you want when the model should go on working with what it just made: writing alt text for it, say, which is the shape of the tool example below.

Here, `native=False` ensures the capability uses the generator we configured. With `ImageGeneration(local=images)`, it prefers native image generation when the agent's model supports it and uses that generator otherwise. `ImageGeneration()` by itself is native-only: it doesn't configure a fallback for you. "Local" means a tool implementation in your application; the generator still calls the remote image provider. This is fallback based on model capabilities, not automatic failover between image providers after a failed request.

The native path uses [`ImageGenerationTool`](https://pydantic.dev/docs/ai/tools-toolsets/native-tools/#image-generation-tool) to ask the conversational model to generate an image.

## Why we added image generation

Until around March, we weren't really thinking about supporting it: image generation looked like another tool you could hand-roll and plug in.

Users asked for it, and the calculus changed. Pydantic AI is meant to be part of the de facto standard library for building AI applications in Python, the way Pydantic is for validation, and a standard library carries the things people reach for rather than leaving every team to rebuild them. We had also underestimated what integrating image generation buys:

- **Less adapter code.** `ImageGenerator` handles provider setup, request mapping, and decoding the generated image into a common result type.
- **Typed settings and earlier feedback.** Common settings such as `dimensions` and `aspect_ratio` have one interface. Provider-specific controls keep their prefixes. The adapters validate supported geometry and warn about ignored or overridden settings, though providers still enforce their own limits. The [settings guide](https://pydantic.dev/docs/ai/guides/image-generation/#settings) describes those differences.
- **Easier model comparisons.** You can try another provider through the same generation interface, adjusting credentials and any provider-specific settings. You don't need to rewrite the surrounding application to consume a different response shape.
- **Integration with the rest of the framework.** The generated `BinaryImage` can become agent input or a tool result. [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/) also has [media externalization](https://pydantic.dev/docs/ai/harness/media/) for moving large payloads out of persisted message history. Storage is configured separately; generating an image doesn't persist it automatically.
- **OpenTelemetry instrumentation.** Enable tracing on the generator and follow its calls alongside the agent and tool spans in [Logfire](https://pydantic.dev/logfire).

And, yes, we like the compact, Pydantic-style syntax.

Some people argue that boilerplate and parallel implementations across SDKs aren't much of a concern anymore, since coding agents can write them reliably. But complexity remains everybody's enemy. One implementation with a setting you can vary leaves less code to understand and fewer places for behavior to drift. As long as that keeps codebases cheaper and easier to maintain, we'll keep working on cleaner APIs.

## Write your own tool and trace it in Logfire

You can also wrap the generator in your own tool. This is useful when you want to control what the tool returns, such as passing the generated image back to the agent so it can write alt text.

For the traced example below, also install Logfire with `uv add logfire` and configure a project token through `LOGFIRE_TOKEN`. The [Logfire setup guide](https://pydantic.dev/docs/ai/integrations/logfire/) covers connecting your project.

```python
import logfire
from pydantic_ai import Agent, ImageGenerator
from pydantic_ai.messages import BinaryImage

logfire.configure()
logfire.instrument_pydantic_ai()

images = ImageGenerator('openai:gpt-image-2', instrument=True)
agent = Agent('openai:gpt-5-mini')

@agent.tool_plain
async def create_illustration(prompt: str) -> list[str | BinaryImage]:
    """Generate an illustration from a visual prompt."""
    result = await images.generate(prompt)
    return ['Illustration ready.', result.image]

result = agent.run_sync(
    'Generate an illustration of acoustic live music at a cafe. '
    'Then write alt text for it.'
)
print(result.output)
```

A tool can return a list mixing text and binary content: the text becomes the tool result the model reads, and the `BinaryImage` goes into its input as an image. `instrument=True` traces the image-generation call, `logfire.instrument_pydantic_ai()` instruments the agent, and the image preview below comes from that same list.

<iframe title="Logfire public trace: cafe illustration and alt text" src="https://logfire-us.pydantic.dev/public-trace/3a13bef7-b072-408b-bf2e-e100a3037404?spanId=1f524101c81bf21b&amp;embedded=true&amp;theme=light"></iframe>

Explore the spans above, or [open the full trace](https://logfire-us.pydantic.dev/public-trace/3a13bef7-b072-408b-bf2e-e100a3037404?spanId=1f524101c81bf21b). This recorded cafe workflow also includes a visual-brief subagent before image generation and alt text.

The trace uses Pydantic AI 2.41.0 and Logfire 5.0.0. In that version, images returned directly by the capability appear as JSON in Logfire rather than the preview shown for a tool's own binary content. We're tracking [preview parity for tool results](https://github.com/pydantic/pydantic-ai/issues/8247).

## Keeping open source fun

There's a human side to how this feature came about.

The same jump in coding-agent capabilities that let us take on more work has also changed open source. More issues and PRs arrive with help from coding agents. The volume leaves us with a sifting problem: which issues should we prioritize, and how do we coordinate who works on what?

I'll write about that in more detail another time. For now, one thing that's helped is reaching out to contributors and inviting them to talk with us on Slack.

We arranged calls to hear what they were using Pydantic AI for, their biggest pain points (in the framework and otherwise), and what they'd like to see next. Those conversations gave us opportunities to point users to newer APIs for old workarounds, learn from their tricks, and come up with bigger ideas. One example was using scratchpads to improve success rates with more complicated output types.

[Egon Ferri](https://x.com/Egon96) was particularly interested in image generation. We discussed the constraints, and he got to work on [the original PR](https://github.com/pydantic/pydantic-ai/pull/5357). Thank you, Egon, for working on this and pushing the boundaries of the framework!

That is roughly how we want this to go. A compelling feature moves fastest when someone who needs it [champions](https://pydantic.dev/docs/ai/project/contributing/#champions) it: they bring the use case, they shape the plan, and they stay through the review. It is why image generation shipped rather than sitting in the backlog, and the same door is open for whatever you need next.

Between that PR and its release, we added Pydantic AI Harness, lots of capabilities, and [Pydantic AI v2](https://pydantic.dev/articles/pydantic-ai-v2). It was finally time to get image generation out.

If you're trying this in your application, or have a workaround you think we should know about, [come talk with us on Slack](https://pydantic.dev/docs/logfire/join-slack/).
