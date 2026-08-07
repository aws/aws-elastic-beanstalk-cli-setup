# Elastic Beanstalk CLI Installer
- [1. Overview](#1-overview)
  - [1.1. Prerequisites](#11-prerequisites)
- [2. Quick start](#2-quick-start)
  - [2.1. Clone this repository](#21-clone-this-repository)
  - [2.2. Install/Upgrade the EB CLI](#22-installupgrade-the-eb-cli)
    - [MacOS/Linux](#macoslinux)
    - [Windows](#windows)
  - [2.3. After installation](#23-after-installation)
- [3. Usage](#3-usage)
  - [3.1 Advanced usage](#31-advanced-usage)
  - [3.2 Options](#32-options)
- [4. Troubleshooting](#4-troubleshooting)
- [5. Frequently asked questions](#5-frequently-asked-questions)
  - [5.1. For the **experienced Python developer**, what's the advantage of this mode of installation instead of regular `pip` inside a `virtualenv`?](#51-for-the-experienced-python-developer-whats-the-advantage-of-this-mode-of-installation-instead-of-regular-pip-inside-a-virtualenv)
  - [5.2. On macOS (or Linux systems with `brew`), is this better than `brew install awsebcli`?](#52-on-macos-or-linux-systems-with-brew-is-this-better-than-brew-install-awsebcli)
  - [5.3. I already have the EB CLI installed. Can I still execute `ebcli_installer.py`?](#53-i-already-have-the-eb-cli-installed-can-i-still-execute-ebcli_installerpy)
  - [5.4. How does `ebcli_installer.py` work?](#54-how-does-ebcli_installerpy-work)
  - [5.5. Are there dependency problems that this mode of installation doesn't solve?](#55-are-there-dependency-problems-that-this-mode-of-installation-doesnt-solve)
- [6. License](#6-license)

## 1. Overview

This repository hosts scripts to generate self-contained installations of the [EB CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html).

### 1.1. Prerequisites

You will need to have the following prerequisites installed before running the install script.

* **Git**
  * If not already installed you can download git from the [Git downloads page](https://git-scm.com/downloads).
* **Python**
  * We recommend that you install Python using the [pyenv](https://github.com/pyenv/pyenv) Python version manager. Alternately, you can download Python from the [Python downloads page](https://www.python.org/downloads/).
* **virtualenv**
  * Follow the [virtualenv documentation](https://virtualenv.pypa.io/en/latest/installation.html) to install virtualenv.

## 2. Quick start

### 2.1. Clone this repository

Use the following:

```
git clone https://github.com/aws/aws-elastic-beanstalk-cli-setup.git
```

### 2.2. Install/Upgrade the EB CLI

#### MacOS/Linux
On **Bash** or **Zsh**:

```
python ./aws-elastic-beanstalk-cli-setup/scripts/ebcli_installer.py
```

#### Windows
In **PowerShell** or in a **Command Prompt** window:

```
python .\aws-elastic-beanstalk-cli-setup\scripts\ebcli_installer.py
```

### 2.3. After installation

On Linux and macOS, the output contains instructions to add the EB CLI (and Python) executable file to the shell's `$PATH` variable, if it isn't already in it.

## 3. Usage

The `ebcli_installer.py` Python script will install the [awsebcli](https://pypi.org/project/awsebcli/) package in a virtual environment to prevent potential conflicts with other Python packages.

For most use cases you can execute the `ebcli_installer.py` script with no arguments.

```
python ./aws-elastic-beanstalk-cli-setup/scripts/ebcli_installer.py
```

### 3.1 Advanced usage

  - To install a **specific version** of the EB CLI:

    ```shell
    python scripts/ebcli_installer.py --version 3.14.13
    ```

  - To install the EB CLI with a specific **version of Python** (the Python version doesn't need to be in `$PATH`):

    ```shell
    python scripts/ebcli_installer.py --python-installation /path/to/some/python/on/your/computer
    ```

  - To install the EB CLI **from source** (Git repository, .tar file, .zip file):
    ```shell
    python scripts/ebcli_installer.py --ebcli-source /path/to/awsebcli.zip

    python scripts/ebcli_installer.py --ebcli-source /path/to/EBCLI/codebase/on/your/computer
    ```
  - To install the EB CLI at a **specific location**, instead of in the standard `.ebcli-virtual-env` directory in the user's home directory:

    ```shell
    python scripts/ebcli_installer.py --location /path/to/ebcli/installation/location
    ```
### 3.2 Options

```
options:
  -h, --help            show this help message and exit
  -e VIRTUALENV_EXECUTABLE, --virtualenv-executable VIRTUALENV_EXECUTABLE
                        path to the virtualenv installation to use to create the EBCLI's virtualenv
  -i, --hide-export-recommendation
                        boolean to hide recommendation to modify PATH
  -l LOCATION, --location LOCATION
                        location to store the awsebcli packages and its dependencies in
  -p PYTHON_INSTALLATION, --python-installation PYTHON_INSTALLATION
                        path to the python installation under which to install the awsebcli and its
                        dependencies
  -q, --quiet           enable quiet mode to display only minimal, necessary output
  -s EBCLI_SOURCE, --ebcli-source EBCLI_SOURCE
                        filesystem path to a Git repository of the EBCLI, or a .zip or .tar file of
                        the EBCLI source code; useful when testing a development version of the EBCLI.
  -v VERSION, --version VERSION
                        version of EBCLI to install
```

## 4. Troubleshooting

- **Linux**

    Most installation problems have been due to missing libraries such as `OpenSSL`.

  - On **Ubuntu and Debian**, run the following command to install dependencies.

    ```shell
    apt-get install \
        build-essential zlib1g-dev libssl-dev libncurses-dev \
        libffi-dev libsqlite3-dev libreadline-dev libbz2-dev
    ```

  - On **Amazon Linux and Fedora**, run the following command to install dependencies.

    ```shell
    yum group install "Development Tools"
    yum install \
        zlib-devel openssl-devel ncurses-devel libffi-devel \
        sqlite-devel.x86_64 readline-devel.x86_64 bzip2-devel.x86_64
    ```

- **macOS**

  Most installation problems on macOS are related to loading and linking OpenSSL and zlib. The following command installs the necessary packages and tells the Python installer where to find them:

    ```
    brew install zlib openssl readline
    CFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix readline)/include -I$(xcrun --show-sdk-path)/usr/include" LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix zlib)/lib" ./scripts/bundled_installer
    ```
    Run `brew info` to get the latest environment variable export suggestions, such as `brew info zlib`

- **Windows**

    - In PowerShell, if you encounter an error with the message "execution of scripts is disabled on this system", set the [execution policy](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-6) to `"RemoteSigned"` and then rerun `bundled_installer`.

      ```ps1
      Set-ExecutionPolicy RemoteSigned
      ```
    - If you encounter an error with the message "No module named 'virtualenv'", use the following commands to install `virtualenv` and the EB CLI:
      ```ps1
      pip uninstall -y virtualenv
      pip install virtualenv
      python .\aws-elastic-beanstalk-cli-setup\scripts\ebcli_installer.py
      ```
## 5. Frequently asked questions

### 5.1. For the **experienced Python developer**, what's the advantage of this mode of installation instead of regular `pip` inside a `virtualenv`?

Even within a `virtualenv`, a developer might need to install multiple packages whose dependencies are in conflict. For example, at times the AWS CLI and the EB CLI have used conflicting versions of `botocore`. [One such instance](https://github.com/aws/aws-cli/issues/3550) was particularly egregious. When there are conflicts, users have to manage separate `virtualenvs` for each of the conflicting packages, or find a combination of the packages without conflicts.

Both of these workarounds become unmanageable over time, and as the number of packages that are in conflict increases.

### 5.2. On macOS (or Linux systems with `brew`), is this better than `brew install awsebcli`?

**Yes**, for these reasons:

  - The AWS Elastic Beanstalk team has no control over how `brew` operates.
  - The `brew install ...` mechanism doesn't solve the problem of dependency conflicts, which is a primary goal of this project.

### 5.3. I already have the EB CLI installed. Can I still execute `ebcli_installer.py`?

**Yes**.

Consider the following two cases:

- `ebcli_installer.py` was previously run, creating `.ebcli-virtual-env` in the user's home directory (or the user's choice of a directory indicated through the `--location` argument). In this case, the EB CLI will overwrite `.ebcli-virtual-env` and attempt to install the latest version of the EB CLI in the `virtualenv` within it.

- `eb` is in `$PATH`, however, it wasn't installed by `ebcli_installer.py`. In this case, the installer will install `eb` within `.ebcli-virtual-env` in the
user's home directory (or the user's choice of a directory indicated through the `--location` argument), and prompt the user to prefix
`/path-to/.ebcli-virtual-env/executables` to `$PATH`. Until you perform this action, the older `eb` executable file will continue to be referenced when you type `eb`.

### 5.4. How does `ebcli_installer.py` work?

When executing the Python script, `ebcli_installer.py` does the following:

- Creates a `virtualenv` exclusive to the `eb` installation.
- Installs `eb` inside that `virtualenv`.
- In the `<installation-location>/executables` directory, it generates:
  - A `.py` wrapper for `eb` on Linux or macOS.
  - `.bat` and `.ps1` wrappers for `eb` on Windows.
- When complete, you will be prompted to add `<installation-location>/executables` to `$PATH`, only if the directory is not already in it.

### 5.5. Are there dependency problems that this mode of installation doesn't solve?

Unfortunately, **yes**.

Suppose the dependencies of `eb`, say `Dep A` and `Dep B`, are in conflict. Because `pip` lacks dependency management capabilities, the resulting `eb` installation might not work.

## 6. License

This library is licensed under the Apache-2.0 License.
