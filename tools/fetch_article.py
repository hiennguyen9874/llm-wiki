#!/usr/bin/env python3
"""Fetch a page via defuddle and save it as folder/index.md + assets/.

Example:
    python3 tools/fetch_article.py 'https://www.lmsys.org/blog/2026-07-06-dspark-sglang/' -o raw/2026-07-06-dspark-sglang
    python3 tools/fetch_article.py 'https://example.com/post'   # auto folder under raw/

Output layout:
    <output-dir>/
      index.md          # defuddle markdown, image links rewritten to relative paths
      assets/
        perf-compare.png
        ...

Remote images (``![alt](https://...)`` and ``<img src="...">``) are downloaded
into ``assets/`` and rewritten to ``assets/<file>`` so the folder is
self-contained and viewable offline / in Obsidian.
Non-image links are left untouched.
"""

from __future__ import annotations

import argparse
import mimetypes
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

# ![alt](destination "title")  — destination may be <url> or bare url
MD_IMAGE_RE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\(\s*"
    r"(?P<destination><[^>\s]+>|[^)\s]+)"
    r"(?P<title>\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
# <img ... src="..." ...> left over by defuddle (raw HTML figures)
HTML_IMG_RE = re.compile(
    r"<img\b[^>]*?\bsrc\s*=\s*(?P<quote>['\"])(?P<src>.+?)(?P=quote)[^>]*?>",
    re.IGNORECASE | re.DOTALL,
)
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")

IMAGE_EXTENSIONS = {
    ".avif", ".bmp", ".gif", ".jpeg", ".jpg",
    ".png", ".svg", ".webp",
}
CONTENT_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/avif": ".avif",
    "image/bmp": ".bmp",
    "image/svg+xml": ".svg",
}

UA = "llm-wiki-fetch-article/1.0"


def fenced_ranges(text: str) -> list[tuple[int, int]]:
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


def in_range(pos: int, ranges: list[tuple[int, int]]) -> bool:
    return any(s <= pos < e for s, e in ranges)


def slugify(value: str, max_len: int = 80) -> str:
    value = unquote(value).strip().lower()
    value = re.sub(r"\.html?$", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    value = re.sub(r"-{2,}", "-", value)
    return (value[:max_len].rstrip("-") or "article")


def default_output_dir(url: str) -> Path:
    parsed = urlparse(url)
    segments = [s for s in parsed.path.split("/") if s and s not in (".", "..")]
    if segments:
        slug = slugify(segments[-1])
    else:
        slug = slugify(parsed.netloc.replace("www.", ""))
    # prefix date-like parent if present: /blog/2026-07-06-slug/ -> keep full slug
    return ROOT / "raw" / slug


def normalize_output_dir(raw: str) -> Path:
    p = Path(raw)
    # Friendly: allow legacy `-o raw/foo.md` -> folder `raw/foo/`
    if p.suffix.lower() in (".md", ".mdx", ".markdown"):
        p = p.with_suffix("")
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


def extension_from_content_type(content_type: str, url: str) -> str:
    suffix = Path(unquote(urlparse(url).path)).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return suffix
    media = content_type.split(";", 1)[0].strip().lower()
    if media in CONTENT_EXTENSIONS:
        return CONTENT_EXTENSIONS[media]
    guessed = mimetypes.guess_extension(media) if media else None
    if guessed:
        guessed = guessed.lower()
        if guessed in IMAGE_EXTENSIONS:
            return guessed
        if guessed == ".jpe":
            return ".jpg"
    return ""


def sanitize_basename(name: str) -> str:
    name = unquote(name).strip().split("/")[-1]
    name = re.sub(r"[?#].*$", "", name)
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-_.")
    return name[:100] or ""


def unique_name(directory: Path, desired: str, taken: set[str]) -> str:
    candidate = desired
    stem, dot, ext = desired.partition(".") if "." in desired else (desired, "", "")
    # partition splits on first dot; we want last dot
    if "." in desired:
        stem = desired.rsplit(".", 1)[0]
        ext = "." + desired.rsplit(".", 1)[1]
    else:
        stem, ext = desired, ""
    i = 2
    while candidate in taken or (directory / candidate).exists():
        candidate = f"{stem}-{i}{ext}"
        i += 1
    taken.add(candidate)
    return candidate


def run_defuddle(url: str, frontmatter: bool, user_agent: str | None,
                 defuddle_bin: str, timeout: int) -> str:
    exe = defuddle_bin or shutil.which("defuddle")
    if not exe:
        raise RuntimeError("defuddle not found in PATH (install with: npm i -g defuddle)")
    cmd = [exe, "parse", url, "--md"]
    if frontmatter:
        cmd.append("--frontmatter")
    if user_agent:
        cmd += ["--user-agent", user_agent]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"defuddle timed out after {timeout}s") from exc
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()[:2000]
        raise RuntimeError(f"defuddle failed (exit {proc.returncode}): {err}")
    if not proc.stdout.strip():
        raise RuntimeError("defuddle returned empty markdown")
    return proc.stdout


