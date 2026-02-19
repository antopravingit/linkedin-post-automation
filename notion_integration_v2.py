#!/usr/bin/env python3
"""Improved Notion Integration - Better formatting for LinkedIn posts"""

import os
from notion_client import Client
from text_sanitizer import sanitize_for_linkedin


def create_notion_page_improved(approval_pack, title=None):
    """Create a Notion page with paragraph blocks instead of code block"""

    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_DATABASE_ID")

    if not api_key or not db_id:
        raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID must be set")

    notion = Client(auth=api_key)

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

    # Extract post content
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
            post_content.append(line.strip())

    # Add paragraphs
    for para in post_content:
        if para:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": para}}]
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

    # Create page
    response = notion.pages.create(
        parent={"database_id": db_id},
        properties={
            "Title": {"title": [{"text": {"content": page_title}}]},
            "Status": {"status": {"name": "Draft"}}
        },
        children=children
    )

    page_url = f"https://notion.so/{response['id'].replace('-', '')}"
    print(f"[Notion] Page created: {page_url}")
    return page_url


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    sample = """
LINKEDIN POST:

Sarah Chen showed me a technique for LLM hallucinations.

She demonstrated a fact-checking approach using opposing viewpoints.

What I love about this approach is how simple but effective it is.

This is why I value working with smart people.

APPROVAL INSTRUCTIONS:
Review and edit as needed
"""

    try:
        url = create_notion_page_improved(sample, "Test Post - Improved")
        print(f"Success: {url}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
