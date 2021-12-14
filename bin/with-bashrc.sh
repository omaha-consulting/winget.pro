#!/bin/bash
# Following an idea similar to https://web.archive.org/web/20130526045634/http:/
# /sjsnyder.com/managing-virtualenv-apps-with-supervisor

# Calculate the home directory from $(id -u). The motivation for this is that
# Supervisor only sets the UID.
export USER=$(getent passwd | cut -d : -f 1,3 | grep ":$(id -u)$" | cut -d : -f 1)
export HOME=$(getent passwd $USER | cut -d : -f 6)
source $HOME/.bashrc
exec $@