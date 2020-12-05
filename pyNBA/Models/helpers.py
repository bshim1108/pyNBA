from pyNBA.Models.features import FeatureCreation
from pyNBA.Data.constants import ROTO_NAME_TO_NBA_NAME, SEASON_TO_REGULAR_SEASON_DATES


class CleanData(object):
    def __init__(self):
        self.feature_creation = FeatureCreation()

    def select_regular_season_games(self, df):
        for season in SEASON_TO_REGULAR_SEASON_DATES:
            regular_season_end = SEASON_TO_REGULAR_SEASON_DATES[season]['END']
            df = df.loc[~( (df['SEASON'] == season) & (df['DATE'] > regular_season_end) )]
        return df

    def drop_rows_player_inactive(self, df):
        df = df.loc[~(df['SECONDSPLAYED'] == 0)]
        return df

    def drop_rows_player_injured(self, df):
        df = df.loc[~( (df['SECONDSPLAYED'] == 0) & (df['COMMENT'] != "DNP - Coach's Decision") )]
        return df

    def drop_rows_player_rest(self, df, thresh=1200):
        df = self.feature_creation.expanding_mean(
            df=df, group_col_names=['SEASON', 'PLAYERID'], col_name='SECONDSPLAYED', new_col_name='AVG_SP'
            )
        df = df.loc[~( (df['AVG_SP'] > thresh) & (df['COMMENT'] == "DNP - Coach's Decision") )]
        df = df.drop(columns=['AVG_SP'])
        return df

    def roto_name_to_nba_name(self, name):
        name_list = name.split(',')
        name = "{} {}".format(name_list[-1].lstrip(), ' '.join(name_list[:-1]))
        if name in ROTO_NAME_TO_NBA_NAME:
            return ROTO_NAME_TO_NBA_NAME[name]
        return name
