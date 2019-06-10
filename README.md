# Mozilla Developer Portal

## Development workflow

### Setup

Since this project uses [Docker](https://www.docker.com/), you'll need to install [Docker](https://hub.docker.com/search?q=&type=edition&offering=community) and [Docker Compose](https://docs.docker.com/compose/install/) to run this project locally.

To get set up in one-command, run:

```shell
./setup.sh
```

This command will create an .env file with unique keys, build docker images and containers, run database migrations, load fixture data, and prompt to create a superuser.

### Running

With Docker Desktop running in the background, bring up the services built by the setup script by running:

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

### Updating

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

## Static site generation

A static file version of the site is generated using [Wagtail Bakery](https://github.com/wagtail/wagtail-bakery) which is built on top of [Django Bakery](https://github.com/datadesk/django-bakery)

### Usage

Build the site out as flat files to the /build folder (specified in settings/base.py):  

```shell
docker-compose exec app python manage.py build
```

Check the built static site:  

```shell
docker-compose exec app python manage.py buildserver 0.0.0.0:8080
```
