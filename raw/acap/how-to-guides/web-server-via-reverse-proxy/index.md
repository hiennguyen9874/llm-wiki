---
title: "Web server | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/how-to-guides/web-server-via-reverse-proxy/"
domain: "developer.axis.com"
language: "en"
description: "Web server development for ACAP applications can either be done by using a Reverse Proxy configuration or FastCGI. Each method offer its own advantages and can be chosen based on your specific use case or requirements."
word_count: 432
---

Version: ACAP version 12

Web server development for ACAP applications can either be done by using a Reverse Proxy configuration or FastCGI. Each method offer its own advantages and can be chosen based on your specific use case or requirements.

## Web server with reverse proxy

[Reverse Proxy configuration](https://httpd.apache.org/docs/2.4/howto/reverse_proxy.html) provides a flexible way for an application to expose an external API through the Apache Server in AXIS OS system and internally route the requests to a small Web Server running in the application.

Web Server via Reverse Proxy is a technique that can be used for exposing many types of network APIs and can e.g., cover same CGI use cases as axHttp API from ACAP SDK 3.

The Web Server running in the application can also be exposed directly to the network by allowing external access to the port in the network configuration for the device. There are some disadvantages with exposing Web Server directly to the network such as non standard ports and no reuse of authentication, TLS and other features that comes with Apache Server.

### Configure reverse proxy

Serving a web page with a reverse proxy setup requires that `acapPackageConf.configuration.reverseProxy` is set in the manifest. One example of this is shown below.

```json
{
    "schemaVersion": "1.8.0",
    "acapPackageConf": {
        "setup": {
            "appName": "dynamic_user_app",
            "friendlyName": "App with reverse proxy",
            "vendor": "Axis Communications",
            "embeddedSdkVersion": "3.0",
            "runMode": "never",
            "version": "1.0.0"
        },
        "configuration": {
            "reverseProxy": [
                {
                    "apiPath": "my_web_server",
                    "target": "http://localhost:2001",
                    "access": "admin"
                }
            ]
        }
    }
}
```

### Reverse proxy example

- [reverse-proxy-using-fixed-port](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/web-server/reverse-proxy-using-fixed-port)
	- An example of an application using [CivetWeb web server](https://github.com/civetweb/civetweb) to expose an external API with Reverse Proxy configuration in Apache Server. This example uses a port to route requests between the application and the reverse proxy. Read more about the limitations and the considerations needed when using a port in the example [README](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/web-server/reverse-proxy-using-fixed-port/README.md).

## Web server with FastCGI

The [FastCGI API](https://developer.axis.com/acap/reference/supported-apis/#fastcgi) enables integration with the device's Apache web server, offering an approach for applications to handle HTTP requests efficiently. By leveraging FastCGI, the application can manage requests and responses seamlessly, utilizing [uriparser](https://uriparser.github.io/) to parse query parameters. This method is more integrated with the Axis device compared to [Web server with reverse proxy](#web-server-with-reverse-proxy), as it utilizes the built-in Apache web server, eliminating the need of a custom web server. This integration allows the API to be exposed on the same port as VAPIX, ensuring users are authenticated in the same manner and using the same user pool as VAPIX.

### FastCGI example

- [http-requests-using-fastcgi](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/web-server/http-requests-using-fastcgi)
	- An example of an application using [FastCGI](https://developer.axis.com/acap/reference/supported-apis/#fastcgi) to handle the requests and responses, building upon the web server already present in the device.
