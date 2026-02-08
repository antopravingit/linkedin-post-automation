"""
Extract Notion links from curator output for GitHub Actions
"""

import re
import sys

def extract_links():
    with open('generation.log', 'r') as f:
        content = f.read()

    # Extract Notion URLs
    urls = re.findall(r'https://www\.notion\.so/[^\s]+', content)

    if not urls:
        print('No Notion URLs found')
        sys.exit(1)

    print(f'Found {len(urls)} Notion pages')

    # Save URLs to file
    with open('notion_links.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')

    # Set GitHub output (for next steps)
    output_file = os.environ.get('GITHUB_OUTPUT')
    if output_file:
        with open(output_file, 'a') as f:
            f.write(f'urls={urls}\n')

    return urls

if __name__ == "__main__":
    import os
    extract_links()
