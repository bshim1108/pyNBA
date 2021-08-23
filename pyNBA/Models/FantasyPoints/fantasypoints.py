from functools import reduce
import pandas as pd

from pyNBA.DFS.constants import Site
from pyNBA.DFS.rules import FPCalculator

from pyNBA.Models.points_per_second import PPSModel
from pyNBA.Models.made_threes_per_second import MTPSModel
from pyNBA.Models.rebounds_per_second import RPSModel
from pyNBA.Models.assists_per_second import APSModel
from pyNBA.Models.turnovers_per_second import TPSModel
from pyNBA.Models.steals_per_second import SPSModel
from pyNBA.Models.blocks_per_second import BPSModel
from pyNBA.Models.seconds import SecondsModel


class FPModel(object):
    def __init__(self, train_data, test_data, site):
        self.train_data = train_data
        self.test_data = test_data
        self.original_columns = list(test_data.columns)
        self.site = site
        self.FPCalculator = FPCalculator(site)

        self.pps_model = PPSModel(train_data, test_data)
        self.rps_model = RPSModel(train_data, test_data)
        self.aps_model = APSModel(train_data, test_data)
        self.tps_model = TPSModel(train_data, test_data)
        self.sps_model = SPSModel(train_data, test_data)
        self.bps_model = BPSModel(train_data, test_data)
        self.seconds_model = SecondsModel(train_data, test_data)

        if self.site == Site.DRAFTKINGS:
            self.mtps_model = MTPSModel(train_data, test_data)

        self.trained_model = False

    def train_model(self, quarterly_boxscore_data, odds_data):
        self.seconds_model.create_features(quarterly_boxscore_data, odds_data)
        self.seconds_model.train_model()

        self.pps_model.create_features()
        self.pps_model.train_model()

        self.rps_model.create_features(odds_data)
        self.rps_model.train_model()

        self.aps_model.create_features(odds_data)
        self.aps_model.train_model()

        self.tps_model.create_features(odds_data)
        self.tps_model.train_model()

        self.sps_model.create_features(odds_data)
        self.sps_model.train_model()

        self.bps_model.create_features(odds_data)
        self.bps_model.train_model()

        if self.site == Site.DRAFTKINGS:
            self.mtps_model.create_features(odds_data)
            self.mtps_model.train_model()

        self.trained_model = True

    def predict(self):
        if not self.trained_model:
            raise Exception('Must train model before generating predictions')

        sp_pred = self.seconds_model.predict()
        pps_pred = self.pps_model.predict()
        mtps_pred = self.mtps_model.predict()
        rps_pred = self.rps_model.predict()
        aps_pred = self.aps_model.predict()
        tps_pred = self.tps_model.predict()
        sps_pred = self.sps_model.predict()
        bps_pred = self.bps_model.predict()

        dfs = [self.test_data, pps_pred, rps_pred, aps_pred, tps_pred, bps_pred, sps_pred, sp_pred]
        if self.site == Site.DRAFTKINGS:
            dfs.append(mtps_pred)
        predictions = reduce(lambda left, right: pd.merge(left, right, on=['GAMEID', 'PLAYERID'], how='outer'), dfs)

        if self.site == Site.DRAFTKINGS:
            predictions['FPPS_HAT'] = predictions.apply(
                lambda x: self.FPCalculator.calculate_draftkings_fp(
                    x['PPS_HAT'], x['RPS_HAT'], x['APS_HAT'],
                    x['TPS_HAT'], x['BPS_HAT'], x['SPS_HAT'], x['MTPS_HAT']
                ),
                axis=1
            )
        else:
            predictions['FPPS_HAT'] = predictions.apply(
                lambda x: self.FPCalculator.calculate_fanduel_fp(
                    x['SEASON'], x['PPS_HAT'], x['RPS_HAT'], x['APS_HAT'],
                    x['TPS_HAT'], x['BPS_HAT'], x['SPS_HAT']
                ),
                axis=1
            )

        output_column = '{}_FP_HAT'.format(self.site)
        predictions[output_column] = predictions['SECONDSPLAYED_HAT'] * predictions['FPPS_HAT']

        return predictions[self.original_columns + [output_column]], output_column
