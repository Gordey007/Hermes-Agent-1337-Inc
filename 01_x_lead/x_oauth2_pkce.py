"""
x_oauth2_pkce.py — obtain a User Access Token via OAuth 2.0 PKCE
without third-party libraries, using only requests + the standard library

Run it once -> get an access_token -> add it to .env
"""

import os
import base64
import hashlib
import secrets
import urllib.parse
import webbrowser
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

# Fill in these values from developer.x.com -> your App -> Keys and Tokens
CLIENT_ID     = os.getenv("X_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("X_CLIENT_SECRET", "")  # only for a confidential app
REDIRECT_URI  = "http://localhost:3000"  # must match your App settings

# Permissions required for DMs + posting
SCOPES = "tweet.read tweet.write users.read dm.read dm.write offline.access"


# ─────────────────────────────────────────────
#  Generate PKCE code_verifier and code_challenge
# ─────────────────────────────────────────────
def generate_pkce() -> tuple[str, str]:
    """Returns (code_verifier, code_challenge)"""
    code_verifier = secrets.token_urlsafe(32)  # 43-128 characters
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


# ─────────────────────────────────────────────
#  Step 1: Open the browser for authorization
# ─────────────────────────────────────────────
def get_authorization_url(code_challenge: str, state: str) -> str:
    params = {
        "response_type":        "code",
        "client_id":            CLIENT_ID,
        "redirect_uri":         REDIRECT_URI,
        "scope":                SCOPES,
        "state":                state,
        "code_challenge":       code_challenge,
        "code_challenge_method": "S256",
    }
    return "https://x.com/i/oauth2/authorize?" + urllib.parse.urlencode(params)


# ─────────────────────────────────────────────
#  Step 2: Exchange code -> access_token
# ─────────────────────────────────────────────
def exchange_code_for_token(code: str, code_verifier: str) -> dict:
    """
    POST /oauth2/token
    Works for a public client (without CLIENT_SECRET)
    and a confidential client (with Basic Auth from CLIENT_ID:CLIENT_SECRET)
    """
    url = "https://api.x.com/2/oauth2/token"

    data = {
        "grant_type":    "authorization_code",
        "code":          code,
        "redirect_uri":  REDIRECT_URI,
        "code_verifier": code_verifier,
        "client_id":     CLIENT_ID,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Confidential client: add Basic Auth
    if CLIENT_SECRET and CLIENT_SECRET != "INSERT_CLIENT_SECRET":
        creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        headers["Authorization"] = f"Basic {creds}"
        data.pop("client_id", None)  # with Basic Auth, client_id is not needed in the body

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print(f"[exchange_code] ERROR {response.status_code}: {response.text}")
        return {}

    return response.json()


# ─────────────────────────────────────────────
#  Step 3 (optional): Refresh access_token via refresh_token
# ─────────────────────────────────────────────
def refresh_access_token(refresh_token: str) -> dict:
    """Refresh an expired access_token without reauthorizing the user"""
    url = "https://api.x.com/2/oauth2/token"

    data = {
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token,
        "client_id":     CLIENT_ID,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    if CLIENT_SECRET and CLIENT_SECRET != "INSERT_CLIENT_SECRET":
        creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        headers["Authorization"] = f"Basic {creds}"

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print(f"[refresh_token] ERROR {response.status_code}: {response.text}")
        return {}

    return response.json()


# ─────────────────────────────────────────────
#  Full flow - run once
# ─────────────────────────────────────────────
def run_oauth_flow():
    state         = secrets.token_urlsafe(16)
    code_verifier, code_challenge = generate_pkce()

    auth_url = get_authorization_url(code_challenge, state)

    print("=" * 60)
    print("Step 1: Opening the browser for authorization...")
    print(f"\nURL:\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("=" * 60)
    print("Step 2: After authorization, X will redirect you to:")
    print(f"  {REDIRECT_URI}?code=XXXX&state={state}")
    print("\nCopy the FULL redirect URL and paste it here:")
    redirect_url = input(">>> ").strip()

    # Extract code from the redirect URL
    parsed = urllib.parse.urlparse(redirect_url)
    params = urllib.parse.parse_qs(parsed.query)

    returned_state = params.get("state", [None])[0]
    code = params.get("code", [None])[0]

    if returned_state != state:
        print("❌ state does not match! Possible CSRF attack.")
        return

    if not code:
        print("❌ code not found in the URL")
        return

    print(f"\nStep 3: Exchanging code for access_token...")
    token_data = exchange_code_for_token(code, code_verifier)

    if not token_data:
        return

    access_token  = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in    = token_data.get("expires_in")

    print("\n" + "=" * 60)
    print("✅ Success!")
    print(f"  access_token  : {access_token}")
    print(f"  refresh_token : {refresh_token if refresh_token else 'none (offline.access scope required)'}...")
    print(f"  expires_in    : {expires_in} sec ({int(expires_in)//3600}h)")

    # Save to .env automatically
    env_path = ".env"
    set_key(env_path, "X_USER_ACCESS_TOKEN", access_token)
    if refresh_token:
        set_key(env_path, "X_REFRESH_TOKEN", refresh_token)

    print(f"\n✅ Saved to {env_path}")
    print("  X_USER_ACCESS_TOKEN - use it in x_actions.py")
    print("  X_REFRESH_TOKEN     - for refreshing the token")

    return token_data


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "refresh":
        # python x_oauth2_pkce.py refresh
        rt = os.getenv("X_REFRESH_TOKEN")
        if not rt:
            print("❌ X_REFRESH_TOKEN not found in .env")
        else:
            result = refresh_access_token(rt)
            if result:
                set_key(".env", "X_USER_ACCESS_TOKEN", result["access_token"])
                if result.get("refresh_token"):
                    set_key(".env", "X_REFRESH_TOKEN", result["refresh_token"])
                print("✅ Token refreshed and saved to .env")
    else:
        run_oauth_flow()
