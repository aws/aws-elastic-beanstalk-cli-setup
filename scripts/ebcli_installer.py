"""
This script generates a self-contained installation of the EBCLI.

Prerequisites:

    1. Python + pip (preferably Python 3.7, although Python 2.7, 3.4, 3.5,
       3.6, and 3.7 are supported)
    2. virtualenv
    3. Bash/Zsh on Linux/MacOS ; PowerShell/CMD Prompt on Windows

Usage:

    To execute script:

        # let the script find Python in PATH
        python /<location to script>/bundled_installer.py

        # specify Python executable
        python scripts/bundled_installer.py -p ~/.pyenv/versions/3.7.2/bin/python

    To view help text:

        python /<location to script>/bundled_installer.py --help

"""
import argparse
import os
import subprocess
import sys


if sys.version_info < (3, 0):
    input = raw_input


EBCLI_INSTALLER_STAMP = '.ebcli_installer_stamp'

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(PROJECT_ROOT, 'VERSION')) as version_file:
    EBCLI_INSTALLER_VERSION = version_file.read().strip()


EXECUTABLE_WRAPPERS = {
    'bat': '\n'.join(
        [
            '@echo off',
            'REM Safe way to consolidate CMD line arguments to pass to `eb`',
            'set args=%1',
            'shift',
            ':start',
            'if [%1] == [] goto done',
            'set args=%args% %1',
            'shift',
            'goto start',
            ':done',
            '',
            'REM activate virtualenv, call eb and deactivate virtualenv',
            'CALL {bin_location}\\activate.bat',
            '@start CALL {bin_location}\\eb.exe %args%',
            '@echo off',
            'deactivate'
        ]
    ),
    'ps1': '\n'.join(
        [
            '{bin_location}\\activate.ps1',
            '{bin_location}\\eb $args',
            'deactivate'
        ]
    ),
    'py': """#!/usr/bin/env python
import subprocess
import sys


def _exec_cmd(args):
    \"\"\"
    Function invokes the real `eb` executable within the EBCLI-specifc
    virtualenv. `KeyboardInterrupt`s are in this parent process as showing
    the stacktrace associated with this script has no information for
    the user and is confusing.

    Note that any of the stack traces the subprocess (the real `eb` process)
    wishes to print will be printed to STDOUT. As such, this wrapper strives
    to be completely non-intervening.

    In the event of a `KeyboardInterrupt`s, it is possible that the child might
    not have returned leaving the returncode `None`. In this situation, it
    is prudent to wait for the subprocess to exit normally.
    
    Outside `KyeboardInterrupts`s, it is unclear whether it is possible for
    the return code of the subprocess to remain None. In all such cases, the
    wrapper will assume a failure and return a non-zero exit code.
    \"\"\"
    p = subprocess.Popen(args)
    try:
        p.communicate()
    except KeyboardInterrupt:
        p.wait()

    if p.returncode is None:
        print('Assuming failure because `eb` returned with an indeterminate exit-code.')
        return 1

    return p.returncode


activate_this = "{bin_location}/activate_this.py"

if sys.version_info < (3, 0):
    execfile(activate_this, dict(__file__=activate_this))
else:
    exec(open(activate_this).read(), dict(__file__=activate_this))

exit(_exec_cmd(['{bin_location}/eb'] + sys.argv[1:]))
"""
}


PATH_EXPORTER_SCRIPTS = {
    'bat': 'WSCript {path_exporter_script}\n',
    'vbs': '\n'.join(
        [
            'Set wshShell = CreateObject( "WScript.Shell" )',
            'Set wshUserEnv = wshShell.Environment( "USER" )',
            'Dim pathVar',
            'pathVar = wshUserEnv( "Path" )',
            '',
            'If InStr(pathVar, "{new_location}") = 0 Then',
            'wshUserEnv( "Path" ) = wshUserEnv( "Path" ) + ";{new_location}"',
            'End If',
            '',
            'Set wshUserEnv = Nothing',
            'Set wshShell   = Nothing',
            '',
        ]
    )
}


