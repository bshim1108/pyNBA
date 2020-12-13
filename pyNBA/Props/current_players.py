import time
import requests
import gspread
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from pyNBA.Data.helpers import Helpers
from pyNBA.Data.constants import CURRENT_SEASON
from nba_api.stats.endpoints import CommonTeamRoster
from nba_api.stats.static.teams import find_team_by_abbreviation

class CurrentPlayers(object):
    def __init__(self):
        pass

    def get_lineup_data(self):
        helpers = Helpers()

        team_to_opp_team = {}
        team_to_status = {}

        current_player_data = pd.DataFrame(columns=[
            'TEAM', 'NAME', 'START', 'PLAYERSTATUS'
        ])

        URL = 'https://www.rotowire.com/basketball/nba-lineups.php'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        games = soup.find_all('div', class_='lineup is-nba')
        for game in games:
            away_team = game.find('a', class_='lineup__team is-visit').find('div', class_='lineup__abbr').text
            away_team = helpers.prepare_team(away_team)
            away_lineup = game.find('ul', class_='lineup__list is-visit')
            away_player_data, away_lineup_status = helpers.get_player_data(away_lineup)
            away_player_data['TEAM'] = away_team
            away_player_data['NAME'] = away_player_data['NAME'].apply(lambda x: helpers.prepare_name(x, away_team))

            home_team = game.find('a', class_='lineup__team is-home').find('div', class_='lineup__abbr').text
            home_team = helpers.prepare_team(home_team)
            home_lineup = game.find('ul', class_='lineup__list is-home')
            home_player_data, home_lineup_status = helpers.get_player_data(home_lineup)
            home_player_data['TEAM'] = home_team
            home_player_data['NAME'] = home_player_data['NAME'].apply(lambda x: helpers.prepare_name(x, home_team))
            
            team_to_opp_team[away_team] = home_team
            team_to_opp_team[home_team] = away_team
            team_to_status[away_team] = away_lineup_status
            team_to_status[home_team] = home_lineup_status
            
            current_player_data = current_player_data.append(away_player_data)
            current_player_data = current_player_data.append(home_player_data)

        roster_data = pd.DataFrame()
        for team_abbreviation in current_player_data['TEAM'].unique():
            team = find_team_by_abbreviation(team_abbreviation)
            team_id = team['id']

            roster = CommonTeamRoster(season=CURRENT_SEASON, team_id=team_id).get_data_frames()[0]
            time.sleep(0.500)
            
            roster['TEAM'] = team['abbreviation']

            roster_data = roster_data.append(roster)

        roster_data = roster_data.rename(columns={'TeamID': 'TEAMID', 'PLAYER_ID': 'PLAYERID', 'PLAYER': 'NAME'})

        roster_data['POSITION'] = roster_data['POSITION'].str.replace('G', 'Guard')
        roster_data['POSITION'] = roster_data['POSITION'].str.replace('F', 'Forward')
        roster_data['POSITION'] = roster_data['POSITION'].str.replace('C', 'Center')

        current_data = roster_data.merge(current_player_data, on=['NAME', 'TEAM'], how='left')

        current_data['LINEUPSTATUS'] = current_data['TEAM'].apply(lambda x: team_to_status[x])
        current_data['OPP_TEAM'] = current_data['TEAM'].apply(lambda x: team_to_opp_team[x])

        current_data['START'] = current_data['START'].fillna(0)
        current_data['PLAYERSTATUS'] = current_data['PLAYERSTATUS'].fillna('Healthy')
        current_data['SEASON'] = CURRENT_SEASON

        current_data = current_data[[
            'SEASON', 'LINEUPSTATUS', 'PLAYERID', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION',
            'START', 'PLAYERSTATUS'
            ]]

        return current_data

    def write_lineup_data(self):
        current_lineups = self.get_lineup_data()
        current_lineups = current_lineups.sort_values(by=['TEAM', 'START'], ascending=[True, False])

        print('writing currnet lineup data to excel...')
        gc = gspread.service_account()
        sh = gc.open('Current Lineups')
        sh.values_clear("Data!A1:Z9999")
        worksheet = sh.worksheet("Data")
        worksheet.update([current_lineups.columns.values.tolist()] + current_lineups.values.tolist())
        sh.share('brandonshimiaie@gmail.com', perm_type='user', role='writer')

if __name__ == "__main__": 
    CurrentPlayers().write_lineup_data()