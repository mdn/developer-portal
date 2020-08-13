# Deployed environments

The Developer Portal project currently has three deployed environments:

- Dev
- Stage
- Production

Each of these is running:

- an `app` pod running the webapp:

  - Wagtail CMS at `/admin/`, which live-renders content pages at `/` (and other paths)
  - the Django admin at `/django-admin/`

- a `celery-beat` pod to handle running scheduled tasks. (One instance only.)
- 1...n `celery-worker` pods, depending on which environment it is

Each environment has a CDN (Amazon Cloudfront).

Each environment has a configuration file used by k8s `dev.sh`, `stage.sh` and `prod.sh` (in `k8s/config/`) and in each of those files there are two env vars defined: `APP_HOST` and `APP_CDN_HOST` (which contribute values to Django settings).

- `APP_HOST` is the hostname the CMS runs on, directly - ie no CDN cacheing
- `APP_CDN_HOST` is the hostname that the CDN runs on, fronting whatever is definied as `APP_HOST`. This currently caches statics and HTML, and _doesn't_ forward cookies.

# Deploying to environments

The current workflow has the expectation that code is merged to master before it can be deployed on Stage or Production. This is because CI looks for a Docker image with the same hash as the `HEAD` of `master`.

### To get code on to Stage:

- merge it to `master` (eg: merge a PR)
- wait for CI to pass on `master` - see the relevant Slack channel for notifications, or look at Jenkins (VPN needed)
- check out `stage-push` and ensure it's up to date with `origin/stage-push`
- merge `master` INTO `stage-push` -- this should not create a merge commit and should effectively fast-forward `stage-push`'s `HEAD` to be the same as `master`'s
- push `stage-push` up to its origin - this will trigger CI to take the same image it just made for `master` (ie, same hash) and deploy it to the Staging environment.

### To get code into Production:

- as above, but using the `prod-push` branch instead of `stage-push`

### To get code on to Dev

This is a little different from above, because we're talking about WIP features or code being deployed to Dev to allow for manual QA, and it assumes that you want to deploy new code BEFORE you merge it to `master`. (If you don't, just treat `dev-push` like `stage-push`, but you'll have to work out how you handle WIP/non-signed-off code now having been merged to `master`).

- Create or use a new branch specifically for making CI build a Docker image using that code. `dev/merge-branch-to-get-CI-to-build-image` is what's currently being used.
- Check out `dev/merge-branch-to-get-CI-to-build-image` and ensure it's up to date with `origin/dev/merge-branch-to-get-CI-to-build-image`
- Merge any feature branch you want into `dev/merge-branch-to-get-CI-to-build-image` - you may have to fix conflicts manually, and accept that the state of the code on this branch might be temporarily diverging from what will eventually exist on `master`.
- Push `dev/merge-branch-to-get-CI-to-build-image` to origin and wait for CI to build the image and run the tests. Note that this is NOT notified in Slack: you'll have to look in CI
- Once CI is happy, note the hash of the `HEAD` of `dev/merge-branch-to-get-CI-to-build-image` - let's all that `TheHash`
- Check out `dev-push`.
- Switch the `HEAD` of `dev-push` to match that of `dev/merge-branch-to-get-CI-to-build-image` with: `git reset --hard TheHash`
- Push `dev-push` to `origin/dev-push` - it may need force-pushing but usually does not.
- Look for notifications (in Slack or CI) that the deployment worked.

Note that because dev-push contains WIP/non-`master` features, which themselves may contain database Migrations, the state of the DB schema on Dev will sometimes differ from the schema of the DB on Stage and Prod.
