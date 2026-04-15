# Pi Hook

## Short answer

Pi’s main hook system is **extension event hooks** via:

```ts
pi.on("hook_name", async (event, ctx) => { ... })
```

That is the primary supported way to implement hooks in pi extensions.  
Source: `docs/extensions.md:5-16, 54-99`, `README.md:327-334`.

There is also:

1. **A bash-specific `spawnHook`** for custom bash tool behavior  
   Source: `docs/extensions.md:1676-1688`
2. **SDK/session event subscriptions** via `session.subscribe(...)` when embedding pi programmatically  
   Source: `docs/sdk.md:244-304`, `dist/core/agent-session.d.ts:39-65`

---

# 1) All extension hooks supported by pi

Verified from the installed type definitions and extension docs:  
`dist/core/extensions/types.d.ts:312-728`, `docs/extensions.md:290-736`.

## Resource hooks
- `resources_discover` — add extra skill/prompt/theme paths

## Session hooks
- `session_start` — session started/loaded/reloaded
- `session_before_switch` — before `/new` or `/resume`; can cancel
- `session_before_fork` — before `/fork`; can cancel or skip restore
- `session_before_compact` — before compaction; can cancel/customize
- `session_compact` — after compaction
- `session_shutdown` — before exit/shutdown
- `session_before_tree` — before `/tree` navigation; can cancel/customize summary
- `session_tree` — after `/tree` navigation

## Agent / model / context hooks
- `context` — modify messages before each LLM call
- `before_provider_request` — inspect/replace provider payload before request
- `before_agent_start` — inject a message and/or modify system prompt
- `agent_start` — agent loop started
- `agent_end` — agent loop ended
- `turn_start` — a turn started
- `turn_end` — a turn ended
- `model_select` — model changed

## Message / tool lifecycle hooks
- `message_start` — message started
- `message_update` — assistant streaming update
- `message_end` — message ended
- `tool_execution_start` — tool started running
- `tool_execution_update` — tool emitted partial output
- `tool_execution_end` — tool finished

## Interception hooks
- `tool_call` — before tool executes; can block; can mutate args
- `tool_result` — after tool executes; can modify result
- `user_bash` — intercept `!cmd` / `!!cmd`
- `input` — intercept raw user input before skill/template expansion

## Total
**27 extension hooks**

---

# 2) Which hooks can actually change behavior?

These are the important “intercept/modify” hooks:

- `resources_discover` → returns extra resource paths
- `session_before_switch` → `{ cancel: true }`
- `session_before_fork` → `{ cancel: true }` or `{ skipConversationRestore: true }`
- `session_before_compact` → `{ cancel: true }` or custom compaction
- `session_before_tree` → `{ cancel: true }` or custom summary/instructions
- `context` → return modified `messages`
- `before_provider_request` → return replacement payload
- `before_agent_start` → return `{ message, systemPrompt }`
- `tool_call` → mutate `event.input` and/or return `{ block: true, reason }`
- `tool_result` → return partial patched result
- `user_bash` → return custom bash operations or full replacement result
- `input` → return `{ action: "continue" | "transform" | "handled" }`

Source: `docs/extensions.md:292-736`, `dist/core/extensions/types.d.ts:318-680`.

---

# 3) How to implement a hook

## Minimal extension structure

Create a TypeScript file:

- global: `~/.pi/agent/extensions/my-hook.ts`
- project-local: `.pi/extensions/my-hook.ts`

Then:

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Hook loaded", "info");
  });
}
```

Run/test quickly with:

```bash
pi -e ./my-hook.ts
```

Or place it in an extensions folder and use `/reload`.  
Source: `docs/extensions.md:7, 54-99`.

---

## Example A: block dangerous bash commands with `tool_call`

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { isToolCallEventType } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (!isToolCallEventType("bash", event)) return;

    if (event.input.command.includes("rm -rf")) {
      const ok = await ctx.ui.confirm("Dangerous command", "Allow rm -rf?");
      if (!ok) {
        return { block: true, reason: "Blocked by extension" };
      }
    }
  });
}
```