INSTALLATION_SUCCESS_MESSAGE_WITH_EXPORT_RECOMMENDATION__NON_WINDOWS = """
    Note: To complete installation, ensure `eb` is in PATH. You can ensure this by executing:

    1. Bash:

       echo 'export PATH="{eb_location}:$PATH"' >> ~/.bash_profile && source ~/.bash_profile

    2. Zsh:

       echo 'export PATH="{eb_location}:$PATH"' >> ~/.zshenv && source ~/.zshenv
"""


INSTALLATION_SUCCESS_MESSAGE_WITH_EXPORT_RECOMMENDATION__WINDOWS = """
To complete installation, ensure `eb` is in PATH. You can ensure this by executing:


    1. CMD Prompt:

        cmd.exe /c "{path_exporter_bat}"

    2. PowerShell:

        & "{path_exporter}"


NOTE: Additionally, you would need to **restart this shell**
"""


MINIMAL_INSTALLATION_SUCCESS_MESSAGE = """Success!

EBCLI has been installed.
"""


PIP_AND_VIRTUALENV_NOT_FOUND = ' '.join(
    [
        'ERROR: Could not find "pip" and "virtualenv" installed.'
        'Ensure "pip" and "virtualenv" are installed and that they'
        'are in PATH before executing this script.'
    ]
)


VIRTUALENV_DIR_NAME = '.ebcli-virtual-env'


VIRTUALENV_NOT_FOUND = ' '.join(
    [
        'ERROR: Could not find and "virtualenv" installed. Ensure'
        'virtualenv is installed and that it is in PATH before executing'
        'this script.'
    ]
)


GREEN_COLOR_CODE = 10


RED_COLOR_CODE = 9


YELLOW_COLOR_CODE = 11


class ArgumentError(Exception):
    pass


class Step(object):
    """
    Class labels an installation Step and is expected to be invoked as
    the decorator of Step functions.
    """
    Step_number = 1

    def __init__(self, title):
        self.title = title

    def __call__(self, func):
        def wrapped(*args):
            title = '{0}. {1}'.format(Step.Step_number, self.title)
            marker = '*' * len(title)
            print('\n{0}\n{1}\n{0}'.format(marker, title))
            return_value = func(*args)
            Step.Step_number += 1

            return return_value
        return wrapped


@Step('Activating virtualenv')
def _activate_virtualenv(virtualenv_location):
    """
    Function activates virtualenv, ".ebcli-virtual-env", created apriori for the
    rest of the lifetime of this script.
    :param virtualenv_location: the relative or absolute path to the location
                          where the virtualenv, ".ebcli-virtual-env", was
                          created by this script.
    :return None
    """
    if sys.platform.startswith('win32'):
        activate_script_directory = 'Scripts'
    else:
        activate_script_directory = 'bin'

    activate_this_path = os.path.join(
        virtualenv_location,
        VIRTUALENV_DIR_NAME,
        activate_script_directory,
        'activate_this.py'
    )

    if sys.version_info < (3, 0):
        execfile(activate_this_path, dict(__file__=activate_this_path))
    else:
        exec(open(activate_this_path).read(), dict(__file__=activate_this_path))


