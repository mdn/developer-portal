#!/bin/sh

set -e

COLOR_GREEN='\033[0;32m'
COLOR_NONE='\033[0m'

log() {
  echo "${COLOR_GREEN}SETUP: ${1}${COLOR_NONE}"
}


log 'Stopping Docker services.'
docker-compose --log-level ERROR down

if [ "$1" = '--prune' ]; then
  log 'Pruning images.'
  docker image prune -f
  log 'Pruning containers.'
  docker container prune -f
  log 'Pruning volumes.'
  docker volume prune -f
fi


log  'Generating unique .env file.'
cat <<EOT > .env
# These env variables are used when running the project locally.

# Python config
PYTHONUNBUFFERED=1

# Django config
DJANGO_ENV=dev
DJANGO_SECRET_KEY="$(openssl rand -base64 64 | tr -d '+/\n=')"

# Postgres setup
POSTGRES_DB=developerportal
POSTGRES_HOST=db
POSTGRES_PASSWORD="$(openssl rand -base64 64 | tr -d '+/\n=')"
POSTGRES_USER=admin
EOT


log 'Building Docker services.'
docker-compose up --build --detach


log 'Running migrations.'
docker-compose run --rm app python manage.py migrate


log 'Loading data.'
docker-compose run --rm app python manage.py loaddata developerportal/apps/**/fixtures/*.json


log 'Creating super user.'
docker-compose run --rm app python manage.py createsuperuser


log 'Done. Shutting down services.'
docker-compose down
