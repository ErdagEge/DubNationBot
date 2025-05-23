import logging
import os
from config import load_config
from nba_utils import get_team_roster, get_player_stats
from reddit_bot import initialize_reddit, get_replied_comment_ids, save_replied_comment_ids, reply_to_comments
from nba_api.stats.static import teams

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

def main():
    config_path = os.getenv('DUBNATIONBOT_CONFIG', 'config.json')
    config = load_config(config_path)
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
    replied_comment_ids = get_replied_comment_ids()

    reply_to_comments(subreddit, warriors_players, get_player_stats, replied_comment_ids, stats_cache)

    save_replied_comment_ids(replied_comment_ids)

if __name__ == "__main__":
    main()
