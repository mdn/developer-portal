FROM node:12.10-alpine@sha256:7a1789ae7b16137af96748012c6175c0561709f830de29922b7355509f4f9175 AS static

WORKDIR /app/

COPY package.json package-lock.json /app/
RUN npm ci
RUN rm -rf dist

COPY .eslintignore .prettierignore webpack.config.js /app/
COPY src/ /app/src/

RUN npm run build


FROM python:3.7-alpine@sha256:488bfa82d8ac22f1ed9f1d4297613a920bf14913adb98a652af7dbbbf1c3cab9 AS app

EXPOSE 8000
WORKDIR /app/

# Update cron to publish/unpublished scheduled pages hourly
RUN crontab -l | { cat; echo '0 * * * * /usr/local/bin/python /app/manage.py publish_scheduled_pages'; } | crontab -

# Update cron to "bake" a new static site each hour and push it to S3 - allows 10 mins for auto-publishing to complete
RUN crontab -l | { cat; echo '10 * * * * /usr/local/bin/python /app/manage.py build && /usr/local/bin/python /app/manage.py publish'; } | crontab -

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

COPY manage.py requirements.txt /app/
COPY developerportal/ /app/developerportal/
COPY src/ /app/src/
COPY --from=static /app/dist /app/dist/

# Collect all of the static files into the static folder
RUN DJANGO_ENV=production python manage.py collectstatic
CMD crond -d 8 -L /var/log/cron.log && \
  exec gunicorn developerportal.wsgi:application --bind=0.0.0.0:8000 --reload --workers=3
