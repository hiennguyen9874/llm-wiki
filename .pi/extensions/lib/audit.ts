import * as fs from "node:fs";
import * as path from "node:path";

import { looksLikeMarkdownCitation } from "./frontmatter";
import {
	fileExists,
	isMarkdownPath,
	isOutputsPath,
	isRawPath,
	isWikiIndexPath,
	isWikiLogPath,
	isWikiPath,
	resolveInRepo,
	toRepoRelative,
} from "./paths";

export type TurnAuditState = {
	startedAt: number;
	pending: Map<string, { toolName: string; path?: string; isNew?: boolean }>;
	rawReads: Set<string>;
	changedPaths: Set<string>;
	wikiChanged: Set<string>;
	outputsChanged: Set<string>;
	newWikiPages: Set<string>;
	newOutputMarkdown: Set<string>;
	newVisualArtifacts: Set<string>;
	sourceLikePages: Set<string>;
	touchedIndex: boolean;
	touchedLog: boolean;
};

export function beginTurn(): TurnAuditState {
	return {
		startedAt: Date.now(),
		pending: new Map(),
		rawReads: new Set(),
		changedPaths: new Set(),
		wikiChanged: new Set(),
		outputsChanged: new Set(),
		newWikiPages: new Set(),
		newOutputMarkdown: new Set(),
		newVisualArtifacts: new Set(),
		sourceLikePages: new Set(),
		touchedIndex: false,
		touchedLog: false,
	};
}

export function recordToolCall(state: TurnAuditState, event: { toolCallId: string; toolName: string; input: Record<string, unknown> }): void {
	if (event.toolName !== "read" && event.toolName !== "write" && event.toolName !== "edit") return;

	const rawPath = typeof event.input.path === "string" ? event.input.path : "";
	if (!rawPath) return;

	const relativePath = toRepoRelative(rawPath);
	state.pending.set(event.toolCallId, {
		toolName: event.toolName,
		path: relativePath,
		isNew: event.toolName === "write" ? !fileExists(relativePath) : false,
	});
}

export function recordToolResult(
	state: TurnAuditState,
	event: { toolCallId: string; isError: boolean },
): void {
	const pending = state.pending.get(event.toolCallId);
	if (!pending) return;
	state.pending.delete(event.toolCallId);
	if (event.isError || !pending.path) return;

	const relativePath = pending.path;

	if (pending.toolName === "read") {
		if (isRawPath(relativePath)) state.rawReads.add(relativePath);
		return;
	}

	state.changedPaths.add(relativePath);

	if (isWikiLogPath(relativePath)) state.touchedLog = true;
	if (isWikiIndexPath(relativePath)) state.touchedIndex = true;

	if (isWikiPath(relativePath) && !isWikiLogPath(relativePath) && !isWikiIndexPath(relativePath)) {
		state.wikiChanged.add(relativePath);
		if (pending.isNew) {
			if (isMarkdownPath(relativePath)) state.newWikiPages.add(relativePath);
			if (relativePath.startsWith("wiki/bases/") || relativePath.startsWith("wiki/canvases/")) {
				state.newVisualArtifacts.add(relativePath);
			}
			if (path.posix.basename(relativePath).startsWith("source-")) {
				state.sourceLikePages.add(relativePath);
			}
		}
	}

	if (isOutputsPath(relativePath)) {
		state.outputsChanged.add(relativePath);
		if (pending.isNew && isMarkdownPath(relativePath)) {
			state.newOutputMarkdown.add(relativePath);
		}
	}
}

export function summarizeAudit(state: TurnAuditState): {
	changedCount: number;
	wikiChangedCount: number;
	outputsChangedCount: number;
	rawReadsCount: number;
} {
	return {
		changedCount: state.changedPaths.size,
		wikiChangedCount: state.wikiChanged.size,
		outputsChangedCount: state.outputsChanged.size,
		rawReadsCount: state.rawReads.size,
	};
}

export function findLikelyWorkflowGaps(state: TurnAuditState): string[] {
	const findings: string[] = [];
	const durableChangeCount = state.wikiChanged.size + state.outputsChanged.size;

	if (durableChangeCount > 0 && !state.touchedLog) {
		findings.push("Changed durable artifacts without appending `wiki/log.md`.");
	}

	if ((state.newWikiPages.size > 0 || state.newVisualArtifacts.size > 0) && !state.touchedIndex) {
		findings.push("Created important wiki artifacts without updating `wiki/index.md`.");
	}

	if (state.outputsChanged.size > 0 && state.wikiChanged.size === 0) {
		findings.push("Updated `outputs/` without integrating any `wiki/` pages.");
	}

	if (state.rawReads.size > 0) {
		if (state.wikiChanged.size === 0) {
			findings.push("Read from `raw/` but did not update any canonical `wiki/` pages.");
		} else if (state.wikiChanged.size === 1 && state.sourceLikePages.size === 0) {
			findings.push("Ingest-like work touched only one wiki page and no `source-*` page.");
		}
	}

	const uncited = [...state.newWikiPages, ...state.newOutputMarkdown].filter((relativePath) => {
		if (!fileExists(relativePath)) return false;
		try {
			const content = fs.readFileSync(resolveInRepo(relativePath), "utf-8");
			return !looksLikeMarkdownCitation(content);
		} catch {
			return false;
		}
	});

	if (uncited.length > 0) {
		const preview = uncited.slice(0, 3).join(", ");
		const suffix = uncited.length > 3 ? ` (+${uncited.length - 3} more)` : "";
		findings.push(`New markdown may need explicit citations: ${preview}${suffix}.`);
	}

	return findings;
}
