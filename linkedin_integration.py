"""
LinkedIn Integration - Posts approved content to LinkedIn using official API.
"""

import os
import time
from typing import Optional
from linkedin_oauth import is_linkedin_configured as oauth_configured
from linkedin_poster import post_with_auto_token
from utils import extract_linkedin_draft_safe


def is_linkedin_configured() -> bool:
    """
    Check if LinkedIn integration is properly configured.

    Returns:
        True if LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET are set
    """
    return oauth_configured()


def get_linkedin_setup_instructions() -> str:
    """
    Get instructions for setting up LinkedIn integration.

    Returns:
        String with setup instructions
    """
    return """
To enable LinkedIn integration:

1. Create a LinkedIn Developer account at:
   https://www.linkedin.com/developers/apps

2. Create a new application and configure:
   - Redirect URI: http://localhost:8000/callback
   - OAuth scopes: w_member_social (for posting)

3. Copy your credentials and add to .env:
   LINKEDIN_CLIENT_ID=your_client_id_here
   LINKEDIN_CLIENT_SECRET=your_client_secret_here
   LINKEDIN_REDIRECT_URI=http://localhost:8000/callback

4. Run authentication:
   python linkedin_oauth.py

This uses LinkedIn's official UGC API for posting.
"""


def post_to_linkedin(post_content: str) -> str:
    """
    Post content to LinkedIn using official API.

    Args:
        post_content: The LinkedIn post content

    Returns:
        URL of the posted LinkedIn update

    Raises:
        ValueError: If authentication not configured
        Exception: If posting fails
    """
    if not is_linkedin_configured():
        raise ValueError(
            "LinkedIn OAuth not configured. "
            "See get_linkedin_setup_instructions() for details."
        )

    return post_with_auto_token(post_content)


def get_page_status(page: dict) -> str:
    """
    Extract the status from a Notion page.

    Args:
        page: Notion page object

    Returns:
        Status name or empty string
    """
    status_prop = page.get("properties", {}).get("Status", {})

    # Handle 'status' type property
    if isinstance(status_prop, dict) and status_prop.get('type') == 'status':
        return status_prop.get('status', {}).get('name', '')

    # Handle 'select' type property (for backwards compatibility)
    if isinstance(status_prop, dict) and status_prop.get('type') == 'select':
        return status_prop.get('select', {}).get('name', '')

    return ''


def extract_linkedin_draft_from_notion(page_text: str) -> Optional[str]:
    """
    Extract the LinkedIn draft from a Notion page content with sanitization.
    Looks for "LINKEDIN POST:" sections (one per article).

    Args:
        page_text: The full page content from Notion

    Returns:
        The sanitized LinkedIn draft text, or None if not found
    """
    # Use safe extraction with sanitization
    return extract_linkedin_draft_safe(page_text)


def extract_linkedin_draft_with_option(page_text: str) -> tuple[Optional[str], str]:
    """
    Extract the LinkedIn draft and which article it came from.

    Args:
        page_text: The full page content from Notion

    Returns:
        Tuple of (draft_text, article_info) where article_info describes which article
        Returns (None, "") if not found
    """
    # Find all "LINKEDIN POST:" sections (case-insensitive)
    import re
    # Match both "LINKEDIN POST:" and "LinkedIn Post" with or without colon
    # Stop at double newline + marker OR end of string
    pattern = r'LINKEDIN POST\s*:?\s*\n(.*?)(?=\n\n(?:ARTICLE \d+|WHY THIS MATTERS|Article Details|OPTION)|\Z)'
    matches = re.findall(pattern, page_text, re.DOTALL | re.IGNORECASE)

    if matches:
        # Get the first LinkedIn post found
        draft = matches[0].strip()
        # Clean up any remaining metadata
        lines = draft.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            # Skip any metadata lines
            if line and not line.startswith('Article') and not line.startswith('http'):
                clean_lines.append(line)
        return '\n'.join(clean_lines).strip(), "Article 1"

    # Fallback to old format (LinkedIn Draft Post:)
    if "LinkedIn Draft Post:" not in page_text:
        return None, ""

    parts = page_text.split("LinkedIn Draft Post:")
    if len(parts) < 2:
        return None, ""

    draft_section = parts[1].strip()
    lines = draft_section.split('\n')
    draft_lines = []

    for line in lines:
        line = line.strip()
        if line.startswith('OPTION') and line != 'OPTION 1':
            break
        if not line and draft_lines and draft_lines[-1].strip() == '':
            break
        if line:
            draft_lines.append(line)

    if not draft_lines:
        return None, ""

    draft = '\n'.join(draft_lines).strip()
    return draft, "Default"


