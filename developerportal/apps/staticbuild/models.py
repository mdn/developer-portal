from django.db.models import DateTimeField, Model, signals
from django.dispatch import receiver
from django.utils.formats import date_format


class StaticBuild(Model):
    date = DateTimeField(auto_now_add=True)

    def __str__(self):
        return date_format(self.date, "SHORT_DATETIME_FORMAT")


@receiver(signals.post_save, sender=StaticBuild, dispatch_uid="static_build_uid")
def trigger_build(sender, instance, created=False, **kwargs):
    if created:
        from .wagtail_hooks import static_build

        static_build(force=True)
