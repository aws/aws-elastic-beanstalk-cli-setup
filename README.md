## EBCLI Installer

------

### 1. Overview

------

This repository hosts scripts to generate self-contained installations of the [EBCLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html).

------

### 2. Usage

------

#### 2.1. Clone this repository:

```bash
git clone https://github.com/aws/aws-elastic-beanstalk-cli-setup.git
```

#### 2.2. Install:

On Bash and Zsh:

```bash
python aws-elasticbeanstalk-cli-setup/scripts/bundled_installer
```

On PowerShell and CMD Prompt:

```bash
python .\aws-elasticbeanstalk-cli-setup\scripts\bundled_installer
```

#### 2.3. Post-installation activities:

The emitted output will contain instructions to add the EBCLI (and Python) executable to the shell's `$PATH` variable, if it is not already in it. Ensure you follow the steps emitted in the output.

### 3. Advanced usage:

To install the EBCLI, `bundled_installer` runs `ebcli_installer.py`. `ebcli_installer.py` has the following capabilities:

  - to install a **specific version** of the EBCLI:

    ```bash
    python scripts/ebcli_installer.py --version 3.14.13
    ```

  - to install the EBCLI with a specific **version of Python** (such a `python` need not even exist in `$PATH`)

    ```bash
    python scripts/ebcli_installer.py --python-installation /path/to/some/python/on/your/computer
    ```

  - to install the EBCLI **from source** (Git repository, .tar, .zip)
    ```bash
    python scripts/ebcli_installer.py --ebcli-source /path/to/awsebcli.zip

    python scripts/ebcli_installer.py --ebcli-source /path/to/EBCLI/codebase/on/your/computer
    ```
  - to install the EBCLI at a **specific location** rather than the standard `.ebcli-virtual-env` directory in the user's home.

    ```bash
    python scripts/ebcli_installer.py --location /path/to/ebcli/installation/location
    ```

Run the following to view the help text associated with `ebcli_installer.py`:

```bash
python scripts/ebcli_installer.py --help
```

### 4. FAQs:

------

#### 4.1. Can I skip Python installation?

**Yes.** If you already have Python installed on your system, you can simply run the following after step `2.1.`:

On **Bash** and **Zsh**:

```bash
python aws-elasticbeanstalk-cli-setup/scripts/ebcli_installer.py
```

On **PowerShell** and **CMD Prompt**:

```bash
python .\aws-elasticbeanstalk-cli-setup\scripts\ebcli_installer.py
```

#### 4.2. For the **seasoned Python developer**, what is the advantage of this mode of installation over regular `pip` inside a `virtualenv`:

Even within a `virtualenv`, a developer might find the need to install multiple packages whose dependencies are in conflict. For instance, at various points in time, the AWSCLI and the EBCLI have been conflict with one another due to their dependency on `botocore`. [One such instance](https://github.com/aws/aws-cli/issues/3550) was particularly egregious. When there are conflicts, users have to bear the onus of managing separate virtualenvs for each of the conflicting packages, or find a combination of the packages devoid of conflicts. Both these workarounds become unmanageable over time and as the number of packages that are in conflict increases.

#### 4.3. On OS X (or Linux systems with `brew`), is this better than `brew install awsebcli`?

**Yes**, for a few reasons:

  - the Beanstalk team does not have control over how `brew` operates. So installation problems will take time to fix as will general queries to be responded to.
  - the `brew install ...` mechanism does not solve the problem of dependency conflicts, which is a primary goal of this project.

#### 4.3. For the developers who are **new to Python**, does this mode of installation pose challenges?

The opinion of the Beanstalk team is "**No**".

Aside from the problem described in `3.2.`, developers new to Python are often confused by the presence of multiple Pythons, and `pip` executables on their system. A common problem that such developers encounter is where they install `eb` with one `pip` executable (presumably using the `sudo` prefix) only to find that only to find that no `eb`-related commands work because the correct set of directories is not properly referenced.

Normally, for such developers, usage of `virtualenv` is the correct path forward, however, this becomes yet another hurdle before executing with `eb`.

Another common problem is where users install Python and `pip` though means not recommended by AWS Documentation such as arbitrary PPAs on Ubuntu, or similar unmaintained sources that lack scrutiny.

#### 4.4. Can I execute the Bash scripts in a Cygwin, git-bash and other Bash-like shells on Windows?

**No**. At this time, we do not directly support execution on Bash-like environments on Windows. Please use PowerShell or CMD Prompt to install. You may add to `$PATH` the location of the `eb` and `Python` executables.

#### 4.5. Can I execute the Bash scripts in a `fish` shell?
**Yes**, but only if you have Bash on your computer. At this time we do not provide specific guidance on how to set `$PATH` in Fish, however, Fish has [detailed documentation](https://fishshell.com/docs/current/tutorial.html#tut_path) for this purpose.

#### 4.6. I already have Python installed. Can I still execute `bundled_installer`?

**Yes**. It is safe to execute `bundled_installer` even if you already have a Python installed. The installer will simply skip reinstallation.

#### 4.7. I already have the EBCLI installed. Can I still execute `ebcli_installer.py`?

**Yes**.

There are two cases to consider:

- `ebcli_installer.py` was previously run, thereby creating `.ebcli-virtual-env` in the user's home directory (or the user's choice of a directory indicated through the `--location` argument). In this case, the EBCLI will simply overwrite `.ebcli-virtual-env` and attempt to install the latest version of the EBCLI in the virtualenv within it.

- `eb` is in `$PATH`, however, it was not installed by `ebcli_installer.py`. In this case, the installer will install `eb` within `.ebcli-virtual-env` in the user's home directory (or the user's choice of a directory indicated through the `--location` argument) and prompt the user to prefix `/path-to/.ebcli-virtual-env/executables` to `$PATH`. Until you perform this action, the older `eb` executable will continue to be referenced when you type `eb`.

#### 4.8. How does `ebcli_installer.py` work?

Upon executing the Python script, it will:

- create a virtualenv exclusive to the `eb` installation
- install `eb` inside that virtualenv
- generate inside the `<installation-location>/executables` directory:
  - a `.py` wrapper for `eb` on Linux/OS X
  - `.bat` and `.ps1` wrappers for `eb` on Windows
- upon completion, you will be prompted to add `<installation-location>/executables` to `$PATH`, only if the directory is not already in it.

#### 4.8. How does `bundled_installer` work?

- On OS X/Linux, `bundled_installer` uses the extremely popular [`pyenv` project](https://github.com/pyenv/pyenv) to install the latest version of Python 3.7.
- On Windows, it simply downloads the MSI installer of the latest Python from Python's website and silently installs it.

#### 4.9. Are there dependency problems that this mode of installation does not solve?

Unfortunately, **yes**.

Suppose the dependencies of `eb`, say `Dep A` and `Dep B` are in conflict. Because `pip` lacks dependency management capabilities, the resulting `eb` installation might be rendered defective.

#### 4.10. Is it okay to use Python 2.7 to install the EBCLI?

**Yes**, however, note that Python 2.7 will become deprecated on the 1st of January 2020, beyond which point, security updates will cease to come through.

Besides, the latest minor version series, Python 3.7, offers significant improvements over the Python 2.7 series, and it is highly recommended that you use Python 3.7 for the purposes of testing, even though the Beanstalk team tests the EBCLI against Python 2.7.

### 5. License

This library is licensed under the Mozilla Public License Version 2.0.
