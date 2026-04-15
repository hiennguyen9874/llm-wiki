#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TASKS = new Set(["review", "lint", "retention-pass", "privacy-scan"]);
const MODES = new Set(["notify", "run"]);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..", "..");
const stateDir = path.join(repoRoot, ".pi", "state");
const queueFile = path.join(stateDir, "maintenance-triggers.json");

function usage() {
	console.log(`Usage:\n  node .pi/scripts/trigger-maintenance.mjs <task> [--mode notify|run] [--reason text] [--requested-by source]\n\nTasks:\n  review\n  lint\n  retention-pass\n  privacy-scan\n\nExamples:\n  node .pi/scripts/trigger-maintenance.mjs review --reason weekly-cron\n  node .pi/scripts/trigger-maintenance.mjs lint --mode run --reason monthly-systemd`);
}

function ensureQueue() {
	fs.mkdirSync(stateDir, { recursive: true });
	if (!fs.existsSync(queueFile)) {
		fs.writeFileSync(queueFile, `${JSON.stringify({ version: 1, triggers: [] }, null, 2)}\n`, "utf8");
	}
}

function readQueue() {
	ensureQueue();
	try {
		const parsed = JSON.parse(fs.readFileSync(queueFile, "utf8"));
		if (!parsed || typeof parsed !== "object" || !Array.isArray(parsed.triggers)) {
			return { version: 1, triggers: [] };
		}
		return { version: 1, triggers: parsed.triggers };
	} catch {
		return { version: 1, triggers: [] };
	}
}

function writeQueue(queue) {
	ensureQueue();
	fs.writeFileSync(queueFile, `${JSON.stringify(queue, null, 2)}\n`, "utf8");
}

function parseArgs(argv) {
	if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
		usage();
		process.exit(argv.length === 0 ? 1 : 0);
	}

	const task = String(argv[0]).trim().replace(/^\//, "").toLowerCase();
	if (!TASKS.has(task)) {
		console.error(`Unknown task: ${argv[0]}`);
		usage();
		process.exit(1);
	}

	let mode = "notify";
	let reason = "";
	let requestedBy = "external-script";

	for (let index = 1; index < argv.length; index += 1) {
		const token = argv[index];
		if (token === "--mode") {
			const value = argv[index + 1];
			if (!value || !MODES.has(value)) {
				console.error(`Invalid mode: ${value ?? "(missing)"}`);
				process.exit(1);
			}
			mode = value;
			index += 1;
			continue;
		}
		if (token === "--reason") {
			reason = argv[index + 1] ?? "";
			index += 1;
			continue;
		}
		if (token === "--requested-by") {
			requestedBy = argv[index + 1] ?? requestedBy;
			index += 1;
			continue;
		}
		console.error(`Unknown argument: ${token}`);
		usage();
		process.exit(1);
	}

	return { task, mode, reason: reason.trim(), requestedBy: requestedBy.trim() || "external-script" };
}

const { task, mode, reason, requestedBy } = parseArgs(process.argv.slice(2));
const queue = readQueue();
queue.triggers.push({
	id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
	createdAt: new Date().toISOString(),
	task,
	mode,
	reason: reason || undefined,
	requestedBy,
});
writeQueue(queue);
console.log(`Queued ${mode} trigger for /${task} in ${path.relative(repoRoot, queueFile)}` + (reason ? ` (${reason})` : ""));
