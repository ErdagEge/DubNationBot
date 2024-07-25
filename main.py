import praw
import json
import pandas as pd
from nba_api.stats.endpoints import commonplayerinfo, commonteamroster
from nba_api.stats.static import players, teams

# Load the configuration from the JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialize the Reddit instance with the configuration data
reddit_instance = praw.Reddit(
    username=config['username'],
    password=config['password'],
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    user_agent=config['user_agent']
)

# getting all the NBA teams
nba_teams = teams.get_teams()


# Getting the roster of a specific team
def get_team_roster(team_id):
    roster = commonteamroster.CommonTeamRoster(team_id=team_id)
    return roster.get_data_frames()[0]


# Getting team id for the Golden State Warriors
warriors_id = [team['id'] for team in nba_teams if team['full_name'] == 'Golden State Warriors'][0]

# Fetch the roster for Golden State Warriors
warriors_roster = get_team_roster(warriors_id)

# Get the players name
warriors_players = warriors_roster['PLAYER'].tolist()


# Function to get player stats using nba_api
def get_player_stats(player_name):
    nba_players = players.get_players()
    selected_player = next((selected_player for selected_player in nba_players if selected_player['full_name'] == player_name), None)
    if selected_player:
        player_id = selected_player['id']
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        selected_stats = player_info.player_headline_stats.get_dict()
        if selected_stats['data']:
            selected_stats = selected_stats['data'][0]  # Get the first entry
            return {
                "PPG": selected_stats[3],
                "RPG": selected_stats[4],
                "APG": selected_stats[5]
            }
    return "Stats not available."


# Get the top 25 posts in the last week
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
                comment.reply(reply_text)
                print(f"Just replied to comment {comment.id} with {player} stats.")

print(warriors_players)

# print(reddit_instance.user.me())

# HOW TO GET TOP 25 POSTS IN THE LAST WEEK
# subreddit = reddit_instance.subreddit("warriors")
# top_25_submissions = subreddit.top(limit=25, time_filter="week")
# for submission in top_25_submissions:
#    print(submission.title)

# HOW TO POST A POST
# subreddit = reddit_instance.subreddit("testingground4bots")
# subreddit.submit(title="This is a test post", selftext="Hello Test.")

# submission = reddit_instance.submission("1e9ghv0")
# comments = submission.comments

# HOW TO COMMENT
# for comment in comments:
#    if "test my stuff" in comment.body:
#        comment.reply("reply.")
