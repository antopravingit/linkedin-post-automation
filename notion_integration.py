"""
Notion Integration - Pushes approval packs to Notion for review.
"""

import os
from typing import Optional


def get_title_property_name(notion, db_id: str) -> str:
    """
    Detect the correct title property name in the Notion database.

    Args:
        notion: Notion client
        db_id: Database ID

    Returns:
        The name of the title property
    """
    try:
        database = notion.databases.retrieve(db_id)
        properties = database.get("properties", {})

        # Look for title property
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                print(f"[Notion] Detected title property: '{prop_name}'")
                return prop_name

        print("[Notion] No title property found, will use default")
        return "Title"
    except Exception as e:
        print(f"[Notion] Could not detect title property: {e}")
        return "Title"


def parse_article_content(article_text: str) -> dict:
    """
    Parse article content into sections.

    Args:
        article_text: Raw article text from approval pack

    Returns:
        Dictionary with sections: title, url, summary, why_matters, linkedin_post
    """
    import re

    result = {
        "title": "",
        "url": "",
        "summary": "",
        "why_matters": "",
        "linkedin_post": ""
    }

    # Extract article title
    title_match = re.search(r'ARTICLE \d+: ([^\n]+)', article_text)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Extract article URL
    url_match = re.search(r'Article URL: (https?://[^\s]+)', article_text)
    if url_match:
        result["url"] = url_match.group(1).strip()

    # Extract ARTICLE SUMMARY section
    summary_match = re.search(r'ARTICLE SUMMARY:(.*?)(?=WHY THIS MATTERS:|LINKEDIN POST:|$)', article_text, re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
        # Clean up bullet points (remove • or ✔ symbols)
        result["summary"] = re.sub(r'^[•\-\*]\s*', '', summary_text, flags=re.MULTILINE).strip()

    # Extract WHY THIS MATTERS section
    why_match = re.search(r'WHY THIS MATTERS:(.*?)(?=LINKEDIN POST:|$)', article_text, re.DOTALL)
    if why_match:
        result["why_matters"] = why_match.group(1).strip()

    # Extract LINKEDIN POST section
    post_match = re.search(r'LINKEDIN POST:(.*?)(?=ARTICLE \d+|$)', article_text, re.DOTALL)
    if post_match:
        result["linkedin_post"] = post_match.group(1).strip()

    return result


def create_notion_pages_for_articles(approval_pack: str, database_id: Optional[str] = None) -> list[str]:
    """
    Create separate Notion pages for each article in the approval pack.

    Args:
        approval_pack: The formatted approval pack with multiple articles
        database_id: Notion database ID (or from NOTION_DATABASE_ID env var)

    Returns:
        List of URLs of the created Notion pages
    """
    try:
        from notion_client import Client
    except ImportError:
        raise ImportError(
            "notion-client package not installed. "
            "Run: pip install notion-client"
        )

    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        raise ValueError(
            "NOTION_API_KEY environment variable not set. "
            "Create an integration at https://www.notion.so/my-integrations"
        )

    db_id = database_id or os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        raise ValueError(
            "NOTION_DATABASE_ID environment variable not set. "
            "Share a database with your integration and copy its ID from the URL."
        )

    notion = Client(auth=api_key)

    # Detect the correct title property name
    title_property = get_title_property_name(notion, db_id)

    page_urls = []

    # Split approval pack into individual articles
    import re
    article_pattern = r'ARTICLE \d+:.*?(?=ARTICLE \d+|$)'
    articles = re.findall(article_pattern, approval_pack, re.DOTALL)

    if not articles:
        # Fallback to single page mode
        print("[!] Could not find separate articles. Creating single page...")
        url = create_notion_page(approval_pack, database_id)
        return [url]

    print(f"\n[Notion] Creating {len(articles)} separate pages (one per article)...")

    for i, article_content in enumerate(articles, 1):
        # Get current date for the page title
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")

        # Extract article title
        title_match = re.search(r'ARTICLE \d+: ([^\n]+)', article_content)
        article_title = title_match.group(1).strip() if title_match else f"Article {i}"
        title = f"Article {i}: {article_title}"

        print(f"\n[Notion] Creating page for: {article_title}")

        # Create page with this article
        try:
            # Build properties dynamically with detected title property
            properties = {
                title_property: {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }

            # Try to add Status property if it exists
            try:
                database = notion.databases.retrieve(db_id)
                if "Status" in database.get("properties", {}):
                    properties["Status"] = {
                        "select": {
                            "name": "Draft"
                        }
                    }
            except Exception:
                # Status property doesn't exist or can't be detected - continue without it
                pass  # Keep properties as-is (without Status field)

            # Parse article content
            parsed = parse_article_content(article_content)

            # Build formatted Notion blocks
            children = []

            # Article Details heading
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Article Details"}}]
                }
            })

            # Article Title and URL
            if parsed["title"]:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Title: "}, "annotations": {"bold": True}},
                            {"type": "text", "text": {"content": parsed["title"]}}
                        ]
                    }
                })

            if parsed["url"]:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "URL: "}, "annotations": {"bold": True}},
                            {"type": "text", "text": {"content": parsed["url"]}, "annotations": {"code": True}, "href": parsed["url"]}
                        ]
                    }
                })

            # Summary heading
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "Summary"}}]
                }
            })

            # Summary bullet points
            if parsed["summary"]:
                summary_lines = [line.strip() for line in parsed["summary"].split('\n') if line.strip()]
                for line in summary_lines[:10]:  # Limit to 10 bullet points
                    children.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": line}}]
                        }
                    })

            # Why This Matters heading
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "Why This Matters"}}]
                }
            })

            # Why This Matters content
            if parsed["why_matters"]:
                children.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": parsed["why_matters"]}}],
                        "icon": {"emoji": "💡"}
                    }
                })

            # LinkedIn Post heading
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "LinkedIn Post"}}]
                }
            })

            # LinkedIn Post in quote block
            if parsed["linkedin_post"]:
                children.append({
                    "object": "block",
                    "type": "quote",
                    "quote": {
                        "rich_text": [{"type": "text", "text": {"content": parsed["linkedin_post"]}}]
                    }
                })

            # Add divider at the end
            children.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })

            response = notion.pages.create(
                parent={
                    "database_id": db_id
                },
                properties=properties,
                children=children
            )

            page_id = response["id"]
            page_url = notion.pages.retrieve(page_id)["url"]
            page_urls.append(page_url)

            print(f"    [+] Page {i} created: {page_url}")

        except Exception as e:
            print(f"    [!] Failed to create page {i}: {e}")

    print(f"\n[+] Created {len(page_urls)} Notion pages")
    return page_urls


