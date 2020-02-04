from django.test import TestCase, override_settings


class SurveyTagTests(TestCase):
    def test_survey_content_only_rendered_if_survey_url_configured(self):
        with override_settings(TASK_COMPLETION_SURVEY_URL="https://example.com/test"):
            response = self.client.get("/")
            self.assertContains(response, "complete a short survey", 1)

        with override_settings(TASK_COMPLETION_SURVEY_URL=None):
            response = self.client.get("/")
            self.assertNotContains(response, "complete a short survey")

        with override_settings(TASK_COMPLETION_SURVEY_URL="undefined"):
            response = self.client.get("/")
            self.assertNotContains(response, "complete a short survey")