@Step('Finishing up')
def _announce_success(virtualenv_location, hide_export_recommendation):
    """
    Function checks whether the installation location is already in PATH.

    If the location is not in PATH, the user is recommended that the location
    be added to PATH along with the precise commands and instructions to do so.

    The commands are specific to OS + shell combinations:

        1. Windows + PowerShell: execute a visual basic script to amend PATH
        2. Windows + CMD Prompt: execute a BAT script to invoke the above visual
                                 basic script
        3. UNIX + Bash: echo PATH modifier to .bash_profile and source it
        4. UNIX + Zsh: echo PATH modifier to .zshenv and source it

    On Windows, users will be expected to run either a visual basic script
    (if using PowerShell) or a Batch script (which wraps the above visual basic
    script) to amend their PATH variable. This function also generates these
    scripts but only when `virtualenv_location` is not already in PATH.

    :param virtualenv_location: the relative or absolute path to the location
                                where the virtualenv, ".ebcli-virtual-env", was
                                created.
    :param hide_export_recommendation: boolean indicating whether or not to
                                       hide PATH export instructions. Useful
                                       when invoked from shells that allow
                                       modifying system PATH variable
                                       conveniently.
    :return: None
    """
    new_location = _eb_wrapper_location(virtualenv_location)

    if new_location in os.environ['PATH']:
        content = MINIMAL_INSTALLATION_SUCCESS_MESSAGE.format(
            path=new_location,
            new_eb_path=os.path.join(new_location, 'eb')
        )

        _print_success_message(content)
    else:
        path_exporter = os.path.join(new_location, 'path_exporter.vbs')
        path_exporter_wrapper = os.path.join(new_location, 'path_exporter.bat')
        if sys.platform.startswith('win32'):
            with open(path_exporter, 'w') as file:
                file.write(
                    PATH_EXPORTER_SCRIPTS['vbs'].format(
                        new_location=new_location
                    )
                )

            with open(path_exporter_wrapper, 'w') as file:
                file.write(
                    PATH_EXPORTER_SCRIPTS['bat'].format(
                        path_exporter_script=path_exporter
                    )
                )

                _print_success_message('Success!')

                if not hide_export_recommendation:
                    _print_recommendation_message(
                        INSTALLATION_SUCCESS_MESSAGE_WITH_EXPORT_RECOMMENDATION__WINDOWS
                            .format(
                            path_exporter_bat=path_exporter_wrapper,
                            path_exporter=path_exporter
                        )
                    )
        else:
            _print_success_message('Success!')
            _print_recommendation_message(
                INSTALLATION_SUCCESS_MESSAGE_WITH_EXPORT_RECOMMENDATION__NON_WINDOWS
                    .format(eb_location=new_location)
            )


def _print_in_foreground(message, color_number):
    """
    Function prints a given `message` on the terminal in the foreground. `color_number`
    is a number between and including 0 and 255. FOr a list of color codes see:

        https://misc.flogisoft.com/bash/tip_colors_and_formatting#background1

    On Windows, `color_number` is rejected, and hence not used. At present, PowerShell
    is able to recognize ANSI/VT100 escape sequences, however, CMD prompt is not.

    :param message: a string to print in the foreground on the terminal
    :param color_number: an integer between and including 0 and 255 representing
                         a color
    :return: None
    """
    if sys.platform.startswith('win32'):
        import colorama
        colorama.init()
        if color_number == GREEN_COLOR_CODE:
            print(colorama.Fore.GREEN + message)
        elif color_number == RED_COLOR_CODE:
            print(colorama.Fore.RED + message)
        elif color_number == YELLOW_COLOR_CODE:
            print(colorama.Fore.LIGHTYELLOW_EX + message)
        else:
            print(message)
        print(colorama.Style.RESET_ALL)

    else:
        # Courtesy https://misc.flogisoft.com/bash/tip_colors_and_formatting
        print(
            "\033[38;5;{color_number}m{message}\033[0m".format(
                color_number=color_number,
                message=message,
            )
        )

def _print_recommendation_message(message):
    _print_in_foreground(message, YELLOW_COLOR_CODE)


def _print_success_message(message):
    _print_in_foreground(message, GREEN_COLOR_CODE)


def _print_error_message(message):
    _print_in_foreground(message, RED_COLOR_CODE)


