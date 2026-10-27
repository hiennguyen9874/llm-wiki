---
type: Concept
title: "VAPIX access from ACAP applications: local service accounts"
description: "How an ACAP application obtains admin-level VAPIX service-account credentials over D-Bus and calls VAPIX on the local virtual host 127.0.0.12, with manifest requirements, proxy caveat, and device limits."
tags: [edge-ai, axis, acap, vapix, dbus, security]
status: stable
created: 2026-10-27
    generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-vapix-access
    resource: ../raw/acap/how-to-guides/VAPIX-access-for-ACAP-applications/index.md
    scope: ../raw/acap/how-to-guides/VAPIX-access-for-ACAP-applications/
    kind: docs
    revision: "ACAP version 12"
    title: "VAPIX access for ACAP applications | Axis developer documentation"
  - id: acap-vapix-example
    resource: ../raw/acap-native-sdk-examples/vapix/README.md
    scope: ../raw/acap-native-sdk-examples/vapix/
    kind: code
    revision: "acap-native-sdk-examples 12.11.0-7-g3025a4e"
    title: "ACAP application calling VAPIX APIs — example README"
---

# VAPIX access from ACAP applications: local service accounts

An ACAP application does not need a device user's password to call VAPIX. From AXIS OS 11.6 it can acquire a **VAPIX service account** at runtime over D-Bus: it asks `com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials` for credentials with `admin` access level, receives a generated username and a high-complexity random password, and then sends ordinary HTTP requests with basic authentication to the local virtual host `127.0.0.12`. Those credentials are valid only on that loopback host and are never written to a file, so the application must keep them in memory only and re-fetch them on every start. Two preconditions are easy to miss: the application must run as a **dynamic user** (the D-Bus service is not available to the general SDK user), and the method must be declared under `resources.dbus.requiredMethods` in `manifest.json`.[^acap-vapix-access]

## Why a service account instead of a device user

VAPIX calls are HTTP requests, and the device checks them with basic access authentication. Handing an application a named device user would mean storing a real user password, which is exactly what this feature avoids: every credential acquisition mints a fresh pair, the password is random, and the pair is scoped to the local virtual host only. The trade-off is lifetime — nothing is persisted, so credentials disappear when the device reboots and must be re-acquired by the application each time it starts.[^acap-vapix-access]

## Manifest requirements

Two manifest changes are required:[^acap-vapix-access]

| Change | Field | Reason |
| --- | --- | --- |
| Declare the D-Bus method | `resources.dbus.requiredMethods` | The application may only call D-Bus methods it declares |
| Remove the static user | no `acapPackageConf.setup.user` section | The D-Bus service requires a dynamically generated user |

The documented example manifest (ACAP 12, schema 1.3.1):[^acap-vapix-access]

```json
{
    "schemaVersion": "1.3.1",
    "acapPackageConf": {
        "setup": {
            "appName": "vapix_access",
            "vendor": "Axis Communications",
            "embeddedSdkVersion": "3.0",
            "runMode": "never",
            "version": "1.0.0"
        }
    },
    "resources": {
        "dbus": {
            "requiredMethods": ["com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials"]
        }
    }
}
```

This is the same grant described in [ACAP application user types and permissions](acap-application-user-permissions.md), which lists the VAPIX method among the documented D-Bus methods available to a dynamic user and notes that `dbus` resources are supported only for dynamic users. From manifest schema v2.x the allowed values in `resources.dbus` are also enforced by the schema itself, so a wrong method name can fail at build time rather than at install, as recorded in [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md).

## Acquiring credentials over D-Bus

The acquisition is a single method call on the system bus. The application passes a username of its choosing; the device creates the account and returns `username:password` as one string.[^acap-vapix-access]

### From C with GDBus

The documented steps use GDBus, the high-level D-Bus library:[^acap-vapix-access]

1. Open a connection to the system bus: `g_bus_get_sync(G_BUS_TYPE_SYSTEM, NULL, &error)`.
2. Call the method with the chosen username as a `(s)` variant:

```c
GVariant *username = g_variant_new("(s)", "testuser");
GVariant *result = g_dbus_connection_call_sync (connection,
                                                "com.axis.HTTPConf1",
                                                "/com/axis/HTTPConf1/VAPIXServiceAccounts1",
                                                "com.axis.HTTPConf1.VAPIXServiceAccounts1",
                                                "GetCredentials",
                                                username,
                                                NULL,
                                                G_DBUS_CALL_FLAGS_NONE,
                                                -1,
                                                NULL,
                                                &error);
```

