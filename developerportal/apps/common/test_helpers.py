# Patch wagtail.tests.utils.WagtailPageTests to re-configure use of the ModelBackend
# so that WagtailPageTests.client.login() will work

from django.test import override_settings

from wagtail.tests.utils import WagtailPageTests


class PatchedWagtailPageTests(WagtailPageTests):
    @override_settings(
        AUTHENTICATION_BACKENDS=(
            "mozilla_django_oidc.auth.OIDCAuthenticationBackend",
            "django.contrib.auth.backends.ModelBackend",
        )
    )
    def login(self):
        return super().login()
