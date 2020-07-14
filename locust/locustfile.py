import random
import string

from locust import between, task
from locust.contrib.fasthttp import FastHttpUser


def get_asset_paths(add_cachebreaker=False) -> list:
    """Return the JS and CSS bundle paths for the site -- at the moment we have
    no need for code splitting, etc

    While production uses django-whitenoise to serve files with a cachebreaking
    hash, the files are also available via their unhashed filename.
    If we want to, we can ask for them after appending a random cachebreaker
    param as a querystring to ensure we get a fresh set every time we run the
    load tests
    """

    if add_cachebreaker:
        cachebreaker = f"?v={random.random()}"
    else:
        cachebreaker = ""

    return [
        f"/static/js/bundle.js{cachebreaker}",
        f"/static/css/bundle.css{cachebreaker}",
    ]


def get_random_string(length=9):
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


class QuickstartUser(FastHttpUser):
    wait_time = between(5, 9)

    @task(6)
    def view_homepage(self):
        self.client.get("/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(4)
    def view_posts_page(self):
        self.client.get(f"/posts/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(2)
    def view_posts_page_paginated(self):
        random_page = random.randrange(1, 30)
        path = f"/posts/?page={random_page}"

        with self.client.get(path, catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()

        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(2)
    def view_posts_page_filtered(self):
        random_topic = random.choice(["rust", "voice", "browser-extensions"])
        path = f"/posts/?topic={random_topic}"
        self.client.get(path)
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(4)
    def view_events_page(self):
        self.client.get(f"/events/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(2)
    def view_events_page_paginated(self):
        random_page = random.randrange(1, 30)
        path = f"/events/?page={random_page}"

        with self.client.get(path, catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()

        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(2)
    def view_events_page_filtered(self):
        random_country_code = random.choice(["GB", "US", "NO", "NL", "DE"])
        path = f"/events/?date=past&date=future&location={random_country_code}"
        self.client.get(path)
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(1)
    def view_event_page(self):
        self.client.get(f"/events/view-source-conference-2019/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(1)
    def view_topics_page(self):
        self.client.get(f"/topics/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(4)
    def view_topic_page(self):
        self.client.get(f"/topics/rust/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(2)
    def view_people_page(self):
        self.client.get(f"/communities/people/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(1)
    def view_person_page(self):
        self.client.get(f"/communities/people/chris-mills/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(1)
    def view_404_page(self):
        with self.client.get("/does_not_exist/", catch_response=True) as response:
            if response.status_code == 404:
                response.success()
            for asset_path in get_asset_paths():
                self.client.get(asset_path)

    @task(1)
    def view_video_page(self):
        self.client.get(f"/videos/firefox-font-editor-advanced/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(1)
    def view_about_page(self):
        self.client.get(f"/about/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(3)
    def view_topic__developer_tools(self):
        # This may fail if the target site doesn't have this Topic
        self.client.get(f"/topics/developer-tools/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(2)
    def view_topic__voice(self):
        # This may fail if the target site doesn't have this Topic
        self.client.get(f"/topics/voice/")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(1)
    def search_site_with_random_string(self):
        param = get_random_string()
        self.client.get(f"/search/?search={param}")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)

    @task(2)
    def search_site_with_with_repeated_params(self):
        # These should be satisfied by the CDN after the first search
        param = get_random_string()

        param = random.choice(
            [
                "Hello, World!",
                "Firefox",
                "CSS Grid",
                "Mixed Reality",
                "WebThings",
                "Mozilla",
                "jobs",
            ]
        )
        self.client.get(f"/search/?search={param}")
        for asset_path in get_asset_paths():
            self.client.get(asset_path)
