from wagtail.core.signals import page_published, page_unpublished

from .tasks import invalidate_entire_cdn


def purge_cdn_on_publish(signal, **kwargs):
    # TODO: refine this to be more selective and only invalidate the
    # keys we know we need to. At the moment we're erring on the side
    # of caution.
    invalidate_entire_cdn.delay()


page_published.connect(purge_cdn_on_publish)
page_unpublished.connect(purge_cdn_on_publish)
