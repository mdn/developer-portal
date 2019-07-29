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

### Users

GitHub OAuth is supported for admin login. When running in production, the auth pipeline checks to see if the GitHub user is a member of the __mdn__ organization. Additional organizations can be added via the `GITHUB_ORGS` env variable.

When running in debug any GitHub user is allowed to log in and is automatically given superuser status. It is possible to log in without using GitHub by creating a Django superuser as normal:

```shell
docker-compose exec app python manage.py createsuperuser
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

A static version of this site can be generated. This is automatically run in production when resources are published/unpublished from the Wagtail admin.

### Usage

To manually build the static site, run:

```shell
docker-compose exec app python manage.py build --settings=developerportal.settings.production
```

The result of this will be output to the /build directory.