def collect_markdown_images(text: str, page_url: str) -> list[re.Match]:
    ranges = fenced_ranges(text)
    out = []
    for m in MD_IMAGE_RE.finditer(text):
        if in_range(m.start(), ranges):
            continue
        dest = m.group("destination").strip().strip("<>")
        if not dest or dest.startswith("#") or dest.startswith("data:"):
            continue
        abs_url = urljoin(page_url, dest)
        if urlparse(abs_url).scheme not in ("http", "https"):
            continue
        out.append(m)
    return out


def collect_html_images(text: str, page_url: str) -> list[re.Match]:
    ranges = fenced_ranges(text)
    out = []
    for m in HTML_IMG_RE.finditer(text):
        if in_range(m.start(), ranges):
            continue
        src = (m.group("src") or "").strip()
        if not src or src.startswith("data:"):
            continue
        abs_url = urljoin(page_url, src)
        if urlparse(abs_url).scheme not in ("http", "https"):
            continue
        out.append(m)
    return out


def download_bytes(url: str, timeout: int) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": UA})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read(), resp.headers.get("Content-Type", "")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"could not download {url}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="Page URL to fetch")
    ap.add_argument("-o", "--output", default=None,
                    help="Output folder (default: raw/<slug> derived from URL). "
                         "A trailing .md path is accepted and treated as folder.")
    ap.add_argument("--index-name", default="index.md", help="Markdown filename inside folder (default: index.md)")
    ap.add_argument("--assets-dir", default="assets", help="Assets subfolder name (default: assets)")
    ap.add_argument("--no-frontmatter", action="store_true", help="Do not prepend defuddle YAML frontmatter")
    ap.add_argument("--no-download", action="store_true", help="Skip image downloading, keep remote URLs")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing index.md and redownload existing assets")
    ap.add_argument("--strict", action="store_true",
                    help="Fail on first image download error instead of keeping remote URL")
    ap.add_argument("--timeout", type=int, default=60, help="defuddle timeout in seconds (default: 60)")
    ap.add_argument("--dl-timeout", type=int, default=30, help="per-image download timeout (default: 30)")
    ap.add_argument("--user-agent", default=None, help="Custom User-Agent for defuddle (helps with 403s)")
    ap.add_argument("--defuddle-bin", default="defuddle", help="defuddle binary (default: defuddle)")
    args = ap.parse_args(argv)

    parsed = urlparse(args.url)
    if parsed.scheme not in ("http", "https"):
        print(f"error: not an http(s) URL: {args.url}", file=sys.stderr)
        return 1

    out_dir = normalize_output_dir(args.output) if args.output else default_output_dir(args.url)
    index_path = out_dir / args.index_name
    assets_path = out_dir / args.assets_dir

    if index_path.exists() and not args.force:
        print(f"error: {index_path} already exists (use --force to overwrite). "
              f"raw/ is treated as immutable evidence.", file=sys.stderr)
        return 1

    print(f"fetch  {args.url}")
    try:
        md = run_defuddle(args.url, frontmatter=not args.no_frontmatter,
                          user_agent=args.user_agent,
                          defuddle_bin=args.defuddle_bin, timeout=args.timeout)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.no_download:
        out_dir.mkdir(parents=True, exist_ok=True)
        index_path.write_text(md, encoding="utf-8")
        print(f"wrote  {index_path} (images not downloaded)")
        return 0

    md_matches = collect_markdown_images(md, args.url)
    html_matches = collect_html_images(md, args.url)
    total_refs = len(md_matches) + len(html_matches)
    if total_refs == 0:
        out_dir.mkdir(parents=True, exist_ok=True)
        index_path.write_text(md, encoding="utf-8")
        print(f"wrote  {index_path} (no remote images found)")
        return 0

    print(f"images {total_refs} remote reference(s) "
          f"({len(md_matches)} markdown, {len(html_matches)} html)")

    assets_path.mkdir(parents=True, exist_ok=True)
    url_to_file: dict[str, str] = {}
    taken: set[str] = {p.name for p in assets_path.iterdir() if p.is_file()}
    failed = 0
    saved = 0

    # --- download each unique URL once ---
    ordered_urls: list[str] = []
    for m in md_matches:
        u = urljoin(args.url, m.group("destination").strip().strip("<>"))
        if u not in url_to_file and u not in ordered_urls:
            ordered_urls.append(u)
    for m in html_matches:
        u = urljoin(args.url, m.group("src").strip())
        if u not in url_to_file and u not in ordered_urls:
            ordered_urls.append(u)

    for i, url in enumerate(ordered_urls, 1):
        base = sanitize_basename(urlparse(url).path)
        stem_ext = Path(base).suffix.lower()
        if base and stem_ext in IMAGE_EXTENSIONS:
            desired = base
        elif base and "." in base:
            # keep stem, normalize ext later if needed
            desired = base
        else:
            desired = (base or f"image-{i}")
        try:
            data, ctype = download_bytes(url, timeout=args.dl_timeout)
            if not data:
                raise RuntimeError("empty response")
            ext = Path(desired).suffix.lower()
            if ext not in IMAGE_EXTENSIONS:
                detected = extension_from_content_type(ctype, url)
                if detected:
                    stem = desired.rsplit(".", 1)[0] if "." in desired else desired
                    desired = f"{stem}{detected}"
                else:
                    desired = f"{desired}.img" if "." not in desired else desired
            # normalize .jpeg -> keep as-is; ensure filename safe
            desired = sanitize_basename(desired) or f"image-{i}.img"
            fname = desired if url not in url_to_file else url_to_file[url]
            if url not in url_to_file:
                fname = unique_name(assets_path, desired, taken)
                dest = assets_path / fname
                if dest.exists() and dest.stat().st_size > 0 and not args.force:
                    print(f"exists {dest.relative_to(ROOT) if dest.is_relative_to(ROOT) else dest}")
                else:
                    tmp = dest.with_name(dest.name + ".part")
                    tmp.write_bytes(data)
                    tmp.replace(dest)
                    print(f"saved  {dest.relative_to(ROOT) if dest.is_relative_to(ROOT) else dest}")
                    saved += 1
                url_to_file[url] = fname
        except RuntimeError as exc:
            print(f"warn   {exc}", file=sys.stderr)
            failed += 1
            if args.strict:
                print("error: --strict set, aborting", file=sys.stderr)
                return 1
            continue

    # --- rewrite markdown (reverse order so offsets stay valid) ---
    replacements: list[tuple[int, int, str]] = []
    for m in md_matches:
        url = urljoin(args.url, m.group("destination").strip().strip("<>"))
        fname = url_to_file.get(url)
        if not fname:
            continue  # download failed -> keep remote
        rel = f"{args.assets_dir}/{fname}"
        rep = f"![{m.group('alt')}]({rel}"
        if m.group("title"):
            rep += m.group("title")
        rep += ")"
        replacements.append((m.start(), m.end(), rep))

    for m in html_matches:
        url = urljoin(args.url, m.group("src").strip())
        fname = url_to_file.get(url)
        if not fname:
            continue
        rel = f"{args.assets_dir}/{fname}"
        old_tag = m.group(0)
        new_tag = re.sub(r'\bsrc\s*=\s*(["\']).*?\1', f'src="{rel}"', old_tag, count=1, flags=re.IGNORECASE)
        replacements.append((m.start(), m.end(), new_tag))

    replacements.sort(key=lambda r: r[0], reverse=True)
    for s, e, rep in replacements:
        md = md[:s] + rep + md[e:]

    out_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text(md, encoding="utf-8")
    try:
        disp_index = index_path.relative_to(ROOT)
    except ValueError:
        disp_index = index_path
    print(f"wrote  {disp_index} ({len(replacements)} rewritten, {failed} failed, {saved} downloaded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
