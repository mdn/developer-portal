import boto3
import logging
import mimetypes
import os
from boto3.exceptions import S3UploadFailedError


def upload_file():
    s3_client = boto3.client('s3')
    bucket = 'mozilla-developer-portal-potato'
    for root, dirs, files in os.walk('build'):
        for name in files:
            file_name = f'{root}/{name}'
            mimetype, _ = mimetypes.guess_type(os.path.abspath(file_name))

            if not mimetype:
                mimetype = 'binary/octet-stream'
            try:
                response = s3_client.upload_file(file_name, bucket, file_name, { "ContentType": mimetype })
            except S3UploadFailedError as e:
                logging.error(e)



