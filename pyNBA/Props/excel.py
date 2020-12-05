import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
import gspread
from functools import reduce
from datetime import datetime
from pyNBA.Data.data import QueryData
from pyNBA.Models.helpers import CleanData
from pyNBA.Models.StatsV2.minutesplayed import MinutesPlayed
from pyNBA.Models.StatsV2.possessionsperminute import PossessionsPerMinute
from pyNBA.Models.StatsV2.pointsperpossession import PointsPerPossession
from pyNBA.Models.StatsV2.assistsperpossession import AssistsPerPossession
from pyNBA.Models.StatsV2.reboundsperpossession import ReboundsPerPossession
from pyNBA.Models.StatsV2.turnoversperpossession import TurnoversPerPossession

class Excel(object):
    def __init__(self):
        self.current_date = datetime.now()

    def get_historical_boxscores(self, start_date=None, end_date=None):
        query_data = QueryData(update=True)
        clean_data = CleanData()

        boxscores = query_data.query_boxscore_data()
        boxscores = clean_data.select_regular_season_games(boxscores)
        boxscores = clean_data.drop_rows_player_injured(boxscores)
        boxscores = clean_data.drop_rows_player_rest(boxscores)

        if start_date is not None:
            boxscores = boxscores.loc[boxscores['DATE'] >= start_date]
        if end_date is not None:
            boxscores = boxscores.loc[boxscores['DATE'] <= end_date]

        return boxscores

    #TODO
    def get_current_players(self):
        current_date_string = self.current_date.strftime("%Y-%m-%d")

        boxscores = self.get_historical_boxscores()
        current_row_cols = ['PLAYERID', 'SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION', 'START']

        last_boxscores = boxscores.loc[boxscores['DATE'] == '2020-03-11']
        last_boxscores['DATE'] = current_date_string
        for col in last_boxscores.columns:
            if col not in current_row_cols:
                last_boxscores[col] = np.nan
        last_boxscores['GAMEID'] = str(1e24)

        return last_boxscores

    def generate_data(self, train_start_date=None, train_end_date=None):
        print('retrieving historical boxscores...')
        historical_boxscores = self.get_historical_boxscores(train_start_date, train_end_date)

        print('retrieving current players...')
        current_players = self.get_current_players()
        data = historical_boxscores.append(current_players)

        current_date_string = self.current_date.strftime("%Y-%m-%d")

        print('generating minutes data...')
        mp_out = MinutesPlayed().predict(data, current_date_string, current_date_string)

        print('generating possessions/minute data...')
        ppm_out = PossessionsPerMinute().predict(data, current_date_string, current_date_string)

        print('generating points/possession data...')
        ppp_out = PointsPerPossession().predict(data, current_date_string, current_date_string)

        print('generating rebounds/possession data...')
        rpp_out = ReboundsPerPossession().predict(data, current_date_string, current_date_string)

        print('generating assists/possession data...')
        app_out = AssistsPerPossession().predict(data, current_date_string, current_date_string)

        print('generating turnovers/possession data...')
        tpp_out = TurnoversPerPossession().predict(data, current_date_string, current_date_string)

        predicted_boxscores = reduce(
            lambda left, right: pd.merge(
                left, right, on=['SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION', 'START']
                ), [mp_out, ppm_out, ppp_out, app_out, rpp_out, tpp_out]
                )
        return predicted_boxscores

    def write_data(self, train_start_date=None, train_end_date=None):
        predicted_boxscores = self.generate_data(train_start_date, train_end_date)
        predicted_boxscores = predicted_boxscores.sort_values(by=['TEAM', 'START', 'MA3_MP(REG)_R'], ascending=False)

        print('writing data to excel...')
        gc = gspread.service_account()
        sh = gc.open('Predicted Stats')
        worksheet = sh.get_worksheet(0)
        worksheet.update([predicted_boxscores.columns.values.tolist()] + predicted_boxscores.values.tolist())
        sh.share('brandonshimiaie@gmail.com', perm_type='user', role='writer')

if __name__ == "__main__": 
    Excel().write_data()
  