@Step('Creating exclusive virtualenv for EBCLI')
def _create_virtualenv(
        virtualenv_executable,
        virtualenv_location,
        python_installation,
        quiet
):
    """
    Function creates a new virtualenv at path `virtualenv_location`
    using the Python at path `python_installation`, if one is provided.
    If `virtualenv_location` is not provided, the user's HOME directory
    is assumed as the location to create the virtualenv in. If
    `python_installation` is not provided, virtualenv attempts to
    find a Python in $PATH to use. If no Python executable is found in
    PATH, and yet if execution managed to get this far, it could mean:
        - the Python executable was made unavailable between the start
          of execution of this script and now
        - this script was executed with a Python executable not in PATH

    Prior to creation of the virtualenv, this function checks whether
    one by name `.ebcli-virtual-env` already exists. If this directory
    was not created by this installer, installation halts and the user
    is asked to either delete the directory or to specify an alternate
    location using the `--location` argument of this script.

    In all other cases, `.ebcli-virtual-env` is (re)created and a file
    to denote that the installer created `.ebcli-virtual-env` is added.

    :param virtualenv_executable: the name of the virtualenv executable
    :param virtualenv_location: the relative or absolute path to the location
                                where the virtualenv, ".ebcli-virtual-env", must
                                be created.
    :param python_installation: the relative or absolute path to the location
                                of a Python executable to use to create the
                                virtualenv with
    :param quiet: whether to display the output of virtualenv creation in
                  STDOUT or not

    :return the relative or absolute path to the location where the
            virtualenv, ".ebcli-virtual-env", was created.
    """
    virtualenv_location = virtualenv_location or _user_local_directory()
    virtualenv_directory = os.path.join(virtualenv_location, VIRTUALENV_DIR_NAME)
    python_installation = python_installation or sys.executable

    if (
        os.path.exists(virtualenv_directory)
        and not _directory_was_created_by_installer(virtualenv_directory)
    ):
        _error(
            'Installation cannot proceed because "{virtualenv_location}" already exists '
                'but was not created by this EBCLI installer.'
            '\n'
            '\n'
            'You can either:\n'
            '\n'
            '1. Delete "{virtualenv_location}" after verifying you don\'t need it; OR\n'
            '2. Specify an alternate location to install the EBCLI and its artifacts in '
                'using the `--location` argument of this script .\n'.format(
                virtualenv_location=virtualenv_directory
            )
        )

    virtualenv_args = [
        virtualenv_executable or 'virtualenv',
        '"{}"'.format(virtualenv_directory)
    ]

    python_installation and virtualenv_args.extend(
        ['-p', '"{}"'.format(python_installation)]
    )

    if _exec_cmd(virtualenv_args, quiet) != 0:
        exit(1)

    _add_ebcli_stamp(virtualenv_directory)

    return virtualenv_location


@Step('Locating virtualenv installation')
def _locate_virtualenv_executable():
    """
    Function attempts to find the location at which `virtualenv` is installed.

    If such a location is found, the function returns normally. Otherwise, the
    function further proceeds to check for `pip` and informs the user that either
    or both of `pip` and `virtualenv` are missing.
    :param quiet: a boolean indicating whether minimal output printed should be
                  non-verbose, minimal.
    :return: None
    :side-effect: script will exit with a non-0 return code if a
                  virtualenv and/or pip executables haven't been found.
    """
    virtualenv_executables = ['virtualenv']

    if sys.platform.startswith('win32'):
        virtualenv_executables += ['virtualenv.cmd', 'virtualenv.exe']
    virtualenv_executable = None
    for _virtualenv_executable in virtualenv_executables:
        if _executable_found(_virtualenv_executable, True):
            virtualenv_executable = _virtualenv_executable

    if not virtualenv_executable:
        if not _pip_executable_found(True):
            print(PIP_AND_VIRTUALENV_NOT_FOUND)
        else:
            print(VIRTUALENV_NOT_FOUND)

    return virtualenv_executable


