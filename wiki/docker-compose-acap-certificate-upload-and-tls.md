---
type: Concept
title: "Docker Compose ACAP certificates and TLS: FastCGI upload endpoint, validation and defects"
description: "How the Docker Compose ACAP receives dockerd TLS certificates over HTTP: the three FastCGI endpoints, POST and DELETE handling, header/footer validation, dockerd TLS arguments, port 2376 versus 2375, and the multipart-parser and routing defects found in the code."
tags: [edge-ai, axis, acap, docker, tls, fastcgi, certificates, security, c]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: dc-http
    resource: ../raw/docker-compose-acap/app/http_request.c
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce (985c8cede8b73d3a02a74c36e8a71d17b04852fe)"
    title: "http_request.c — POST and DELETE dispatch"
  - id: dc-multipart
    resource: ../raw/docker-compose-acap/app/fcgi_write_file_from_stream.c
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "fcgi_write_file_from_stream.c — multipart stream to temp file"
  - id: dc-tls
    resource: ../raw/docker-compose-acap/app/tls.c
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "tls.c — certificate checks and dockerd TLS arguments"
  - id: dc-fcgi
    resource: ../raw/docker-compose-acap/app/fcgi_server.c
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "fcgi_server.c — FastCGI socket and thread"
  - id: dc-manifest
    resource: ../raw/docker-compose-acap/app/manifest.json
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "ACAP manifest of the application"
  - id: dc-readme
    resource: ../raw/docker-compose-acap/README.md
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "README"
  - id: dc-html
    resource: ../raw/docker-compose-acap/app/html/index.html
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "Settings page with curl examples"
---

# Docker Compose ACAP certificates and TLS: FastCGI upload endpoint, validation and defects

When `TCPSocket` and `UseTLS` are both on, dockerd needs `ca.pem`, `server-cert.pem` and `server-key.pem` in the application's `localdata` directory and listens on port 2376 with `--tlsverify`. The application lets an administrator **upload and delete those files over HTTP** through a small FastCGI service, so no SSH access is needed. The README says an upload is rejected if the header or footer is wrong; the code does enforce that, but nothing else, and the multipart parser has memory-safety defects.[^dc-readme][^dc-tls] Daemon supervision is in [Daemon runtime](docker-compose-acap-daemon-runtime.md); general FastCGI exposure is in [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md).

## Endpoints and access

The manifest declares three `httpConfig` entries of type `fastCgi` with `access: admin`, named `ca.pem`, `server-cert.pem` and `server-key.pem`, so the device exposes `/local/<appName>/<name>` for each.[^dc-manifest] The wrapper opens a FastCGI Unix socket named by the environment variable `FCGI_SOCKET_NAME`, `chmod`s it `0777`, and serves all requests on one GLib thread.[^dc-fcgi]

```sh
curl --anyauth -u "<user>:<password>" -F file=@server-cert.pem -X POST   http://<device-ip>/local/dockerdwrapperwithcompose/server-cert.pem
curl --anyauth -u "<user>:<password>" -X DELETE http://<device-ip>/local/dockerdwrapperwithcompose/server-cert.pem
```

An alternative is `scp` into `/usr/local/packages/<app>/localdata/` followed by an application restart.[^dc-readme]

## Request handling

| Method | Behaviour | Status codes | Restarts dockerd |
| --- | --- | --- | --- |
| POST | stream the multipart body to a `mkstemp` file in `/tmp`, check PEM header and footer, copy to `localdata` with overwrite, delete the temp file | 204 success, 422 stream failure, 400 wrong format, 500 copy failure | yes, after a successful upload |
| DELETE | `stat` then `unlink` the named file in `localdata` | 204, 404 missing, 500 | no |
| other | rejected | 405 | no |

The behaviour matches the README's statements that dockerd restarts after each upload and not after a delete.[^dc-http][^dc-readme] The file name is the last URI segment; the `/local/<app>/` prefix is not validated in code and scoping rests on the manifest names.[^dc-http]

## Validation and dockerd arguments

- **Format check:** a file whose name contains `key` must begin and end with a `PRIVATE KEY` or `RSA PRIVATE KEY` PEM marker; every other file must have `BEGIN CERTIFICATE` and `END CERTIFICATE` markers. The header is read from the start and the footer from the end of the file.[^dc-tls]
- **Presence check:** `access(F_OK)` per file in `localdata`; missing files yield Status 3 and log warnings, only when TCP and TLS are on.[^dc-tls]
- **Arguments:** `--tlscacert`, `--tlscert` and `--tlskey` pointing into `localdata`, built into a static 512-byte buffer.[^dc-tls]
- **Client side:** a client uses `--tlsverify` with CA, client certificate and key against `tcp://<device>:2376`; without TLS the daemon listens on 2375, which the README calls extremely insecure. Generating the certificates is delegated to Docker's "protect access" documentation.[^dc-readme]
- **Settings page:** `html/index.html` is a static page with the curl examples, but it uses `/local/dockerdwrapper/` while the application name is `dockerdwrapperwithcompose`.[^dc-html][^dc-manifest]

