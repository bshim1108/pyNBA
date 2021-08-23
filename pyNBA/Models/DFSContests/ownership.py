import numpy as np
import pandas as pd

from pyNBA.Data.constants import DB_TEAM_TO_NBA_TEAM
from pyNBA.Models.helpers import CleanData
from pyNBA.DFS.rules import FPCalculator

from pyNBA.Models.features import FeatureCreation
from pyNBA.Models.base import XGBoostRegressionModel

from pyNBA.Models.constants import (OWNERSHIP_MODEL_PARAMS, OWNERSHIP_MODEL_REGRESSORS,
                                    OWNERSHIP_MODEL_REGRESSAND)
from pyNBA.Data.constants import OWNERSHIP_NAME_TO_NBA_NAME


class OwnershipModel(object):
    def __init__(self, train_data, test_data):
        self.feature_creation = FeatureCreation()
        self.clean_data = CleanData()

        self.train_data = train_data
        self.test_data = test_data
        self.model = XGBoostRegressionModel(OWNERSHIP_MODEL_PARAMS)

        self.regressors = OWNERSHIP_MODEL_REGRESSORS
        self.regressand = OWNERSHIP_MODEL_REGRESSAND

        self.created_features = False
        self.trained_model = False

    def create_features(self):
        for df in [self.train_data, self.test_data]:
            df['VALUE'] = df['PROJECTION']/df['SALARY']

            df = self.feature_creation.expanding_mean(
                df=df, group_col_names=['SEASON', 'PLAYER_ID'], col_name='FINAL', new_col_name='AVG_FP'
            )
            df = self.feature_creation.lag(
                df=df, group_col_names=['SEASON', 'PLAYER_ID'], col_name='FINAL', new_col_name='L1_FP', n_shift=1
            )
            df = self.feature_creation.rolling_mean(
                df=df, group_col_names=['SEASON', 'PLAYER_ID'], col_name='FINAL', new_col_name='MA5_FP', n_rolling=5
            )

            df = self.feature_creation.lag(
                df=df, group_col_names=['SEASON', 'PLAYER_ID'], col_name='SALARY', new_col_name='L1_SALARY', n_shift=1
            )
            df['SALARY_CHANGE'] = df['SALARY'] - df['L1_SALARY']

            df = self.feature_creation.lag(
                df=df, group_col_names=['SEASON', 'PLAYER_ID'], col_name='PROJECTION', new_col_name='L1_PROJECTION', n_shift=1
            )
            df['PROJECTION_CHANGE'] = df['PROJECTION'] - df['L1_PROJECTION']

            df['POSITIONS'] = df['POS'].apply(lambda x: x.split('/'))
            df['NUM_POSITIONS'] = df['POSITIONS'].apply(lambda x: len(x))
            df['is_G'] = df['POSITIONS'].apply(lambda x: 1 if bool(set(x) & set(['PG', 'SG'])) else 0)
            df['is_F'] = df['POSITIONS'].apply(lambda x: 1 if bool(set(x) & set(['SF', 'PF'])) else 0)

            df = self.feature_creation.expanding_mean(
                df=df, group_col_names=['SEASON', 'PLAYER_ID'], col_name='OWNERSHIP', new_col_name='AVG_OWNERSHIP'
            )

            df = self.feature_creation.lag(
                df=df, group_col_names=['SEASON', 'PLAYER_ID'], col_name='OWNERSHIP', new_col_name='L1_OWNERSHIP', n_shift=1
            )

            df = self.feature_creation.rolling_mean(
                df=df, group_col_names=['SEASON', 'PLAYER_ID'], col_name='OWNERSHIP', new_col_name='MA5_OWNERSHIP', n_rolling=5
            )

            slate_player_info = df[['SLATEID', 'PLAYER_ID', 'POSITIONS', 'SALARY', 'VALUE']]
            slate_player_info['SALARY_BIN'] = pd.cut(
                slate_player_info['SALARY'], bins=[3000, 4000, 6000, 8000, 10500], duplicates='drop', include_lowest=True
                )
            slate_player_info = slate_player_info.explode('POSITIONS').rename(columns={'POSITIONS': 'L1_POSITION'})

            L1_TO_L2 = {'PG': 'G', 'SG': 'G', 'SF': 'F', 'PF': 'F', 'C': 'C'}
            slate_player_info['L2_POSITION'] = slate_player_info['L1_POSITION'].apply(lambda x: L1_TO_L2[x])

            MIN_VALUE = 0.0025
            counts = slate_player_info.loc[slate_player_info['VALUE'] > MIN_VALUE]

            temp = counts.groupby(['SLATEID', 'L1_POSITION'])['PLAYER_ID'].count().reset_index()
            temp = temp.rename(columns={'PLAYER_ID': 'L1P_COUNT'})
            slate_player_info = slate_player_info.merge(temp, on=['SLATEID', 'L1_POSITION'], how='left')

            temp = counts.groupby(['SLATEID', 'L1_POSITION', 'SALARY_BIN'])['PLAYER_ID'].count().reset_index()
            temp = temp.rename(columns={'PLAYER_ID': 'L1P_SB_COUNT'})
            slate_player_info = slate_player_info.merge(temp, on=['SLATEID', 'L1_POSITION', 'SALARY_BIN'], how='left')

            temp = counts.groupby(['SLATEID', 'L2_POSITION'])['PLAYER_ID'].count().reset_index()
            temp = temp.rename(columns={'PLAYER_ID': 'L2P_COUNT'})
            slate_player_info = slate_player_info.merge(temp, on=['SLATEID', 'L2_POSITION'], how='left')

            temp = counts.groupby(['SLATEID', 'L2_POSITION', 'SALARY_BIN'])['PLAYER_ID'].count().reset_index()
            temp = temp.rename(columns={'PLAYER_ID': 'L2P_SB_COUNT'})
            slate_player_info = slate_player_info.merge(temp, on=['SLATEID', 'L2_POSITION', 'SALARY_BIN'], how='left')

            temp = counts.groupby(['SLATEID'])['PLAYER_ID'].count().reset_index()
            temp = temp.rename(columns={'PLAYER_ID': 'L3P_COUNT'})
            slate_player_info = slate_player_info.merge(temp, on=['SLATEID'], how='left')

            temp = counts.groupby(['SLATEID', 'SALARY_BIN'])['PLAYER_ID'].count().reset_index()
            temp = temp.rename(columns={'PLAYER_ID': 'L3P_SB_COUNT'})
            slate_player_info = slate_player_info.merge(temp, on=['SLATEID', 'SALARY_BIN'], how='left')

            slate_player_info['SALARY_FLOOR'] = slate_player_info['SALARY_BIN'].apply(lambda x: x.left)

            slate_player_info['L1P_RANK'] = slate_player_info.groupby(['SLATEID', 'L1_POSITION'])['VALUE'].rank(method='min', ascending=False)
            slate_player_info['L1P_SB_RANK'] = slate_player_info.groupby(['SLATEID', 'L1_POSITION', 'SALARY_FLOOR'])['VALUE'].rank(method='min', ascending=False)
            slate_player_info['L2P_RANK'] = slate_player_info.groupby(['SLATEID', 'L2_POSITION'])['VALUE'].rank(method='min', ascending=False)
            slate_player_info['L2P_SB_RANK'] = slate_player_info.groupby(['SLATEID', 'L2_POSITION', 'SALARY_FLOOR'])['VALUE'].rank(method='min', ascending=False)
            slate_player_info['L3P_RANK'] = slate_player_info.groupby(['SLATEID'])['VALUE'].rank(method='min', ascending=False)
            slate_player_info['L3P_SB_RANK'] = slate_player_info.groupby(['SLATEID', 'SALARY_FLOOR'])['VALUE'].rank(method='min', ascending=False)

            slate_player_info = slate_player_info[[
                'SLATEID', 'PLAYER_ID',
                'L1P_COUNT', 'L1P_RANK', 'L1P_SB_COUNT', 'L1P_SB_RANK',
                'L2P_COUNT', 'L2P_RANK', 'L2P_SB_COUNT', 'L2P_SB_RANK',
                'L3P_COUNT', 'L3P_RANK', 'L3P_SB_COUNT', 'L3P_SB_RANK'
            ]].groupby(['SLATEID', 'PLAYER_ID']).mean().reset_index()

            df = df.merge(slate_player_info, on=['SLATEID', 'PLAYER_ID'], how='left')

        self.created_features = True

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

        output_column = '{}_HAT'.format(self.regressand)

        self.test_data[output_column] = self.model.predict(self.test_data[self.regressors])

        return self.test_data[['DATE', 'SLATEID', 'PLAYER_ID', output_column]]
