# Mozilla Developer Portal [![Build Status](https://travis-ci.org/mdn/developer-portal.svg?branch=master)](https://travis-ci.org/mdn/developer-portal)

## Development workflow

### Setup

This project uses [Docker](https://www.docker.com/). The easiest way to get started is to install [Docker Desktop](https://hub.docker.com/search?q=Docker%20Desktop&type=edition&offering=community) which provides the `docker` and `docker-compose` commands.

After installing Docker, use the __dev-setup__ script to run the project locally:

```shell
./scripts/dev-setup
```

This command will create an .env file with unique keys, build docker images and containers, run database migrations, and load fixture data.

### Run locally

With Docker Desktop running in the background, bring up the services by running:

```shell
docker-compose up
```

As you make changes, remember to run the tests…:

```shell
docker-compose exec app python manage.py test
docker-compose exec static npm run test
```

…and to make and apply database migrations:

```shell
docker-compose exec app python manage.py makemigrations
docker-compose exec app python manage.py migrate
```

### User authentication

GitHub OAuth is supported for admin login. When running in production, the auth pipeline checks to see if the GitHub user is a member of the __mdn__ organization. Additional organizations can be added via the `GITHUB_ORGS` env variable.

When running in debug any GitHub user is allowed to log in and is automatically given superuser status. It is possible to log in without using GitHub by creating a Django superuser as normal:

```shell
docker-compose exec app python manage.py createsuperuser
```

### Update

After pulling master you may need to install new dependencies…:

```shell
docker-compose build
```

…or run database migrations:

```shell
docker-compose exec app python manage.py migrate
```

If things get messed up, you could (as a last resort) prune ALL Docker images, containers and volumes, and start from scratch:

```shell
./setup.sh --prune
```

## Building a static site

Wagtail Bakery can build a static version of the site. In production this runs automatically when pages are published or unpublished from the Wagtail admin.

### Usage

To manually build the static site, run:

```shell
docker-compose exec app python manage.py build --settings=developerportal.settings.production
```

The result of this will be output to the /build directory.
