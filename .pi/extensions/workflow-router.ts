import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

import { isLikelyRawPath, isSingleUrl, normalizeRepoRelativePath } from "./lib/paths";

const ALIASES: Record<string, string> = {
	review: "/review",
	lint: "/lint",
	"privacy-scan": "/privacy-scan",
	"session-start": "/session-start",
	"session-end": "/session-end",
};

export default function (pi: ExtensionAPI) {
	pi.on("input", async (event, ctx) => {
		if (event.source === "extension") return { action: "continue" };

		const text = event.text.trim();
		if (!text || text.startsWith("/")) return { action: "continue" };

		const alias = ALIASES[text.toLowerCase()];
		if (alias) return { action: "transform", text: alias };

		if (isSingleUrl(text)) {
			return { action: "transform", text: `/ingest-url ${text}` };
		}

		if (isLikelyRawPath(text, ctx.cwd)) {
			const normalized = normalizeRepoRelativePath(text, ctx.cwd) ?? text;
			return { action: "transform", text: `/ingest ${normalized}` };
		}

		return { action: "continue" };
	});
}
