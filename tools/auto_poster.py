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
            # Handle all block types that can contain text
            if block.get('type') == 'paragraph':
                text = block['paragraph'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'heading_1':
                text = block['heading_1'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'heading_2':
                text = block['heading_2'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'heading_3':
                text = block['heading_3'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'bulleted_list_item':
                text = block['bulleted_list_item'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'numbered_list_item':
                text = block['numbered_list_item'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'to_do':
                text = block['to_do'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'toggle':
                text = block['toggle'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'callout':
                text = block['callout'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'quote':
                text = block['quote'].get('rich_text', [])
                if text:
                    page_text += text[0].get('plain_text', '') + '\n'
            elif block.get('type') == 'code':
                code = block['code'].get('rich_text', [])
                if code:
                    page_text += code[0].get('plain_text', '') + '\n'

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
