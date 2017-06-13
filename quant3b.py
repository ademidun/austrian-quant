import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from sklearn import svm, preprocessing
import pandas as pd
from matplotlib import style
import statistics
from my_utils import FEATURES

style.use("ggplot")

def build_data_set():
    data_df = pd.DataFrame.from_csv("key_stats_acc_perf_NO_NA.csv")

    data_df = data_df.reindex(np.random.permutation(data_df.index))
    data_df = data_df.replace("NaN", 0).replace("N/A", 0)

    X = np.array(data_df[FEATURES].values)#.tolist()

    y = (data_df["Status"]
         .replace("underperform", 0)
         .replace("outperform", 1)
         .values.tolist())

    X = preprocessing.scale(X)

    z = np.array(data_df[["stock_p_change", "sp500_p_change"]])

    return X, y, z

def analysis():
    test_size = 400

    invest_amount = 1000
    total_invests = 0
    if_market = 0
    if_strat = 0

    X, y, Z = build_data_set()
    print(len(X))

    clf = svm.SVC(kernel="linear", C=1.0) # create a new classifer
    clf.fit(X[:-test_size], y[:-test_size]) # create a model for my classifier based on the feature set and labels, 'supervision

    correct_count = 0

    for x in range(1, test_size + 1):
        if clf.predict(X[-x])[0] == y[-x]:
            correct_count += 1

        if clf.predict(X[-x])[0] == 1:
            invest_return = invest_amount + (invest_amount * (Z[-x][0] / 100))
            market_return = invest_amount + (invest_amount * (Z[-x][1] / 100))
            total_invests += 1
            if_market += market_return
            if_strat += invest_return

    data_df = pd.DataFrame.from_csv("forward_sample_WITH_NA.csv")

    data_df = data_df.replace("N/A", 0).replace("NaN", 0)

    X = np.array(data_df[FEATURES].values)

    X = preprocessing.scale(X)

    Z = data_df["Ticker"].values.tolist()

    invest_list = []

    for i in range(len(X)):
        p = clf.predict(X[i])[0]
        if p == 1:
            print(Z[i])
            invest_list.append(Z[i])

    print(len(invest_list))
    print(invest_list)

analysis()