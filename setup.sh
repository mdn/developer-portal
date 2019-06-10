#!/bin/sh

set -e

COLOR_GREEN='\033[0;32m'
COLOR_NONE='\033[0m'

log() {
  echo "${COLOR_GREEN}SETUP: ${1}${COLOR_NONE}"
}

show_help() {
  echo 'Usage: setup.sh [ --help | --prune | --detach | --non-interactive ]'
  echo '  --help   - Show this help text.'
  echo '  --prune  - Prune images, containers and volumes before building.'
  echo '  --detach - Keep services running in the background when finished.'
  echo '  --non-interactive - Skip steps that require user input.'
  exit 0
}


while test $# -gt 0
do
  case "$1" in
    --help) show_help
      ;;
    --detach) ARG_DETACH=1
      ;;
    --non-interactive) ARG_NON_INTERACTIVE=1
      ;;
    --prune) ARG_PRUNE=1
      ;;
  esac
  shift
done


log 'Stopping Docker services.'
touch .env # Create empty file so docker-compose down can run
docker-compose --log-level ERROR down

if [ -n "$ARG_PRUNE" ]; then
  log 'Pruning images.'
  docker image prune -f
  log 'Pruning containers.'
  docker container prune -f
  log 'Pruning volumes.'
  docker volume prune -f
fi


log 'Generating unique .env file.'
cat <<EOT > .env
# This file was generated by setup.sh and is for local use only.
PYTHONUNBUFFERED=1
DJANGO_ENV=dev
DJANGO_SECRET_KEY="$(openssl rand -base64 64 | tr -d '+/\n=')"
POSTGRES_DB=developerportal
POSTGRES_HOST=db
POSTGRES_PASSWORD="$(openssl rand -base64 64 | tr -d '+/\n=')"
POSTGRES_USER=admin
EOT


log 'Building Docker services.'
docker-compose up --build --detach


log 'Running migrations.'
docker-compose exec app python manage.py migrate


log 'Loading data.'
docker-compose exec app python manage.py loaddata developerportal/apps/**/fixtures/*.json


if [ -z "$ARG_NON_INTERACTIVE" ]; then
  log 'Creating super user.'
  docker-compose exec app python manage.py createsuperuser
fi


if [ -n "$ARG_DETACH" ]; then
  log 'Done! Services running detached.'
else
  log 'Done! Shutting down services.'
  docker-compose down
fi
