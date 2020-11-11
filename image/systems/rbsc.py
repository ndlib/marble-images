import os
import json
from queue import Queue
import threading
from pyvips import Image, Error
import shared.config as config
import shared.aws_utility as aws_utility
import time


counter = 0
skip = ['TEMP_BPP_1001-052.jpg',
    'TEMP_BPP_1001-029-c3.jpg',
    'TEMP_BPP_1001-087.jpg',
    'TEMP_BPP_1001-090-c3.jpg',
    'TEMP_BPP_1001-091-c2.jpg',
    'TEMP_BPP_1001-117.jpg',
    'TEMP_BPP_1001-137-c1.jpg',
    'TEMP_BPP_1001-140.jpg',
    'TEMP_BPP_1001-145-c1.jpg',
    'TEMP_BPP_1001-150-c2.jpg',
    'TEMP_BPP_1001-156.jpg',
    'TEMP_BPP_1001-209-c2.jpg',
    'TEMP_BPP_1001-212.jpg',
    'TEMP_BPP_1001-223-c1.jpg',
    'TEMP_BPP_1001-244-c2.jpg',
    'TEMP_BPP_1001-269.jpg',
    'TEMP_BPP_1001-227-c3.jpg',
    'TEMP_BPP_1001-290.jpg',
    'TEMP_BPP_1001-300.jpg',
    'TEMP_BPP_1001-313-c2.jpg',
    'TEMP_EPH_5007-05a.jpg',
    'TEMP_EPH_5007-10b.jpg',
    'TEMP_EPH_5007-34b.jpg']


def _list_changes() -> list:
    kwargs = {'Bucket': config.PROCESS_BUCKET, 'Prefix': 'rbsc/'}
    data = []
    while True:
        resp = aws_utility.list_files(**kwargs)
        if resp['KeyCount'] == 0:
            return {}
        for obj in resp['Contents']:
            local_file = os.path.basename(obj["Key"])
            aws_utility.download_file(config.PROCESS_BUCKET, obj["Key"], local_file)
            with open(local_file) as json_file:
                data.append(json.load(json_file))
            json_file.close()  # force close before deletion
            os.remove(local_file)
            aws_utility.delete_file(config.PROCESS_BUCKET, obj["Key"])
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
    return data


def _reprocess_image(queue: Queue) -> None:
    while not queue.empty():
        img_data = queue.get()
        tif_filename = os.path.basename(img_data["key"])
        tif_filename = f"{os.path.splitext(tif_filename)[0]}.tif"
        local_file = f"TEMP_{os.path.basename(img_data['key'])}"
        if local_file not in skip:
            aws_utility.download_file(config.RBSC_BUCKET, img_data["key"], local_file)
            image = _preprocess_image(local_file)
            if image:
                image.tiffsave(tif_filename, tile=True, pyramid=True, compression=config.COMPRESSION_TYPE,
                    tile_width=config.PYTIF_TILE_WIDTH, tile_height=config.PYTIF_TILE_HEIGHT, \
                    xres=config.DPI_VALUE, yres=config.DPI_VALUE) # noqa
                os.remove(local_file)
                key = f"{img_data['path']}{tif_filename}"
                aws_utility.upload_file(config.IMAGE_BUCKET, key, tif_filename)
                os.remove(tif_filename)
        global counter
        counter += 1
        queue.task_done()
    # print(f"{image.get_fields()}")  # image fields, including exif


def _preprocess_image(local_file: str) -> Image:
    try:
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
    except Error as e:
        image = None
        print(f"Error on image - {local_file} - {e}")
    return image


def process_rbsc_changes():
    jobs = Queue()
    for img_data in _list_changes():
        jobs.put(img_data)

    start_time = time.time()
    for i in range(config.MAX_THREADS):
        threading.Thread(target=_reprocess_image, args=(jobs,)).start()

    jobs.join()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"RBSC PROCESSED {counter} IMAGES")
    print(f"ELAPSED TIME = {elapsed_time} seconds")


if __name__ == "__main__":
    process_rbsc_changes()
