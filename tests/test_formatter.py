from app.formatter import (
    reverse_text,
    capitalize_words,
    count_vowels,
)


def test_reverse_text():
    assert reverse_text("python") == "nohtyp"


def test_capitalize_words():
    result = capitalize_words("hello world")
    assert result == "Hello World"


def test_count_vowels():
    assert count_vowels("education") == 5