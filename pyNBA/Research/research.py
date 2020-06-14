from scipy.stats import pearsonr
import ppscore as pps
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class Helpers(object):
    def __init__(self):
        pass

    '''
    Recognize whether a column is numerical or categorical.
    '''
    def utils_recognize_type(self, df, col, max_cat=12):
        if (df[col].dtype == "O") | (df[col].nunique() < max_cat):
            return "x"
        else:
            return "y"

    def visualize_dataframe(self, df, max_cat=12):
        dic_cols = {col:self.utils_recognize_type(df, col, max_cat=max_cat) for col in df.columns}
        heatmap = df.isnull()
        for k,v in dic_cols.items():
            if v == "y":
                heatmap[k] = heatmap[k].apply(lambda x: 0.5 if x is False else 1)
            else:
                heatmap[k] = heatmap[k].apply(lambda x: 0 if x is False else 1)
        sns.heatmap(heatmap, cbar=False).set_title('Dataset Overview')
        plt.show()
        print("\033[1;37;40m Categerocial ", "\033[1;30;43m Numeric ", "\033[1;30;47m NaN ")
        print('\nPercentage of rows containing at least one missing value:', 100*round((1 - len(df.dropna())/len(df)), 5))

    def visualize_variable_distribution(self, df, x, log_boxplot=True, figsize=(12, 8)):
        fig, ax = plt.subplots(nrows=1, ncols=2,  sharex=False, sharey=False, figsize=figsize)
        fig.suptitle(x, fontsize=16)

        # distribution
        ax[0].title.set_text('distribution')
        variable = df[x].dropna()
        sns.distplot(variable, hist=True, kde=True, kde_kws={"shade": True}, ax=ax[0])
        des = df[x].describe()
        des['skew'] = df[x].skew()
        ax[0].axvline(des["25%"], ls='--')
        ax[0].axvline(des["mean"], ls='--')
        ax[0].axvline(des["75%"], ls='--')
        ax[0].grid(True)
        des = round(des, 5).apply(lambda x: str(x))
        box = '\n'.join(("min: "+des["min"], "25%: "+des["25%"], "mean: "+des["mean"], "75%: "+des["75%"], "max: "+des["max"], "skew: "+des['skew']))
        ax[0].text(0.95, 0.95, box, transform=ax[0].transAxes, fontsize=10, va='top', ha="right", bbox=dict(boxstyle='round', facecolor='white', alpha=1))

        # boxplot 
        temp_df = pd.DataFrame(df[x])
        if log_boxplot:
            ax[1].title.set_text('outliers (log scale)')
            temp_df[x] = np.log(temp_df[x])
        else:
            ax[1].title.set_text('outliers')
        temp_df.boxplot(column=x, ax=ax[1])
        plt.show()

    def visualize_numeric_x_vs_y(self, df, x, y, figsize=(12, 8)):
        df = df.dropna(subset=[x, y])

        # bin plot
        breaks = np.quantile(df[x], q=np.linspace(0, 1, 11))
        groups = df.groupby([pd.cut(df[x], bins=breaks, 
                duplicates='drop')])[y].agg(['mean','median','size'])
        fig, ax = plt.subplots(figsize=figsize)
        fig.suptitle(x+"   vs   "+y, fontsize=16)
        groups[["mean", "median"]].plot(kind="line", ax=ax)
        groups["size"].plot(kind="bar", ax=ax, rot=45, secondary_y=True,
                            color="grey", alpha=0.3, grid=True)
        ax.set(ylabel=y)
        ax.right_ax.set_ylabel("Observasions in each bin")
        plt.show()

        # scatter plot
        sns.jointplot(x=x, y=y, data=df, dropna=True, kind='reg', 
                    height=int((figsize[0]+figsize[1])/2) )
        plt.show()

    def visualize_categorical_x_vs_y(self, df, x, y, figsize=(16, 6)):
        df = df.dropna(subset=[x, y])

        fig, ax = plt.subplots(nrows=1, ncols=3,  sharex=False, sharey=False, figsize=figsize)
        fig.suptitle(x+"   vs   "+y, fontsize=16)

        # distribution
        ax[0].title.set_text('density')
        for i in df[x].unique():
            sns.distplot(df[df[x]==i][y], hist=False, label=i, ax=ax[0])
        ax[0].grid(True)

        # stacked
        ax[1].title.set_text('bins')
        breaks = np.quantile(df[y], q=np.linspace(0,1,11))
        tmp = df.groupby([x, pd.cut(df[y], breaks, duplicates='drop')]).size().unstack().T
        tmp = tmp[df[x].unique()]
        tmp["tot"] = tmp.sum(axis=1)
        for col in tmp.drop("tot", axis=1).columns:
            tmp[col] = tmp[col] / tmp["tot"]
        tmp.drop("tot", axis=1).plot(kind='bar', stacked=True, ax=ax[1], legend=True, grid=True)

        # boxplot   
        ax[2].title.set_text('outliers')
        sns.boxplot(x=x, y=y, data=df, ax=ax[2])
        ax[2].grid(True)
        plt.show()

    def correlation(self, df, col_1, col_2):
        df = df.dropna(subset=[col_1, col_2])
        r = pearsonr(df[col_1], df[col_2])
        return r

    def predictive_power_score(self, df, feature_col_name, target_col_name):
        df = df.dropna(subset=[feature_col_name, target_col_name])
        p = pps.score(df, feature_col_name, target_col_name)
        return p