"""
Utility functions for text sanitization and validation.
"""

import html
import re
from typing import Optional


def sanitize_text(text: str, max_length: int = 3000) -> str:
    """
    Sanitize text for safe posting to LinkedIn.

    Removes HTML tags, escapes special characters, removes control characters,
    and truncates if too long. LinkedIn has a 3000 character limit.

    Args:
        text: Raw text to sanitize
        max_length: Maximum allowed length (LinkedIn has 3000 char limit)

    Returns:
        Sanitized text safe for posting
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # HTML escape any remaining special characters
    text = html.escape(text)

    # Remove control characters (except newline, tab, carriage return)
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + "..."

    return text


def extract_linkedin_draft_safe(page_text: str) -> Optional[str]:
    """
    Extract LinkedIn draft from Notion page with sanitization.

    Args:
        page_text: The full page content from Notion

    Returns:
        Sanitized LinkedIn draft text, or None if not found
    """
    # Find all "LINKEDIN POST:" sections (case-insensitive)
    import re
    pattern = r'LINKEDIN POST\s*:?\s*\n(.*?)(?=\n\n(?:ARTICLE \d+|WHY THIS MATTERS|Article Details|OPTION)|\Z)'
    matches = re.findall(pattern, page_text, re.DOTALL | re.IGNORECASE)

    if matches:
        draft = matches[0].strip()

        # Clean up metadata lines
        lines = draft.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            # Skip metadata lines
            if line and not line.startswith('Article') and not line.startswith('http'):
                clean_lines.append(line)

        draft = '\n'.join(clean_lines).strip()

        # Sanitize before returning
        return sanitize_text(draft, max_length=3000)

    return None


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if URL appears valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http or https
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}'  # domain
        r'|\[?\d{1,3}\]?\.\d{1,3}\.\d{1,3}\.\d{1,3}\])'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    return bool(url_pattern.match(url))
