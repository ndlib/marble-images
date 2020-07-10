#!/bin/bash
magenta=`tput setaf 5`
reset=`tput sgr0`

echo "${magenta}----- BUILD -----${reset}"

cd deploy/blueprints
# if [ ${LOCAL_DEPLOY:=false} = true ]
# then
#   APPROVAL='any-change'
# else
#   APPROVAL='never'
# fi
APPROVAL='never'

echo -e "\n${blue}Deploying with cdk...${reset}"
npm run -- cdk deploy $STACK_NAME \
  -c stage="$STAGE" \
  -c contact=$CONTACT \
  -c owner=$OWNER \
  -c lambdaCodePath='../../src' \
  -c dockerfilePath='../../docker' \
  --require-approval=never \
  --exclusively "$@" \
  || { echo "CDK deployment failed"; exit 1; }