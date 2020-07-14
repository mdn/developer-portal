# Locust.io usage for load testing

This directory contains a basic `locustfile.py` for use when load testing the Developer Portal project.

It expects all the structural pages to be present on the target site, as well as some content pages, which are present on all deployed environments at the time of setting up Locust.

To learn more about Locust, see [https://docs.locust.io/en/stable/index.html](the official docs)

## Quickstart

### Simple local running, using a Docker image

- `cd` into the `locust/` directory of the checked-out project and ensure that `locustfile.py` (or whichever configuration file you wish to run) is present in `locust/`

* **Recommended approach**: spin up a main node and and (at least) four workers, use docker-compose:

```bash
docker-compose up --scale worker=4
```

Or if you just want to run a single Docker container:

```bash
docker run -p 8089:8089 -v $PWD:/mnt/locust locustio/locust -f /mnt/locust/locustfile.py
```

### View the dashboard

Go to http://localhost:8089/

### Start the tests

**Number of total users to simulate**

- Number of concurrent Locust users. Try starting with 200, but then dial it up for subsequent tests

**Hatch rate**

- Set how fast users are spawned. Try 3 to start with

**Host**

- Enter the hostname of the site you want to test, taking care to specify the CDNed version of the site if that's what you want to load test. Bear in mind that all deployed sites feature rate limiting.

  - CDNed dev and stage sites: https://developer-portal-cdn.{rest of URL for the CMS origin site}
  - CDNed prod site: https://developer.mozila.com
