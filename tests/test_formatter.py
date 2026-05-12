import unittest

from app.formatter import (
    reverse_text,
    capitalize_words,
    count_vowels,
)


class TestFormatter(unittest.TestCase):

    def test_reverse_text(self):
        self.assertEqual(reverse_text("python"), "nohtyp")

    def test_capitalize_words(self):
        result = capitalize_words("hello world")
        self.assertEqual(result, "Hello World")

    def test_count_vowels(self):
        self.assertEqual(count_vowels("education"), 5)


if __name__ == "__main__":
    unittest.main()
