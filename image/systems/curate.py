import os
import json
from queue import Queue
import threading
from pyvips import Image, Error
import botocore
import shared.config as config
import shared.logger as logger
import shared.aws_utility as aws_utility
import requests
import time

counter = 0
gdrive_creds = aws_utility.get_gdrive_creds()


def _list_changes() -> dict:
    try:
        local_file = 'curate.json'
        remote_file = 'curate.json'
        aws_utility.download_file(config.PROCESS_BUCKET, remote_file, local_file)
        with open(local_file) as json_file:
            data = json.load(json_file)
        os.remove(local_file)
        aws_utility.delete_file(config.PROCESS_BUCKET, remote_file)
        return data.values()
    except botocore.exceptions.ClientError as err:
        status = err.response["ResponseMetadata"]["HTTPStatusCode"]
        errcode = err.response["Error"]["Code"]
        if status == 404:
            logger.error(f"Remote file - {remote_file} not found. No work to do.")
        else:
            logger.error(f"Unexpected err - {status}:{errcode}")
        return {}


def _reprocess_image(queue: Queue) -> None:
    while not queue.empty():
        img_data = queue.get()
        filename = img_data['title']
        tif_filename = f"{os.path.splitext(filename)[0]}.tif"
        local_file = f"TEMP_{filename}"
        logger.debug(f"filename - {filename}")
        logger.debug(f"local - {local_file}")
        logger.debug(f"tif - {tif_filename}")
        with open(local_file, 'wb') as image_file:
            image_file.write(requests.get(img_data['filePath']).content)
        image = _preprocess_image(img_data, local_file)
        if image:
            image.tiffsave(tif_filename, tile=True, pyramid=True, compression=config.COMPRESSION_TYPE,
                tile_width=config.PYTIF_TILE_WIDTH, tile_height=config.PYTIF_TILE_HEIGHT, \
                xres=config.DPI_VALUE, yres=config.DPI_VALUE) # noqa
            key = f"{tif_filename}"
            aws_utility.upload_file(config.IMAGE_BUCKET, key, tif_filename)
            os.remove(tif_filename)
        os.remove(local_file)
        global counter
        counter += 1
        queue.task_done()
        # print(f"{image.get_fields()}")  # image fields, including exif


def _preprocess_image(img_data: dict, local_file: str) -> Image:
    try:
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
            logger.debug(f"Image resizing - {img_data['id']}")
            logger.debug(f"Resizing {local_file} by: {shrink_by}")
            logger.debug(f"Original {local_file} height: {image.height}")
            logger.debug(f"Original {local_file} width: {image.width}")
            image = image.shrink(shrink_by, shrink_by)
            logger.debug(f"Updated {local_file} height: {image.height}")
            logger.debug(f"Updated {local_file} width: {image.width}")
    except Error as pye:
        image = None
        logger.error(f"VIPs error - {pye.message}")
    return image


def process_curate_changes():
    jobs = Queue()
    logger.info("GATHERING CURATE IMAGES TO PROCESS")
    for img_data in _list_changes():
        jobs.put(img_data)
    logger.info(f"{jobs.qsize()} IMAGES TO PROCESS")

    start_time = time.time()
    for i in range(config.MAX_THREADS):
        threading.Thread(target=_reprocess_image, args=(jobs,)).start()

    jobs.join()
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"PROCESSED {counter} IMAGES")
    logger.info(f"ELAPSED TIME = {elapsed_time} seconds")


if __name__ == "__main__":
    process_curate_changes()