@Step('Creating EB wrappers')
def _generate_ebcli_wrappers(virtualenv_location):
    """
    Function generates:
        - a Python wrapper for the awsebcli on Unix/Linux computers; OR
        - Powershell and CMD Prompt wrappers on Windows

    within a "executables" directory inside ".ebcli-virtual-env". Further,
    on Unix/Linux, the wrapper is made an executable.

    :param virtualenv_location: the relative or absolute path to the location
                          where the virtualenv, ".ebcli-virtual-env",
                          exists.
    :return None
    """
    executables_dir = _eb_wrapper_location(virtualenv_location)
    not os.path.exists(executables_dir) and os.mkdir(executables_dir)

    ebcli_script_path = os.path.join(executables_dir, 'eb')
    ebcli_ps1_script_path = os.path.join(executables_dir, 'eb.ps1')
    ebcli_bat_script_path = os.path.join(executables_dir, 'eb.bat')

    if sys.platform.startswith('win32'):
        with open(ebcli_ps1_script_path, 'w') as script:
            script.write(_powershell_script_body(virtualenv_location))

        with open(ebcli_bat_script_path, 'w') as script:
            script.write(_bat_script_body(virtualenv_location))
    else:
        with open(ebcli_script_path, 'w') as script:
            script.write(_python_script_body(virtualenv_location))
        _exec_cmd(['chmod', '+x', ebcli_script_path], False)


@Step('Installing EBCLI')
def _install_ebcli(quiet, version, ebcli_source):
    """
    Function installs the awsebcli presumably within the virtualenv,
    ".ebcli-virtual-env", created and activated by this script apriori.
    If `version` is passed, the specific version of the EBCLI is installed.

    The presence of `version` and `ebcli_source` will lead to an exception
    as they represent two different ways of installing the EBCLI.

    :param quiet: whether to display the output of awsebcli installation to
                  the terminal or not
    :param version: the specific version of awsebcli to install
    :return None
    """
    if ebcli_source:
        install_args = ['pip', 'install', '{}'.format(ebcli_source.strip())]
    elif version:
        install_args = ['pip', 'install', 'awsebcli=={}'.format(version.strip())]
    else:
        install_args = [
            'pip', 'install', 'awsebcli',
            '--upgrade',
            '--upgrade-strategy', 'eager',
        ]
    returncode = _exec_cmd(install_args, quiet)

    if returncode != 0:
        exit(returncode)


def _add_ebcli_stamp(virtualenv_directory):
    """
    Function adds a stamp in the form of a file, `EBCLI_INSTALLER_STAMP`
    to recognize during future executions of this script that it created
    it.

    :param virtualenv_directory: The directory where the EBCLI and its artifacts
    will be installed
    :return: None
    """
    with open(
        os.path.join(
            virtualenv_directory,
            EBCLI_INSTALLER_STAMP
        ),
        'w'
    ) as file:
        file.write('\n')


def _bat_script_body(virtualenv_location):
    """
    Function returns a CMD Prompt (bat) script which essentially will
    wrap the `eb` executable such that the executable is invoked within
    the virtualenv, ".ebcli-virtual-env", created apriori.
    :param virtualenv_location: the relative or absolute path to the location
                          where the virtualenv, ".ebcli-virtual-env", was
                          created.
    :return: None
    """
    return EXECUTABLE_WRAPPERS['bat'].format(
        bin_location=_original_eb_location(virtualenv_location)
    )


def _directory_was_created_by_installer(virtualenv_directory):
    """
    Function checks whether `virtualenv_directory` was previously created
    by this script.

    :param virtualenv_directory: The directory where the EBCLI and its
                                 artifacts will be installed.
    :return: Boolean indicating whether `virtualenv_directory` was created
             by this script or not.
    """
    return os.path.exists(
        os.path.join(
            virtualenv_directory,
            EBCLI_INSTALLER_STAMP
        )
    )


def _eb_wrapper_location(virtualenv_location):
    """
    Function returns the location of the directory within the virtualenv,
    ".ebcli-virtual-env", where the wrapper of the `eb` executable should
    be installed. This is `executables` on all OSes.
    :param virtualenv_location: the relative or absolute path to the location
                          where the virtualenv, ".ebcli-virtual-env", was
                          created.
    :return: the location of the directory within the virtualenv where
             the wrapper of the `eb` executable should be installed.
    """
    return os.path.join(
        os.path.abspath(virtualenv_location),
        VIRTUALENV_DIR_NAME,
        'executables'
    )


