---
title: "Set up device - advanced | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/get-started/set-up-developer-environment/set-up-device-advanced/"
domain: "developer.axis.com"
language: "en"
description: "Access the device through SSH"
word_count: 1057
---

Version: ACAP version 12

## Access the device through SSH

Developing an ACAP application often requires SSH access to the device for debugging, testing, and running command-line operations in AXIS OS. To support this workflow, you must enable and create a non-root SSH user on the device. The following instructions describe how to do this setup.

### Enable SSH and create a non-root user

Access to Axis devices via SSH is disabled by default. However, developers can enable SSH either through the device's web interface or by using the [SSH VAPIX API](https://developer.axis.com/vapix/network-video/ssh/). Starting with AXIS OS 12, SSH access requires a `non-root` user account.

The `non-root` SSH user has restricted privileges and can't perform administrative operations. It's suitable for tasks such as browsing the file system, monitoring device resources, and performing other non-administrative operations.

The following instructions describe how to enable SSH access using the web interface and create a `non-root` user account:

1. Go to `https://<AXIS_DEVICE_IP>/index.html#system/accounts`.
	- `<AXIS_DEVICE_IP>`: the IP address of the device.
2. Find the section on the web page called **SSH accounts**.
3. Toggle on the **Enable SSH** switch.
4. Click the **\+ Add SSH account** button to add a new SSH user.
5. Follow the instructions in the dialog and fill out the required fields to create an SSH account.

> [!-info] -info
> info
> 
> An ACAP application user can get SSH access by requesting and installing the [Developer Mode](#developer-mode).

### Connect to the device

To connect to the Axis device through SSH, use a command-line SSH client. It's included by default on Windows, macOS, and most Linux distributions and can be launched directly from the system terminal. Once the SSH user has been created, use it to connect to the device and provide the correct user's password.

```sh
ssh <ssh-user>@<AXIS_DEVICE_IP>
<ssh-user>@<AXIS_DEVICE_IP>'s password:
```

Where:

- `<ssh-user>` is the `non-root` SSH user created by the developer.
- `<AXIS_DEVICE_IP>` is the IP address of the device.

After typing the correct password, a shell prompt appears in the format `<ssh-user>@axis-<serial_number>`, confirming a successful SSH connection.

```sh
<ssh-user>@axis-<serial_number>:~#
```

Where:

- `<serial_number>` is the device serial number or MAC address.

## Developer Mode

Developer Mode is a feature introduced in AXIS OS 11.11 that grants SSH access to an ACAP application's dynamic user on an Axis device. When Developer Mode is enabled, the ACAP application's dynamic user is added to the `ssh` group.

To enable Developer Mode on Axis devices running AXIS OS 11.11 or later, install the `axis-unlock-acap-devmode` Custom Firmware Certificate (CFC) on the Axis device.

> [!-info] -info
> info
> 
> Starting with AXIS OS 13, the **Custom Firmware Certificate (CFC)** is no longer available and has been replaced by the [Developer Mode ACAP application](https://developer.axis.com/acap/13-alpha/get-started/set-up-developer-environment/set-up-device-advanced/#developer-mode).
> 
> The **Developer Mode ACAP application** can be installed on devices running AXIS OS 12.11 to prepare for an upgrade to AXIS OS 13. However, it has no effect on AXIS OS 12.11. On AXIS OS 12.11, unsigned ACAP applications still require the **Allow unsigned apps** option to be enabled, and SSH access still requires the [Custom Firmware Certificate (CFC)](#get-the-custom-firmware-certificate-cfc).
> 
> Developers planning to migrate devices **from AXIS OS 12.11 to AXIS OS 13.x** with **unsigned ACAP applications** should review [Upgrading to AXIS OS 13 with unsigned ACAP applications](https://developer.axis.com/acap/13-alpha/get-started/set-up-developer-environment/set-up-device-advanced/#upgrading-to-axis-os-13-with-unsigned-acap-applications) before upgrading.

### Get the Custom Firmware Certificate (CFC)

To enable Developer Mode on your Axis devices, you need to obtain a unique CFC for each individual unit. Axis partners are able to request a CFC through a web service accessible at [CFC Portal](https://www.axis.com/support/cfcportal).

- If not already logged in to your MyAxis account you will be redirected to a log in page during the verification step.

To request a CFC, you will need to provide information about your device. This information can be retrieved either by calling VAPIX APIs or by using the device web interface, and is explained in the sections below.

Once you have gathered this information, you will be able to submit a request for a CFC through the web service. If the request is successful, you will receive a file ending with the suffix `.fcr`, which is the actual certificate file you will need to install on your device.

#### Using VAPIX APIs

1. Use the [basicdeviceinfo API](https://developer.axis.com/vapix/network-video/basic-device-information/#description) to retrieve:
	- `SerialNumber`: The serial number of the device.
		- `Soc`: The name of the device's SoC (system-on-chip), e.g., `artpec-7`, `artpec-8`, `ambarella-cv25`, etc.
		- `SocSerialNumber`: The unique identifier of the SoC, also referred to as **Processor Serial Number**.
2. Use the [OAK API](https://developer.axis.com/vapix/network-video/oak-api/) to retrieve the Owner Authentication Key (OAK).

#### Using the device web interface

1. Navigate to the device's plain configuration page, typically at `http://192.168.0.90/index.html#system/plainConfig`.
2. Search for the **SerialNumber** and **Soc** values.
3. To get the OAK, navigate to the device's network configuration page, typically at `http://192.168.0.90/index.html#system/network`.
4. Scroll down to the **Owner authentication key (OAK)** section and press the **Get key** button.

### Install the CFC on your device

1. Navigate to the device's security configuration page, typically at `http://192.168.0.90/index.html#system/security`.
2. Scroll down to the **Custom Signed AXIS OS Certificate** section.
3. If `axis-unlock-acap-devmode` is not already installed, install it via the **Install** button.

### Verify Developer Mode is enabled

When Developer Mode is enabled on your device, an SSH account is automatically created whenever an ACAP application using a [dynamic user](https://developer.axis.com/acap/how-to-guides/configure-application-user/#difference-between-the-application-user-types) is installed. Follow these steps to enable SSH access for the application user:

1. Navigate to the device's accounts configuration page, typically at `https://<AXIS_DEVICE_IP>/index.html#system/accounts`.
2. Scroll down to the **SSH accounts** section.
3. Verify that the **Enable SSH** switch is enabled.
4. Find the ACAP application user (named `acap-<appName>`).
5. To enable SSH access for the ACAP application user:
	- **Set a password for it** by pressing the three dots to the right and choosing **Update SSH account**. This is required for SSH access.

### Disable Developer Mode

1. Navigate to the device's security configuration page, typically at `http://<AXIS_DEVICE_IP>/index.html#system/security`.
2. Scroll down to the **Custom Signed AXIS OS Certificate** section.
3. `axis-unlock-acap-devmode` will be listed as one of the **Installed certificates**. Press the three dots to the right of the certificate and choose **Delete certificate**.
4. Additionally, the device needs to be factory defaulted after removing the certificate for developer mode to be disabled.
	- Navigate to the device's maintenance page, typically at `http://<AXIS_DEVICE_IP>/index.html#maintenance`.
		- In the **Factory default** section press the `Default` button followed by `Restore all` in the popup frame.

To verify that developer mode is no longer active, one way is to install an ACAP application and verify that no new ACAP SSH user is added.
