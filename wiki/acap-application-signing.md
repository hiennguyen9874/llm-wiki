---
type: Concept
title: "ACAP application signing: service portal and signing service"
description: "How Axis signs ACAP applications: TIP partners through the ACAP Service Portal and non-TIP developers through the ACAP Signing Service, the manifest values each requires, SHA-512/RSA verification on device, and the AXIS OS install policy that ends unsigned apps at 13."
tags: [edge-ai, axis, acap, signing, security, distribution]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:21:35Z }
stale_after: 2027-04-30
sources:
  - id: acap-app-signing
    resource: ../raw/acap/how-to-guides/service-portal/acap-application-signing/index.md
    scope: ../raw/acap/how-to-guides/service-portal/
    kind: docs
    revision: "ACAP version 12"
    title: "ACAP application signing | Axis developer documentation"
---

# ACAP application signing: service portal and signing service

Signing an ACAP application means Axis cryptographically signs the built `.eap` package, so a device can prove that the package is unmodified and that a known software provider produced it. The signing itself is **not** done with a developer-held key: the package is uploaded to an Axis service, signed with Axis's private key inside an HSM, and returned as a signed `.eap`.[^acap-app-signing] Which service applies depends on partnership status — [TIP](https://www.axis.com/partner/technology-integration-partner-program) partners use the ACAP Service Portal, everyone else uses the ACAP Signing Service — and both paths require the application's `manifest.json` to be rebuilt with account-specific `vendor` (and, on schema v2, `vendorId`) values before upload. The signed package is compatible with older AXIS OS, but the install policy of the device decides whether an unsigned build is still accepted at all.[^acap-app-signing]

## Why sign

Signing gives three concrete guarantees, all stated from the end user's point of view: the application was not tampered with during distribution, its software provider is identified, and the user can trust that the installed application is genuine.[^acap-app-signing]

The mechanism behind that guarantee is asymmetric: Axis holds the private key, the device ships with the public key, and the check happens at installation. A developer therefore cannot self-sign an application for a device — signing is a service interaction, not a build flag.[^acap-app-signing]

## Two signing paths

| | ACAP Service Portal | ACAP Signing Service |
| --- | --- | --- |
| Audience | Members of the Axis Technology Integration Partner (TIP) program | Non-TIP partners |
| Sign-in | `axis.com` account | `axis.com` account |
| Manifest schema | v1 and v2 (`appId` and `vendor` for both, `vendorId` for v2) | v2.x only |
| Also manages | Application registration, licensing, device compatibility | Nothing; no package or history is stored |
| Where values come from | Application details page, "Pre-requisite information to sign" | Welcome page, account-specific `manifest.json` example |

The schema restriction is the one hard gate: an application built on manifest schema v1.x cannot be signed through the ACAP Signing Service and must be upgraded to v2 first. The portal path has no such restriction, but it requires a *registered* application in the portal.[^acap-app-signing]

## Sign as a TIP partner

Prerequisites named by the guide are a registered application in the portal and an active `axis.com` account. The procedure is: open the portal and log in, locate the application with **Filter items by name or description** (clicking **REGISTER** if it is not registered yet), read the required values from the manifest examples on the application details page, rebuild the application with those values, then **SIGN PACKAGE** → upload the `.eap` → **SIGN**. On success a confirmation appears and the signed `.eap` is downloaded automatically.[^acap-app-signing]

The values to carry into `manifest.json` depend on the schema version:[^acap-app-signing]

| Value | Manifest schema v1 | Manifest schema v2 |
| --- | --- | --- |
| `appId` | Available | Available |
| `vendor` | Available | Available |
| `vendorId` | — | Available |

