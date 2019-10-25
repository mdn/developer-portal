"""Tests to show that the standard way to sign in to Wagtail and in to the Django Admin
just do not work (which is good, because everyone should go via SSO)"""

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginDeniedTest(TestCase):
    def setUp(self):
        self.wagtail_login_url = reverse("wagtailadmin_login")
        self.django_admin_login_url = reverse("admin:login")

    def _create_admin(self):
        # create an admin user
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin12345"
        )
        assert admin.is_active is True
        assert admin.has_usable_password() is True
        assert admin.check_password("admin12345") is True
        assert admin.is_staff is True
        assert admin.is_superuser is True

        return admin

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

    def test_posting_to_login_still_denied(self):
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
            payload = {"username": admin.username, "password": "admin12345"}
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
