import pandas as pd
import numpy as np
from pyNBA.Data.data import QueryData
from pyNBA.Models.helpers import CleanData
from pyNBA.DFS.rules import FPCalculator
from pyNBA.DFS.constants import Site
from pyNBA.Data.constants import (ROTOWIRE_NAME_TO_NBA_NAME, LINESTARAPP_TEAM_TO_NBA_TEAM,
                                  LINESTARAPP_NAME_TO_NBA_NAME, OWNERSHIP_NAME_TO_NBA_NAME,
                                  BAD_CONTEST_SUBSTRINGS)

class GetData(object):
    def __init__(self, site: Site):
        self.query_data = QueryData(update=False)
        self.clean_data = CleanData()
        self.site = site

    def get_projection_data(self):

        linestarapp_data = self.query_data.query_linestarapp_data()
        linestarapp_data = linestarapp_data.loc[linestarapp_data['SITE'] == self.site]
        linestarapp_data['PLAYER_NAME'] = linestarapp_data['PLAYER_NAME'].apply(
            lambda x: x if x not in LINESTARAPP_NAME_TO_NBA_NAME else LINESTARAPP_NAME_TO_NBA_NAME[x]
        )
        linestarapp_data['TEAM'] = linestarapp_data['TEAM'].apply(
            lambda x: x if x not in LINESTARAPP_TEAM_TO_NBA_TEAM else LINESTARAPP_TEAM_TO_NBA_TEAM[x]
        )

        rotowire_data = self.query_data.query_rotowire_data()
        rotowire_data = rotowire_data.drop(columns=['TEAM', 'POS', 'G'])
        rotowire_data['PLAYER_NAME'] = rotowire_data['PLAYER_NAME'].apply(
            lambda x: x if x not in ROTOWIRE_NAME_TO_NBA_NAME else ROTOWIRE_NAME_TO_NBA_NAME[x]
        )

        boxscore_data = self.query_data.query_boxscore_data()

        def _get_projection(projection_1, projection_2):
            """Returns a projection given two projections, with favor to the first projection"""
            if np.isnan(projection_1) and np.isnan(projection_2):
                return 0
            elif np.isnan(projection_1):
                return projection_2
            elif np.isnan(projection_2):
                return projection_1
            elif projection_1 == 0 or projection_2 == 0:
                return 0
            else:
                return projection_1

        linestarapp_data = linestarapp_data.loc[linestarapp_data['SITE'] == self.site]
        linestarapp_data = linestarapp_data.rename(columns={'PROJECTION': 'LINESTARAPP_PROJECTION'})

        rotowire_data['ROTOWIRE_PROJECTION'] = rotowire_data.apply(
            lambda row: FPCalculator.calculate_draftkings_fp(
                row['PTS'], row['REB'], row['AST'], row['TOV'], row['BLK'], row['STL'],
                row['THREEPM'], (row['DBLDBL'], row['TRPDBL'])
            ),
            axis=1
        )
        projections = linestarapp_data.merge(rotowire_data, on=['DATE', 'PLAYER_NAME'], how='left')
        projections['PROJECTION'] = projections.apply(
            lambda row: _get_projection(row['ROTOWIRE_PROJECTION'], row['LINESTARAPP_PROJECTION']),
            axis=1
        )

        player_comments = boxscore_data[['DATE', 'NAME', 'COMMENT']]
        player_comments = player_comments.rename(columns={'NAME': 'PLAYER_NAME'})
        projections = projections.merge(player_comments, on=['DATE', 'PLAYER_NAME'], how='left')

        projections = projections.loc[projections['DATE'].isin(set(boxscore_data['DATE'].unique()))]
        projections = projections[[
            'DATE', 'SITE', 'PLAYER_ID', 'PLAYER_NAME', 'POS', 'TEAM', 'START', 'SPREAD', 'TOTAL',
            'OPPRANK_DvP_L20', 'OPPRANK_D_L20', 'PROJECTION', 'FINAL', 'COMMENT'
        ]]

        return projections

    def get_salary_data(self):
        linestarapp_data = self.query_data.query_linestarapp_data()
        linestarapp_data = linestarapp_data.loc[linestarapp_data['SITE'] == self.site]
        linestarapp_data['PLAYER_NAME'] = linestarapp_data['PLAYER_NAME'].apply(
            lambda x: x if x not in LINESTARAPP_NAME_TO_NBA_NAME else LINESTARAPP_NAME_TO_NBA_NAME[x]
        )
        linestarapp_data['TEAM'] = linestarapp_data['TEAM'].apply(
            lambda x: x if x not in LINESTARAPP_TEAM_TO_NBA_TEAM else LINESTARAPP_TEAM_TO_NBA_TEAM[x]
        )

        salary_data = self.query_data.query_salary_data()
        salary_data = salary_data.loc[salary_data['SITE'] == self.site]
        salary_data['POSITION'] = salary_data['POSITION'].apply(lambda x: x.replace('_', '/'))
        salary_data['NAME'] = salary_data['PLAYER'].apply(self.clean_data.convert_rotoguru_name_to_nba_name)

        boxscore_data = self.query_data.query_boxscore_data()

        salaries = linestarapp_data.merge(
            salary_data,
            left_on=['SITE', 'DATE', 'PLAYER_NAME', 'POS'],
            right_on=['SITE', 'DATE', 'NAME', 'POSITION'],
            how='left',
            suffixes = ('_linestarrapp', '_rotoguru')
        )

        salaries = salaries.loc[salaries['DATE'].isin(set(boxscore_data['DATE'].unique()))]

        salaries['SALARY'] = salaries[['SALARY_linestarrapp', 'SALARY_rotoguru']].min(axis=1)
        salaries.loc[salaries['SALARY'] < 3000, 'SALARY'] = 3000
        salaries = salaries[['DATE', 'SITE', 'PLAYER_ID', 'PLAYER_NAME', 'POS', 'TEAM', 'SALARY']]

        return salaries
    
    def get_ownership_data(self):
        contest_data = self.query_data.query_contest_data()
        contest_data = contest_data.loc[contest_data['SITE'] == self.site]
        contest_data = contest_data.loc[
            (contest_data['SLATETYPE'] == 'Classic') & (contest_data['CASHLINE'] > 200) &
            (~contest_data['CONTESTNAME'].str.lower().str.contains('|'.join(BAD_CONTEST_SUBSTRINGS)))
        ].dropna(subset=['CASHLINE'])
        contest_data['MAXROI'] = contest_data['TOPPRIZE']/contest_data['ENTRYFEE']
        contest_data = contest_data.loc[contest_data['MAXROI'] > 2]

        ownership_data = self.query_data.query_ownership_data()
        ownership_data['PLAYERNAME'] = ownership_data['PLAYERNAME'].apply(
            lambda x: x if x not in OWNERSHIP_NAME_TO_NBA_NAME else OWNERSHIP_NAME_TO_NBA_NAME[x]
        )
        ownership_data = ownership_data.rename(columns={'PLAYERNAME': 'PLAYER_NAME'})
        ownership_data = ownership_data.groupby(['SLATEID', 'PLAYER_NAME'])['OWNERSHIP'].mean().reset_index()

        slate_dates = contest_data[['DATE', 'SITE', 'SLATEID', 'GAMECOUNT']].drop_duplicates()
        ownerships = ownership_data.merge(slate_dates, on=['SLATEID'], how='inner')

        slate_players_per_game = (
            ownerships.groupby('SLATEID')['PLAYER_NAME'].count() / ownerships.groupby('SLATEID')['GAMECOUNT'].first()
        ).reset_index()
        bad_slates = slate_players_per_game.loc[
            (slate_players_per_game[0] < 20) |
            (slate_players_per_game[0] > 40)
        ]['SLATEID'].unique()
        ownerships = ownerships.loc[~ownerships['SLATEID'].isin(bad_slates)]

        return ownerships
    
    def get_player_data(self):
        boxscore_data = self.query_data.query_boxscore_data()

        projections = self.get_projection_data()
        salaries = self.get_salary_data()
        ownerships = self.get_ownership_data()

        player_data = ownerships.merge(
            salaries,
            on=['DATE', 'SITE', 'PLAYER_NAME'],
            how='left'
        )
        player_data = player_data.merge(
            projections,
            on=['DATE', 'SITE', 'PLAYER_ID', 'PLAYER_NAME', 'POS', 'TEAM'],
            how='left'
        )

        season_dates = boxscore_data[['SEASON', 'DATE']].drop_duplicates()
        player_data = player_data.merge(
            season_dates,
            on=['DATE'],
            how='left'
        )

        player_data = player_data.dropna(subset=['SALARY'])
        player_data = player_data.loc[
            (player_data['PROJECTION'] != 0) |
            (player_data['COMMENT'].isnull()) |
            (player_data['COMMENT'] == '') |
            (player_data['COMMENT'].str.contains('coach', case=False))
        ]

        player_data = player_data[[
            'SEASON', 'DATE', 'SLATEID', 'GAMECOUNT', 'PLAYER_ID', 'PLAYER_NAME', 'TEAM', 'POS', 'SALARY',
            'START', 'SPREAD', 'TOTAL', 'OPPRANK_DvP_L20', 'OPPRANK_D_L20', 'PROJECTION', 'FINAL', 'OWNERSHIP',
            'COMMENT'
        ]].sort_values(by=['DATE', 'SLATEID', 'SALARY'], ascending=[True, False, False])

        return player_data