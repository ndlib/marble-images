import os
import json
from queue import Queue
import threading
from pyvips import Image
import botocore
import shared.config as config
import shared.aws_utility as aws_utility
import shared.google_utility as google_utility
import time

counter = 0
# establish a one-time connection to Google Drive
gdrive_creds = aws_utility.get_gdrive_creds()
# gdrive_conn = google_utility.establish_connection(gdrive_creds)


def _list_changes() -> dict:
    try:
        local_file = 'google.json'
        remote_file = 'google.json'
        aws_utility.download_file(config.PROCESS_BUCKET, remote_file, local_file)
        with open(local_file) as json_file:
            data = json.load(json_file)
        json_file.close()  # force close before deletion
        os.remove(local_file)
        aws_utility.delete_file(config.PROCESS_BUCKET, remote_file)
        return data.values()
    except botocore.exceptions.ClientError as err:
        status = err.response["ResponseMetadata"]["HTTPStatusCode"]
        errcode = err.response["Error"]["Code"]
        if status == 404:
            print(f"Remote file - {remote_file} not found. No work to do.")
        else:
            print(f"Unexpected err - {status}:{errcode}")
        return {}


def _reprocess_image(queue: Queue) -> None:
    while not queue.empty():
        img_data = queue.get()
        tif_filename = f"{os.path.splitext(img_data['id'])[0]}.tif"
        local_file = f"TEMP_{img_data['id']}"
        conn = google_utility.establish_connection(gdrive_creds)
        if google_utility.download_file(conn, img_data["fileId"], local_file):
            global counter
            counter += 1
            image = _preprocess_image(img_data, local_file)
            image.tiffsave(tif_filename, tile=True, pyramid=True, compression=config.COMPRESSION_TYPE,
                tile_width=config.PYTIF_TILE_WIDTH, tile_height=config.PYTIF_TILE_HEIGHT, \
                xres=config.DPI_VALUE, yres=config.DPI_VALUE) # noqa
            os.remove(local_file)
            key = f"{img_data['collectionId']}/{tif_filename}"
            aws_utility.upload_file(config.IMAGE_BUCKET, key, tif_filename)
            os.remove(tif_filename)
        queue.task_done()
        # print(f"{image.get_fields()}")  # image fields, including exif


def _preprocess_image(img_data: dict, local_file: str) -> Image:
    image = Image.new_from_file(local_file, access='sequential')
    max_height = config.DEFAULT_MAX_HEIGHT
    max_width = config.DEFAULT_MAX_WIDTH
    if img_data.get("copyrightStatus", "").lower() == "copyright":
        max_height = config.COPYRIGHT_MAX_HEIGHT
        max_width = config.COPYRIGHT_MAX_WIDTH
    if image.height > max_height or image.width > max_width:
        if image.height >= image.width:
            shrink_by = image.height / max_height
        else:
            shrink_by = image.width / max_width
        print(f"Image resizing - {img_data['id']}")
        print(f"Resizing original image by: {shrink_by}")
        print(f"Original image height: {image.height}")
        print(f"Original image width: {image.width}")
        image = image.shrink(shrink_by, shrink_by)
    return image


def process_embark_changes():
    jobs = Queue()
    for img_data in _list_changes():
        jobs.put(img_data)

    start_time = time.time()
    for i in range(config.MAX_THREADS):
        threading.Thread(target=_reprocess_image, args=(jobs,)).start()

    jobs.join()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"PROCESSED {counter} IMAGES")
    print(f"ELAPSED TIME = {elapsed_time} seconds")


if __name__ == "__main__":
    process_embark_changes()
