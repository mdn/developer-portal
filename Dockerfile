FROM python:3.7-alpine AS app

EXPOSE 8000
WORKDIR /app/
COPY . /app/

# Alpine deps for Pillow
RUN apk add --no-cache jpeg-dev zlib-dev
# Alpine deps for psycopg2
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
# Alpine deps for pylibmc
RUN apk add --no-cache libmemcached-dev zlib-dev

# Python deps
RUN pip install -U pip
RUN pip install -r requirements.txt --no-cache-dir

# Clean Alpine deps
RUN apk --purge del .build-deps

CMD exec gunicorn developerportal.wsgi:application --bind=0.0.0.0:8000 --reload --workers=3


FROM node:12.2-alpine AS static

WORKDIR /app/
COPY . /app/

RUN npm ci
CMD npm run build
