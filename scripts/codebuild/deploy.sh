#!/bin/bash
magenta=`tput setaf 5`
reset=`tput sgr0`

echo "${magenta}----- DEPLOY -----${reset}"

cdk deploy --ci --require-approval=never "$@" || { echo "CDK deployment failed"; exit 1; }