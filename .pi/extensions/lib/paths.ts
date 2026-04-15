import * as fs from "node:fs";
import * as path from "node:path";

const repoRoot = normalizeSlashes(process.cwd());

export function normalizeSlashes(value: string): string {
	return value.replace(/\\/g, "/");
}

export function resolveInRepo(inputPath: string, cwd = repoRoot): string {
	const target = inputPath.trim();
	const resolved = path.isAbsolute(target) ? path.normalize(target) : path.resolve(cwd, target);
	return normalizeSlashes(resolved);
}

export function toRepoRelative(inputPath: string, cwd = repoRoot): string {
	const resolved = resolveInRepo(inputPath, cwd);
	const relative = path.relative(repoRoot, resolved);

	if (relative && !relative.startsWith("..") && !path.isAbsolute(relative)) {
		return normalizeSlashes(relative) || ".";
	}

	return resolved;
}

export function normalizeRepoRelativePath(inputPath: string, cwd = repoRoot): string | null {
	const trimmed = inputPath.trim();
	if (!trimmed) return null;
	return toRepoRelative(trimmed, cwd);
}

export function fileExists(inputPath: string, cwd = repoRoot): boolean {
	try {
		return fs.existsSync(resolveInRepo(inputPath, cwd));
	} catch {
		return false;
	}
}

export function isUnderRepo(inputPath: string, cwd = repoRoot): boolean {
	const relative = toRepoRelative(inputPath, cwd);
	return !path.isAbsolute(relative) && relative !== "." && !relative.startsWith("../");
}

export function isSingleToken(text: string): boolean {
	const trimmed = text.trim();
	return Boolean(trimmed) && !/\s/.test(trimmed);
}

export function isSingleUrl(text: string): boolean {
	const trimmed = text.trim();
	if (!isSingleToken(trimmed)) return false;

	try {
		const url = new URL(trimmed);
		return url.protocol === "http:" || url.protocol === "https:";
	} catch {
		return false;
	}
}

export function isRawPath(inputPath: string, cwd = repoRoot): boolean {
	const relative = toRepoRelative(inputPath, cwd);
	return relative === "raw" || relative.startsWith("raw/");
}

export function isWikiPath(inputPath: string, cwd = repoRoot): boolean {
	const relative = toRepoRelative(inputPath, cwd);
	return relative === "wiki" || relative.startsWith("wiki/");
}

export function isOutputsPath(inputPath: string, cwd = repoRoot): boolean {
	const relative = toRepoRelative(inputPath, cwd);
	return relative === "outputs" || relative.startsWith("outputs/");
}

export function isPiPath(inputPath: string, cwd = repoRoot): boolean {
	const relative = toRepoRelative(inputPath, cwd);
	return relative === ".pi" || relative.startsWith(".pi/");
}

export function isWikiLogPath(inputPath: string, cwd = repoRoot): boolean {
	return toRepoRelative(inputPath, cwd) === "wiki/log.md";
}

export function isWikiIndexPath(inputPath: string, cwd = repoRoot): boolean {
	return toRepoRelative(inputPath, cwd) === "wiki/index.md";
}

export function isMarkdownPath(inputPath: string, cwd = repoRoot): boolean {
	return toRepoRelative(inputPath, cwd).endsWith(".md");
}

export function isProtectedPolicyPath(inputPath: string, cwd = repoRoot): boolean {
	const relative = toRepoRelative(inputPath, cwd);
	return relative === "AGENTS.md" || relative.startsWith(".pi/prompts/") || relative.startsWith(".pi/skills/");
}

export function isLikelyRawPath(text: string, cwd = repoRoot): boolean {
	if (!isSingleToken(text)) return false;
	if (text.trim().startsWith("/")) return false;
	if (isSingleUrl(text)) return false;

	const normalized = normalizeRepoRelativePath(text, cwd);
	if (!normalized) return false;
	if (!isRawPath(normalized, cwd)) return false;

	return fileExists(normalized, repoRoot);
}

export function countFilesRecursively(relativeDir: string): number {
	const root = resolveInRepo(relativeDir);
	if (!fs.existsSync(root)) return 0;

	let count = 0;
	const stack = [root];

	while (stack.length) {
		const current = stack.pop();
		if (!current) continue;

		for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
			if (entry.name.startsWith(".")) continue;
			const fullPath = path.join(current, entry.name);
			if (entry.isDirectory()) stack.push(fullPath);
			else if (entry.isFile()) count += 1;
		}
	}

	return count;
}
