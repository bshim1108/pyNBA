import pandas as pd

class BaseStatModel(object):
    def __init__(self, use_cached_model=False, train_start_date=None, train_end_date=None):
        if (not use_cached_model) and (train_start_date is None and train_end_date is None):
            raise Exception('Must use cached model or specify a training start and end date')
        self.use_cached_model = use_cached_model
        self.train_start_date = train_start_date
        self.train_end_date = train_end_date

    def set_params(self, base_model, cached_model, regressand, regressors, weight, generate_regressors_params={}):
        self.base_model = base_model
        self.regressand = regressand
        self.regressors = regressors
        self.weight = weight
        self.cached_model = cached_model
        self.generate_regressors_params = generate_regressors_params

    def generate_regressors(self, boxscores, start_date, end_date):
        return boxscores

    def preprocess(self, boxscores):
        return boxscores

    def predict(self, boxscores, predict_start_date, predict_end_date):
        model = self.get_model(boxscores)

        y_hat = '{}_HAT'.format(self.regressand)
        predicted_data = self.generate_regressors(
            boxscores, predict_start_date, predict_end_date, **self.generate_regressors_params
            )
        predicted_data[y_hat] = model.predict(predicted_data[self.regressors])
        return predicted_data

    def get_model(self, boxscores):
        if self.use_cached_model:
            if self.use_cached_model is None:
                raise Exception('Cached model does not exist')
            model = self.cached_model
        else:
            train_data = self.generate_regressors(
                boxscores, self.train_start_date, self.train_end_date, **self.generate_regressors_params
                )
            model = self.fit_model(train_data)
        return model

    def fit_model(self, train_data):
        train_data = self.preprocess(train_data)
        y = train_data[self.regressand]
        X = train_data[self.regressors]
        w = train_data[self.weight] if self.weight is not None else None
        self.base_model.fit(X, y, sample_weight=w)
        return self.base_model