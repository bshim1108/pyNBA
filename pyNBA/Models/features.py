import pandas as pd


class FeatureCreation(object):
    def __init__(self):
        pass

    def prepare_df(self, df, new_col_name, order_idx_name):
        if new_col_name in df.columns:
            df = df.drop(columns=new_col_name)

        if isinstance(df.index, pd.MultiIndex):
            original_idx_name = df.index.names
        else:
            original_idx_name = df.index.name
        if original_idx_name is not None:
            df = df.reset_index()
        df = df.set_index(order_idx_name).sort_index()
        return df, original_idx_name

    def merge_stat_to_df(self, stat_df, df, group_col_names, col_name, new_col_name, n_shift, order_idx_name='DATE'):
        index_name = df.index.name

        stat_df = stat_df.groupby(by=group_col_names).shift(n_shift)
        stat_df = stat_df.reset_index()
        stat_df = stat_df.rename(columns={col_name: new_col_name})

        temp_cols = group_col_names + [index_name] + [new_col_name]
        stat_df = stat_df[temp_cols]

        merge_cols = group_col_names + [index_name]
        df = df.merge(stat_df, on=merge_cols, how='left')
        return df

    def expanding_mean(self, df, group_col_names, col_name, new_col_name, min_periods=1, n_shift=1,
                       order_idx_name='DATE'):
        df, original_idx_name = self.prepare_df(df, new_col_name=new_col_name, order_idx_name=order_idx_name)

        temp = df.groupby(group_col_names)[col_name].expanding(min_periods=min_periods).mean()

        df = self.merge_stat_to_df(
            stat_df=temp, df=df, group_col_names=group_col_names, col_name=col_name, new_col_name=new_col_name,
            n_shift=n_shift
            )

        if original_idx_name is None:
            return df
        return df.set_index(original_idx_name)

    def expanding_weighted_mean(self, df, group_col_names, col_name, weight_col_name, new_col_name, min_periods=1,
                                n_shift=1, order_idx_name='DATE'):
        df, original_idx_name = self.prepare_df(df, new_col_name=new_col_name, order_idx_name=order_idx_name)

        df['weighted_col'] = df[col_name] * df[weight_col_name]
        temp = df.groupby(group_col_names)
        temp = temp['weighted_col'].expanding(min_periods=min_periods).sum() / \
            temp[weight_col_name].expanding(min_periods=min_periods).sum()
        temp = temp.rename(col_name)
        df = df.drop(columns='weighted_col')

        df = self.merge_stat_to_df(
            stat_df=temp, df=df, group_col_names=group_col_names, col_name=col_name, new_col_name=new_col_name,
            n_shift=n_shift
            )

        if original_idx_name is None:
            return df
        return df.set_index(original_idx_name)

    def expanding_ewm(self, df, group_col_names, col_name, new_col_name, alpha, min_periods=1, n_shift=1,
                      order_idx_name='DATE'):
        df, original_idx_name = self.prepare_df(df, new_col_name=new_col_name, order_idx_name=order_idx_name)

        temp = df.set_index(group_col_names, append=True)
        temp = temp.groupby(group_col_names)[col_name].transform(
            lambda x: x.ewm(alpha=alpha, min_periods=min_periods).mean()
            )

        df = self.merge_stat_to_df(
            stat_df=temp, df=df, group_col_names=group_col_names, col_name=col_name, new_col_name=new_col_name,
            n_shift=n_shift
            )

        if original_idx_name is None:
            return df
        return df.set_index(original_idx_name)

    def expanding_sum(self, df, group_col_names, col_name, new_col_name, min_periods=1, n_shift=1,
                      order_idx_name='DATE'):
        df, original_idx_name = self.prepare_df(df, new_col_name=new_col_name, order_idx_name=order_idx_name)

        temp = df.groupby(group_col_names)[col_name].expanding(min_periods=min_periods).sum()

        df = self.merge_stat_to_df(
            stat_df=temp, df=df, group_col_names=group_col_names, col_name=col_name, new_col_name=new_col_name,
            n_shift=n_shift
            )

        if original_idx_name is None:
            return df
        return df.set_index(original_idx_name)

    def rolling_mean(self, df, group_col_names, col_name, new_col_name, n_rolling, min_periods=None, n_shift=1,
                     order_idx_name='DATE'):
        min_periods = min_periods or n_rolling
        df, original_idx_name = self.prepare_df(df, new_col_name=new_col_name, order_idx_name=order_idx_name)

        min_periods = max(min_periods, n_rolling)
        temp = df.groupby(group_col_names)[col_name].rolling(window=n_rolling, min_periods=min_periods).mean()

        df = self.merge_stat_to_df(
            stat_df=temp, df=df, group_col_names=group_col_names, col_name=col_name, new_col_name=new_col_name,
            n_shift=n_shift
            )

        if original_idx_name is None:
            return df
        return df.set_index(original_idx_name)

    def rolling_weighted_mean(self, df, group_col_names, col_name, weight_col_name, new_col_name, n_rolling,
                              min_periods=None, n_shift=1, order_idx_name='DATE'):
        min_periods = min_periods or n_rolling
        df, original_idx_name = self.prepare_df(df, new_col_name=new_col_name, order_idx_name=order_idx_name)

        min_periods = max(min_periods, n_rolling)
        df['weighted_col'] = df[col_name] * df[weight_col_name]
        temp = df.groupby(group_col_names)
        temp = temp['weighted_col'].rolling(window=n_rolling, min_periods=min_periods).sum() / \
            temp[weight_col_name].rolling(n_rolling, min_periods=min_periods).sum()
        temp = temp.rename(col_name)
        df = df.drop(columns='weighted_col')

        df = self.merge_stat_to_df(
            stat_df=temp, df=df, group_col_names=group_col_names, col_name=col_name, new_col_name=new_col_name,
            n_shift=n_shift
            )

        if original_idx_name is None:
            return df
        return df.set_index(original_idx_name)

    def lag(self, df, group_col_names, col_name, new_col_name, n_shift=1, order_idx_name='DATE'):
        df, original_idx_name = self.prepare_df(df, new_col_name=new_col_name, order_idx_name=order_idx_name)

        temp = df.set_index(group_col_names, append=True)[col_name]

        df = self.merge_stat_to_df(
            stat_df=temp, df=df, group_col_names=group_col_names, col_name=col_name, new_col_name=new_col_name,
            n_shift=n_shift
            )

        if original_idx_name is None:
            return df
        return df.set_index(original_idx_name)

    def expanding_standard_deviation(self, df, group_col_names, col_name, new_col_name, min_periods=1,
                                     n_shift=1, order_idx_name='DATE'):
        df, original_idx_name = self.prepare_df(df, new_col_name=new_col_name, order_idx_name=order_idx_name)

        temp = df.groupby(group_col_names)[col_name].expanding(min_periods=min_periods).std()

        df = self.merge_stat_to_df(
            stat_df=temp, df=df, group_col_names=group_col_names, col_name=col_name, new_col_name=new_col_name,
            n_shift=n_shift
            )

        if original_idx_name is None:
            return df
        return df.set_index(original_idx_name)
