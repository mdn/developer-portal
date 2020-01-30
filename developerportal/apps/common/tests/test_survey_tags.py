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

        with override_settings(TASK_COMPLETION_SURVEY_URL="undefined"):
            response = self.client.get("/")
            self.assertNotContains(response, "complete a short survey")

    @override_settings(TASK_COMPLETION_SURVEY_URL="https://example.com/test")
    def test_survey_content_always_rendered_regardless_of_flag_state(self):

        with override_flag("show_task_completion_survey", active=True):
            response = self.client.get("/")
            self.assertContains(response, "complete a short survey", 1)

            # Check for key CSS/HTML attrs
            self.assertContains(response, 'js-task-completion-survey" hidden>')

        with override_flag("show_task_completion_survey", active=False):
            response = self.client.get("/")
            self.assertContains(response, "complete a short survey")

            # Check for key CSS/HTML attrs
            self.assertContains(response, 'js-task-completion-survey" hidden>')
