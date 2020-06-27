from pyNBA.Models.features import FeatureCreation


class VarianceModel(object):
    def __init__(self, test_data):
        self.feature_creation = FeatureCreation()
        self.test_data = test_data
        self.original_columns = list(self.test_data.columns)

    def predict(self, y, y_hat):
        abs_residual_column = 'ABS_RESIDUAL'
        output_column = 'AVG_ABS_RESIDUAL'
        self.test_data[abs_residual_column] = (self.test_data[y] - self.test_data[y_hat]).abs()
        self.test_data = self.feature_creation.expanding_mean(
            df=self.test_data, group_col_names=['SEASON', 'PLAYERID', 'START'], col_name=abs_residual_column,
            new_col_name=output_column, min_periods=5
        )

        return self.test_data[self.original_columns + [output_column]], output_column
