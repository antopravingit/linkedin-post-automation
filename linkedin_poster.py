"""
LinkedIn Poster - Posts content using LinkedIn's official UGC API
"""

import os
import requests
from typing import Optional
from linkedin_oauth import load_access_token, is_linkedin_configured


def post_to_linkedin_ugc(post_content: str, access_token: str) -> str:
    """
    Post content to LinkedIn using the official UGC API.

    Args:
        post_content: The LinkedIn post content
        access_token: Valid OAuth access token

    Returns:
        URL of the posted LinkedIn update

    Raises:
        ValueError: If access_token is invalid
        Exception: If posting fails
    """
    # Get user profile (to get the person URN)
    print("[LinkedIn] Getting profile...")

    profile_url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    response = requests.get(profile_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to get profile: {response.text}")

    profile_data = response.json()
    person_urn = profile_data.get('sub')

    if not person_urn:
        raise Exception("Could not get person URN from profile")

    print(f"[LinkedIn] Profile URN: {person_urn}")

    # Create the post using UGC API
    print("[LinkedIn] Creating post...")

    # Get LinkedIn ID from person URN (format: urn:li:person:ABC123)
    if person_urn.startswith('urn:li:person:'):
        person_id = person_urn.replace('urn:li:person:', '')
    else:
        person_id = person_urn

    # Construct the UGC post
    ugc_url = "https://api.linkedin.com/v2/ugcPosts"

    post_data = {
        "author": f"urn:li:person:{person_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202401'
    }

    response = requests.post(ugc_url, json=post_data, headers=headers)

    if response.status_code != 201:
        raise Exception(f"Failed to create post: {response.status_code} - {response.text}")

    post_response = response.json()

    # Extract the post URN
    post_urn = post_response.get('id')

    if not post_urn:
        raise Exception("Post created but no ID returned")

    # Construct post URL
    post_url = f"https://www.linkedin.com/feed/update/{post_urn}"

    print(f"[LinkedIn] Post created successfully!")
    print(f"[LinkedIn] Post URN: {post_urn}")
    print(f"[LinkedIn] URL: {post_url}")

    return post_url


def post_with_auto_token(post_content: str) -> str:
    """
    Post to LinkedIn, automatically loading access token.

    Args:
        post_content: The LinkedIn post content

    Returns:
        URL of the posted LinkedIn update

    Raises:
        ValueError: If authentication not configured
        Exception: If posting fails
    """
    if not is_linkedin_configured():
        raise ValueError(
            "LinkedIn OAuth not configured. "
            "Please run: python linkedin_oauth.py"
        )

    # Load or get access token
    access_token = load_access_token()

    if not access_token:
        raise Exception(
            "No valid access token found. "
            "Please run: python linkedin_oauth.py"
        )

    # Post using the token
    return post_to_linkedin_ugc(post_content, access_token)


if __name__ == "__main__":
    # Test posting
    test_content = """This is a test post from the LinkedIn AI Content Curator tool.

If you can see this, the official LinkedIn API integration is working!"""

    try:
        post_url = post_with_auto_token(test_content)
        print(f"\n[+] Test successful!")
        print(f"Post URL: {post_url}")
    except Exception as e:
        print(f"\n[!] Test failed: {e}")
        print("\nTo set up authentication, run:")
        print("python linkedin_oauth.py")
