from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from editor.utils import perform_inference
from editor.models import InferenceResult


class PerformInferenceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester", password="pw"
        )

    @patch("editor.utils.requests.post")
    def test_perform_inference_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"choices": [{"text": '{"foo": "bar"}'}]}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        result = perform_inference(self.user, "default", ai_json="{}")
        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_result, {"foo": "bar"})
        self.assertEqual(result.last_modified_by, self.user)
        self.assertEqual(result.history.count(), 1)

    @patch("editor.utils.requests.post")
    def test_perform_inference_no_prompt(self, mock_post):
        result = perform_inference(self.user, "default", ai_json="")
        self.assertIsNone(result)
        mock_post.assert_not_called()
