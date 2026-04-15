import { complete } from "@mariozechner/pi-ai";
import { convertToLlm, serializeConversation } from "@mariozechner/pi-coding-agent";
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

const MAX_SNIPPET_LENGTH = 280;
const MAX_BULLETS = 6;
const MAX_PATHS = 12;

function flattenContent(value: unknown): string {
	if (typeof value === "string") return value;
	if (Array.isArray(value)) return value.map((item) => flattenContent(item)).filter(Boolean).join("\n");
	if (!value || typeof value !== "object") return "";

	if ("text" in value && typeof (value as { text?: unknown }).text === "string") {
		return (value as { text: string }).text;
	}

	if ("content" in value) {
		return flattenContent((value as { content?: unknown }).content);
	}

	return "";
}

function compactWhitespace(text: string): string {
	return text.replace(/\s+/g, " ").trim();
}

function truncate(text: string, maxLength = MAX_SNIPPET_LENGTH): string {
	if (text.length <= maxLength) return text;
	return `${text.slice(0, maxLength - 1).trimEnd()}…`;
}

function extractOriginalQuestion(messages: unknown[]): string {
	for (const message of messages) {
		if (!message || typeof message !== "object") continue;
		if ((message as { role?: unknown }).role !== "user") continue;
		const text = compactWhitespace(flattenContent((message as { content?: unknown }).content));
		if (text) return truncate(text, 420);
	}
	return "Unknown from surviving context; inspect recent retained turns if needed.";
}

function extractRecentBullets(messages: unknown[]): string[] {
	const snippets = messages
		.filter((message) => message && typeof message === "object")
		.map((message) => {
			const role = typeof (message as { role?: unknown }).role === "string" ? (message as { role: string }).role : "unknown";
			const text = compactWhitespace(flattenContent((message as { content?: unknown }).content));
			return { role, text };
		})
		.filter((entry) => entry.text && (entry.role === "user" || entry.role === "assistant"));

	return snippets
		.slice(-12)
		.map((entry) => `${entry.role}: ${truncate(entry.text)}`)
		.filter((entry, index, all) => all.indexOf(entry) === index)
		.slice(0, MAX_BULLETS);
}

function extractPaths(text: string): string[] {
	const matches = text.matchAll(/(?:^|[\s`'"(])((?:\.\/)?(?:raw|wiki|outputs|docs|\.pi)\/[A-Za-z0-9._/-]+|AGENTS\.md|README\.md|PI-HOOKS-IMPLEMENTATION-PLAN\.md)/gm);
	const seen = new Set<string>();
	const paths: string[] = [];

	for (const match of matches) {
		const candidate = match[1]?.replace(/^\.\//, "");
		if (!candidate || seen.has(candidate)) continue;
		seen.add(candidate);
		paths.push(candidate);
		if (paths.length >= MAX_PATHS) break;
	}

	return paths;
}

function buildFallbackSummary(args: {
	messages: unknown[];
	conversationText: string;
	previousSummary?: string;
}): string {
	const originalQuestion = extractOriginalQuestion(args.messages);
	const recentBullets = extractRecentBullets(args.messages);
	const changedPaths = extractPaths(args.conversationText);
	const previous = args.previousSummary?.trim();

	const sections = [
		"## Goal",
		`- ${originalQuestion}`,
		"",
		"## What was done",
		...(recentBullets.length > 0 ? recentBullets.map((item) => `- ${item}`) : ["- Review recent kept turns for the latest detailed actions."]),
		"",
		"## Key findings / decisions",
		...(previous ? ["- Prior compaction context exists; review it alongside retained turns if continuity matters."] : ["- No earlier compaction summary was available."]),
		"- This fallback summary was generated heuristically because model-based compaction was unavailable.",
		"",
		"## Changed files / pages",
		...(changedPaths.length > 0 ? changedPaths.map((item) => `- ${item}`) : ["- No file paths were reliably extracted from the compacted context."]),
		"",
		"## Unresolved questions",
		"- Re-check the most recent retained turns for any open decisions or blocked items.",
		"",
		"## Next recommended steps",
		"- Resume from the latest retained turns and continue the active workflow.",
		...(changedPaths.some((item) => item.startsWith("wiki/") || item.startsWith("outputs/")) ? ["- If durable artifacts were changed, verify `wiki/log.md` and `wiki/index.md` as appropriate."] : []),
	];

	if (previous) {
		sections.push("", "## Previous compaction context", previous);
	}

	return sections.join("\n");
}

async function summarizeWithModel(args: {
	conversationText: string;
	previousSummary?: string;
	signal: AbortSignal;
	ctx: any;
}) {
	const model = args.ctx.modelRegistry.find("google", "gemini-2.5-flash");
	if (!model) return null;

	const auth = await args.ctx.modelRegistry.getApiKeyAndHeaders(model);
	if (!auth.ok || !auth.apiKey) return null;

	const previousContext = args.previousSummary?.trim()
		? `\n\nPrevious compaction summary for continuity:\n${args.previousSummary.trim()}`
		: "";

	const response = await complete(
		model,
		{
			messages: [
				{
					role: "user",
					content: [
						{
							type: "text",
							text: `You are summarizing a pi coding session for future continuation in a manual-first second-brain repository.${previousContext}

Create a compact but information-dense markdown summary for session memory only. This is NOT durable wiki knowledge.

Required sections exactly:
## Goal
## What was done
## Key findings / decisions
## Changed files / pages
## Unresolved questions
## Next recommended steps

Requirements:
- Preserve important repository paths exactly.
- Keep concrete implementation decisions and constraints.
- Distinguish completed work from open follow-up.
- Prefer bullets over prose.
- Include only information needed to continue work effectively.

<conversation>
${args.conversationText}
</conversation>`,
						},
					],
					timestamp: Date.now(),
				},
			],
		},
		{
			apiKey: auth.apiKey,
			headers: auth.headers,
			maxTokens: 2048,
			signal: args.signal,
		},
	);

	return response.content
		.filter((item): item is { type: "text"; text: string } => item.type === "text")
		.map((item) => item.text)
		.join("\n")
		.trim();
}

export default function (pi: ExtensionAPI) {
	pi.on("session_before_compact", async (event, ctx) => {
		const { preparation, signal } = event;
		const { messagesToSummarize, turnPrefixMessages, previousSummary, firstKeptEntryId, tokensBefore } = preparation;
		const allMessages = [...messagesToSummarize, ...turnPrefixMessages];
		if (allMessages.length === 0 || signal.aborted) return undefined;

		const conversationText = serializeConversation(convertToLlm(allMessages));
		let summary = "";

		try {
			summary =
				(await summarizeWithModel({
					conversationText,
					previousSummary,
					signal,
					ctx,
				})) ?? "";
		} catch (error) {
			if (ctx.hasUI && !signal.aborted) {
				const message = error instanceof Error ? error.message : String(error);
				ctx.ui.notify(`Compaction memory fallback: ${message}`, "warning");
			}
		}

		if (!summary) {
			summary = buildFallbackSummary({
				messages: allMessages,
				conversationText,
				previousSummary,
			});
			if (ctx.hasUI && !signal.aborted) {
				ctx.ui.notify("Using heuristic compaction memory summary.", "info");
			}
		}

		if (!summary.trim()) return undefined;

		return {
			compaction: {
				summary,
				firstKeptEntryId,
				tokensBefore,
			},
		};
	});
}
