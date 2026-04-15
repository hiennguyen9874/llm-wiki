import * as path from "node:path";

import { toRepoRelative } from "./paths";

export function hasYamlFrontmatter(content: string): boolean {
	return /^---\n[\s\S]*?\n---(?:\n|$)/.test(content);
}

export function isKebabCaseFilename(inputPath: string): boolean {
	const relative = toRepoRelative(inputPath);
	const ext = path.posix.extname(relative);
	const base = path.posix.basename(relative, ext);
	return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(base);
}

export function looksLikeMarkdownCitation(content: string): boolean {
	return (
		/\[\[[^\]]+\]\]/.test(content) ||
		/\[[^\]]+\]\(https?:\/\/[^\s)]+\)/.test(content) ||
		/^#{1,6}\s+Sources?\b/m.test(content) ||
		/^related_sources:/m.test(content)
	);
}
