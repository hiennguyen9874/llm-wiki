---
type: Concept
title: Pydantic AI workspace file authority
description: What trust level a workspace's own files carry when a capability puts them in the prompt — the operator, user and none levels, how path_authority resolves per file, and what authority does not restrict.
tags: [pydantic-ai, workspaces, sandboxing, prompt-injection]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:25:00Z }
stale_after: 2027-01-16
sources:
  - id: pydantic-workspace-docs
    resource: ../raw/core-concepts/workspace/index.md
    scope: ../raw/core-concepts/workspace/
    kind: documentation
    revision: sha256:106c823ceb0c9563c3569f0dc7dac59f8a7e88365b54f2dc10bc3c3df5c09871
    title: "Workspaces"
---

A workspace's files are not the operator's voice by default. Pydantic AI gives each workspace an `authority` level describing who wrote the files in it — `'operator'`, `'user'` or `'none'` — and capabilities that lift a workspace file into the prompt are expected to carry that level with the text, so a cloned third-party repository cannot speak to the model with the same standing as the application's own instructions. The setting governs prompt provenance only: it does not restrict what the agent's tools can read, write or run[^pydantic-workspace-docs]

## The three levels

The model treats an agent's instructions as the operator speaking, so a capability that would put workspace text there assigns it no more authority than the file itself carries. A capability part whose source is `await WorkspaceSource.from_workspace(workspace, path)` asks the workspace for the file's level, and Pydantic AI renders the text accordingly[^pydantic-workspace-docs]:

| Level | Meant for | Rendered as |
| --- | --- | --- |
| `'operator'` | Files the application's side wrote | The application's voice |
| `'user'` | The user's own files, such as their uploads | The user's turn |
| `'none'` | Files nobody on the application's side wrote, such as a cloned third-party repository | Framed data |

`LocalWorkspace` takes the level directly, and tools keep working as before — the agent reads, edits and runs commands in the workspace either way[^pydantic-workspace-docs]:

```python
agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[LocalWorkspace('./checkout', authority='none')])
```

Built-in capabilities that load workspace files into instructions check `authority` as they adopt the setting[^pydantic-workspace-docs] The [Harness](pydantic-ai-harness.md) workspace capabilities — `E2BSandbox`, `DockerContainer`, `SSHWorkspace` — accept the same `authority` and `path_authority` arguments for a sandbox, container or host filled with files the operator did not write, but their paths are paths on that environment, so `~` is not expanded[^pydantic-workspace-docs]

## Authority by path

One workspace can hold files of different authorship: a vendored dependency inside the operator's repository, or the operator's own instruction files beside a cloned third-party repository. `path_authority` gives directories and files their own level, overriding `authority` underneath them[^pydantic-workspace-docs]:

```python
LocalWorkspace(
    './checkout',
    authority='none',
    path_authority={'~/.config/my-app': 'operator', 'docs/upload': 'user'},
)
```

`authority_of(path)` resolves a file's level by these rules, all of which the source states as documented behaviour rather than as a sample[^pydantic-workspace-docs]:

- The longest matching path wins, so a lower directory can sit inside a higher one, and the reverse.
- Relative paths resolve against the working directory. `LocalWorkspace` expands `~`; `AuthorityWorkspace` takes workspace paths as written and refuses one starting with `~`.
- A file outside the working directory is outside the workspace at `'none'`, unless `path_authority` lists a path containing it.
- Symlinks are followed, and a file takes the **lower** of the level where its path is written and where it leads: a link from a `'none'` directory to an `'operator'` file is at `'none'`, and so is a link from an `'operator'` directory to a `'none'` file. In a chain, the links on the path itself count and so does the final target, but not a link reached only through another link's target.
- Paths also match ignoring case, keeping the lower level, so on a case-insensitive filesystem `Vendor/` cannot escape a lower `vendor/`.
- Without `path_authority`, every file in the working directory sits at `authority`.

For a single run, wrap the workspace in `AuthorityWorkspace(workspace, authority=...)` and pass it as `workspace=`; see [workspace selection](pydantic-ai-workspace-selection.md). A wrapper only ever lowers the level — with several, the lowest wins, and a wrapper's `path_authority` never raises a level another wrapper set[^pydantic-workspace-docs]

