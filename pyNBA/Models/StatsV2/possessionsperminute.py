import pandas as pd
import numpy as np
from pyNBA.Models.StatsV2.basestatmodel import BaseStatModel
from pyNBA.Models.features import FeatureCreation

class PossessionsPerMinute(object):
    def generate_regressors(self, boxscores, start_date, end_date):
        feature_creation = FeatureCreation()

        relevant_seasons = boxscores.loc[
                    (boxscores['DATE'] >= start_date) & 
                    (boxscores['DATE'] <= end_date)
                    ]['SEASON'].unique()
        boxscores = boxscores.loc[boxscores['SEASON'].isin(relevant_seasons)]

        boxscores['MP'] = boxscores['SECONDSPLAYED']/60
        boxscores['POSSESSIONS/MINUTE'] = boxscores['POSS']/boxscores['MP']

        # average player possessions/minute
        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='POSSESSIONS/MINUTE',
            new_col_name='AVG_POSSESSIONS/MINUTE', weight_col_name='MP'
        )

        # average possessions/minute that opp team allowed
        team_boxscores = boxscores.groupby(['SEASON', 'DATE', 'TEAM', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_POSSESSIONS': x['POSS'].sum(),
                'TEAM_MP': x['MP'].sum()
            })
        ).reset_index()
        team_boxscores['TEAM_POSSESSIONS/MINUTE'] = team_boxscores['TEAM_POSSESSIONS']/team_boxscores['TEAM_MP']

        opp_team_boxscores = team_boxscores.rename(
            columns={'TEAM': 'OPP_TEAM', 'OPP_TEAM': 'TEAM', 'TEAM_POSSESSIONS': 'OPP_TEAM_POSSESSIONS', 'TEAM_MP': 'OPP_TEAM_MP',
                    'TEAM_POSSESSIONS/MINUTE': 'OPP_TEAM_POSSESSIONS/MINUTE'}
        )

        team_boxscores = team_boxscores.merge(opp_team_boxscores, on=['SEASON', 'DATE', 'TEAM', 'OPP_TEAM'], how='left')

        team_boxscores = feature_creation.expanding_weighted_mean(
            df=team_boxscores, group_col_names=['SEASON', 'OPP_TEAM'], col_name='TEAM_POSSESSIONS/MINUTE',
            new_col_name='AVG_POSSESSIONS/MINUTE_OPP_TEAM_ALLOWED', weight_col_name='TEAM_MP'
        )

        # average possessions/minute that opp team played against
        season_stats = team_boxscores.groupby(['SEASON', 'TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_POSSESSIONS(SEASON)': x['TEAM_POSSESSIONS'].mean(),
                'TEAM_MP(SEASON)': x['TEAM_MP'].mean(),
                'TEAM_POSSESSIONS_ALLOWED(SEASON)': x['OPP_TEAM_POSSESSIONS'].mean(),
                'TEAM_MP_ALLOWED(SEASON)': x['OPP_TEAM_MP'].mean()
            })
        ).reset_index()

        season_stats['TEAM_POSSESSIONS/MINUTE(SEASON)'] = season_stats['TEAM_POSSESSIONS(SEASON)']/season_stats['TEAM_MP(SEASON)']
        season_stats['TEAM_POSSESSIONS/MINUTE_ALLOWED(SEASON)'] = \
            season_stats['TEAM_POSSESSIONS_ALLOWED(SEASON)']/season_stats['TEAM_MP_ALLOWED(SEASON)']

        opp_season_stats = season_stats.rename(columns={
            'TEAM': 'OPP_TEAM', 'TEAM_POSSESSIONS(SEASON)': 'OPP_TEAM_POSSESSIONS(SEASON)', 'TEAM_MP(SEASON)': 'OPP_TEAM_MP(SEASON)',
            'TEAM_POSSESSIONS_ALLOWED(SEASON)': 'OPP_TEAM_POSSESSIONS_ALLOWED(SEASON)',
            'TEAM_MP_ALLOWED(SEASON)': 'OPP_TEAM_MP_ALLOWED(SEASON)',
            'TEAM_POSSESSIONS/MINUTE(SEASON)': 'OPP_TEAM_POSSESSIONS/MINUTE(SEASON)',
            'TEAM_POSSESSIONS/MINUTE_ALLOWED(SEASON)': 'OPP_TEAM_POSSESSIONS/MINUTE_ALLOWED(SEASON)'
            })

        team_boxscores = team_boxscores.merge(season_stats, on=['SEASON', 'TEAM'], how='left')
        team_boxscores = team_boxscores.merge(opp_season_stats, on=['SEASON', 'OPP_TEAM'], how='left')

        team_boxscores = feature_creation.expanding_weighted_mean(
            df=team_boxscores, group_col_names=['SEASON', 'OPP_TEAM'], col_name='TEAM_POSSESSIONS/MINUTE(SEASON)',
            new_col_name='AVG_POSSESSIONS/MINUTE(SEASON)_OPP_TEAM_P.A.', weight_col_name='OPP_TEAM_MP'
        )

        # possessions/minute allowed that player played against
        boxscores = boxscores.merge(team_boxscores, on=['SEASON', 'DATE', 'TEAM', 'OPP_TEAM'], how='left')

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='OPP_TEAM_POSSESSIONS/MINUTE_ALLOWED(SEASON)',
            new_col_name='AVG_POSSESSIONS/MINUTE_ALLOWED(SEASON)_PLAYER_P.A.', weight_col_name='MP'
        )

        # player possessions/minute
        boxscores['PLAYER_POSSESSIONS/MINUTE'] = \
            2*boxscores['AVG_POSSESSIONS/MINUTE'] - boxscores['AVG_POSSESSIONS/MINUTE_ALLOWED(SEASON)_PLAYER_P.A.']

        # opp possessions/minute allowed
        boxscores['OPP_POSSESSIONS/MINUTE_ALLOWED'] = \
            2*boxscores['AVG_POSSESSIONS/MINUTE_OPP_TEAM_ALLOWED'] - boxscores['AVG_POSSESSIONS/MINUTE(SEASON)_OPP_TEAM_P.A.']

        boxscores = boxscores.loc[
            (boxscores['DATE'] >= start_date) & 
            (boxscores['DATE'] <= end_date)
            ]

        return boxscores

    def predict(self, boxscores, predict_start_date, predict_end_date):
        predicted_data = self.generate_regressors(boxscores, predict_start_date, predict_end_date)
        
        predicted_data = predicted_data.rename(columns={
            'PLAYER_POSSESSIONS/MINUTE': 'POSS/MP', 'OPP_POSSESSIONS/MINUTE_ALLOWED': 'POSS/MP_DEF'
            })
        cols = [
            'SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION', 'START', 'PLAYERCHANCE',
            'POSS/MP', 'POSS/MP_DEF'
            ]
        return predicted_data[cols]