---
title: "Axis developer documentation"
site: "Pre-requisites"
source: "https://developer.axis.com/acap/get-started/set-up-developer-environment/pre-requisites/"
domain: "developer.axis.com"
language: "en"
description: "To develop ACAP applications, you need the following:"
word_count: 181
---

Version: ACAP version 12

- A computer with Linux, Windows, or macOS.
- Docker ([download](https://docs.docker.com/get-docker/))
	- For Windows and macOS, use the automatically upgradable **Docker desktop stable**.
		- For Linux, use **Docker Engine** version 23.0.0 or later.
- Git ([download](https://git-scm.com/downloads))
- We also recommend using [Microsoft Visual Studio Code](https://code.visualstudio.com/). But you are free to choose your favorite editor.

## Understanding the ACAP SDK

The ACAP Native SDK uses a containerized approach that differs from traditional SDK installations.

### How it works

Unlike traditional SDKs that require separate download and installation, the ACAP Native SDK is distributed as Docker images. When you build an ACAP application:

1. The `Dockerfile` in each example specifies which SDK version to use.
2. Docker automatically downloads the SDK image on first build.
3. Your application is built inside this containerized environment.

### What this means for you

- No manual SDK download needed.
	- Just follow the `docker build` instructions in each example, Docker takes care of the rest.
- The SDK is cached locally. After the first download, subsequent builds are faster.

Docker is not just a build tool, it's the SDK delivery mechanism.
