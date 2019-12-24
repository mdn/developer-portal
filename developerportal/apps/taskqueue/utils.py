import logging
import os
from http import HTTPStatus

from django.conf import settings
from django.utils.timezone import now as tz_now

import boto3

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


def set_up_boto3():
    """
    A DRY place to make sure AWS credentials in settings override
    environment based credentials.  Boto3 will fall back to:
    http://boto3.readthedocs.io/en/latest/guide/configuration.html

    Taken from https://github.com/datadesk/django-bakery/blob/
    a2f1f74b03951450d797ec70cc9872d6c694e1e3/bakery/management/commands/__init__.py#L8
    """
    session_kwargs = {}
    if hasattr(settings, "AWS_ACCESS_KEY_ID"):
        session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID

    if hasattr(settings, "AWS_SECRET_ACCESS_KEY"):
        session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    boto3.setup_default_session(**session_kwargs)


def invalidate_cdn(invalidation_targets=None):

    set_up_boto3()

    distribution_id = settings.AWS_CLOUDFRONT_DISTRIBUTION_ID

    if not distribution_id:
        logger.info("No Cloudfront distribtion ID configured. Skipping CDN purge.")
    else:
        logger.info("Purging Cloudfront distribtion ID {}.".format(distribution_id))

        if invalidation_targets is None:
            invalidation_targets = ["/*"]  # this wildcard should catch everything

        client = boto3.client("cloudfront")

        # Make a unique string so that this call to invalidate is not ignored
        caller_reference = tz_now().isoformat()

        response = client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                "Paths": {
                    "Items": invalidation_targets,
                    "Quantity": len(invalidation_targets),
                },
                "CallerReference": caller_reference,
            },
        )
        http_status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if http_status == HTTPStatus.CREATED:
            invalidation_status = response.get("Invalidation", {}).get(
                "Status", "RESPONSE ERROR"
            )
            logger.info(
                (
                    "Got a positive response from Cloudfront. "
                    "Invalidation status: {}"
                ).format(invalidation_status)
            )
            logger.debug("Response: {}".format(response))
        else:
            logger.warning(
                "Got an unexpected response from Cloudfront: {}".format(response)
            )
