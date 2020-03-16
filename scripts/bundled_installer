#!/usr/bin/env bash
# ******************************************************************
#   ABOUT
# ******************************************************************
#
# This script installs:
#
#   - the latest (or close to it) Python
#   - the latest version of the EBCLI
export PYTHON_VERSION="3.7.2"
export PYENV_ROOT=${PYENV_ROOT:-"$HOME/.pyenv"}
export PYENV_BIN="$PYENV_ROOT/versions/$PYTHON_VERSION/bin"
BASH_PROFILE="$HOME/.bash_profile"
ZSHENV="$HOME/.zshrc"
PYTHON_ALREADY_IN_PATH=false

function change_to_scripts_directory() {
    SCRIPTS_DIRECTORY=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

    cd "$SCRIPTS_DIRECTORY"
}

function echo_with_colors_inverted()
{
    MESSAGE=$1
    echo -e "\033[7m$MESSAGE\033[0m"
}

function exit_if_return_code_is_non_zero() {
    if [[ $? -ne 0 ]] ; then
        echo_with_indentation "Exiting due to failure"

        exit $?
    fi
}

function install_python() {
    echo ""
    echo_with_colors_inverted "=============================================="
    echo_with_colors_inverted "I. Installing Python                          "
    echo_with_colors_inverted "=============================================="
    if [ -f python_installer ]; then
        SUPPRESS_PATH_EXPORT_MESSAGE=true
        source ./python_installer SUPPRESS_PATH_EXPORT_MESSAGE
        exit_if_return_code_is_non_zero
    fi
}

function install_ebcli() {
    echo ""
    echo_with_colors_inverted "=============================================="
    echo_with_colors_inverted "II. Creating self-contained EBCLI installation"
    echo_with_colors_inverted "=============================================="
    if [ -f ebcli_installer.py ]; then
        ${PYENV_BIN}/python ./ebcli_installer.py \
            --python-installation ${PYENV_BIN}/python \
            --virtualenv-executable ${PYENV_BIN}/virtualenv
        exit_if_return_code_is_non_zero
    fi
}

function print_python_path_export_message() {
    if [ "${PYTHON_ALREADY_IN_PATH}" = false ]; then
        print_path_export_instructions
    fi
}

change_to_scripts_directory
install_python
install_ebcli
print_python_path_export_message
