#!/bin/bash
blue=`tput setaf 4`
magenta=`tput setaf 5`
reset=`tput sgr0`

echo "${magenta}----- PRE-BUILD -----${reset}"

# clear out existing artifacts from previous builds
rm -r -f ./deploy/blueprints && mkdir -p ./deploy

# run unit tests and abort on any failures
# echo -e "\n${blue}Running unit tests...${reset}"
# yarn test || { echo "Unit Tests Failed"; exit 1; }

# copy the blueprints repo into deploy/blueprints so we can run the deploy from there after building
echo -e "\n${blue}Copying blueprints...${reset}"
cp -R -f $BLUEPRINTS_DIR/ ./deploy/blueprints || { echo "Failed to copy blueprints. Make sure you have marble_images_blueprints checked out."; exit 1; }
# install packages in the blueprints folder
chmod -R 755 ./deploy/blueprints/*
pushd ./deploy/blueprints
./setup.sh || { echo "Failed to set up blueprints."; exit 1; }
popd

# create Sentry release and associate commits
# yarn sentry-cli releases new marble_images@$VERSION || { echo "Failed to create sentry release."; exit 1; }
# yarn sentry-cli releases set-commits marble_images@$VERSION --commit "$GITHUB_REPO@$VERSION" || { echo "Failed to associate commits with sentry release."; exit 1; }