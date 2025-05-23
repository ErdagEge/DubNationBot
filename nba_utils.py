import logging
from nba_api.stats.endpoints import commonplayerinfo, commonteamroster
from nba_api.stats.static import players

def get_team_roster(team_id: int):
    """
    Fetches the current NBA team roster.
    Returns a DataFrame or None on failure.
    """
    try:
        roster = commonteamroster.CommonTeamRoster(team_id=team_id)
        return roster.get_data_frames()[0]
    except Exception as e:
        logging.error(f"Error fetching team roster: {e}")
        return None

def get_player_stats(player_name: str):
    """
    Fetches headline stats for a player by full name.
    Returns a dict of stats or 'Stats not available.' string.
    """
    try:
        nba_players = players.get_players()
        selected_player = next((p for p in nba_players if p['full_name'] == player_name), None)
        if selected_player:
            player_id = selected_player['id']
            player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
            stats_dict = player_info.player_headline_stats.get_dict()
            if stats_dict['data']:
                stats = stats_dict['data'][0]
                return {
                    "PPG": stats[3],
                    "RPG": stats[4],
                    "APG": stats[5]
                }
        return "Stats not available."
    except Exception as e:
        logging.error(f"Error fetching player stats: {e}")
        return "Stats not available."
