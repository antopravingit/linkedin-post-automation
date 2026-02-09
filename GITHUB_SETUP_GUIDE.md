# GitHub Setup Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `linkedin-post-automation` (or whatever you prefer)
3. Description: `Automated LinkedIn content curation system with AI`
4. **IMPORTANT**: Leave "Initialize this repository" UNCHECKED
   - Don't add README
   - Don't add .gitignore
   - Don't choose a license
5. Click **"Create repository"**

## Step 2: Push Your Code

After creating the repository, GitHub will show you commands. Run these:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/linkedin-post-automation.git

# Push to GitHub
git push -u origin master
```

## Step 3: Add Secrets to GitHub

Once pushed, you need to add your API keys as secrets:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each secret:

### Add These Secrets:

**IMPORTANT:** Get your actual API keys from your services. See "How to Get Your API Keys" section below.

| Secret Name | How to Get It |
|------------|---------------|
| `OPENAI_API_KEY` | From https://platform.openai.com/api-keys |
| `NOTION_API_KEY` | From https://www.notion.so/my-integrations (click your integration, copy "Internal Integration Token") |
| `NOTION_DATABASE_ID` | From your Notion database URL (the 32-character string after `/` and before `?`) |
| `LINKEDIN_CLIENT_ID` | From https://www.linkedin.com/developers/apps |
| `LINKEDIN_CLIENT_SECRET` | From your LinkedIn app details |
| `SMTP_EMAIL` | Your Gmail address |
| `SMTP_PASSWORD` | Gmail app-specific password (not your regular password) |
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `NOTIFICATION_EMAIL` | Your notification email address |

### How to Get Your API Keys:

**Notion API Key:**
1. Go to https://www.notion.so/my-integrations
2. Find or create your integration
3. Copy the "Internal Integration Token" (starts with `ntn_`)
4. **IMPORTANT:** If your key was rotated, use the NEW token from Notion, not the old one

**Notion Database ID:**
1. Open your Notion database
2. Copy the URL - it looks like: `https://notion.so/workspace/[DATABASE_ID]?v=...`
3. The Database ID is the 32-character string between `/` and `?`

**LinkedIn Credentials:**
1. Go to https://www.linkedin.com/developers/apps
2. Create an app or use existing one
3. Copy Client ID and Client Secret

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy the key (starts with `sk-proj-`)

**Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not enabled
3. Go to "App passwords"
4. Generate a new app password for "Mail"
5. Copy the 16-character password

### Security Notes:

**NEVER commit actual API keys to public repositories!**
- GitHub secrets stay encrypted and private
- Files with secrets will be scanned and keys may be revoked
- Always use placeholders in documentation
- Keep a secure local backup of your keys (see SECRETS_BACKUP.md)

## Step 4: Enable GitHub Actions

1. Go to your repository
2. Click **Actions** tab
3. GitHub will ask: "Do you want to enable GitHub Actions?"
4. Click **"I understand my workflows, go ahead and enable them"**

## Step 5: Test It Out!

### Test 1: Manual Workflow Run
1. Go to **Actions** tab
2. Select **"Generate LinkedIn Content"** workflow
3. Click **"Run workflow"** button
4. Select branch: `master`
5. Click **"Run workflow"** (green button)
6. Watch it run in real-time!
7. Check your email for the 5 articles

### Test 2: Test Failure Notifications
1. Go to **Actions** tab
2. Select **"Test Failure Notification"** workflow
3. Click **"Run workflow"**
4. You'll get a failure test email

## What Happens Next

### Every Monday at 9 AM UTC:
- GitHub Actions runs automatically
- Discovers articles, selects top 5
- Creates Notion pages
- Sends you email with links

### Every 2 Hours:
- GitHub Actions checks Notion for approved articles
- Posts them to LinkedIn
- Updates status to "Posted"

### 1st of Every Month:
- GitHub Actions cleans up old Notion articles
- Sends you a cleanup report email

## Verification Checklist

After setup, you should have:
- [x] Code pushed to GitHub
- [x] All 8 secrets added
- [x] GitHub Actions enabled
- [x] Tested manual workflow run
- [x] Received email with 5 articles
- [x] Tested failure notifications

## Troubleshooting

**Workflow not running?**
- Check: Settings → Actions → General → Workflow permissions
- Make sure: "Read and write permissions" is enabled

**Not receiving emails?**
- Check: Secrets are correct (especially SMTP_EMAIL and SMTP_PASSWORD)
- Check: Gmail app password (not your regular password)

**LinkedIn posting failing?**
- Make sure you've completed LinkedIn OAuth at least once locally
- Check: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET are correct

## Success!

Once everything is set up:
- Your computer doesn't need to be on
- Articles generate automatically every Monday
- Posts go out every 2 hours
- You get email notifications for everything
- Database cleans up automatically

**Total time investment: ~10 minutes per week!**
