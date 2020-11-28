import os

# MULTITHREADING
if 'MAX_THREADS' in os.environ:
    MAX_THREADS = os.environ['MAX_THREADS']
else:
    MAX_THREADS = 4

# IMAGE CONSTANTS
DEFAULT_MAX_HEIGHT = 4000.0
DEFAULT_MAX_WIDTH = 4000.0
COPYRIGHT_MAX_HEIGHT = 560.0
COPYRIGHT_MAX_WIDTH = 843.0
PYTIF_TILE_WIDTH = 512
PYTIF_TILE_HEIGHT = 512
# pixels per millimeter; equiv. 300 DPI
DPI_VALUE = 11.812
COMPRESSION_TYPE = 'deflate'

# BUCKET SETTINGS
# Image sources and destination buckets
RBSC_BUCKET = os.environ['RBSC_BUCKET']
IMAGE_BUCKET = os.environ['IMAGE_BUCKET']
PROCESS_BUCKET = os.environ['PROCESS_BUCKET']
JSON_PROCESS_DIR = 'rbsc/'

# EC2/LOCAL SETTINGS
# local processing dir
EC2_PROCESS_DIR = '/process/rbsc'

# LOGGER SETTINGS
LOG_DEBUG = False
LOG_INFO = True
LOG_ERROR = True
