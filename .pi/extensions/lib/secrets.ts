export type SecretHit = {
	kind: string;
	confidence: "high" | "medium";
	preview: string;
};

type SensitivePattern = {
	kind: string;
	confidence: SecretHit["confidence"];
	regex: RegExp;
};

const PATTERNS: SensitivePattern[] = [
	{
		kind: "private-key",
		confidence: "high",
		regex: /-----BEGIN [A-Z ]*PRIVATE KEY-----/g,
	},
	{
		kind: "anthropic-key",
		confidence: "high",
		regex: /\bsk-ant-[A-Za-z0-9_-]{10,}\b/g,
	},
	{
		kind: "openai-style-key",
		confidence: "high",
		regex: /\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{16,}\b/g,
	},
	{
		kind: "google-api-key",
		confidence: "high",
		regex: /\bAIza[0-9A-Za-z\-_]{20,}\b/g,
	},
	{
		kind: "github-token",
		confidence: "high",
		regex: /\bgh[pousr]_[A-Za-z0-9]{20,}\b/g,
	},
	{
		kind: "aws-access-key",
		confidence: "high",
		regex: /\bAKIA[0-9A-Z]{16}\b/g,
	},
	{
		kind: "credential-assignment",
		confidence: "medium",
		regex: /\b(?:api[_-]?key|token|secret|password)\b\s*[:=]\s*["']?[A-Za-z0-9_\-./+=]{12,}/gi,
	},
	{
		kind: "email-address",
		confidence: "medium",
		regex: /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi,
	},
	{
		kind: "phone-number",
		confidence: "medium",
		regex: /\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b/g,
	},
];

function maskPreview(value: string): string {
	const compact = value.replace(/\s+/g, " ").trim();
	if (compact.startsWith("-----BEGIN")) return "-----BEGIN … PRIVATE KEY-----";
	if (compact.length <= 8) return compact;
	return `${compact.slice(0, 4)}…${compact.slice(-4)}`;
}

export function scanForSensitivePatterns(content: string): SecretHit[] {
	const hits: SecretHit[] = [];
	const seen = new Set<string>();

	for (const pattern of PATTERNS) {
		for (const match of content.matchAll(pattern.regex)) {
			const value = match[0];
			const preview = maskPreview(value);
			const key = `${pattern.kind}:${preview}`;
			if (seen.has(key)) continue;
			seen.add(key);
			hits.push({ kind: pattern.kind, confidence: pattern.confidence, preview });
			if (hits.length >= 10) return hits;
		}
	}

	return hits;
}
