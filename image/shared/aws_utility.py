import json
import boto3


AWS_REGION = 'us-east-1'
S3_CLIENT = boto3.client('s3')
S3_RESOURCE = boto3.resource('s3')
SSM_CLIENT = boto3.client('ssm', region_name=AWS_REGION)


def download_file(bucket: str, remote_file: str, local_file: str) -> None:
    S3_RESOURCE.Bucket(bucket).download_file(remote_file, local_file)


def upload_file(bucket: str, remote_file: str, local_file: str) -> None:
    S3_RESOURCE.meta.client.upload_file(local_file, bucket, remote_file)


def delete_file(bucket: str, remote_file: str) -> None:
    S3_RESOURCE.Object(bucket, remote_file).delete()


def list_files(**kwargs: dict) -> dict:
    return S3_CLIENT.list_objects_v2(**kwargs)


def get_gdrive_creds() -> dict:
    # AWS SSM key containing Google Drive credentials
    GDRIVE_CRED = "/all/marble/google/credentials"
    gdrive_creds = SSM_CLIENT.get_parameter(Name=GDRIVE_CRED, WithDecryption=True)
    return json.loads(gdrive_creds['Parameter']['Value'])
