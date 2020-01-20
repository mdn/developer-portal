import logging
import os

from django.conf import settings

from .celery import app
from .models import IngestionConfiguration
from .utils import ingest_content

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


@app.task
def ingest_videos():
    if settings.AUTOMATICALLY_INGEST_CONTENT:
        ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_VIDEO)
    else:
        logger.info(
            "Skipping automatic video ingestion "
            "because settings.AUTOMATICALLY_INGEST_CONTENT is False"
        )


@app.task
def ingest_articles():
    if settings.AUTOMATICALLY_INGEST_CONTENT:
        ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_ARTICLE)
    else:
        logger.info(
            "Skipping automatic article ingestion "
            "because settings.AUTOMATICALLY_INGEST_CONTENT is False"
        )
