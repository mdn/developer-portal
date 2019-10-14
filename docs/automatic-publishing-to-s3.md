# Automatic publishing of a static site to S3

[Wagtail Bakery](https://github.com/wagtail/wagtail-bakery) can build ("bake") a static version of the site and sync it to Amazon S3, where it can be served as a website.

_Note that "Publish" and "Unpublish" here refer to the Wagtail sense of making a page live / not live. Emitting a version of the site to S3 will be referred to as "build-and-sync"._

In production, this "build-and-sync" process will run at a few points:

1. It will be run whenever a Page is Published or Unpublished from the Wagtail admin. (Note: this means if two Pages are published, the "build-and-sync" process is run twice...)

2. Hourly, on a schedule, we'll check for any Wagtail Pages due to be automaticaly Published or Unpublished, and if any are found, that will be done. This action will then trigger the "build-and-sync" step mentioned in 1 for each page being automatically Published or Unpublished.

3. Hourly, on a schedule, the whole site needs to republished, so that listings of upcoming Events, for instance, don't become too stale (especially if it's a weekend, for instance).

**Case 1** will be performed asynchronously, via a task queue. Publishing/Unpublishing a Page immediately puts a task in the queue. A worker process picks it up and runs the "build-and-sync" process. This process will sync new HTML for **every Page within the site** as well as any new/changed assets (CSS, JS, images and user media) to the S3 bucket.

**Case 2** will be triggered by a scheduler/cron job running Wagtail's [`publish_scheduled_pages`](https://docs.wagtail.io/en/v2.0/reference/management_commands.html#publish-scheduled-pages) management command. This implicitly then triggers `Case 1`.

**Case 3** will be triggered by a different scheduler/cron job. The cleanest way to implement this is to add a new management command that emits the post-Publish Django Signal that starts **Case 1**, so we simply end up with a new enqueued task, which the worker picks up.)

## A note about queue load

There is a risk that the various ways of triggering an async build, plus the fact that each Publish/Unpublish action for each page will trigger a new static build, means there may be a lot of "build-and-sync" tasks in the queue, and all but the most recent one will be redundant. (We might want to look at a way to purge outmoded "build-and-sync" tasks and just use the newest one.)

# CDN invalidation

We can't lean on Wagtail for frontend/CDN cache invalidation because the build-and-sync process happens asynchronously, so we'll be handling that with a post-publish API call to the CDN
