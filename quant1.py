import time
from datetime import datetime
from time import mktime

import matplotlib as mpl
import re

mpl.use('TkAgg')
import matplotlib.pyplot as plt
import os
import pandas as pd
from matplotlib import style
from my_utils import my_gather, my_df_cols, FEATURES
from my_keys import quandl_api_key
import numpy as np
from sklearn import svm, preprocessing
import quandl
style.use("ggplot")

style.use('dark_background')

path = "/Users/tomiwa/Downloads/intraQuarter"

quandl.ApiConfig.api_key = quandl_api_key

data = quandl.Dataset("WIKI/KO" ).data(params={ 'start_date':'2001-12-01', 'end_date':'2010-12-30'})

def Key_Stats(gather=my_gather):
    statspath = path + '/_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)]
    df = pd.DataFrame(columns=my_df_cols)
    sp500_df = pd.DataFrame.from_csv("YAHOO-INDEX_GSPC.csv")

    stock_list = stock_list[1:550:7]
    print('stock_list: ', stock_list)
    time.sleep(5)

    ticker_list = []
    counter = 0
    for each_dir in stock_list:  # first 25 elements (1-50 skip 2)
        quarterly_files = os.listdir(each_dir)
        ticker = each_dir.split("/")[-1]
        ticker_list.append(ticker)
        # print('ticker: ', ticker)
        starting_stock_value = False
        starting_sp500_value = False
        if counter == 5:
            print('ticker check: ', ticker)
            counter = 0
        if len(quarterly_files) > 0:
            for file in quarterly_files:
                date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
                unix_time = mktime(date_stamp.timetuple())
                full_file_path = each_dir + '/' + file
                # print('full_file_path: ', full_file_path)
                source = open(full_file_path, 'r').read()
                # Now we take the entire html page and look for Total Debt/Equity (mrq)
                # :</td><td class="yfnc_tabledata1">
                try:
                    value_list = []

                    for each_data in gather:
                        try:
                            regex = re.escape(each_data) + r'.*?(\d{1,8}\.\d{1,8}M?B?|N/A)%?</td>'
                            value = re.search(regex, source)
                            value = (value.group(1))

                            if "B" in value:
                                value = float(value.replace("B", '')) * 1000000000

                            elif "M" in value:
                                value = float(value.replace("M", '')) * 1000000

                            value_list.append(value)

                        except Exception as e:
                            value = "N/A"
                            value_list.append(value)

                    # get the row date for the current stock
                    try:
                        sp500_date = datetime.fromtimestamp(unix_time).strftime('%y-%m-%d')
                        # find the row where the index equals the sp500_date
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        # the value we want is in that row in the 'Close' column
                        sp500_value = float(row["Close"])

                    except:
                        sp500_date = datetime.fromtimestamp(unix_time - 259200).strftime('%Y-%m-%d')
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        sp500_value = float(row["Close"])

                    try:
                        stock_price = float(source.split('</small><big><b>')[1].split('</b></big>')[0])
                        # stock_price = re.search(r'(\d{1,8}\.\d{1,8})', stock_price)
                        # stock_price = float(stock_price.group(1))
                    except Exception as e:
                        #    <span id="yfs_l10_afl">43.27</span>
                        try:
                            stock_price = (source.split('</small><big><b>')[1].split('</b></big>')[0])
                            stock_price = re.search(r'(\d{1,8}\.\d{1,8})', stock_price)
                            stock_price = float(stock_price.group(1))

                            # print(stock_price)
                        except Exception as e:
                            try:
                                stock_price = (source.split('<span class="time_rtq_ticker">')[1].split('</span>')[0])
                                stock_price = re.search(r'(\d{1,8}\.\d{1,8})', stock_price)
                                stock_price = float(stock_price.group(1))
                            except Exception as e:
                                print(str(e), 'a;lsdkfh', file, ticker)

                                # print('Latest:',stock_price)

                                # print('stock price',str(e),ticker,file)
                                # time.sleep(15)

                    if not starting_stock_value:
                        starting_stock_value = stock_price

                    if not starting_sp500_value:
                        starting_sp500_value = sp500_value

                    stock_p_change = ((stock_price - starting_stock_value) / starting_stock_value) * 100
                    sp500_p_change = ((sp500_value - starting_sp500_value) / starting_sp500_value) * 100

                    location = len(df['Date'])

                    difference = stock_p_change - sp500_p_change

                    if difference > 0:
                        status = "outperform"
                    else:
                        status = "underperform"

                    if value_list.count("N/A") > 0:
                        pass

                    else:

                        df = df.append({'Date': date_stamp,
                                        'Unix': unix_time,
                                        'Ticker': ticker,

                                        'Price': stock_price,
                                        'stock_p_change': stock_p_change,
                                        'SP500': sp500_value,
                                        'sp500_p_change': sp500_p_change,
                                        'Difference': difference,
                                        'DE Ratio': value_list[0],
                                        # 'Market Cap':value_list[1],
                                        'Trailing P/E': value_list[1],
                                        'Price/Sales': value_list[2],
                                        'Price/Book': value_list[3],
                                        'Profit Margin': value_list[4],
                                        'Operating Margin': value_list[5],
                                        'Return on Assets': value_list[6],
                                        'Return on Equity': value_list[7],
                                        'Revenue Per Share': value_list[8],
                                        'Market Cap': value_list[9],
                                        'Enterprise Value': value_list[10],
                                        'Forward P/E': value_list[11],
                                        'PEG Ratio': value_list[12],
                                        'Enterprise Value/Revenue': value_list[13],
                                        'Enterprise Value/EBITDA': value_list[14],
                                        'Revenue': value_list[15],
                                        'Gross Profit': value_list[16],
                                        'EBITDA': value_list[17],
                                        'Net Income Avl to Common ': value_list[18],
                                        'Diluted EPS': value_list[19],
                                        'Earnings Growth': value_list[20],
                                        'Revenue Growth': value_list[21],
                                        'Total Cash': value_list[22],
                                        'Total Cash Per Share': value_list[23],
                                        'Total Debt': value_list[24],
                                        'Current Ratio': value_list[25],
                                        'Book Value Per Share': value_list[26],
                                        'Cash Flow': value_list[27],
                                        'Beta': value_list[28],
                                        'Held by Insiders': value_list[29],
                                        'Held by Institutions': value_list[30],
                                        'Shares Short (as of': value_list[31],
                                        'Short Ratio': value_list[32],
                                        'Short % of Float': value_list[33],
                                        'Shares Short (prior ': value_list[34],
                                        'Status': status},
                                       ignore_index=True)


                except Exception as e:
                    pass
        counter += 1

    for each_ticker in ticker_list:
        try:
            plot_df = df[(df['Ticker'] == each_ticker)]

            plot_df = plot_df.set_index(['Date'])

            if plot_df['Status'][-1] == 'underperform':
                color = 'r'
            else:
                color = 'g'

            plot_df['Difference'].plot(label=each_ticker, color=color)
            plt.legend()
        except Exception as e:
            print(str(e))

    plt.show()
    df.to_csv("key_stats_jun7.csv")
    # time.sleep(1)


