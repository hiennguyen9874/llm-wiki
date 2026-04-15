import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

import { beginTurn, findLikelyWorkflowGaps, recordToolCall, recordToolResult, summarizeAudit, type TurnAuditState } from "./lib/audit";

export default function (pi: ExtensionAPI) {
	let currentTurn: TurnAuditState | null = null;

	pi.on("agent_start", async () => {
		currentTurn = beginTurn();
	});

	pi.on("tool_call", async (event) => {
		if (!currentTurn) currentTurn = beginTurn();
		recordToolCall(currentTurn, event as { toolCallId: string; toolName: string; input: Record<string, unknown> });
		return undefined;
	});

	pi.on("tool_result", async (event) => {
		if (!currentTurn) return undefined;
		recordToolResult(currentTurn, event as { toolCallId: string; isError: boolean });
		return undefined;
	});

	pi.on("agent_end", async (_event, ctx) => {
		if (!currentTurn) return;

		const findings = findLikelyWorkflowGaps(currentTurn);
		const summary = summarizeAudit(currentTurn);

		if (findings.length > 0 && ctx.hasUI) {
			const lines = findings.map((finding) => `- ${finding}`).join("\n");
			const suggestion = currentTurn.rawReads.size > 0 ? "Consider `/ingest`, `/review`, or a manual integration pass." : "Consider `/review` or `/session-end`.";
			ctx.ui.notify(
				`Workflow audit (${summary.changedCount} changed, ${summary.rawReadsCount} raw reads):\n${lines}\n${suggestion}`,
				"warning",
			);
		}

		currentTurn = null;
	});
}
