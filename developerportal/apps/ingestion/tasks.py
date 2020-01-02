from .celery import app


@app.tasks
def ingest_articles():
    assert False, "WRITE ME"


@app.tasks
def ingest_videos():
    assert False, "WRITE ME"
