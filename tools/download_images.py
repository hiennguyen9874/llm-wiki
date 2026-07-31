#!/usr/bin/env python3
"""Download remote Markdown images into ``raw/assets``.

Usage::

    python3 tools/download_images.py raw/article.md
    python3 tools/download_images.py              # all Markdown files in raw/

Remote image links are changed to Markdown image links pointing at a path
relative to the source file, for example ``assets/article/image-1.jpg``.
Only links that look like images are considered: explicit Markdown images,
links labelled Image/Photo/etc., and URLs with a known image extension or
format query parameter.
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
ASSETS = RAW / "assets"

# The destination part intentionally does not include whitespace or ')' so it
# also handles the Twitter URLs used by the imported source files.
LINK_RE = re.compile(
    r"(?P<bang>!?)(?:\[(?P<label>[^]]*)\])\(\s*"
    r"(?P<destination><https?://[^>\s]+>|https?://[^)\s]+)"
    r"(?P<title>\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
IMAGE_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".webp",
}
IMAGE_LABEL_RE = re.compile(r"^\s*(?:image|img|figure|photo|picture)\b", re.I)
FORMAT_EXTENSIONS = {ext.lstrip(".") for ext in IMAGE_EXTENSIONS}
CONTENT_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/avif": ".avif",
    "image/bmp": ".bmp",
    "image/svg+xml": ".svg",
}


def fenced_ranges(text: str) -> list[tuple[int, int]]:
    """Return character ranges occupied by fenced code blocks."""
    ranges: list[tuple[int, int]] = []
    start: int | None = None
    offset = 0
    for line in text.splitlines(keepends=True):
        if FENCE_RE.match(line):
            if start is None:
                start = offset
            else:
                ranges.append((start, offset + len(line)))
                start = None
        offset += len(line)
    if start is not None:
        ranges.append((start, len(text)))
    return ranges


def in_range(position: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in ranges)


def url_is_image(label: str, bang: str, url: str) -> bool:
    if bang:
        return True
    parsed = urlparse(url)
    suffix = Path(unquote(parsed.path)).suffix.lower()
    if suffix in IMAGE_EXTENSIONS or IMAGE_LABEL_RE.match(label):
        return True
    formats = parse_qs(parsed.query).get("format", [])
    return any(value.lower().lstrip(".") in FORMAT_EXTENSIONS for value in formats)


def extension_from_response(url: str, content_type: str) -> str:
    parsed = urlparse(url)
    suffix = Path(unquote(parsed.path)).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return suffix

    formats = parse_qs(parsed.query).get("format", [])
    for value in formats:
        value = value.lower().lstrip(".")
        if value in FORMAT_EXTENSIONS:
            return ".jpeg" if value == "jpeg" else f".{value}"

    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type in CONTENT_EXTENSIONS:
        return CONTENT_EXTENSIONS[media_type]
    guessed = mimetypes.guess_extension(media_type) if media_type else None
    return guessed if guessed in IMAGE_EXTENSIONS else ".img"


def download(url: str, destination: Path, force: bool, timeout: int) -> None:
    if destination.exists() and destination.stat().st_size > 0 and not force:
        print(f"exists  {destination.relative_to(ROOT)}")
        return

    request = Request(url, headers={"User-Agent": "llm-wiki-image-downloader/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"could not download {url}: {exc}") from exc

    if not data:
        raise RuntimeError(f"downloaded an empty response from {url}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".part")
    temporary.write_bytes(data)
    temporary.replace(destination)
    print(f"saved   {destination.relative_to(ROOT)}")


def source_files(paths: list[str]) -> list[Path]:
    if paths:
        result = []
        for value in paths:
            path = Path(value)
            if not path.is_absolute():
                path = (Path.cwd() / path).resolve()
            if path.suffix.lower() != ".md":
                raise ValueError(f"not a Markdown file: {value}")
            if not path.is_file():
                raise ValueError(f"file does not exist: {value}")
            result.append(path)
        return result
    return sorted(
        path
        for path in RAW.rglob("*.md")
        if path.is_file() and ASSETS not in path.parents
    )


def process(path: Path, force: bool, timeout: int) -> int:
    text = path.read_text(encoding="utf-8")
    ranges = fenced_ranges(text)
    matches = [
        match
        for match in LINK_RE.finditer(text)
        if not in_range(match.start(), ranges)
        and url_is_image(
            match.group("label"), match.group("bang"), match.group("destination").strip("<>")
        )
    ]
    if not matches:
        print(f"skip    {path.relative_to(ROOT)} (no remote images)")
        return 0

    folder = ASSETS / path.stem
    replacements: list[tuple[int, int, str]] = []
    downloaded: dict[str, str] = {}
    for index, match in enumerate(matches, 1):
        url = match.group("destination").strip("<>")
        local_name = downloaded.get(url)
        if local_name is None:
            # Download once per URL. The response determines the extension for
            # extensionless CDN URLs such as pbs.twimg.com/media/....
            parsed_suffix = Path(unquote(urlparse(url).path)).suffix.lower()
            query_format = parse_qs(urlparse(url).query).get("format", [""])[0].lower()
            extension = parsed_suffix if parsed_suffix in IMAGE_EXTENSIONS else (
                ".jpeg" if query_format == "jpeg" else f".{query_format}" if query_format in FORMAT_EXTENSIONS else ""
            )
            if not extension:
                # Start with .img, then use the response content type to give
                # extensionless CDN URLs a useful extension.
                extension = ".img"
            local_name = f"image-{index}{extension}"
            destination = folder / local_name
            if extension == ".img" or not destination.exists():
                if extension == ".img":
                    # Download once and use the response content type to give
                    # the file a useful extension when possible.
                    request = Request(url, headers={"User-Agent": "llm-wiki-image-downloader/1.0"})
                    try:
                        with urlopen(request, timeout=timeout) as response:
                            data = response.read()
                            response_extension = extension_from_response(url, response.headers.get("Content-Type", ""))
                    except (HTTPError, URLError, TimeoutError) as exc:
                        raise RuntimeError(f"could not download {url}: {exc}") from exc
                    if not data:
                        raise RuntimeError(f"downloaded an empty response from {url}")
                    local_name = f"image-{index}{response_extension}"
                    destination = folder / local_name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    temporary = destination.with_name(destination.name + ".part")
                    temporary.write_bytes(data)
                    temporary.replace(destination)
                    print(f"saved   {destination.relative_to(ROOT)}")
                else:
                    download(url, destination, force, timeout)
            else:
                print(f"exists  {destination.relative_to(ROOT)}")
            downloaded[url] = local_name

        asset = folder / local_name
        relative_asset = Path(os.path.relpath(asset, path.parent)).as_posix()
        # Convert the source's `[Image 1](...)` form to an actual Markdown
        # image while retaining the label and any optional title.
        replacement = f"![{match.group('label')}]({relative_asset}"
        if match.group("title"):
            replacement += match.group("title")
        replacement += ")"
        replacements.append((match.start(), match.end(), replacement))

    for start, end, replacement in reversed(replacements):
        text = text[:start] + replacement + text[end:]
    path.write_text(text, encoding="utf-8")
    print(f"updated {path.relative_to(ROOT)} ({len(matches)} image link(s))")
    return len(matches)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Markdown files (default: all Markdown files under raw/)")
    parser.add_argument("--force", action="store_true", help="redownload existing assets")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds (default: 30)")
    args = parser.parse_args(argv)

    try:
        files = source_files(args.files)
        total = sum(process(path, args.force, args.timeout) for path in files)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"processed {len(files)} file(s), {total} image link(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
