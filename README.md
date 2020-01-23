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

#### Accessing the site

Note that the local build goes via nginx so that we can have local-dev HTTPS for greater parity with production.

You can find the local site under HTTPS at `https://developer-portal-127-0-0-1.nip.io`. `http://localhost:8000` will also still respond, but be aware that any behaviour which requires HTTPS (eg: CSP) may cause problems.
Feel free to add `127.0.0.1 developer-portal-127-0-0-1.nip.io` to your `/etc/hosts` if you want to work totally offline.

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

Mozilla SSO via OpenID Connect is the default for admin login.

To use this locally, you will need to have a Mozilla SSO account, plus values for `OIDC_RP_CLIENT_ID` and `OIDC_RP_CLIENT_SECRET` in your `.env` or in `settings.local`. You can local-development versions of these credentials from a another MDN Developer Portal team member, someone on Mozilla IAM team or the project's SRE (@limed).

If you have a Mozilla SSO account, create a Django superuser with the same email address.

```shell
docker-compose exec app python manage.py createsuperuser
```

If you do not have a Mozilla SSO account, or you want to work offline, you can create a Django superuser and configure the local build to use conventional Django auth. See `settings/local.py.example`

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

### Usage

The preferred way to do things is to have `settings.DEBUG=False` and to have an AWS bucket configured as per `settings/local.py.example` and to let the task queue run the static-build-and-publish, either when a page is published or via a special management command for requesting a build:

```shell
docker-compose exec app python manage.py request_static_build
```

However, if you really can't set `DEBUG=False` or you don't want to build via the task queue, you can manually build the static site with:

```shell
docker-compose exec app python manage.py build --settings=developerportal.settings.worker
```

The result of this will be output to the /app/build directory _inside the `app` container, not on your host_.

To publish the site to the S3 bucket configured in your settings (via environment vars in production, but more likely via `settings/local.py` for local dev):

```shell
docker-compose exec app python manage.py publish --settings=developerportal.settings.worker
```
