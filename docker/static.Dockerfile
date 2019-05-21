FROM node:12.2-alpine

WORKDIR /app/
COPY . /app/

RUN npm ci
RUN npm run build