Behavior:
- runs before bash executes
- can block execution
- can also modify `event.input.command` in place

Source: `docs/extensions.md:562-600`, example `examples/extensions/permission-gate.ts`.

---

## Example B: modify the system prompt with `before_agent_start`

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("before_agent_start", async (event) => {
    return {
      systemPrompt: event.systemPrompt + "\n\nAlways answer briefly.",
    };
  });
}
```

Behavior:
- runs after user submits input
- can inject custom session message
- can replace/extend the system prompt for that turn

Source: `docs/extensions.md:416-437`, example `examples/extensions/pirate.ts`.

---

## Example C: intercept raw input with `input`

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("input", async (event, ctx) => {
    if (event.text === "ping") {
      ctx.ui.notify("pong", "info");
      return { action: "handled" };
    }

    if (event.text.startsWith("?quick ")) {
      return {
        action: "transform",
        text: `Respond briefly: ${event.text.slice(7)}`,
      };
    }

    return { action: "continue" };
  });
}
```

Behavior:
- runs before skill expansion and prompt template expansion
- can transform input or fully handle it without LLM

Source: `docs/extensions.md:692-736`, example `examples/extensions/input-transform.ts`.

---

# 4) Bash-specific hook: `spawnHook`

This is not a general event hook. It is a **bash tool option** that lets you rewrite command/cwd/env before bash execution.

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { createBashTool } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  const bashTool = createBashTool(process.cwd(), {
    spawnHook: ({ command, cwd, env }) => ({
      command: `source ~/.profile\n${command}`,
      cwd,
      env: { ...env, MY_FLAG: "1" },
    }),
  });

  pi.registerTool({
    ...bashTool,
    execute: async (id, params, signal, onUpdate) => {
      return bashTool.execute(id, params, signal, onUpdate);
    },
  });
}
```

Use this when you want to wrap bash itself rather than intercept tool calls generically.  
Source: `docs/extensions.md:1676-1688`, `examples/extensions/bash-spawn-hook.ts`.

---

# 5) “Core” / SDK event subscriptions

If by “core hooks” you mean programmatic embedding, pi also exposes session events through:

```ts
session.subscribe((event) => {
  // inspect event.type
});
```

The docs show these common SDK events:

- `message_update`
- `tool_execution_start`
- `tool_execution_update`
- `tool_execution_end`
- `message_start`
- `message_end`
- `agent_start`
- `agent_end`
- `turn_start`
- `turn_end`
- `queue_update`
- `compaction_start`
- `compaction_end`
- `auto_retry_start`
- `auto_retry_end`

Source: `docs/sdk.md:244-304`, `dist/core/agent-session.d.ts:39-65`.

Important: `session.subscribe(...)` is mainly for **observing runtime events**.  
For **changing behavior**, use **extensions with `pi.on(...)`**.

---

# 6) Recommended way to build hooks

If you want to add hooks in a real project, use this pattern:

1. Create `.pi/extensions/my-hooks.ts`
2. Export `default function (pi: ExtensionAPI)`
3. Add one or more `pi.on(...)` handlers
4. Return the proper result shape for intercepting hooks
5. Reload with `/reload`

Recommended starter:

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { isToolCallEventType } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("My hooks loaded", "info");
  });

  pi.on("tool_call", async (event, ctx) => {
    if (!isToolCallEventType("bash", event)) return;

    event.input.command = `source ~/.profile\n${event.input.command}`;

    if (event.input.command.includes("rm -rf")) {
      return { block: true, reason: "Blocked by policy" };
    }
  });

  pi.on("before_agent_start", async (event) => {
    return {
      systemPrompt: event.systemPrompt + "\n\nFollow team coding rules.",
    };
  });
}
```

---
