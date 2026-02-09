"""
Send failure notification for GitHub Actions
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def send_failure_notification(workflow_name: str, error_message: str = ""):
    """Send email notification when workflow fails."""
    # Check if email is configured
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not smtp_email or not smtp_password:
        print('[*] Email not configured, skipping failure notification')
        return 0

    # SMTP configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    recipient = os.getenv('NOTIFICATION_EMAIL', smtp_email)

    # Create email
    msg = MIMEMultipart()
    msg['Subject'] = f'❌ FAILED: {workflow_name} - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    msg['From'] = smtp_email
    msg['To'] = recipient

    # Email body
    error_details = error_message if error_message else "(no additional details)"

    body = f'''
⚠️ WORKFLOW FAILURE ALERT ⚠️

Workflow: {workflow_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC

The GitHub Actions workflow has FAILED.

Error details:
{error_details}

What you should do:
1. Check the GitHub Actions tab for detailed logs
2. Look at the uploaded artifacts (logs) for more information
3. Fix the issue and re-run manually if needed

GitHub Actions URL:
https://github.com/YOUR_USERNAME/YOUR_REPO/actions

Don't worry, this happens! Just check the logs and fix it.
'''

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()

        print(f'[+] Failure notification sent to {recipient}')
        return 0

    except Exception as e:
        print(f'[!] Failed to send failure notification: {e}')
        return 1


if __name__ == "__main__":
    import sys

    workflow_name = sys.argv[1] if len(sys.argv) > 1 else "GitHub Actions Workflow"
    error_msg = sys.argv[2] if len(sys.argv) > 2 else ""

    sys.exit(send_failure_notification(workflow_name, error_msg))
