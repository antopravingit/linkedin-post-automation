#!/usr/bin/env python3
"""
Notion Database Cleanup Tool

Cleans up old articles from your Notion database based on status and age.

Usage:
    python tools/cleanup_notion.py                    # Interactive mode
    python tools/cleanup_notion.py --older-than 7     # Delete Notion pages older than 7 days
    python tools/cleanup_notion.py --status "Not Reviewed"  # Delete specific status
"""

import os
import sys
from datetime import datetime, timedelta
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()


def cleanup_notion(days_old=30, status=None, dry_run=True):
    """
    Clean up Notion database by deleting old articles.

    Args:
        days_old: Delete articles older than this many days (default: 30)
        status: Only delete articles with this status (None = all statuses)
        dry_run: If True, show what would be deleted without actually deleting
    """
    try:
        notion_api_key = os.getenv('NOTION_API_KEY')
        database_id = os.getenv('NOTION_DATABASE_ID')

        if not notion_api_key or not database_id:
            print('[!] Missing NOTION_API_KEY or NOTION_DATABASE_ID')
            print('[!] Add them to your .env file')
            return 1

        notion = Client(auth=notion_api_key)

        print(f"[*] Cleaning up Notion database...")
        print(f"    Database ID: {database_id}")
        print(f"    Articles older than: {days_old} days")
        if status:
            print(f"    Status filter: {status}")
        print(f"    Mode: {'DRY RUN (no actual deletion)' if dry_run else 'LIVE (will delete)'}")
        print(f"    Current date: {datetime.now().strftime('%Y-%m-%d')}")
        print()

        # Search for pages in the database
        print("[*] Searching Notion database...")
        response = notion.search()
        all_pages = response.get('results', [])
        print(f"[*] Notion search returned {len(all_pages)} total items")

        db_id_clean = database_id.replace('-', '')
        print(f"[*] Looking for database ID: {db_id_clean}")

        # Filter pages from our database
        pages = [p for p in all_pages
                 if p.get('parent', {}).get('database_id', '').replace('-', '') == db_id_clean]

        print(f"[+] Found {len(pages)} total pages in target database\n")

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_old)
        pages_to_delete = []

        for page in pages:
            page_id = page.get('id')
            created_time = page.get('created_time')
            page_status = get_page_status(page)
            title_obj = page.get('properties', {}).get('Title', {}).get('title', [])
            title = title_obj[0].get('plain_text', 'Unknown') if title_obj else 'Unknown'

            # Parse created time and remove timezone info for comparison
            try:
                created_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                # Remove timezone info to make comparison work
                created_date = created_date.replace(tzinfo=None)
            except:
                continue

            # Check if page matches criteria
            matches_age = created_date < cutoff_date
            matches_status = status is None or page_status == status

            # Also check for specific statuses that indicate "junk"
            # e.g., "Not Reviewed" articles that are old
            is_junk = page_status in ["Not Reviewed", "Draft", None] and matches_age

            if matches_age and (matches_status or is_junk):
                pages_to_delete.append({
                    'id': page_id,
                    'title': title,
                    'status': page_status,
                    'created': created_date,
                    'age_days': (datetime.now() - created_date).days
                })

        if not pages_to_delete:
            print("[*] No pages to delete. Database is clean!")
            print(f"[*] Checked {len(pages)} pages, none matched deletion criteria")
            print(f"[*] Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")
            return 0

        # Show pages that would be deleted
        print(f"[*] Found {len(pages_to_delete)} page(s) to delete:\n")
        for i, page in enumerate(pages_to_delete, 1):
            print(f"  {i}. {page['title']}")
            print(f"     Status: {page['status'] or 'No status'}")
            print(f"     Created: {page['created'].strftime('%Y-%m-%d')}")
            print(f"     Age: {page['age_days']} days")
            print()

        # Confirm deletion
        if dry_run:
            print("[*] This was a DRY RUN. No pages were deleted.")
            print(f"[*] Run with --no-dry-run to actually delete {len(pages_to_delete)} pages")
            return 0

        # Check if running in CI environment (GitHub Actions, etc.)
        is_ci = os.environ.get('CI', '').lower() == 'true'

        # Actual deletion
        if not is_ci:
            confirm = input(f"\n[!] Delete {len(pages_to_delete)} pages? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("[*] Cancelled. No pages deleted.")
                return 0
        else:
            print(f"[*] Running in CI mode - auto-confirming deletion of {len(pages_to_delete)} pages")

        print(f"\n[*] Deleting {len(pages_to_delete)} pages...")
        deleted_count = 0

        for page in pages_to_delete:
            try:
                notion.blocks.delete(block_id=page['id'])
                deleted_count += 1
                print(f"  [+] Deleted: {page['title'][:50]}...")
            except Exception as e:
                print(f"  [!] Failed to delete {page['title']}: {e}")

        print(f"\n[+] Successfully deleted {deleted_count}/{len(pages_to_delete)} pages")
        return 0

    except Exception as e:
        print(f"[!] ERROR: {str(e)}")
        import traceback
        print(f"[!] Traceback: {traceback.format_exc()}")
        return 1


def get_page_status(page):
    """Extract status from Notion page."""
    status_prop = page.get('properties', {}).get('Status', {})
    if status_prop.get('type') == 'status':
        return status_prop.get('status', {}).get('name', '')
    return ''


def interactive_mode():
    """Interactive mode for cleanup."""
    print("\n" + "=" * 60)
    print("NOTION DATABASE CLEANUP")
    print("=" * 60)

    try:
        days_input = input("\nDelete articles older than how many days? (default 30): ").strip()
        days_old = int(days_input) if days_input else 30

        print("\nStatus options:")
        print("  1. All statuses")
        print("  2. Only 'Not Reviewed'")
        print("  3. Only 'Draft'")
        print("  4. Custom status name")

        status_choice = input("\nSelect status filter (default 1): ").strip() or '1'

        status_map = {
            '1': None,
            '2': 'Not Reviewed',
            '3': 'Draft'
        }

        status = status_map.get(status_choice)
        if status_choice == '4':
            status = input("Enter status name: ").strip()

        print("\nMode:")
        print("  1. Dry run (show what would be deleted)")
        print("  2. Live run (actually delete)")

        mode_choice = input("\nSelect mode (default 1): ").strip() or '1'
        dry_run = mode_choice == '1'

        print()
        cleanup_notion(days_old=days_old, status=status, dry_run=dry_run)

    except KeyboardInterrupt:
        print("\n\n[*] Cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Clean up Notion database')
    parser.add_argument('--older-than', type=int, default=30,
                        help='Delete articles older than N days (default: 30)')
    parser.add_argument('--status', type=str, default=None,
                        help='Only delete articles with this status')
    parser.add_argument('--no-dry-run', action='store_true',
                        help='Actually delete pages (default is dry-run)')

    args = parser.parse_args()

    # If no arguments provided, run interactive mode
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        cleanup_notion(days_old=args.older_than, status=args.status, dry_run=not args.no_dry_run)
