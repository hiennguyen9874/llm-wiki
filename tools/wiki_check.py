#!/usr/bin/env python3
"""Deterministic structural checks for the LLM wiki; standard library only."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
RESERVED = {"index.md", "log.md"}
REQUIRED = ("type", "title", "description")
VALID_STATUS = {"draft", "stable", "deprecated"}
LINK_RE = re.compile(r"(?<!!)\[[^]]*\]\(((?:\\.|[^)\s])+)(?:\s+['\"].*?['\"])?\)")


def frontmatter(path: Path) -> tuple[str | None, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, lines
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None, lines
    return "\n".join(lines[1:end]), lines[end + 1 :]


def field(block: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", block)
    if not match:
        return None
    value = match.group(1).strip().strip("'\"")
    return value or None


def links(path: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8")
    targets: list[Path] = []
    for raw in LINK_RE.findall(text):
        target = unquote(raw.replace(r"\(", "(").replace(r"\)", ")").split("#", 1)[0])
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        resolved = (WIKI / target.lstrip("/")) if target.startswith("/") else (path.parent / target)
        if resolved.is_dir():
            resolved /= "index.md"
        targets.append(resolved.resolve())
    return targets


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    errors: list[str] = []
    concepts = sorted(p.resolve() for p in WIKI.rglob("*.md") if p.name not in RESERVED)
    indexes = sorted(p.resolve() for p in WIKI.rglob("index.md"))

    for concept in concepts:
        block, _ = frontmatter(concept)
        if block is None:
            errors.append(f"frontmatter: {relative(concept)} is missing or unclosed")
            continue
        for key in REQUIRED:
            if field(block, key) is None:
                errors.append(f"metadata: {relative(concept)} missing {key}")
        status = field(block, "status")
        if status and status not in VALID_STATUS:
            errors.append(f"lifecycle: {relative(concept)} has invalid status {status!r}")

    index_refs: Counter[Path] = Counter()
    index_links: dict[Path, list[Path]] = {}
    for index in indexes:
        index_links[index] = links(index)
        for target in index_links[index]:
            if target in concepts:
                index_refs[target] += 1

    root_index = (WIKI / "index.md").resolve()
    reachable_indexes: set[Path] = set()
    pending = [root_index]
    while pending:
        index = pending.pop()
        if index in reachable_indexes or index not in index_links:
            continue
        reachable_indexes.add(index)
        pending.extend(target for target in index_links[index] if target in index_links)
    for index in indexes:
        if index not in reachable_indexes:
            errors.append(f"index: {relative(index)} is unreachable from wiki/index.md")

    for concept in concepts:
        count = index_refs[concept]
        if count == 0:
            errors.append(f"index: {relative(concept)} is not listed")
        elif count > 1:
            errors.append(f"index: {relative(concept)} is listed {count} times")

    for page in sorted(p.resolve() for p in WIKI.rglob("*.md")):
        for target in links(page):
            if not target.exists():
                errors.append(f"link: {relative(page)} -> {relative(target)} is missing")

    if errors:
        print(f"FAIL: {len(errors)} structural issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"OK: {len(concepts)} concept(s), {len(indexes)} index file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
