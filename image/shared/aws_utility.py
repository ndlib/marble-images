import json
import boto3
from botocore.exceptions import ClientError
from . import config
from . import logger


AWS_REGION = 'us-east-1'
S3_CLIENT = boto3.client('s3')
S3_RESOURCE = boto3.resource('s3')
SSM_CLIENT = boto3.client('ssm', region_name=AWS_REGION)


def download_file(bucket: str, remote_file: str, local_file: str) -> bool:
    downloaded = True
    try:
        S3_RESOURCE.Bucket(bucket).download_file(remote_file, local_file)
    except ClientError as ce:
        logger.error(f"Error retrieving {remote_file} - {ce}")
        downloaded = False
    return downloaded


def upload_file(bucket: str, remote_file: str, local_file: str) -> None:
    S3_RESOURCE.meta.client.upload_file(local_file, bucket, remote_file)


def delete_file(bucket: str, remote_file: str) -> None:
    S3_RESOURCE.Object(bucket, remote_file).delete()


def list_files(**kwargs: dict) -> dict:
    return S3_CLIENT.list_objects_v2(**kwargs)


def get_gdrive_creds() -> dict:
    # AWS SSM key containing Google Drive credentials
    GDRIVE_CRED = "/all/marble/google/credentials"
    return get_multiple_ssm_values(GDRIVE_CRED)


def get_graphql_api_key() -> dict:
    return get_single_ssm_value(config.GRAPHQL_API_KEY_KEY_PATH)


def get_graphql_api_url() -> dict:
    return get_single_ssm_value(config.GRAPHQL_API_URL_KEY_PATH)


def get_single_ssm_value(ssm_key: str) -> str:
    value = SSM_CLIENT.get_parameter(Name=ssm_key, WithDecryption=True)
    return value['Parameter']['Value']


def get_multiple_ssm_values(ssm_key: str) -> dict:
    values = SSM_CLIENT.get_parameter(Name=ssm_key, WithDecryption=True)
    return json.loads(values['Parameter']['Value'])
