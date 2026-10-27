---
title: "Include third party libraries | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/how-to-guides/include-third-party-libraries/"
domain: "developer.axis.com"
language: "en"
description: "ACAP Native SDK"
word_count: 508
---

Version: ACAP version 12

## ACAP Native SDK

Below is a generic guide on how to build and include a third-party library in your application using the ACAP Native SDK.

The third-party library build is taken care of by the Docker file. So while building the third-party library, update and install all necessary build tools needed to build a specific third-party library. Refer to one of the examples in [utility-libraries](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/utility-libraries) that show how supporting build tools are installed, and how third-party library compilation for **armv7hf** is done using the Docker file.

### Overview of Docker commands used to build the third-party library and generate an ACAP application

Docker command to install supporting build tools:

```dockerfile
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
         <ubuntu-package>
```

Cloning of the source code to build the third-party library must be made to a specific work directory in the Docker container.

Docker command to switch to the third-party library build directory:

```dockerfile
WORKDIR /opt/build
```

Now clone the source code to `/opt/build` directory, from which the third-party library is generated:

```dockerfile
RUN git clone <Third-party source code github path>
```

Go to the cloned directory:

```dockerfile
WORKDIR /opt/build/<cloned directory>
```

Before building a third-party library:

- Source the cross-compilation environment setup file.
- Configure output build directory path for custom library build using \[--prefix\]
- Include cross compiler flags if any.
- Run `make`
- Below is one of the examples with respect to cURL:
```dockerfile
#  lib generate
# - Source the SDK environment script to get links to cross compiler through
# - CONFIGURE_FLAGS environment variable
WORKDIR /opt/build/curl
RUN . /opt/axis/acapsdk/environment-setup* && \
    autoreconf -fi && \
    ./configure --prefix=${PWD}/build ${CONFIGURE_FLAGS} --without-ssl && \
    make && \
    make install
```

Once the build is successful copy the generated library directory to the `/opt/app/lib` folder.

```dockerfile
# Copy the library to application folder
ARG BUILDDIR=/opt/build/curl
COPY ./app /opt/app/
WORKDIR /opt/app
RUN mkdir lib && cp -r ${BUILDDIR}/build lib
```

`/opt/app/lib` folder contains cross-compiled shared library files that will be included in the ACAP.

In the application `Makefile`, enter the custom library header file and library path, and link the library.

```bash
LDLIBS += -Llib/
CFLAGS += -Ilib/include
SHLIB_DIR = ./lib
LDFLAGS = -L$(SHLIB_DIR) -Wl,--no-as-needed,-rpath,'$$ORIGIN/lib'
SHLIBS += -lm -l[lib](linking-third-party-lib)
```

### Importance of setting RPATH

The **RPATH** setting is to change the library search path so that one executable or library can link the desired dependent libraries during runtime.

> [!-info] -info
> info
> 
> Set **RPATH** to the directory where shared libraries are located, with the help of **$ORIGIN**. This will tell the linker to search and include libraries under the specified library path, usually used to override the default library paths.

Once all of the above configurations are made you are ready to build and install the application. See [Building using a Dockerfile](https://developer.axis.com/acap/how-to-guides/build-install-run/#building-using-a-dockerfile).

### Troubleshooting

Normally, the Configure file is available when building a custom library for a specific architecture. If the Configure file is not available, then create an output build directory using Makefile, and copy generated lib files to the output library directory as shown in the reference below.

```bash
mkdir -p build
mkdir -p build/include
cp *.h build/include
cp [lib.so] build/
```
