import praw
import json
import os
import logging
import pandas as pd
import re
import time
from nba_api.stats.endpoints import commonplayerinfo, commonteamroster
from nba_api.stats.static import players, teams
from praw.exceptions import APIException

# ... [other functions unchanged for brevity] ...

def main():
    config = load_config('config.json')
    if not config:
        return

    reddit_instance = initialize_reddit(config)
    if not reddit_instance:
        return

    nba_teams = teams.get_teams()
    warriors_id = next((team['id'] for team in nba_teams if team['full_name'] == 'Golden State Warriors'), None)
    if not warriors_id:
        logging.error("Golden State Warriors team ID not found.")
        return

    warriors_roster = get_team_roster(warriors_id)
    if warriors_roster is None:
        return

    warriors_players = warriors_roster['PLAYER'].tolist()
    stats_cache = {}

    subreddit = reddit_instance.subreddit("warriors")
    top_25_submissions = subreddit.top(limit=25, time_filter="week")

    replied_comment_ids = set()
    if os.path.exists("replied_to.json"):
        with open("replied_to.json", "r") as f:
            replied_comment_ids = set(json.load(f))

    for submission in top_25_submissions:
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()

        for comment in comments:
            if comment.id in replied_comment_ids:
                continue
            for player in warriors_players:
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
                        time.sleep(10)  # Wait 10 seconds between replies
                    except APIException as api_exc:
                        logging.error(f"API error replying to comment {comment.id}: {api_exc}")
                        if api_exc.error_type == "RATELIMIT":
                            # Extract wait time from message, or default to 10 min
                            time.sleep(600)
                    except Exception as e:
                        logging.error(f"Error replying to comment {comment.id}: {e}")

    # Save replied comment ids
    with open("replied_to.json", "w") as f:
        json.dump(list(replied_comment_ids), f)
