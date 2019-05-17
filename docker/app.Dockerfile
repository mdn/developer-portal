# Use the official Python runtime image as the parent.
FROM python:3.7

EXPOSE 8000
WORKDIR /app/
COPY . /app/

RUN pip install -U pip
RUN pip install -r requirements.txt

CMD exec gunicorn developerportal.wsgi:application --bind=0.0.0.0:8000 --reload --workers=3
