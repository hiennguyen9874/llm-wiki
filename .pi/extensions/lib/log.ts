export type LogEntry = {
	date: string;
	action: string;
	description: string;
};

export function parseLogActions(markdown: string): LogEntry[] {
	const entries: LogEntry[] = [];
	const regex = /^## \[(\d{4}-\d{2}-\d{2})\]\s+([^|]+)\|\s+(.+)$/gm;

	for (const match of markdown.matchAll(regex)) {
		entries.push({
			date: match[1],
			action: match[2].trim(),
			description: match[3].trim(),
		});
	}

	return entries;
}

export function findLastAction(entries: LogEntry[], action: string): LogEntry | null {
	const matching = entries.filter((entry) => entry.action === action);
	if (matching.length === 0) return null;
	matching.sort((a, b) => a.date.localeCompare(b.date));
	return matching.at(-1) ?? null;
}

export function daysSince(dateString: string, now = new Date()): number {
	const target = new Date(`${dateString}T00:00:00`);
	const diffMs = now.getTime() - target.getTime();
	return Math.floor(diffMs / (1000 * 60 * 60 * 24));
}
