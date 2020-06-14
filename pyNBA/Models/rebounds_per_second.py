import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from pyNBA.Models.features import FeatureCreation
from pyNBA.Models.base import CatBoostRegressionModel

from pyNBA.Models.constants import RPS_MODEL_PARAMS

class RPSModel(object):
    def __init__(self, train_data, test_data):
        self.feature_creation = FeatureCreation()

        self.train_data = train_data
        self.test_data = test_data
        self.model = CatBoostRegressionModel(RPS_MODEL_PARAMS)

        self.regressors = []
        self.regressand = 'RPS'

        self.created_features = False
        self.generated_weights = False
        self.trained_model = False

    def create_features(self, odds_data, sp_threshold=1200):
        data = pd.concat([self.train_data, self.test_data])

        data['REB'] = data['DREB'] + data['OREB']
        data[self.regressand] = data['REB']/data['SECONDSPLAYED']
        data['ORPS'] = data['OREB']/data['SECONDSPLAYED']
        data['DRPS'] = data['DREB']/data['SECONDSPLAYED']

        data['CLEAN_DRPS'] = data['DRPS']
        data.loc[data['SECONDSPLAYED'] <= sp_threshold, 'CLEAN_DRPS'] = np.nan
        data['CLEAN_ORPS'] = data['ORPS']
        data.loc[data['SECONDSPLAYED'] <= sp_threshold, 'CLEAN_ORPS'] = np.nan

        train_index = self.train_data.set_index(['GAMEID', 'PLAYERID']).index
        test_index = self.test_data.set_index(['GAMEID', 'PLAYERID']).index

        # season averages
        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='DRPS', weight_col_name='SECONDSPLAYED',
            new_col_name='AVG_DRPS'
        )
        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='ORPS', weight_col_name='SECONDSPLAYED',
            new_col_name='AVG_ORPS'
        )
        self.regressors.append('AVG_DRPS')
        self.regressors.append('AVG_ORPS')

        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'OPP_TEAM', 'PLAYERID'], col_name=self.regressand, weight_col_name='SECONDSPLAYED',
            new_col_name='AVG_Y_OPP_TEAM'
        )
        self.regressors.append('AVG_Y_OPP_TEAM')

        # 1 game lags
        data = self.feature_creation.lag(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='CLEAN_DRPS', new_col_name='L1_DRPS', n_shift=1
        )
        self.regressors.append('L1_DRPS')

        # exponentially weighted means
        data = self.feature_creation.expanding_ewm(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='DRPS', new_col_name='EWM_DRPS', alpha=0.90
        )
        data = self.feature_creation.expanding_ewm(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='ORPS', new_col_name='EWM_ORPS', alpha=0.90
        )
        self.regressors.append('EWM_DRPS')
        self.regressors.append('EWM_ORPS')

        # moving averages
        data = self.feature_creation.rolling_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='DRPS', new_col_name='MA2_DRPS',
            weight_col_name='SECONDSPLAYED', n_rolling=2, min_periods=1
        )
        data = self.feature_creation.rolling_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='DRPS', new_col_name='MA15_DRPS',
            weight_col_name='SECONDSPLAYED', n_rolling=15, min_periods=8
        )
        data = self.feature_creation.rolling_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='ORPS', new_col_name='MA6_ORPS',
            weight_col_name='SECONDSPLAYED', n_rolling=6, min_periods=3
        )
        data = self.feature_creation.rolling_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='ORPS', new_col_name='MA18_ORPS',
            weight_col_name='SECONDSPLAYED', n_rolling=18, min_periods=9
        )
        self.regressors.append('MA2_DRPS')
        self.regressors.append('MA15_DRPS')
        self.regressors.append('MA6_ORPS')
        self.regressors.append('MA18_ORPS')

        # start
        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID', 'START'], col_name=self.regressand, weight_col_name='SECONDSPLAYED',
            new_col_name='AVG_Y_R'
        )
        self.regressors.append('AVG_Y_R')

        # position
        data['NORM_POS'] = data['POSITION'].apply(lambda x: x if '-' not in x else x.split('-')[0])
        data['GUARD'] = 0
        data.loc[data['NORM_POS'] == 'Guard', 'GUARD'] = 1
        self.regressors.append('GUARD')

        # defense
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='DREB', new_col_name='AVG_DREB'
        )
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='OREB', new_col_name='AVG_OREB'
        )
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SECONDSPLAYED', new_col_name='AVG_SP'
        )

        temp = data.dropna(subset=['DREB', 'SECONDSPLAYED', 'AVG_DREB', 'AVG_SP'])
        grouped_defensive_boxscores = temp.groupby(['SEASON', 'DATE', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_DRPS_ALLOWED': x['DREB'].sum()/x['SECONDSPLAYED'].sum(),
                'TEAM_DRPS_AVG': x['AVG_DREB'].sum()/x['AVG_SP'].sum()
            })
        ).reset_index()
        grouped_defensive_boxscores['TEAM_DRPS_DIFF_ALLOWED'] = grouped_defensive_boxscores['TEAM_DRPS_ALLOWED'] - grouped_defensive_boxscores['TEAM_DRPS_AVG']
        grouped_defensive_boxscores = self.feature_creation.expanding_mean(
            df=grouped_defensive_boxscores, group_col_names=['SEASON', 'OPP_TEAM'], col_name='TEAM_DRPS_DIFF_ALLOWED', new_col_name='AVG_TEAM_DRPS_DIFF_ALLOWED',
            order_idx_name='DATE', min_periods=5
        )
        data = data.merge(grouped_defensive_boxscores, on=['SEASON', 'DATE', 'OPP_TEAM'], how='left')
        self.regressors.append('AVG_TEAM_DRPS_DIFF_ALLOWED')

        temp = data.dropna(subset=['DREB', 'SECONDSPLAYED', 'AVG_DREB', 'AVG_SP'])
        grouped_defensive_boxscores = temp.groupby(['SEASON', 'DATE', 'START', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_DRPS_ALLOWED_R': x['DREB'].sum()/x['SECONDSPLAYED'].sum(),
                'TEAM_DRPS_AVG_R': x['AVG_DREB'].sum()/x['AVG_SP'].sum()
            })
        ).reset_index()
        grouped_defensive_boxscores['TEAM_DRPS_DIFF_ALLOWED_R'] = grouped_defensive_boxscores['TEAM_DRPS_ALLOWED_R'] - grouped_defensive_boxscores['TEAM_DRPS_AVG_R']
        grouped_defensive_boxscores = self.feature_creation.expanding_mean(
            df=grouped_defensive_boxscores, group_col_names=['SEASON', 'START', 'OPP_TEAM'], col_name='TEAM_DRPS_DIFF_ALLOWED_R',
            new_col_name='AVG_TEAM_DRPS_DIFF_ALLOWED_R', order_idx_name='DATE', min_periods=5
        )
        data = data.merge(grouped_defensive_boxscores, on=['SEASON', 'DATE', 'START', 'OPP_TEAM'], how='left')
        self.regressors.append('AVG_TEAM_DRPS_DIFF_ALLOWED_R')


        temp = data.dropna(subset=['DREB', 'OREB', 'SECONDSPLAYED', 'AVG_DREB', 'AVG_OREB', 'AVG_SP'])
        grouped_defensive_boxscores = temp.groupby(['SEASON', 'DATE', 'NORM_POS', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_DRPS_ALLOWED_P': x['DREB'].sum()/x['SECONDSPLAYED'].sum(),
                'TEAM_DRPS_AVG_P': x['AVG_DREB'].sum()/x['AVG_SP'].sum(),
                'TEAM_ORPS_ALLOWED_P': x['OREB'].sum()/x['SECONDSPLAYED'].sum(),
                'TEAM_ORPS_AVG_P': x['AVG_OREB'].sum()/x['AVG_SP'].sum()
            })
        ).reset_index()
        grouped_defensive_boxscores['TEAM_DRPS_DIFF_ALLOWED_P'] = grouped_defensive_boxscores['TEAM_DRPS_ALLOWED_P'] - grouped_defensive_boxscores['TEAM_DRPS_AVG_P']
        grouped_defensive_boxscores['TEAM_ORPS_DIFF_ALLOWED_P'] = grouped_defensive_boxscores['TEAM_ORPS_ALLOWED_P'] - grouped_defensive_boxscores['TEAM_ORPS_AVG_P']
        grouped_defensive_boxscores = self.feature_creation.expanding_mean(
            df=grouped_defensive_boxscores, group_col_names=['SEASON', 'NORM_POS', 'OPP_TEAM'], col_name='TEAM_DRPS_DIFF_ALLOWED_P',
            new_col_name='AVG_TEAM_DRPS_DIFF_ALLOWED_P', order_idx_name='DATE', min_periods=5
        )
        grouped_defensive_boxscores = self.feature_creation.expanding_mean(
            df=grouped_defensive_boxscores, group_col_names=['SEASON', 'NORM_POS', 'OPP_TEAM'], col_name='TEAM_ORPS_DIFF_ALLOWED_P',
            new_col_name='AVG_TEAM_ORPS_DIFF_ALLOWED_P', order_idx_name='DATE', min_periods=5
        )
        data = data.merge(grouped_defensive_boxscores, on=['SEASON', 'DATE', 'NORM_POS', 'OPP_TEAM'], how='left')
        self.regressors.append('AVG_TEAM_DRPS_DIFF_ALLOWED_P')
        self.regressors.append('AVG_TEAM_ORPS_DIFF_ALLOWED_P')

        # total
        full_game_odds = odds_data.loc[odds_data['PERIOD'] == 'Full Game']
        full_game_odds['TOTAL'] = full_game_odds['TOTAL'].replace(['PK', '-'], np.nan)
        data = data.merge(full_game_odds, on=['DATE', 'TEAM'], how='left')
        self.regressors.append('TOTAL')

        # injuries
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='REB', new_col_name='AVG_REB'
        )

        temp = data.dropna(subset=['DREB', 'AVG_DREB', 'SECONDSPLAYED', 'AVG_SP'])
        temp = temp.groupby(['SEASON', 'GAMEID', 'TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_ACTIVE_AVG_DRPS': x['AVG_DREB'].sum()/x['AVG_SP'].sum(),
                'TEAM_DRPS': x['DREB'].sum()/x['SECONDSPLAYED'].sum(),
                'TEAM_ACTIVE_AVG_RPS': x['AVG_REB'].sum()/x['AVG_SP'].sum(),
                'TEAM_RPS': x['REB'].sum()/x['SECONDSPLAYED'].sum()
            })
        )
        temp = self.feature_creation.expanding_mean(
            df=temp, group_col_names=['SEASON', 'TEAM'], col_name='TEAM_DRPS', new_col_name='AVG_TEAM_DRPS'
        )
        temp['TEAM_ACTIVE_AVG_DRPS_DIFF'] = temp['TEAM_ACTIVE_AVG_DRPS'] - temp['AVG_TEAM_DRPS']
        data = data.merge(temp, on=['GAMEID', 'TEAM'], how='left')
        self.regressors.append('TEAM_ACTIVE_AVG_DRPS_DIFF')

        # regressand by lineup
        data['START_LINEUP'] = np.nan
        data['STARS'] = np.nan
        data = data.set_index(['GAMEID', 'TEAM'])
        for (game_id, team), temp in data.groupby(['GAMEID', 'TEAM']):
            start_lineup = list(temp.loc[temp['START'] == 1, 'PLAYERID'].values)
            start_lineup.sort()
            start_lineup = '_'.join(start_lineup)
            data.loc[(game_id, team), 'START_LINEUP'] = start_lineup
            
            stars = list(temp.loc[temp['AVG_DREB'] >= 7, 'PLAYERID'].values)
            stars.sort()
            stars = '_'.join(stars)
            data.loc[(game_id, team), 'STARS'] = stars
        data = data.reset_index()

        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'START_LINEUP', 'PLAYERID'], col_name=self.regressand, weight_col_name='SECONDSPLAYED',
            new_col_name='AVG_Y_STARTERS'
        )

        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'STARS', 'PLAYERID'], col_name=self.regressand, weight_col_name='SECONDSPLAYED',
            new_col_name='AVG_Y_STARS'
        )
        self.regressors.append('AVG_Y_STARTERS')
        self.regressors.append('AVG_Y_STARS')

        # misc
        data['GP'] = 1
        data = self.feature_creation.expanding_sum(df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='GP', new_col_name='COUNT_GP')
        self.regressors.append('COUNT_GP')
        self.regressors.append('AVG_SP')

        # to fill
        data = self.feature_creation.expanding_weighted_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name=self.regressand, weight_col_name='SECONDSPLAYED', new_col_name='AVG_Y'
        )

        data = self.generate_weights(data)
        data = self.preprocess(data)
        data = data.set_index(['GAMEID', 'PLAYERID'])

        train_index = list(set(data.index.values).intersection(set(train_index.values)))
        self.train_data = data.loc[train_index].reset_index()
        test_index = list(set(data.index.values).intersection(set(test_index.values)))
        self.test_data = data.loc[test_index].reset_index()

        self.created_features = True

    def preprocess(self, data):
        data['AVG_Y_R'] = data['AVG_Y_R'].fillna(data['AVG_Y'])
        data['AVG_Y_OPP_TEAM'] = data['AVG_Y_OPP_TEAM'].fillna(data['AVG_Y'])

        data['L1_DRPS'] = data['L1_DRPS'].fillna(data['AVG_DRPS'])

        data['EWM_DRPS'] = data['EWM_DRPS'].fillna(data['AVG_DRPS'])
        data['EWM_ORPS'] = data['EWM_ORPS'].fillna(data['AVG_ORPS'])

        data['MA2_DRPS'] = data['MA2_DRPS'].fillna(data['AVG_DRPS'])
        data['MA15_DRPS'] = data['MA15_DRPS'].fillna(data['MA2_DRPS'])
        data['MA6_ORPS'] = data['MA6_ORPS'].fillna(data['AVG_ORPS'])
        data['MA18_ORPS'] = data['MA18_ORPS'].fillna(data['MA6_ORPS'])

        data['AVG_TEAM_DRPS_DIFF_ALLOWED'] = data['AVG_TEAM_DRPS_DIFF_ALLOWED'].fillna(0)
        data['AVG_TEAM_DRPS_DIFF_ALLOWED_R'] = data['AVG_TEAM_DRPS_DIFF_ALLOWED_R'].fillna(0)
        data['AVG_TEAM_DRPS_DIFF_ALLOWED_P'] = data['AVG_TEAM_DRPS_DIFF_ALLOWED_P'].fillna(0)
        data['AVG_TEAM_ORPS_DIFF_ALLOWED_P'] = data['AVG_TEAM_ORPS_DIFF_ALLOWED_P'].fillna(0)

        data['TOTAL'] = data['TOTAL'].fillna(200)

        data['TEAM_ACTIVE_AVG_DRPS_DIFF'] = data['TEAM_ACTIVE_AVG_DRPS_DIFF'].fillna(0)
        data['AVG_Y_STARS'] = data['AVG_Y_STARS'].fillna(data['AVG_Y'])
        data['AVG_Y_STARTERS'] = data['AVG_Y_STARTERS'].fillna(data['AVG_Y_STARS'])

        data['COUNT_GP'] = data['COUNT_GP'].fillna(0)

        # we can predict Y for a player as long as AVG_Y is not nan
        data = data.dropna(subset=['AVG_Y'])

        return data

    def generate_weights(self, data):
        sp_weight_func = lambda x: 1/(1 + np.exp((-0.80*x + 600)/180)) - 0.01
        tsp_weight_func = lambda x: 1/(1 + np.exp((-0.175*x + 840)/300)) - 0.04

        data = self.feature_creation.expanding_sum(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='SECONDSPLAYED', new_col_name='SUM_SP'
        )

        self.weight = 'WEIGHT'
        data[self.weight] = data['SECONDSPLAYED'].apply(sp_weight_func) * data['SUM_SP'].apply(tsp_weight_func)

        return data

    def train_model(self):
        if not self.created_features:
            raise Exception('Must create features before training model')

        #drop games in which players played a minute or less
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
