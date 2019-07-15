import logging
import mimetypes
import os

import boto3
from boto3.exceptions import S3UploadFailedError


logging.basicConfig(level=os.environ.get('LOGLEVEL', logging.INFO))
logger = logging.getLogger(__name__)


class S3Uploader:
    s3 = boto3.client('s3')

    def __init__(self, bucket=None):
        self.bucket = bucket

    def _content_type_for_file(self, file_name):
        """Guess the content type for a file."""
        mimetype, _ = mimetypes.guess_type(os.path.abspath(file_name))
        return mimetype if mimetype else 'binary/octet-stream'


    def upload_directory(self, directory):
        """Upload a directory to S3."""
        for root, _, files in os.walk('build'):
            for name in files:
                file_name = os.path.join(root, name)
                self.upload_file(file_name)


    def upload_file(self, file_name):
        """Upload a single file to S3."""
        extra_args = {
            'ACL': 'public-read',
            'ContentType': self._content_type_for_file(file_name),
        }
        try:
            logger.info(f'- Uploading file {file_name}')
            self.s3.upload_file(file_name, self.bucket, file_name, extra_args)
        except S3UploadFailedError as e:
            logger.error(e)
