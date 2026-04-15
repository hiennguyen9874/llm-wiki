import * as fs from "node:fs";

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

import {
	enqueueMaintenanceTrigger,
	ensureMaintenanceState,
	getMaintenanceQueueDisplayPath,
	getMaintenanceQueueFilePath,
	MAINTENANCE_STATE_DIR,
	normalizeMaintenanceTask,
	normalizeTriggerMode,
	readMaintenanceQueue,
	replaceMaintenanceQueue,
	summarizeTriggers,
	type MaintenanceTask,
	type MaintenanceTrigger,
	type TriggerMode,
} from "./lib/maintenance";
import { resolveInRepo } from "./lib/paths";

const RESCAN_DEBOUNCE_MS = 500;

type WatchState = {
	watcher: fs.FSWatcher | null;
	pendingTimer: ReturnType<typeof setTimeout> | null;
	processing: boolean;
	needsRescan: boolean;
};

type TriggerArgs = {
	task: MaintenanceTask;
	mode: TriggerMode;
	reason?: string;
};

function notify(ctx: any, message: string, level: "info" | "success" | "warning" | "error"): void {
	if (!ctx?.hasUI) return;
	ctx.ui.notify(message, level);
}

function cleanup(state: WatchState): void {
	if (state.pendingTimer) {
		clearTimeout(state.pendingTimer);
		state.pendingTimer = null;
	}
	if (state.watcher) {
		try {
			state.watcher.close();
		} catch {
			// Ignore watcher cleanup failures.
		}
		state.watcher = null;
	}
	state.processing = false;
	state.needsRescan = false;
}

function parseTriggerArgs(args: string, defaultMode: TriggerMode): TriggerArgs | { error: string } {
	const parts = args.trim().split(/\s+/).filter(Boolean);
	if (parts.length === 0) {
		return { error: "Usage: /maintenance-trigger <review|lint|retention-pass|privacy-scan> [notify|run] [reason]" };
	}

	const task = normalizeMaintenanceTask(parts[0]);
	if (!task) {
		return { error: `Unknown maintenance task: ${parts[0]}` };
	}

	let mode = defaultMode;
	let reasonStart = 1;
	const maybeMode = normalizeTriggerMode(parts[1]);
	if (maybeMode) {
		mode = maybeMode;
		reasonStart = 2;
	}

	const reason = parts.slice(reasonStart).join(" ").trim() || undefined;
	return { task, mode, reason };
}

function formatNotificationLines(title: string, triggers: MaintenanceTrigger[]): string {
	return [title, ...summarizeTriggers(triggers).map((line) => `- ${line}`)].join("\n");
}

function dispatchRunTriggers(pi: ExtensionAPI, triggers: MaintenanceTrigger[], ctx: any): void {
	let sentImmediate = false;

	for (const trigger of triggers) {
		const command = `/${trigger.task}`;
		const shouldQueueFollowUp = sentImmediate || !ctx.isIdle();
		if (shouldQueueFollowUp) pi.sendUserMessage(command, { deliverAs: "followUp" });
		else pi.sendUserMessage(command);
		sentImmediate = true;
	}

	if (triggers.length > 0) {
		notify(ctx, formatNotificationLines("Scheduled maintenance queued:", triggers), "info");
	}
}

function dispatchNotifyTriggers(triggers: MaintenanceTrigger[], ctx: any): void {
	if (triggers.length === 0) return;
	notify(
		ctx,
		`${formatNotificationLines("Scheduled maintenance reminders:", triggers)}\nUse /maintenance-run <task> to run one immediately.`,
		"info",
	);
}

