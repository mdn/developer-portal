FROM node:12.2-alpine AS static

WORKDIR /app/

COPY package.json package-lock.json /app/
RUN npm ci
RUN rm -rf dist

COPY .eslintignore webpack.config.js /app/
COPY src/ /app/src/

RUN npm run build


FROM python:3.7-alpine AS app

EXPOSE 8000
WORKDIR /app/

RUN crontab -l | { cat; echo '0 * * * * /usr/local/bin/python /app/manage.py build && /usr/local/bin/python /app/manage.py s3upload'; } | crontab -
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

CMD exec gunicorn developerportal.wsgi:application --bind=0.0.0.0:8000 --reload --workers=3
