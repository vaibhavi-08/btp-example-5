def reverse_text(text):
    return text[::-1]


def capitalize_words(text):
    return text.title()


def count_vowels(text):
    vowels = "aeiouAEIOU"

    count = 0

    for char in text:
        if char in vowels:
            count += 1

    return count
