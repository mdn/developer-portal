# Automatic publishing of a static site to S3

[Wagtail Bakery](https://github.com/wagtail/wagtail-bakery) can build ("bake") a static version of the site and sync it to Amazon S3, where it can be served as a website.

_Note that "Publish" and "Unpublish" here refer to the Wagtail sense of making a page live / not live. Emitting a static version of the site to S3 will be referred to as "build-and-sync"._

In production, this "build-and-sync" process will be requested at a few points:

1. Whenever a Page is Published or Unpublished from the Wagtail admin. (This means if two Pages are published, the "build-and-sync" process is requested twice, but that's fine because requesting a build is idempotent: a flag is set, but a separate periodic task checks for this flag and does a build, so we don't end up with concurrent builds.)

2. Hourly, on a schedule, we'll check for any Wagtail Pages due to be automaticaly Published or Unpublished, and if any are found, that will be done. This is done via the [`publish_scheduled_pages`](https://docs.wagtail.io/en/v2.0/reference/management_commands.html#publish-scheduled-pages) management command. This action will automatically then request the "build-and-sync" step mentioned in 1 for each page being automatically Published or Unpublished - assuming there are some that are scheduled to be published/unpublished.

3. Hourly, on a schedule, the whole site needs to republished, so that listings of upcoming Events, for instance, don't become too stale (especially if it's a weekend, for instance). Therefore, once an hour, a request for a new static build is raised, even if no Pages have been Published/Unpublished.

## How is the build executed?

All builds are performed asynchronously, via a task queue. Note that the task queue uses a special settings module (`settings.worker`). This is an extension of `settings.production` but includes a Google Analytics code, because we _only_ want to get GA metrics for the static site, not the pages live-rendered by Django/Wagtail because their users will be the MDN team, etc.

## What gets published?

Currently, the build-and-sync process will producde and sync new HTML for **every Page within the site**, regardless of whether its content has just been updated, as well as any new or changed assets (CSS, JS, images and user media) to the S3 bucket. (Static assets are only going to change with a new code release - user media such as photos are already up in S3, in a different bucket from the one that holds the static site.)

## What about CDN invalidation?

We can't lean on Wagtail for frontend/CDN cache invalidation because the build-and-sync process happens asynchronously, on the whole site, while Wagtail FE cache invalidation works on individually-published pages only.

So, instead, we handle CDN invalidation directly, with a post-publish API call to the CDN with a wildcard invalidation for `/*`.
