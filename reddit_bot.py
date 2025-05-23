import praw
import logging
import re
import time
import json
import os
from praw.exceptions import APIException

def initialize_reddit(config: dict) -> praw.Reddit | None:
    """
    Initializes a PRAW Reddit instance from a config dictionary.
    """
    try:
        return praw.Reddit(
            username=config['username'],
            password=config['password'],
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            user_agent=config['user_agent']
        )
    except Exception as e:
        logging.error(f"Error initializing Reddit instance: {e}")
        return None

def get_replied_comment_ids(filename: str = "replied_to.json") -> set:
    """
    Loads replied comment IDs from file.
    """
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return set(json.load(f))
        except Exception as e:
            logging.warning(f"Error loading replied comment IDs: {e}")
    return set()

def save_replied_comment_ids(comment_ids: set, filename: str = "replied_to.json"):
    """
    Saves replied comment IDs to file.
    """
    try:
        with open(filename, "w") as f:
            json.dump(list(comment_ids), f)
    except Exception as e:
        logging.warning(f"Error saving replied comment IDs: {e}")

def reply_to_comments(subreddit, warriors_players, get_player_stats, replied_comment_ids: set, stats_cache: dict):
    """
    Scans subreddit top posts and replies to comments mentioning Warriors players.
    """
    top_submissions = subreddit.top(limit=25, time_filter="week")
    for submission in top_submissions:
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()
        for comment in comments:
            if comment.id in replied_comment_ids:
                continue
            for player in warriors_players:
                # Case-insensitive, word-boundary search
                pattern = re.compile(rf"\b{re.escape(player)}\b", re.IGNORECASE)
                if pattern.search(comment.body):
                    if player not in stats_cache:
                        stats_cache[player] = get_player_stats(player)
                    stats = stats_cache[player]
                    if stats != "Stats not available.":
                        reply_text = f"{player} Stats: PPG: {stats['PPG']}, RPG: {stats['RPG']}, APG: {stats['APG']}"
                    else:
                        reply_text = f"Stats for {player} are not available."
                    try:
                        comment.reply(reply_text)
                        replied_comment_ids.add(comment.id)
                        logging.info(f"Replied to comment {comment.id} with {player} stats.")
                        time.sleep(10)
                    except APIException as api_exc:
                        logging.error(f"API error replying to comment {comment.id}: {api_exc}")
                        if api_exc.error_type == "RATELIMIT":
                            # Try to extract wait time in minutes
                            match = re.search(r'(\d+) minutes?', str(api_exc))
                            wait = int(match.group(1)) * 60 if match else 600
                            logging.warning(f"Rate limited. Waiting {wait} seconds.")
                            time.sleep(wait)
                    except Exception as e:
                        logging.error(f"Error replying to comment {comment.id}: {e}")
