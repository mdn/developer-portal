FROM python:3.7-alpine AS app
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

COPY .env developerportal manage.py /app/
CMD exec gunicorn developerportal.wsgi:application --bind=0.0.0.0:8000 --reload --workers=3


FROM node:12.2-alpine AS static
WORKDIR /app/

COPY package.json package-lock.json /app/
RUN npm ci
RUN rm -rf dist

COPY .eslintignore webpack.config.js src /app/

CMD npm run build
