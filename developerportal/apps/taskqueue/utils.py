import logging
import os
from http import HTTPStatus

from django.conf import settings
from django.utils.timezone import now as tz_now

import boto3

logging.basicConfig(level=os.environ.get("LOGLEVEL", logging.INFO))
logger = logging.getLogger(__name__)


def invalidate_cdn(invalidation_targets=None):
    distribution_id = settings.AWS_CLOUDFRONT_DISTRIBUTION_ID

    if not distribution_id:
        logger.info("No Cloudfront distribtion ID configured. Skipping CDN purge.")
    else:
        logger.info("Purging Cloudfront distribtion ID {}.".format(distribution_id))

        if invalidation_targets is None:
            invalidation_targets = ["/*"]  # this wildcard should catch everything

        client = boto3.client("cloudfront")

        # Make a unique string so that this call to invalidate is not ignored
        caller_reference = str(tz_now().isoformat())

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
