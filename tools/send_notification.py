"""
Send email notification for GitHub Actions
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def send_notification():
    # Check if email is configured
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not smtp_email or not smtp_password:
        print('[*] Email not configured, skipping notification')
        print('[*] To enable email, add SMTP_EMAIL and SMTP_PASSWORD to GitHub Secrets')
        return 0

    # Read URLs
    try:
        with open('notion_links.txt', 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('[*] No notion_links.txt file found')
        return 0

    if not urls:
        print('[*] No URLs to send')
        return 0

    # SMTP configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    recipient = os.getenv('NOTIFICATION_EMAIL', smtp_email)

    # Create email
    article_count = len(urls)
    msg = MIMEMultipart()
    msg['Subject'] = f'{article_count} LinkedIn Articles Ready for Review - {datetime.now().strftime("%Y-%m-%d")}'
    msg['From'] = smtp_email
    msg['To'] = recipient

    # Email body
    body = f'''
{article_count} new LinkedIn article{"s" if article_count != 1 else ""} ready for your review (mix of technical + general).

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

ARTICLES TO REVIEW:
{'=' * 60}
'''

    for i, url in enumerate(urls, 1):
        body += f'\n{i}. {url}\n'

    body += f'''
{'=' * 60}

NEXT STEPS:
1. Click each link to review the article in Notion
2. Keep the ones you like, delete the others
3. Change status to "Approved" for articles you want to post
4. Auto-poster will post them to LinkedIn

Or run locally: python approve.py
'''

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()

        print(f'[+] Email notification sent to {recipient}')
        print(f'    {len(urls)} articles ready for review')
        return 0

    except Exception as e:
        print(f'[!] Failed to send email: {e}')
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(send_notification())
