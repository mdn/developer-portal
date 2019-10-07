# Mozilla Developer Portal [![Build Status](https://travis-ci.org/mdn/developer-portal.svg?branch=master)](https://travis-ci.org/mdn/developer-portal)

## Development workflow

### Setup

This project uses [Docker](https://www.docker.com/). The easiest way to get started is to install [Docker Desktop](https://hub.docker.com/search?q=Docker%20Desktop&type=edition&offering=community) which provides the `docker` and `docker-compose` commands.

After installing Docker, use the **dev-setup** script to run the project locally:

```shell
./scripts/dev-setup
```

This command will create an .env file with unique keys, build docker images and containers, run database migrations, and load fixture data.

It's worth copying `settings/local.py.example` to `settings/local.py` but leaving everything commented out for now. Updating `local.py` can be a handy way to re-enable production-like settings (eg S3 uploads) that are disabled via the default local-development settings.

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

### Linting and autoformatting with (or without) a pre-commit hook

The project has support for using [Therapist](https://github.com/rehandalal/therapist) to run pre-commit linting and formatting tools. You don't _have_ to use it, but it makes it life easier.

`therapist` is configured to run:

- [black](https://github.com/psf/black) for code formatting
- [flake8](http://flake8.pycqa.org/en/latest/) for syntax checking
- [isort](https://github.com/timothycrosley/isort/) for import-order management
- [eslint](https://eslint.org/) for JavaScript checking
- [prettier](https://prettier.io/) for JavaScript formatting

At the moment, this project assumes have all of the above installed and available on the `$PATH` of your _host_ machine, along with Python 3 and `pip`. You can install the dependencies using `virtualenv` and `nvm` if you want, or not, or globally. As long as they're available, you're good.

(Note: this project is not currently supporting use of `therapist` inside Docker containers.)

**TIP: It's wise to enable all of the above tooling in your code editor, if possible, so that things are already in order before the pre-commit hook is run.**

#### `therapist` setup and usage

Install `therapist` :

    $ pip install therapist

Install the pre-commit hook that will trigger `therapist` automatically:

    $ therapist install
    Installing pre-commit hook...	DONE

(Take a look at the pre-commit file added to `.git/hooks/` to confirm the path looks right.)

Now, when you `git-commit` a change, the _staged_ changes will be checked by one or more of `black`, `isort`, `flake8`, `eslint` and/or `prettier`. See `.therapist.yml` in the project root for the configuration.

Alternatively, if you wanted to run it across the whole codebase, run:

    $ therapist run developerportal/

And if, for some reason, you want `therapist` to auto-fix everything wrong using those tools, run:

    $ therapist run developerportal/ --fix

Finally, `therapist` can be passed a list of file paths if you want to just run it on specific things:

    $ therapist run developerportal/path/to/file.js developerportal/path/to/another_file.py

### User authentication

GitHub OAuth is supported for admin login. When running in production, the auth pipeline checks to see if the GitHub user is a member of the **mdn** organization. Additional organizations can be added via the `GITHUB_ORGS` env variable.

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

See [these notes](docs/automatic-publishing-to-s3.md) for more detail.

### Usage

To manually build the static site, run:

```shell
docker-compose exec app python manage.py build --settings=developerportal.settings.production
```

The result of this will be output to the /build directory.
