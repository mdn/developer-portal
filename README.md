# Mozilla Developer Portal

## Setup

Since this project uses [Docker](https://www.docker.com/), you'll need to install [Docker](https://hub.docker.com/search?q=&type=edition&offering=community) and [Docker Compose](https://docs.docker.com/compose/install/) to run this project locally.

To install dependencies and start the development server, run:

```shell
docker-compose build
docker-compose run app python manage.py createsuperuser
docker-compose up
```
