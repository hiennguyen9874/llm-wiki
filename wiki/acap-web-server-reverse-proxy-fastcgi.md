---
type: Concept
title: "Exposing an HTTP API from an ACAP application: reverse proxy and FastCGI"
description: "Two ways for an ACAP application to serve web pages and HTTP APIs on an Axis device — Apache reverse proxy to an in-app web server, or FastCGI on the device's own Apache — with their manifest keys, URL schemes, authentication models and limits."
tags: [edge-ai, axis, acap, web-server, networking]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T13:10:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-web-server-docs
    resource: ../raw/acap/how-to-guides/web-server-via-reverse-proxy/index.md
    scope: ../raw/acap/how-to-guides/web-server-via-reverse-proxy/
    kind: docs
    revision: "ACAP version 12"
    title: "Web server | Axis developer documentation"
  - id: acap-web-server-examples
    resource: ../raw/acap-native-sdk-examples/web-server/README.md
    scope: ../raw/acap-native-sdk-examples/web-server/
    kind: code
    revision: "acap-native-sdk-examples 12.11.0-7-g3025a4e"
    title: "Web server examples — ACAP Native SDK examples"
---

# Exposing an HTTP API from an ACAP application: reverse proxy and FastCGI

An ACAP application that needs to answer HTTP requests has two vendor-documented routes, and they differ in who terminates the connection. With a **reverse proxy**, the Apache server in AXIS OS exposes the application's API under `/local/<appName>/<apiPath>` and forwards requests to a small web server that the application runs itself on a local port. With **FastCGI**, the application has no server of its own: it plugs into the Apache server already present on the device, so its endpoint sits on the same port as VAPIX and shares VAPIX authentication and user pool. The vendor page frames the choice as capability trade-off, not as a migration.[^acap-web-server-docs]

## Comparison

| | Reverse proxy | FastCGI |
| --- | --- | --- |
| Who serves HTTP | Application's own server (CivetWeb in the example), reachable on a fixed local port | Apache in AXIS OS; application only handles request/response |
| Manifest key | `acapPackageConf.configuration.reverseProxy` | `acapPackageConf.configuration.httpConfig` |
| Public URL | `http://<AXIS_DEVICE_IP>/local/<appName>/<apiPath>` | `http://<AXIS_DEVICE_IP>/local/<appName>/<name>`, e.g. `/local/fastcgi_example/example.cgi` |
| Port | Application port, often non-standard | Same port as VAPIX |
| Authentication | `access` policy per proxy entry; no VAPIX user pool | VAPIX authentication and user pool |
| Extra dependency | Bundled web server (or any server of choice) | FastCGI API from the SDK, plus a URI parser in the example |
| Best fit | Reusing existing server-side code and routing | Tight integration, serving settings pages or a small API |

Both routes cover the CGI use cases of the legacy `axHttp` API from ACAP SDK 3, which is why neither is a new capability but a new packaging of an old one.[^acap-web-server-docs] **Synthesis:** the deciding factor is usually authentication reuse and port hygiene, since a proxy entry under `/local/` is still authenticated by Apache while a directly exposed application port is not.

## Reverse proxy configuration

The manifest needs one `reverseProxy` entry per exposed path. The vendor example:[^acap-web-server-docs]

```json
"configuration": {
  "reverseProxy": [
    {
      "apiPath": "my_web_server",
      "target": "http://localhost:2001",
      "access": "admin"
    }
  ]
}
```

- `apiPath` becomes the URL segment after `/local/<appName>/`.
- `target` is the local URL the application's server listens on.
- `access` is the access policy for calling it (`admin` in both sources).

The example application adds `"settingPage": "my_web_server"` next to `reverseProxy`, which is what puts an **Open** button on the device GUI pointing at `/local/<appName>/<settingPage>`; the field is optional and independent of the proxy itself.[^acap-web-server-examples] The vendor page shows manifest `schemaVersion` 1.8.0 while the example at SDK 12.11.0 uses 2.2.0 with the same `reverseProxy` field shape and only a trailing slash added to `target` — **Observed** difference, with no claim that runtime behaviour differs.[^acap-web-server-docs][^acap-web-server-examples]

Manifest-based reverse proxy arrived in manifest **1.5.0**. Before that, the proxy had to be configured from the `postinstall` script, and the manifest method is stricter about URLs to avoid the name clashes that the script mechanism allowed — so upgrading an old application changes its public URLs to the `/local/<appName>/<apiPath>` scheme.[^acap-web-server-examples]

### Port and content constraints

- **Fixed port.** The CivetWeb example listens on `2001`. That port can already be taken by an AXIS OS service or another application, so a real deployment checks Axis's list of commonly used network ports; changing it means editing both the C source and `manifest.json` before building.[^acap-web-server-examples]
- **Relative addresses only.** Apache reverse proxy cannot rewrite absolute addresses inside an HTML page (`/image.png`), so pages must reference content relatively (`image.png`, `../image.png`). The example sidesteps this by rooting every asset at its own proxy prefix, i.e. `/local/web_server_rev_proxy/my_web_server/style.css`, which is not an absolute path outside the proxied tree.[^acap-web-server-examples]
- **Direct exposure is the alternative.** The in-app server can be published by opening its port in the device network configuration, but the vendor names the costs: non-standard ports and no reuse of Apache's authentication, TLS and other features.[^acap-web-server-docs]

## FastCGI configuration

FastCGI is a supported ACAP API, and it is configured in `manifest.json` under `httpConfig`:[^acap-web-server-docs][^acap-web-server-examples]

```json
"configuration": {
  "httpConfig": [
    { "access": "viewer", "name": "example.cgi", "type": "fastCgi" }
  ]
}
```

