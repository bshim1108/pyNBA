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

class PlayerProps(object):
    def __init__(self):
        self.current_date_string = datetime.now().strftime("%Y-%m-%d")
        self.query_data = QueryData(update=True)
        self.gc = gspread.service_account()

    def get_historical_boxscores(self, start_date=None, end_date=None):
        clean_data = CleanData()

        boxscores = self.query_data.query_boxscore_data()
        # boxscores = boxscores.loc[boxscores['SEASONTYPE'] == 'Regular Season']
        boxscores = clean_data.drop_rows_player_injured(boxscores)

        if start_date is not None:
            boxscores = boxscores.loc[boxscores['DATE'] >= start_date]
        if end_date is not None:
            boxscores = boxscores.loc[boxscores['DATE'] <= end_date]

        return boxscores

    def get_current_players(self):
        sh = self.gc.open('Current Lineups')
        worksheet = sh.worksheet("Data")
        current_lineups = pd.DataFrame(worksheet.get_all_records())
    
        current_lineups = current_lineups.loc[current_lineups['PLAYERCHANCE'] > 50]

        current_lineups = current_lineups[['PLAYERID', 'SEASON', 'TEAM', 'OPP_TEAM', 'NAME', 'START', 'POSITION']]
        current_lineups['PLAYERID'] = current_lineups['PLAYERID'].astype(str)
        current_lineups['DATE'] = self.current_date_string
        current_lineups['GAMEID'] = str(1e24)

        return current_lineups

    def generate_data(self, train_start_date=None, train_end_date=None):
        print('retrieving historical boxscores...')
        historical_boxscores = self.get_historical_boxscores(train_start_date, train_end_date)
        historical_boxscores['NAME'] = None
        historical_boxscores['POSITION'] = None

        print('retrieving current players...')
        current_players = self.get_current_players()
        data = historical_boxscores.append(current_players)

        print('generating minutes data...')
        mp_out = MinutesPlayed().predict(data, self.current_date_string, self.current_date_string)

        print('generating possessions/minute data...')
        ppm_out = PossessionsPerMinute().predict(data, self.current_date_string, self.current_date_string)

        print('generating points/possession data...')
        ppp_out = PointsPerPossession().predict(data, self.current_date_string, self.current_date_string)

        print('generating rebounds/possession data...')
        rpp_out = ReboundsPerPossession().predict(data, self.current_date_string, self.current_date_string)

        print('generating assists/possession data...')
        app_out = AssistsPerPossession().predict(data, self.current_date_string, self.current_date_string)

        print('generating turnovers/possession data...')
        tpp_out = TurnoversPerPossession().predict(data, self.current_date_string, self.current_date_string)

        predicted_boxscores = reduce(
            lambda left, right: pd.merge(
                left, right, on=['SEASON', 'DATE', 'TEAM', 'OPP_TEAM', 'NAME', 'POSITION', 'START']
                ), [mp_out, ppm_out, ppp_out, app_out, rpp_out, tpp_out]
                )
        return predicted_boxscores

    def write_stat_data(self, train_start_date=None, train_end_date=None):
        predicted_boxscores = self.generate_data(train_start_date, train_end_date)
        predicted_boxscores = predicted_boxscores.fillna(0)
        predicted_boxscores = predicted_boxscores.sort_values(by=['TEAM', 'START', 'AVG_MP(REG)_R'], ascending=False)

        print('writing player stat data to excel...')
        sh = self.gc.open('Predicted Stats')
        sh.values_clear("RawData!A1:Z999")
        worksheet = sh.worksheet("RawData")
        worksheet.update([predicted_boxscores.columns.values.tolist()] + predicted_boxscores.values.tolist())
        sh.share('brandonshimiaie@gmail.com', perm_type='user', role='writer')

if __name__ == "__main__": 
    PlayerProps().write_stat_data()
  