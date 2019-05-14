# Use the official Python runtime image as the parent.
FROM node:12.2

WORKDIR /app/
COPY . /app/

RUN npm ci
RUN npm run build
