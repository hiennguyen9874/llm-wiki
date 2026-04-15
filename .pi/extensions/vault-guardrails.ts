import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

import { hasYamlFrontmatter, isKebabCaseFilename } from "./lib/frontmatter";
import { collectDangerousBashReasons, isApprovedRawCreatePath } from "./lib/policy";
import { scanForSensitivePatterns } from "./lib/secrets";
import {
	fileExists,
	isOutputsPath,
	isProtectedPolicyPath,
	isRawPath,
	isWikiLogPath,
	isWikiPath,
	toRepoRelative,
} from "./lib/paths";

function notify(ctx: { hasUI: boolean; ui: { notify: (message: string, level: "info" | "success" | "warning" | "error") => void } }, message: string, level: "info" | "success" | "warning" | "error" = "warning") {
	if (ctx.hasUI) ctx.ui.notify(message, level);
}

function summarizeHits(content: string): { high: string[]; medium: string[] } {
	const hits = scanForSensitivePatterns(content);
	const high = hits.filter((hit) => hit.confidence === "high").map((hit) => hit.kind);
	const medium = hits.filter((hit) => hit.confidence === "medium").map((hit) => hit.kind);
	return {
		high: Array.from(new Set(high)),
		medium: Array.from(new Set(medium)),
	};
}

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", async (event, ctx) => {
		if (event.toolName === "bash") {
			const command = typeof event.input.command === "string" ? event.input.command : "";
			const reasons = collectDangerousBashReasons(command);
			if (reasons.length === 0) return undefined;

			if (!ctx.hasUI) {
				return {
					block: true,
					reason: `Potentially destructive bash blocked: ${reasons.join(", ")}`,
				};
			}

			const allow = await ctx.ui.confirm(
				"Allow potentially destructive bash?",
				`${command}\n\nReasons: ${reasons.join(", ")}`,
			);
			if (!allow) {
				return { block: true, reason: "Blocked by user" };
			}
			return undefined;
		}

		if (event.toolName !== "write" && event.toolName !== "edit") return undefined;
		if (typeof event.input.path !== "string") return undefined;

		const relativePath = toRepoRelative(event.input.path, ctx.cwd);
		const exists = fileExists(relativePath);

		if (event.toolName === "edit" && isRawPath(relativePath)) {
			return { block: true, reason: "`raw/` is immutable; create a new capture instead of editing in place." };
		}

		if (event.toolName === "write" && isRawPath(relativePath) && exists) {
			return { block: true, reason: "Overwriting existing files in `raw/` is blocked; preserve raw captures immutably." };
		}

		if (event.toolName === "write" && isRawPath(relativePath) && !isApprovedRawCreatePath(relativePath)) {
			notify(ctx, `Creating a raw file outside the standard capture folders: ${relativePath}`);
		}

		if (event.toolName === "write" && isWikiLogPath(relativePath) && exists) {
			return { block: true, reason: "Direct writes to `wiki/log.md` are blocked; append with `edit` instead." };
		}

		if (isProtectedPolicyPath(relativePath)) {
			notify(ctx, `Editing governance or workflow policy file: ${relativePath}`);
		}

		let candidateContent = "";
		if (event.toolName === "write") {
			candidateContent = typeof event.input.content === "string" ? event.input.content : "";
		} else {
			const edits = Array.isArray(event.input.edits) ? event.input.edits : [];
			candidateContent = edits
				.map((entry) => {
					if (!entry || typeof entry !== "object") return "";
					const newText = (entry as { newText?: unknown }).newText;
					return typeof newText === "string" ? newText : "";
				})
				.join("\n");
		}

		if ((isWikiPath(relativePath) || isOutputsPath(relativePath)) && candidateContent) {
			const hits = summarizeHits(candidateContent);
			if (hits.high.length > 0) {
				return {
					block: true,
					reason: `Sensitive content detected in downstream artifact: ${hits.high.join(", ")}`,
				};
			}
			if (hits.medium.length > 0) {
				notify(ctx, `Potential sensitive content detected in ${relativePath}: ${hits.medium.join(", ")}`);
			}
		}

		if (event.toolName === "write" && !exists && (isWikiPath(relativePath) || isOutputsPath(relativePath)) && relativePath.endsWith(".md")) {
			if (!isKebabCaseFilename(relativePath)) {
				notify(ctx, `Filename should usually be lowercase kebab-case: ${relativePath}`);
			}

			if (isWikiPath(relativePath) && !hasYamlFrontmatter(candidateContent)) {
				notify(ctx, `New wiki note is missing YAML frontmatter: ${relativePath}`);
			}
		}

		return undefined;
	});
}
