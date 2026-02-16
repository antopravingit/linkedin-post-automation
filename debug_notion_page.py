#!/usr/bin/env python3
"""
Debug tool to check what content the auto-poster sees from Notion
"""

import os
import sys
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion_api_key = os.getenv('NOTION_API_KEY')
database_id = os.getenv('NOTION_DATABASE_ID')

if not notion_api_key or not database_id:
    print('[!] Missing NOTION_API_KEY or NOTION_DATABASE_ID')
    sys.exit(1)

notion = Client(auth=notion_api_key)

print('[*] Searching for pages in your database...')

# Search for pages
response = notion.search()
all_pages = response.get('results', [])
db_id_clean = database_id.replace('-', '')

pages = [p for p in all_pages
         if p.get('parent', {}).get('database_id', '').replace('-', '') == db_id_clean]

print(f'[+] Found {len(pages)} pages\n')

for page in pages:
    page_id = page.get('id')
    title_obj = page.get('properties', {}).get('Title', {}).get('title', [])
    title = title_obj[0].get('plain_text', 'Unknown') if title_obj else 'Unknown'
    status = page.get('properties', {}).get('Status', {}).get('status', {}).get('name', 'No status')

    print(f"\n{'='*70}")
    print(f"Page: {title}")
    print(f"Status: {status}")
    print(f"{'='*70}")

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
            except:
                pass

    print(f"\n[*] Raw content from Notion API:")
    print(f"{'-'*70}")
    print(page_text)
    print(f"{'-'*70}")

    # Check for LINKEDIN POST
    if 'LINKEDIN POST:' in page_text:
        print(f"\n[+] ✓ Found 'LINKEDIN POST:' in content")

        # Try to extract
        import re
        pattern = r'LINKEDIN POST:\s*\n(.*?)(?=\n\n(?:ARTICLE \d+|WHY THIS MATTERS|OPTION|\Z))'
        matches = re.findall(pattern, page_text, re.DOTALL)

        if matches:
            print(f"[+] ✓ Regex pattern matched successfully")
            print(f"\nExtracted draft:")
            print(f"{'-'*70}")
            print(matches[0].strip())
            print(f"{'-'*70}")
        else:
            print(f"[!] ✗ Regex pattern did NOT match")
            print(f"\n[*] This means 'LINKEDIN POST:' was found but the extraction pattern failed.")
            print(f"[*] Usually because content after 'LINKEDIN POST:' doesn't end with:")
            print(f"    - Double newline + 'ARTICLE N'")
            print(f"    - Double newline + 'WHY THIS MATTERS'")
            print(f"    - Double newline + 'OPTION'")
            print(f"    - End of content")
    else:
        print(f"\n[!] ✗ 'LINKEDIN POST:' NOT found in content")
        print(f"[*] The auto-poster will skip this page")

print(f"\n{'='*70}")
print("[*] Debug complete!")
print(f"{'='*70}")
