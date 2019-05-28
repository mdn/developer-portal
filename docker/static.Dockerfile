FROM node:12.2-alpine

WORKDIR /app/
COPY . /app/

RUN npm ci
RUN rm -rf dist
RUN npm run build
