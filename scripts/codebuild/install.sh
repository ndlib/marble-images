#!/bin/bash
blue=`tput setaf 4`
magenta=`tput setaf 5`
reset=`tput sgr0`

echo "${magenta}----- INSTALL -----${reset}"

# install yarn and packages
npm install -g yarn || { echo "Npm install failed"; exit 1; }
yarn install || { echo "Yarn install failed"; exit 1; }