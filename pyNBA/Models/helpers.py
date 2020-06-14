from pyNBA.Models.features import FeatureCreation

class CleanData(object):
    def __init__(self):
        self.feature_creation = FeatureCreation()

    def drop_rows_player_inactive(self, df):
        df = df.loc[~(df['SECONDSPLAYED'] == 0)]
        return df

    def drop_rows_player_injured(self, df):
        df = df.loc[~((df['SECONDSPLAYED'] == 0) & (df['COMMENT'] != "DNP - Coach's Decision"))]
        return df

    def drop_rows_player_rest(self, df, thresh=1200):
        df = self.feature_creation.expanding_mean(df=df, group_col_names=['SEASON', 'PLAYERID'], col_name='SECONDSPLAYED', new_col_name='AVG_SP')
        df = df.loc[~((df['AVG_SP'] > thresh) & (df['COMMENT'] == "DNP - Coach's Decision"))]
        df = df.drop(columns=['AVG_SP'])
        return df