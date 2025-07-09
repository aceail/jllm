from django.test import TestCase

from editor.utils import parse_json_from_string


class ParseJsonFallbackTests(TestCase):
    def test_parse_key_value_fallback(self):
        text = "환자ID: 123\n성별: 남자\n나이: 45"
        result = parse_json_from_string(text)
        self.assertEqual(result["환자ID"], "123")
        self.assertEqual(result["성별"], "남자")
        self.assertEqual(result["나이"], 45)
