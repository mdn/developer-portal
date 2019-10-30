"""Tests to show that the standard way to sign in to Wagtail and in to the Django Admin
just do not work (which is good, because everyone should go via SSO)"""

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class LoginTestBase(TestCase):

    TEST_ADMIN_PASSWORD = "admin12345"

    def setUp(self):
        self.wagtail_login_url = reverse("wagtailadmin_login")
        self.django_admin_login_url = reverse("admin:login")

    def _create_admin(self):
        # create an admin user
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password=self.TEST_ADMIN_PASSWORD,
        )
        assert admin.is_active is True
        assert admin.has_usable_password() is True
        assert admin.check_password(self.TEST_ADMIN_PASSWORD) is True
        assert admin.is_staff is True
        assert admin.is_superuser is True

        return admin


class ConventionalLoginDeniedTest(LoginTestBase):
    def test_login_page_contains_no_form(self):
        for url in (self.wagtail_login_url, self.django_admin_login_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                assert response.status_code == 200
                # Check for the form field attrs that would normally be present
                self.assertNotContains(response, b'name="username"')
                self.assertNotContains(response, b'name="password"')
                # No CSRF token == no go, anyway
                self.assertNotContains(response, b"csrfmiddlewaretoken")
                # Confirm SSO link
                self.assertContains(response, b"Sign in with Mozilla SSO")

    def test_posting_to_login_denied(self):
        admin = self._create_admin()
        for url, error_message, expected_template in (
            (
                self.wagtail_login_url,
                b"Your username and password didn't match.",
                "wagtailadmin/login.html",
            ),
            (
                self.django_admin_login_url,
                b"Please enter the correct username and password for a staff account.",
                "admin/login.html",
            ),
        ):
            payload = {"username": admin.username, "password": self.TEST_ADMIN_PASSWORD}
            with self.subTest(
                url=url,
                error_message=error_message,
                expected_template=expected_template,
            ):
                response = self.client.post(url, data=payload, follow=True)
                self.assertEqual(
                    response.status_code,
                    200,  # 200 is what comes back after the redirect
                )
                # Show that while we provided valid credentials, we still get treated
                # as if they are not the correct ones.
                self.assertContains(response, error_message)
                self.assertContains(response, b"Sign in with Mozilla SSO")
                self.assertTemplateUsed(response, expected_template)

    def test_only_sso_backend_enabled(self):
        self.assertEqual(
            settings.AUTHENTICATION_BACKENDS,
            ("mozilla_django_oidc.auth.OIDCAuthenticationBackend",),
        )


class ConventionalLoginAllowedTest(LoginTestBase):
    """If certain settings are set in settings.local, regular
    username + password sign-in functionality is restored
    """

    @override_settings(USE_CONVENTIONAL_AUTH=True)
    def test_login_page_contains_form(self):
        for url in (self.wagtail_login_url, self.django_admin_login_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                assert response.status_code == 200
                # Check for the form field attrs that would normally be present
                self.assertContains(response, b'name="username"', 1)
                self.assertContains(response, b'name="password"', 1)
                self.assertContains(response, b"csrfmiddlewaretoken", 1)
                self.assertNotContains(response, b"Sign in with Mozilla SSO")

    @override_settings(
        AUTHENTICATION_BACKENDS=(
            "mozilla_django_oidc.auth.OIDCAuthenticationBackend",
            "django.contrib.auth.backends.ModelBackend",
        )
    )
    def test_posting_to_login_is_accepted_if_the_modelbackend_is_re_configured(self):
        admin = self._create_admin()
        for url, expected_template in (
            (self.wagtail_login_url, "wagtailadmin/home.html"),
            (
                self.django_admin_login_url,
                "wagtailadmin/home.html"
                # CORRECT: signing in to Django Admin redirects to Wagtail Admin,
                # because that's what LOGIN_REDIRECT_URL points to
            ),
        ):
            payload = {"username": admin.username, "password": self.TEST_ADMIN_PASSWORD}
            with self.subTest(url=url, expected_template=expected_template):
                response = self.client.post(url, data=payload, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, b"Sign in")
                self.assertTemplateUsed(response, expected_template)
