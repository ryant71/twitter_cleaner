#!/bin/bash

[[ -z "$1" ]] && { echo "Usage: $0 <path> <value>"; exit; }
[[ -z "$2" ]] && { echo "Usage: $0 <path> <value>"; exit; } || path=$1; value=$2

aws --profile=zappa ssm put-parameter \
    --name "${path}" \
    --value "${value}" \
    --type "SecureString" \
    --key-id "alias/aws/ssm" \
    --overwrite
