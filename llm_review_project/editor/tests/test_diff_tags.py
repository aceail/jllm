from django.test import TestCase
from django.contrib.auth import get_user_model
from editor.templatetags import diff_tags
from editor.models import InferenceResult, EditHistory


class DiffTagTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester", password="pw"
        )
        self.other = get_user_model().objects.create_user(
            username="other", password="pw"
        )

    def test_diff_highlight_and_json_equal(self):
        text1 = '{"a":1, "b":2}'
        text2 = '{"b":2, "a":1}'
        # identical after normalization
        self.assertEqual(diff_tags.diff_highlight(text1, text2), text1)
        self.assertTrue(diff_tags.json_equal(text1, text2))
        changed = diff_tags.diff_highlight("foo bar", "foo")
        self.assertIn("<span", changed)

    def test_json_history_diff(self):
        result = InferenceResult.objects.create(
            prompt="p",
            original_text="orig",
            edited_text="orig",
            parsed_result={"val": "one"},
            last_modified_by=self.user,
        )
        EditHistory.objects.create(result=result, editor=self.user, edited_data={"val": "one"})
        EditHistory.objects.create(result=result, editor=self.other, edited_data={"val": "two"})
        html = diff_tags.json_history_diff(result)
        self.assertIn("two", html)
        self.assertIn("diff-added", html)

    def test_json_history_diff_no_history(self):
        result = InferenceResult.objects.create(
            prompt="p", original_text="text", edited_text="text"
        )
        html = diff_tags.json_history_diff(result)
        self.assertEqual(html, result.edited_text)
