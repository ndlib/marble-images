import os
import json
from queue import Queue
import threading
from pyvips import Image, Error
import shared.config as config
import shared.logger as logger
import shared.aws_utility as aws_utility
import time


counter = 0


def _list_changes() -> list:
    kwargs = {'Bucket': config.PROCESS_BUCKET, 'Prefix': config.JSON_PROCESS_DIR}
    data = []
    while True:
        resp = aws_utility.list_files(**kwargs)
        if resp['KeyCount'] == 0:
            return {}
        for obj in resp['Contents']:
            data.append(obj['Key'])
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
    return data


def _reprocess_image(queue: Queue) -> None:
    while not queue.empty():
        img_data = queue.get()
        img_data = _retrieve_file_data(img_data)
        tif_filename = os.path.basename(img_data["key"])
        tif_filename = f"{os.path.splitext(tif_filename)[0]}.tif"
        local_file = f"TEMP_{os.path.basename(img_data['key'])}"
        aws_utility.download_file(config.RBSC_BUCKET, img_data["key"], local_file)
        logger.debug(f'Processing {local_file}')
        image = _preprocess_image(img_data, local_file)
        if image:
            image.tiffsave(tif_filename, tile=True, pyramid=True, compression=config.COMPRESSION_TYPE,
                tile_width=config.PYTIF_TILE_WIDTH, tile_height=config.PYTIF_TILE_HEIGHT, \
                xres=config.DPI_VALUE, yres=config.DPI_VALUE) # noqa
            key = f"{img_data['path']}{tif_filename}"
            aws_utility.upload_file(config.IMAGE_BUCKET, key, tif_filename)
            os.remove(tif_filename)
        os.remove(local_file)
        aws_utility.delete_file(config.PROCESS_BUCKET, f"{config.JSON_PROCESS_DIR}{os.path.splitext(tif_filename)[0]}.json")
        logger.debug(f'Completed {local_file}')
        global counter
        counter += 1
        queue.task_done()
    # print(f"{image.get_fields()}")  # image fields, including exif


def _retrieve_file_data(remote_file: str) -> dict:
    local_file = os.path.basename(remote_file)
    aws_utility.download_file(config.PROCESS_BUCKET, remote_file, local_file)
    with open(local_file) as json_file:
        data = json.load(json_file)
    os.remove(local_file)
    return data


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
            logger.debug(f"Image resizing - {local_file}")
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


def process_rbsc_changes():
    jobs = Queue()
    logger.info("GATHERING RBSC IMAGES TO PROCESS")
    for img_data in _list_changes():
        jobs.put(img_data)
    logger.info(f"{jobs.qsize()} IMAGES TO PROCESS")

    start_time = time.time()
    for i in range(config.MAX_THREADS):
        threading.Thread(target=_reprocess_image, args=(jobs,)).start()

    jobs.join()
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"RBSC PROCESSED {counter} IMAGES")
    logger.info(f"ELAPSED TIME = {elapsed_time} seconds")


if __name__ == "__main__":
    process_rbsc_changes()
