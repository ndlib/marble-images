import config
import json


def download_file(bucket: str, remote_file: str, local_file: str) -> None:
    config.S3_RESOURCE.Bucket(bucket).download_file(remote_file, local_file)


def upload_file(bucket: str, remote_file: str, local_file: str) -> None:
    config.S3_RESOURCE.meta.client.upload_file(local_file, bucket, remote_file)


def delete_file(bucket: str, remote_file: str) -> None:
    config.S3_RESOURCE.Object(bucket, remote_file).delete()


def list_files(**kwargs: dict) -> dict:
    return config.S3_CLIENT.list_objects_v2(**kwargs)


def get_gdrive_creds() -> dict:
    gdrive_creds = config.SSM_CLIENT.get_parameter(Name=config.GDRIVE_CRED, WithDecryption=True)
    return json.loads(gdrive_creds['Parameter']['Value'])
