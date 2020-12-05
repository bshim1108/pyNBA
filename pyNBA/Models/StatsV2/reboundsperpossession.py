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
            'TEAM': 'OPP_TEAM', 'TEAM_POSSESSIONS': 'OPP_TEAM_POSSESSIONS', 'TEAM_OREB': 'OPP_TEAM_OREB', 'TEAM_DREB': 'OPP_TEAM_DREB'
            })
        team_boxscores = team_boxscores.merge(opp_team_boxscores, on=['SEASON', 'DATE', 'OPP_TEAM'], how='left')

        team_boxscores['TEAM_OREB_CHANCES'] = team_boxscores['TEAM_OREB'] + team_boxscores['OPP_TEAM_DREB']
        team_boxscores['TEAM_OREB_CHANCES/POSSESSION'] = team_boxscores['TEAM_OREB_CHANCES']/team_boxscores['TEAM_POSSESSIONS']

        team_boxscores['OPP_TEAM_OREB_CHANCES'] = team_boxscores['TEAM_DREB'] + team_boxscores['OPP_TEAM_OREB']
        team_boxscores['OPP_TEAM_OREB_CHANCES/POSSESSION'] = \
            team_boxscores['OPP_TEAM_OREB_CHANCES']/team_boxscores['OPP_TEAM_POSSESSIONS']

        # average team oreb chances/possession
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
                'TEAM_OREB_CHANCES(SEASON)': x['TEAM_OREB_CHANCES'].mean(),
                'TEAM_POSSESSIONS(SEASON)': x['TEAM_POSSESSIONS'].mean(),
                'TEAM_OREB_CHANCES_ALLOWED(SEASON)': x['OPP_TEAM_OREB_CHANCES'].mean(),
                'TEAM_POSSESSIONS_ALLOWED(SEASON)': x['OPP_TEAM_POSSESSIONS'].mean(),
            })
        ).reset_index()

        season_stats['TEAM_OREB_CHANCES/POSSESSION(SEASON)'] = \
            season_stats['TEAM_OREB_CHANCES(SEASON)']/season_stats['TEAM_POSSESSIONS(SEASON)']
        season_stats['TEAM_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)'] = \
            season_stats['TEAM_OREB_CHANCES_ALLOWED(SEASON)']/season_stats['TEAM_POSSESSIONS_ALLOWED(SEASON)']

        opp_season_stats = season_stats.rename(columns={
            'TEAM': 'OPP_TEAM', 'TEAM_OREB_CHANCES(SEASON)': 'OPP_TEAM_OREB_CHANCES(SEASON)',
            'TEAM_POSSESSIONS(SEASON)': 'OPP_TEAM_POSSESSIONS(SEASON)',
            'TEAM_OREB_CHANCES_ALLOWED(SEASON)': 'OPP_TEAM_OREB_CHANCES_ALLOWED(SEASON)',
            'TEAM_POSSESSIONS_ALLOWED(SEASON)': 'OPP_TEAM_POSSESSIONS_ALLOWED(SEASON)',
            'TEAM_OREB_CHANCES/POSSESSION(SEASON)': 'OPP_TEAM_OREB_CHANCES/POSSESSION(SEASON)',
            'TEAM_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)': 'OPP_TEAM_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)'
            })


        team_boxscores = team_boxscores.merge(season_stats, on=['SEASON', 'TEAM'], how='left')
        team_boxscores = team_boxscores.merge(opp_season_stats, on=['SEASON', 'OPP_TEAM'], how='left')

        team_boxscores = feature_creation.expanding_weighted_mean(
            df=team_boxscores, group_col_names=['SEASON', 'TEAM'], col_name='OPP_TEAM_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)',
            new_col_name='AVG_OREB_CHANCES/POSSESSION_ALLOWED(SEASON)_TEAM_P.A.', weight_col_name='TEAM_POSSESSIONS'
        )

        # average oreb chances/possession that opp team played against
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

        # average player oreb/chance
        boxscores = boxscores.merge(team_boxscores, on=['SEASON', 'DATE', 'TEAM', 'OPP_TEAM'], how='left')

        boxscores['OREB_CHANCES'] = np.nan
        boxscores.loc[boxscores['OREB'] > 0, 'OREB_CHANCES'] = (
            boxscores.loc[boxscores['OREB'] > 0, 'OREB'] / boxscores.loc[boxscores['OREB'] > 0, 'OREB_PCT']
            ).apply(lambda x: round(x))
        boxscores.loc[boxscores['OREB'] == 0, 'OREB_CHANCES'] = \
            boxscores.loc[boxscores['OREB'] == 0, 'TEAM_OREB_CHANCES/POSSESSION']*boxscores.loc[boxscores['OREB'] == 0, 'POSS']
        boxscores['OREB/OREB_CHANCE'] = boxscores['OREB']/boxscores['OREB_CHANCES']

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='OREB/OREB_CHANCE',
            new_col_name='AVG_OREB/OREB_CHANCE', weight_col_name='OREB_CHANCES'
        )

        # average player dreb/chance
        boxscores['TEAM_DREB_CHANCES/POSSESSION'] = boxscores['OPP_TEAM_OREB_CHANCES/POSSESSION']

        boxscores['DREB_CHANCES'] = np.nan
        boxscores.loc[boxscores['DREB'] > 0, 'DREB_CHANCES'] = (
            boxscores.loc[boxscores['DREB'] > 0, 'DREB'] / boxscores.loc[boxscores['DREB'] > 0, 'DREB_PCT']
            ).apply(lambda x: round(x))
        boxscores.loc[boxscores['DREB'] == 0, 'DREB_CHANCES'] = \
            boxscores.loc[boxscores['OREB'] == 0, 'TEAM_DREB_CHANCES/POSSESSION']*boxscores.loc[boxscores['DREB'] == 0, 'POSS']
        boxscores['DREB/DREB_CHANCE'] = boxscores['DREB']/boxscores['DREB_CHANCES']

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='DREB/DREB_CHANCE',
            new_col_name='AVG_DREB/DREB_CHANCE', weight_col_name='DREB_CHANCES'
        )

        # average oreb/oreb chance that opp team allowed
        boxscores['NORMALIZED_POSITION'] = boxscores['POSITION'].apply(lambda x: x if '-' not in x else x.split('-')[0])

        team_position_game_boxscores = boxscores.groupby(['SEASON', 'DATE', 'NORMALIZED_POSITION', 'TEAM', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_POSITION_OREB': x['OREB'].sum(),
                'TEAM_POSITION_OREB_CHANCES': x['OREB_CHANCES'].sum(),
                'TEAM_POSITION_DREB': x['DREB'].sum(),
                'TEAM_POSITION_DREB_CHANCES': x['DREB_CHANCES'].sum()
            })
        ).reset_index()

        opp_team_position_game_boxscores = team_position_game_boxscores.drop(columns='OPP_TEAM')
        opp_team_position_game_boxscores = opp_team_position_game_boxscores.rename(columns={
            'TEAM': 'OPP_TEAM', 'TEAM_POSITION_OREB': 'OPP_TEAM_POSITION_OREB',
            'TEAM_POSITION_OREB_CHANCES': 'OPP_TEAM_POSITION_OREB_CHANCES', 'TEAM_POSITION_DREB': 'OPP_TEAM_POSITION_DREB',
            'TEAM_POSITION_DREB_CHANCES': 'OPP_TEAM_POSITION_DREB_CHANCES'
            })
        team_position_game_boxscores = team_position_game_boxscores.merge(
            opp_team_position_game_boxscores, on=['SEASON', 'DATE', 'NORMALIZED_POSITION', 'OPP_TEAM'], how='left'
            )

        team_position_game_boxscores['TEAM_POSITION_OREB/OREB_CHANCE'] = \
            team_position_game_boxscores['TEAM_POSITION_OREB']/team_position_game_boxscores['TEAM_POSITION_OREB_CHANCES']

        team_position_game_boxscores = feature_creation.expanding_weighted_mean(
            df=team_position_game_boxscores, group_col_names=['SEASON', 'NORMALIZED_POSITION', 'OPP_TEAM'],
            col_name='TEAM_POSITION_OREB/OREB_CHANCE', new_col_name='AVG_TEAM_POSITION_OREB/OREB_CHANCE_OPP_ALLOWED',
            weight_col_name='TEAM_POSITION_OREB_CHANCES'
        )

        # average dreb/dreb chance that opp team allowed
        team_position_game_boxscores['TEAM_POSITION_DREB/DREB_CHANCE'] = \
            team_position_game_boxscores['TEAM_POSITION_DREB']/team_position_game_boxscores['TEAM_POSITION_DREB_CHANCES']

        team_position_game_boxscores = feature_creation.expanding_weighted_mean(
            df=team_position_game_boxscores, group_col_names=['SEASON', 'NORMALIZED_POSITION', 'OPP_TEAM'],
            col_name='TEAM_POSITION_DREB/DREB_CHANCE', new_col_name='AVG_TEAM_POSITION_DREB/DREB_CHANCE_OPP_ALLOWED',
            weight_col_name='TEAM_POSITION_DREB_CHANCES'
        )

        boxscores = boxscores.merge(
            team_position_game_boxscores, on=['SEASON', 'DATE', 'NORMALIZED_POSITION', 'TEAM', 'OPP_TEAM'], how='left'
        )

        # average oreb/oreb chance allowed that player played against
        team_position_season_boxscores = team_position_game_boxscores.groupby(
            ['SEASON', 'NORMALIZED_POSITION', 'TEAM']
            ).apply(
            lambda x: pd.Series({
                'TEAM_POSITION_OREB(SEASON)': x['TEAM_POSITION_OREB'].mean(),
                'TEAM_POSITION_OREB_CHANCES(SEASON)': x['TEAM_POSITION_OREB_CHANCES'].mean(),
                'TEAM_POSITION_DREB(SEASON)': x['TEAM_POSITION_DREB'].mean(),
                'TEAM_POSITION_DREB_CHANCES(SEASON)': x['TEAM_POSITION_DREB_CHANCES'].mean(),
                'TEAM_POSITION_OREB_ALLOWED(SEASON)': x['OPP_TEAM_POSITION_OREB'].mean(),
                'TEAM_POSITION_OREB_CHANCES_ALLOWED(SEASON)': x['OPP_TEAM_POSITION_OREB_CHANCES'].mean(),
                'TEAM_POSITION_DREB_ALLOWED(SEASON)': x['OPP_TEAM_POSITION_DREB'].mean(),
                'TEAM_POSITION_DREB_CHANCES_ALLOWED(SEASON)': x['OPP_TEAM_POSITION_DREB_CHANCES'].mean(),
            })
        ).reset_index()

        opp_team_position_season_boxscores = team_position_season_boxscores.rename(columns={
            'TEAM': 'OPP_TEAM',
            'TEAM_POSITION_OREB(SEASON)': 'OPP_TEAM_POSITION_OREB(SEASON)',
            'TEAM_POSITION_OREB_CHANCES(SEASON)': 'OPP_TEAM_POSITION_OREB_CHANCES(SEASON)',
            'TEAM_POSITION_DREB(SEASON)': 'OPP_TEAM_POSITION_DREB(SEASON)',
            'TEAM_POSITION_DREB_CHANCES(SEASON)': 'OPP_TEAM_POSITION_DREB_CHANCES(SEASON)',
            'TEAM_POSITION_OREB_ALLOWED(SEASON)': 'OPP_TEAM_POSITION_OREB_ALLOWED(SEASON)',
            'TEAM_POSITION_OREB_CHANCES_ALLOWED(SEASON)': 'OPP_TEAM_POSITION_OREB_CHANCES_ALLOWED(SEASON)',
            'TEAM_POSITION_DREB_ALLOWED(SEASON)': 'OPP_TEAM_POSITION_DREB_ALLOWED(SEASON)',
            'TEAM_POSITION_DREB_CHANCES_ALLOWED(SEASON)': 'OPP_TEAM_POSITION_DREB_CHANCES_ALLOWED(SEASON)',
            })

        boxscores = boxscores.merge(
            team_position_season_boxscores, on=['SEASON', 'NORMALIZED_POSITION', 'TEAM'], how='left'
        )
        boxscores = boxscores.merge(
            opp_team_position_season_boxscores, on=['SEASON', 'NORMALIZED_POSITION', 'OPP_TEAM'], how='left'
        )

        boxscores['OPP_TEAM_POSITION_OREB/OREB_CHANCE_ALLOWED(SEASON)'] = \
            boxscores['OPP_TEAM_POSITION_OREB_ALLOWED(SEASON)'] / boxscores['OPP_TEAM_POSITION_OREB_CHANCES_ALLOWED(SEASON)']

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'NORMALIZED_POSITION', 'PLAYERID'],
            col_name='OPP_TEAM_POSITION_OREB/OREB_CHANCE_ALLOWED(SEASON)',
            new_col_name='AVG_TEAM_POSITION_OREB/OREB_CHANCE(SEASON)_ALLOWED_PLAYER_P.A',
            weight_col_name='OREB_CHANCES'
        )

        # average dreb/dreb chance allowed that player played against
        boxscores['OPP_TEAM_POSITION_DREB/DREB_CHANCE_ALLOWED(SEASON)'] = \
            boxscores['OPP_TEAM_POSITION_DREB_ALLOWED(SEASON)'] / boxscores['OPP_TEAM_POSITION_DREB_CHANCES_ALLOWED(SEASON)']

        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'NORMALIZED_POSITION', 'PLAYERID'],
            col_name='OPP_TEAM_POSITION_DREB/DREB_CHANCE_ALLOWED(SEASON)',
            new_col_name='AVG_TEAM_POSITION_DREB/DREB_CHANCE(SEASON)_ALLOWED_PLAYER_P.A',
            weight_col_name='DREB_CHANCES'
        )

        # oreb/oreb chance defense
        boxscores['OREB/CH_DEF'] = \
            boxscores['AVG_TEAM_POSITION_OREB/OREB_CHANCE_OPP_ALLOWED'] / \
                boxscores['AVG_TEAM_POSITION_OREB/OREB_CHANCE(SEASON)_ALLOWED_PLAYER_P.A']

        # dreb/dreb chance defense
        boxscores['DREB/CH_DEF'] = \
            boxscores['AVG_TEAM_POSITION_DREB/DREB_CHANCE_OPP_ALLOWED'] / \
                boxscores['AVG_TEAM_POSITION_DREB/DREB_CHANCE(SEASON)_ALLOWED_PLAYER_P.A']

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
            'SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION', 'START',
            'OREB(CH)/POSS', 'OREB(CH)/POSS_DEF',
            'OREB/CH', 'OREB/CH_DEF', 'DREB/CH', 'DREB/CH_DEF'
            ]
        return predicted_data[cols]