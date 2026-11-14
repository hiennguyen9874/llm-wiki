---
type: Concept
title: Pi Pocket Deployment and Remote Access
description: Installation, networking, backup, upgrade, and container considerations for operating Pi Pocket.
tags: [pi-pocket, deployment, networking]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:42:58Z }
stale_after: 2027-02-14
sources:
  - id: pi-pocket
    resource: ../raw/pi-pocket/README.md
    scope: ../raw/pi-pocket/
    kind: code
    revision: 5d009fa4d1e2b69db54f05e04f750a6f2e591bb1
    title: Pi Pocket 0.28.2
---

[Pi Pocket](pi-pocket-overview.md) can reportedly run natively, in Docker or Podman, through Nix, or on Android with Termux. The project requires Node.js 22.19 or newer and recommends signing in to a Pi provider; native installation is `npm install -g pi-pocket` followed by `pi-pocket`. These instructions are **Reported**, not executed.[^pi-pocket]

## Access and operations

| Mode | Reported exposure |
| --- | --- |
| `local` | Loopback `127.0.0.1`; an independent tunnel may target port 8787. |
| `lan` | Local network, plain HTTP. |
| `cloudflare` | HTTPS quick tunnel; anyone with the link can reach it. |
| `tailscale` | Tailnet address, plain HTTP. |
| `tailscale-serve` | HTTPS at the tailnet name; needs Tailscale CLI, MagicDNS and HTTPS certificates, plus appropriate operator permission. |

The README says the owner sign-in link is a key and must remain private; `--rotate-token` replaces it and signs out devices using it. The default port is 8787 and data folder is `~/.pi-pocket`. **Observed:** `src/server/main.ts::parseArgs` defaults the server to loopback, port 8787 and a five-second keepalive, while allowing flags and environment variables to override them. Behind a reverse proxy, the README recommends setting server keepalive above the proxy's idle timeout or lowering the proxy timeout.[^pi-pocket]

**Reported:** stop the server and back up the complete data folder before upgrading: releases 0.21.0 and 0.28.0 introduce data changes incompatible with older versions. Only one server process may use a database. In containers, persistent bind mounts include the data folder, Pi credentials and workspace; a container's `local` mode binds its own loopback and is not reachable through the ordinary published port. The Docker guide recommends host-loopback publishing plus `lan` inside for single-host access, and notes Compose defaults to root with Chromium's sandbox disabled. See [security](pi-pocket-security.md) before exposing access or mounting sensitive folders.[^pi-pocket]

## Evidence and limits

Documentation and the initial server argument parser were inspected statically; commands, networking, backups and migration were not tested. This is a draft from a partial package review; uninspected implementation and deployment artifacts are identified in the [overview coverage ledger](pi-pocket-overview.md#evidence-and-coverage).[^pi-pocket]

[^pi-pocket]: Pi Pocket revision `5d009fa4d1e2b69db54f05e04f750a6f2e591bb1`: `README.md` §§Quick start, Other ways to run it, Remote access, Limitations; `src/server/main.ts::parseArgs`; `docs/architecture.md` §Durable truth and what memory keeps; `docs/docker.md` §§Folders from the host, Access and ports, Permissions, Security.
