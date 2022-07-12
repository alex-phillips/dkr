#!/bin/bash

set -e

if [[ -z "${ANSIBLE_VAULT_PASSWORD}" ]]; then
    bw get password "Ansible vault key"
    exit 0
fi

echo $ANSIBLE_VAULT_PASSWORD
