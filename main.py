import praw
import json
import os
import logging
import pandas as pd
from nba_api.stats.endpoints import commonplayerinfo, commonteamroster
from nba_api.stats.static import players, teams

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(file_path):
    try:
        with open(file_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file {file_path} not found.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from the configuration file {file_path}.")
        return None


def initialize_reddit(config):
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


def get_team_roster(team_id):
    try:
        roster = commonteamroster.CommonTeamRoster(team_id=team_id)
        return roster.get_data_frames()[0]
    except Exception as e:
        logging.error(f"Error fetching team roster: {e}")
        return None


def get_player_stats(player_name):
    try:
        nba_players = players.get_players()
        selected_player = next((p for p in nba_players if p['full_name'] == player_name), None)
        if selected_player:
            player_id = selected_player['id']
            player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
            selected_stats = player_info.player_headline_stats.get_dict()
            if selected_stats['data']:
                selected_stats = selected_stats['data'][0]
                return {
                    "PPG": selected_stats[3],
                    "RPG": selected_stats[4],
                    "APG": selected_stats[5]
                }
        return "Stats not available."
    except Exception as e:
        logging.error(f"Error fetching player stats: {e}")
        return "Stats not available."


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

    subreddit = reddit_instance.subreddit("warriors")
    top_25_submissions = subreddit.top(limit=25, time_filter="week")

    for submission in top_25_submissions:
        submission.comments.replace_more(limit=0)
        comments = submission.comments.list()

        for comment in comments:
            for player in warriors_players:
                if player in comment.body:
                    stats = get_player_stats(player)
                    if stats != "Stats not available.":
                        reply_text = f"{player} Stats: PPG: {stats['PPG']}, RPG: {stats['RPG']}, APG: {stats['APG']}"
                    else:
                        reply_text = f"Stats for {player} are not available."
                    try:
                        comment.reply(reply_text)
                        logging.info(f"Replied to comment {comment.id} with {player} stats.")
                    except Exception as e:
                        logging.error(f"Error replying to comment {comment.id}: {e}")


if __name__ == "__main__":
    main()
