# Overview
This system watches for image files to be uploaded(typically via AWS Storage Gateway) to an s3 bucket, notes the image data, retrieves the image, transforms it to a pyramid tiff, and uploads it to an s3 bucket.

## Prerequisites
This stack depends on the [marble network stack](https://github.com/ndlib/marble-blueprints/blob/master/docs/shared-infrastructure.md) being setup.

## Details
This system watches for files to be uploaded(typically via AWS Storage Gateway) to a bucket.
```
HTTP PUT lantern.png arn:aws:s3:::source_bucket/digital/isaac_gala/
```
Once uploaded a lambda will trigger and write pertinent image information into an s3 queue.
```
lantern.json
{
    key: 'digital/isaac_gala/lantern.png',
    id: 'isaac_gala',
    eTag: 'C345ASDFJ385JKLJASF6823',
}

HTTP PUT lantern.png arn:aws:s3:::process_bucket/rbsc/lantern.json
```
At a set interval(currently every quarter of an hour) CloudWatch will start-up an ECS task to download all json files in rbsc in the process bucket, download corresponding image files within, generate pyramid tiffs, and upload those resulting files to the image bucket.

# Development:
To model and provision AWS application resources this repository uses the AWS CDK(typescript). Additional scripts are written in python.

## AWS CDK Overview
### Welcome to your CDK TypeScript project!
You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`MarbleImagesStack`).

The `cdk.json` file tells the CDK Toolkit how to execute your app.

### Useful commands

 * `npm run build`   compile typescript to js
 * `npm run watch`   watch for changes and compile
 * `npm run test`    perform the jest unit tests
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk synth`       emits the synthesized CloudFormation template


## Python3 Overview
### Description
Both the ECS task and lambda are written in python3. It's useful to follow the setup steps below to run/test these scripts locally in a virtual python environment.

### Installation
1. Setup pyenv - https://github.com/pyenv/pyenv
2. Setup aws-cdk - https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html

Use venv - https://docs.python.org/3/library/venv.html

venv is included in the Python standard library and requires no additional installation. Additional details in deployment.

### Testing
Use unittest - https://docs.python.org/3/library/unittest.html

Tests should be placed in test/unit

To execute all test: `python run_all_tests.py`
### Dependencies
#### Development Dependencies
1. Review the src/dev-requirements.txt
#### Production Dependencies
1. Review the lambda/requirements.txt to install/update lambda development packages
2. Review the ECS Dockerfile for python production packages
### Deployment
#### Local deployment to AWS
1. Setup virtual env
    1. python -m venv .env
    2. source .env/bin/activate
2. Run local deployment
    1. local-deploy.sh mystackname
3. Exit virtual env
    1. deactivate

## Image processing with Docker and AWS ECS
Here we aim to take images from various sources and generate [pyramid tiffs](https://iipimage.sourceforge.io/documentation/images/). To accomplish this we'll launch a Fargate instance running our [Dockerfile](Dockerfile),and generate the pyramid tiff using the [pyvips](https://pypi.org/project/pyvips/) library. Additional details found [here](DOCKER.md).
