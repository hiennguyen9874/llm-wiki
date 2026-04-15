import * as fs from "node:fs";

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

import { daysSince, findLastAction, parseLogActions } from "./lib/log";
import { REMINDER_THRESHOLDS, REMINDER_WATCH_DIRS } from "./lib/policy";
import { countFilesRecursively, isOutputsPath, isWikiPath, resolveInRepo, toRepoRelative } from "./lib/paths";

function buildStartupReminders(): string[] {
	const reminders: string[] = [];

	const pendingCounts = REMINDER_WATCH_DIRS.map((dir) => ({ dir, count: countFilesRecursively(dir) })).filter((entry) => entry.count > 0);
	if (pendingCounts.length > 0) {
		reminders.push(`Pending captures: ${pendingCounts.map((entry) => `${entry.dir}=${entry.count}`).join(", ")}.`);
	}

	try {
		const logContent = fs.readFileSync(resolveInRepo("wiki/log.md"), "utf-8");
		const entries = parseLogActions(logContent);

		const review = findLastAction(entries, "review");
		if (!review) reminders.push("No `review` entry yet; consider `/review` soon.");
		else if (daysSince(review.date) > REMINDER_THRESHOLDS.reviewDays) {
			reminders.push(`Last review was ${daysSince(review.date)} days ago; consider /review.`);
		}

		const lint = findLastAction(entries, "lint");
		if (!lint) reminders.push("No `lint` entry yet; consider `/lint` when convenient.");
		else if (daysSince(lint.date) > REMINDER_THRESHOLDS.lintDays) {
			reminders.push(`Last lint was ${daysSince(lint.date)} days ago; consider /lint.`);
		}

		const privacy = findLastAction(entries, "privacy-scan");
		if (privacy && daysSince(privacy.date) > REMINDER_THRESHOLDS.privacyScanDays) {
			reminders.push(`Last privacy scan was ${daysSince(privacy.date)} days ago; consider /privacy-scan.`);
		}

		const retention = findLastAction(entries, "retention-pass");
		if (retention && daysSince(retention.date) > REMINDER_THRESHOLDS.retentionPassDays) {
			reminders.push(`Last retention pass was ${daysSince(retention.date)} days ago; consider /retention-pass.`);
		}
	} catch {
		// Ignore reminder parsing failures.
	}

	return reminders;
}

export default function (pi: ExtensionAPI) {
	const modifiedPaths = new Set<string>();
	let sessionEndedExplicitly = false;
	let isTransitioning = false;

	pi.on("session_before_switch", async () => {
		isTransitioning = true;
		return undefined;
	});

	pi.on("session_before_fork", async () => {
		isTransitioning = true;
		return undefined;
	});

	pi.on("session_start", async (event, ctx) => {
		modifiedPaths.clear();
		sessionEndedExplicitly = false;
		isTransitioning = false;

		if (!ctx.hasUI) return;
		if (event.reason === "reload") return;

		const reminders = buildStartupReminders();
		if (reminders.length === 0) return;

		ctx.ui.notify(`Session reminders:\n- ${reminders.join("\n- ")}`, "info");
	});

	pi.on("input", async (event) => {
		const normalized = event.text.trim().toLowerCase();
		if (["/session-end", "session-end", "/crystallize", "crystallize"].some((prefix) => normalized.startsWith(prefix))) {
			sessionEndedExplicitly = true;
		}
		return { action: "continue" };
	});

	pi.on("tool_result", async (event) => {
		if (event.isError) return undefined;
		if ((event.toolName !== "write" && event.toolName !== "edit") || typeof event.input.path !== "string") return undefined;

		const relativePath = toRepoRelative(event.input.path);
		if (isWikiPath(relativePath) || isOutputsPath(relativePath) || relativePath.startsWith(".pi/") || relativePath === "AGENTS.md" || relativePath === "README.md") {
			modifiedPaths.add(relativePath);
		}
		return undefined;
	});

	pi.on("session_shutdown", async (_event, ctx) => {
		if (!ctx.hasUI) return;
		if (isTransitioning) return;
		if (sessionEndedExplicitly) return;
		if (modifiedPaths.size < REMINDER_THRESHOLDS.sessionEndChangedFiles) return;

		ctx.ui.notify(
			`You changed ${modifiedPaths.size} files this session. Consider /session-end to distill reusable lessons before quitting.`,
			"info",
		);
	});
}
