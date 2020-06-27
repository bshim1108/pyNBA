import numpy as np
import pandas as pd

from pyNBA.Models.features import FeatureCreation
from pyNBA.Models.base import CatBoostRegressionModel, WeightFunctions

from pyNBA.Models.constants import BPS_MODEL_PARAMS


class BPSModel(object):
    def __init__(self, train_data, test_data):
        self.feature_creation = FeatureCreation()

        self.train_data = train_data
        self.test_data = test_data
        self.model = CatBoostRegressionModel(BPS_MODEL_PARAMS)

        self.regressors = []
        self.regressand = 'BPS'

        self.created_features = False
        self.generated_weights = False
        self.trained_model = False

    def create_features(self, odds_data, sp_threshold=60):
        data = pd.concat([self.train_data, self.test_data])

        data[self.regressand] = data['BLK']/data['SECONDSPLAYED']

        clean_regressand = 'CLEAN_{}'.format(self.regressand)
        data[clean_regressand] = data[self.regressand]
        data.loc[data['SECONDSPLAYED'] <= sp_threshold, clean_regressand] = np.nan

        train_index = self.train_data.set_index(['GAMEID', 'PLAYERID']).index
        test_index = self.test_data.set_index(['GAMEID', 'PLAYERID']).index

        # season averages
        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name=self.regressand,
            weight_col_name='SECONDSPLAYED', new_col_name='AVG_Y'
        )
        self.regressors.append('AVG_Y')

        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'OPP_TEAM', 'PLAYERID'], col_name=self.regressand,
            weight_col_name='SECONDSPLAYED', new_col_name='AVG_Y_OPP_TEAM'
        )
        self.regressors.append('AVG_Y_OPP_TEAM')

        # 1 game lags
        data = self.feature_creation.lag(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name=clean_regressand, new_col_name='L1_Y',
            n_shift=1
        )
        self.regressors.append('L1_Y')

        # exponentially weighted means
        data = self.feature_creation.expanding_ewm(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name=self.regressand, new_col_name='EWM_Y',
            alpha=0.90
        )
        self.regressors.append('EWM_Y')

        # moving averages
        data = self.feature_creation.rolling_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name=self.regressand, new_col_name='MA5_Y',
            weight_col_name='SECONDSPLAYED', n_rolling=5, min_periods=3
        )
        data = self.feature_creation.rolling_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name=self.regressand, new_col_name='MA14_Y',
            weight_col_name='SECONDSPLAYED', n_rolling=14, min_periods=7
        )
        self.regressors.append('MA5_Y')
        self.regressors.append('MA14_Y')

        # start
        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID', 'START'], col_name=self.regressand,
            weight_col_name='SECONDSPLAYED', new_col_name='AVG_Y_R'
        )
        self.regressors.append('AVG_Y_R')

        # defense
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='BLK', new_col_name='AVG_BLK'
        )
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SECONDSPLAYED', new_col_name='AVG_SP'
        )

        temp = data.dropna(subset=['BLK', 'SECONDSPLAYED', 'AVG_BLK', 'AVG_SP'])
        grouped_defensive_boxscores = temp.groupby(['SEASON', 'DATE', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_Y_ALLOWED': x['BLK'].sum()/x['SECONDSPLAYED'].sum(),
                'TEAM_Y_AVG': x['AVG_BLK'].sum()/x['AVG_SP'].sum()
            })
        ).reset_index()
        grouped_defensive_boxscores['TEAM_Y_DIFF_ALLOWED'] = grouped_defensive_boxscores['TEAM_Y_ALLOWED'] - \
            grouped_defensive_boxscores['TEAM_Y_AVG']
        grouped_defensive_boxscores = self.feature_creation.expanding_mean(
            df=grouped_defensive_boxscores, group_col_names=['SEASON', 'OPP_TEAM'], col_name='TEAM_Y_DIFF_ALLOWED',
            new_col_name='AVG_TEAM_Y_DIFF_ALLOWED', order_idx_name='DATE', min_periods=5
        )

        data = data.merge(grouped_defensive_boxscores, on=['SEASON', 'DATE', 'OPP_TEAM'], how='left')
        self.regressors.append('AVG_TEAM_Y_DIFF_ALLOWED')

        data['NORM_POS'] = data['POSITION'].apply(lambda x: x if '-' not in x else x.split('-')[0])
        temp = data.dropna(subset=['BLK', 'SECONDSPLAYED', 'AVG_BLK', 'AVG_SP'])
        grouped_defensive_boxscores = temp.groupby(['SEASON', 'DATE', 'NORM_POS', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_Y_ALLOWED_P': x['BLK'].sum()/x['SECONDSPLAYED'].sum(),
                'TEAM_Y_AVG_P': x['AVG_BLK'].sum()/x['AVG_SP'].sum()
            })
        ).reset_index()
        grouped_defensive_boxscores['TEAM_Y_DIFF_ALLOWED_P'] = grouped_defensive_boxscores['TEAM_Y_ALLOWED_P'] - \
            grouped_defensive_boxscores['TEAM_Y_AVG_P']
        grouped_defensive_boxscores = self.feature_creation.expanding_mean(
            df=grouped_defensive_boxscores, group_col_names=['SEASON', 'OPP_TEAM', 'NORM_POS'],
            col_name='TEAM_Y_DIFF_ALLOWED_P', new_col_name='AVG_TEAM_Y_DIFF_ALLOWED_P', order_idx_name='DATE',
            min_periods=5
        )
        data = data.merge(grouped_defensive_boxscores, on=['SEASON', 'DATE', 'OPP_TEAM', 'NORM_POS'], how='left')
        self.regressors.append('AVG_TEAM_Y_DIFF_ALLOWED_P')

        # total
        full_game_odds = odds_data.loc[odds_data['PERIOD'] == 'Full Game']
        full_game_odds['TOTAL'] = full_game_odds['TOTAL'].replace(['PK', '-'], np.nan)
        data = data.merge(full_game_odds, on=['DATE', 'TEAM'], how='left')
        self.regressors.append('TOTAL')

        # misc
        data['GP'] = 1
        data = self.feature_creation.expanding_sum(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='GP', new_col_name='COUNT_GP'
            )
        self.regressors.append('COUNT_GP')
        self.regressors.append('AVG_SP')

        data = self.generate_weights(data)
        data = self.preprocess(data)
        data = data.set_index(['GAMEID', 'PLAYERID'])

        train_index = list(set(data.index.values).intersection(set(train_index.values)))
        self.train_data = data.loc[train_index].reset_index()
        test_index = list(set(data.index.values).intersection(set(test_index.values)))
        self.test_data = data.loc[test_index].reset_index()

        self.created_features = True

    def preprocess(self, data):
        data['AVG_Y_OPP_TEAM'] = data['AVG_Y_OPP_TEAM'].fillna(data['AVG_Y'])

        data['L1_Y'] = data['L1_Y'].fillna(data['AVG_Y'])
        data['EWM_Y'] = data['EWM_Y'].fillna(data['AVG_Y'])

        data['MA5_Y'] = data['MA5_Y'].fillna(data['AVG_Y'])
        data['MA14_Y'] = data['MA14_Y'].fillna(data['MA5_Y'])

        data['AVG_Y_R'] = data['AVG_Y_R'].fillna(data['AVG_Y'])

        data['AVG_TEAM_Y_DIFF_ALLOWED'] = data['AVG_TEAM_Y_DIFF_ALLOWED'].fillna(0)
        data['AVG_TEAM_Y_DIFF_ALLOWED_P'] = data['AVG_TEAM_Y_DIFF_ALLOWED_P'].fillna(0)

        data['TOTAL'] = data['TOTAL'].fillna(200)

        data['COUNT_GP'] = data['COUNT_GP'].fillna(0)

        # we can predict Y for a player as long as AVG_Y is not nan
        data = data.dropna(subset=['AVG_Y'])

        return data

    def generate_weights(self, data):
        data = self.feature_creation.expanding_sum(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='SECONDSPLAYED', new_col_name='SUM_SP'
        )

        self.weight = 'WEIGHT'
        data[self.weight] = data['SECONDSPLAYED'].apply(WeightFunctions.game_seconds_played_weight) * \
            data['SUM_SP'].apply(WeightFunctions.season_seconds_played_weight)

        return data

    def train_model(self):
        if not self.created_features:
            raise Exception('Must create features before training model')

        # drop games in which players played a minute or less
        self.train_data = self.train_data.loc[self.train_data['SECONDSPLAYED'] > 60]

        X = self.train_data[self.regressors]
        y = self.train_data[self.regressand]
        w = self.train_data[self.weight]
        self.model.fit(X, y, sample_weight=w, test_size=0.25, early_stopping_rounds=25)

        self.trained_model = True

    def predict(self):
        if not self.trained_model:
            raise Exception('Must train model before generating predictions')

        self.test_data['{}_HAT'.format(self.regressand)] = self.model.predict(self.test_data[self.regressors])

        return self.test_data[['GAMEID', 'PLAYERID', '{}_HAT'.format(self.regressand)]]
