# Mozilla Developer Portal

## Setup

Since this project uses [Docker](https://www.docker.com/), you'll need to install [Docker](https://hub.docker.com/search?q=&type=edition&offering=community) and [Docker Compose](https://docs.docker.com/compose/install/) to run this project locally.

To install dependencies and start the development server, run:

```shell
docker-compose build
docker-compose up
```

With that running, in a new window run the following to create the database schemas and a super (admin) user.

```shell
docker-compose run app python manage.py migrate
docker-compose run app python manage.py createsuperuser
```

## Static site generation

A static file version of the site is generated using [Wagtail Bakery](https://github.com/wagtail/wagtail-bakery) which is built on top of [Django Bakery](https://github.com/datadesk/django-bakery)

### Usage

Get the container ID:  

```shell
docker container ls
```

Run a shell in the running container:  

```shell
docker exec -it CONTAINER_ID /bin/bash
```

Build the site out as flat files to the /build folder (specified in settings/base.py):  

```shell
root@CONTAINER_ID:/app# ./manage.py build
```

Check the built static site:  

```shell
root@CONTAINER_ID:/app# ./manage.py buildserver 0.0.0.0:8080
```
