import pandas as pd
from pyNBA.Models.StatsV2.basestatmodel import BaseStatModel
from pyNBA.Models.base import CatBoostRegressionModel
from pyNBA.Models.features import FeatureCreation
from pyNBA.Data.data import QueryData

class MinutesPlayed(object):
    def generate_regressors(self, boxscores, start_date, end_date, q_boxscores):
        feature_creation = FeatureCreation()

        relevant_seasons = boxscores.loc[
                    (boxscores['DATE'] >= start_date) & 
                    (boxscores['DATE'] <= end_date)
                    ]['SEASON'].unique()
        boxscores = boxscores.loc[boxscores['SEASON'].isin(relevant_seasons)]

        boxscores = boxscores.merge(q_boxscores, on=['GAMEID', 'PLAYERID'], how='left')
        boxscores[q_boxscores.columns] = boxscores[q_boxscores.columns].fillna(0)
        boxscores['SP(REG)'] = boxscores['SP(Q1)'] + boxscores['SP(Q2)'] + boxscores['SP(Q3)'] + boxscores['SP(Q4)']
        boxscores['MP(REG)'] = boxscores['SP(REG)']/60
        boxscores['MP(Q4)'] = boxscores['SP(Q4)']/60

        # average minutes played in role
        boxscores = feature_creation.expanding_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID', 'START'], col_name='MP(REG)',
            new_col_name='AVG_MP(REG)_R'
        )

        boxscores = feature_creation.rolling_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID', 'START'], col_name='MP(REG)',
            new_col_name='MA3_MP(REG)_R', n_rolling=5
        )

        boxscores = boxscores.loc[
            (boxscores['DATE'] >= start_date) & 
            (boxscores['DATE'] <= end_date)
            ]

        return boxscores

    def predict(self, boxscores, predict_start_date, predict_end_date, update=True):
        query_data = QueryData(update=update)

        q_boxscores = query_data.query_quarterly_boxscore_data()
        q_boxscores = q_boxscores.pivot_table('SECONDSPLAYED', ['GAMEID', 'PLAYERID'], 'QUARTER')
        q_boxscores.columns = ['SP(Q{})'.format(str(col)) for col in q_boxscores.columns]

        predicted_data = self.generate_regressors(boxscores, predict_start_date, predict_end_date, q_boxscores)
        predicted_data[['AVG_MP(REG)_R', 'MA3_MP(REG)_R']] = predicted_data[['AVG_MP(REG)_R', 'MA3_MP(REG)_R']].fillna(0)

        cols = [
            'SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION', 'START', 'PLAYERCHANCE',
            'AVG_MP(REG)_R', 'MA3_MP(REG)_R'
            ]
        return predicted_data[cols]
