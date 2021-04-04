"""tracker of image processing stats"""
from . import config
from . import logger


class Statistic(object):
    count = 0
    errors = {}

    @classmethod
    def attempted(cls, delta=1):
        cls.count += delta

    @classmethod
    def download_err(cls, img_data: dict):
        err_type = "DOWNLOAD"
        if err_type not in cls.errors:
            cls.errors[err_type] = []
        if img_data["sourceType"] == config.S3:
            cls.errors[err_type].append(img_data["sourceFilePath"])
        else:
            cls.errors[err_type].append(img_data["sourceUri"])

    @classmethod
    def vips_err(cls, img_data: dict):
        err_type = "VIPS"
        if err_type not in cls.errors:
            cls.errors[err_type] = []
        cls.errors[err_type].append(img_data["id"])

    @classmethod
    def summary(cls):
        logger.info("IMAGE PROCESS SUMMARY:")
        logger.info(f"\tATTEMPTED: {cls.count}")
        logger.info(f"\tERRORS: {cls.errors}")
        for k, v in cls.errors.items():
            logger.info(f"\t{len(v)} {k} ERRORS")
