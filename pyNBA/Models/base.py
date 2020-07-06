import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import xgboost as xgb
from catboost import CatBoostRegressor, Pool


class Model(object):
    def __init__(self):
        self.model = None

    def fit(self):
        pass

    def predict(self, X):
        return self.model.predict(X)


class LinearRegressionModel(Model):
    def __init__(self):
        self.model = LinearRegression()

    def fit(self, X, y, sample_weight=None):
        if sample_weight is not None:
            self.model.fit(X, y, sample_weight=sample_weight)
        else:
            self.model.fit(X, y)


class XGBoostRegressionModel(Model):
    def __init__(self, params):
        self.model = xgb.XGBRegressor()
        self.model.set_params(**params)

    def fit(self, X, y, sample_weight=None, test_size=0.25, early_stopping_rounds=25):
        if sample_weight is not None:
            X_train, X_test, y_train, y_test, sw_train, sw_test = train_test_split(
                X, y, sample_weight, test_size=test_size
                )
            eval_set = [(X_test, y_test)]
            self.model.fit(
                X_train, y_train, sample_weight=sw_train, eval_set=eval_set, sample_weight_eval_set=sw_test,
                early_stopping_rounds=early_stopping_rounds, verbose=0
                )
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
            eval_set = [(X_test, y_test)]
            self.model.fit(
                X_train, y_train, eval_set=eval_set, early_stopping_rounds=early_stopping_rounds, verbose=0
                )


class CatBoostRegressionModel(Model):
    def __init__(self, params):
        self.model = CatBoostRegressor()
        self.model.set_params(**params, silent=True)

    def fit(self, X, y, sample_weight=None, test_size=0.25, early_stopping_rounds=25):
        if sample_weight is not None:
            X_train, X_test, y_train, y_test, sw_train, sw_test = train_test_split(
                X, y, sample_weight, test_size=test_size
                )
            eval_set = Pool(
                data=X_test,
                label=y_test,
                weight=sw_test
            )
            self.model.fit(
                X_train, y_train, sample_weight=sw_train, eval_set=eval_set,
                early_stopping_rounds=early_stopping_rounds
                )
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
            eval_set = Pool(
                data=X_test,
                label=y_test
            )
            self.model.fit(X_train, y_train, eval_set=eval_set, early_stopping_rounds=early_stopping_rounds)


class WeightFunctions(object):
    @staticmethod
    def game_seconds_played_weight(game_seconds_played):
        return 1/(1 + np.exp((-0.80*game_seconds_played + 600)/180)) - 0.01

    @staticmethod
    def season_seconds_played_weight(season_seconds_played):
        return 1/(1 + np.exp((-0.175*season_seconds_played + 840)/300)) - 0.04
