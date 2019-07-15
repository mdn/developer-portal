import logging
import mimetypes
import os

import boto3
from boto3.exceptions import S3UploadFailedError


logging.basicConfig(level=logging.INFO)


def upload_file():
    s3_client = boto3.client('s3')
    bucket = os.environ.get('AWS_BUCKET')

    for root, dirs, files in os.walk('build'):
        for name in files:
            file_name = f'{root}/{name}'
            mimetype, _ = mimetypes.guess_type(os.path.abspath(file_name))

            if not mimetype:
                mimetype = 'binary/octet-stream'
            try:
                response = s3_client.upload_file(file_name, bucket, file_name, { 'ContentType': mimetype })
                logging.info(f'Uploaded to aws - {file_name}')
            except S3UploadFailedError as e:
                logging.error(e)
