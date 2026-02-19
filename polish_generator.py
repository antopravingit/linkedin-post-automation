#!/usr/bin/env python3
"""
Polish Generator - Enhance user-provided content while maintaining voice.

Provides intelligent polishing of draft content without losing the author's authentic voice.
"""

import os
from typing import Optional


def polish_with_claude(draft_content: str, context: str = "") -> str:
    """
    Polish content using Claude API while maintaining user's voice.

    Args:
        draft_content: User's draft content
        context: Additional context about the content

    Returns:
        Polished LinkedIn post
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = """You are an expert at polishing LinkedIn posts while maintaining the author's authentic voice.

Your job:
1. Fix grammar and spelling
2. Improve flow and readability
3. Suggest better word choices (but don't change meaning)
4. Adjust length for LinkedIn (3-10 lines ideally)
5. Add a strong hook if missing
6. Keep the author's voice and personality intact
7. Don't add information they didn't provide
8. Remove any filler or redundancy

CRITICAL: The result must sound like THE SAME PERSON wrote it, just better.

Output ONLY the polished post, no explanations or meta-commentary."""

    user_message = f"""Polish this LinkedIn post for me:

{draft_content}

{context}

Requirements:
- Keep my voice and personality
- Fix grammar and improve flow
- Make it more engaging
- Keep it to 3-10 lines
- Don't add new information
- Don't change my meaning

Output ONLY the polished post."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        temperature=0.7,  # Lower for polishing to maintain voice
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    return response.content[0].text.strip()


def polish_with_openai(draft_content: str, context: str = "") -> str:
    """Polish content using OpenAI API."""
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    system_prompt = """You are an expert at polishing LinkedIn posts while maintaining the author's authentic voice.

Your job:
1. Fix grammar and spelling
2. Improve flow and readability
3. Suggest better word choices (but don't change meaning)
4. Adjust length for LinkedIn (3-10 lines ideally)
5. Add a strong hook if missing
6. Keep the author's voice and personality intact
7. Don't add information they didn't provide
8. Remove any filler or redundancy

CRITICAL: The result must sound like THE SAME PERSON wrote it, just better.

Output ONLY the polished post, no explanations or meta-commentary."""

    user_message = f"""Polish this LinkedIn post for me:

{draft_content}

{context}

Requirements:
- Keep my voice and personality
- Fix grammar and improve flow
- Make it more engaging
- Keep it to 3-10 lines
- Don't add new information
- Don't change my meaning

Output ONLY the polished post."""

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content.strip()


def format_polished_pack(original: str, polished: str) -> str:
    """Format polished content as approval pack."""
    from datetime import datetime

    date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""CONTENT POLISHER
Processed: {date_str}

{"=" * 70}

ORIGINAL DRAFT:
{original}

{"=" * 70}

POLISHED VERSION:
{polished}

{"=" * 70}

NEXT STEPS:
1. Compare original and polished versions
2. Ensure your voice is maintained
3. Make any final edits
4. Post to LinkedIn when ready
"""


def polish_content(draft_content: str, context: str = "") -> tuple[str, str]:
    """
    Polish user content using available AI provider.

    Args:
        draft_content: User's draft content
        context: Additional context

    Returns:
        Tuple of (polished_content, provider_used)
    """
    # Determine provider
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            polished = polish_with_claude(draft_content, context)
            return polished, "Claude"
        except Exception as e:
            print(f"[!] Claude polishing failed: {e}")

    if os.getenv("OPENAI_API_KEY"):
        try:
            polished = polish_with_openai(draft_content, context)
            return polished, "OpenAI"
        except Exception as e:
            print(f"[!] OpenAI polishing failed: {e}")

    # Fallback: return original
    print("[!] AI polishing unavailable, returning original")
    return draft_content, "None"
