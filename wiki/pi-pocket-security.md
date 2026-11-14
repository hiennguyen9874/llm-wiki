---
type: Concept
title: Pi Pocket Security and Trust Boundaries
description: Pi Pocket's reported access, session, browser, extension, and container trust boundaries and their limitations.
tags: [pi-pocket, security, access-control]
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

**Reported threat model:** anyone who can steer a [Pi Pocket](pi-pocket-overview.md) session can cause commands to run with the server user's privileges, reaching that user's files, app settings, tokens and code. Invite only people trusted at the keyboard. A session-scoped invite limits app visibility, not what the agent can reach; worktrees, plan mode, and spend limits are not security sandboxes. Viewers are intended to read, react, and chat but not make Pi act. These are source claims, not an independent security audit.[^pi-pocket]

## Sign-in and access

The owner sign-in link is a secret. The security guide reports random tokens stored hashed and sent in host-only `HttpOnly` cookies; hostnames such as `localhost` and `127.0.0.1` require separate sign-ins. Invites expire and are one-time; owner invites confer the owner token and full control. Rotation revokes devices using that token and outstanding owner invites. Exposure depends on [access mode](pi-pocket-deployment.md); LAN HTTP does not supply transport encryption.[^pi-pocket]

## Boundaries that need special care

- **Browser:** the server-side browser can reach localhost, the local network and the internet. Steering users and Pi can use it without Lancet Guard checks; disable it if guests should not reach those networks. Its pages do not receive app cookies, according to the guide.[^pi-pocket]
- **Extensions:** enabled drop-ins run with owner rights; browser modules run within the app page. The gallery pins downloads and checks hashes, but the guide recommends reviewing code before enabling. A theme can misrepresent UI, including approvals.[^pi-pocket]
- **Linked sessions:** Agent Teams is off by default; hostile content can propagate between sessions. Fencing and model instructions are guidance, not a security boundary. Use a session budget, and understand that a request crossing the limit is stopped only afterward.[^pi-pocket]
- **Containers:** Compose is documented as root by default, and Chromium runs with `--no-sandbox`; mounted folders and provider keys are available to commands executed in the container. Mount only trusted projects and avoid exposing the port to the public internet without a tunnel.[^pi-pocket]
- **Public artifacts:** a published artifact link's token is its access control; the sandboxed page can reach the network, so treat the link as a secret.[^pi-pocket]

## Evidence and limits

These claims are **Reported** by `SECURITY.md` and the Docker guide. No penetration test, runtime check or full code review was performed. This draft inherits the [partial coverage and screening limits](pi-pocket-overview.md#evidence-and-coverage).[^pi-pocket]

[^pi-pocket]: Pi Pocket revision `5d009fa4d1e2b69db54f05e04f750a6f2e591bb1`: `SECURITY.md` §What Pi Pocket protects, and what it does not; `README.md` §Remote access; `docs/docker.md` §§Permissions, Security.
