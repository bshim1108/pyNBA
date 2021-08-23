import time
import pandas as pd
from os import path
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from nba_api.stats.endpoints import PlayByPlayV2, SynergyPlayTypes
from pyNBA.Data.constants import (CURRENT_SEASON, LINEUP_TEAM_TO_NBA_TEAM, LINEUP_NAME_TO_NBA_NAME, NUMBERFIRE_NAME_TO_NBA_NAME)

class Helpers(object):
    def __init__(self):
        pass

    def get_player_minutes(self):
        player_to_mintes = {}

        URL = 'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        players = soup.find_all('tr', {'data-sport-path': 'nba'})
        for player in players:
            name = player.find('a', {'class': 'full'}).text.strip()
            if name in NUMBERFIRE_NAME_TO_NBA_NAME:
                name = NUMBERFIRE_NAME_TO_NBA_NAME[name]

            minutes = float(player.find('td', {'class': 'min'}).text.strip())

            player_to_mintes[name] = minutes

        return player_to_mintes

    def increment_timestring(self, timestring):
        temp = timestring.split(':')
        minutes = temp[0]
        seconds = int(temp[1])
        seconds += 1
        return '{}:{}'.format(minutes, str(seconds))

    def get_play_by_play_attempts(self, game_id):
        play_by_play = PlayByPlayV2(game_id=game_id).get_data_frames()[0]
        if play_by_play.empty:
            print('PlayByPlay data empty for game_id: {}'.format(game_id))
            return pd.DataFrame()

        play_by_play['DESCRIPTION'] = ''
        play_by_play.loc[~play_by_play['VISITORDESCRIPTION'].isnull(), 'DESCRIPTION'] = \
            play_by_play.loc[~play_by_play['VISITORDESCRIPTION'].isnull(), 'VISITORDESCRIPTION']
        play_by_play.loc[~play_by_play['HOMEDESCRIPTION'].isnull(), 'DESCRIPTION'] = \
            play_by_play.loc[~play_by_play['HOMEDESCRIPTION'].isnull(), 'HOMEDESCRIPTION']
        play_by_play.loc[~play_by_play['NEUTRALDESCRIPTION'].isnull(), 'DESCRIPTION'] = \
            play_by_play.loc[~play_by_play['NEUTRALDESCRIPTION'].isnull(), 'HOMEDESCRIPTION']

        play_by_play['DESCRIPTION'] = play_by_play['DESCRIPTION'].str.replace('Personal Take Foul','PFOUL')
        play_by_play['DESCRIPTION'] = play_by_play['DESCRIPTION'].str.replace('Offensive Charge Foul','OFOUL')
        play_by_play['DESCRIPTION'] = play_by_play['DESCRIPTION'].str.replace('Flagrant','FLAGRANT')
        play_by_play['DESCRIPTION'] = play_by_play['DESCRIPTION'].str.replace('Foul','FOUL')

        attempt_data = play_by_play.loc[
            play_by_play['EVENTMSGTYPE'].isin([1, 2]),
            ['PERIOD', 'PCTIMESTRING', 'DESCRIPTION', 'PLAYER1_ID']
            ]
        attempt_data = attempt_data.rename(columns={'PLAYER1_ID': 'PLAYER_ID'})

        ft_data = pd.DataFrame(columns=['PERIOD', 'PCTIMESTRING', 'DESCRIPTION', 'PLAYER_ID', 'FTA', 'FTM'])
        raw_ft_data = play_by_play.loc[play_by_play['EVENTMSGTYPE'].isin([3, 6])]
        prev_time = None
        for index, row in raw_ft_data.loc[raw_ft_data['EVENTMSGTYPE'] == 6].iterrows():
            time = row['PCTIMESTRING']
            if time == prev_time:
                raw_ft_data.loc[index:, 'PCTIMESTRING'] = raw_ft_data.loc[index:, 'PCTIMESTRING'].apply(
                    lambda x: self.increment_timestring(x)
                    )
            prev_time = time

        for (period, time), rows in raw_ft_data.groupby(['PERIOD', 'PCTIMESTRING']):
            ft_rows = rows.loc[rows['EVENTMSGTYPE'] == 3]
            if ft_rows.empty:
                continue

            foul_play = rows.loc[rows['EVENTMSGTYPE'] == 6]
            if len(foul_play) > 0:
                description = foul_play['DESCRIPTION'].iloc[0]
            else:
                description = None

            if description is not None:
                words = description.split(' ')
                foul_type = None
                for word in words:
                    if 'FOUL' in word:
                        foul_type = word.replace('.', '')
                        break
                foul_type = foul_type or 'UNKNOWNFOUL'
                description = '{} TRIP'.format(foul_type)
            else:
                description = 'UNKNOWNFOUL TRIP'

            for player_id, player_ft_rows in ft_rows.groupby('PLAYER1_ID'):
                if 'Technical' in player_ft_rows['DESCRIPTION'].iloc[0]:
                    player_description = 'TFOUL TRIP'
                else:
                    player_description = description
                fta = len(player_ft_rows)
                ftm = len(player_ft_rows.loc[
                    (~player_ft_rows['DESCRIPTION'].str.contains("MISS")) &
                    (player_ft_rows['DESCRIPTION'] != '')
                    ])
                temp = pd.Series(
                    [period, time, player_description, player_id, fta, ftm],
                    index=['PERIOD', 'PCTIMESTRING', 'DESCRIPTION', 'PLAYER_ID', 'FTA', 'FTM']
                    )
                ft_data = ft_data.append(temp, ignore_index=True)

        attempt_data = pd.merge(
            attempt_data, ft_data[['PLAYER_ID', 'PERIOD', 'PCTIMESTRING', 'FTA', 'FTM']],
            on=['PLAYER_ID', 'PERIOD', 'PCTIMESTRING'], how='left'
            )

        subset = attempt_data[['PLAYER_ID', 'PERIOD', 'PCTIMESTRING']]
        attemp_indexes = set([tuple(x) for x in subset.to_numpy()])
        ft_trips = ft_data.loc[
            ft_data[['PLAYER_ID', 'PERIOD', 'PCTIMESTRING']].apply(
                lambda x: (x['PLAYER_ID'], x['PERIOD'], x['PCTIMESTRING']) not in attemp_indexes, axis=1
                )
            ]
        attempt_data = attempt_data.append(ft_trips)

        attempt_data[['FTA', 'FTM']] = attempt_data[['FTA', 'FTM']].fillna(0)
        attempt_data['PTS'] = attempt_data['FTM']
        attempt_data.loc[
            ~(attempt_data['DESCRIPTION'].str.contains('FOUL') & attempt_data['DESCRIPTION'].str.contains('TRIP')) &
            ~attempt_data['DESCRIPTION'].str.contains('MISS') &
            ~attempt_data['DESCRIPTION'].str.contains('BLOCK') &
            ~attempt_data['DESCRIPTION'].str.contains('3PT'),
            'PTS'] += 2
        attempt_data.loc[
            ~(attempt_data['DESCRIPTION'].str.contains('FOUL') & attempt_data['DESCRIPTION'].str.contains('TRIP')) &
            ~attempt_data['DESCRIPTION'].str.contains('MISS') &
            ~attempt_data['DESCRIPTION'].str.contains('BLOCK') &
            attempt_data['DESCRIPTION'].str.contains('3PT'),
            'PTS'] += 3

        attempt_data = attempt_data.drop_duplicates()
        return attempt_data

    def get_attempts_boxscores(self, game_id):
        play_by_play_attempts = self.get_play_by_play_attempts(game_id)
        if play_by_play_attempts.empty:
            return pd.DataFrame()

        attempts_boxscores = pd.DataFrame(columns=[
            'PLAYER_ID', 'TOTAL_ATTEMPTS', 'TOTAL_PTS', 'TOTAL_FTA', 'TOTAL_FTM',
            'SHOT_ATTEMPTS', 'SHOT_PTS', 'SHOT_FTA', 'SHOT_FTM',
            'SFOUL_ATTEMPTS', 'SFOUL_PTS', 'SFOUL_FTA', 'SFOUL_FTM',
            'PFOUL_ATTEMPTS', 'PFOUL_PTS', 'PFOUL_FTA', 'PFOUL_FTM',
            'TFOUL_ATTEMPTS', 'TFOUL_PTS', 'TFOUL_FTA', 'TFOUL_FTM'
            ])
        for player_id, player_plays in play_by_play_attempts.groupby(['PLAYER_ID']):
            shot_plays = player_plays.loc[~player_plays['DESCRIPTION'].str.contains('TRIP')]
            shot_attempts = len(shot_plays)
            shot_pts = shot_plays['PTS'].sum()
            shot_fta = shot_plays['FTA'].sum()
            shot_ftm = shot_plays['FTM'].sum()

            sfoul_plays = player_plays.loc[player_plays['DESCRIPTION'] == 'SFOUL TRIP']
            sfoul_attempts = len(sfoul_plays)
            sfoul_pts = sfoul_plays['PTS'].sum()
            sfoul_fta = sfoul_plays['FTA'].sum()
            sfoul_ftm = sfoul_plays['FTM'].sum()

            pfoul_plays = player_plays.loc[
                (player_plays['DESCRIPTION'].str.contains('TRIP')) &
                (player_plays['DESCRIPTION'] != 'SFOUL TRIP') & 
                (~player_plays['DESCRIPTION'].str.contains('TFOUL')) &
                (~player_plays['DESCRIPTION'].str.contains('FLAGRANTFOUL'))
                ]
            pfoul_attempts = len(pfoul_plays)
            pfoul_pts = pfoul_plays['PTS'].sum()
            pfoul_fta = pfoul_plays['FTA'].sum()
            pfoul_ftm = pfoul_plays['FTM'].sum()

            tfoul_plays = player_plays.loc[
                (player_plays['DESCRIPTION'].str.contains('TFOUL')) |
                (player_plays['DESCRIPTION'].str.contains('FLAGRANTFOUL'))
                ]
            tfoul_attempts = len(tfoul_plays)
            tfoul_pts = tfoul_plays['PTS'].sum()
            tfoul_fta = tfoul_plays['FTA'].sum()
            tfoul_ftm = tfoul_plays['FTM'].sum()

            total_attempts = len(player_plays) - tfoul_attempts
            total_pts = player_plays['PTS'].sum()
            total_fta = player_plays['FTA'].sum()
            total_ftm = player_plays['FTM'].sum()

            temp = pd.Series(
                [player_id, total_attempts, total_pts, total_fta, total_ftm,
                shot_attempts, shot_pts, shot_fta, shot_ftm,
                sfoul_attempts, sfoul_pts, sfoul_fta, sfoul_ftm,
                pfoul_attempts, pfoul_pts, pfoul_fta, pfoul_ftm,
                tfoul_attempts, tfoul_pts, tfoul_fta, tfoul_ftm],
                index=['PLAYER_ID', 'TOTAL_ATTEMPTS', 'TOTAL_PTS', 'TOTAL_FTA', 'TOTAL_FTM',
                    'SHOT_ATTEMPTS', 'SHOT_PTS', 'SHOT_FTA', 'SHOT_FTM',
                    'SFOUL_ATTEMPTS', 'SFOUL_PTS', 'SFOUL_FTA', 'SFOUL_FTM',
                    'PFOUL_ATTEMPTS', 'PFOUL_PTS', 'PFOUL_FTA', 'PFOUL_FTM',
                    'TFOUL_ATTEMPTS', 'TFOUL_PTS', 'TFOUL_FTA', 'TFOUL_FTM']
                )
            attempts_boxscores = attempts_boxscores.append(temp, ignore_index=True)

        attempts_boxscores['GAME_ID'] = game_id
        return attempts_boxscores

    def get_play_type_breakdown(self, play_type, season, player_or_team):
        if player_or_team == 'player':
            player_or_team_abbreviation = 'P'
            type_grouping_nullable = 'Offensive'
        elif player_or_team == 'team':
            player_or_team_abbreviation = 'T'
            type_grouping_nullable = 'Defensive'
        else:
            raise Exception('player_or_team parameter must be one of the following: player, team')

        if season != CURRENT_SEASON:
            file_name = "/Users/brandonshimiaie/Projects/pyNBA/pyNBA/Data/playtypedata/{}/{}_{}_Final.pkl".format(
                player_or_team, play_type, season
                )
        else:
            current_date_string = datetime.now().strftime("%Y-%m-%d")
            file_name = "/Users/brandonshimiaie/Projects/pyNBA/pyNBA/Data/playtypedata/{}/{}_{}_{}.pkl".format(
                player_or_team, play_type, season, current_date_string
                )

        if not path.exists(file_name):
            play_type_breakdown = SynergyPlayTypes(
                season=season, play_type_nullable=play_type, season_type_all_star='Regular Season',
                player_or_team_abbreviation=player_or_team_abbreviation, type_grouping_nullable=type_grouping_nullable
                ).get_data_frames()[0]
            time.sleep(2.000)
            play_type_breakdown.to_pickle(file_name)

        return pd.read_pickle(file_name)

    def prepare_team(self, team):
        if team in LINEUP_TEAM_TO_NBA_TEAM:
            return LINEUP_TEAM_TO_NBA_TEAM[team]
        return team

    def prepare_name(self, name, team):
        if name in LINEUP_NAME_TO_NBA_NAME:
            if isinstance(LINEUP_NAME_TO_NBA_NAME[name], dict):
                return LINEUP_NAME_TO_NBA_NAME[name][team]
            return LINEUP_NAME_TO_NBA_NAME[name]
        return name

    def get_player_data(self, lineup):
        player_data = pd.DataFrame(columns=['NAME', 'START', 'PLAYERSTATUS', 'PLAYERCHANCE'])

        players_added = {}
        lineup_status = ''
        start = 1

        rows = lineup.find_all('li')
        for row in rows:
            row_class = row['class']
            if row_class[0] == 'lineup__status':
                lineup_status_data = row_class[1]
                if lineup_status_data == 'is-expected':
                    lineup_status = 'Expected'
                elif lineup_status_data == 'is-confirmed':
                    lineup_status = 'Confirmed'
            elif row_class[0] == 'lineup__title':
                start = 0
            elif row_class[0] == 'lineup__player':
                player_position = row.find('div', class_='lineup__pos').text
                player_name = row.find('a').text
                status_data = row.find('span', class_='lineup__inj')
                player_status = 'Healthy' if status_data is None else status_data.text
                player_chance = int(row_class[1].split('-')[-1])
                if player_position != 'BE' and player_name not in players_added:
                    temp = pd.Series(
                        [player_name, start, player_status, player_chance],
                        index=['NAME', 'START', 'PLAYERSTATUS', 'PLAYERCHANCE']
                        )
                    player_data = player_data.append(temp, ignore_index=True)
                    players_added[player_name] = 1
                    
        return player_data, lineup_status
