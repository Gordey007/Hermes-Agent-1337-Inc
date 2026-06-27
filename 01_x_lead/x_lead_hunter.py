"""X/Twitter lead hunter: search for recent tweets (recent search) + bot filter + 
write to the database.

Refactoring: the database connection is handled by a single db.py file (Step 0),
save_tweets_to_db correctly tracks inserted/skipped records and commits,
queries are read from queries.yaml instead of being hardcoded.

cron
x_lead_hunter
Execute the command bash: `uv run /sandbox/tools/x_lead/x_lead_hunter.py`
*/1 * * * * - test
0 0 * * * - prod
"""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import requests
import yaml

from db import get_conn

from dotenv import load_dotenv
load_dotenv()


BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
QUERIES_PATH = Path(__file__).parent / "queries.yaml"

TWEET_FIELDS = ",".join([
    "article", "attachments", "author_id", "card_uri", "community_id", "context_annotations",
    "conversation_id", "created_at", "display_text_range", "edit_controls", "edit_history_tweet_ids",
    "entities", "geo", "id", "in_reply_to_user_id", "lang", "matched_media_notes", "media_metadata",
    "note_tweet", "possibly_sensitive", "public_metrics", "referenced_tweets", "reply_settings",
    "source", "suggested_source_links", "text", "withheld",
])

USER_FIELDS = ",".join([
    "affiliation", "connection_status", "created_at", "description", "entities",
    "id", "is_identity_verified", "location", "most_recent_tweet_id", "name",
    "pinned_tweet_id", "profile_banner_url", "profile_image_url", "protected",
    "public_metrics", "receives_your_dm", "subscription_type", "url", "username",
    "verified", "verified_followers_count", "verified_type", "withheld",
])

EXPANSIONS = "author_id"

BOT_FILTER_CONFIG = {
    "min_followers":        10,
    "min_tweet_count":       5,
    "min_account_age_days": 30,
    "digits_in_username":    4,
    "require_description":  True,
    "min_tweet_text_length": 100,
}


def _extract_author_username(tweet: dict, author: dict) -> str:
    username = author.get("username") or tweet.get("author_username")
    if username:
        return username
    match = re.search(r"x\.com/([^/]+)/status/", tweet.get("tweet_url", ""))
    if match:
        return match.group(1)
    return "unknown"


def _build_lead_row(tweet: dict) -> dict:
    author = tweet.get("_author") or {}
    metrics = tweet.get("public_metrics") or {}

    tweet_id = str(tweet["id"])
    author_id = str(tweet.get("author_id") or author.get("id") or "")
    author_username = _extract_author_username(tweet, author)

    tweet_url = tweet.get("tweet_url") or f"https://x.com/{author_username}/status/{tweet_id}"

    return {
        "tweet_id": tweet_id,
        "tweet_url": tweet_url,
        "tweet_text": tweet.get("text", ""),
        "author_id": author_id,
        "author_username": author_username,
        "lang": tweet.get("lang"),
        "created_at": tweet.get("created_at"),
        "impression_count": metrics.get("impression_count", 0),
        "like_count": metrics.get("like_count", 0),
        "reply_count": metrics.get("reply_count", 0),
        "retweet_count": metrics.get("retweet_count", 0),
    }


def save_tweets_to_db(tweets: list[dict]) -> dict:
    """Writes tweets to the database, tracks inserted/skipped records and commits."""
    if not tweets:
        print("[save_tweets_to_db] inserted=0 skipped=0")
        return {"inserted": 0, "skipped": 0}

    inserted = skipped = 0
    insert_sql = """
    INSERT OR IGNORE INTO leads (
        tweet_id, tweet_url, tweet_text, author_id, author_username,
        lang, created_at, impression_count, like_count, reply_count, retweet_count
    ) VALUES (
        :tweet_id, :tweet_url, :tweet_text, :author_id, :author_username,
        :lang, :created_at, :impression_count, :like_count, :reply_count, :retweet_count
    )
    """

    with get_conn() as conn:
        for tweet in tweets:
            row = _build_lead_row(tweet)
            cursor = conn.execute(insert_sql, row)
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        conn.commit()

    print(f"[save_tweets_to_db] inserted={inserted} skipped={skipped}")
    return {"inserted": inserted, "skipped": skipped}


