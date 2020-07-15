import boto3
import os

# AWS SETTINGS
AWS_REGION = 'us-east-1'
S3_CLIENT = boto3.client('s3')
S3_RESOURCE = boto3.resource('s3')
SSM_CLIENT = boto3.client('ssm', region_name=AWS_REGION)

# IMAGE CONSTANTS
DEFAULT_MAX_HEIGHT = 4000.0
DEFAULT_MAX_WIDTH = 4000.0
COPYRIGHT_MAX_HEIGHT = 560.0
COPYRIGHT_MAX_WIDTH = 843.0
PYTIF_TILE_WIDTH = 512
PYTIF_TILE_HEIGHT = 512
COMPRESSION_TYPE = 'deflate'

# BUCKET SETTINGS
# Image sources and destination buckets
RBSC_BUCKET = os.environ['RBSC_BUCKET']
IMAGE_BUCKET = os.environ['IMAGE_BUCKET']
PROCESS_BUCKET = os.environ['PROCESS_BUCKET']

# GOOGLE DRIVE SETTINGS
# AWS SSM key containing Google Drive credentials
GDRIVE_CRED = "/all/marble/google/credentials"

# TESTING SETTINGS
# Set to True to pull files locally and runthrough image processing
TESTING = False
TEST_DIR = "../../tests"
EMBARK_DIR = f"{TEST_DIR}/embark"
