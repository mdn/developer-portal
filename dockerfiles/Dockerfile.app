FROM python:3.7-alpine

EXPOSE 8000
WORKDIR /app/

RUN apk add --no-cache --virtual .build-deps \
  gcc \
  musl-dev \
  postgresql-dev
RUN apk add --no-cache \
  jpeg-dev \
  libc-dev \
  libmemcached-dev \
  libxslt-dev \
  postgresql-libs \
  zlib-dev

COPY requirements.txt /app/
RUN pip install -U pip
RUN pip install -r requirements.txt --no-cache-dir

RUN apk --purge del .build-deps

COPY .env manage.py requirements.txt /app/
COPY developerportal/ /app/developerportal/
CMD exec gunicorn developerportal.wsgi:application --bind=0.0.0.0:8000 --reload --workers=3
