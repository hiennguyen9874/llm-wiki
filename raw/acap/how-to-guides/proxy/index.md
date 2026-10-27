---
title: "Axis developer documentation"
site: "Proxy"
source: "https://developer.axis.com/acap/how-to-guides/proxy/"
domain: "developer.axis.com"
language: "en"
description: "Proxy in build time"
word_count: 264
---

Version: ACAP version 12

## Proxy in build time

The ACAP Native SDK build environment uses Docker. If the build machine is positioned inside a network using a proxy, the Docker toolchain needs to be configured.

### Docker daemon proxy

In order to pull ACAP Native SDK images from Docker Hub within a network using a proxy, it is necessary to configure the Docker daemon. Please refer to Docker's guide, [Daemon proxy configuration](https://docs.docker.com/engine/daemon/proxy), for detailed instructions.

### Docker build environment

Further proxy configuration might also be needed to be able to build and run Docker containers. For example, if you're within a network using a proxy and your `Dockerfile` contains instructions for installing Ubuntu packages with `apt` or downloading files with `curl`. To set up proxy configuration for these cases, follow the instructions in [Use a proxy server with the Docker CLI](https://docs.docker.com/engine/cli/proxy).

## Proxy in runtime

Proxy settings may need to be configured on your Axis device to run an ACAP application successfully, especially if the device is behind a network proxy and your ACAP application requires internet access.

To make an ACAP application use a proxy during runtime, it's possible to configure a global proxy on your Axis devices. Global proxy settings act as environment variables in AXIS OS, that ACAP applications automatically can pick up. There are three types of global device proxies that can be configured; `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`.

### Configure global device proxy

Global device proxy can be configured via either:

- The VAPIX [Network Settings API](https://developer.axis.com/vapix/network-video/network-settings-api/#set-global-proxy-configuration-api-specification).
- The network page at `http://<AXIS_DEVICE_IP>/index.html#system/network`, in section `Global proxies`.
