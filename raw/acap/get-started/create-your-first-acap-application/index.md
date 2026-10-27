---
title: "Create your first ACAP application | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/get-started/create-your-first-acap-application/"
domain: "developer.axis.com"
language: "en"
description: "After setting up your development environment, you are ready to create your"
word_count: 1929
---

Version: ACAP version 12

After setting up your development environment, you are ready to create your first ACAP application.

This page will guide you through the entire process of writing, building, running, and testing your first ACAP application. We will start off by writing a simple Hello World application. After that, we're going to extend it with a commonly used Axis API called AXParameter.

The application created in this guide is based on [hello-world](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/hello-world) and [axparameter](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/axparameter) from the [ACAP Native SDK Examples](https://github.com/AxisCommunications/acap-native-sdk-examples) repository.

## Set up the ACAP application project

Navigate to a place on your computer where you want to create the project directory for your application. Create the project directory with a fitting name, e.g., `hello-world`.

Inside `hello-world`, create a directory called `app`, and a file called `Dockerfile`. The `app` directory will be the root of your application, containing all the files needed to build the application. The `Dockerfile` will contain instructions for how to build it.

To complete the setup of the project file structure, navigate into the `app` directory and create the following required files:

- `manifest.json`
- `Makefile`
- `hello_world.c`
- `LICENSE`

The complete project structure should look like this:

```markdown
hello-world
├── app
│   ├── hello_world.c
│   ├── LICENSE
│   ├── Makefile
│   └── manifest.json
└── Dockerfile
```

> [!-info] -info
> info
> 
> For a more detailed explanation of the project structure, see [Application project structure](https://developer.axis.com/acap/reference/application-project-structure/).

## Write the application

With the project set up, let's begin writing the application.

### Manifest file

Let's start by writing the `manifest.json` file. This file defines the application and its configuration, and is used when installing the application on the Axis device.

The `manifest.json` file we're creating here will only contain the required fields. These required fields are validated during the building and singing process.

```json
{
  "schemaVersion": "1.7.4",
  "acapPackageConf": {
    "setup": {
      "appName": "hello_world",
      "vendor": "Example",
      "version": "1.0.0",
      "runMode": "never",
      "embeddedSdkVersion": "3.0"
    }
  }
}
```

> [!-info] -info
> info
> 
> For more details about the manifest file, see [manifest schemas](https://developer.axis.com/acap/reference/manifest-schemas/general-info/). From there, find all field descriptions by selecting your schema version in the sidebar.

### Main program

The application code can be written in either `C`, `C++`, or `shell`. In this guide we're going to use `C`.

Since we want to create a Hello World application, we only need a simple main function, where we open the syslog and print "Hello World!" to it. This is done with the following code in `hello_world.c`:

```c
#include <syslog.h>

#define APP_NAME "hello_world"

int main(void) {
    /* Open the syslog to report messages for APP_NAME */
    openlog(APP_NAME, LOG_PID | LOG_CONS, LOG_USER);

    syslog(LOG_INFO, "Hello World!");
}
```

> [!-info] -info
> info
> 
> For more details, see [Supported languages](https://developer.axis.com/acap/reference/supported-languages/).

### Makefile

The `Makefile` will contain the instructions for how to compile the program files. In this case it's just `hello_world.c`.

```makefile
PROGS     = hello_world
SRCS      = hello_world.c
OBJS      = $(SRCS:.c=.o)

all: $(PROGS)

$(PROGS): $(OBJS)
    $(CC) $(LDFLAGS) $^ $(LIBS) -o $@

clean:
    rm -f $(PROGS) *.o *.eap* *_LICENSE.txt package.conf* param.conf tmp*
```

### LICENSE file

The `LICENSE` file is also required and should list all open source licensed source code distributed with the application. If this file is left empty, the application build will fail. For this guide, just put:

```markdown
No licenses
```

## Build the application

When the application project files in `app` are written, it's time to build the ACAP application, i.e., the EAP (Embedded Application Package) file with the suffix `.eap`. To build the EAP file, we are going to use the ACAP Native SDK.

The ACAP Native SDK is a Docker container, and inside it you will find all the tools needed to build an ACAP application.

There are two ways to build an ACAP application, either by using a Dockerfile or by entering the ACAP Native SDK interactively. A Dockerfile will be used in this guide, since that is the method used in the [ACAP Native SDK Examples](https://github.com/AxisCommunications/acap-native-sdk-examples) repository. However, for a faster development loop, i.e., write code, build, test, and repeat, it can be a good idea to [Building interactively inside the SDK container](https://developer.axis.com/acap/how-to-guides/build-install-run/#building-interactively-inside-the-sdk-container).

With a Dockerfile, you're going to use the commands `docker build` and `docker cp` to build and then copy out the build artifacts, such as the `.eap` file.

Begin the `Dockerfile` by defining some arguments and use the `FROM` command to pull and use the ACAP Native SDK as the base image for the build:

```dockerfile
ARG ARCH=armv7hf
ARG VERSION=12.5.0
ARG UBUNTU_VERSION=24.04
ARG REPO=axisecp
ARG SDK=acap-native-sdk

FROM ${REPO}/${SDK}:${VERSION}-${ARCH}-ubuntu${UBUNTU_VERSION}
```

The important arguments that you might want to change are `ARCH` and `VERSION`. `ARCH` must match the architecture on your target Axis device, i.e., if you make an ACAP application for an ARTPEC-7, you must use the `armv7hf` SDK, and if you are targeting an ARTPEC-8 or later, you must use the `aarch64` SDK. Which SDK `VERSION` to use mainly depends on what AXIS OS your target device is running. Read more about ACAP Native SDK versions in [Software compatibility](https://developer.axis.com/acap/reference/axis-devices-and-compatibility/#software-compatibility).

After that, copy over the application project files stored in `app` into the container, and run the `acap-build` tool. Don't forget to source the `/opt/axis/acapsdk/environment-setup*` file to export important environment variables:

```dockerfile
ARG ARCH=armv7hf
ARG VERSION=12.5.0
ARG UBUNTU_VERSION=24.04
ARG REPO=axisecp
ARG SDK=acap-native-sdk

FROM ${REPO}/${SDK}:${VERSION}-${ARCH}-ubuntu${UBUNTU_VERSION}

# Building the ACAP application
COPY ./app /opt/app/
WORKDIR /opt/app
RUN . /opt/axis/acapsdk/environment-setup* && acap-build ./
```

With the `Dockerfile` complete, it's time to build it. As we defined `ARCH=armv7hf` in the `Dockerfile`, it will default to using the `armv7hf` SDK architecture. However, it is possible to choose between `armv7hf` and `aarch64` when calling the `docker build` command by using the `--build-arg` option.

To build the application, stand in the directory containing your `Dockerfile` and use the following command to build a custom image according to the build steps defined in the `Dockerfile`:

```bash
docker build --tag <APP_IMAGE> --build-arg ARCH=<ARCH> .
```
- `<APP_IMAGE>` is the name to tag the image with, e.g., `hello_world:1.0`
- `<ARCH>` is the SDK architecture, `armv7hf` or `aarch64`.

Instantiate a container from the custom image and copy the content to a local directory `build`:

```bash
docker cp $(docker create <APP_IMAGE>):/opt/app ./build
```

The `build` directory contains the build artifacts, where the application file is found with suffix `.eap`, depending on which SDK architecture that was chosen, one of these files should be found:

- `hello_world_1_0_0_aarch64.eap`
- `hello_world_1_0_0_armv7hf.eap`

> [!-info] -info
> info
> 
> For a detailed explanation of building an ACAP application, see the [Build, install, control](https://developer.axis.com/acap/how-to-guides/build-install-run/) guide.

## Install and start the application

Browse to the application page of the Axis device:

```sh
http://<AXIS_DEVICE_IP>/index.html#apps
```
- Click on the tab **Apps** in the device GUI
- Enable **Allow unsigned app** \` toggle
- Click **(+ Add app)** button to upload the application file
- Browse to the newly built ACAP application, depending on architecture:
	- `hello_world_1_0_0_aarch64.eap`
		- `hello_world_1_0_0_armv7hf.eap`
- Click **Install**
- Run the application by enabling the **Start** switch

Enabling the **Allow unsigned app** toggle is needed since the application is not signed. Learn more about the benefits of signing and how to sign an application on the [ACAP application singing](https://developer.axis.com/acap/how-to-guides/service-portal/acap-application-signing/) page.

### Test the application

To check that the application works as intended, open the app log, which can be found by either:

- Browsing to `http://<AXIS_DEVICE_IP>/axis-cgi/admin/systemlog.cgi?appname=hello_world`.
- Browsing to the **Apps** page and select **App log**.

If the log prints "Hello World!" as shown below, congratulations! You have successfully made your first ACAP application!

```markdown
----- Contents of SYSTEM_LOG for 'hello_world' -----

[ INFO ] hello_world[6425]: Hello World!
```

## Use your first API

There are a lot of different APIs available inside AXIS OS, and it is possible to create an application using those APIs without having to include them manually when building the application.

To be able to use an API that exists inside AXIS OS, that API has to be part of the ACAP Native SDK. The SDK supports various Axis APIs used for different use cases, such as VDO, used for video capture, AXEvent, used for sending and subscribing to events, and Larod, used for machine learning tasks on the built-in Deep Learning Processing Unit (DLPU). The SDK also contains some open-source APIs, such as `curl` and OpenCL. See [Native SDK API](https://developer.axis.com/acap/reference/supported-apis/) for a full list of the supported APIs.

Now, let's extend our Hello World application by using the AXParameter API, but before writing any code, take a moment to learn what it is and what it does by reading the [Parameter API](https://developer.axis.com/acap/reference/supported-apis/#parameter-api) section of the [Native SDK API](https://developer.axis.com/acap/reference/supported-apis/) page.

The first thing that needs to be updated is the `Makefile`. We need to include the `axparameter` library and also `glib-2.0` and `gio-2.0` since they are required for `axparameter` to work. The highlighted parts below show which lines to change.

```makefile
PROGS     = hello_world
SRCS      = hello_world.c
OBJS      = $(SRCS:.c=.o)

PKGS = glib-2.0 gio-2.0 axparameter

CFLAGS += $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) pkg-config --cflags $(PKGS))
LDLIBS += $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) pkg-config --libs $(PKGS))

all: $(PROGS)

$(PROGS): $(OBJS)
    $(CC) $(LDFLAGS) $^ $(LIBS) $(LDLIBS) -o $@

clean:
    rm -f $(PROGS) *.o *.eap* *_LICENSE.txt package.conf* param.conf tmp*
```

The `manifest.json` file can be used to configure default parameters for your application. Let's add a `string` typed parameter called *Message*, with a default value set to "Hello World!":

```json
{
  "schemaVersion": "1.7.4",
  "acapPackageConf": {
    "setup": {
      "appName": "hello_world",
      "vendor": "Example",
      "version": "1.0.0",
      "runMode": "never",
      "embeddedSdkVersion": "3.0"
    },
    "configuration": {
      "paramConfig": [
        {
          "name": "Message",
          "default": "Hello World!",
          "type": "string"
        }
      ]
    }
  }
}
```

The extension we are going to do to the Hello World application is to read the parameter value of *Message* and print that to the syslog. Make sure to include the `axparameter` library and use the `glib` library types when interacting with the `axparameter` methods. For each Axis API in the ACAP Native SDK, there is detailed reference documentation linked from the [Native SDK API](https://developer.axis.com/acap/reference/supported-apis/) page. Here is the [AXParameter API documentation](https://developer.axis.com/acap/acap-native-sdk-version-12/api/src/api/axparameter/html/index.html).

```c
#include <syslog.h>
#include <axsdk/axparameter.h>

#define APP_NAME "hello_world"

int main(void) {
    /* Open the syslog to report messages for APP_NAME */
    openlog(APP_NAME, LOG_PID | LOG_CONS, LOG_USER);

    // Passing in APP_NAME gives access to this application's parameters without qualifiers and
    // makes it possible to add or remove parameters.
    AXParameter* handle = ax_parameter_new(APP_NAME, NULL);

    // Create a gchar pointer that will contain the message set in the parameter
    gchar* message;

    // Use the parameter get function to retrieve the value from the "Message" parameter and store it in the gchar pointer.
    ax_parameter_get(handle, "Message", &message, NULL);

    // Log the message to the syslog.
    syslog(LOG_INFO, "%s", message);

    // Free the gchar pointer
    free(message);

    // Free the axparameter handle
    ax_parameter_free(handle);
}
```

Keep the Dockerfile as is and run the `docker build` and `docker cp` commands once again to build and extract the new `.eap` file. Remember to remove the old `build` directory before running `docker cp`. Then install the `.eap` just like before, see [Install and start the application](#install-and-start-the-application).

Since we have not updated the `appName` field in `manifest.json`, this installation will do an upgrade of the previously installed application. If you choose to update the `appName`, make sure to also update the filename of your main `.c` file, update the `#define APP_NAME` variable inside of the `.c` file, and update the reference to the `.c` file in the `Makefile` file.

When running the application, you will see that "Hello World!" is still being printed. That is the case because "Hello World!" was set as the default value of the *Message* parameter in `manifest.json`. Try setting a new value of the parameter through the web interface:

1. Go to **Apps** tab.
2. Open the application options.
3. Click **Settings** and change the value of the **Message** parameter.

Run the application again, and the new value should be logged.

To see a more comprehensive example using the `AXParameter` API, see [axparameter](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/axparameter) from the [ACAP Native SDK Examples](https://github.com/AxisCommunications/acap-native-sdk-examples) repository.