def post_approved_from_notion(database_id: str, poll_interval: int = 60) -> None:
    """
    Poll Notion database for approved posts and automatically publish to LinkedIn.

    Args:
        database_id: Notion database ID
        poll_interval: Seconds between polls (default: 60)

    Raises:
        ImportError: If notion-client not installed
        ValueError: If credentials not set
    """
    try:
        from notion_client import Client
    except ImportError:
        raise ImportError(
            "notion-client package not installed. "
            "Run: pip install notion-client"
        )

    notion_api_key = os.getenv("NOTION_API_KEY")
    if not notion_api_key:
        raise ValueError(
            "NOTION_API_KEY environment variable not set"
        )

    notion = Client(auth=notion_api_key)

    print(f"\n[Auto-Poster] Started polling for approved posts...")
    print(f"[Auto-Poster] Polling every {poll_interval} seconds")
    print(f"[Auto-Poster] Press Ctrl+C to stop\n")

    processed_pages = set()

    try:
        while True:
            # Search for pages in the database
            try:
                response = notion.search()
            except Exception as e:
                print(f"[Auto-Poster] Failed to search pages: {e}")
                time.sleep(poll_interval)
                continue

            # Filter pages from our database (handle both hyphenated and non-hyphenated IDs)
            all_pages = response.get("results", [])
            db_id_clean = database_id.replace('-', '')

            pages = [p for p in all_pages
                     if p.get("parent", {}).get("database_id", "").replace('-', '') == db_id_clean]

            if not pages:
                print(f"[Auto-Poster] No pages found from database, will retry in {poll_interval}s")
                time.sleep(poll_interval)
                continue

            for page in pages:
                page_id = page.get("id")

                # Skip if already processed
                if page_id in processed_pages:
                    continue

                # Check if page is approved
                status = get_page_status(page)
                if status != "Approved":
                    continue

                # Get page content
                page_content = notion.blocks.children.list(block_id=page_id)

                # Extract text from blocks (iterate all rich_text elements)
                page_text = ""
                for block in page_content.get("results", []):
                    block_type = block.get("type")

                    # Get all text from rich_text array
                    if block_type == "paragraph":
                        rich_text = block.get("paragraph", {}).get("rich_text", [])
                        for text_obj in rich_text:
                            page_text += text_obj.get("plain_text", "") + "\n"
                    elif block_type == "code":
                        rich_text = block.get("code", {}).get("rich_text", [])
                        for text_obj in rich_text:
                            page_text += text_obj.get("plain_text", "") + "\n"
                    elif block_type in ["heading_1", "heading_2", "heading_3"]:
                        rich_text = block.get(block_type, {}).get("rich_text", [])
                        for text_obj in rich_text:
                            page_text += text_obj.get("plain_text", "") + "\n"

                # Extract LinkedIn draft
                draft, option_used = extract_linkedin_draft_with_option(page_text)

                if draft:
                    try:
                        print(f"\n[Auto-Poster] Found approved post: {page.get('properties', {}).get('Title', {}).get('title', [{}])[0].get('plain_text', 'Unknown')}")
                        print(f"[Auto-Poster] Using: {option_used}")
                        print(f"[Auto-Poster] Draft content:")
                        print(f"---")
                        print(draft)
                        print(f"---")

                        # Post to LinkedIn
                        post_url = post_to_linkedin(draft)

                        # Update Notion status to "Posted" (find property dynamically)
                        try:
                            # Find status property
                            status_prop = None
                            status_type = None
                            for prop_name, prop_data in page.get("properties", {}).items():
                                if prop_data.get("type") in ["status", "select"]:
                                    if status_type != "status":
                                        status_prop = prop_name
                                        status_type = prop_data.get("type")
                                    if prop_data.get("type") == "status":
                                        status_prop = prop_name
                                        status_type = "status"
                                        break

                            if status_prop:
                                if status_type == "status":
                                    notion.pages.update(
                                        page_id=page_id,
                                        properties={
                                            status_prop: {
                                                "status": {
                                                    "name": "Posted"
                                                }
                                            }
                                        }
                                    )
                                else:  # "select" type
                                    notion.pages.update(
                                        page_id=page_id,
                                        properties={
                                            status_prop: {
                                                "select": {
                                                    "name": "Posted"
                                                }
                                            }
                                        }
                                    )
                                print(f"[Auto-Poster] Updated Notion status to 'Posted'")
                            else:
                                print(f"[Auto-Poster] Warning: No status property found")
                        except Exception as e:
                            print(f"[Auto-Poster] Could not update Notion status: {e}")
                            print(f"[Auto-Poster] (You may need to manually update it)")

                        print(f"\n[Auto-Poster] Successfully posted to LinkedIn!")
                        print(f"[Auto-Poster] Post URL: {post_url}")

                        # Mark as processed
                        processed_pages.add(page_id)

                    except Exception as e:
                        print(f"[Auto-Poster] Failed to post: {e}")
                        print(f"[Auto-Poster] Will retry on next poll")

            # Wait before next poll
            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print(f"\n\n[Auto-Poster] Stopped polling")