def _ensure_not_inside_virtualenv_to_begin_with():
    """
    Function checks whether the `VIRTUAL_ENV` environment variable has
    already been set in effect checking whether a virtualenv is presently
    active in the context of this shell. If so, this script is exited
    immediately with a non-0 exit code.

    Rationale:
        1. when a virtualenv is entered current `PATH` is saved
        2. real `PATH` is amended so that the `bin`/`Scripts` directory inside
           the virtualenv is at the head of PATH
        3. it is possible that the user (or a script such as this one) may
           further amend the head of PATH.
        4. all of the changes made to PATH will be lost upon deactivation
           of the virtualenv thereby leading to unpredictable behaviour.

    :return: None
    :side-effect: script will exit with a non-0 return code if a
                  virtualenv has already been activated within the shell.
    """
    if os.environ.get('VIRTUAL_ENV'):
        _error('This script cannot be executed inside a virtual environment.')


def _error(message):
    _print_error_message('ERROR: {}'.format(message))
    exit(1)


def _exec_cmd(args, quiet):
    """
    Function invokes `subprocess.Popen` in the `shell=True` mode and returns
    the return code of the subprocess.

    :param args: the args to pass to `subprocess.Popen`
    :param quiet: Whether to avoid displaying output of the subprocess to
                  STDOUT
    :return: the return code of the subprocess
    """
    stdout = subprocess.PIPE if quiet else None
    p = subprocess.Popen(
        ' '.join(args),
        stdout=stdout,
        stderr=stdout,
        shell=True
    )

    p.communicate()

    return p.returncode


def _executable_found(executable, quiet):
    """
    Function attempts to locate `executable` and returns True
    if it can find it installed, else False.
    :param executable: The executable to find on the computer
    :return: True/False
    """
    return _exec_cmd([executable, '--version'], quiet) == 0


def _user_local_directory():
    """
    Function attempts to find the home of the current user. On Unix/Linux,
    this is $HOME or "~". On Windows, this can be one of $USERPROFILE,
    $LOCALAPPDATA, or $APPDATA. In the event that the home cannot be
    determined, execution will continue normally.
    :return: the home of the current user
    """
    if sys.platform.startswith('win32'):
        identified_location = (
            os.environ.get('USERPROFILE')
            or os.environ.get('LOCALAPPDATA')
            or os.environ.get('APPDATA')
        )
    else:
        identified_location = os.environ.get('HOME')

    if not identified_location:
        _error(
            "Could not determine user's HOME directory. "
            "Pass a location explicitly using the `--location` argument."
        )
    return identified_location


def _original_eb_location(virtualenv_location):
    """
    Function returns the location of the directory within the virtualenv,
    ".ebcli-virtual-env", where the original `eb` executable is expected
    to be found. This is `bin` on Unix/Linux and `Scripts` on Windows.
    :param virtualenv_location: the relative or absolute path to the location
                          where the virtualenv, ".ebcli-virtual-env", was
                          created.
    :return: the location of the directory within the virtualenv where
             the original `eb` executable is expected to be found
    """
    if sys.platform.startswith('win32'):
        scripts_directory = 'Scripts'
    else:
        scripts_directory = 'bin'

    return os.path.join(
        os.path.abspath(virtualenv_location),
        VIRTUALENV_DIR_NAME,
        scripts_directory
    )


