"""Utils useful to all migrations"""

import json
import logging

logger = logging.getLogger(__name__)


def move_Page_image_to_Page_card_image(
    PageModel, source_field="image", dest_field="card_image"
):
    """For the given PageModel, set the Image defined as `source_field` to also
    be the Image referenced by `dest_field`, including updating the JSON representation
    of the page in the latest revision of the page, if any

    (Basically this is just repointing FKs)
    """

    all_pages = PageModel.objects.all()

    logger.info("Found %s %s records to update", len(all_pages), PageModel.__name__)

    for page in all_pages:
        logger.info("Updating %s", page)
        # This is a simple FK update - the image doesn't need changing, just which field
        # is keying to it
        if not getattr(page, source_field):
            logger.info("No %s on this page. Skipping", source_field)
            continue

        logger.info(
            "BEFORE: Page source image: %s; dest image: %s",
            getattr(page, source_field),
            getattr(page, dest_field),
        )

        image_id = getattr(page, source_field)

        setattr(page, dest_field, image_id)
        page.save()
        logger.info(
            "AFTER: Page source image: %s; dest image: %s",
            getattr(page, source_field),
            getattr(page, dest_field),
        )

        # We should also update the the JSON representation of the page in the
        # latest revision, which could be a WIP draft or it could be the last published
        # revision of the page, which would match the state of the current live Page
        last_rev = page.revisions.last()
        if last_rev:
            # Get the JSON representation of the revision
            logger.info("JSON BEFORE: %s", last_rev.content_json)
            rev_content = json.loads(last_rev.content_json)

            # Modify it
            rev_content[dest_field] = rev_content[source_field]

            # Store it
            last_rev.content_json = json.dumps(rev_content)
            last_rev.save()
            logger.info("JSON AFTER: %s", last_rev.content_json)

            # Note: there's need to publish() this revision: if it's a draft, we'll let
            # a Moderator publish it when ready; if it's a revision for a now-live page,
            # we've already updated the state of that page anyway
        else:
            logger.warning("No last revision found for this page.")

    logger.info("All done for %s", PageModel.__name__)
