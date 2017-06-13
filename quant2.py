import time
from datetime import datetime

import matplotlib as mpl

mpl.use('TkAgg')
import os
import pandas as pd
from matplotlib import style
from my_utils import my_gather, my_df_cols_1y
from my_keys import quandl_api_key
import quandl
import re

style.use("ggplot")

style.use('dark_background')

path = "/Users/tomiwa/Downloads/intraQuarter"


def init_quandl():
    quandl.ApiConfig.api_key = quandl_api_key

    data = quandl.Dataset("WIKI/KO").data(params={'start_date': '2001-12-01', 'end_date': '2010-12-30'})


def Key_Stats(gather=my_gather):
    """
     Key_Stats is different from Stock_Prices() because in the latter function,
    we are appending columns to a dataframe based on what we pulled from the Quandl API.
    While with the Key_Stats function, we are initializing our dataframe with the columns we want
     and mapping that to the columns returned by quandl.Dataset.data
    :param gather:
    :return:
    """

    statspath = path + '/_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)]
    stock_list = stock_list[1:]
    df = pd.DataFrame(columns=my_df_cols_1y)

    sp500_df = pd.DataFrame.from_csv("YAHOO-INDEX_GSPC.csv")
    stock_df = pd.DataFrame.from_csv("stock_prices_big.csv")

    ticker_list = []
    for each_dir in stock_list:  # show the first 550 stocks, skipping every 15
        each_file = os.listdir(each_dir)  # each_dir is a list of quarterly earnings for particular stock
        ticker = each_dir.split('/')[-1]
        ticker_list.append(ticker)

        if len(each_file) > 0:
            for file in each_file:  # file represents a different quarterly filing for that stock
                date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
                unix_time = time.mktime(date_stamp.timetuple())
                full_file_path = each_dir + '/' + file
                # display the .html webpage of where the quarterly stock webpage is
                source = open(full_file_path, 'r').read()
                try:
                    value_list = []

                    for each_data in gather:  # for each metric recorded that quarter
                        try:
                            # this regex searches for the metric string and first digits after it
                            # print("each_data(1): ", each_data)
                            regex = re.escape(each_data) + r'.*?(\d{1,8}\.\d{1,8}M?B?|N/A)%?'
                            value = re.search(regex, source)
                            value = (value.group(1))
                            # print("regex(1): ",regex)
                            # print("value(1): ",value)
                            #
                            # print("value(2): ", value)
                            if "B" in value:
                                value = float(value.replace('B', '')) * 1000000000

                            elif "M" in value:
                                value = float(value.replace("M", '')) * 1000000

                            value_list.append(value)
                            # print("value(3): ", value)
                        except Exception as e:
                            value = "N/A"
                            value_list.append(value)
                            # print("N/A value: ", str(e))

                    try:  # find the date of that file,  get the stock price at that date
                        sp500_date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d')
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        sp500_value = float(row["Close"])

                    except:
                        try:
                            # -259200 means in your local timezone
                            sp500_date = datetime.fromtimestamp(unix_time - 259200).strftime('%Y-%m-%d')
                            row = sp500_df[(sp500_df.index == sp500_date)]
                            sp500_value = float(row["Close"])

                        except Exception as e:
                            print("fapsdolkfhasf;lsak", str(e))



                    try:
                        one_year_later = unix_time + 31536000
                        # print("one_year_later: ", one_year_later)
                        sp500_1y = datetime.fromtimestamp(one_year_later).strftime('%Y-%m-%d') #notice the lowercase v uppercase m
                        # print("sp500_1y: ", sp500_1y)
                        row = sp500_df[(sp500_df.index == sp500_1y)]
                        # print("row[\"Close\"]: ", row["Close"])
                        sp500_1y_value = float(row["Close"])  # Changed from Adjusted Close to Close

                    except:
                        try:
                            sp500_1y = datetime.fromtimestamp(one_year_later - 259200).strftime('%Y-%m-%d')
                            row = sp500_df[(sp500_df.index == sp500_1y)]
                            ## print("row[\"Close\"](2): ", row["Close"])
                            sp500_1y_value = float(row["Close"])
                        except Exception as e:
                            # print("sp500 1 year later issue", str(e))
                            pass

                    try:
                        stock_price_1y = datetime.fromtimestamp(one_year_later).strftime('%Y-%m-%d')
                        row = stock_df[(stock_df.index == stock_price_1y)][ticker.upper()]

                        stock_1y_value = round(float(row), 2)
                        ## print(stock_1y_value)
                        ## time.sleep(1555)

                    except Exception as e:
                        try:
                            stock_price_1y = datetime.fromtimestamp(one_year_later - 259200).strftime('%Y-%m-%d')
                            row = stock_df[(stock_df.index == stock_price_1y)][ticker.upper()]
                            stock_1y_value = round(float(row), 2)
                        except Exception as e:
                            try:
                                stock_price_1y = datetime.fromtimestamp(one_year_later - 259200).strftime('%Y-%m-%d')
                                row = stock_df[(stock_df.index == stock_price_1y)][ticker.upper()]
                                stock_1y_value = round(float(row), 2)
                            except Exception as e:
                                print("stock price (1): ", str(e))

                    try:
                        stock_price = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d')
                        row = stock_df[(stock_df.index == stock_price)][ticker.upper()]
                        stock_price = round(float(row), 2)

                    except Exception as e:
                        try:
                            stock_price = datetime.fromtimestamp(unix_time - 259200).strftime('%Y-%m-%d')
                            row = stock_df[(stock_df.index == stock_price)][ticker.upper()]
                            stock_price = round(float(row), 2)
                        except Exception as e:
                            print("stock price (2): ", str(e))

                    # Now we try and see label our feature set based on performance since last year
                    if not sp500_1y_value:
                        print("There is no (sp500_1y_value):", sp500_1y_value)
                        sp500_1y_value = sp500_value

                    if not stock_1y_value:
                        print("There is no (stock_1y_value):", stock_1y_value)
                        stock_1y_value = stock_price
                    try:
                        stock_p_change = round((((stock_1y_value - stock_price) / stock_price) * 100), 2)
                        sp500_p_change = round((((sp500_1y_value - sp500_value) / sp500_value) * 100), 2)

                    except Exception as e:
                        stock_1y_value = stock_price
                        print("baweflsak", str(e))

                    difference = stock_p_change - sp500_p_change

                    if difference > 0:
                        status = "outperform"
                    else:
                        status = "underperform"

                    if value_list.count("N/A") > 0:
                        pass

                    else:
                        try: # we could have normalized the data before putting in a dataframe
                            df = df.append({'Date': date_stamp,
                                        'Unix': unix_time,
                                        'Ticker': ticker,
                                        'Price': stock_price,
                                        'Price_1y': stock_1y_value,
                                        'stock_p_change': stock_p_change,
                                        'SP500': sp500_value,
                                        'SP500_1y': sp500_1y_value,
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
                            print("bouffdaddy: ", str(e))


                except Exception as e:
                    print("blahmhasf;lsak", str(e))

    df.to_csv("key_stats_acc_perf_NO_NA_2.csv")

Key_Stats()


def Stock_Prices():
    df = pd.DataFrame()
    statspath = path + '/_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)]

    stock_list = stock_list[1:550:25]
    print(stock_list[:20])

    for each_dir in stock_list[1:]:
        try:
            ticker = each_dir.split('/')[-1]
            name = "WIKI/" + ticker.upper()
            data = quandl.Dataset(name) \
                .data(params={'start_date': '2001-12-01', 'end_date': '2010-12-30'})
            data = data.to_pandas()
            data[ticker.upper()] = data["Adj. Close"]
            df = pd.concat([df, data[ticker.upper()]], axis=1)

        except Exception as e:
            print(str(e))
            time.sleep(10)

    print("df[:10] ", df[:10])
    df.to_csv("stock_prices.csv")



