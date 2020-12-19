import pandas as pd
import numpy as np
import time
from nba_api.stats.endpoints import SynergyPlayTypes
from pyNBA.Models.constants import PLAY_TYPES
from pyNBA.Models.features import FeatureCreation
from pyNBA.Data.helpers import Helpers

class PointsPerPossession(object):
    def generate_regressors(self, boxscores, start_date, end_date):
        feature_creation = FeatureCreation()
        helpers = Helpers()

        relevant_seasons = boxscores.loc[
                    (boxscores['DATE'] >= start_date) & 
                    (boxscores['DATE'] <= end_date)
                    ]['SEASON'].unique()
        boxscores = boxscores.loc[boxscores['SEASON'].isin(relevant_seasons)]

        boxscores['ATTEMPTS'] = boxscores['TOTAL_ATTEMPTS']
        boxscores['ATTEMPTS/POSSESSION'] = boxscores['ATTEMPTS']/boxscores['POSS']

        # average attempts per possession
        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='ATTEMPTS/POSSESSION',
            new_col_name='AVG_ATTEMPTS/POSSESSION', weight_col_name='POSS'
        )

        boxscores['POINTS/ATTEMPT'] = boxscores['PTS']/boxscores['ATTEMPTS']

        # average points per attempt
        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='POINTS/ATTEMPT',
            new_col_name='AVG_POINTS/ATTEMPT', weight_col_name='ATTEMPTS'
        )

        # adjustment for defense (points per attempt)
        for play_type in PLAY_TYPES:
            player_play_type_data = pd.DataFrame()
            team_play_type_data = pd.DataFrame()
            for season in relevant_seasons:
                player_data = helpers.get_play_type_breakdown(play_type, season, 'player')

                player_data['SEASON'] = season
                player_data['PLAYER_ID'] = player_data['PLAYER_ID'].apply(lambda x: str(x))
                player_data = player_data.rename(columns={
                    'TEAM_ABBREVIATION': 'TEAM', 'PLAYER_ID': 'PLAYERID',
                    'PPP': '{}_PPP'.format(play_type), 'POSS_PCT': '{}_POSS_PCT'.format(play_type)
                    })
                player_data = player_data[
                    ['SEASON', 'PLAYERID', 'TEAM', '{}_PPP'.format(play_type), '{}_POSS_PCT'.format(play_type)]
                    ]

                player_play_type_data = player_play_type_data.append(player_data)
                
                team_data = helpers.get_play_type_breakdown(play_type, season, 'team')

                team_data['SEASON'] = season
                team_data = team_data.rename(columns={
                    'TEAM_ABBREVIATION': 'OPP_TEAM', 'PPP': '{}_PPP_ALLOWED'.format(play_type),
                    'POSS_PCT': '{}_POSS_PCT_ALLOWED'.format(play_type)
                    })
                team_data = team_data[
                    ['SEASON', 'OPP_TEAM', '{}_PPP_ALLOWED'.format(play_type), '{}_POSS_PCT_ALLOWED'.format(play_type)]
                    ]
                
                team_play_type_data = team_play_type_data.append(team_data)
                
            boxscores = boxscores.merge(player_play_type_data, on=['SEASON', 'PLAYERID', 'TEAM'], how='left')
            boxscores = boxscores.merge(team_play_type_data, on=['SEASON', 'OPP_TEAM'], how='left')

        poss_pct_cols = ['{}_POSS_PCT'.format(i) for i in PLAY_TYPES]
        poss_pct_allowed_cols = ['{}_POSS_PCT_ALLOWED'.format(i) for i in PLAY_TYPES]
        boxscores[poss_pct_cols] = boxscores[poss_pct_cols].replace([0], 0.001)
        boxscores[poss_pct_allowed_cols] = boxscores[poss_pct_allowed_cols].replace([0], 0.001)
        boxscores['TOTAL_POSS_PCT'] = boxscores[poss_pct_cols].sum(axis=1)
        boxscores['TOTAL_POSS_PCT_ALLOWED'] = boxscores[poss_pct_allowed_cols].sum(axis=1)
        boxscores[poss_pct_cols] = boxscores[poss_pct_cols].div(boxscores['TOTAL_POSS_PCT'], axis=0)
        boxscores[poss_pct_allowed_cols] = boxscores[poss_pct_allowed_cols].div(boxscores['TOTAL_POSS_PCT_ALLOWED'], axis=0)

        boxscores['NET_POINTS/ATTEMPT'] = 0
        boxscores['TOTAL_POSS_PCT'] = 0
        boxscores['IMPLIED_NET_POINTS/ATTEMPT'] = 0
        boxscores['TOTAL_IMPLIED_POSS_PCT'] = 0
        for play_type in PLAY_TYPES:
            boxscores = feature_creation.expanding_weighted_mean(
                df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'],
                col_name='{}_PPP_ALLOWED'.format(play_type), weight_col_name='ATTEMPTS',
                new_col_name='AVG_{}_PPP_ALLOWED_PLAYED_AGAINST'.format(play_type)
            )
            boxscores = feature_creation.expanding_weighted_mean(
                df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'],
                col_name='{}_POSS_PCT_ALLOWED'.format(play_type), weight_col_name='POSS',
                new_col_name='AVG_{}_POSS_PCT_ALLOWED_PLAYED_AGAINST'.format(play_type)
            )

            boxscores['PPP_ADJ'] = boxscores.apply(
                lambda row: row['{}_PPP_ALLOWED'.format(play_type)]/row['AVG_{}_PPP_ALLOWED_PLAYED_AGAINST'.format(play_type)] \
                    if (not np.isnan(row['{}_PPP_ALLOWED'.format(play_type)]) and \
                        not np.isnan(row['AVG_{}_PPP_ALLOWED_PLAYED_AGAINST'.format(play_type)])) \
                        else 1,
                axis = 1
                )
            boxscores['POSS_PCT_ADJ'] = boxscores.apply(
                lambda row: row['{}_POSS_PCT_ALLOWED'.format(play_type)]/row['AVG_{}_POSS_PCT_ALLOWED_PLAYED_AGAINST'.format(play_type)] \
                    if (not np.isnan(row['{}_POSS_PCT_ALLOWED'.format(play_type)]) and \
                        not np.isnan(row['AVG_{}_POSS_PCT_ALLOWED_PLAYED_AGAINST'.format(play_type)])) \
                        else 1,
                axis = 1
                )

            boxscores['NET_POINTS/ATTEMPT'] += \
                boxscores['{}_PPP'.format(play_type)].fillna(0) * boxscores['{}_POSS_PCT'.format(play_type)].fillna(0)
            boxscores['TOTAL_POSS_PCT'] += boxscores['{}_POSS_PCT'.format(play_type)].fillna(0)

            boxscores['IMPLIED_NET_POINTS/ATTEMPT'] += (boxscores['{}_PPP'.format(play_type)].fillna(0) * boxscores['PPP_ADJ']) * \
                (boxscores['{}_POSS_PCT'.format(play_type)].fillna(0) * boxscores['POSS_PCT_ADJ'])
            boxscores['TOTAL_IMPLIED_POSS_PCT'] += boxscores['{}_POSS_PCT'.format(play_type)].fillna(0) * boxscores['POSS_PCT_ADJ']

        boxscores['POINTS/ATTEMPT_DEF_ADJ'] = boxscores.apply(
            lambda row: (row['IMPLIED_NET_POINTS/ATTEMPT']/row['TOTAL_IMPLIED_POSS_PCT']) - \
                (row['NET_POINTS/ATTEMPT']/row['TOTAL_POSS_PCT']) \
                    if (row['TOTAL_POSS_PCT'] > 0 and row['TOTAL_IMPLIED_POSS_PCT'] > 0) else 0,
            axis = 1
        )
    
        boxscores = boxscores.loc[
            (boxscores['DATE'] >= start_date) & 
            (boxscores['DATE'] <= end_date)
            ]

        return boxscores

    def predict(self, boxscores, predict_start_date, predict_end_date):
        predicted_data = self.generate_regressors(boxscores, predict_start_date, predict_end_date)

        predicted_data = predicted_data.rename(columns={
            'AVG_ATTEMPTS/POSSESSION': 'ATT/POSS', 'AVG_POINTS/ATTEMPT': 'PTS/ATT',
            'POINTS/ATTEMPT_DEF_ADJ': 'PTS/ATT_DEF'
            })
        cols = [
            'SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION', 'START',
            'ATT/POSS', 'PTS/ATT', 'PTS/ATT_DEF'
            ]
        return predicted_data[cols]