The returned string is the credential pair; it is not a structured object, so the application splits it on the first `:`.

### From the command line over SSH

For a manual check, the same call works with `gdbus` on the device, provided the developer has an SSH account — an ACAP application user gets SSH through Developer Mode, as covered in [SSH và Developer Mode trên thiết bị Axis](axis-device-ssh-developer-mode.md):[^acap-vapix-access]

```bash
gdbus call \
        --system \
        --dest com.axis.HTTPConf1 \
        --object-path /com/axis/HTTPConf1/VAPIXServiceAccounts1 \
        --method com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials \
        "testuser"
```

The reply is a tuple holding one string of the form `id:password`. The documentation prints a sample reply with a plausible-looking credential; that value is a generated example, is device- and session-specific, and is deliberately not reproduced here.[^acap-vapix-access]

## Making the VAPIX call

With credentials in hand the application talks plain HTTP to `127.0.0.12`, where a local server checks the credentials with basic access authentication and forwards the request. The documented cURL settings:[^acap-vapix-access]

```c
curl_easy_setopt(curl, CURLOPT_URL, "http://127.0.0.12/axis-cgi/applications/list.cgi");
curl_easy_setopt(curl, CURLOPT_USERPWD, credentials);
curl_easy_setopt(curl, CURLOPT_HTTPAUTH, CURLAUTH_ANY);
curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_to_file);
curl_easy_setopt(curl, CURLOPT_WRITEDATA, &file);
```

The URL shape is fixed: `http://127.0.0.12/axis-cgi/<endpoint>`, where the endpoint is any VAPIX CGI. A manual check from the SSH shell uses the same pair:[^acap-vapix-access]

```bash
curl -s -u <id>:<pass> http://127.0.0.12/axis-cgi/applications/list.cgi
```

## Global device proxy interaction

If the device has a global proxy configured, `127.0.0.12` is reachable only when it is added to the proxy **`No proxy`** list. This is a hard failure mode rather than a degradation: the local virtual host is a special address, so a proxy that intercepts it breaks credential validation and every subsequent VAPIX call. The device-side proxy layer itself is described in [Proxy configuration for ACAP builds and runtime](acap-proxy-configuration.md).[^acap-vapix-access][^acap-vapix-example]

## Version history

The feature matured across three AXIS OS releases, per the example's README:[^acap-vapix-example]

| Release | Status |
| --- | --- |
| AXIS OS 11.6 | Feature introduced as Beta |
| AXIS OS 11.8 | D-Bus API format changed |
| AXIS OS 11.9 | General Availability |

Because the format changed in 11.8, code copied from a pre-11.8 example will not match the documented `GetCredentials` signature.

## Limitations

- A device holds at most **200** VAPIX service accounts.[^acap-vapix-access]
- **No accounts survive a reboot**; restarting the device removes every created credential, so the application must re-fetch on each start.[^acap-vapix-access]
- Credentials belong **in memory only** and must not be written to any file.[^acap-vapix-access]
- Only the specific D-Bus method calls introduced by this feature are officially supported; using other D-Bus methods is unsupported and may behave undefined.[^acap-vapix-access]
- The credentials carry `admin` access level, so the application effectively acts as an administrator on the device — the loopback-only scope is the containment mechanism, not a reduced privilege level.[^acap-vapix-access]

## Example application (observed)

The repository copy of `raw/acap-native-sdk-examples/vapix/` is available locally, so these points are **Observed** from static inspection rather than reported:[^acap-vapix-example]

| Artifact | Observation |
| --- | --- |
| `app/manifest.json` | `schemaVersion` 2.2.0, `compatibleOsVersions` max `13`, appName `vapix_example`, no `user` section, and `resources.dbus.requiredMethods` set to the VAPIX method |
| `app/vapix_example.c` | `retrieve_vapix_credentials()` opens the system bus, calls `GetCredentials` with a username, and `parse_credentials()` splits the reply on `:` with `sscanf` |
| `app/vapix_example.c` | `vapix_post()` builds `http://127.0.0.12/axis-cgi/<endpoint>`, sets `CURLOPT_USERPWD`, POSTs, and treats any non-200 response as fatal |
| `app/vapix_example.c` | The example calls the Basic device information VAPIX API and parses product and SoC fields from the JSON reply |
| `README.md` | The example recommends POST for all VAPIX calls, because POST covers the use cases GET would cover |

