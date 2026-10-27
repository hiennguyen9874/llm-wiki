---
type: Concept
title: "Deploying an ACAP application to many devices: upload.cgi and control.cgi"
description: "Four ways Axis documents for installing and starting an ACAP application on tens or thousands of devices — AXIS Device Manager, PowerShell, Bash and any language — built on the VAPIX upload.cgi and control.cgi endpoints, with the rules, the app-name lookup and the inconsistencies in the sample scripts."
tags: [edge-ai, axis, acap, deployment, vapix, fleet]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T15:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-docs-repo
    resource: ../raw/acap-documentation/README.md
    scope: ../raw/acap-documentation/
    kind: code
    revision: "12.2-17-g4aa04f1 (4aa04f185618e66f493453bcd62da1788c3059e4, 2025-02-06)"
    title: "ACAP documentation (archived repository)"
  - id: acap-docs-faq-deployment
    resource: ../raw/acap-documentation/docs/faq/deployment.md
    scope: ../raw/acap-documentation/docs/faq/deployment.md
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "FAQ: Deployment"
---

# Deploying an ACAP application to many devices: upload.cgi and control.cgi

Installing an ACAP application through the device web page does not scale to ten or a thousand devices, so the FAQ offers four routes: the AXIS Device Manager wizard, a PowerShell script, a Bash/curl script, or custom code against two VAPIX endpoints. All scripted routes do the same two calls per device: `POST /axis-cgi/applications/upload.cgi` with the `.eap` file, then `GET`/`POST /axis-cgi/applications/control.cgi?package=<appName>&action=start`.[^acap-docs-faq-deployment] The repository is an archived snapshot ([ACAP documentation repository](acap-documentation-repository.md)).[^acap-docs-repo]

## Routes

| Route | Requirements | Mechanism |
| --- | --- | --- |
| AXIS Device Manager | Windows application | Select devices → right-click *Install Camera Application…* → choose the app → optionally install licences → *Finish*; a task shows progress and outcome |
| PowerShell (`deploy.ps1`) | PowerShell 7 or higher (check `$PSVersionTable`); Windows, macOS or Linux | Reads a CSV of `IP,username,password`; `Invoke-RestMethod` multipart upload then start |
| Bash (`deploy.sh`) | Bash and curl (WSL on Windows) | Same CSV; `curl --anyauth -u user:pass -F packfil=@app …/upload.cgi`, then `…/control.cgi?package=<name>&action=start` |
| Any language | HTTP client | Three rules below |

Rules for custom code:[^acap-docs-faq-deployment]

1. Axis devices use **digest access authentication** for all HTTP requests.
2. Upload (and update) goes through `upload.cgi`.
3. Start and stop go through `control.cgi`.

## Finding the application name

`control.cgi` needs the package name as defined in the manifest or `package.conf`. The page says there is "no good way to get hold of this other than to install the ACAP application on a device and view the URL of its logs": install through the web UI, open the *App log*, and read `appname=` in the log URL, for example `…/axis-cgi/admin/systemlog.cgi?appname=my_app` gives `my_app`.[^acap-docs-faq-deployment] **Synthesis:** the same name is the manifest `appName` field ([Manifest schema 1.x history](acap-manifest-schema-v1-history.md)), so it can be read from the source tree instead; the page does not say so.

## Defects and cautions

All **Observed** by static reading of the sample scripts, not run:

- **Field name mismatch**: the PowerShell script posts the file under form field `file`; the Bash script uses `packfil` for the same endpoint. Only one is likely to be what the device expects, and the page does not say which.
- The PowerShell script reads `$app` while the declared parameter is `$App`; it works because PowerShell is case-insensitive.
- Both use plain HTTP (`-AllowUnencryptedAuthentication` in PowerShell), so credentials and package cross the network unencrypted unless the device is already behind TLS. The CSV holds passwords in clear text; the examples use placeholders such as `pass1`.
- The page does not mention signing. Since AXIS OS 12.0 devices accept signed applications only by default, an unsigned `.eap` may be refused unless the device is configured otherwise ([ACAP application signing](acap-application-signing.md)). **Synthesis.**
- The 4.x-era install channels for one device (web UI, `eap-install.sh`, curl) are in [Build, install, and control ACAP applications](acap-build-install-control.md).

## Limits

The scripts were not executed against a device; the success output shown (`Install: OK`, `Start: OK`) is the page's own sample. Licence installation through the Service Portal and Device Manager licence handling are not detailed in this source. Evidence class: **Reported** for the procedures, **Observed** for the defects.

## Relationships

- **Uses** VAPIX `applications` endpoints; related local-access credentials are in [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).
- **Complements** [Build, install, and control ACAP applications](acap-build-install-control.md) by covering the many-device case.
- **Constrained by** [ACAP application signing](acap-application-signing.md).
- **Source map**: [ACAP documentation repository](acap-documentation-repository.md).

[^acap-docs-repo]: [README](../raw/acap-documentation/README.md) archive notice; the page redirects to `developer.axis.com/acap/faq/deployment`.
[^acap-docs-faq-deployment]: [deployment.md](../raw/acap-documentation/docs/faq/deployment.md) §Deploy ACAP application, §using AXIS Device Manager, §using PowerShell (script, CSV example, app-name steps), §using Bash (script), §using a programming language.
