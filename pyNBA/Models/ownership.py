import numpy as np
import pandas as pd

from pyNBA.Data.constants import DB_TEAM_TO_NBA_TEAM
from pyNBA.Models.helpers import CleanData
from pyNBA.DFS.rules import FPCalculator

from pyNBA.Models.features import FeatureCreation
from pyNBA.Models.base import XGBoostRegressionModel

from pyNBA.Models.constants import OWNERSHIP_MODEL_PARAMS, DEFAULT_STD


class OwnershipModel(object):
    def __init__(self, train_data, test_data, site):
        self.feature_creation = FeatureCreation()
        self.clean_data = CleanData()

        self.train_data = train_data
        self.test_data = test_data
        self.site = site
        self.model = XGBoostRegressionModel(OWNERSHIP_MODEL_PARAMS)

        self.regressors = []
        self.regressand = 'OWNERSHIP'

        self.created_features = False
        self.trained_model = False

    def create_features(self, salary_data, contest_data, ownership_data, odds_data):
        data = pd.concat([self.train_data, self.test_data])

        train_index = self.train_data.set_index(['GAMEID', 'PLAYERID']).index
        test_index = self.test_data.set_index(['GAMEID', 'PLAYERID']).index

        salary_data = salary_data.loc[salary_data['SITE'] == self.site]
        data = data.merge(salary_data, on=['DATE', 'NAME'], how='left')
        data = data.dropna(subset=['SALARY'])

        # player stat features
        CustomFPCalculator = FPCalculator(self.site)

        data['REB'] = data['DREB'] + data['OREB']
        data['DKFP'] = data.apply(
            lambda x: CustomFPCalculator.calculate_fantasy_points(
                x['SEASON'], x['PTS'], x['REB'], x['AST'], x['TOV'], x['BLK'], x['STL'], x['FG3M']
            ),
            axis=1
        )

        feature_creation = FeatureCreation()

        data = feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='DKFP', new_col_name='AVG_DKFP'
        )

        data['VALUE'] = data['AVG_DKFP']/data['SALARY']
        self.regressors.append('VALUE')

        data = feature_creation.lag(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='DKFP', new_col_name='L1_DKFP',
            n_shift=1
        )
        self.regressors.append('L1_DKFP')

        data = feature_creation.rolling_mean(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='DKFP', new_col_name='MA5_DKFP', n_rolling=5
        )
        self.regressors.append('MA5_DKFP')

        data = feature_creation.lag(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='SALARY', new_col_name='L1_SALARY', n_shift=1
        )
        self.regressors.append('SALARY')

        data = feature_creation.expanding_standard_deviation(
            df=data, group_col_names=['SEASON', 'PLAYERID'], col_name='DKFP', new_col_name='STD_DKFP', min_periods=5
        )
        self.regressors.append('STD_DKFP')

        self.regressors.append('START')

        data['DFS_POSITIONS'] = data['DFS_POSITION'].apply(lambda x: x.split('_') if isinstance(x, str) else np.nan)
        data['NUM_POSITIONS'] = data['DFS_POSITIONS'].apply(lambda x: len(x) if isinstance(x, list) else np.nan)
        self.regressors.append('NUM_POSITIONS')

        for position in ['SF', 'PG', 'C']:
            data[position] = 0
            data.loc[data['DFS_POSITION'].str.contains(position), position] = 1
            self.regressors.append(position)

        # historical ownership of player
        ownership_data = ownership_data.merge(contest_data, on=['SLATEID', 'CONTESTNAME'], how='left')
        aggregated_ownership = ownership_data.groupby(['DATE', 'NAME']).apply(
            lambda x: pd.Series({
                'TOTAL_OWNERSHIP': x['OWNERSHIP'].mean()
            })
        ).reset_index()

        data = data.merge(aggregated_ownership, on=['DATE', 'NAME'], how='left')
        data = data.dropna(subset=['TOTAL_OWNERSHIP'])

        data = feature_creation.expanding_mean(
            df=data, group_col_names=['SEASON', 'NAME'], col_name='TOTAL_OWNERSHIP', new_col_name='AVG_OWNERSHIP'
        )
        self.regressors.append('AVG_OWNERSHIP')

        data = feature_creation.lag(
            df=data, group_col_names=['SEASON', 'NAME'], col_name='TOTAL_OWNERSHIP', new_col_name='L1_OWNERSHIP',
            n_shift=1
        )
        self.regressors.append('L1_OWNERSHIP')

        data = feature_creation.rolling_mean(
            df=data, group_col_names=['SEASON', 'NAME'], col_name='TOTAL_OWNERSHIP', new_col_name='MA5_OWNERSHIP',
            n_rolling=5
        )
        self.regressors.append('MA5_OWNERSHIP')

        # defense
        data['NORM_POS'] = data['POSITION'].apply(lambda x: x if '-' not in x else x.split('-')[0])

        temp = data.dropna(subset=['DKFP', 'AVG_DKFP'])
        grouped_defensive_boxscores = temp.groupby(['SEASON', 'DATE', 'NORM_POS', 'OPP_TEAM']).apply(
            lambda x: pd.Series({
                'TEAM_DKFP_ALLOWED_P': x['DKFP'].sum(),
                'TEAM_DKFP_AVG_P': x['AVG_DKFP'].sum()
            })
        ).reset_index()

        grouped_defensive_boxscores['DvP'] = grouped_defensive_boxscores['TEAM_DKFP_ALLOWED_P'] - \
            grouped_defensive_boxscores['TEAM_DKFP_AVG_P']

        grouped_defensive_boxscores = feature_creation.expanding_mean(
            df=grouped_defensive_boxscores, group_col_names=['SEASON', 'OPP_TEAM', 'NORM_POS'], col_name='DvP',
            new_col_name='AVG_DvP', order_idx_name='DATE', min_periods=5
        )
        self.regressors.append('AVG_DvP')

        data = data.merge(grouped_defensive_boxscores, on=['SEASON', 'DATE', 'OPP_TEAM', 'NORM_POS'], how='left')

        # vegas lines
        odds_data['TOTAL'] = odds_data['TOTAL'].replace(['PK', '-'], np.nan)
        odds_data['POINTSPREAD'] = odds_data['POINTSPREAD'].replace(['PK', '-'], 0)
        full_game_odds = odds_data.loc[odds_data['PERIOD'] == 'Full Game']
        data = data.merge(full_game_odds, on=['DATE', 'TEAM'], how='left')
        self.regressors.append('TOTAL')
        self.regressors.append('POINTSPREAD')

        # slate info
        slates = contest_data.loc[contest_data['SITE'] == self.site, ['DATE', 'SLATEID', 'TEAMS']].drop_duplicates()
        slates['TEAMS'] = slates['TEAMS'].apply(lambda x: x.split('_'))
        slates = slates.explode('TEAMS').rename(columns={"TEAMS": "TEAM"})
        slates['TEAM'] = slates['TEAM'].apply(lambda x: x if x not in DB_TEAM_TO_NBA_TEAM else DB_TEAM_TO_NBA_TEAM[x])

        slate_players = data[['DATE', 'TEAM', 'NAME', 'DFS_POSITIONS', 'SALARY', 'VALUE']].merge(
            slates, on=['DATE', 'TEAM'], how='left'
            )
        slate_players['SALARY_BIN'] = pd.cut(
            slate_players['SALARY'], bins=list(range(3000, 15000, 1000)), duplicates='drop', include_lowest=True
            )
        slate_players = slate_players.explode('DFS_POSITIONS').rename(columns={'DFS_POSITIONS': 'SINGLE_DFS_POSITION'})

        MIN_VALUE = 0.002

        all_temp = slate_players.groupby(['SLATEID', 'SINGLE_DFS_POSITION']).apply(
            lambda x: pd.Series({
                'L1P_COUNT': x.loc[x['VALUE'] > MIN_VALUE, 'NAME'].count()
            })
        ).reset_index().dropna()
        slate_players = slate_players.merge(all_temp, on=['SLATEID', 'SINGLE_DFS_POSITION'], how='left')

        L1_TO_L2 = {'PG': 'G', 'SG': 'G', 'SF': 'F', 'PF': 'F', 'C': 'C'}
        slate_players['LEVEL2_DFS_POSITION'] = slate_players['SINGLE_DFS_POSITION'].apply(
            lambda x: L1_TO_L2[x] if isinstance(x, str) else np.nan
            )

        all_temp = slate_players.groupby(['SLATEID']).apply(
            lambda x: pd.Series({
                'L3P_COUNT': x.loc[x['VALUE'] > MIN_VALUE, 'NAME'].count()
            })
        ).reset_index().dropna()
        slate_players = slate_players.merge(all_temp, on=['SLATEID'], how='left')

        sb_temp = slate_players.groupby(['SLATEID', 'SALARY_BIN']).apply(
            lambda x: pd.Series({
                'L3P_SB_COUNT': x.loc[x['VALUE'] > MIN_VALUE, 'NAME'].count()
            })
        ).reset_index().dropna()
        slate_players = slate_players.merge(sb_temp, on=['SLATEID', 'SALARY_BIN'], how='left')

        slate_players['SALARY_FLOOR'] = slate_players['SALARY_BIN'].apply(lambda x: x.left)

        slate_players['L1P_RANK'] = slate_players.groupby(
            ['SLATEID', 'SINGLE_DFS_POSITION']
            )['VALUE'].rank(method='min', ascending=False)

        slate_players['L2P_RANK'] = slate_players.groupby(
            ['SLATEID', 'LEVEL2_DFS_POSITION']
        )['VALUE'].rank(method='min', ascending=False)

        slate_players['L2P_SB_RANK'] = slate_players.groupby(
            ['SLATEID', 'LEVEL2_DFS_POSITION', 'SALARY_FLOOR']
        )['VALUE'].rank(method='min', ascending=False)

        slate_players['L3P_RANK'] = slate_players.groupby(
            ['SLATEID']
            )['VALUE'].rank(method='min', ascending=False)

        slate_players['L3P_SB_RANK'] = slate_players.groupby(
            ['SLATEID', 'SALARY_FLOOR']
            )['VALUE'].rank(method='min', ascending=False)

        slate_data = slate_players.groupby(['DATE', 'SLATEID', 'NAME']).apply(
            lambda x: pd.Series({
                'L1P_COUNT': x['L1P_COUNT'].mean(),
                'L1P_RANK': x['L1P_RANK'].mean(),
                'L2P_RANK': x['L2P_RANK'].mean(),
                'L2P_SB_RANK': x['L2P_SB_RANK'].mean(),
                'L3P_COUNT': x['L3P_COUNT'].mean(),
                'L3P_RANK': x['L3P_RANK'].mean(),
                'L3P_SB_COUNT': x['L3P_SB_COUNT'].mean(),
                'L3P_SB_RANK': x['L3P_SB_RANK'].mean()
            })
        ).reset_index()

        self.regressors.append('L1P_COUNT')
        self.regressors.append('L1P_RANK')
        self.regressors.append('L2P_RANK')
        self.regressors.append('L2P_SB_RANK')
        self.regressors.append('L3P_COUNT')
        self.regressors.append('L3P_RANK')
        self.regressors.append('L3P_SB_COUNT')
        self.regressors.append('L3P_SB_RANK')

        # contest info
        self.regressors.append('TOTALENTRIES')
        self.regressors.append('GAMECOUNT')

        data = self.preprocess(data, slate_data, ownership_data)
        data = data.set_index(['GAMEID', 'PLAYERID'])

        train_index = list(set(data.index.values).intersection(set(train_index.values)))
        self.train_data = data.loc[train_index].reset_index()
        test_index = list(set(data.index.values).intersection(set(test_index.values)))
        self.test_data = data.loc[test_index].reset_index()

        self.created_features = True

    def preprocess(self, data, slate_data, ownership_data):
        ownership_data = ownership_data.merge(slate_data, on=['DATE', 'SLATEID', 'NAME'], how='left')
        data = ownership_data.merge(data, on=['DATE', 'NAME'], how='left')

        data['L1_DKFP'] = data['L1_DKFP'].fillna(data['AVG_DKFP'])
        data['MA5_DKFP'] = data['MA5_DKFP'].fillna(data['AVG_DKFP'])

        data['STD_DKFP'] = data['STD_DKFP'].fillna(DEFAULT_STD*data['AVG_DKFP'])

        data['L1_OWNERSHIP'] = data['L1_OWNERSHIP'].fillna(data['AVG_OWNERSHIP'])
        data['MA5_OWNERSHIP'] = data['MA5_OWNERSHIP'].fillna(data['AVG_OWNERSHIP'])

        data['AVG_DvP'] = data['AVG_DvP'].fillna(0)

        data['TOTAL'] = data['TOTAL'].fillna(data['TOTAL'].mean())
        data['POINTSPREAD'] = data['POINTSPREAD'].fillna(0)

        data['L3P_SB_COUNT'] = data['L3P_SB_COUNT'].fillna(0)

        # we can predict Y for a player as long as AVG_Y is not nan
        data = data.dropna(subset=['AVG_OWNERSHIP'])

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

        output_column = '{}_HAT'.format(self.regressand)

        self.test_data[output_column] = self.model.predict(self.test_data[self.regressors])

        return self.test_data[['DATE', 'SLATEID', 'CONTESTID', 'NAME', output_column]], output_column
