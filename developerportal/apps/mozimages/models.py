from django.db import models

from wagtail.images.models import AbstractImage, AbstractRendition, Image


class MozImage(AbstractImage):
    # Additional fields:
    caption = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + ("caption",)


class Rendition(AbstractRendition):
    image = models.ForeignKey(
        MozImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