def _parse_arguments():
    """
    Function creates an `ArgumentParser`, parses arguments, and returns
    the parsed arguments.

    :return: an instance of argparse.Namespace representing the command-line
             arguments passed by the user.
    """
    parser = argparse.ArgumentParser(
        description='EBCLI installer {}\n\n'
                    'This program creates an isolated virtualenv solely meant for invoking '
                    '`eb` within.'.format(EBCLI_INSTALLER_VERSION),
        usage='python {file_name} [optional arguments]'.format(file_name=__file__),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-e', '--virtualenv-executable',
        help="path to the virtualenv installation to use to create the EBCLI's virtualenv"
    )
    parser.add_argument(
        '-i', '--hide-export-recommendation',
        action='store_true',
        help="boolean to hide recommendation to modify PATH"
    )
    parser.add_argument(
        '-l', '--location',
        help='location to store the awsebcli packages and its dependencies in'
    )
    parser.add_argument(
        '-p', '--python-installation',
        help='path to the python installation under which to install the '
             'awsebcli and its \ndependencies'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='enable quiet mode to display only minimal, necessary output'
    )
    parser.add_argument(
        '-s', '--ebcli-source',
        help='filesystem path to a Git repository of the EBCLI, or a .zip or .tar file of \n'
             'the EBCLI source code; useful when testing a development version of the EBCLI.'
    )
    parser.add_argument(
        '-v', '--version',
        help='version of EBCLI to install'
    )

    arguments = parser.parse_args()

    if arguments.version and arguments.ebcli_source:
        raise ArgumentError(
            '"--version" and "--ebcli-source" cannot be used together '
            'because they represent two distinct sources of the EBCLI.'
        )
    return arguments


def _pip_executable_found(quiet):
    """
    Function attempts to locate one of pip, pip2, and pip3 and returns True
    if it can find one of them, else False.

    In addition to the form `pip<x>`, `pip` may also be installed as `pip<x.y>`.
    We avoid checking for these as the likelihood that `pip` got installed as
    `pip<x.y>` but not as `pip<x>`
    :return: True/False
    """
    pip_executables = ['pip', 'pip2', 'pip3']
    if sys.platform.startswith('win32'):
        pip_executables += [
            'pip.exe', 'pip2.exe', 'pip3.exe',
            'pip.cmd', 'pip2.cmd', 'pip3.cmd',
        ]
    for executable in pip_executables:
        if _executable_found(executable, quiet):
            if not quiet:
                print('Found {}'.format(executable))
            return True


def _powershell_script_body(virtualenv_location):
    """
    Function returns a Powershell (PS1) script which essentially will
    wrap the `eb` executable such that the executable is invoked within
    the virtualenv, ".ebcli-virtual-env", created apriori.
    :param virtualenv_location: the relative or absolute path to the location
                          where the virtualenv, ".ebcli-virtual-env", was
                          created.
    :return: None
    """
    return EXECUTABLE_WRAPPERS['ps1'].format(
        bin_location=_original_eb_location(virtualenv_location)
    )


def _python_script_body(virtualenv_location):
    """
    Function returns a Python script which essentially will wrap
    the `eb` executable such that the executable is invoked within
    the virtualenv, ".ebcli-virtual-env", created apriori.
    :param virtualenv_location: the relative or absolute path to the location
                          where the virtualenv, ".ebcli-virtual-env", was
                          created.
    :return: None
    """
    return EXECUTABLE_WRAPPERS['py'].format(
        bin_location=_original_eb_location(virtualenv_location)
    )


if __name__ == '__main__':
    _ensure_not_inside_virtualenv_to_begin_with()
    arguments_context = _parse_arguments()
    virtualenv = (
        arguments_context.virtualenv_executable
        or _locate_virtualenv_executable()
    )
    virtualenv_location = _create_virtualenv(
        virtualenv,
        arguments_context.location,
        arguments_context.python_installation,
        arguments_context.quiet
    )
    _activate_virtualenv(virtualenv_location)
    _install_ebcli(
        arguments_context.quiet,
        arguments_context.version,
        arguments_context.ebcli_source
    )
    _generate_ebcli_wrappers(virtualenv_location)
    _announce_success(
        virtualenv_location,
        arguments_context.hide_export_recommendation
    )