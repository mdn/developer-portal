# CDN invalidation

We front the dynamically rendered Wagtail pages with a CDN (AWS Cloudfront), but we don't want them to become stale.

As such there are two moments which purge certain pages from the CDN.

1. **Currently, whenever any page is published, the _entire_ CDN is invalidated.** This is a something of a sledgehammer approach, but there are a number of areas where content from one page type is included in another page type, and only one of them is being published at that point in time. Refinement is possible, but for now this should work. See `developerportal.apps.taskqueue.wagtail_hooks` for details.

2. **Once a day (shortly after midnight, server time), a selected range of pages are also invalidated**, because they feature content which reference that happens/happened at a particular point in time: an `Event`. See `developerportal.apps.taskqueue.celery` for details.