## Defects and gaps (Observed)

1. **Stack buffer overflow risk:** the boundary length is the length of the `boundary=` text in the `Content-Type` header, which the client controls. After each full buffer the code copies `boundary_len` bytes into a 2049-byte stack buffer, so a boundary longer than the buffer overruns it. The endpoint requires an admin login, which limits exposure but not the defect.[^dc-multipart]
2. **Wrong prefix length:** the multipart check compares with `sizeof(MULTIPART_FORM_DATA) - 1`, where the constant is a `const char*`, so it compares the pointer size minus one (7 bytes on aarch64, 3 on armv7hf), not the 19 characters of the string; any header beginning with the same seven characters passes. A missing `CONTENT_TYPE` is dereferenced as NULL.[^dc-multipart]
3. **Empty boundary and NULL arithmetic:** an empty `boundary=` makes the comparison length zero so it always matches; the pre-boundary flag is set even when `strstr` returned NULL and a pointer is then advanced from NULL; `strtol` is unchecked and there is no upload size cap.[^dc-multipart]
4. **No filename allowlist:** any single-segment name is accepted by the handler, including `daemon.json` (which would break the daemon configuration); DELETE can unlink any file in `localdata`. The manifest's three entries limit reachable URLs in practice, so this is a defence-in-depth gap rather than a proven exposure.[^dc-http][^dc-manifest]
5. **Routing details:** the query string is not stripped, so `ca.pem?x` returns 404; a missing `REQUEST_URI` crashes `strrchr`.[^dc-http]
6. **Classification and buffer arithmetic:** `strstr(filename, "key")` misclassifies names such as `monkey.pem`; `g_snprintf(ptr, end - ptr, …)` receives a huge size if the buffer is exhausted; a PEM lacking a trailing newline can fail the footer check; the copy is not atomic because `g_file_copy` overwrites in place.[^dc-tls]
7. **Server hygiene:** the `malloc` in `fcgi_start` is unchecked and the socket is world-writable (`0777`).[^dc-fcgi]

## Evidence class

Endpoint list, status codes, validation rules and arguments are **Observed** by static reading; header/footer rejection and restart behaviour agree with the **Reported** README. Defects are **Observed** and **Unverified**: no request was sent and no fuzzing was done. Whether the TLS flags actually secure the daemon was not tested.

## Relationships

- **Part of** [Docker Compose ACAP repository](docker-compose-acap-repository.md).
- **Triggers** the restart logic of [Daemon runtime](docker-compose-acap-daemon-runtime.md) and sets Status 3 there.
- **Implements** the TLS prerequisite that [Container-based ACAP applications](acap-container-applications.md) states for the Docker ACAP.
- **Uses** the FastCGI reverse-proxy mechanism of [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md) and admin-only access from the manifest model in [ACAP application user types and permissions](acap-application-user-permissions.md).

[^dc-http]: `app/http_request.c::{http_request_callback, post_request, delete_request, exists_in_localdata, remove_from_localdata, copy_to_localdata}`; `app/app_paths.h::APP_LOCALDATA`.
[^dc-multipart]: `app/fcgi_write_file_from_stream.c::fcgi_write_file_from_stream` (content-type prefix check, `boundary_len`, 2048-byte `buffer`, trailing `memcpy`, pre/post-boundary handling).
[^dc-tls]: `app/tls.c::{tls_certs, is_key_file, cert_file_exists, tls_missing_certs, tls_log_missing_cert_warnings, tls_file_dockerd_args, tls_file_has_correct_format}`; check call site `get_and_verify_tls_selection` in `app/dockerdwrapperwithcompose.c`.
[^dc-fcgi]: `app/fcgi_server.c::{fcgi_start, handle_fcgi, fcgi_stop}`.
[^dc-manifest]: `app/manifest.json::acapPackageConf.configuration.httpConfig`.
[^dc-readme]: `README.md` §Using TLS to secure the application (TLS Setup, Client key and certificate, Usage example without TLS).
[^dc-html]: `app/html/index.html` (curl examples for the three PEM files).
