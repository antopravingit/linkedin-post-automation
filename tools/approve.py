"""
Simple CLI tool to review and approve LinkedIn posts
"""

import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

try:
    from notion_client import Client
except ImportError:
    print("[!] notion-client not installed. Run: pip install notion-client")
    exit(1)


def get_pending_articles():
    """Get all articles with 'Draft' status from Notion."""
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    notion = Client(auth=api_key)

    print("[*] Fetching pending articles from Notion...")
    print()

    try:
        # Query database for pages with Draft status
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Status",
                "select": {
                    "equals": "Draft"
                }
            }
        )

        pages = response.get("results", [])

        if not pages:
            print("[+] No pending articles found!")
            print()
            print("All articles have been reviewed. Great job!")
            return []

        return pages

    except Exception as e:
        print(f"[!] Error fetching articles: {e}")
        print()
        print("Make sure your Notion database has a 'Status' property.")
        return []


def display_articles(pages):
    """Display articles in a numbered list."""
    print("=" * 70)
    print(f"PENDING ARTICLES: {len(pages)} articles to review")
    print("=" * 70)
    print()

    for i, page in enumerate(pages, 1):
        # Get title
        title = "Untitled"
        props = page.get("properties", {})
        if "Title" in props:
            title_text = props["Title"].get("title", [])
            if title_text:
                title = title_text[0].get("plain_text", "Untitled")

        # Get URL
        url = f"https://notion.so/{page['id'].replace('-', '')}"

        print(f"{i}. {title}")
        print(f"   URL: {url}")
        print()

    print("-" * 70)
    print()
    print("Commands:")
    print("  approve <number>     - Approve article (e.g., 'approve 1' or 'approve 1 3 5')")
    print("  delete <number>      - Delete article (e.g., 'delete 2')")
    print("  open <number>        - Open article in browser")
    print("  list                 - Show pending articles again")
    print("  quit                 - Exit")
    print()


def approve_page(page_id: str):
    """Change page status to Approved."""
    api_key = os.getenv("NOTION_API_KEY")
    notion = Client(auth=api_key)

    try:
        notion.pages.update(
            page_id=page_id,
            properties={
                "Status": {
                    "select": {
                        "name": "Approved"
                    }
                }
            }
        )
        return True
    except Exception as e:
        print(f"[!] Error approving page: {e}")
        return False


def delete_page(page_id: str):
    """Delete a page from Notion."""
    api_key = os.getenv("NOTION_API_KEY")
    notion = Client(auth=api_key)

    try:
        notion.pages.delete(page_id)
        return True
    except Exception as e:
        print(f"[!] Error deleting page: {e}")
        return False


def interactive_approval():
    """Interactive approval session."""
    pages = get_pending_articles()

    if not pages:
        return

    display_articles(pages)

    while True:
        try:
            cmd = input("Enter command (or 'quit' to exit): ").strip().lower()

            if not cmd:
                continue

            if cmd in ['quit', 'exit', 'q']:
                print()
                print("[+] Exiting. Remaining articles stay in Draft status.")
                break

            if cmd == 'list':
                pages = get_pending_articles()
                if pages:
                    display_articles(pages)
                continue

            parts = cmd.split()
            action = parts[0]

            if action == 'approve':
                # Approve one or more articles
                numbers = [int(n) for n in parts[1:]]
                for num in numbers:
                    if 1 <= num <= len(pages):
                        page = pages[num - 1]
                        page_id = page['id']
                        title = page.get("properties", {}).get("Title", {}).get("title", [{}])[0].get("plain_text", "Untitled")

                        if approve_page(page_id):
                            print(f"  [+] Approved: {title}")
                    else:
                        print(f"  [!] Invalid number: {num}")

            elif action == 'delete':
                # Delete one or more articles
                numbers = [int(n) for n in parts[1:]]
                for num in sorted(numbers, reverse=True):  # Delete from high to low to maintain indices
                    if 1 <= num <= len(pages):
                        page = pages[num - 1]
                        page_id = page['id']
                        title = page.get("properties", {}).get("Title", {}).get("title", [{}])[0].get("plain_text", "Untitled")

                        if delete_page(page_id):
                            print(f"  [+] Deleted: {title}")
                            pages.pop(num - 1)
                    else:
                        print(f"  [!] Invalid number: {num}")

                if pages:
                    print()
                    print("[*] Remaining articles:")
                    display_articles(pages)

            elif action == 'open':
                # Open in browser
                import webbrowser
                numbers = [int(n) for n in parts[1:]]
                for num in numbers:
                    if 1 <= num <= len(pages):
                        page = pages[num - 1]
                        url = f"https://notion.so/{page['id'].replace('-', '')}"
                        webbrowser.open(url)
                        print(f"  [+] Opening article {num} in browser...")

            else:
                print("[!] Unknown command. Try 'approve', 'delete', 'open', 'list', or 'quit'")

            print()

        except KeyboardInterrupt:
            print("\n\n[+] Exiting. Remaining articles stay in Draft status.")
            break
        except (ValueError, IndexError) as e:
            print(f"[!] Invalid input. Use command format like 'approve 1' or 'delete 2 3'")
            print()


if __name__ == "__main__":
    print("=" * 70)
    print("LINKEDIN ARTICLE APPROVAL TOOL")
    print("=" * 70)
    print()

    interactive_approval()
