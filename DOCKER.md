
# Docker Overview

## What is Docker?

Docker is designed to provide an isolated environment in which to run an application(similar to a virtual machine). It does this through containers. Containers allow a developer to package up an application with all of the parts it needs, such as libraries and other dependencies, and ship it all out as one package.

## What is a Dockerfile?

Dockerfiles enable you to create your own images. A Dockerfile describes the software that makes up an image. Dockerfiles contain a set of instructions that specify what environment to use and which commands to run.

## Installation

Your computer may already have Docker installed, so check first!

[Installation Guide](https://docs.docker.com/get-docker/)

## Local Development

Converting images to pyramid tiff is done in [process_images.py](img_src/process_images.py). This python3 script can be run separately outside of docker. However, if you want to run the script inside the container here's how...

1. start Docker
2. open a terminal window build and tag the Dockerfile image

```bash
# build and tag the Dockerfile image
cd /some/path/to/marble-images/docker
docker build -t marble:latest .

# open the image in a shell
docker run -it --entrypoint /bin/bash marble:latest

# from here youre in the image!
# Vips installed - to verify...
which vips
# should yield this output - /usr/bin/vips
# the process_images.py script is in /usr/local/bin
# roam around and when youre all done type exit!
```

## Additional Commands

- To list existing images with their tag

```bash
docker images
```

- To delete a single image

```bash
  docker rmi <image id>
```

note: image id is provided from the list step
