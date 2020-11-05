import os
import json
import boto3
from urllib.parse import unquote_plus


def handler(event, context):
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    etag = event["Records"][0]["s3"]["object"]["eTag"]
    path = key.rsplit('/', 1)[0] + "/"
    data = {'key': key, 'eTag': etag, 'path': path}
    filename = os.path.basename(key)
    filename = os.path.splitext(filename)[0]
    os.chdir("/tmp")
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    bucket = os.environ['PROCESS_BUCKET']
    boto3.resource('s3').meta. \
        client.upload_file(filename, bucket, f"rbsc/{filename}.json")


# event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1', 'eventTime': '2020-06-25T18:42:38.099Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AROAI6CZ2KVAQG2B4HD34:rdought1'}, 'requestParameters': {'sourceIPAddress': '98.32.232.192'}, 'responseElements': {'x-amz-request-id': '0EEA4E5B5B77C96F', 'x-amz-id-2': 'HoiHuQMD7tJraZ+l1XIRd/tmq74gB2thtXC/3r8x6vEPNOw7xyMMnIHqZFpzlRhnv+TilKahUH4Q98zG4p7La0grRPD7DXgT'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'NjQ2Y2M1YTAtMzFhNi00NjRjLTk3NWUtM2E5YjQ2MTNiZTZk', 'bucket': {'name': 'devred-sample', 'ownerIdentity': {'principalId': 'A1LSOVJBH3XNJN'}, 'arn': 'arn:aws:s3:::devred-sample'}, 'object': {'key': 'digital/The+Term+of+Contract.json', 'size': 87, 'eTag': 'd860c4f5d9e70b1d361be804f66b791c', 'sequencer': '005EF4F01FAAC12B20'}}}]}
# handler(event, None)
