from pyNBA.Models.features import FeatureCreation


class VarianceModel(object):
    def __init__(self, test_data):
        self.feature_creation = FeatureCreation()
        self.test_data = test_data
        self.original_columns = list(self.test_data.columns)

    def predict(self, y):
        output_column = 'STD_{}'.format(y)
        self.test_data = self.feature_creation.expanding_standard_deviation(
            df=self.test_data, group_col_names=['SEASON', 'PLAYERID', 'START'], col_name=y,
            new_col_name=output_column, min_periods=4
        )

        return self.test_data[self.original_columns + [output_column]], output_column
