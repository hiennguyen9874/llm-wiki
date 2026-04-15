import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

// Project-local pi extensions are auto-discovered from .pi/extensions/*.ts.
// This no-op file keeps the directory visible in editors without changing behavior.
export default function (_pi: ExtensionAPI) {}
