FROM python:3.7-alpine AS app
EXPOSE 8000
WORKDIR /app/

# Alpine deps for Pillow
RUN apk add --no-cache jpeg-dev zlib-dev
# Alpine deps for psycopg2
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
# Alpine deps for pylibmc
RUN apk add --no-cache libmemcached-dev zlib-dev
# Alpine deps for libxml, used by readtime
RUN apk add --no-cache libc-dev libxslt-dev

# Python deps
COPY requirements.txt /app/
RUN pip install -U pip
RUN pip install -r requirements.txt --no-cache-dir

# Clean Alpine deps
RUN apk --purge del .build-deps

RUN touch .env
COPY .env developerportal manage.py /app/
CMD exec gunicorn developerportal.wsgi:application --bind=0.0.0.0:8000 --reload --workers=3


FROM node:12.2-alpine AS static
WORKDIR /app/

# Install dependencies
COPY package.json package-lock.json /app/
RUN npm ci
RUN rm -rf dist

# Copy source
COPY .eslintignore webpack.config.js src /app/

CMD npm run build
