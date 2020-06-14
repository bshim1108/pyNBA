import numpy as np
import pandas as pd

from pyNBA.Models.features import FeatureCreation
from pyNBA.Models.base import CatBoostRegressionModel

from pyNBA.Models.constants import SECONDS_MODEL_PARAMS


class SecondsModel(object):
    def __init__(self, train_data, test_data):
        self.feature_creation = FeatureCreation()

        self.train_data = train_data
        self.test_data = test_data
        self.model = CatBoostRegressionModel(SECONDS_MODEL_PARAMS)

        self.regressors = []
        self.regressand = 'SECONDSPLAYED'

        self.created_features = False
        self.trained_model = False

    def create_features(self, quarterly_boxscore_data, odds_data):
        data = pd.concat([self.train_data, self.test_data])
        train_index = self.train_data.set_index(['GAMEID', 'PLAYERID']).index
        test_index = self.test_data.set_index(['GAMEID', 'PLAYERID']).index

        quarterly_boxscore_data = quarterly_boxscore_data.pivot_table(
            'SECONDSPLAYED', ['GAMEID', 'PLAYERID'], 'QUARTER'
            )
        quarterly_boxscore_data.columns = ['SP(Q{})'.format(str(col)) for col in quarterly_boxscore_data.columns]
        data = data.merge(quarterly_boxscore_data, on=['GAMEID', 'PLAYERID'], how='left')
        data[quarterly_boxscore_data.columns] = data[quarterly_boxscore_data.columns].fillna(0)
        data['SP(Q1-Q3)'] = data['SP(Q1)'] + data['SP(Q2)'] + data['SP(Q3)']
        data['SP(REG)'] = data['SP(Q1-Q3)'] + data['SP(Q4)']

        # season averages
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SECONDSPLAYED', new_col_name='AVG_Y'
            )
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(REG)', new_col_name='AVG_SP(REG)'
            )
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(Q1-Q3)', new_col_name='AVG_SP(Q1-Q3)'
            )
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(Q4)', new_col_name='AVG_SP(Q4)'
            )
        self.regressors.append('AVG_Y')
        self.regressors.append('AVG_SP(REG)')
        self.regressors.append('AVG_SP(Q1-Q3)')
        self.regressors.append('AVG_SP(Q4)')

        # 1 game lags
        data = self.feature_creation.lag(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(REG)', new_col_name='L1_SP(REG)',
            n_shift=1)

        data = self.feature_creation.lag(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(Q1-Q3)', new_col_name='L1_SP(Q1-Q3)',
            n_shift=1
            )
        self.regressors.append('L1_SP(REG)')
        self.regressors.append('L1_SP(Q1-Q3)')

        # exponentially weighted means
        data = self.feature_creation.expanding_ewm(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(REG)', new_col_name='EWM_SP(REG)',
            alpha=0.90
            )
        data = self.feature_creation.expanding_ewm(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(Q1-Q3)', new_col_name='EWM_SP(Q1-Q3)',
            alpha=0.90
            )
        self.regressors.append('EWM_SP(REG)')
        self.regressors.append('EWM_SP(Q1-Q3)')

        # moving averages
        data = self.feature_creation.rolling_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(REG)', new_col_name='MA2_SP(REG)',
            n_rolling=2, min_periods=1
        )
        data = self.feature_creation.rolling_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(Q1-Q3)', new_col_name='MA2_SP(Q1-Q3)',
            n_rolling=2, min_periods=1
        )
        data = self.feature_creation.rolling_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(Q4)', new_col_name='MA3_SP(Q4)',
            n_rolling=3, min_periods=2
        )
        data = self.feature_creation.rolling_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SP(Q4)', new_col_name='MA7_SP(Q4)',
            n_rolling=7, min_periods=4
        )
        self.regressors.append('MA2_SP(REG)')
        self.regressors.append('MA2_SP(Q1-Q3)')
        self.regressors.append('MA7_SP(Q4)')

        # start
        self.regressors.append('START')

        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID', 'START'], col_name='SP(REG)',
            new_col_name='AVG_SP(REG)_R'
            )
        self.regressors.append('AVG_SP(REG)_R')

        # depth
        temp = data.groupby(['GAMEID', 'TEAM']).apply(
            lambda x: pd.Series({
                'DEPTH': x['PLAYERID'].count()
            })
        )
        data = data.merge(temp, on=['GAMEID', 'TEAM'], how='left')

        self.regressors.append('DEPTH')

        # removed time
        temp = data.dropna(subset=['AVG_SP(REG)'])
        temp = temp.groupby(['GAMEID', 'TEAM']).apply(
            lambda x: pd.Series({
                'SUM_AVG_SP(REG)': x['AVG_SP(REG)'].sum()
            })
        )
        data = data.merge(temp, on=['GAMEID', 'TEAM'], how='left')
        self.regressors.append('SUM_AVG_SP(REG)')

        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SUM_AVG_SP(REG)',
            new_col_name='AVG_SUM_AVG_SP(REG)'
        )
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID', 'START'], col_name='SUM_AVG_SP(REG)',
            new_col_name='AVG_SUM_AVG_SP(REG)_R'
        )
        self.regressors.append('AVG_SUM_AVG_SP(REG)')
        self.regressors.append('AVG_SUM_AVG_SP(REG)_R')

        data['NORM_POS'] = data['POSITION'].apply(lambda x: x if '-' not in x else x.split('-')[0])
        temp = data.dropna(subset=['AVG_SP(REG)'])
        temp = temp.groupby(['GAMEID', 'TEAM', 'NORM_POS']).apply(
            lambda x: pd.Series({
                'SUM_AVG_SP(REG)_P': x['AVG_SP(REG)'].sum()
            })
        )
        data = data.merge(temp, on=['GAMEID', 'TEAM', 'NORM_POS'], how='left')
        self.regressors.append('SUM_AVG_SP(REG)_P')

        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='SUM_AVG_SP(REG)_P',
            new_col_name='AVG_SUM_AVG_SP(REG)_P'
        )
        self.regressors.append('AVG_SUM_AVG_SP(REG)_P')

        # regressand by lineup
        data['START_LINEUP'] = np.nan
        data['STARS'] = np.nan
        data = data.set_index(['GAMEID', 'TEAM'])
        for (game_id, team), temp in data.groupby(['GAMEID', 'TEAM']):
            start_lineup = list(temp.loc[temp['START'] == 1, 'PLAYERID'].values)
            start_lineup.sort()
            start_lineup = '_'.join(start_lineup)
            data.loc[(game_id, team), 'START_LINEUP'] = start_lineup

            stars = list(temp.loc[temp['AVG_SP(REG)'] > 2040, 'PLAYERID'].values)
            stars.sort()
            stars = '_'.join(stars)
            data.loc[(game_id, team), 'STARS'] = stars
        data = data.reset_index()

        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'START_LINEUP', 'PLAYERID'], col_name='AVG_SP(REG)',
            new_col_name='AVG_SP(REG)_STARTERS'
        )
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'STARS', 'PLAYERID'], col_name='AVG_SP(REG)',
            new_col_name='AVG_SP(REG)_STARS'
        )
        self.regressors.append('AVG_SP(REG)_STARTERS')
        self.regressors.append('AVG_SP(REG)_STARS')

        # spread
        full_game_odds = odds_data.loc[odds_data['PERIOD'] == 'Full Game']
        full_game_odds['POINTSPREAD'] = full_game_odds['POINTSPREAD'].replace(['PK', '-'], 0)
        data = data.merge(full_game_odds, on=['DATE', 'TEAM'], how='left')

        data['ABS_POINTSPREAD'] = data['POINTSPREAD'].abs()
        self.regressors.append('ABS_POINTSPREAD')

        temp = data.groupby(['GAMEID', 'TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_PTS': x['PTS'].sum()
            })
        )
        data = data.merge(temp, on=['GAMEID', 'TEAM'], how='left')

        temp = data.groupby(['GAMEID', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'OPP_TEAM_PTS': x['PTS'].sum()
            })
        )
        data = data.merge(temp, left_on=['GAMEID', 'TEAM'], right_on=['GAMEID', 'OPP_TEAM'], how='left')

        data['ABS_DIFF_PTS'] = (data['TEAM_PTS'] - data['OPP_TEAM_PTS']).abs()
        data = self.feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='ABS_DIFF_PTS',
            new_col_name='AVG_ABS_DIFF_PTS'
            )
        self.regressors.append('AVG_ABS_DIFF_PTS')

        # misc
        data['GP'] = 1
        data = self.feature_creation.expanding_sum(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='GP', new_col_name='COUNT_GP'
            )
        self.regressors.append('COUNT_GP')

        data = self.preprocess(data)
        data = data.set_index(['GAMEID', 'PLAYERID'])

        train_index = list(set(data.index.values).intersection(set(train_index.values)))
        self.train_data = data.loc[train_index].reset_index()
        test_index = list(set(data.index.values).intersection(set(test_index.values)))
        self.test_data = data.loc[test_index].reset_index()

        self.created_features = True

    def preprocess(self, data):
        data['L1_SP(REG)'] = data['L1_SP(REG)'].fillna(data['AVG_SP(REG)'])
        data['L1_SP(Q1-Q3)'] = data['L1_SP(Q1-Q3)'].fillna(data['AVG_SP(Q1-Q3)'])

        data['EWM_SP(REG)'] = data['EWM_SP(REG)'].fillna(data['AVG_SP(REG)'])
        data['EWM_SP(Q1-Q3)'] = data['EWM_SP(Q1-Q3)'].fillna(data['AVG_SP(Q1-Q3)'])

        data['MA2_SP(REG)'] = data['MA2_SP(REG)'].fillna(data['AVG_SP(REG)'])
        data['MA2_SP(Q1-Q3)'] = data['MA2_SP(Q1-Q3)'].fillna(data['AVG_SP(Q1-Q3)'])
        data['MA7_SP(Q4)'] = data['MA7_SP(Q4)'].fillna(data['MA3_SP(Q4)'])

        data['AVG_SP(REG)_R'] = data['AVG_SP(REG)_R'].fillna(data['AVG_SP(REG)'])

        data['AVG_SUM_AVG_SP(REG)'] = data['AVG_SUM_AVG_SP(REG)'].fillna(data['SUM_AVG_SP(REG)'])
        data['AVG_SUM_AVG_SP(REG)_R'] = data['AVG_SUM_AVG_SP(REG)_R'].fillna(data['AVG_SUM_AVG_SP(REG)'])
        data['AVG_SUM_AVG_SP(REG)_P'] = data['AVG_SUM_AVG_SP(REG)_P'].fillna(data['SUM_AVG_SP(REG)_P'])

        data['AVG_SP(REG)_STARS'] = data['AVG_SP(REG)_STARS'].fillna(data['AVG_SP(REG)'])
        data['AVG_SP(REG)_STARTERS'] = data['AVG_SP(REG)_STARTERS'].fillna(data['AVG_SP(REG)_STARS'])

        data['COUNT_GP'] = data['COUNT_GP'].fillna(0)

        data['ABS_POINTSPREAD'] = data['ABS_POINTSPREAD'].fillna(0)
        data['AVG_ABS_DIFF_PTS'] = data['AVG_ABS_DIFF_PTS'].fillna(data['ABS_POINTSPREAD'])

        # we can predict Y for a player as long as AVG_Y is not nan
        data = data.dropna(subset=['AVG_Y'])

        return data

    def train_model(self):
        if not self.created_features:
            raise Exception('Must create features before training model')

        X = self.train_data[self.regressors]
        y = self.train_data[self.regressand]
        self.model.fit(X, y, test_size=0.25, early_stopping_rounds=25)

        self.trained_model = True

    def predict(self):
        if not self.trained_model:
            raise Exception('Must train model before generating predictions')

        self.test_data['{}_HAT'.format(self.regressand)] = self.model.predict(self.test_data[self.regressors])
        return self.test_data[['GAMEID', 'PLAYERID', '{}_HAT'.format(self.regressand)]]