def Build_Data_Set():
    ''' Convert a csv to a df with features and labels for ML training.'''
    data_df = pd.DataFrame.from_csv("key_stats.csv")

    # data_df = data_df[:100]
    data_df = Randomizing(data_df)
    X = np.array(data_df[FEATURES].values)

    y = (data_df["Status"]
         .replace("underperform", 0)
         .replace("outperform", 1)
         .values.tolist())
    X = preprocessing.scale(X)

    return X, y


def Analysis():
    test_size = 330

    X, y = Build_Data_Set()
    print('len(X): ', len(X))

    clf = svm.SVC(kernel='linear', C=1.0)
    clf.fit(X[:-test_size], y[:-test_size])

    correct_count = 0

    for x in range(1, test_size + 1):
        if y[-x] == clf.predict(X[-x])[0]:
            correct_count += 1
    print('Accuracy: %', (correct_count / test_size) * 100.0)

def Randomizing(df):
    df2 = df.reindex(np.random.permutation(df.index))
    return df2

data_df = pd.DataFrame.from_csv("key_stats.csv")
Randomizing(data_df)


def Analysis2():
    X, y = Build_Data_Set()

    clf = svm.SVC(kernel='linear', C=1.0)
    clf.fit(X, y)

    w = clf.coef_[0]
    a = -w[0] / w[1]
    xx = np.linspace(min(X[:, 0]), max(X[:, 0]))
    yy = a * xx - clf.intercept_[0] / w[1]

    h0 = plt.plot(xx, yy, "k-", label="non weighted")

    plt.scatter(X[:, 0], X[:, 1], c=y)
    plt.ylabel("Trailing P/E")
    plt.xlabel("DE Ratio")
    plt.legend()

    plt.show()


def debug_run():
    gather = "Total Debt/Equity (mrq)"

    statspath = path + '/_KeyStats'
    print(os.walk(statspath))
    # x is a tuple so foreach element x in os.walk(),
    # take the first tuple element
    stock_list = [x[0] for x in os.walk(statspath)]
    print('stock_list: ', stock_list)

    # file structure
    # /Users/tomiwa/Downloads/intraQuarter
    # |_ KeyStats
    #     |_ aapl
    #         |_ 20040130190102.html
    for each_dir in stock_list[1:]:
        each_file = os.listdir(each_dir)
        ticker = each_dir.split("/")[1]
        if len(each_file) > 0:
            for file in each_file:
                date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
                unix_time = time.mktime(date_stamp.timetuple())
                print(date_stamp, unix_time)
                full_file_path = each_dir + '/' + file
                print('full_file_path: ', full_file_path)
                source = open(full_file_path, 'r').read()
                print('source: ', source)
                value = source.split(gather + ':</td><td class="yfnc_tabledata1">')[1].split('</td>')[0]
                print(ticker + ":", value)
                time.sleep(15)

'''
Each directory in keystats is a stock ticker.
Each stock ticker, has files with date time filename 
in the format %Y%m%d%H%M%S.html' indicating when 
the data was pulled
We want to convert those file names into unix time stamps.

This function is useful for teaching how to scrape data from a webpage
'''

'''
1. Go through the HTMl of each stock at quarterly intervals and get their DE Ratio
2. Get the s&p500 index csv, conver it to a datafram and match up the stock price on that day
3. With the share price and DE Ratio for that stock on the given day
'''
Key_Stats()
