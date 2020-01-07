from .celery import app


@app.task
def ingest_articles():
    assert False, "WRITE ME"


@app.task
def ingest_videos():
    assert False, "WRITE ME"