## When the level is read

A capability asks when it reads a file and keeps the level with the text rather than asking again each time it sends it, so a symlink changed later cannot change the requests a conversation has already made. The consequence for an operator is that lowering a workspace's authority applies from the next read: text already added to a conversation stays in that history, so a lowered authority needs a new conversation[^pydantic-workspace-docs]

## What authority is not

- **Not access control.** `path_authority` sets the authority of text a capability puts in the prompt, not what the agent can read, write or run — the agent's tools reach every path as before. Limiting actions is the job of [tool approval](pydantic-ai-deferred-approvals.md) or a [sandbox](pydantic-ai-workspaces-and-sandboxes.md)[^pydantic-workspace-docs]
- **Not a label on tool output.** What a tool returns, such as a file `read_file` read, is tool output whatever the workspace's authority[^pydantic-workspace-docs]
- **Not stable under concurrent change.** A file's level reflects where its path leads when it is read, and symlinks can change[^pydantic-workspace-docs]

## Limits

- The source is Pydantic's own documentation page for workspaces, names no Pydantic AI release version, and reports no measurement; every claim here is **Reported**[^pydantic-workspace-docs]
- The rendering-by-voice table is prose in the source: no sample shows a capability part being assembled from `WorkspaceSource.from_workspace`, and the built-in capabilities said to check `authority` are not named, so which capability actually honours the level is not established[^pydantic-workspace-docs]
- The symlink and case-folding resolution rules carry several exceptions in one paragraph and were not exercised against a workspace; only the `path_authority` example is shown[^pydantic-workspace-docs]
- No workspace, capability or model request was created here, so no prompt was inspected to confirm that a `'none'` file is framed as data rather than read as an instruction[^pydantic-workspace-docs]

## Relationships

- **Qualifies** [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md): that page records the `ctx.workspace` surface; this one records the provenance attached to the files it exposes.
- **Is set on** the workspace capabilities [Pydantic AI Harness](pydantic-ai-harness.md) ships for sandboxes, containers and SSH hosts, which take the same arguments with environment-relative paths.
- **Is wrapped per run by** `AuthorityWorkspace`, whose `workspace=` plumbing is in [workspace selection](pydantic-ai-workspace-selection.md).
- **Rests on** the [capability primitive](pydantic-ai-capability-primitive.md): a capability part decides whether workspace text enters instructions at all, which is where the level is consulted.
- **Is the same scale as** [capability parts and authority](pydantic-ai-capability-parts-and-authority.md): that page records the six sources a capability part can carry, the lower-of rule against the kind's asked-for authority, and the capability `authority` ceiling — `WorkspaceSource.from_workspace` is one of those sources, and a workspace capability's authority is both its ceiling and its files' default level.
- **Is not a substitute for** [deferred tool approval](pydantic-ai-deferred-approvals.md) or a sandbox — authority classifies text, it does not bound actions.
- **Applies to** the operator-versus-clone distinction in [Claude Agent SDK versus Pydantic AI](claude-agent-sdk-vs-pydantic-ai.md), where the agent works on code the operator did not write.

[^pydantic-workspace-docs]: Pydantic, "Workspaces" (pydantic.dev docs, `/docs/ai/core-concepts/workspace/`), 6,000 words as declared, 6,040 by local `wc -w`, no version, author or date stated; local capture `raw/core-concepts/workspace/index.md`, content digest sha256:106c823e. §"Files you didn't write" (raw lines 227–281) for the three levels, the `WorkspaceSource.from_workspace` rendering voices, the `LocalWorkspace('./checkout', authority='none')` sample, the Harness backends taking the same arguments and not expanding `~`, `authority_of`, the longest-match/outside-the-working-directory/symlink/case-folding rules, `AuthorityWorkspace` and lowest-wins, the read-time check and the new-conversation advice, and the statement that authority is not access control and that tool output stays tool output. Evidence class: **Reported** — vendor reference documentation naming no version; nothing was constructed or run.
