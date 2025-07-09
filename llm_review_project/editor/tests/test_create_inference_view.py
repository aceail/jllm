from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from editor.models import InferenceResult


class CreateInferenceViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester", password="pw"
        )

    @patch("editor.views.perform_inference")
    def test_create_inference_success(self, mock_perform):
        self.client.force_login(self.user)
        result = InferenceResult.objects.create(
            prompt="p", original_text="o", edited_text="o"
        )
        mock_perform.return_value = result

        response = self.client.post(
            reverse("editor:create_inference"),
            {"solution": "default", "prompt": "hello"},
        )
        self.assertRedirects(
            response,
            reverse("editor:editor_with_id", args=[result.id]),
        )
        mock_perform.assert_called_once()

    @patch("editor.views.perform_inference")
    def test_create_inference_failure(self, mock_perform):
        self.client.force_login(self.user)
        mock_perform.return_value = None
        response = self.client.post(
            reverse("editor:create_inference"),
            {"solution": "default", "prompt": "hello"},
        )
        self.assertRedirects(response, reverse("editor:main_editor"))
