import hashlib

from django.db import models

from wagtail.images.models import AbstractImage, AbstractRendition, Image


class MozImage(AbstractImage):
    # Additional fields:
    caption = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + ("caption",)

    def _extract_suffix(self, filename, delimiter="."):
        parts = filename.split(delimiter)
        if len(parts) == 1:
            return ""
        return f"{delimiter}{parts[-1]}"

    def get_upload_to(self, filename):
        """Custom filename-setting code that will scrub original filenames and
        use a SHA1 of them instead."""

        hashed_filename = hashlib.sha1(filename.encode("utf-8")).hexdigest()[:32]
        # Reducing the hash to 32 chars gives us more scope for padding if two files
        # with the same original filename are uploaded and get extra chars added
        # to their name (because settings.AWS_S3_FILE_OVERWRITE is False)

        file_suffix = self._extract_suffix(filename)
        _filename = f"{hashed_filename}{file_suffix}"

        # Make sure we use the rest of Wagtail's logic to benefit from
        # edge-case contingencies – see AbstractImage.get_upload_to in
        # https://github.com/wagtail/wagtail/blob/master/wagtail/images/models.py
        _upload_to = super().get_upload_to(_filename)

        return _upload_to


class Rendition(AbstractRendition):
    image = models.ForeignKey(
        MozImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
