---
title: "Skills"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/harness/skills/"
domain: "pydantic.dev"
language: "en"
description: "Load Agent Skills (SKILL.md files) from the run's workspace into a Pydantic AI agent on demand: the model sees each skill's name and description and loads its instructions when needed."
word_count: 4876
---

Use [Agent Skills](https://agentskills.io/specification) to give an agent specialized instructions without putting every instruction in its initial prompt.

Point `Skills` at one or more skill libraries. The model first sees each skill’s name and description, followed by its `when_to_use` text if it has one. When a skill is useful, the model loads it with the `load_capability` tool to receive that skill’s instructions.

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/skills/)

> While Pydantic AI Harness is on 0.x releases, the API may change between minor releases; when it does, deprecation warnings and release-note migration guidance tell you (or your agent) exactly how to upgrade. See the [version policy](https://pydantic.dev/docs/ai/harness/#version-policy).

```
flowchart TB
    accTitle: Skills: load SKILL.md instructions on demand
    accDescr: At run start, the Skills capability reads the workspace files under .agents/skills/, here code-review/SKILL.md and release-notes/SKILL.md. It puts each skill's name and description in the model's instructions. When a skill is needed, the model calls load_capability and gets a heading, the skill directory and the SKILL.md body.
    subgraph workspace["Workspace"]
        files[".agents/skills/<br/>code-review/SKILL.md<br/>release-notes/SKILL.md"]
    end
    skills["Skills()"]:::capability
    model(["model"])
    load["load_capability"]:::capability
    files -->|"read at run start"| skills
    skills -->|"instructions: each skill's<br/>name and description"| model
    model <-->|"when a skill is needed:<br/>heading, skill directory,<br/>SKILL.md body"| load
    classDef capability stroke:#E520E9,stroke-width:2px
```

## Installation

Install the `skills` extra for YAML frontmatter support:

- [pip](#tab-panel-0-0)
- [uv](#tab-panel-0-1)

Terminal

```bash
pip install "pydantic-ai-harness[skills]"
```

## Quick start

Create a skill library:

```
.agents/skills/
  code-review/
    SKILL.md
```

Add the skill’s description and instructions:

```markdown
---
name: code-review
description: Review a change for correctness and repository conventions.
---

Inspect the change and report findings by severity.
```

Then add the library to your agent, with a [workspace](https://pydantic.dev/docs/ai/core-concepts/workspace/) to read it from:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import Skills

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[LocalWorkspace('.'), Skills('.agents/skills')],
)
```

`Skills` does not search `.agents`, `.claude`, or your home directory automatically. Pass each library you want it to load; to layer several the way coding agents do, see [Layer project and personal skills](#layer-project-and-personal-skills).

## How it works

At the start of every run, `Skills`:

1. Reads each configured library from the run’s workspace. Relative paths resolve from its working directory.
2. Scans the immediate child directories and validates the selected `SKILL.md` files.
3. Offers each selected skill as a [deferred capability](https://pydantic.dev/docs/ai/capabilities/on-demand/) named after it: the model sees its name, description and `when_to_use`, and loads it with the `load_capability` tool.

Loading a skill returns a `# Skill: <name>` heading, a line naming the skill’s directory in the workspace, and the skill’s Markdown body. The catalog is the same on every run over the same files, so it stays in the cached prefix; a new or renamed skill appears in it on the next run. Without any skills, `Skills` adds no instructions and no `load_capability` tool.

A run without a workspace fails at its start, unless every library has its own `workspace=` backend, as in [Ship skills with your application](#ship-skills-with-your-application).

## Ship skills with your application

To load skills that ship inside your application, keep `Skills` and pass `workspace=` a `LocalWorkspaceBackend` rooted at your application’s files. `Skills` then reads its libraries from that directory instead of the run’s workspace, and discovers, validates, and selects `SKILL.md` packages the same way. The agent needs no workspace of its own:

```python
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai_harness import Skills

APP_DIR = Path(__file__).parent  # contains skills/code-review/SKILL.md

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[Skills('skills', workspace=LocalWorkspaceBackend(APP_DIR))],
)
```

Relative library paths resolve against the backend’s directory, so `'skills'` above is `APP_DIR / 'skills'`. `LocalWorkspaceBackend` takes a path on disk: build it from `Path(__file__)`, not from `importlib.resources.files()`, which returns a `Traversable` that is a real directory only when the package is installed unzipped.

The model sees each skill’s name and description in the catalog, and loading a skill returns its heading and `SKILL.md` body. The loaded instructions do not name the skill’s directory, since the model’s file and shell tools don’t work there. Pass `read_files=True` to let the model read a loaded skill’s `references/` and other text files from `APP_DIR`. To run its `scripts/`, put its library in the run’s workspace instead and give the agent `Shell` there; see [Bundled files](#bundled-files).

The same backend works when the agent’s own workspace is a sandbox: `Skills` reads the skills from your application’s files, and the agent’s tools act in the sandbox. `workspace=` takes a backend, not the `LocalWorkspace` capability. Under a durable engine such as Temporal, a `workspace=` backend is read in-process, not through the workflow.

For instructions that are not `SKILL.md` packages in a directory, such as runbooks kept in a database or files in a custom format, skip `Skills` and define each one as a deferred `Capability`: [Loading skills from Markdown files](https://pydantic.dev/docs/ai/capabilities/on-demand/#loading-skills-from-markdown-files) shows a file loader, and [Loading runbooks from a database](https://pydantic.dev/docs/ai/capabilities/on-demand/#loading-runbooks-from-a-database) reads the instructions at run time.

## Choose which skills to expose

By default, all discovered skills are included. Use `include` or `exclude` to change the catalog for a particular agent:

```python
from pydantic_ai_harness import Skills

review_skills = Skills(
    '.agents/skills',
    include=['code-review'],
)

release_skills = Skills(
    '.agents/skills',
    exclude=['code-review'],
)
```

| Configuration | Skills in the catalog |
| --- | --- |
| Neither option | All discovered skills |
| `include=['a', 'b']` | Only `a` and `b` |
| `include=[]` | No skills |
| `exclude=['a', 'b']` | All except `a` and `b` |
| `exclude=[]` | All discovered skills |

`include` and `exclude` cannot be used together. The constructor overloads catch this in typed code, and runtime validation covers agent specs and untyped callers. Unknown names fail at run start. Pass `unknown_names='skip'` to ignore them instead, for a selection shared by projects that do not all have every skill it names, such as a person’s list of skills to hide.

Selection happens before frontmatter is parsed. An unselected skill does not add instructions or frontmatter validation errors to that `Skills` instance.

These options control catalog exposure. They are not filesystem permissions or an access-control boundary.

Directory paths choose where discovery starts in the workspace; they do not create a containment boundary, and normal symlink resolution applies.

A selected `SKILL.md` body becomes model instructions. Load libraries only from sources you trust, and review repository-provided skills before exposing them.

## Skill format

Each immediate child directory containing `SKILL.md` is a skill:

```
.agents/skills/
  code-review/
    SKILL.md
  release-notes/
    SKILL.md
```

The loader uses these parts of `SKILL.md`:

| Part | Requirement |
| --- | --- |
| `name` | Optional. Defaults to the parent directory name. If provided, it must match the directory after Unicode normalization. |
| `description` | Required and non-blank. The Agent Skills limit is 1,024 characters; longer descriptions load with a warning. This appears in the initial catalog. |
| `when_to_use` | Optional. Appended to the description in the catalog, so write the whole trigger clause, such as “Use when …”. A blank value counts as unset. |
| Markdown body | Optional. This is loaded under a generated `# Skill: <name>` heading. |
| `disable-model-invocation` | Optional, `true` or `false`. `true` leaves the skill out of the model’s catalog; see [Invoke a skill yourself](#invoke-a-skill-yourself). |
| `user-invocable` | Optional, `true` or `false`. `false` tells a host not to offer the skill as a command; the model still sees it. |

Skill names and `include` or `exclude` values are normalized with Unicode NFKC before matching. A normalized name can contain at most 64 lowercase Unicode letters or numbers, separated by single hyphens. It cannot start or end with a hyphen.

`disable-model-invocation` and `user-invocable` come from [Claude Code](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill). Any value other than `true` or `false` (in any letter case) skips the skill with a warning, rather than guessing whether it may be invoked.

Only immediate children are discovered. For example, `code-review/references/SKILL.md` does not create another skill. Ordinary files and child directories without `SKILL.md` are ignored.

You can pass several libraries:

```python
from pydantic_ai_harness import Skills

skills = Skills([
    '.agents/skills',
    'company/skills',
])
```

By default, selected skill names must be unique across those libraries. Repeated references to the same resolved library are scanned once, and a skill found twice, through a symlinked library or skill directory or as a byte-identical copy of its `SKILL.md`, counts once.

## Layer project and personal skills

Coding agents read skills from conventional locations that a project may not have, and let a project’s skill take precedence over a personal one with the same name. Two options give `Skills` the same behavior:

```python
from pydantic_ai_harness import Skills

skills = Skills(
    ['.agents/skills', '.claude/skills', '/home/me/.agents/skills', '/home/me/.claude/skills'],
    missing_directories='skip',
    duplicate_names='keep_first',
)
```
- `missing_directories='skip'` leaves out a library directory that does not exist, instead of failing the run. A path that is a file, or that holds a `SKILL.md` itself (a skill package rather than a library of them), is left out with a `UserWarning`, so one a model creates mid-session doesn’t fail every later run.
- `duplicate_names='keep_first'` keeps the skill from the earlier directory when two valid skills with different `SKILL.md` files share a name, and skips the other with a `UserWarning`. An invalid `SKILL.md` is skipped first, so it does not hide a valid skill with its name.

Directories are listed in precedence order. Paths are workspace paths, and `~` is not expanded, because the workspace may be a sandbox with a home directory of its own; spell out the absolute path for a library on this machine.

If `.agents/skills` is a symlink to `.claude/skills`, or holds byte-identical copies of its `SKILL.md` files, as in many repositories, each skill is listed once. Only `SKILL.md` is compared: the first directory’s bundled files are the ones the model is pointed at.

## Bundled files

Agent Skill packages can contain directories such as `references/`, `assets/`, and `scripts/`. `Skills` does not run those files, and reads them only with `read_files=True`.

The loaded instructions name the skill’s directory in the run’s workspace, so a model with file or shell tools, such as those from `FileSystem` or `Shell`, can follow a relative reference like `references/guide.md` or run `scripts/check.py`. `${CLAUDE_SKILL_DIR}` and `${SKILL_DIR}` in the body become that directory. Skills read from a `workspace=` backend are not where those tools work, so their instructions leave the directory out and keep the placeholders as written.

To let the model read a loaded skill’s files without giving it general file access, pass `read_files=True`:

```python
from pydantic_ai_harness import Skills

skills = Skills('.agents/skills', read_files=True)
```

The model gets a `read_skill_file` tool that takes a skill name and a path relative to its directory, such as `references/guide.md`. It reads from the workspace the skill came from, including a `workspace=` backend, so it also works for [skills shipped with your application](#ship-skills-with-your-application). A read returns at most 50,000 characters, and says which `offset` to pass to read on. A file over 10 MiB is refused.

The tool refuses a skill the model has not loaded with `load_capability`, an absolute path, a path that leads outside the skill’s directory through `..` or a symlink, and a file that is not UTF-8 text. It does not read a skill with `disable-model-invocation: true`, even after a host sends its `render()` as a prompt. A host-rendered skill the model can load becomes readable once the model loads it. The tool reads nothing from a workspace whose backend implements neither `SupportsRealpath` nor `SupportsCommands`, since it cannot resolve symlinks. When two `Skills` combine, only the libraries of one with `read_files=True` are readable. With a `scanner`, the text a read returns is scanned first, along with 1,000 characters on each side, and withheld if flagged, with a zero-duration `artifact_scan flagged` span whose action is `withheld`.

`Skills` reads the libraries itself: the model does not need `FileSystem` or `Shell` to load a skill, and adding either does not change which files `Skills` reads.

[`pydantic-ai-skills`](https://github.com/DougTrajano/pydantic-ai-skills), a community package by [Doug Trajano](https://github.com/DougTrajano) that builds on `Skills`, was the first to offer skill-scoped file tools. It also runs a skill’s scripts through sandboxed executors and loads skill libraries from Git and S3. For a library kept elsewhere, you can also sync it to a directory in the workspace and point `Skills` at that directory.

## Compatibility with existing skill libraries

The portable `name`, `description`, and Markdown instructions are supported. `name` may be omitted and derived from the directory.

The following behavioral fields are accepted for compatibility, but their behavior is not implemented:

```
agent, allowed-tools, argument-hint, arguments, context, dependencies,
disallowed-tools, effort, hooks, model, paths, shell, tools
```

If a selected skill uses any of these fields, the run emits one aggregated `UserWarning` at its start. Fields such as `license`, `compatibility`, and `metadata` are accepted without changing runtime behavior. Other unknown, non-behavioral fields are also accepted.

`when_to_use` is not one of them: its text is appended to the skill’s description in the model’s catalog, so the model sees when to load the skill. Multiline values keep their line breaks, with continuation lines indented inside the catalog entry. Write the whole trigger clause, since it’s appended as written:

```markdown
---
name: review
description: Review a pull request.
when_to_use: Use when the user asks for a review or a second opinion on a diff.
---
```

To keep a skill’s tools hidden until the skill is loaded, define that skill as an [on-demand capability with its tools](https://pydantic.dev/docs/ai/capabilities/on-demand/#hide-tools-until-loaded) instead: `Skills` delivers instructions only. Such a capability sits alongside `Skills` on the same agent: both appear in one catalog, and the model loads either with the `load_capability` tool. A capability `id` that matches a skill name `Skills` exposes to the model fails the run, so leave that skill out of the library or out of `include`, or pass its name in `exclude`.

## Invoke a skill yourself

The model decides when to load a skill. A host that also lets a person invoke a skill, such as a `/code-review src/app.py` command in a terminal client, reads the same catalog with `load` and renders the skill as a prompt:

```python
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai_harness import Skills

skills = Skills('.agents/skills', missing_directories='skip')
catalog = await skills.load(LocalWorkspaceBackend('.'))
review = next(skill for skill in catalog.skills if skill.name == 'code-review')
result = await agent.run(review.render('src/app.py'))
```

`load` reads the libraries as a run would, without emitting warnings. Each entry in the catalog’s `skipped` is a `SkippedSkill` with the `path` left out, a `reason`, and the `message` a run would warn with, for the host to show:

| `reason` | Left out |
| --- | --- |
| `'invalid'` | A `SKILL.md` with malformed frontmatter, invalid UTF-8, or an invalid or mismatched name |
| `'duplicate_name'` | A `SKILL.md` named like a skill found earlier, with `duplicate_names='keep_first'` |
| `'not_a_directory'` | A library path that is a file, with `missing_directories='skip'` |
| `'skill_package'` | A library path that holds a `SKILL.md` itself, with `missing_directories='skip'` |
| `'flagged'` | A skill whose description, `when_to_use` or body the `scanner` flagged; see [Scan skills before loading them](#scan-skills-before-loading-them) |

Each `SkillDefinition` has the skill’s `name`, `description`, `when_to_use`, `body`, `path`, `directory`, `in_run_workspace`, `model_invocable`, and `user_invocable`. The catalog includes skills with `disable-model-invocation: true` (`model_invocable` is `False`), which a run leaves out of the model’s catalog, so a host can offer them as commands only. `Skills` doesn’t offer commands itself, so `user_invocable` is for the host to check before it offers one.

`render(arguments)` returns what loading the skill returns, with every `$ARGUMENTS` in the body replaced by `arguments`. A body without `$ARGUMENTS` gets `ARGUMENTS: <arguments>` appended. Other placeholders, such as Claude Code’s indexed `$0` or `$ARGUMENTS[0]`, are left unchanged, and do not count as `$ARGUMENTS`. `render()` without arguments returns the instructions the model gets when it loads the skill, including leaving the directory out for a skill read from `workspace=` (`in_run_workspace` is `False`).

## Use an agent spec

`Skills` works with Pydantic AI’s [YAML and JSON agent specs](https://pydantic.dev/docs/ai/core-concepts/agent-spec/):

```yaml
model: anthropic:claude-opus-5-5
capabilities:
  - Skills:
      directories: .agents/skills
      include:
        - code-review
        - release-notes
```

Register `Skills` when loading the spec:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Skills

agent = Agent.from_file('agent.yaml', custom_capability_types=[Skills])
```

The `skills` extra installs PyYAML. It parses `SKILL.md` frontmatter and YAML agent specs.

## Scan skills before loading them

Skills an agent wrote, or that came from a third party, can carry instructions that take effect in a later session. Pass an [`ArtifactScanner`](https://pydantic.dev/docs/ai/harness/artifact-scanning/) to check each skill’s description, `when_to_use` and body for prompt injection, credential exfiltration, HTML comments, and invisible characters before it is offered:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import ArtifactScanner, Skills

agent = Agent(
    capabilities=[
        LocalWorkspace('.'),
        Skills('.agents/skills', scanner=ArtifactScanner()),
    ],
)
```

A flagged skill is left out of the catalog with a `UserWarning`, and a zero-duration `artifact_scan flagged` span. `Skills.load()` reports it as a `SkippedSkill` with `reason='flagged'` and the findings in `scan`. Bundled files are scanned only when the model reads them with `read_files=True`. The scanner belongs to the `Skills` it is passed to, so when two combine, a vetted library can go unscanned while an agent-written one is scanned.

## Configuration

```python
Skills(
    directories: str | Path | Sequence[str | Path],
    *,
    include: Collection[str] | None = None,
    exclude: Collection[str] | None = None,
    missing_directories: Literal['error', 'skip'] = 'error',
    duplicate_names: Literal['error', 'keep_first'] = 'error',
    unknown_names: Literal['error', 'skip'] = 'error',
    workspace: WorkspaceBackend | None = None,
    scanner: ArtifactScanner | None = None,
    read_files: bool = False,
)
```

Pass at least one library directory, not the path of an individual skill package. Malformed frontmatter, invalid UTF-8, and invalid or mismatched names warn and skip that skill. Unknown selections fail at run start, and so do duplicate selected names, missing libraries, and library paths that are files or skill packages, unless `duplicate_names`, `missing_directories`, or `unknown_names` say otherwise.

Two `Skills` on one agent combine into one catalog.

- [Agent Skills specification](https://agentskills.io/specification)
- [Adding skills support to an agent](https://agentskills.io/client-implementation/adding-skills-support)
- [Pydantic AI workspaces](https://pydantic.dev/docs/ai/core-concepts/workspace/)
- [Pydantic AI capabilities overview](https://pydantic.dev/docs/ai/capabilities/overview/)
- For instructions or tools defined in Python rather than a `SKILL.md` package, use core [`Capability`](https://pydantic.dev/docs/ai/capabilities/overview/) with `defer_loading=True`.

## API reference

### Skills

**Bases:** `AbstractCapability[AgentDepsT]`

Offer Agent Skill instructions from the run’s workspace as deferred capabilities.

Skill libraries are directories in the run’s workspace (`ctx.workspace`), read at the start of every run; relative paths resolve against its working directory. Attach `LocalWorkspace` to read directories on this machine, or pass `workspace=` to read them from a workspace of their own. A run with neither fails at its start.

Each selected immediate child containing `SKILL.md` becomes a deferred capability named after the skill: the model sees its name, description and `when_to_use`, and loads its Markdown body, with the skill’s directory in the run’s workspace, with `load_capability`. Bundled files are not executed, and are read only with `read_files=True`. Descriptions longer than the Agent Skills limit are preserved and emit a warning. A skill found twice, through a symlink or as a byte-identical `SKILL.md`, counts once. A skill whose frontmatter has `disable-model-invocation: true` is left out of the model’s catalog.

`load` reads the same skills outside a run, for a host that lets a person invoke a skill itself; render one with `SkillDefinition.render`.

With `read_files=True`, the model also gets a `read_skill_file` tool that reads the text files in a loaded skill’s directory, such as `references/guide.md`, and nothing outside it.

Two `Skills` on one agent combine, so every library either names stays reachable.

#### Attributes

##### id

One per agent: two `Skills` combine into one catalog.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `'skills'`

##### directories

Skill-library paths in the workspace, read at the start of each run.

**Type:** [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | `Path`, …\] **Default:** `self._normalize_directories(directories)`

##### include

Exact skill names to expose, or `None` to expose all discovered skills.

**Type:** [`frozenset`](https://docs.python.org/3/builtins/stdtypes.html#frozenset) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `self._normalize_selection('include', include) if include is not None else None`

##### exclude

Exact skill names to omit from the catalog.

**Type:** [`frozenset`](https://docs.python.org/3/builtins/stdtypes.html#frozenset) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] **Default:** `self._normalize_selection('exclude', exclude) if exclude is not None else frozenset()`

##### missing\_directories

`'error'` fails the run on a library path that is not a library; `'skip'` leaves it out, with a warning unless it does not exist.

**Type:** `MissingDirectories` **Default:** `missing_directories`

##### duplicate\_names

`'error'` fails the run when two different `SKILL.md` files share a name; `'keep_first'` keeps the first.

**Type:** `DuplicateNames` **Default:** `duplicate_names`

##### unknown\_names

`'error'` fails the run on an `include` or `exclude` name no library has; `'skip'` ignores that name.

**Type:** `UnknownNames` **Default:** `unknown_names`

##### workspace

Where the libraries live, when not in the run’s workspace; see `__init__`.

**Type:** `WorkspaceBackend` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `workspace`

##### scanner

Scans each skill’s description, `when_to_use` and body before it is offered, skipping flagged skills; see `__init__`.

**Type:** `ArtifactScanner` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `scanner`

##### read\_files

Whether the model gets a `read_skill_file` tool for a loaded skill’s files; see `__init__`.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `read_files`

#### Methods

##### \_\_init\_\_

```python
def __init__(
    directories: str | Path | Sequence[str | Path],
    *,
    include: Collection[str],
    exclude: None = None,
    missing_directories: MissingDirectories = 'error',
    duplicate_names: DuplicateNames = 'error',
    unknown_names: UnknownNames = 'error',
    workspace: WorkspaceBackend | None = None,
    scanner: ArtifactScanner | None = None,
    read_files: bool = False,
) -> None
def __init__(
    directories: str | Path | Sequence[str | Path],
    *,
    include: None = None,
    exclude: Collection[str] | None = None,
    missing_directories: MissingDirectories = 'error',
    duplicate_names: DuplicateNames = 'error',
    unknown_names: UnknownNames = 'error',
    workspace: WorkspaceBackend | None = None,
    scanner: ArtifactScanner | None = None,
    read_files: bool = False,
) -> None
```

Configure the skill libraries to read at the start of each run.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

###### Parameters

**`directories`**: [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | `Path` | [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | `Path`\]

One skill-library path or a sequence of paths in the workspace, in precedence order. `~` is not expanded: the workspace may be a sandbox with a home of its own.

**`include`**: [`Collection`](https://docs.python.org/3/library/typing.html#typing.Collection) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

Exact names to expose. Omit to expose all discovered skills.

**`exclude`**: [`Collection`](https://docs.python.org/3/library/typing.html#typing.Collection) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

Exact names to omit. Cannot be combined with `include`.

**`missing_directories`**: `MissingDirectories` *Default:* `'error'`

`'error'` (the default) fails the run when a library path does not exist, is not a directory, or is itself a skill package. `'skip'` leaves such a path out, for conventional locations such as `.agents/skills` that a project may not have: one that does not exist quietly, any other with a warning.

**`duplicate_names`**: `DuplicateNames` *Default:* `'error'`

`'error'` (the default) fails the run when two different `SKILL.md` files share a name. `'keep_first'` keeps the one from the earlier directory and skips the other with a warning, the way coding agents layer project skills over personal ones.

**`unknown_names`**: `UnknownNames` *Default:* `'error'`

`'error'` (the default) fails the run when an `include` or `exclude` name matches no skill. `'skip'` ignores that name, for a selection shared by projects that do not all have every skill it names.

**`workspace`**: `WorkspaceBackend` | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

A workspace backend to read the libraries from instead of the run’s, such as `LocalWorkspaceBackend('/app')` for skills shipped with the code while the agent works in a sandbox. It is read in-process: a durable engine does not route it through its workflow machinery.

**`scanner`**: `ArtifactScanner` | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

An `ArtifactScanner` that checks each skill’s description, `when_to_use` and body for prompt injection, credential exfiltration, and hidden content. A flagged skill is left out of the catalog, with a warning, as a `SkippedSkill` whose `reason` is `'flagged'`. Omit to load skills unscanned. With `read_files`, it also scans the text each file read returns, and withholds it if flagged.

**`read_files`**: [`bool`](https://docs.python.org/3/builtins/functions.html#bool) *Default:* `False`

Give the model a `read_skill_file` tool that reads a UTF-8 text file in the directory of a skill it has loaded, from the workspace the skill was read from. It works without file tools and for a `workspace=` library, and does not reach files outside the skill’s directory, through `..` or a symlink. A workspace whose backend implements neither `SupportsRealpath` nor `SupportsCommands` cannot resolve symlinks, so the tool reads nothing from it.

##### from\_spec

`@classmethod`

```python
def from_spec(
    cls,
    directories: str | Sequence[str],
    *,
    include: Sequence[str] | None = None,
    exclude: Sequence[str] | None = None,
    missing_directories: MissingDirectories = 'error',
    duplicate_names: DuplicateNames = 'error',
    unknown_names: UnknownNames = 'error',
    read_files: bool = False,
    **kwargs: Any,
) -> Skills[Any]
```

Build from an agent spec, naming the fields a spec can express.

Core reads this signature to generate the spec’s JSON schema. Inherited, it would read `__init__`, whose `Collection[str]` selectors and `workspace` backend have no JSON schema and would drop the long form, leaving only `Skills: <directories>`. `**kwargs` reaches `__init__` unchanged, so a spec that set anything else still loads.

###### Returns

`Skills`\[[`Any`](https://docs.python.org/3/library/typing.html#typing.Any)\]

##### \_\_repr\_\_

```python
def __repr__() -> str
```

Show only the `Skills` configuration that callers control.

###### Returns

[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### combine

`@classmethod`

```python
def combine(
    cls,
    capabilities: Sequence[AbstractCapability[AgentDepsT]],
) -> AbstractCapability[AgentDepsT]
```

Serve every combined configuration’s libraries through one catalog.

The field-by-field default would keep only the last configuration’s directories, dropping the other libraries. A skill name selected by two configurations must name the same `SKILL.md`, or a byte-identical copy, unless the later configuration has `duplicate_names='keep_first'`.

###### Returns

`AbstractCapability`\[`AgentDepsT`\]

##### get\_toolset

```python
def get_toolset() -> AgentToolset[AgentDepsT] | None
```

The `read_skill_file` tool when `read_files` is set, so a durable engine registers it with the agent.

###### Returns

[`AgentToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AgentToolset) \[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### for\_run

`@async`

```python
def for_run(ctx: RunContext[AgentDepsT]) -> AbstractCapability[AgentDepsT]
```

Read the selected skills, from each configuration’s `workspace=` or else the run’s workspace.

Returns one deferred capability per skill the model may load, with the `read_skill_file` tool when one of them has `read_files` set; without any skills, it adds no instructions or tools. Emits a `UserWarning` for each skipped `SKILL.md` or library path, an overlong description, or unsupported frontmatter. Raises `UserError` when a configuration without `workspace=` meets a run without a workspace.

###### Returns

`AbstractCapability`\[`AgentDepsT`\]

##### load

`@async`

```python
def load(workspace: WorkspaceBackend | None = None) -> SkillCatalog
```

Read the selected skills now, as a run does at its start, without emitting warnings.

For a host that offers skills to a person as well as to the model, such as a `/code-review` command that sends `skill.render(arguments)` as a prompt. The catalog includes skills the model may not load (`model_invocable`), and its `skipped` entries say which `SKILL.md` files and library paths were left out, for the host to show.

###### Returns

`SkillCatalog`

###### Parameters

**`workspace`**: `WorkspaceBackend` | [`None`](https://docs.python.org/3/builtins/constants.html#None) *Default:* `None`

Where libraries without their own `workspace=` live, as the run’s workspace would be, such as `LocalWorkspaceBackend('.')`.

###### Raises

- `UserError` — A configuration without `workspace=` needs `workspace`, and none was passed.
- `ValueError` — A configuration problem that would also fail a run, such as, with `unknown_names='error'`, an unknown `include` name or, with `duplicate_names='error'`, two skills with one name.

### SkillDefinition

Validated skill metadata and body from a single `SKILL.md`.

#### Attributes

##### name

The skill’s name: its `name` frontmatter field, or else its directory’s name.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### description

The `description` frontmatter field, listed in the model’s catalog.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### when\_to\_use

The `when_to_use` frontmatter field, appended to the catalog description.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### body

The Markdown after the frontmatter, without leading and trailing blank lines.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### ignored\_behavioral\_fields

Frontmatter fields such as `allowed-tools` whose behavior `Skills` does not implement.

**Type:** [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), …\]

##### model\_invocable

Whether the model may load it; `False` when its frontmatter has `disable-model-invocation: true`.

A run leaves such a skill out of the model’s catalog. `Skills.load` still returns it, for a host that lets a person invoke it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### user\_invocable

Whether a host should let a person invoke it; `False` when its frontmatter has `user-invocable: false`.

`Skills` itself only offers skills to the model, so this is for a host, such as one with a `/skill-name` command.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### path

Absolute workspace path of the `SKILL.md` it was read from.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### in\_run\_workspace

Whether it was read from the run’s workspace, where the model’s file and shell tools can reach its directory.

`False` for a library read from `Skills(workspace=...)`; `render` then leaves the directory out.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### directory

Absolute workspace path of the skill’s directory, which holds any `scripts/` or `references/`.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

#### Methods

##### render

```python
def render(arguments: str | None = None) -> str
```

The skill’s instructions as the model receives them: a heading, the skill’s directory, and the body.

Pass `arguments` when a user invokes the skill with a command such as `/code-review src/app.py`: every `$ARGUMENTS` in the body becomes `arguments`, and a body without `$ARGUMENTS` gets `ARGUMENTS: <arguments>` appended. Other placeholders, such as Claude Code’s indexed `$0` and `$ARGUMENTS[0]`, are left unchanged. Without `arguments`, the result is the instructions the model gets when it loads the skill.

When `in_run_workspace`, `${CLAUDE_SKILL_DIR}` and `${SKILL_DIR}` in the body become the skill’s directory. Otherwise they are left unchanged, and the directory line is left out.

###### Returns

[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### SkillCatalog

The skills `Skills.load` read, and each `SKILL.md` or library it left out.

Run-time advice, such as frontmatter fields whose behavior is not implemented, is not included: a run emits it as a `UserWarning`, and each skill’s `ignored_behavioral_fields` lists its own.

#### Attributes

##### skills

The selected, valid skills, in catalog order, including those the model may not load.

**Type:** [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple) \[`SkillDefinition`, …\]

##### skipped

Each `SKILL.md` or library path left out, in the order it was found.

A run emits each `message` as a `UserWarning`; a host showing skills to a person can show them instead.

**Type:** [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple) \[`SkippedSkill`, …\]

### SkippedSkill

A `SKILL.md` or skill library path that `Skills` left out, and why.

#### Attributes

##### path

Absolute workspace path of the skipped `SKILL.md`, or of the skipped library.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### reason

Why it was left out.

**Type:** `SkipReason`

##### message

A sentence naming the path and the problem, as a run’s `UserWarning` says it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### scan

The artifact scan’s findings when `reason` is `'flagged'`, otherwise `None`.

**Type:** `ArtifactScanResult` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`
