import config
import os
import json
from pyvips import Image
import aws_utility


def _list_changes() -> dict:
    kwargs = {'Bucket': config.PROCESS_BUCKET, 'Prefix': 'rbsc/'}
    while True:
        resp = aws_utility.list_files(**kwargs)
        if resp['KeyCount'] == 0:
            return {}
        for obj in resp['Contents']:
            local_file = os.path.basename(obj["Key"])
            aws_utility.download_file(config.PROCESS_BUCKET, obj["Key"], local_file)
            with open(local_file) as json_file:
                yield json.load(json_file)
            json_file.close()  # force close before deletion
            os.remove(local_file)
            aws_utility.delete_file(config.PROCESS_BUCKET, obj["Key"])
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


def _reprocess_image(img_data: dict) -> None:
    tif_filename = os.path.basename(img_data["key"])
    tif_filename = f"{os.path.splitext(tif_filename)[0]}.tif"
    local_file = f"TEMP_{os.path.basename(img_data['key'])}"
    aws_utility.download_file(config.RBSC_BUCKET, img_data["key"], local_file)
    image = _preprocess_image(local_file)
    image.tiffsave(tif_filename, tile=True, pyramid=True, compression=config.COMPRESSION_TYPE,
        tile_width=config.PYTIF_TILE_WIDTH, tile_height=config.PYTIF_TILE_HEIGHT)  # noqa
    os.remove(local_file)
    key = f"{img_data['id']}/{tif_filename}"
    aws_utility.upload_file(config.IMAGE_BUCKET, key, tif_filename)
    os.remove(tif_filename)
    # print(f"{image.get_fields()}")  # image fields, including exif


def _preprocess_image(local_file: str) -> Image:
    image = Image.new_from_file(local_file, access='sequential')
    if image.height > config.DEFAULT_MAX_HEIGHT or image.width > config.DEFAULT_MAX_WIDTH:
        if image.height >= image.width:
            shrink_by = image.height / config.DEFAULT_MAX_HEIGHT
        else:
            shrink_by = image.width / config.DEFAULT_MAX_WIDTH
        print(f'Resizing original image by: {shrink_by}')
        print(f'Original image height: {image.height}')
        print(f'Original image width: {image.width}')
        image = image.shrink(shrink_by, shrink_by)
    return image.copy(xres=config.DPI_VALUE, yres=config.DPI_VALUE)


def process_rbsc_changes():
    for img_data in _list_changes():
        _reprocess_image(img_data)


if __name__ == "__main__":
    process_rbsc_changes()
