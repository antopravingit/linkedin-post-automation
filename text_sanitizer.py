#!/usr/bin/env python3
"""
Text Sanitizer - Fix encoding issues for LinkedIn posting

LinkedIn has issues with certain Unicode characters:
- Curly/smart quotes (', ', ", ") display as junk
- Em dashes (—) look like AI content
- Smart apostrophes need to be straight quotes
"""


def sanitize_for_linkedin(text: str) -> str:
    """
    Sanitize text for LinkedIn posting by fixing encoding issues.

    Args:
        text: Raw text that may have problematic characters

    Returns:
        Sanitized text safe for LinkedIn
    """
    # Replace curly/smart quotes with straight quotes
    replacements = {
        # Left and right single quotes
        '\u2018': "'",  # '
        '\u2019': "'",  # '
        '\u201b': "'",  # '

        # Left and right double quotes
        '\u201c': '"',  # "
        '\u201d': '"',  # "
        '\u201f': '"',  # "

        # Em dash and en dash
        '\u2014': '--',  # — → --
        '\u2013': '-',   # – → -

        # Other problematic characters
        '\u2026': '...',  # ellipsis …
        '\u00a0': ' ',    # non-breaking space
        '\u200b': '',     # zero-width space
        '\u200c': '',     # zero-width non-joiner
        '\u200d': '',     # zero-width joiner
    }

    for bad_char, good_char in replacements.items():
        text = text.replace(bad_char, good_char)

    return text


def demo_sanitizer():
    """Demonstrate the sanitizer with examples"""

    test_cases = [
        "Cohere's new open multilingual models are a game-changer",
        "Developers' work is enhanced by AI's capabilities",
        "It's important to don't overlook this",
        "The model's performance—improved significantly",
        '''Here's what we've learned: "it's working well"''',
    ]

    print("TEXT SANITIZER DEMO")
    print("=" * 70)
    print()

    for test in test_cases:
        original = test
        sanitized = sanitize_for_linkedin(test)

        # Only show if changed
        if original != sanitized:
            print(f"BEFORE:  {repr(original)}")
            print(f"AFTER:   {repr(sanitized)}")
            print(f"DISPLAY: {sanitized}")
            print()
        else:
            print(f"OK: {sanitized}")
            print()

    print("=" * 70)
    print("All problematic characters have been replaced!")


if __name__ == "__main__":
    demo_sanitizer()
