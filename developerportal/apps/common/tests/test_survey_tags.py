from django.test import TestCase, override_settings

from waffle.testutils import override_flag


class SurveyTagTests(TestCase):
    @override_flag("show_task_completion_survey", active=True)
    def test_survey_content_only_rendered_if_survey_url_configured(self):
        with override_settings(TASK_COMPLETION_SURVEY_URL="https://example.com/test"):
            response = self.client.get("/")
            self.assertContains(response, "complete a short survey", 1)

        with override_settings(TASK_COMPLETION_SURVEY_URL=None):
            response = self.client.get("/")
            self.assertNotContains(response, "complete a short survey")

    @override_settings(TASK_COMPLETION_SURVEY_URL="https://example.com/test")
    def test_survey_content_only_rendered_if_flag_allows_it(self):

        with override_flag("show_task_completion_survey", active=True):
            response = self.client.get("/")
            self.assertContains(response, "complete a short survey", 1)

        with override_flag("show_task_completion_survey", active=False):
            response = self.client.get("/")
            self.assertNotContains(response, "complete a short survey")
