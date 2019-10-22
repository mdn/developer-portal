# Automatic publishing of a static site to S3

[Wagtail Bakery](https://github.com/wagtail/wagtail-bakery) can build ("bake") a static version of the site and sync it to Amazon S3, where it can be served as a website.

_Note that "Publish" and "Unpublish" here refer to the Wagtail sense of making a page live / not live. Emitting a version of the site to S3 will be referred to as "build-and-sync"._

In production, this "build-and-sync" process will be requested at a few points:

1. Whenever a Page is Published or Unpublished from the Wagtail admin. (Note: this means if two Pages are published, the "build-and-sync" process is called twice, but requesting a build is idempotent: a flag is set, but a separate periodic task checks for this flag and does a build, so we don't end up with concurrent builds.)

2. Hourly, on a schedule, we'll check for any Wagtail Pages due to be automaticaly Published or Unpublished, and if any are found, that will be done. This is done via the [`publish_scheduled_pages`](https://docs.wagtail.io/en/v2.0/reference/management_commands.html#publish-scheduled-pages) management command. This action will automatically then trigger the "build-and-sync" step mentioned in 1 for each page being automatically Published or Unpublished.

3. Hourly, on a schedule, the whole site needs to republished, so that listings of upcoming Events, for instance, don't become too stale (especially if it's a weekend, for instance).

All builds are performed asynchronously, via a task queue.

Note that the build-and-sync process will sync new HTML for **every Page within the site** as well as any new/changed assets (CSS, JS, images and user media) to the S3 bucket.

# CDN invalidation

We can't lean on Wagtail for frontend/CDN cache invalidation because the build-and-sync process happens asynchronously, on the whole site, while Wagtail FE cache invalidation works on individually-published pages only. So,we handle that with a post-publish API call to the CDN with a wildcard invalidation for `/*`
