import pandas as pd
import numpy as np
from pyNBA.Models.StatsV2.basestatmodel import BaseStatModel
from pyNBA.Models.base import LinearRegressionModel
from pyNBA.Models.features import FeatureCreation
from pyNBA.Data.data import QueryData

class ReboundsPerPossession(object):
    def generate_regressors(self, boxscores, start_date, end_date):
        feature_creation = FeatureCreation()

        relevant_seasons = boxscores.loc[
                    (boxscores['DATE'] >= start_date) & 
                    (boxscores['DATE'] <= end_date)
                    ]['SEASON'].unique()
        boxscores = boxscores.loc[boxscores['SEASON'].isin(relevant_seasons)]

        team_boxscores = boxscores.groupby(['SEASON', 'DATE', 'TEAM', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_POSSESSIONS': x['POSS'].sum()/5,
                'TEAM_OREB': x['OREB'].sum(),
                'TEAM_DREB': x['DREB'].sum()
            })
        ).reset_index()

        opp_team_boxscores = team_boxscores.drop(columns='OPP_TEAM')
        opp_team_boxscores = opp_team_boxscores.rename(columns={
            'TEAM': 'OPP_TEAM', 'TEAM_POSSESSIONS': 'OPP_TEAM_POSSESSIONS', 'TEAM_OREB': 'OPP_TEAM_OREB',
            'TEAM_DREB': 'OPP_TEAM_DREB'
            })
        team_boxscores = team_boxscores.merge(opp_team_boxscores, on=['SEASON', 'DATE', 'OPP_TEAM'], how='left')

        team_boxscores['TEAM_OREB_CHANCES'] = team_boxscores['TEAM_OREB'] + team_boxscores['OPP_TEAM_DREB']
        team_boxscores['TEAM_DREB_CHANCES'] = team_boxscores['TEAM_DREB'] + team_boxscores['OPP_TEAM_OREB']

        # average team oreb chances/possession
        team_boxscores['TEAM_OREB_CHANCES/POSSESSION'] = team_boxscores['TEAM_OREB_CHANCES']/team_boxscores['TEAM_POSSESSIONS']

        team_boxscores = feature_creation.expanding_weighted_mean(
            df=team_boxscores, group_col_names=['SEASON', 'TEAM'], col_name='TEAM_OREB_CHANCES/POSSESSION',
            new_col_name='AVG_TEAM_OREB_CHANCES/POSSESSION', weight_col_name='TEAM_POSSESSIONS'
        )

        # average oreb chances/possession that opp team allowed
        team_boxscores = feature_creation.expanding_weighted_mean(
            df=team_boxscores, group_col_names=['SEASON', 'OPP_TEAM'], col_name='TEAM_OREB_CHANCES/POSSESSION',
            new_col_name='AVG_OREB_CHANCES/POSSESSION_OPP_TEAM_ALLOWED', weight_col_name='TEAM_POSSESSIONS'
        )

        # average oreb chances/possession allowed that team played against
        season_stats = team_boxscores.groupby(['SEASON', 'TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_OREB_ALLOWED(SEASON)': x['OPP_TEAM_OREB'].mean(),
                'TEAM_OREB_CHANCES(SEASON)': x['TEAM_OREB_CHANCES'].mean(),
                'TEAM_OREB_CHANCES_ALLOWED(SEASON)': x['TEAM_DREB_CHANCES'].mean(),
                'TEAM_DREB_ALLOWED(SEASON)': x['OPP_TEAM_DREB'].mean(),
                'TEAM_DREB_CHANCES(SEASON)': x['TEAM_DREB_CHANCES'].mean(),
                'TEAM_DREB_CHANCES_ALLOWED(SEASON)': x['TEAM_DREB_CHANCES'].mean(),
                'TEAM_POSSESSIONS(SEASON)': x['TEAM_POSSESSIONS'].mean(),
                'TEAM_POSSESSIONS_ALLOWED(SEASON)': x['OPP_TEAM_POSSESSIONS'].mean()
            })
        ).reset_index()

        opp_season_stats = season_stats.rename(columns={
            'TEAM': 'OPP_TEAM',
            'TEAM_OREB_ALLOWED(SEASON)': 'OPP_TEAM_OREB_ALLOWED(SEASON)',
            'TEAM_OREB_CHANCES(SEASON)': 'OPP_TEAM_OREB_CHANCES(SEASON)',
            'TEAM_OREB_CHANCES_ALLOWED(SEASON)': 'OPP_TEAM_OREB_CHANCES_ALLOWED(SEASON)',
            'TEAM_DREB_ALLOWED(SEASON)': 'OPP_TEAM_DREB_ALLOWED(SEASON)',
            'TEAM_DREB_CHANCES(SEASON)': 'OPP_TEAM_DREB_CHANCES(SEASON)',
            'TEAM_DREB_CHANCES_ALLOWED(SEASON)': 'OPP_TEAM_DREB_CHANCES_ALLOWED(SEASON)',
            'TEAM_POSSESSIONS(SEASON)': 'OPP_TEAM_POSSESSIONS(SEASON)',
            'TEAM_POSSESSIONS_ALLOWED(SEASON)': 'OPP_TEAM_POSSESSIONS_ALLOWED(SEASON)'
            })


        team_boxscores = team_boxscores.merge(season_stats, on=['SEASON', 'TEAM'], how='left')
        team_boxscores = team_boxscores.merge(opp_season_stats, on=['SEASON', 'OPP_TEAM'], how='left')

        team_boxscores['OPP_TEAM_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)'] = \
            team_boxscores['OPP_TEAM_OREB_CHANCES_ALLOWED(SEASON)']/team_boxscores['OPP_TEAM_POSSESSIONS_ALLOWED(SEASON)']

        team_boxscores = feature_creation.expanding_weighted_mean(
            df=team_boxscores, group_col_names=['SEASON', 'TEAM'], col_name='OPP_TEAM_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)',
            new_col_name='AVG_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)_TEAM_P.A.', weight_col_name='TEAM_POSSESSIONS'
        )

        # average oreb chances/possession that opp team played against
        team_boxscores['TEAM_OREB_CHANCES/POSSESSION(SEASON)'] = \
            team_boxscores['TEAM_OREB_CHANCES(SEASON)']/team_boxscores['TEAM_POSSESSIONS(SEASON)']

        team_boxscores = feature_creation.expanding_weighted_mean(
            df=team_boxscores, group_col_names=['SEASON', 'OPP_TEAM'], col_name='TEAM_OREB_CHANCES/POSSESSION(SEASON)',
            new_col_name='AVG_OREB_CHANCES/POSSESSION(SEASON)_OPP_TEAM_P.A.', weight_col_name='OPP_TEAM_POSSESSIONS'
        )

        # team oreb chances/possession
        team_boxscores['TEAM_OREB_CHANCES/POSSESSION_HAT'] = \
            2*team_boxscores['AVG_TEAM_OREB_CHANCES/POSSESSION'] - \
                team_boxscores['AVG_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)_TEAM_P.A.']

        # opp team oreb chances/possession allowed
        team_boxscores['OPP_TEAM_OREB_CHANCES/POSSESSION_ALLOWED_HAT'] = \
            2*team_boxscores['AVG_OREB_CHANCES/POSSESSION_OPP_TEAM_ALLOWED'] - \
                team_boxscores['AVG_OREB_CHANCES/POSSESSION(SEASON)_OPP_TEAM_P.A.']

        boxscores = boxscores.merge(team_boxscores, on=['SEASON', 'DATE', 'TEAM', 'OPP_TEAM'], how='left')

        boxscores['OREB_CHANCES'] = np.nan
        boxscores.loc[boxscores['OREB'] > 0, 'OREB_CHANCES'] = (
            boxscores.loc[boxscores['OREB'] > 0, 'OREB'] / boxscores.loc[boxscores['OREB'] > 0, 'OREB_PCT']
            ).apply(lambda x: round(x))
        boxscores.loc[boxscores['OREB'] == 0, 'OREB_CHANCES'] = \
            boxscores.loc[boxscores['OREB'] == 0, 'TEAM_OREB_CHANCES/POSSESSION']*boxscores.loc[boxscores['OREB'] == 0, 'POSS']

        boxscores['TEAM_DREB_CHANCES/POSSESSION'] = boxscores['TEAM_DREB_CHANCES']/boxscores['TEAM_POSSESSIONS']

        boxscores['DREB_CHANCES'] = np.nan
        boxscores.loc[boxscores['DREB'] > 0, 'DREB_CHANCES'] = (
            boxscores.loc[boxscores['DREB'] > 0, 'DREB'] / boxscores.loc[boxscores['DREB'] > 0, 'DREB_PCT']
            ).apply(lambda x: round(x))
        boxscores.loc[boxscores['DREB'] == 0, 'DREB_CHANCES'] = \
            boxscores.loc[boxscores['DREB'] == 0, 'TEAM_DREB_CHANCES/POSSESSION']*boxscores.loc[boxscores['DREB'] == 0, 'POSS']

        temp = boxscores.groupby(['SEASON', 'DATE', 'TEAM', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'IMPLIED_TEAM_OREB_CHANCES': x['OREB_CHANCES'].sum()/5,
                'IMPLIED_TEAM_DREB_CHANCES': x['DREB_CHANCES'].sum()/5
            })
        ).reset_index()
        boxscores = boxscores.merge(temp, on=['SEASON', 'DATE', 'TEAM', 'OPP_TEAM'], how='left')

        # average player oreb/chance
        boxscores['OREB_CHANCES'] = boxscores['OREB_CHANCES']*(boxscores['TEAM_OREB_CHANCES']/boxscores['IMPLIED_TEAM_OREB_CHANCES']) 
        boxscores['OREB/OREB_CHANCE'] = boxscores['OREB']/boxscores['OREB_CHANCES']

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='OREB/OREB_CHANCE',
            new_col_name='AVG_OREB/OREB_CHANCE', weight_col_name='OREB_CHANCES'
        )

        # average player dreb/chance
        boxscores['DREB_CHANCES'] = boxscores['DREB_CHANCES']*(boxscores['TEAM_DREB_CHANCES']/boxscores['IMPLIED_TEAM_DREB_CHANCES']) 
        boxscores['DREB/DREB_CHANCE'] = boxscores['DREB']/boxscores['DREB_CHANCES']

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='DREB/DREB_CHANCE',
            new_col_name='AVG_DREB/DREB_CHANCE', weight_col_name='DREB_CHANCES'
        )

        # average oreb/oreb chance that opp team allowed
        team_game_boxscores = boxscores.groupby(['SEASON', 'DATE', 'TEAM', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_OREB': x['OREB'].sum(),
                'TEAM_OREB_CHANCES': x['OREB_CHANCES'].sum()/5,
                'TEAM_DREB': x['DREB'].sum(),
                'TEAM_DREB_CHANCES': x['DREB_CHANCES'].sum()/5
            })
        ).reset_index()

        opp_team_game_boxscores = team_game_boxscores.drop(columns='OPP_TEAM')
        opp_team_game_boxscores = opp_team_game_boxscores.rename(columns={
            'TEAM': 'OPP_TEAM', 'TEAM_OREB': 'OPP_TEAM_OREB',
            'TEAM_OREB_CHANCES': 'OPP_TEAM_OREB_CHANCES', 'TEAM_DREB': 'OPP_TEAM_DREB',
            'TEAM_DREB_CHANCES': 'OPP_TEAM_DREB_CHANCES'
            })
        team_game_boxscores = team_game_boxscores.merge(
            opp_team_game_boxscores, on=['SEASON', 'DATE', 'OPP_TEAM'], how='left'
            )

        team_game_boxscores['TEAM_OREB/OREB_CHANCE'] = \
            team_game_boxscores['TEAM_OREB']/team_game_boxscores['TEAM_OREB_CHANCES']

        team_game_boxscores = feature_creation.expanding_weighted_mean(
            df=team_game_boxscores, group_col_names=['SEASON', 'OPP_TEAM'],
            col_name='TEAM_OREB/OREB_CHANCE', new_col_name='AVG_TEAM_OREB/OREB_CHANCE_OPP_ALLOWED',
            weight_col_name='TEAM_OREB_CHANCES'
        )

        # average dreb/dreb chance that opp team allowed
        team_game_boxscores['TEAM_DREB/DREB_CHANCE'] = \
            team_game_boxscores['TEAM_DREB']/team_game_boxscores['TEAM_DREB_CHANCES']

        team_game_boxscores = feature_creation.expanding_weighted_mean(
            df=team_game_boxscores, group_col_names=['SEASON', 'OPP_TEAM'],
            col_name='TEAM_DREB/DREB_CHANCE', new_col_name='AVG_TEAM_DREB/DREB_CHANCE_OPP_ALLOWED',
            weight_col_name='TEAM_DREB_CHANCES'
        )

        boxscores = boxscores.merge(
            team_game_boxscores, on=['SEASON', 'DATE', 'TEAM', 'OPP_TEAM'], how='left'
        )

        # average oreb/oreb chance allowed that player played against
        boxscores['OPP_TEAM_OREB/OREB_CHANCE_ALLOWED(SEASON)'] = \
            boxscores['OPP_TEAM_OREB_ALLOWED(SEASON)'] / boxscores['OPP_TEAM_OREB_CHANCES_ALLOWED(SEASON)']

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'],
            col_name='OPP_TEAM_OREB/OREB_CHANCE_ALLOWED(SEASON)',
            new_col_name='AVG_TEAM_OREB/OREB_CHANCE(SEASON)_ALLOWED_PLAYER_P.A',
            weight_col_name='OREB_CHANCES'
        )

        # average dreb/dreb chance allowed that player played against
        boxscores['OPP_TEAM_DREB/DREB_CHANCE_ALLOWED(SEASON)'] = \
            boxscores['OPP_TEAM_DREB_ALLOWED(SEASON)'] / boxscores['OPP_TEAM_DREB_CHANCES_ALLOWED(SEASON)']

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'],
            col_name='OPP_TEAM_DREB/DREB_CHANCE_ALLOWED(SEASON)',
            new_col_name='AVG_TEAM_DREB/DREB_CHANCE(SEASON)_ALLOWED_PLAYER_P.A',
            weight_col_name='DREB_CHANCES'
        )

        # oreb/oreb chance defense
        boxscores['OREB/CH_DEF'] = \
            boxscores['AVG_TEAM_OREB/OREB_CHANCE_OPP_ALLOWED'] / \
                boxscores['AVG_TEAM_OREB/OREB_CHANCE(SEASON)_ALLOWED_PLAYER_P.A']

        # dreb/dreb chance defense
        boxscores['DREB/CH_DEF'] = \
            boxscores['AVG_TEAM_DREB/DREB_CHANCE_OPP_ALLOWED'] / \
                boxscores['AVG_TEAM_DREB/DREB_CHANCE(SEASON)_ALLOWED_PLAYER_P.A']

        boxscores = boxscores.loc[
            (boxscores['DATE'] >= start_date) & 
            (boxscores['DATE'] <= end_date)
            ]

        return boxscores

    def predict(self, boxscores, predict_start_date, predict_end_date):
        predicted_data = self.generate_regressors(boxscores, predict_start_date, predict_end_date)

        predicted_data = predicted_data.rename(columns={
            'TEAM_OREB_CHANCES/POSSESSION_HAT': 'OREB(CH)/POSS',
            'OPP_TEAM_OREB_CHANCES/POSSESSION_ALLOWED_HAT': 'OREB(CH)/POSS_DEF',
            'AVG_OREB/OREB_CHANCE': 'OREB/CH',
            'AVG_DREB/DREB_CHANCE': 'DREB/CH'
            })
        cols = [
            'SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION', 'START', 'PLAYERCHANCE',
            'OREB(CH)/POSS', 'OREB(CH)/POSS_DEF',
            'OREB/CH', 'OREB/CH_DEF', 'DREB/CH', 'DREB/CH_DEF'
            ]
        return predicted_data[cols]