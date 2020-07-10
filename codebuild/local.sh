#!/bin/bash

# export the blueprints directory to an environment variable so we know where to find the infrastructure code
# to do the deploy. For local deploy, this assumes that the marble-images-blueprints repo is a "sibling" to this
# project in your folder structure.
export BLUEPRINTS_DIR="../marble-images-blueprints"
export LOCAL_DEPLOY=true

# provide some friendly defaults so the user does not need to assuming they are deploying a test build
export STAGE=${STAGE:="test"}
export STACK_NAME=${STACK_NAME:="marbleImages-${STAGE}"}
export OWNER=${OWNER:=$(id -un)}
export CONTACT=${CONTACT:=$OWNER@nd.edu}
export GITHUB_REPO=$(git config --get remote.origin.url | sed 's/.*\/\([^ ]*\/[^.]*\).*/\1/') # ndlib/marble-images

./scripts/codebuild/install.sh || { exit 1; }
./scripts/codebuild/pre_build.sh || { exit 1; }
./scripts/codebuild/build.sh || { exit 1; }
./scripts/codebuild/post_build.sh || { exit 1; }