def create_notion_page(approval_pack: str, database_id: Optional[str] = None) -> str:
    """
    Create a new page in Notion with the approval pack content.

    Args:
        approval_pack: The formatted approval pack content
        database_id: Notion database ID (or from NOTION_DATABASE_ID env var)

    Returns:
        URL of the created Notion page

    Raises:
        ImportError: If notion-client is not installed
        ValueError: If NOTION_API_KEY or database_id is not set
    """
    try:
        from notion_client import Client
    except ImportError:
        raise ImportError(
            "notion-client package not installed. "
            "Run: pip install notion-client"
        )

    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        raise ValueError(
            "NOTION_API_KEY environment variable not set. "
            "Create an integration at https://www.notion.so/my-integrations"
        )

    db_id = database_id or os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        raise ValueError(
            "NOTION_DATABASE_ID environment variable not set. "
            "Share a database with your integration and copy its ID from the URL."
        )

    notion = Client(auth=api_key)

    # Detect the correct title property name
    title_property = get_title_property_name(notion, db_id)

    # Get current date for the page title
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    title = f"LinkedIn Post Approval - {date_str}"

    print(f"\n[Notion] Creating page in database...")

    # First, try to create page with Status property
    try:
        # Build properties dynamically
        properties = {
            title_property: {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }

        # Try to add Status property
        try:
            database = notion.databases.retrieve(db_id)
            if "Status" in database.get("properties", {}):
                properties["Status"] = {
                    "select": {
                        "name": "Draft"
                    }
                }
        except:
            pass

        response = notion.pages.create(
            parent={
                "database_id": db_id
            },
            properties=properties,
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Approval Pack"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": approval_pack
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Review & Approval"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Review the approval pack above"
                            }
                        }
                    ],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Edit the LinkedIn draft if needed"
                            }
                        }
                    ],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Copy the draft and post to LinkedIn manually"
                            }
                        }
                    ],
                    "checked": False
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Update status to 'Posted' after publishing"
                            }
                        }
                    ],
                    "checked": False
                }
            }
        ]
    )

        page_id = response["id"]
        page_url = f"https://notion.so/{page_id.replace('-', '')}"

        print(f"[Notion] Page created successfully!")
        print(f"[Notion] URL: {page_url}")

        return page_url

    except Exception as e:
        # If Status property fails, try without it
        if "Status" in str(e) or "Name" in str(e):
            print(f"[Notion] Status property not compatible, creating without Status...")
            response = notion.pages.create(
                parent={
                    "database_id": db_id
                },
                properties={
                    title_property: {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Approval Pack"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": approval_pack
                                    }
                                }
                            ],
                            "language": "plain text"
                        }
                    },
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Review & Approval"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "to_do",
                        "to_do": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Review the approval pack above"
                                    }
                                }
                            ],
                            "checked": False
                        }
                    },
                    {
                        "object": "block",
                        "type": "to_do",
                        "to_do": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Edit the LinkedIn draft if needed"
                                    }
                                }
                            ],
                            "checked": False
                        }
                    },
                    {
                        "object": "block",
                        "type": "to_do",
                        "to_do": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Copy the draft and post to LinkedIn manually"
                                    }
                                }
                            ],
                            "checked": False
                        }
                    },
                    {
                        "object": "block",
                        "type": "to_do",
                        "to_do": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Update status to 'Posted' after publishing"
                                    }
                                }
                            ],
                            "checked": False
                        }
                    }
                ]
            )

            page_id = response["id"]
            page_url = f"https://notion.so/{page_id.replace('-', '')}"

            print(f"[Notion] Page created successfully (without Status property)!")
            print(f"[Notion] URL: {page_url}")

            return page_url
        else:
            raise


def is_notion_configured() -> bool:
    """
    Check if Notion integration is properly configured.

    Returns:
        True if NOTION_API_KEY and NOTION_DATABASE_ID are set
    """
    return bool(os.getenv("NOTION_API_KEY") and os.getenv("NOTION_DATABASE_ID"))


def get_notion_setup_instructions() -> str:
    """
    Get instructions for setting up Notion integration.

    Returns:
        String with setup instructions
    """
    return """
To enable Notion integration:

1. Create a Notion Integration:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Give it a name (e.g., "LinkedIn Curator")
   - Select your workspace
   - Copy the "Internal Integration Token" (this is NOTION_API_KEY)

2. Create a Database:
   - In Notion, create a new database
   - Add these columns/properties:
     * title (Title property)
     * Status (Select property with options: Draft, Approved, Posted)
   - Note the database ID from the URL (the 32-character string after /?v=)

3. Connect Integration to Database:
   - Open your database
   - Click "..." in the top-right
   - Select "Add connections"
   - Find and select your integration

4. Set Environment Variables:
   - NOTION_API_KEY=your_integration_token
   - NOTION_DATABASE_ID=your_database_id

You can set these in your system environment or in a .env file.
"""
