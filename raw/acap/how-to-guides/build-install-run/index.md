---
title: "Build, install, control | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/how-to-guides/build-install-run/"
domain: "developer.axis.com"
language: "en"
description: "The ACAP Native SDK uses a containerized setup instead of a traditional SDK installation. It is distributed as Docker images, without requiring manual installation or environment setup. The SDK provides all the necessary tools for developers to build, install, and control ACAP applications. Make sure you have Docker installed on your computer before getting started."
word_count: 2485
---

Version: ACAP version 12

The **ACAP Native SDK** uses a containerized setup instead of a traditional SDK installation. It is distributed as **Docker images**, without requiring manual installation or environment setup. The SDK provides all the necessary tools for developers to **build, install, and control ACAP applications**. Make sure you have [Docker](https://www.docker.com/) installed on your computer before getting started.

> [!-info] -info
> info
> 
> For developers new to Docker, refer to the [Docker CLI reference](https://docs.docker.com/reference/cli/docker/) for a comprehensive list of available commands and usage examples and get familiar with the Docker CLI commands.

## How to build an ACAP application

The **ACAP Native SDK** provides two distinct methodologies for the ACAP project compilation and packaging, each optimized for different stages of the software lifecycle. When building an application, **Docker** serves as both the **build environment** and the **delivery mechanism** for the SDK, automatically pulling the correct SDK image, building the project inside a container, and caching the resulting image locally for faster future builds.

Specifically, an **ACAP application** can be built either:

- **Dockerfile-Based**, by having Docker build the project from the instructions in a Dockerfile, see [Building using a Dockerfile](#building-using-a-dockerfile).
- **Interactively**, by building and running the project inside a running container, see [Building interactively inside the SDK container](#building-interactively-inside-the-sdk-container).

### Building using a Dockerfile

The **Dockerfile-based build** is primarily relevant for production deployment, Continuous Integration/Continuous Deployment (CI/CD) pipelines, and ensuring consistency and reproducibility builds across different environments. This method is ideal when the application code is stable, and the goal is to generate a final, deployable **Embedded Application Package** (`.eap`) file. It is also essential for automated build processes where manual intervention is minimized, as it simplifies the environment setup by requiring no manual SDK configuration and works well for large-scale or automated workflows.

When building an ACAP application using an automated workflow, a **Dockerfile** defines arguments such as the SDK version, target architecture, Ubuntu version, Docker Registry, and SDK repository. It also contains the instructions that Docker follows to build and create the application image. In this setup, all compilation and packaging are performed inside a Docker container.

> [!-info] -info
> info
> 
> For more details on how to create a Dockerfile for an ACAP application, see [Create your first ACAP application](https://developer.axis.com/acap/get-started/create-your-first-acap-application/#build-the-application). To learn more about writing a Dockerfile in general, refer to the [Docker documentation](https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/).

Beyond the Dockerfile, the top-level structure of an ACAP application also includes an `app` directory, where the application's project files are placed (See [Application project structure](https://developer.axis.com/acap/reference/application-project-structure/)).

Standing in your working directory, follow the step-by-step instructions below to build your ACAP application using this method:

```bash
docker build --build-arg ARCH=<ARCH> --tag <APP_IMAGE> .
```

Where:

- `<ARCH>`: specifies the SDK architecture — either `armv7hf` or `aarch64`. If the `--build-arg` flag is not provided, the command will use the `ARCH` value defined in the Dockerfile.
- `<APP_IMAGE>`: is the name and version to tag the image with, e.g., `my_acap:1.0`

As an example, the following command builds the `my_acap` application version 1.0 for the `armv7hf` architecture:

> [!-info] -info
> info
> 
> The 1.0 version here is just used for the resulting Docker image tag. The actual version of the application should be defined through the [`manifest.json`](https://developer.axis.com/acap/reference/manifest-schemas/general-info/) file in the `acapPackageConf.setup.version` field.

```bash
docker build --build-arg ARCH=armv7hf --tag my_acap:1.0 .
```

Alternatively, the following command builds the ACAP application for the `aarch64` architecture:

```bash
docker build --build-arg ARCH=aarch64 --tag my_acap:1.0 .
```

> [!-success] -success
> tip
> 
> On Apple Silicon (ARM) computers, use `--platform=linux/amd64` for both the `build` and `create` commands to suppress the **InvalidBaseImagePlatform** warning and ensure consistent behavior.

Once the build completes successfully, check the Docker image list to confirm that the image was created:

```bash
docker image ls
```

Next, you can create a temporary container from the custom image and copy its contents to a local directory named `build`:

```bash
docker cp $(docker create <APP_IMAGE>):/opt/app ./build
```

Then, this creates a `build` folder in the working directory, containing the generated application files described below:

> [!-info] -info
> info
> 
> The directory structure shown below represents a generic example. Depending on the complexity of the ACAP application, your own project directory may include additional source files, configuration files, etc.

```bash
<APP_NAME>
├── app
│   ├── <APP_NAME>.c
│   ├── LICENSE
│   ├── Makefile
│   └── manifest.json
├── build
│   ├── <APP_NAME>*
│   ├── <APP_NAME>_<VERSION>_<ARCH>.eap
│   ├── <APP_NAME>_<VERSION>_LICENSE.txt
│   ├── <APP_NAME>.c
│   ├── LICENSE
│   ├── Makefile
│   ├── manifest.json
│   ├── package.conf
│   ├── package.conf.orig
│   └── param.conf
├── Dockerfile
└── README.md
```

Where:

- **`build/<APP_NAME>*`** - Application executable binary file.
- **`build/<APP_NAME>_<VERSION>_<ARCH>.eap`** - Application package `.eap` file.
- **`build/<APP_NAME>_<VERSION>_LICENSE.txt`** - Copy of LICENSE file.
- **`build/manifest.json`** - Defines the application and its configuration.
- **`build/package.conf`** - Defines the application and its configuration.
- **`build/package.conf.orig`** - Defines the application and its configuration, original file.
- **`build/param.conf`** - File containing application parameters.

### Building interactively inside the SDK container

Conversely, the **interactive build method** supports a dynamic workflow by bind-mounting the project directory into a running container, which allows developers to execute build and package commands directly within the environment. This approach is helpful for **active development**, **debugging**, and **iterative testing**, as it provides immediate feedback, full control, and simplified experimentation directly inside the container.

The **SDK container** contains built-in tools to simplify the development workflow, such as `acap-build` and `eap-install.sh`. [The `acap-build` tool](#the-acap-build-tool) automates the process of building and packaging an application, while [the `eap-install.sh` tool](#controlling-from-inside-sdk-container) is used to manage ACAP applications packages on a target device, allowing developers to install, start, stop, or remove apps remotely using the device’s IP address and credentials.

To run the SDK container interactively and mount the application project, go to the directory of the application, *the one containing the `app` directory*, and run the following command:

```bash
docker run -v $PWD/app:/opt/app --rm -i -t axisecp/acap-native-sdk:<SDK_VERSION>-<ARCH>-<UBUNTU_VERSION>
```

Where:

- `-v $PWD/app:/opt/app`: Volume mount flag. Mounts the current working directory `$PWD/app` from the local machine into the container at `/opt/app`.
- `--rm`: Remove flag. It automatically removes the container after it stops, preventing leftover temporary containers.
- `-i`: Interactive flag. Keeps the container's standard input (STDIN) open, allowing interactive commands.
- `-t`: TTY flag. Allocates a pseudo-TTY, which, when used with -i, provides an interactive shell experience (like a standard terminal).
- `axisecp/acap-native-sdk`: Image Name and Tag. Specifies the official ACAP Native SDK Docker image to use in the Docker Hub repository.
- `<SDK_VERSION>-<ARCH>-<UBUNTU_VERSION>`: Specifies the SDK version, target architecture, and base Ubuntu version to use.

As an example, the following command selects `12.6.0` of the SDK, targets the `armv7hf` architecture and specifies Ubuntu `24.04`.

```bash
docker run -v $PWD/app:/opt/app --rm -i -t axisecp/acap-native-sdk:12.6.0-armv7hf-ubuntu24.04
```

Alternatively, the following command builds the application for the `aarch64` architecture using the same SDK and Ubuntu version:

```bash
docker run -v $PWD/app:/opt/app --rm -i -t axisecp/acap-native-sdk:12.6.0-aarch64-ubuntu24.04
```

> [!-success] -success
> tip
> 
> On Apple Silicon (ARM) computers, use `--platform=linux/amd64` for the `docker run` command to suppress the **InvalidBaseImagePlatform** warning and ensure consistent behavior.

At this point, you should be inside the container and see a prompt similar to the one below. The bind mount ensures that any changes made inside the container in `/opt/app` are reflected in the host directory `$PWD/app` in the local machine.

```bash
root@1e6b4f3d5a2c:/opt/app#
```

> [!-info] -info
> info
> 
> Once inside the container, the current working directory should be `/opt/app` and contain the application project files. You can verify this by running the command `pwd && ls`. The output below shows the directory contents for the [axparameter example](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/axparameter):
> 
> ```bash
> root@5d47cd14242f:/opt/app# pwd && ls
> /opt/app
> LICENSE  Makefile  axparameter.c  manifest.json
> ```

Now you’re ready to build and install the application. See [The `acap-build` tool](#the-acap-build-tool).

#### The acap-build tool

The `acap-build` script automates the process of building and packaging an ACAP application. It supports make as the build tool and can generate the final `.eap` package directly from within the container. Developers can also specify a custom manifest file, include additional resources, or disable package creation if needed.

To build an application, stand in the application directory inside the container and run the `acap-build` tool. For example, on the directory `/otp/app`, run the command below:

```bash
acap-build .
```

This command will compile and package your application into an `.eap` file. When you run the `acap-build` tool, it performs the following steps:

- Runs make, performing any required cross-compilation as defined in the available `Makefile`.
- Automatic insertions and updates in `manifest.json` file (Will only affect the `manifest.json` file inside the EAP file, not the original `manifest.json` file in the application project directory):
	- Sets `schemaVersion` to the highest schema version available in the SDK within the same major version. **Introduced in SDK version 12.11.0**
		- If omitted, sets `architecture` field based on SDK architecture.
		- If omitted, and using `schemaVersion` v2.x or higher, sets `compatibleOsVersions.min` field(s) to the AXIS OS version the SDK is based on. **Introduced in SDK version 12.10.0**
- Validates the manifest file against the manifest schema.
- Generates a `package.conf` file and related configuration files for backward compatibility. See [Migrating from package.conf to manifest.json](https://developer.axis.com/acap/how-to-guides/migrating-from-package-conf-to-manifest-json/) for more information.
- Creates an EAP (Embedded Application Package) file with suffix `.eap` including:
	- application executable
		- `LICENSE` file
		- any available `html` and `lib` folder
		- Postinstall and preuninstall scripts specified in `manifest.json`
		- other files listed with the `-a` option in the `acap-build` request
		- generated backward compatibility files

For more information or help with the build tool, run the `acap-build -h` command to display the available options and usage information for building an ACAP project:

> [!-info] -info
> info
> 
> Systemd will start and stop the ACAP application. It then assumes execution failure if the main process dies, which means that the process must not fork off to a background process.

## How to install an ACAP application

The installing process for an ACAP application consists of uploading the compiled package (the `.eap` file) to one or more target devices. This can be done using the device’s [web interface](#installing-using-the-web-gui), the [`eap-install.sh` tool](#installing-using-the-script-from-inside-the-sdk-container) provided inside the ACAP Native SDK container, or the [VAPIX API](#installing-using-vapix-api). Once installed, the application can be started, stopped, or removed as needed, enabling developers to test and manage their ACAP applications directly on the device environment.

### Installing using the web GUI

Axis devices supports a user-friendly web interface to install an ACAP application. The GUI provides a straightforward environment for uploading and managing applications without using command-line tools and it is particularly convenient for quick testing or managing a small number of devices.

To access the **Apps** section in the device web interface, open your web browser and navigate to:

```bash
http://<AXIS_DEVICE_IP>/index.html#apps
```

You can also click on the tab **Apps** in the device GUI to go the this section. The **Apps** section displays the application management interface, where all installed ACAP applications are visible. If your ACAP application is not [signed](https://developer.axis.com/acap/how-to-guides/service-portal/acap-application-signing/), you need to enable the **Allow unsigned apps** toggle in the **Apps** section, which may require administrator privileges.

To install your ACAP application, click the (**\+ Add app**) button to start the upload process. Browse to your built application package (the `.eap` file) and select the appropriate version for your device architecture:

- **ARM64 devices**: `<APP_NAME>_<VERSION>_aarch64.eap`
- **ARMv7 devices**: `<APP_NAME>_<VERSION>_armv7hf.eap`

Once the file is uploaded, click **Install** to begin the installation. Wait for the process to complete, after which the application will appear in the apps list, ready to run.

### Installing using the script from inside the SDK container

The SDK helps with installing a built application on the device from a terminal. You can also install application packages, using the device's web interface, but that is less convenient during application development.

To install a built application on a device, run:

```bash
eap-install.sh
```

Run the command without any options to get help.

To install a built application on a device, run the following command (you must enter the IP address and username and password of the device the first time):

```bash
eap-install.sh <axis_device_ip> <admin_account> <password> install
eap-install.sh 192.168.0.90 admin-user admin-password install
```

If the Network settings of your Axis device are set to HTTPS-only, you will be prompted to opt-in because the script does not currently support certificate verification:

```bash
Failed to connect to device via HTTP. Try HTTPS with --insecure? (y/n)
```

When you choose to run the script despite the insecure connection warning, it will internally use the [\-k (--insecure)](https://curl.se/docs/manpage.html#-k) option for the cURL calls. This allows the script to skip certificate verification.

The command remembers the device-ip and password after the first successful execution. After this you can simply run:

```bash
eap-install.sh install
```

> [!-info] -info
> info
> 
> You must run the command from the application project directory, see [Application project structure](https://developer.axis.com/acap/reference/application-project-structure/).

### Installing using VAPIX API

The [VAPIX Applications API](https://developer.axis.com/vapix/applications/application-api/#upload-application) provides an interface that allows developers to manage ACAP applications on Axis devices. It enables developers to upload, start, stop, and remove applications remotely, making it ideal for automated deployment and system integration. To upload and install an ACAP application using VAPIX, see [Upload Application](https://developer.axis.com/vapix/applications/application-api/#upload-application) in VAPIX documentation.

> [!-info] -info
> info
> 
> When working with unsigned ACAP applications, ensure that the device is configured to allow unsigned apps. If the **Allow unsigned apps** option is disabled, you can enable it using the VAPIX `AllowUnsigned` action before running the upload command. For more details, see [Configure Applications](https://developer.axis.com/vapix/applications/application-api/#configure-applications) in the VAPIX Applications API documentation.

## How to run and control an ACAP application

Controlling the ACAP application, e.g., starting, stopping, and removing the package, can be accomplished through multiple methods: the intuitive [Device Web GUI](#controlling-using-the-web-gui), [the `eap-install.sh` tool](#controlling-from-inside-sdk-container) accessible from within the interactive ACAP Native SDK container, or the [VAPIX API](#controlling-using-vapix).

### Controlling using the web GUI

The **Device Web GUI** provides a direct interface for managing the installed ACAP applications, allowing easy monitoring and control of applications without using command-line tools. It provides a simple interface for common operations:

- Start or Stop the ACAP: Locate your installed applications in the apps list. Use the toggle the switch to **start** (toggle **on**) or **stop** (toggle **off**) the application.
- Check application logs: Click the three-dot ellipsis menu associated with the application and select **App log** to view its logs.
- Remove the application: Click the three-dot ellipsis menu associated with the application and select **Delete** to remove it from the device.

### Controlling from inside SDK container

Before you continue, make sure that you have done a first successful execution of shell script command `eap-install.sh`, see [Installing using the script from inside the SDK container](#installing-using-the-script-from-inside-the-sdk-container) for more information.

To start, stop and remove an installed application, run:

```bash
eap-install.sh [start|stop|remove]
```

To start an installed application on the device, run:

```bash
eap-install.sh start
```

Now you can see the status of the application using the device's web interface.

To stop a running application, run:

```bash
eap-install.sh stop
```

To remove an installed application, run:

```bash
eap-install.sh remove
```

### Controlling using VAPIX

Once an ACAP application is installed on a device, it can be managed and controlled using the [VAPIX Application API](https://developer.axis.com/vapix/applications/application-api/#control-application). This API allows you to remote control of applications, including starting, stopping, and removing them, which is particularly useful for automated workflows or integration with external management systems. Additionally, the [VAPIX Application API](https://developer.axis.com/vapix/applications/application-api/#list-installed-applications) provides an endpoint to list of all installed ACAP applications, allowing verification of their presence and operational status.
