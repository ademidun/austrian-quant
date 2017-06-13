import matplotlib as mpl
import numpy as np
import pandas as pd
from sklearn import preprocessing, svm
# import matplotlib.pyplot as plt

mpl.use('TkAgg')
from matplotlib import style

style.use("ggplot")
from my_utils import FEATURES


def Build_Data(csv_file="key_stats_acc_perf_NO_NA_2.csv", feature_set=FEATURES):

    """
    :param csv_file:
    :param feature_set:
    :return: X = feature set, y = label set, z = % change in stock and sp500
    """
    # Apparently its preferable to do pd.read_csv(csv_file)

    data_df = pd.DataFrame.from_csv(csv_file)
    # shuffle the indices of the df using a random permutation of the df indices

    data_df = data_df.reindex(np.random.permutation(data_df.index))
    data_df = data_df.dropna(subset=["stock_p_change", "sp500_p_change"])
    data_df = data_df.replace("NaN", 0).replace("N/A", 0)

    X = np.array(data_df[feature_set])  # create a feature set from the dataframe
    y = (data_df["Status"]
         .replace("underperform", 0)
         .replace("outperform", 1)
         .values.tolist())  # convert the status column into a label list

    X = preprocessing.scale(X)  # normalize the feature set

    # how to generate a numpy array w/ 2 columns
    z = np.array(data_df[["stock_p_change","sp500_p_change"]])
    return X, y, z  # return the feature set and the corresponding label, and the results;


def Build_Data_Set_No_Result(csv_file="key_stats_acc_perf_NO_NA_2.csv", feature_set=FEATURES):
    # Apparently its preferable to do pd.read_csv(csv_file)

    data_df = pd.DataFrame.from_csv(csv_file)
    # shuffle the indices of the df using a random permutation of the df indices

    data_df = data_df.reindex(np.random.permutation(data_df.index))
    data_df = data_df.replace("NaN", 0).replace("N/A", 0)
    X = data_df[feature_set]
    print ('X.head(): ',X.head())
    X = np.array(X)  # create a feature set from the dataframe
    y = (data_df["Status"]
         .replace("underperform", 0)
         .replace("outperform", 1)
         .values.tolist())  # convert the status column into a label list
    X = preprocessing.scale(X)  # normalize the feature set

    return X, y  # return the feature set and the coreesponding label;


def Analysis():

    test_size = 400

    invest_amount = 1000
    total_invests = 0
    if_market = 0
    if_strat = 0

    X, y, z = Build_Data()
    print(len(X))

    clf = svm.SVC(kernel="linear", C=1.0)
    clf.fit(X[:-test_size],y[:-test_size])

    correct_count = 0

    for i in range(1,test_size+1):
        clf_prediction = clf.predict(X[-i])[0]
        if clf_prediction == y[-i]:
            correct_count +=1

        if clf_prediction == 1: # if we predict the stock will outperform
            invest_return = invest_amount + (invest_amount * (z[-i][0]/100))
            market_return = invest_amount + (invest_amount * (z[-i][1]/100))
            total_invests += 1
            if_market += market_return
            if_strat += invest_return

    print("Accuracy: %", (correct_count/test_size) * 100.0)

    print("Total Trades: ", total_invests)
    print("Ending with Strategy: ", if_strat)
    print("Ending: ", if_market)

    compared = ( (if_strat - if_market) / if_market ) * 100.0
    do_nothing  = total_invests * invest_amount

    avg_market = ( (if_market - do_nothing) / do_nothing) * 100.0
    avg_strat = ( ( if_strat - do_nothing) / do_nothing) * 100.0

    print("Compared to market we earn", str(compared) + "% more.")
    print("Average investment return:", str(avg_strat) + "%")
    print("Average market return", str(avg_market) + "%")


def Analysis2():

    test_size = 450
    X, y = Build_Data_Set_No_Result()
    print(len(X))


    # Now we want to make a classifier based on our normalized feature set
    # and numerical labels
    clf = svm.SVC(kernel="linear", C=1.0)
    clf.fit(X[:-test_size],y[:-test_size])

    correct_count = 0

    for i in range(1, test_size+1):
        if clf.predict(np.array([X[-i]]))[0] == y[-i]:
            correct_count +=1

    print("Accuracy: %",(correct_count/test_size)*100.00)


Analysis()

