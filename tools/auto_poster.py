#!/usr/bin/env python3
"""
Auto-Poster - Checks Notion for approved posts and posts to LinkedIn
Designed to run once (not in a loop) for GitHub Actions
"""

import os
import sys
from notion_client import Client
from dotenv import load_dotenv

# Add parent directory to path to import from main package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from linkedin_integration import get_page_status, extract_linkedin_draft_from_notion, post_to_linkedin

notion_api_key = os.getenv('NOTION_API_KEY')
database_id = os.getenv('NOTION_DATABASE_ID')

if not notion_api_key or not database_id:
    print('[!] Missing NOTION_API_KEY or NOTION_DATABASE_ID')
    sys.exit(1)

notion = Client(auth=notion_api_key)

print('[Auto-Poster] Checking for approved posts...')

# Search for pages
response = notion.search()
all_pages = response.get('results', [])
db_id_clean = database_id.replace('-', '')

pages = [p for p in all_pages
         if p.get('parent', {}).get('database_id', '').replace('-', '') == db_id_clean]

posted_count = 0

for page in pages:
    page_id = page.get('id')
    status = get_page_status(page)

    if status == 'Approved':
        title_obj = page.get('properties', {}).get('Title', {}).get('title', [])
        title = title_obj[0].get('plain_text', 'Unknown') if title_obj else 'Unknown'

        print(f'[Auto-Poster] Found approved post: {title}')

        # Get content
        page_content = notion.blocks.children.list(block_id=page_id)
        page_text = ''

        for block in page_content.get('results', []):
            block_type = block.get('type')
            has_children = block.get('has_children', False)

            # Get all text from rich_text array (not just first element)
            text_content = ''
            if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3',
                              'bulleted_list_item', 'numbered_list_item', 'to_do',
                              'toggle', 'callout', 'quote']:
                rich_text = block.get(block_type, {}).get('rich_text', [])
                for text_obj in rich_text:
                    text_content += text_obj.get('plain_text', '')

            if block_type == 'code':
                rich_text = block.get('code', {}).get('rich_text', [])
                for text_obj in rich_text:
                    text_content += text_obj.get('plain_text', '')

            # Add to page_text
            if text_content:
                page_text += text_content + '\n'

            # If block has children, fetch them too
            if has_children:
                try:
                    children = notion.blocks.children.list(block_id=block.get('id'))
                    for child in children.get('results', []):
                        child_type = child.get('type')
                        child_text = ''
                        if child_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3',
                                          'bulleted_list_item', 'numbered_list_item']:
                            rich_text = child.get(child_type, {}).get('rich_text', [])
                            for text_obj in rich_text:
                                child_text += text_obj.get('plain_text', '')
                        if child_text:
                            page_text += child_text + '\n'
                except Exception as e:
                    # Log but don't fail - child blocks are optional
                    import sys
                    print(f'[Warning] Failed to fetch child blocks: {e}', file=sys.stderr)

        # Extract draft
        draft = extract_linkedin_draft_from_notion(page_text)

        if draft:
            try:
                print(f'[Auto-Poster] Posting to LinkedIn...')
                post_url = post_to_linkedin(draft)

                # Update Notion status
                notion.pages.update(
                    page_id=page_id,
                    properties={
                        'Status': {
                            'status': {
                                'name': 'Posted'
                            }
                        }
                    }
                )

                print(f'[Auto-Poster] Successfully posted!')
                print(f'[Auto-Poster] Post URL: {post_url}')
                posted_count += 1

            except Exception as e:
                print(f'[Auto-Poster] Failed to post: {e}')
                print(f'[Auto-Poster] Continuing to next post...')
        else:
            print(f'[Auto-Poster] No LinkedIn draft found')

print(f'[Auto-Poster] Posted {posted_count} post(s)')

# Exit with error if no posts were made but there were approved items
if posted_count == 0:
    approved_count = sum(1 for p in pages if get_page_status(p) == 'Approved')
    if approved_count > 0:
        print(f'[Auto-Poster] Warning: {approved_count} approved post(s) could not be posted')
        sys.exit(1)
