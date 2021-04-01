from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class Cluster(object):
    def __init__(self, df, cluster_cols):
        self.df = df[cluster_cols]

    def create_kmeans_clusters(self, n_clusters, normalize=True):
        if normalize:
            data = StandardScaler().fit_transform(self.df)
        else:
            data = self.df._get_numeric_data()

        k_means = KMeans(n_clusters=n_clusters)
        k_means.fit(data)
        clusters = k_means.labels_
        dists = (k_means.transform(data)**2).sum(axis=1).round(2)
        return pd.DataFrame({'CLUSTER': clusters, 'CENTROID_DISTANCE': dists}, index=self.df.index)

        c = 'adnbansodabsfiubgfolibsaefiglbEI;UFHGoe;fhoewQHFqwfhfjkabsflajsbfoasbfiasbfkasbflajsbfljsabflanslfhajsl;fhlasfhlkahflakhflakhsflakhsflahsflkahsf'


class Evaluate(object):
    def __init__(self, df, cluster_cols):
        self.df = df[cluster_cols]

    def compute_gap_statistic(self, data, n_refs=20, max_n_clusters=12):
        gaps = np.zeros((len(range(1, max_n_clusters+1)),))
        results_df = pd.DataFrame({'k': [], 'gap': []})

        for gap_index, k in enumerate(range(1, max_n_clusters+1)):
            ref_disps = np.zeros(n_refs)

            for i in range(n_refs):
                km = KMeans(k)
                km.fit(data)

                ref_disp = km.inertia_
                ref_disps[i] = ref_disp

            k_means = KMeans(k)
            k_means.fit(data)

            orig_disp = km.inertia_

            gap = np.log(np.mean(ref_disps)) - np.log(orig_disp)

            gaps[gap_index] = gap

            results_df = results_df.append({'k': k, 'gap': gap}, ignore_index=True)

        return (gaps.argmax() + 1, results_df)

    def optimal_kmeans_n_clusters(self, max_n_clusters=15, normalize=True, plot=True):
        if normalize:
            data = StandardScaler().fit_transform(self.df)
        else:
            data = self.df._get_numeric_data()

        optimal_k, gap_df = self.compute_gap_statistic(data=data, max_n_clusters=max_n_clusters)

        if plot:
            sum_of_squared_distances = []
            k_list = range(1, max_n_clusters)
            for k in k_list:
                k_means = KMeans(n_clusters=k)
                k_means.fit(data)
                sum_of_squared_distances.append(k_means.inertia_)

            _, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

            ax1.plot(k_list, sum_of_squared_distances)
            ax2.plot(gap_df.k, gap_df.gap)
            plt.show()
            plt.close()

        return optimal_k

    def visualize_clusters(self, df, cluster_cols, n_clusters):
        plt.figure(figsize=(28, 16))
        cluster = Cluster(df=df, cluster_cols=cluster_cols)
        clusters = cluster.create_kmeans_clusters(n_clusters=n_clusters)
        df = df.merge(clusters, left_index=True, right_index=True, how='left')

        data = StandardScaler().fit_transform(df[cluster_cols])
        pca = PCA(n_components=2)
        pca.fit(data)
        scores = pca.transform(data)
        df['C1'] = scores[:, 0]
        df['C2'] = scores[:, 1]

        df['CENTER_POINT'] = 0
        for c, temp in df.groupby('CLUSTER'):
            thresh = temp['CENTROID_DISTANCE'].quantile(0.05)
            df.loc[(df['CLUSTER'] == c) & (df['CENTROID_DISTANCE'] <= thresh), 'CENTER_POINT'] = 1

        sns.scatterplot(df['C1'], df['C2'], hue=df['CLUSTER'], palette="Set1", s=60)

        for x, y, name, is_center_point, pts in zip(df['C1'], df['C2'], df.index, df['CENTER_POINT'], df['PTS']):
            if is_center_point or pts > 16:
                label = name
                plt.annotate(label, (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=13)

        plt.show()
        plt.close()
