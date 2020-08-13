FROM node:12.18-alpine@sha256:0b5c7eb38785da1ad4c105930faca0bc546dfcceb0464724456e277fd5e3f6e2 AS static

WORKDIR /app/

COPY package.json package-lock.json /app/
RUN npm ci
RUN rm -rf dist

COPY .eslintignore .prettierignore webpack.config.js /app/
COPY src/ /app/src/

RUN npm run build


FROM python:3.7-alpine@sha256:8cb58b0a85fafeb9b0d7d0bbc02f9b2894c300bdbc602aa1215a9de951961d6e AS app_base

EXPOSE 8000
WORKDIR /app/

RUN apk add --no-cache --virtual .build-deps \
  file \
  make \
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

COPY configs/ /app/configs/
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
