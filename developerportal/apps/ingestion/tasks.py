from .celery import app
from .models import IngestionConfiguration
from .utils import ingest_content


@app.task
def ingest_videos():
    ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_VIDEO)


@app.task
def ingest_articles():
    ingest_content(type_=IngestionConfiguration.CONTENT_TYPE_ARTICLE)
