import pandas as pd
import urllib.request
import os
import time
from datetime import datetime

from time import mktime
import matplotlib as mpl

mpl.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import style

style.use("dark_background")

import re
from my_utils import my_gather, my_df_cols

path = "/Users/tomiwa/Downloads/intraQuarter"


def check_yahoo():
    statspath = path + "/_KeyStats"

    stock_list = [x[0] for x in os.walk(statspath)]

    for e in stock_list[1:555:5]:
        try:
            e = e.split('/')[-1]
            link = "http://finance.yahoo.com/q/ks?s=" + e.upper() + "+Key+Statistics"
            resp = urllib.request.urlopen(link).read()
            # print("resp: ", resp)

            save = "forward/" + str(e) + ".html"
            store = open(save, "w")
            store.write(str(resp))
            store.close()
            # time.sleep(3)

        except FileNotFoundError as e:
            print("What Happened? ", str(e))
            os.makedirs("forward")
            time.sleep(2)

        except Exception as e:
            print("Uhoh: ", str(e))
            time.sleep(2)


def forward(gather=my_gather):
    df = pd.DataFrame(columns=my_df_cols)

    file_list = os.listdir("forward")

    for each_file in file_list:
        ticker = each_file.split(".html")[0]
        full_file_path = "forward/" + each_file
        source = open(full_file_path, "r").read()

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
                    print("UhOh!: ", str(e))
                    # print("N/A value: ", str(e))

            if value_list.count("N/A") > 15:
                pass

            else:
                df = df.append({'Date': "N/A",
                                'Unix': "N/A",
                                'Ticker': ticker,

                                'Price': "N/A",
                                'stock_p_change': "N/A",
                                'SP500': "N/A",
                                'sp500_p_change': "N/A",
                                'Difference': "N/A",
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
                                'Status': "N/A"},
                               ignore_index=True)

        except Exception as e:
            print("UHOH x2!: ", str(e))
            pass

    df.dropna(axis=1, how="all", inplace=True)
    df.to_csv("forward_sample_WITH_NA.csv")


forward()