def _clean_tweet_text_for_bot_filter(text: str) -> str:
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_bot(user: dict, tweet: dict | None = None, config: dict = BOT_FILTER_CONFIG
           ) -> tuple[bool, list[str]]:
    reasons = []
    metrics = user.get("public_metrics", {})
    followers = metrics.get("followers_count", 0)
    tweet_count = metrics.get("tweet_count", 0)
    username = user.get("username", "")
    description = (user.get("description") or "").strip()
    created_at = user.get("created_at", "")

    if followers < config["min_followers"]:
        reasons.append(f"low_followers:{followers}")
    if tweet_count < config["min_tweet_count"]:
        reasons.append(f"low_tweet_count:{tweet_count}")
    if re.search(r"\d{%d,}" % config["digits_in_username"], username):
        reasons.append(f"numeric_username:{username}")
    if config["require_description"] and len(description) < 10:
        reasons.append("no_description")
    if tweet is not None:
        clean_text = _clean_tweet_text_for_bot_filter(tweet.get("text", ""))
        if len(clean_text) < config["min_tweet_text_length"]:
            reasons.append(f"short_text:{len(clean_text)}")
    if created_at:
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                dt = datetime.strptime(created_at, fmt)
                age_days = (datetime.utcnow() - dt).days
                if age_days < config["min_account_age_days"]:
                    reasons.append(f"new_account:{age_days}d")
                break
            except ValueError:
                continue

    return len(reasons) >= 2, reasons


def bot_score(reasons: list[str]) -> int:
    weights = {
        "low_followers": 25, "low_tweet_count": 20,
        "numeric_username": 30, "no_description": 15, "new_account": 25,
        "short_text": 20,
    }
    return min(sum(weights.get(r.split(":")[0], 10) for r in reasons), 100)


def search_recent_tweets(query: str, max_results: int = 10, filter_bots: bool = True) -> list[dict]:
    url = "https://api.x.com/2/tweets/search/recent"

    now = datetime.utcnow()
    end_time = now - timedelta(seconds=10)
    start_time = end_time - timedelta(hours=24)

    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    params = {
        "query": query,
        "max_results": max_results,
        "sort_order": "relevancy",
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tweet.fields": TWEET_FIELDS,
        "user.fields": USER_FIELDS,
        "expansions": EXPANSIONS,
    }

    response = requests.get(url, headers=headers, params=params)
    print(f"[search_recent_tweets] Status: {response.status_code}")
    if response.status_code != 200:
        print(f"  Error: {response.text}")
        return []

    data = response.json()
    if "data" not in data:
        return []

    users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
    clean_tweets: list[dict] = []
    skipped = 0
    for tweet in data["data"]:
        author = users.get(tweet.get("author_id"), {})
        tweet["tweet_url"] = f"https://x.com/{author.get('username')}/status/{tweet['id']}"
        flagged, reasons = is_bot(author, tweet=tweet)
        score = bot_score(reasons)
        if filter_bots and flagged:
            skipped += 1
            print(f"  [BOT] @{author.get('username')} score={score} {reasons}")
            continue
        tweet["_author"] = author
        clean_tweets.append(tweet)

    print(f"[search_recent_tweets] kept={len(clean_tweets)} bots_skipped={skipped}")
    return clean_tweets


def load_queries() -> list[dict]:
    """Loads intents from the queries.yaml (instead of hardcoding)."""
    with open(QUERIES_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("intent_queries", [])


def run_once(max_results: int = 10) -> dict:
    total = {"inserted": 0, "skipped": 0}
    for item in load_queries():
        print(f"\n[run_once] intent={item['intent']}")
        results = search_recent_tweets(item["query"], max_results=max_results)
        if not results:
            continue
        stats = save_tweets_to_db(results)
        total["inserted"] += stats["inserted"]
        total["skipped"] += stats["skipped"]
    print(f"\n[run_once] TOTAL inserted={total['inserted']} skipped={total['skipped']}")
    return total


if __name__ == "__main__":
    run_once()
