export const GOVERNANCE_PATH_LABELS = [
	"AGENTS.md",
	".pi/prompts/",
	".pi/skills/",
] as const;

export const RAW_CREATE_PREFIXES = [
	"raw/inbox/",
	"raw/captures/",
	"raw/web-clips/",
	"raw/articles/",
	"raw/books/",
	"raw/papers/",
	"raw/assets/",
] as const;

export const REMINDER_THRESHOLDS = {
	reviewDays: 7,
	lintDays: 30,
	privacyScanDays: 30,
	retentionPassDays: 30,
	sessionEndChangedFiles: 3,
} as const;

export const CAPTURE_WATCH_DIRS = ["raw/inbox", "raw/captures"] as const;
export const REMINDER_WATCH_DIRS = CAPTURE_WATCH_DIRS;

const DESTRUCTIVE_RULES: Array<{ reason: string; pattern: RegExp; requiresProtectedArea?: boolean }> = [
	{
		reason: "recursive delete",
		pattern: /\brm\s+(-[A-Za-z]*[rf][A-Za-z]*|--recursive|--force)\b/i,
	},
	{
		reason: "find delete",
		pattern: /\bfind\b[\s\S]*\s-delete\b/i,
	},
	{
		reason: "git clean",
		pattern: /\bgit\s+clean\b/i,
	},
	{
		reason: "move or rename in protected areas",
		pattern: /\bmv\b/i,
		requiresProtectedArea: true,
	},
	{
		reason: "bulk rename loop",
		pattern: /\bfor\b[\s\S]*\bmv\b/i,
	},
];

const PROTECTED_SEGMENT_PATTERNS = [
	/(^|[\s'"./])raw\//i,
	/(^|[\s'"./])wiki\//i,
	/(^|[\s'"./])outputs\//i,
	/(^|[\s'"./])\.pi\//i,
	/(^|[\s'"./])AGENTS\.md\b/i,
] as const;

export function isApprovedRawCreatePath(relativePath: string): boolean {
	return RAW_CREATE_PREFIXES.some((prefix) => relativePath === prefix.slice(0, -1) || relativePath.startsWith(prefix));
}

export function referencesProtectedArea(command: string): boolean {
	return PROTECTED_SEGMENT_PATTERNS.some((pattern) => pattern.test(command));
}

export function collectDangerousBashReasons(command: string): string[] {
	const reasons: string[] = [];
	const touchesProtectedArea = referencesProtectedArea(command);

	for (const rule of DESTRUCTIVE_RULES) {
		if (!rule.pattern.test(command)) continue;
		if (rule.requiresProtectedArea && !touchesProtectedArea) continue;
		reasons.push(rule.reason);
	}

	return Array.from(new Set(reasons));
}
