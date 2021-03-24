# Overview

This system polls AWS AppSync for image files that have been changed, retrieves the image, transforms it to a pyramid tiff, and uploads it to an s3 bucket.

## Prerequisites

This stack depends on the [marble network stack](https://github.com/ndlib/marble-blueprints/blob/master/docs/shared-infrastructure.md) being setup.

## Details

At a set interval(daily at 5:30am EDT) CloudWatch will start-up a ECS task to query an AWS AppSync API endpoint for a list of changed files, download the image files, generate pyramid tiffs, and upload those resulting files to the image bucket.

## Development

To model and provision AWS resources this repository uses the AWS CDK(typescript). Additional scripts are written in python3. It's useful to follow the setup steps below to run/test these scripts locally in a virtual python environment.

### Installation

1. Setup pyenv - <https://github.com/pyenv/pyenv>
2. Setup aws-cdk - <https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html>

Use venv - <https://docs.python.org/3/library/venv.html>

venv is included in the Python standard library and requires no additional installation. Additional details in deployment.

### Dependencies

#### Production Dependencies

1. Review the ECS [Dockerfile](Dockerfile) for python production packages

### Local Development

1. Setup virtual env
    1. python -m venv .env
    2. source .env/bin/activate
2. Local development/testing
3. Exit virtual env
    1. deactivate

## Image processing with Docker and AWS ECS

Here we aim to take images from various sources and generate [pyramid tiffs](https://iipimage.sourceforge.io/documentation/images/). To accomplish this we'll launch an ECS Fargate instance running our [Dockerfile](Dockerfile),and generate the pyramid tiff using the [pyvips](https://pypi.org/project/pyvips/) library. Additional details found [here](DOCKER.md).

## Utilities

~~1. [Rerun images](image/utilities/rerun_rbsc_images.py) - execute the below command which will mark these images as needing to be reprocessed (Modify the valid_dirs variable to really narrow down which files are reran). Once that's completed use the AWS console CloudWatch section to modify your scheduled task to run to actually do the reprocessing work.
    1. ```python RBSC_BUCKET=my_source_bucket PROCESS_BUCKET=my_process_bucket rerun_rbsc_images.py```~~
