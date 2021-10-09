import numpy as np
from pyNBA.Models.base import PredictionModel, XGBoostRegressionModel
from pyNBA.Models.constants import (VARIANCE_MODEL_PARAMS, VARIANCE_MODEL_REGRESSORS,
                                    VARIANCE_MODEL_REGRESSAND, VARIANCE_PRIMARY_COLS)


class VarianceModel(PredictionModel):
    def __init__(self, train_data, test_data):
        super().__init__(
            train_data, test_data, VARIANCE_MODEL_REGRESSORS, VARIANCE_MODEL_REGRESSAND,
            VARIANCE_PRIMARY_COLS
            )
        self.model = XGBoostRegressionModel(VARIANCE_MODEL_PARAMS)

    def create_features(self, df):
        df['PROJECTION_DIFF'] = (df['ROTOWIRE_PROJECTION'] - df['LINESTARAPP_PROJECTION']).abs()
        df.loc[
            (df['ROTOWIRE_PROJECTION'] == 0) |
            (df['LINESTARAPP_PROJECTION'] == 0),
            'PROJECTION_DIFF'
        ] = np.nan

        df = self.feature_creation.expanding_mean(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='SALARY', new_col_name='AVG_SALARY'
        )
        df = self.feature_creation.lag(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='SALARY', new_col_name='L1_SALARY', n_shift=1
        )
        df['SALARY_CHANGE'] = df['SALARY'] - df['L1_SALARY']

        df = self.feature_creation.expanding_mean(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='PROJECTION', new_col_name='AVG_PROJECTION'
        )
        df = self.feature_creation.lag(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='PROJECTION', new_col_name='L1_PROJECTION', n_shift=1
        )
        df['PROJECTION_CHANGE'] = df['PROJECTION'] - df['L1_PROJECTION']

        df = self.feature_creation.expanding_standard_deviation(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='FINAL', new_col_name='STD_FP', min_periods=5
        )

        df = self.feature_creation.expanding_min(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='FINAL', new_col_name='MIN_FP'
        )
        df = self.feature_creation.expanding_max(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='FINAL', new_col_name='MAX_FP'
        )

        df['ABS_RES'] = (df['PROJECTION'] - df['FINAL']).abs()
        df = self.feature_creation.expanding_mean(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='ABS_RES', new_col_name='AVG_ABS_RES'
        )
        df = self.feature_creation.lag(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM', 'START'], col_name='ABS_RES', new_col_name='L1_ABS_RES', n_shift=1
        )

        df['GP'] = 1
        df = self.feature_creation.expanding_sum(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM'], col_name='GP', new_col_name='COUNT_GP'
        )
        df = self.feature_creation.expanding_sum(
            df=df, group_col_names=['SEASON', 'PLAYER_ID', 'TEAM'], col_name='START', new_col_name='COUNT_START'
        )
        df['PCT_IN_ROLE'] = np.nan
        df.loc[df['START'] == 1, 'PCT_IN_ROLE'] = df['COUNT_START']/df['COUNT_GP']
        df.loc[df['START'] == 0, 'PCT_IN_ROLE'] = 1 - (df['COUNT_START']/df['COUNT_GP'])

        return df
