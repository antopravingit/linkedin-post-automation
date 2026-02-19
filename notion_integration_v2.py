#!/usr/bin/env python3
"""
Improved Notion Integration - Better formatting for LinkedIn posts

Fixed:
- Dynamic property detection (no hardcoded names)
- Text sanitization applied before storage
- Full rich_text iteration
- Status type detection
- Content length validation
"""

import os
from notion_client import Client
from text_sanitizer import sanitize_for_linkedin
from notion_helper import NotionDatabaseHelper


def create_notion_page_improved(approval_pack, title=None, post_type="Article"):
    """
    Create a Notion page with paragraph blocks instead of code block.

    Args:
        approval_pack: The formatted approval pack content
        title: Optional custom title for the page
        post_type: Type of post (Personal, Colleague, Tech, Community, Article)

    Returns:
        URL of the created Notion page
    """

    notion_helper = NotionDatabaseHelper()

    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    page_title = title or f"LinkedIn Post - {date_str}"

    print(f"\n[Notion] Creating page with improved formatting...")

    # Parse content and build blocks
    children = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "LinkedIn Post"}}]
            }
        },
        {"object": "block", "type": "divider", "divider": {}}
    ]

    # Extract and sanitize post content
    lines = approval_pack.split('\n')
    in_post = False
    post_content = []

    for line in lines:
        if "LINKEDIN POST:" in line.upper():
            in_post = True
            continue
        if "APPROVAL" in line.upper() or "INSTRUCTIONS" in line.upper():
            break
        if in_post and line.strip():
            # Sanitize each line to avoid encoding issues
            sanitized_line = sanitize_for_linkedin(line.strip())
            post_content.append(sanitized_line)

    # Combine into paragraphs (double newline = new paragraph)
    current_para = []
    for line in post_content:
        if not line:  # Empty line = paragraph break
            if current_para:
                para_text = ' '.join(current_para)
                # Validate length before adding
                if len(para_text) > 3000:
                    para_text = para_text[:2997] + "..."
                    print(f"[Notion] Warning: Content truncated to 3000 chars")
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": para_text}}]
                    }
                })
                current_para = []
        else:
            current_para.append(line)

    # Add remaining paragraph
    if current_para:
        para_text = ' '.join(current_para)
        if len(para_text) > 3000:
            para_text = para_text[:2997] + "..."
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": para_text}}]
            }
        })

    # Add approval section
    children.extend([
        {"object": "block", "type": "divider", "divider": {}},
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Review & Approval"}}]
            }
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Review the post content"}}],
                "checked": False
            }
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Edit if needed"}}],
                "checked": False
            }
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": "Change status to Approved when ready"}}],
                "checked": False
            }
        }
    ])

    # Build properties dynamically using helper
    properties = notion_helper.build_page_properties(
        title=page_title,
        status="Draft",
        Type=post_type
    )

    # Create page with retry for rate limits
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            response = notion_helper.notion.pages.create(
                parent={"database_id": notion_helper.database_id},
                properties=properties,
                children=children
            )
            break
        except Exception as e:
            error_str = str(e).lower()
            if 'rate limit' in error_str or '429' in error_str:
                if attempt < max_retries - 1:
                    print(f"[Notion] Rate limited, retrying in {retry_delay}s...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
            raise  # Re-raise if not rate limit or out of retries

    page_url = f"https://notion.so/{response['id'].replace('-', '')}"
    print(f"[Notion] Page created: {page_url}")
    return page_url


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    sample = """
LINKEDIN POST:

Sarah Chen showed me a technique for LLM hallucinations.

She demonstrated a fact-checking approach using opposing viewpoints—I hadn't considered this before.

What I love about this approach is how simple but effective it is.

This is why I value working with smart people—they always have different perspectives that teach me something new.

APPROVAL INSTRUCTIONS:
Review and edit as needed
"""

    try:
        url = create_notion_page_improved(sample, "Test Post - Improved", "Colleague")
        print(f"Success: {url}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
