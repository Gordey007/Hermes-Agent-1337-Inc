"""x_actions.py — post quote-tweets and DMs via the X (Twitter) API v2.

Used by the sales profile (sl-send-x skill) for outreach after a product is built.

Auth:
  X_BEARER_TOKEN       — app bearer token (read/search; set up for lead hunting).
  X_USER_ACCESS_TOKEN  — OAuth 2.0 user access token, required for WRITE operations
                         (post_reply / send_dm / quote_tweet). Needs the
                         "Read and write and Direct message" scope on the app.

Both are read from the environment and are never logged.
"""

import os
import requests
from dotenv import load_dotenv
load_dotenv()

BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
USER_ACCESS_TOKEN = os.getenv("X_USER_ACCESS_TOKEN")  # OAuth 2.0 PKCE token


def _user_auth_headers() -> dict:
    """Headers for write operations (OAuth 2.0 user access token)."""
    return {
        "Authorization": f"Bearer {USER_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def send_dm(participant_id: str, text: str) -> dict:
    """Send a direct message to a user.

    Args:
        participant_id: recipient user ID (author["id"] from search results).
        text: message body.

    Returns:
        {"dm_conversation_id": ..., "dm_event_id": ...} on success, else {"error": ...}.

    Requires X_USER_ACCESS_TOKEN with Read+Write+DM scope. The recipient must allow
    message requests from everyone.
    """
    url = f"https://api.twitter.com/2/dm_conversations/with/{participant_id}/messages"
    response = requests.post(url, headers=_user_auth_headers(), json={"text": text})
    if response.status_code not in (200, 201):
        return {"error": response.text, "status": response.status_code}
    return response.json().get("data", {})


def quote_tweet(tweet_id: str, tweet_author_username: str, text: str) -> dict:
    """Quote-tweet (repost with a comment).

    Args:
        tweet_id: id of the original tweet.
        tweet_author_username: author's username (author["username"]).
        text: your comment (keep it short — the appended URL takes ~23 chars).
    """
    original_url = f"https://x.com/{tweet_author_username}/status/{tweet_id}"
    full_text = f"{text}\n\n{original_url}"
    response = requests.post(
        "https://api.twitter.com/2/tweets",
        headers=_user_auth_headers(), json={"text": full_text})
    if response.status_code not in (200, 201):
        return {"error": response.text, "status": response.status_code}
    return response.json().get("data", {})
