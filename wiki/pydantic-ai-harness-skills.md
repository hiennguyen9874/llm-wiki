---
type: Concept
title: Pydantic AI Harness skills
description: The Harness Skills capability — Agent Skill packages discovered from one or more libraries and offered as deferred capabilities with a cache-stable catalog, the SKILL.md fields it honours and ignores, selection and layering rules, the read_skill_file boundary, and the two ways a skill's body becomes trusted instructions.
tags: [pydantic-ai, agents, harness, skills]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:33:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-skills-docs
    resource: ../raw/harness/skills/index.md
    scope: ../raw/harness/skills/
    kind: documentation
    revision: sha256:c84cf1497589218fa4590b09ee987fbc4b5bc74ec0f52618ae9ddd425958ebf0
    title: "Skills"
---

`Skills` is the [Harness](pydantic-ai-harness.md) capability that loads [Agent Skills](https://agentskills.io/specification) — `SKILL.md` packages — from one or more libraries and offers each one as a **deferred capability**: the model sees only a name, description and optional `when_to_use`, and calls `load_capability` to receive the body[^pydantic-skills-docs] It occupies the same on-demand slot as [PydanticAIDocs](pydantic-ai-harness-docs.md), but delivers *procedures* rather than reference pages — the difference between "how this repository does releases" and "what this API's signature is". The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## Discovery: explicit libraries, immediate children

`Skills` does **not** search `.agents`, `.claude` or your home directory on its own; you pass each library, and it scans only the **immediate child directories**, validating each selected `SKILL.md`[^pydantic-skills-docs] So `.agents/skills/code-review/SKILL.md` is a skill, while `code-review/references/SKILL.md` is not a second one, and ordinary files or directories without `SKILL.md` are ignored. A run without a workspace fails at its start unless every library has its own `workspace=` backend.

Discovery runs at the **start of every run**, and the resulting catalog is the same on every run over the same files, so it stays inside the cached prefix; a new or renamed skill appears in the catalog on the next run[^pydantic-skills-docs] With no skills, `Skills` adds neither instructions nor the `load_capability` tool. Two `Skills` on one agent combine into one catalog, and a capability `id` matching a skill name that `Skills` exposes **fails the run**, so a tool-bearing on-demand capability with the same name must be excluded from the library or from `include`.

Loading a skill returns a `# Skill: <name>` heading, a line naming the skill's directory **in the run's workspace**, and the Markdown body — which is what makes bundled `references/…` and `scripts/…` usable by a model that has `FileSystem` or `Shell`[^pydantic-skills-docs]

## What the loader reads

| Part | Requirement |
| --- | --- |
| `name` | Optional; defaults to the parent directory name. If provided it must match the directory after Unicode normalization |
| `description` | Required and non-blank. The Agent Skills limit is **1,024** characters; longer ones load with a warning. This is what appears in the catalog |
| `when_to_use` | Optional, appended to the description in the catalog — write the whole trigger clause ("Use when …"), since it is appended as written; a blank value counts as unset |
| Markdown body | Optional; loaded under the generated heading |
| `disable-model-invocation` | `true`/`false`; `true` keeps the skill out of the model's catalog entirely |
| `user-invocable` | `true`/`false`; `false` tells a host not to offer the skill as a command, while the model still sees it |

Names are normalized with Unicode **NFKC** before matching and may contain at most 64 lowercase letters or numbers separated by single hyphens, with no leading or trailing hyphen[^pydantic-skills-docs] `disable-model-invocation` and `user-invocable` come from Claude Code, and any value other than `true`/`false` in any letter case **skips** the skill with a warning rather than guessing whether it may be invoked.

A list of behavioural fields is accepted for compatibility but **not implemented** — `agent`, `allowed-tools`, `argument-hint`, `arguments`, `context`, `dependencies`, `disallowed-tools`, `effort`, `hooks`, `model`, `paths`, `shell`, `tools` — and a selected skill using any of them emits one aggregated `UserWarning` at run start[^pydantic-skills-docs] Non-behavioural fields such as `license`, `compatibility` and `metadata` pass without effect. The practical reading: a skill copied from another ecosystem may *look* like it restricts its own tools, and it does not. To hide a skill's tools until it loads, the source's answer is a core on-demand capability with its tools beside `Skills`, not a frontmatter field.

## Selection is catalog exposure, not access control

`include` and `exclude` reshape the catalog for one agent, cannot be combined, and are validated both by constructor overloads for typed code and at runtime for specs and untyped callers[^pydantic-skills-docs]

| Configuration | Catalog |
| --- | --- |
| Neither | All discovered skills |
| `include=['a','b']` | Only `a` and `b` |
| `include=[]` | No skills |
| `exclude=['a','b']` | All except those |
| `exclude=[]` | All discovered skills |

Selection happens **before** frontmatter is parsed, so an unselected skill contributes no instructions and no validation error; unknown names fail at run start unless `unknown_names='skip'`, which is the option for a shared list naming skills some projects lack[^pydantic-skills-docs] The source states the limit plainly: these options control catalog exposure and are **not** a filesystem permission or access-control boundary, and directory paths choose a discovery root rather than creating containment — normal symlink resolution applies.

Two options make conventional layering work the way coding agents do it[^pydantic-skills-docs]:

- `missing_directories='skip'` leaves out a library that does not exist instead of failing the run; a path that is a file, or that holds a `SKILL.md` itself (a skill *package* rather than a library of them), is left out with a `UserWarning` — deliberately, so a package the model creates mid-session does not fail every later run.
- `duplicate_names='keep_first'` keeps the earlier directory's skill and skips the later with a warning, so `['.agents/skills', '~/.agents/skills']` gives project precedence over personal. An invalid `SKILL.md` is skipped **first**, so it cannot hide a valid skill of the same name.

Directories are listed in **precedence order**, paths are workspace paths, and `~` is **not** expanded — because the workspace may be a sandbox with its own home — so a library on the real machine needs its absolute path spelled out[^pydantic-skills-docs] Deduplication is by `SKILL.md`: a symlinked library or byte-identical copies count once, and the first directory's bundled files are the ones the model is pointed at.

## Shipping skills with the application

`Skills('skills', workspace=LocalWorkspaceBackend(APP_DIR))` reads libraries from your application's files instead of the run's workspace, so the agent needs no workspace of its own and the same backend works when the agent's own workspace is a sandbox[^pydantic-skills-docs] Three constraints:

- Relative library paths resolve against the **backend's** directory, and the backend must be built from a real path — `Path(__file__)`, not `importlib.resources.files()`, which is only a real directory when the package is installed unzipped.
- The loaded instructions then **omit** the skill's directory, since the model's file and shell tools do not work there; `${CLAUDE_SKILL_DIR}` and `${SKILL_DIR}` stay as written.
- Under a durable engine such as Temporal a `workspace=` backend is read **in-process**, not through the workflow.

`read_files=True` is the bridge for such skills[^pydantic-skills-docs]: it adds a `read_skill_file` tool taking a skill name and a path relative to its directory, reading from the workspace the skill came from — at most 50,000 characters per read, with the `offset` to continue, refusing a file over 10 MiB. The tool refuses a skill the model has **not** loaded with `load_capability`, an absolute path, a path escaping the skill's directory through `..` or a symlink, a non-UTF-8 file, and a skill with `disable-model-invocation: true` even after a host sends its `render()` as a prompt; a host-rendered skill becomes readable once the model loads it. It reads nothing from a backend implementing neither `SupportsRealpath` nor `SupportsCommands`, because it cannot resolve symlinks. When two `Skills` combine, only the libraries of one with `read_files=True` are readable.

For instructions that are not `SKILL.md` packages — runbooks in a database, files in a custom format — the source says to skip `Skills` and define each as a deferred `Capability` with a loader.

## Host invocation, outside a run

`load(backend)` reads the libraries as a run would, without warnings, and returns a catalog whose entries carry `name`, `description`, `when_to_use`, `body`, `path`, `directory`, `in_run_workspace`, `model_invocable` and `user_invocable`[^pydantic-skills-docs] That is how a terminal client offers `/code-review src/app.py`: `render('src/app.py')` returns what loading returns, with every `$ARGUMENTS` in the body replaced — and `ARGUMENTS: <arguments>` appended when the body has no `$ARGUMENTS` — while other placeholders such as Claude Code's `$0`/`$ARGUMENTS[0]` are left unchanged.

Each skipped entry is a `SkippedSkill` with a `path`, a `reason` and the warning message, and the reasons are exhaustive: `'invalid'` (malformed frontmatter, invalid UTF-8, invalid or mismatched name), `'duplicate_name'`, `'not_a_directory'`, `'skill_package'` and `'flagged'`[^pydantic-skills-docs] The catalog includes `disable-model-invocation: true` skills with `model_invocable=False` so a host can offer them as commands only; `Skills` offers no commands itself.

## The trust boundary

A selected `SKILL.md` body **becomes model instructions**, and the source says so directly: load libraries only from sources you trust, and review repository-provided skills before exposing them[^pydantic-skills-docs] `scanner=ArtifactScanner()` is the mechanical check: a flagged skill is left out of the catalog with a `UserWarning` and a zero-duration `artifact_scan flagged` span, and `load()` reports it as `reason='flagged'` with findings in `scan`. Bundled files are scanned **only** when the model reads them with `read_files=True`, and the read text is scanned along with 1,000 characters on each side and withheld when flagged (span action `withheld`). The scanner belongs to the instance it is passed to, so in a combined agent one vetted library can go unscanned while an agent-written one is scanned.

The second trust path is less obvious: a skill the **agent itself** writes mid-session is discovered on the next run, which is why `missing_directories='skip'` exists and why scanning is recommended for exactly that case. The community package `pydantic-ai-skills` (Doug Trajano) extends this capability with skill-scoped file tools, sandboxed script execution and Git/S3 libraries — outside this capture's verification.

## Configuration and specs

```python
Skills(
    directories: str | Path | Sequence[str | Path],
    *,
    include=None,                 # exact names to expose
    exclude=None,                 # exact names to omit
    missing_directories='error',  # or 'skip'
    duplicate_names='error',      # or 'keep_first'
    unknown_names='error',        # or 'skip'
    workspace: WorkspaceBackend | None = None,
    scanner: ArtifactScanner | None = None,
    read_files=False,
)
```

Pass at least one **library** directory, not an individual skill package. Malformed frontmatter, invalid UTF-8 and invalid or mismatched names warn and skip that skill; unknown selections, duplicate selected names, missing libraries and library paths that are files or packages fail at run start unless the matching option says otherwise[^pydantic-skills-docs] The default `id` is `'skills'`, one per agent, because two instances combine.

Specs declare `directories` plus `include`/`exclude` and register `Skills` with `custom_capability_types`, and the `skills` extra installs PyYAML for both `SKILL.md` frontmatter and YAML specs[^pydantic-skills-docs]

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram was read in its text form[^pydantic-skills-docs] External links — the Agent Skills specification and client-implementation guide, the on-demand capability pages, Claude Code's skills documentation, the community `pydantic-ai-skills` package, the workspace and artifact-scanning pages — were read as links and not followed. The page names no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-opus-5-5`, an alias no release pin corroborates.

Nothing was installed, no library scanned, no skill loaded, rendered or read and no scanner decision observed, so every claim is **Reported** and none **Observed** or **Reproduced**. Unstated and consequential: how a large catalog of descriptions costs against `max_tokens`-style budgets (a skill contributes only name, description and `when_to_use`, but nothing bounds the total), what the aggregated compatibility warning does to a run's tone in production logs, whether `when_to_use` is length-limited, and how `render()` handles binary or image references.

## Relationships

- **Same on-demand shape as** [PydanticAIDocs](pydantic-ai-harness-docs.md) and [on-demand capabilities](pydantic-ai-on-demand-capabilities.md), with procedures rather than reference pages.
- **Complements** [Harness memory](pydantic-ai-harness-memory.md): memory stores what the agent learned, skills store what the team decided, and the source recommends a scanner for both.
- **Composed into** [Coder](pydantic-ai-harness-coder.md) beside it, where its directory line makes bundled `references/` and `scripts/` reachable through `FileSystem` and `Shell`.
- **Constrained by** [workspace file authority](pydantic-ai-workspace-authority.md): a skill body is instructions, so its provenance decides whether it should be loaded at all — the same reasoning [prompt injection defender](pydantic-ai-harness-prompt-injection-defender.md) applies to tool results.
- **Related to** [Pydantic AI coding-agent skills](pydantic-ai-coding-agent-skills.md), which is about the skills Pydantic ships for *your* agent, not a capability for loading yours.

[^pydantic-skills-docs]: Pydantic Docs, "Skills", <https://pydantic.dev/docs/ai/harness/skills/>; local capture `raw/harness/skills/index.md`, content digest sha256:c84cf149, 4,876 words as declared (4,982 by `wc -w`), 775 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11–15 for the one-paragraph contract and the `load_capability` route; 17–39 for the flow diagram (library read at run start → catalog instructions → `load_capability` returns heading, directory and body); 41–49 for the `skills` extra; 51–84 for the quick start, the explicit-library rule and the no-workspace failure; 86–108 for the four run-start steps, catalog stability, the empty-library case, the workspace requirement and the `workspace=` shipping route; 110–130 for `workspace=` with `LocalWorkspaceBackend`, the `Path(__file__)` note and the durable in-process caveat; 132–146 for `include`/`exclude`, the "not an access-control boundary" statement and the trust warning; 148–172 for the format table, the NFKC name grammar, the `disable-model-invocation`/`user-invocable` handling and the immediate-children rule; 174–200 for the compatibility field list, deduplication and layering; 202–218 for `missing_directories`/`duplicate_names`, precedence order and the `~` rule; 220–236 for bundled files, the placeholders and the `read_files` tool limits; 238–258 for the compatibility warning and the on-demand-with-tools alternative; 260–282 for `load()`, `render()`, `$ARGUMENTS` and the `SkippedSkill` reasons; 284–312 for the agent-spec form and the scanner section; 314–340 for the configuration block, the run-start failure list and the combining rule; 342–774 for the API reference. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
