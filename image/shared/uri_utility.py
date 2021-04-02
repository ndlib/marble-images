""" Common code to perform basic uri calls """
import requests
from . import logger


def download_file(local_file: str, uri: str) -> bool:
    downloaded = True
    try:
        with open(local_file, 'wb') as image_file:
            image_file.write(requests.get(uri).content)
    except IOError as ioe:
        logger.error(f"Error retrieving {uri} - {ioe}")
        downloaded = False
    return downloaded
