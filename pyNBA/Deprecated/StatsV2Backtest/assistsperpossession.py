import pandas as pd
from pyNBA.Models.features import FeatureCreation

class AssistsPerPossession(object):
    def generate_regressors(self, boxscores, start_date, end_date):
        feature_creation = FeatureCreation()

        relevant_seasons = boxscores.loc[
                    (boxscores['DATE'] >= start_date) & 
                    (boxscores['DATE'] <= end_date)
                    ]['SEASON'].unique()
        boxscores = boxscores.loc[boxscores['SEASON'].isin(relevant_seasons)]

        boxscores['ASSISTS/POSSESSION'] = boxscores['AST']/boxscores['POSS']

        # average player assists/possession
        boxscores = feature_creation.expanding_weighted_mean(
            df=boxscores, group_col_names=['SEASON', 'TEAM', 'PLAYERID'], col_name='ASSISTS/POSSESSION',
            new_col_name='AVG_ASSISTS/POSSESSION', weight_col_name='POSS'
        )

        boxscores = boxscores.loc[
            (boxscores['DATE'] >= start_date) & 
            (boxscores['DATE'] <= end_date)
            ]

        return boxscores

    def predict(self, boxscores, predict_start_date, predict_end_date):
        predicted_data = self.generate_regressors(boxscores, predict_start_date, predict_end_date)

        predicted_data = predicted_data.rename(columns={'AVG_ASSISTS/POSSESSION': 'AST/POSS'})
        cols = [
            'SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'PLAYERID', 'START',
            'AST/POSS'
            ]
        return predicted_data[cols]