function refreshQueue(pi: ExtensionAPI, state: WatchState, ctx: any): void {
	if (state.processing) {
		state.needsRescan = true;
		return;
	}

	state.processing = true;
	try {
		const queue = readMaintenanceQueue();
		if (queue.triggers.length === 0) return;

		const runTriggers: MaintenanceTrigger[] = [];
		const notifyTriggers: MaintenanceTrigger[] = [];
		const remaining: MaintenanceTrigger[] = [];

		for (const trigger of queue.triggers) {
			if (trigger.mode === "run") runTriggers.push(trigger);
			else if (ctx.hasUI) notifyTriggers.push(trigger);
			else remaining.push(trigger);
		}

		replaceMaintenanceQueue(remaining);

		if (notifyTriggers.length > 0) dispatchNotifyTriggers(notifyTriggers, ctx);
		if (runTriggers.length > 0) dispatchRunTriggers(pi, runTriggers, ctx);
	} finally {
		state.processing = false;
		if (state.needsRescan) {
			state.needsRescan = false;
			scheduleRefresh(pi, state, ctx, 0);
		}
	}
}

function scheduleRefresh(pi: ExtensionAPI, state: WatchState, ctx: any, delay = RESCAN_DEBOUNCE_MS): void {
	if (state.pendingTimer) clearTimeout(state.pendingTimer);
	state.pendingTimer = setTimeout(() => {
		state.pendingTimer = null;
		refreshQueue(pi, state, ctx);
	}, delay);
}

function watchTriggerDirectory(pi: ExtensionAPI, state: WatchState, ctx: any): void {
	ensureMaintenanceState();
	const directory = resolveInRepo(MAINTENANCE_STATE_DIR);
	state.watcher = fs.watch(directory, (_eventType, filename) => {
		if (filename && filename !== "maintenance-triggers.json") return;
		scheduleRefresh(pi, state, ctx);
	});
}

export default function (pi: ExtensionAPI) {
	const state: WatchState = {
		watcher: null,
		pendingTimer: null,
		processing: false,
		needsRescan: false,
	};

	pi.registerCommand("maintenance-status", {
		description: "Show scheduled-maintenance trigger status and queue path",
		handler: async (_args, ctx) => {
			ensureMaintenanceState();
			const queue = readMaintenanceQueue();
			const summary = queue.triggers.length > 0 ? summarizeTriggers(queue.triggers).map((line) => `- ${line}`).join("\n") : "- none";
			notify(
				ctx,
				`Scheduled maintenance queue: ${getMaintenanceQueueDisplayPath()}\nPending triggers:\n${summary}\nWatcher active: ${state.watcher ? "yes" : "no"}`,
				"info",
			);
		},
	});

	pi.registerCommand("maintenance-trigger", {
		description: "Queue a scheduled maintenance trigger: /maintenance-trigger <task> [notify|run] [reason]",
		handler: async (args, ctx) => {
			const parsed = parseTriggerArgs(args, "notify");
			if ("error" in parsed) {
				notify(ctx, parsed.error, "warning");
				return;
			}

			const trigger = enqueueMaintenanceTrigger({
				task: parsed.task,
				mode: parsed.mode,
				reason: parsed.reason,
				requestedBy: "user-command",
			});

			notify(
				ctx,
				`Queued ${trigger.mode} trigger for /${trigger.task} in ${getMaintenanceQueueDisplayPath()}` +
					(trigger.reason ? ` (${trigger.reason})` : ""),
				"success",
			);
			scheduleRefresh(pi, state, ctx, 0);
		},
	});

	pi.registerCommand("maintenance-run", {
		description: "Opt-in immediate maintenance run: /maintenance-run <task> [reason]",
		handler: async (args, ctx) => {
			const parsed = parseTriggerArgs(args, "run");
			if ("error" in parsed) {
				notify(ctx, "Usage: /maintenance-run <review|lint|retention-pass|privacy-scan> [reason]", "warning");
				return;
			}

			enqueueMaintenanceTrigger({
				task: parsed.task,
				mode: "run",
				reason: parsed.reason,
				requestedBy: "user-command",
			});
			scheduleRefresh(pi, state, ctx, 0);
		},
	});

	pi.on("session_start", async (_event, ctx) => {
		cleanup(state);
		ensureMaintenanceState();
		try {
			watchTriggerDirectory(pi, state, ctx);
		} catch {
			notify(ctx, `Could not watch ${getMaintenanceQueueFilePath()}`, "warning");
		}

		scheduleRefresh(pi, state, ctx, 0);
	});

	pi.on("session_shutdown", async () => {
		cleanup(state);
	});
}
