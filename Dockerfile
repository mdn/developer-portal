FROM node:12.16-alpine@sha256:08f387b98dd00c1a746580dbd91e538d534911cdd14f6d1d0b36b4687e823006 AS static

WORKDIR /app/

COPY package.json package-lock.json /app/
RUN npm ci
RUN rm -rf dist

COPY .eslintignore .prettierignore webpack.config.js /app/
COPY src/ /app/src/

RUN npm run build


FROM python:3.7-alpine@sha256:c90e5d8cf74a534acc6f7f4d0566a3be533ea943f374e58284b60b3aa9e05968 AS app_base

EXPOSE 8000
WORKDIR /app/

RUN apk add --no-cache --virtual .build-deps \
  gcc \
  musl-dev \
  postgresql-dev
RUN apk add --no-cache \
  jpeg-dev \
  libc-dev \
  libffi-dev \
  libmemcached-dev \
  libxslt-dev \
  postgresql-libs \
  zlib-dev

COPY requirements.txt /app/
RUN pip install -U pip
RUN pip install -r requirements.txt --no-cache-dir
RUN apk --purge del .build-deps

COPY etc/newrelic.ini /app/etc/newrelic.ini
COPY manage.py requirements.txt /app/
COPY developerportal/ /app/developerportal/
COPY src/ /app/src/
COPY --from=static /app/dist /app/dist/

# Create a non-root user with a fixed UID, no password and a home directory
RUN adduser -u 1000 -s /bin/bash -D devportaluser \
  && mkdir -p app \
  && chown devportaluser:devportaluser /app \
  && chmod 775 /app

# Collect all of the static files into the static folder
USER devportaluser
RUN DJANGO_ENV=production python manage.py collectstatic

# The following is explicitly called by docker-compose or a k8s manifest
# CMD exec gunicorn developerportal.wsgi:application --bind=0.0.0.0:8000 --reload --workers=3
