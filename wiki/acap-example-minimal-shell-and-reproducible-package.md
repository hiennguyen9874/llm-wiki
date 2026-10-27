---
type: Concept
title: "ACAP examples: hello-world, shell-script-example and reproducible-package"
description: "The smallest ACAP examples: a C hello-world logging to syslog, an architecture-independent shell-script app packaged as _all.eap, and reproducible-package, which gets bit-identical .eap files through SOURCE_DATE_EPOCH, with verification steps and the BUILD_DATE caveat."
tags: [edge-ai, axis, acap, examples, hello-world, shell, reproducible-builds]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: native-examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e (3025a4e9db74f1af5bb878d4efc82ac0e300a792, commit date 2026-09-01)"
    title: "AxisCommunications/acap-native-sdk-examples (git submodule)"
---

# ACAP examples: hello-world, shell-script-example and reproducible-package

Three examples define the minimum shape of an ACAP package and one packaging property.[^native-examples]

## hello-world

A C app whose `main` calls `syslog(LOG_INFO, "Hello World!")` and returns (`hello-world/app/hello_world.c`). The Makefile derives the program name from `jq -r '.acapPackageConf.setup.appName' manifest.json`, compiles with strict warnings and `-Werror`, links `-lm` and strips the binary. The manifest has `appName: hello_world`, no `friendlyName`, no `resources`. Outputs: `hello_world_1_0_0_{armv7hf,aarch64}.eap`; expected log `hello_world[6425]: Hello World!`.[^native-examples] It is the canonical build and install walk-through that other READMEs copy; the same flow in prose is [Create, build and install your first ACAP application](acap-first-application-workflow.md), and reading the log is covered in [Application logging in ACAP](acap-application-logging.md).

## shell-script-example

An app that is a shell script: `app/` holds only `shell_script_example`, `LICENSE` and `manifest.json`; there is no Makefile. The script sets `PROCESS_ID=$(pidof shell_script_example)` and calls `logger -t "shell_script_example[$PROCESS_ID]" -p INFO "Hello World!"`. The manifest sets `architecture: "all"`, so the package is `shell_script_example_1_0_0_all.eap` and one build runs on every architecture. `pidof` may be empty very early in startup, giving an empty tag index.[^native-examples]

## reproducible-package

- **Goal:** three builds of the same sources give byte-identical `.eap` files.
- **Mechanism:** the Dockerfile takes `ARG TIMESTAMP` and runs `export SOURCE_DATE_EPOCH=${TIMESTAMP} && acap-build ./`; archive member timestamps then follow that epoch. The README's procedure builds once with no timestamp (the non-reproducible baseline), then twice with `TIMESTAMP="$(git log -1 --pretty=%ct)"`, and compares with `cmp`: build 1 vs 2 differ (README cites byte 13), build 2 vs 3 are identical. An interactive variant runs `SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct) acap-build .` inside the container, which needs the `.git` directory.
- **Script:** `reproducible_package.sh {build|test|clean}` with `--arch`, `--repo`, `--sdk`, `--sdk-version`, `--ubuntu-version` tags images `rep-<arch>:1|2|3`, runs both `cmp` checks and cleans up; CI runs it for each architecture.
- **Caveat (Observed):** the Makefile computes `BUILD_DATE` from `SOURCE_DATE_EPOCH` and prints it, but never passes it to the compiler, so the README's statement that the Makefile "sets BUILD_DATE" has no effect on the binary; reproducibility rests on `acap-build` honouring `SOURCE_DATE_EPOCH`. The README's first `docker build` omits `--no-cache` although the text says it is used.[^native-examples]

Evidence class: the mechanism and the missing `-DBUILD_DATE` are **Observed**; the byte-identical result is **Reported** by the README and not reproduced.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md); conventions in [shared build conventions](acap-examples-build-and-manifest-conventions.md).
- **Related** [Build, install, and control ACAP applications](acap-build-install-control.md) for `acap-build` and architecture options.

[^native-examples]: `hello-world/app/{hello_world.c,Makefile,manifest.json}`, `hello-world/README.md`; `shell-script-example/app/{shell_script_example,manifest.json}`, `shell-script-example/README.md`; `reproducible-package/{Dockerfile,README.md,reproducible_package.sh,app/Makefile,app/manifest.json}`; `.github/workflows/reproducible-package.yml`.
