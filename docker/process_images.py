#!/usr/bin/python3

import os
import json
import boto3
from pyvips import Image


S3_CLIENT = boto3.client('s3')
S3_RESOURCE = boto3.resource('s3')
MAX_IMG_HEIGHT = 4000.0
MAX_IMG_WIDTH = 4000.0
PYTIF_TILE_WIDTH = 512
PYTIF_TILE_HEIGHT = 512
COMPRESSION_TYPE = 'deflate'
RBSC_BUCKET = os.environ['RBSC_BUCKET']
IMAGE_BUCKET = os.environ['IMAGE_BUCKET']
PROCESS_BUCKET = os.environ['PROCESS_BUCKET']


def list_changed_images() -> dict:
    kwargs = {'Bucket': PROCESS_BUCKET, 'Prefix': 'rbsc/'}
    while True:
        resp = S3_CLIENT.list_objects_v2(**kwargs)
        if resp['KeyCount'] == 0:
            return {}
        for obj in resp['Contents']:
            local_file = os.path.basename(obj["Key"])
            S3_RESOURCE.Bucket(PROCESS_BUCKET).download_file(obj["Key"], local_file)
            with open(local_file) as json_file:
                yield json.load(json_file)
            json_file.close()  # force close before deletion
            os.remove(local_file)
            S3_RESOURCE.Object(PROCESS_BUCKET, obj["Key"]).delete()
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


def process_image(img_data: dict) -> None:
    tif_filename = os.path.basename(img_data["key"])
    tif_filename = f"{os.path.splitext(tif_filename)[0]}.tif"
    local_file = f"TEMP_{os.path.basename(img_data['key'])}"
    S3_RESOURCE.Bucket(RBSC_BUCKET).download_file(img_data["key"], local_file)
    image = _preprocess_image(local_file)
    image.tiffsave(tif_filename, tile=True, pyramid=True, compression=COMPRESSION_TYPE,
        tile_width=PYTIF_TILE_WIDTH, tile_height=PYTIF_TILE_HEIGHT)  # noqa
    S3_RESOURCE.Bucket(RBSC_BUCKET).download_file(img_data["key"], local_file)
    os.remove(local_file)
    key = f"{img_data['id']}/{tif_filename}"
    S3_RESOURCE.meta.client.upload_file(tif_filename, IMAGE_BUCKET, key)
    os.remove(tif_filename)
    # print(f"{image.get_fields()}")  # image fields, including exif


def _preprocess_image(local_file: str) -> Image:
    image = Image.new_from_file(local_file, access='sequential')
    if image.height > MAX_IMG_HEIGHT or image.width > MAX_IMG_WIDTH:
        if image.height >= image.width:
            shrink_by = image.height / MAX_IMG_HEIGHT
        else:
            shrink_by = image.width / MAX_IMG_WIDTH
        print(f'Resizing original image by: {shrink_by}')
        print(f'Original image height: {image.height}')
        print(f'Original image width: {image.width}')

        image = image.shrink(shrink_by, shrink_by)
    return image


if __name__ == "__main__":
    for img_data in list_changed_images():
        process_image(img_data)
