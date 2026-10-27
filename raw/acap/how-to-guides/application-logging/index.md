---
title: "Application logging | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/how-to-guides/application-logging/"
domain: "developer.axis.com"
language: "en"
description: "This guide explains how to use the logging functionality in ACAP applications."
word_count: 395
---

Version: ACAP version 12

This guide explains how to use the logging functionality in ACAP applications.

## Produce logs

This section goes through the details of how to send messages to the log. See the [hello-world](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/hello-world) example application for a minimal example.

### Basic use

The logging functionality in ACAP applications depends on the syslog library. Include it to your application by adding this line:

```c
#include <syslog.h>
```

With the syslog library included, it's possible to use `syslog()` to log messages. This function is used similarly to `printf()`, but it takes a priority level as its first argument:

- `LOG_INFO` - Informational message
- `LOG_WARNING` - Warning conditions
- `LOG_ERR` - Error conditions
- `LOG_CRIT` - Critical conditions

For example, to log an informational message:

```c
syslog(LOG_INFO, "%s", "Hello World!");
```

### Debug logging

There's also a fifth logging priority level, `LOG_DEBUG`, that can be used when you don't want the logs to be visible in the [Device web interface](#device-web-interface). However, they will show up when using [`journalctl`](#journalctl).

### Using openlog()

Optionally, it is possible to call `openlog()` before the first call to `syslog()` to configure how the application sends messages to the system log. For example, `openlog()` can be used to set a custom identifier for logging. The default identifier is the `appName` of your application, as defined in `manifest.json`. Note that the methods explained in [View logs](#view-logs), assumes that you're not using a custom identifier. For example, when viewing the logs via the device web interface, the logs won't show up unless you edit the `URL` by using your custom identifier instead of the actual app name:

```markdown
http://<AXIS_DEVICE_IP>/axis-cgi/admin/systemlog.cgi?appname=<CUSTOM_IDENTIFIER>
```

## View logs

This section describes the different methods available to view application logs.

### Device web interface

The most accessible method for viewing logs is via the device web interface. This is most likely how your application users will view the log. To find it, browse to you device:

```sh
http://<AXIS_DEVICE_IP>
```

From there, the application log can be found by:

1. Go to the **Apps** tab.
2. Open the application options.
3. Click **App log**.

Or alternatively, directly at:

```markdown
http://<AXIS_DEVICE_IP>/axis-cgi/admin/systemlog.cgi?appname=<APPNAME>
```

### journalctl

When connected to the Axis device through SSH, it's possible to use the `journalctl` tool to view the log. Use the `-t/--identifier` option to only show logs from your application, and the `-f/--follow` option to follow the journal:

```sh
journalctl -t <APPNAME> -f
```

For help on using the `journalctl` tool, run `journalctl -h`.
