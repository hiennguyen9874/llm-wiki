import * as fs from "node:fs";

import { resolveInRepo, toRepoRelative } from "./paths";

export const MAINTENANCE_TASKS = ["review", "lint", "retention-pass", "privacy-scan"] as const;
export const TRIGGER_MODES = ["notify", "run"] as const;
export const MAINTENANCE_STATE_DIR = ".pi/state";
export const MAINTENANCE_QUEUE_PATH = `${MAINTENANCE_STATE_DIR}/maintenance-triggers.json`;

export type MaintenanceTask = (typeof MAINTENANCE_TASKS)[number];
export type TriggerMode = (typeof TRIGGER_MODES)[number];

export type MaintenanceTrigger = {
	id: string;
	createdAt: string;
	task: MaintenanceTask;
	mode: TriggerMode;
	reason?: string;
	requestedBy: string;
};

type MaintenanceQueueFile = {
	version: 1;
	triggers: MaintenanceTrigger[];
};

const EMPTY_QUEUE: MaintenanceQueueFile = {
	version: 1,
	triggers: [],
};

function isRecord(value: unknown): value is Record<string, unknown> {
	return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function normalizeMaintenanceTask(value: string): MaintenanceTask | null {
	const normalized = value.trim().replace(/^\//, "").toLowerCase();
	return MAINTENANCE_TASKS.find((task) => task === normalized) ?? null;
}

export function normalizeTriggerMode(value?: string | null): TriggerMode | null {
	if (!value) return null;
	const normalized = value.trim().toLowerCase();
	return TRIGGER_MODES.find((mode) => mode === normalized) ?? null;
}

function normalizeReason(value: unknown): string | undefined {
	if (typeof value !== "string") return undefined;
	const trimmed = value.trim();
	return trimmed || undefined;
}

function isIsoDate(value: unknown): value is string {
	return typeof value === "string" && !Number.isNaN(Date.parse(value));
}

function sanitizeTrigger(value: unknown): MaintenanceTrigger | null {
	if (!isRecord(value)) return null;

	const task = typeof value.task === "string" ? normalizeMaintenanceTask(value.task) : null;
	const mode = typeof value.mode === "string" ? normalizeTriggerMode(value.mode) : null;
	const createdAt = isIsoDate(value.createdAt) ? value.createdAt : new Date().toISOString();
	const requestedBy = typeof value.requestedBy === "string" && value.requestedBy.trim() ? value.requestedBy.trim() : "unknown";
	const reason = normalizeReason(value.reason);

	if (!task || !mode) return null;

	return {
		id: typeof value.id === "string" && value.id.trim() ? value.id.trim() : `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
		createdAt,
		task,
		mode,
		reason,
		requestedBy,
	};
}

export function ensureMaintenanceState(): void {
	fs.mkdirSync(resolveInRepo(MAINTENANCE_STATE_DIR), { recursive: true });
	const queueFile = resolveInRepo(MAINTENANCE_QUEUE_PATH);
	if (!fs.existsSync(queueFile)) {
		fs.writeFileSync(queueFile, `${JSON.stringify(EMPTY_QUEUE, null, 2)}\n`, "utf-8");
	}
}

export function readMaintenanceQueue(): MaintenanceQueueFile {
	ensureMaintenanceState();
	const queueFile = resolveInRepo(MAINTENANCE_QUEUE_PATH);

	try {
		const raw = fs.readFileSync(queueFile, "utf-8").trim();
		if (!raw) return { ...EMPTY_QUEUE, triggers: [] };

		const parsed = JSON.parse(raw);
		if (!isRecord(parsed) || !Array.isArray(parsed.triggers)) {
			return { ...EMPTY_QUEUE, triggers: [] };
		}

		return {
			version: 1,
			triggers: parsed.triggers.map((trigger) => sanitizeTrigger(trigger)).filter((trigger): trigger is MaintenanceTrigger => Boolean(trigger)),
		};
	} catch {
		return { ...EMPTY_QUEUE, triggers: [] };
	}
}

export function writeMaintenanceQueue(queue: MaintenanceQueueFile): void {
	ensureMaintenanceState();
	fs.writeFileSync(resolveInRepo(MAINTENANCE_QUEUE_PATH), `${JSON.stringify(queue, null, 2)}\n`, "utf-8");
}

export function enqueueMaintenanceTrigger(input: {
	task: MaintenanceTask;
	mode?: TriggerMode;
	reason?: string;
	requestedBy?: string;
	createdAt?: string;
	id?: string;
}): MaintenanceTrigger {
	const queue = readMaintenanceQueue();
	const trigger: MaintenanceTrigger = {
		id: input.id?.trim() || `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
		createdAt: input.createdAt && isIsoDate(input.createdAt) ? input.createdAt : new Date().toISOString(),
		task: input.task,
		mode: input.mode ?? "notify",
		reason: normalizeReason(input.reason),
		requestedBy: input.requestedBy?.trim() || "user",
	};

	queue.triggers.push(trigger);
	writeMaintenanceQueue(queue);
	return trigger;
}

export function replaceMaintenanceQueue(triggers: MaintenanceTrigger[]): void {
	writeMaintenanceQueue({ version: 1, triggers });
}

export function getMaintenanceQueueFilePath(): string {
	ensureMaintenanceState();
	return resolveInRepo(MAINTENANCE_QUEUE_PATH);
}

export function getMaintenanceQueueDisplayPath(): string {
	return toRepoRelative(getMaintenanceQueueFilePath());
}

export function summarizeTriggers(triggers: MaintenanceTrigger[]): string[] {
	return triggers.map((trigger) => {
		const reason = trigger.reason ? ` — ${trigger.reason}` : "";
		return `/${trigger.task} [${trigger.mode}]${reason}`;
	});
}
