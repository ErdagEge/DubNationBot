import logging
from nba_api.stats.endpoints import commonplayerinfo, commonteamroster
from nba_api.stats.static import players, teams

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