One divergence: the guide sets `CURLOPT_HTTPAUTH` to `CURLAUTH_ANY`, while the example sets it to `CURLAUTH_BASIC`. The device accepts basic authentication in both cases, so this is a documentation/implementation mismatch rather than a functional contradiction — but a reader following the prose will negotiate more methods than the example does.

## Source coverage

- Entry point: `raw/acap/how-to-guides/VAPIX-access-for-ACAP-applications/index.md`, one file, 675 words, site `developer.axis.com`, revision "ACAP version 12". No images or attachments in the folder. Every section was read: overview, example application, manifest modification, credential acquisition, VAPIX call, command-line test, limitations.
- Supporting package: `raw/acap-native-sdk-examples/vapix/` (README, `app/manifest.json`, `app/vapix_example.c`, `app/Makefile`, `app/LICENSE`, `Dockerfile`), inside the pre-existing scope `raw/acap-native-sdk-examples/` at submodule revision `12.11.0-7-g3025a4e`. The README, manifest, and C source were read; `Makefile`, `LICENSE`, and `Dockerfile` were listed but not analysed because they carry no VAPIX-specific knowledge.
- Excluded: the external `https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/vapix` link in the guide — the same example is present locally, so the local copy was used instead; the linked VAPIX API library and *Supported APIs* references, which stay outside `raw/`.
- Limits: the guide names no minimum AXIS OS version for the manifest fields and says nothing about what happens when the 200-account ceiling is reached (whether acquisition fails or evicts). Account cleanup on application uninstall is not documented. The example was not built or run.

## Evidence class

Procedure, manifest requirement, proxy caveat, version history, and limitations are **Reported** from official Axis documentation and the vendored example README. The manifest contents, the C call sequence, the `CURLAUTH_BASIC` divergence, and the example's POST usage are **Observed** by static inspection of the local example. Nothing is **Reproduced**: no application was built, no D-Bus call was issued, and no VAPIX request was made.

## Relationships

- **Depends on** [ACAP application user types and permissions](acap-application-user-permissions.md): the feature requires a dynamic user and a declared D-Bus method; that concept holds the full permission model.
- **Constrained by** [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): schema v2 restricts `resources.dbus` values and can reject an invalid method at build time.
- **Affected by** [Proxy configuration for ACAP builds and runtime](acap-proxy-configuration.md): a global device proxy must exempt `127.0.0.12` in `No proxy`, or VAPIX calls to the loopback host fail.
- **Depends on** [SSH và Developer Mode trên thiết bị Axis](axis-device-ssh-developer-mode.md): the manual `gdbus` test needs a shell on the device.
- **Exemplified by** [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md): the `vapix` example is the reference implementation of this flow.
- **Uses** the VAPIX CGI surface (`/axis-cgi/...`) as an alternative to writing a device-side API of its own.
- **Mirrored by** [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md): this concept is an application calling VAPIX, while a FastCGI endpoint extends the same Apache surface and shares the same user pool.
- **Follows** [Build, install, and control ACAP applications](acap-build-install-control.md): the manifest change takes effect when the package is installed and the app started.
- **Siblings** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md) and [PTZ control example](acap-example-ptz-control-ws-api.md), which uses the same D-Bus credential call with a WebSocket.

[^acap-vapix-access]: Official documentation: [VAPIX access for ACAP applications — Axis developer documentation](../raw/acap/how-to-guides/VAPIX-access-for-ACAP-applications/index.md), whole page, ACAP version 12: overview paragraph, §Example application (§Modify the manifest file, §Acquire credentials, §Make a VAPIX call), §Test from command-line, §Limitations. The sample credential in the `gdbus call` reply is omitted.

[^acap-vapix-example]: Example package: [ACAP application calling VAPIX APIs](../raw/acap-native-sdk-examples/vapix/README.md), §Application description (§Outline of example, §API to get VAPIX credentials incl. Versions, §VAPIX APIs, §Global proxy configuration), §Build the application, §Install and start the application, §Expected output; plus static inspection of `raw/acap-native-sdk-examples/vapix/app/manifest.json` and `raw/acap-native-sdk-examples/vapix/app/vapix_example.c::retrieve_vapix_credentials`, `::vapix_post`, `::parse_credentials`.