`vendor` and `vendorId` are **case-sensitive** and must match the portal values exactly, otherwise validation fails. The manifest must also satisfy the [manifest schema](https://developer.axis.com/acap/reference/manifest-schemas/general-info/) before upload, so the rebuild is a real rebuild, not just an edit of the packaged file.[^acap-app-signing]

## The ACAP Service Portal beyond signing

The portal is the partner-facing management surface for an application's commercial and compatibility metadata, and signing is only one of its functions. It lets a TIP partner:[^acap-app-signing]

- Register and manage applications.
- Retrieve application information — `appId`, `vendor`, `vendorId` — needed for signing.
- Enable and configure the licensing service, including trial and free licenses for users.
- Manage licenses end to end: generate codes, track and modify license keys.
- Declare and restrict application compatibility with Axis devices based on verified support.
- Sign applications to establish authenticity and prevent tampering.

Access is organizational rather than per-user opt-in: every colleague in the TIP program has portal access by default, the **My Colleagues** tool shows who does, and users are added or removed by contacting [partner-services@axis.com](mailto:partner-services@axis.com).[^acap-app-signing]

## Sign as a non-TIP partner

The ACAP Signing Service is a narrower, stateless tool: it signs a `.eap` and returns it, and explicitly does **not** store uploaded packages or signing history. The procedure mirrors the portal's, with two extra gates — accepting the signing terms (which reappear on every visit) and, if prompted, letting the browser access the local network so the account-specific manifest information can load.[^acap-app-signing]

After logging in with an `axis.com` account and accepting the terms, the developer copies the unique `vendor` and `vendorId` from the provided `manifest.json` example, rebuilds the application with a schema-compliant manifest, then uses **CHOOSE YOUR EAP FILE TO SIGN** and **SIGN THE ACAP**. As with the portal, the signed package downloads automatically and the `vendor`/`vendorId` values are case-sensitive.[^acap-app-signing]

## How the device verifies a signature

Applications are signed with **SHA-512** and a **4096-bit RSA** private key kept in a **Thales Luna Network HSM 7** in the Axis datacenter. Axis devices ship preloaded with the matching 4096-bit RSA public key on the Linux filesystem and validate the signature before installation. From **AXIS OS 9.20** the check runs at install time; unsigned applications are still supported, and the format is fully backward compatible — a signed application installs on a device older than 9.20, which simply does not verify it.[^acap-app-signing]

## Install policy over AXIS OS versions

The signature check and the *policy* that requires a signature evolved separately. Axis added a VAPIX interface in **AXIS OS 11.2** to make a device accept only signed applications, then flipped the default in **AXIS OS 12.0** so only signed applications install unless the setting is changed.[^acap-app-signing]

| AXIS OS | Default | Can it be changed? |
| --- | --- | --- |
| 9.20 – 11.1 | Signed and unsigned both allowed | No |
| 11.2 – 11.11 | Signed and unsigned both allowed | Yes, via VAPIX to allow signed only |
| 12.0 – 12.11 | Only signed allowed | Yes, via VAPIX or the **Allow unsigned apps** toggle in the web interface |

Axis recommends allowing unsigned applications **during development** and warns that AXIS OS 13 removes the option to allow them entirely. This is the same enforcement recorded in [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md), which adds the manifest-side consequence: a production signing path becomes a prerequisite for shipping on 13.x.[^acap-app-signing]

## Known display and upgrade caveat

In the AXIS OS 12.11 web interface, some genuinely signed applications can still show the **unsigned** badge. The cause is historical: signature status was not persisted for applications originally installed on **AXIS OS 12.7 or earlier**, so from 12.11 the status is unknown rather than negative, and functionality is unaffected. The related upgrade rule is a hard one: applications installed before **AXIS OS 12.8** must be reinstalled on 12.8 or later *before* upgrading to AXIS OS 13.[^acap-app-signing]

## Coverage and limits

- **Entry point and scope:** `raw/acap/how-to-guides/service-portal/acap-application-signing/index.md`, one 1,371-word page (ACAP version 12) under `raw/acap/how-to-guides/service-portal/`. The folder contains no other pages, images, or attachments.
- **Inspected:** the whole page — rationale, both signing procedures, portal and service capability lists, verification mechanism, the AXIS OS history table, and the planned AXIS OS 13 change.
- **Not read:** linked material outside `raw/` — the TIP program page, the manifest schema general information, the VAPIX Application API, the AXIS OS release notes, and the Axis For Developers article on root ACAP signing. Claims that depend on them are reported only as this page states them.
- **No execution:** neither signing path was exercised, no portal or signing-service session was opened, and no signed `.eap` was installed. All procedural and cryptographic details are therefore **Reported**, not **Reproduced**. Account-specific values (`appId`, `vendor`, `vendorId`) are account data and are deliberately not recorded here.
- **Source inconsistency:** the non-TIP step that warns about case-sensitive values refers to values "provided by ACAP Service Portal", although the step before it says the values come from the ACAP Signing Service welcome page. The requirement — exact match, case-sensitive — is unambiguous; only the service name is inconsistent.
- **Capture noise:** the note about the 12.11 unsigned badge is captured with a malformed callout header (`> [!-secondary] -secondary`), and the manifest link text for v1.x leads to the v2 section anchor. Neither changes the technical content.

## Evidence class

All substantive claims are **Reported** from Axis's official ACAP 12 documentation, read on 2026-10-27. The statement that signing is a service interaction rather than a local build step, and the reading of the history table as two independent tracks (verification from 9.20, enforced default from 12.0), are **Synthesis** from the cited sections.

## Relationships

- **Constrained by** [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md): AXIS OS 13 removes the option to allow unsigned applications, which makes this signing path mandatory for anything shipped to 13.x.
- **Depends on** [Migrating ACAP applications from package.conf to manifest.json](acap-package-conf-to-manifest-migration.md) and [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): schema v2.x is required by the ACAP Signing Service and by `vendorId`, so the legacy migration and the v2 upgrade are preconditions for non-TIP signing.
- **Applied in** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md) and [Build, install, and control ACAP applications](acap-build-install-control.md): both install flows rely on either a signed package or the **Allow unsigned apps** setting described here.
- **Uses** [Phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md): the device's AXIS OS version decides whether the signature is verified and whether unsigned packages are accepted.
- **Related to** the manifest and partner metadata: `appId`, `vendor`, and `vendorId` are owned by the portal and must match the built manifest exactly, so signing validates metadata that is otherwise maintained outside the repository.

[^acap-app-signing]: Official documentation: [ACAP application signing — Axis developer documentation](../raw/acap/how-to-guides/service-portal/acap-application-signing/index.md), whole page: §Why sign your application?, §Sign an ACAP application as a TIP partner (§ACAP Service Portal), §Sign an ACAP application as a non-TIP partner (§ACAP Signing Service), §Verifying the signature, §History (§Planned changes).
