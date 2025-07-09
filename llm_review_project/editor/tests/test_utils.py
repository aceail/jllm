from django.test import TestCase

from editor.utils import parse_json_from_string


class ParseJsonFallbackTests(TestCase):
    def test_parse_key_value_fallback(self):
        text = "환자ID: 123\n성별: 남자\n나이: 45"
        result = parse_json_from_string(text)
        self.assertEqual(result["환자ID"], "123")
        self.assertEqual(result["성별"], "남자")
        self.assertEqual(result["나이"], 45)


class ParseJsonBlockTests(TestCase):
    def test_extract_fenced_json(self):
        text = "prefix\n```json\n{\"a\": 1}\n```\nsuffix"
        result = parse_json_from_string(text)
        self.assertEqual(result["a"], 1)

    def test_invalid_fenced_json_fix(self):
        text = "```json\n{'a':1,}\n```"
        result = parse_json_from_string(text)
        self.assertEqual(result["a"], 1)