- `type` is the CGI implementation, `transferCgi` or `fastCgi`.
- `name` is the CGI path relative to the application web root — any alphanumeric string.
- `access` is the call policy: `admin`, `viewer`, or `operator`.

Operationally the application does not bind a port. AXIS OS passes the socket path in the **`FCGI_SOCKET_NAME`** environment variable; the example reads it, initialises the library, opens that socket with `FCGX_OpenSocket`, and then loops on `FCGX_Accept_r`, writing the response through `FCGX_FPrintF`. The example also `chmod`s the socket and parses `REQUEST_URI` — query string included — with `uriparser` rather than by hand.[^acap-web-server-examples]

The consequences of sitting inside Apache are the reason the vendor prefers it: the API is exposed on the same port as VAPIX and its users are authenticated the same way, from the same user pool. Anything relying on that user identity therefore behaves like VAPIX itself, which is the opposite of the proxy case where `access` alone gates the path.[^acap-web-server-docs][^acap-web-server-examples]

## Build shape of the examples

Both examples build against the ACAP Native SDK 12.11.0 image and bundle what AXIS OS does not provide:[^acap-web-server-examples]

| Example | Bundled dependency | Notes |
| --- | --- | --- |
| `reverse-proxy-using-fixed-port` | CivetWeb v1.16, built as `libcivetweb.a` | Linked with `-lcivetweb`, plus `glib-2.0`/`gio-2.0` for the main loop and signal handling |
| `http-requests-using-fastcgi` | uriparser 0.9.8, cross-compiled per architecture | `fcgi` comes from the SDK; uriparser is copied into `lib/` and found through an `$ORIGIN/lib` RPATH |

The uriparser cross-compilation follows the general third-party pattern recorded in [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md).

## Coverage and limits

- Entry point: `raw/acap/how-to-guides/web-server-via-reverse-proxy/index.md` (432 words, ACAP version 12). The whole page was read; the folder holds no other files.
- Supporting package: `raw/acap-native-sdk-examples/web-server/` at submodule revision `12.11.0-7-g3025a4e`, inside the pre-existing scope `raw/acap-native-sdk-examples/`. Read: both example READMEs (`README.md`, `reverse-proxy-using-fixed-port/README.md`, `http-requests-using-fastcgi/README.md`), both `app/manifest.json`, both `app/Makefile`, both `Dockerfile`, `web_server_rev_proxy.c`, `fastcgi_example.c`, and the example `html/` assets.
- Excluded: `http-requests-using-fastcgi/assets/fcgi.svg` is a diagrams.net scheme that only restates the README flow; both `LICENSE` files are Apache-2.0 boilerplate; `html/axis_logo.svg` and `style.css` are decorative.
- Not executed: no image was built, no `.eap` installed, and no device was contacted. Build commands, the FastCGI socket handshake, and the proxy routing are **Reported** by the sources or **Observed** by reading code — never **Reproduced**.
- The vendor page delegates to external destinations that are not in `raw/`: the Apache `mod_proxy` how-to, both example directories and their READMEs on GitHub, the FastCGI API reference, and uriparser. Only the local copies above could be verified.

## Evidence class

Manifest fields, URL schemes, access policies, the FastCGI port/user-pool argument, the `axHttp` equivalence, the pre-1.5.0 `postinstall` mechanism, and the absolute-address limitation are **Reported** from Axis documentation and example READMEs. The constants `2001`, `url prefix`, the `FCGI_SOCKET_NAME` handshake, `chmod`, `uriparser` usage, and the bundled library versions are **Observed** by static inspection of the local example package. The pre-1.5.0 mechanism and the schema-version difference are notes reconciled across the two sources, not verified on a device.

## Relationships

- **Alternative to** [VAPIX access from ACAP applications](acap-vapix-service-account-access.md): that concept is an application *calling* VAPIX; FastCGI is the mirror image, an application *extending* the VAPIX web surface with its own endpoint on the same port and user pool.
- **Uses** [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md): CivetWeb and uriparser are cross-compiled and bundled with the application.
- **Follows** [Build, install, and control ACAP applications](acap-build-install-control.md): the manifest change takes effect at install, and the examples use the Docker build plus `acap-build` path.
- **Constrained by** [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): `configuration.reverseProxy` and `httpConfig` travel with the manifest version; both examples already use schema 2.2.0.
- **Relates to** [Migrating ACAP applications from package.conf to manifest.json](acap-package-conf-to-manifest-migration.md): `settingPage` and `httpConfig` map to `package.conf` fields, while reverse proxy moved from the post-install script to a manifest section.
- **Exemplified by** [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md): `web-server/reverse-proxy-using-fixed-port` and `web-server/http-requests-using-fastcgi`.

[^acap-web-server-docs]: Official documentation: [Web server — Axis developer documentation](../raw/acap/how-to-guides/web-server-via-reverse-proxy/index.md), ACAP version 12; whole page — intro paragraph, §Web server with reverse proxy (§Configure reverse proxy, §Reverse proxy example), §Web server with FastCGI (§FastCGI example).

[^acap-web-server-examples]: Example package: [Web server examples](../raw/acap-native-sdk-examples/web-server/README.md), revision `12.11.0-7-g3025a4e` — `web-server/README.md` (§Available examples, §Which one to use); `reverse-proxy-using-fixed-port/README.md` (§Serve HTTP requests through reverse proxy incl. port note, §Reverse proxy configuration in Apache server, §Limitations, §Expected output); `http-requests-using-fastcgi/README.md` (§How to integrate the device's Apache web server, §Manifest schema HTTP configuration, §The expected output); plus static inspection of `reverse-proxy-using-fixed-port/app/{manifest.json,Makefile,web_server_rev_proxy.c,html/*}` and `http-requests-using-fastcgi/app/{manifest.json,Makefile,fastcgi_example.c}` and both `Dockerfile`s.
