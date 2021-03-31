import os
from queue import Queue
import threading
from pyvips import Image, Error
import shared.config as config
import shared.logger as logger
import shared.graphql_utility as gql
import shared.aws_utility as aws_utility
import shared.google_utility as google_utility
import time
import requests


counter = 0
gdrive_creds = aws_utility.get_gdrive_creds()


def _reprocess_image(queue: Queue) -> None:
    while not queue.empty():
        img_data = queue.get()
        img_data["filePath"] = f"{os.path.splitext(img_data['filePath'])[0]}.tif"
        tif_filename = os.path.basename(img_data["filePath"])
        local_file = f"TEMP_{os.path.basename(img_data['id'])}"
        logger.info(f"Processing {img_data['id']}")
        _download_source_file(img_data, local_file)
        image = _preprocess_image(img_data, local_file)
        if image:
            image.tiffsave(tif_filename, tile=True, pyramid=True, compression=config.COMPRESSION_TYPE,
                tile_width=config.PYTIF_TILE_WIDTH, tile_height=config.PYTIF_TILE_HEIGHT, \
                xres=config.DPI_VALUE, yres=config.DPI_VALUE) # noqa
            _upload_files(img_data, local_file, tif_filename)
            gql.update_processed_date(img_data['id'])
            os.remove(tif_filename)
        os.remove(local_file)
        logger.debug(f'Completed {local_file}')
        global counter
        counter += 1
        queue.task_done()
    # print(f"{image.get_fields()}")  # image fields, including exif


def _preprocess_image(img_data: dict, local_file: str) -> Image:
    try:
        image = Image.new_from_file(local_file, access='sequential')
        max_height = config.DEFAULT_MAX_HEIGHT
        max_width = config.DEFAULT_MAX_WIDTH
        if img_data["copyrightStatus"] and \
                img_data["copyrightStatus"].lower() == "copyright":
            max_height = config.COPYRIGHT_MAX_HEIGHT
            max_width = config.COPYRIGHT_MAX_WIDTH
        if image.height > max_height or image.width > max_width:
            if image.height >= image.width:
                shrink_by = image.height / max_height
            else:
                shrink_by = image.width / max_width
            logger.debug(f"Resizing {img_data['id']} by {shrink_by}")
            image = image.shrink(shrink_by, shrink_by)
    except Error as pye:
        image = None
        logger.error(f"VIPs error - {pye.message}")
    return image


def _download_source_file(img_data, local_file):
    if img_data["sourceType"] == config.S3:
        s3_info = f"s3://{img_data['sourceBucketName']}/"
        src_img = img_data["sourceFilePath"].replace(s3_info, '')
        try:
            aws_utility.download_file(img_data["sourceBucketName"], src_img, local_file)
        except Exception as e:
            print(f"local_file = '{local_file}'")
            print(f"img_data = '{img_data}'")
            print(f"src bucket = '{img_data['sourceFilePath']}'")
            print(f"src_img = '{src_img}'")
            print(e)
    elif img_data["sourceType"] in [config.URI, config.CURATE]:
        with open(local_file, 'wb') as image_file:
            image_file.write(requests.get(img_data['sourceUri']).content)
    else:
        conn = google_utility.establish_connection(gdrive_creds)
        google_utility.download_file(conn, img_data["sourceUri"][41:-5], local_file)


def _upload_files(img_data, local_file, tif_filename):
    if local_file.endswith(".pdf"):
        key = img_data["filePath"].replace(".tif", ".pdf")
        aws_utility.upload_file(config.IMAGE_BUCKET, key, local_file)
    aws_utility.upload_file(config.IMAGE_BUCKET, img_data["filePath"], tif_filename)


def process_image_changes(data: list):
    jobs = Queue()
    for img_data in data:
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
