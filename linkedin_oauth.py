"""
LinkedIn OAuth Integration - Handles OAuth 2.0 authentication for LinkedIn API
"""

import os
import http.server
import socketserver
import webbrowser
from urllib.parse import parse_qs, urlparse, quote
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def get_linkedin_config() -> dict:
    """Get LinkedIn OAuth configuration from environment"""
    return {
        'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
        'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET'),
        'redirect_uri': os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8000/callback')
    }


def is_linkedin_configured() -> bool:
    """Check if LinkedIn OAuth credentials are configured"""
    config = get_linkedin_config()
    return bool(config['client_id'] and config['client_secret'])


def get_auth_url() -> str:
    """
    Generate LinkedIn OAuth authorization URL.

    Returns:
        Authorization URL to redirect user to
    """
    config = get_linkedin_config()

    if not config['client_id']:
        raise ValueError("LINKEDIN_CLIENT_ID not set in .env file")

    # LinkedIn OAuth scopes needed for posting (2025+)
    # Using OpenID Connect scopes instead of deprecated r_liteprofile
    scopes = [
        'openid',            # Required for OpenID Connect
        'profile',           # Replaces r_liteprofile
        'email',             # Email access (optional)
        'w_member_social',   # Required for posting
    ]

    # URL encode the parameters
    scope_encoded = quote(' '.join(scopes), safe='')
    redirect_uri_encoded = quote(config['redirect_uri'], safe='')

    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={config['client_id']}&"
        f"redirect_uri={redirect_uri_encoded}&"
        f"scope={scope_encoded}"
    )

    return auth_url


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP server to handle OAuth callback"""

    def do_GET(self):
        """Handle GET request for OAuth callback"""
        if self.path.startswith('/callback'):
            # Parse the authorization code from URL
            query = parse_qs(urlparse(self.path).query)

            if 'code' in query:
                # Store the authorization code in the server instance
                # Use the TCPServer's custom attribute
                auth_code = query['code'][0]
                self.server.auth_code = auth_code

                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html><body>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    </body></html>
                """)
            else:
                if 'error' in query:
                    error = query['error'][0]
                    self.server.auth_error = error

                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html><body>
                    <h1>Authentication Failed</h1>
                    <p>Please try again.</p>
                    </body></html>
                """)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def authenticate() -> dict:
    """
    Perform OAuth 2.0 authentication flow.

    Returns:
        Dictionary with 'access_token' and 'expires_in'
    """
    import requests

    config = get_linkedin_config()

    # Step 1: Open browser for user authorization
    auth_url = get_auth_url()
    print("\n" + "=" * 60)
    print("LINKEDIN OAUTH AUTHENTICATION")
    print("=" * 60)
    print(f"\n1. Opening browser to LinkedIn authorization page...")
    print(f"   If browser doesn't open, visit this URL:")
    print(f"   {auth_url}\n")

    # Start local server to handle callback
    port = 8000

    # Create a custom TCPServer class with auth_code attribute
    class OAuthServer(socketserver.TCPServer):
        def __init__(self, *args, **kwargs):
            self.auth_code = None
            self.auth_error = None
            super().__init__(*args, **kwargs)

    try:
        httpd = OAuthServer(("", port), OAuthCallbackHandler)

        # Open browser
        webbrowser.open(auth_url)

        print(f"2. Waiting for authorization callback on port {port}...")
        print(f"   (Press Ctrl+C to cancel)\n")

        # Wait for callback
        httpd.handle_request()  # Handle one request

        if httpd.auth_error:
            raise Exception(f"Authorization failed: {httpd.auth_error}")

        auth_code = httpd.auth_code

        if not auth_code:
            raise Exception("No authorization code received")

        print(f"   [OK] Authorization code received")

    finally:
        httpd.server_close()

    # Step 2: Exchange authorization code for access token
    print(f"\n3. Exchanging authorization code for access token...")

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': config['redirect_uri'],
        'client_id': config['client_id'],
        'client_secret': config['client_secret']
    }

    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        raise Exception(f"Token exchange failed: {response.text}")

    token_data = response.json()

    print(f"   [OK] Access token received")
    print(f"\n" + "=" * 60)
    print("AUTHENTICATION SUCCESSFUL!")
    print("=" * 60)

    return token_data


def save_access_token(token_data: dict) -> str:
    """
    Save access token to file for later use.

    Args:
        token_data: Dictionary with access token info

    Returns:
        Path to saved token file
    """
    import json
    from datetime import datetime, timedelta

    # Calculate expiration time
    expires_in = token_data.get('expires_in', 3600)
    expires_at = datetime.now() + timedelta(seconds=expires_in)

    token_info = {
        'access_token': token_data['access_token'],
        'expires_at': expires_at.isoformat(),
        'obtained_at': datetime.now().isoformat()
    }

    # Save to file
    token_file = os.path.join(os.path.dirname(__file__), 'linkedin_token.json')

    with open(token_file, 'w') as f:
        json.dump(token_info, f, indent=2)

    print(f"\nAccess token saved to: {token_file}")
    print(f"Expires at: {expires_at}")

    return token_file


def load_access_token() -> Optional[str]:
    """
    Load access token from environment variable or file.

    Priority:
    1. Environment variable LINKEDIN_ACCESS_TOKEN (for GitHub Actions)
    2. Local file linkedin_token.json (for local development)

    Returns:
        Access token if exists and not expired, None otherwise
    """
    import json
    from datetime import datetime

    # First, check environment variable (GitHub Secrets)
    env_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if env_token:
        print("[LinkedIn] Using access token from environment variable")
        return env_token

    # Otherwise, load from file
    token_file = os.path.join(os.path.dirname(__file__), 'linkedin_token.json')

    if not os.path.exists(token_file):
        return None

    try:
        with open(token_file, 'r') as f:
            token_info = json.load(f)

        # Check if token is expired
        expires_at = datetime.fromisoformat(token_info['expires_at'])
        if datetime.now() >= expires_at:
            print("Access token has expired. Please re-authenticate.")
            return None

        return token_info['access_token']

    except Exception as e:
        print(f"Error loading token: {e}")
        return None


def setup_linkedin_auth():
    """
    Main function to set up LinkedIn authentication.
    This handles the entire OAuth flow and saves the token.
    """
    if not is_linkedin_configured():
        print("\n[!] LinkedIn OAuth not configured")
        print("Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env file")
        return False

    # Try to load existing token
    existing_token = load_access_token()
    if existing_token:
        print("\n[OK] Using existing access token")
        return True

    # Perform OAuth flow
    try:
        token_data = authenticate()
        save_access_token(token_data)
        print("\n[OK] LinkedIn authentication setup complete!")
        return True
    except Exception as e:
        print(f"\n[!] Authentication failed: {e}")
        return False


if __name__ == "__main__":
    setup_linkedin_auth()
