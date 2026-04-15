import * as fs from "node:fs";

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

import { CAPTURE_WATCH_DIRS } from "./lib/policy";
import { normalizeSlashes, resolveInRepo, toRepoRelative } from "./lib/paths";

const RESCAN_DEBOUNCE_MS = 750;
const MAX_DISPLAYED_NEW_FILES = 4;

type WatchState = {
	watchers: Map<string, fs.FSWatcher>;
	knownFiles: Set<string>;
	pendingTimer: ReturnType<typeof setTimeout> | null;
};

function safeStat(path: string): fs.Stats | null {
	try {
		return fs.statSync(path);
	} catch {
		return null;
	}
}

function listFilesUnder(relativeDir: string): string[] {
	const root = resolveInRepo(relativeDir);
	const stat = safeStat(root);
	if (!stat?.isDirectory()) return [];

	const files: string[] = [];
	const stack = [root];

	while (stack.length > 0) {
		const current = stack.pop();
		if (!current) continue;

		let entries: fs.Dirent[] = [];
		try {
			entries = fs.readdirSync(current, { withFileTypes: true });
		} catch {
			continue;
		}

		for (const entry of entries) {
			if (entry.name.startsWith(".")) continue;
			const fullPath = `${current}/${entry.name}`;
			if (entry.isDirectory()) stack.push(fullPath);
			else if (entry.isFile()) files.push(toRepoRelative(fullPath));
		}
	}

	return files.sort();
}

function listDirectoriesUnder(relativeDir: string): string[] {
	const root = resolveInRepo(relativeDir);
	const stat = safeStat(root);
	if (!stat?.isDirectory()) return [];

	const directories: string[] = [normalizeSlashes(root)];
	const stack = [root];

	while (stack.length > 0) {
		const current = stack.pop();
		if (!current) continue;

		let entries: fs.Dirent[] = [];
		try {
			entries = fs.readdirSync(current, { withFileTypes: true });
		} catch {
			continue;
		}

		for (const entry of entries) {
			if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
			const fullPath = `${current}/${entry.name}`;
			directories.push(normalizeSlashes(fullPath));
			stack.push(fullPath);
		}
	}

	return directories;
}

function scanWatchedFiles(): Set<string> {
	const next = new Set<string>();
	for (const dir of CAPTURE_WATCH_DIRS) {
		for (const file of listFilesUnder(dir)) next.add(file);
	}
	return next;
}

function cleanup(state: WatchState) {
	if (state.pendingTimer) {
		clearTimeout(state.pendingTimer);
		state.pendingTimer = null;
	}

	for (const watcher of state.watchers.values()) {
		try {
			watcher.close();
		} catch {
			// Ignore watcher cleanup errors.
		}
	}
	state.watchers.clear();
}

function suggestCommand(paths: string[]): string {
	if (paths.length === 1) return `/ingest ${paths[0]}`;
	if (paths.every((file) => file.startsWith("raw/inbox/"))) return "/ingest-batch raw/inbox";
	if (paths.every((file) => file.startsWith("raw/captures/"))) return "/ingest-batch raw/captures";
	return "/ingest-batch raw/inbox";
}

function formatNotification(paths: string[]): string {
	const preview = paths.slice(0, MAX_DISPLAYED_NEW_FILES).map((item) => `- ${item}`).join("\n");
	const suffix = paths.length > MAX_DISPLAYED_NEW_FILES ? `\n- (+${paths.length - MAX_DISPLAYED_NEW_FILES} more)` : "";
	return `New capture files detected:\n${preview}${suffix}\nSuggested next step: ${suggestCommand(paths)}`;
}

function refreshWatchers(_pi: ExtensionAPI, state: WatchState, onFsEvent: () => void) {
	const desiredDirectories = new Set<string>();
	for (const dir of CAPTURE_WATCH_DIRS) {
		for (const directory of listDirectoriesUnder(dir)) desiredDirectories.add(directory);
	}

	for (const watched of [...state.watchers.keys()]) {
		if (desiredDirectories.has(watched)) continue;
		const watcher = state.watchers.get(watched);
		if (!watcher) continue;
		watcher.close();
		state.watchers.delete(watched);
	}

	for (const directory of desiredDirectories) {
		if (state.watchers.has(directory)) continue;
		try {
			const watcher = fs.watch(directory, () => onFsEvent());
			state.watchers.set(directory, watcher);
		} catch {
			// Ignore directories that cannot be watched.
		}
	}
}

export default function (pi: ExtensionAPI) {
	const state: WatchState = {
		watchers: new Map(),
		knownFiles: new Set(),
		pendingTimer: null,
	};

	function scheduleScan(ctx: { hasUI: boolean; ui: { notify: (message: string, level: "info" | "success" | "warning" | "error") => void } }) {
		if (state.pendingTimer) clearTimeout(state.pendingTimer);
		state.pendingTimer = setTimeout(() => {
			state.pendingTimer = null;
			refreshWatchers(pi, state, () => scheduleScan(ctx));

			const nextFiles = scanWatchedFiles();
			const newFiles = [...nextFiles].filter((file) => !state.knownFiles.has(file)).sort();
			state.knownFiles = nextFiles;

			if (newFiles.length === 0 || !ctx.hasUI) return;
			ctx.ui.notify(formatNotification(newFiles), "info");
		}, RESCAN_DEBOUNCE_MS);
	}

	pi.on("session_start", async (_event, ctx) => {
		cleanup(state);
		state.knownFiles = scanWatchedFiles();

		if (!ctx.hasUI) return;

		refreshWatchers(pi, state, () => scheduleScan(ctx));
	});

	pi.on("session_shutdown", async () => {
		cleanup(state);
	});
}
