#!/usr/bin/env python
import boto3
import os
import json
import glob
import shared.config as config


s3 = boto3.resource('s3')
rbsc_bucket = s3.Bucket(config.RBSC_BUCKET)
process_bucket = s3.Bucket(config.PROCESS_BUCKET)

# valid prefixes; only process objects in these directories
valid_dirs = ['digital/', 'collections/']
# valid_dirs = ['digital/MARBLE-images/MAN_002205202/']
# valid_dirs = ['digital/civil_war/letters/images/read/']


# valid image extensions
# there is a lot of "junk" in valid_dirs only process objects with these extensions
valid_image_ext = ['jpeg', 'jpg', 'bmp', 'tif', 'tiff', 'png', 'eps', 'pdf']
# valid_image_ext = ['pdf']

for file in rbsc_bucket.objects.all():
    if file.key.startswith(tuple(valid_dirs)):
        if file.key.endswith(tuple(valid_image_ext)):
            path, filename = os.path.split(file.key)
            path += "/"
            filename, ext = os.path.splitext(filename)
            # if filename.startswith('MSN-EA'):
            if not filename.startswith('.'):
                data = {}
                data['key'] = file.key
                data['path'] = path
                with open(f'{filename}.json', 'w') as fp:
                    json.dump(data, fp)

count = 0
for file in glob.glob("*.json"):
    remote_file = f"rbsc/{file}"
    count += 1
    print(f"uploading {count} - {file}")
    process_bucket.upload_file(file, remote_file)
    os.remove(file)
