import logging
import os
from http.client import HTTPS_PORT

from django.conf import settings
from django.db.models import Q
from django.test.client import RequestFactory

from wagtail.contrib.redirects.models import Redirect
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core.models import Site

from bakery.management.commands import get_s3_client
from bakery.views import BuildableMixin
from developerportal.apps.taskqueue.utils import invalidate_cdn
from wagtailbakery.views import AllPublishedPagesView, WagtailBakeryView

logger = logging.getLogger(__name__)


def is_secure_request(site):
    return site.port == HTTPS_PORT or getattr(settings, "SECURE_SSL_REDIRECT", False)


class AllPublishedPagesViewAllowingSecureRedirect(AllPublishedPagesView):
    """Extension of `AllPublishedPagesView` that detects application-level SSL
    redirection in order to avoid an issue where rendered pages end up being 0 bytes

    See https://github.com/wagtail/wagtail-bakery/issues/24 for confirmation of the
    issue and the discussion on https://github.com/wagtail/wagtail-bakery/pull/25
    that points to a custom view being the (current) workaround. Ideally we'll be
    able to replace this when that issue is resolved.

    The following code is taken from that closed PR, which adds the `secure_request`
    variable.
    """

    def build_object(self, obj):
        """
        Build wagtail page and set SERVER_NAME to retrieve corresponding site
        object.
        """
        site = obj.get_site()
        logger.debug("Building %s" % obj)
        secure_request = is_secure_request(site)
        self.request = RequestFactory(SERVER_NAME=site.hostname).get(
            self.get_url(obj), secure=secure_request
        )
        self.set_kwargs(obj)
        path = self.get_build_path(obj)
        self.build_file(path, self.get_content(obj))


class PostPublishOnlyWagtailBakeryView(WagtailBakeryView):
    """
    Base view class designed for hooking in ONLY post_publish actions.
    It should not not do any building or publishing

    It's a slight hack, in that it's one view that produces multiple
    redirects in S3 and noops the actual build step, but it slots in
    nicely to django-bakery's pipeline approach.
    """

    def build_method(self):
        # We don't want to do something on Build, only *after* Publish
        return None

    def post_publish(self):
        raise NotImplementedError()


class S3RedirectManagementView(PostPublishOnlyWagtailBakeryView):
    """Buildable "view" that generates S3-native redirects for each
    Wagtail Redirect that exists."""

    def get_redirect_url(self, redirect):
        """If the redirect points to a Page, generate a relative path,
        else return the URL to redirect to instead."""

        if redirect.redirect_page:
            path = redirect.redirect_page.get_url()
            assert path[0] == "/"  # has to lead with a slash else S3 will choke
            return path

        return redirect.redirect_link  #  a URL

    def tidy_path(self, path):
        return path[1:]  #  strip leading slash

    def post_publish(self, bucket):
        """
        Set up an S3-side redirect for all Wagtail Redirects

        This is inspired by django-bakery's BuildableRedirectView.post_publish method
        and gets called as part of the `publish` management command
        """
        s3_client, s3_resource = get_s3_client()

        #  For now, we're assuming we're only handling the default site
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            logger.warning("No default Site found - skipping generation of redirects")
            return

        no_site_q = Q(site__isnull=True)
        this_site_q = Q(site=site)
        redirects = Redirect.objects.filter(no_site_q | this_site_q)

        if not redirects:
            logger.info(
                "No Wagtail Redirects detected, so no S3 Website Redirects to create"
            )

        for redirect in redirects:
            original_dest = self.tidy_path(redirect.old_path)
            new_dest = self.get_redirect_url(redirect)

            logger.info(
                (
                    "Adding S3 Website Redirect in {bucket_name} from {old} to {new}"
                ).format(old=original_dest, bucket_name=bucket.name, new=new_dest)
            )
            s3_client.put_object(
                ACL="public-read",
                Bucket=bucket.name,
                Key=original_dest,
                WebsiteRedirectLocation=new_dest,
            )


class CloudfrontInvalidationView(PostPublishOnlyWagtailBakeryView):
    """Buildable "view" that invalidates the ENTIRE distribution in Cloudfront."""

    def post_publish(self, bucket):
        invalidation_targets = ["/*"]  # this wildcard should catch everything
        invalidate_cdn(invalidation_targets)


class SitemapBuildableView(BuildableMixin):
    # Note that this code is based on https://github.com/wagtail/wagtail-bakery/pull/38
    # and ONLY builds out the default site (which is fine for our current needs
    # but may change over time). Ideally wagtail-bakery will soon get this behaviour
    # and we can switch to its own implementation

    build_path = "sitemap.xml"

    def build(self):
        logger.info("Building out XML sitemap.")
        default_site = Site.objects.filter(is_default_site=True).first()
        secure_request = is_secure_request(default_site)
        self.request = RequestFactory(SERVER_NAME=default_site.hostname).get(
            self.build_path, secure=secure_request
        )
        path = os.path.join(settings.BUILD_DIR, self.build_path)
        self.prep_directory(self.build_path)
        self.build_file(path, self.get_content())
        logger.info("Sitemap building complete.")

    @property
    def build_method(self):
        return self.build

    def get_content(self):
        return sitemap(self.request).render().content
