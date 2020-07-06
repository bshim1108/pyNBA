import pandas as pd

from pyNBA.Data.constants import DB_TEAM_TO_NBA_TEAM
from pyNBA.Models.helpers import CleanData

from pyNBA.Models.features import FeatureCreation
from pyNBA.Models.base import XGBoostRegressionModel

from pyNBA.Models.constants import TOPSCORE_MODEL_PARAMS


class TopScoreModel(object):
    def __init__(self, train_data, test_data):
        self.feature_creation = FeatureCreation()
        self.clean_data = CleanData()

        self.train_data = train_data
        self.test_data = test_data
        self.model = XGBoostRegressionModel(TOPSCORE_MODEL_PARAMS)

        self.regressors = ['GAMECOUNT', 'TOTALENTRIES', 'AVERAGE_TOTAL']
        self.regressand = 'TOPSCORE'

        self.created_features = False
        self.trained_model = False

    def create_features(self, odds_data):
        data = pd.concat([self.train_data, self.test_data])

        train_index = self.train_data.set_index(['DATE', 'CONTESTID']).index
        test_index = self.test_data.set_index(['DATE', 'CONTESTID']).index

        full_game_odds = odds_data.loc[odds_data['PERIOD'] == 'Full Game']
        data['TEAMSLIST'] = data['TEAMS'].apply(lambda x: x.split('_'))
        team_contest_data = data.explode('TEAMSLIST').rename(columns={'TEAMSLIST': 'TEAM'})
        team_contest_data['TEAM'] = team_contest_data['TEAM'].apply(
            lambda x: x if x not in DB_TEAM_TO_NBA_TEAM else DB_TEAM_TO_NBA_TEAM[x]
        )
        team_contest_data = team_contest_data.merge(full_game_odds, on=['DATE', 'TEAM'], how='left')
        team_contest_data = team_contest_data.dropna(subset=['TOTAL'])

        contest_average_total = team_contest_data.groupby(['DATE', 'CONTESTID']).apply(
            lambda x: pd.Series({
                'AVERAGE_TOTAL': x['TOTAL'].mean()
            })
        ).reset_index()
        data = data.merge(contest_average_total, on=['DATE', 'CONTESTID'], how='left')

        data = data.set_index(['DATE', 'CONTESTID'])

        train_index = list(set(data.index.values).intersection(set(train_index.values)))
        self.train_data = data.loc[train_index].reset_index()
        test_index = list(set(data.index.values).intersection(set(test_index.values)))
        self.test_data = data.loc[test_index].reset_index()

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

        return self.test_data[['DATE', 'CONTESTID', output_column]], output_column
