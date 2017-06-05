import pandas as pd
import os
import time
from datetime import datetime

path = "/Users/tomiwa/Downloads/intraQuarter"

'''
Each directory in keystats is a stock ticker.
Each stock ticker, has files with date time filename 
in the format %Y%m%d%H%M%S.html' indicating when 
the data was pulled
We want to convert those file names into unix time stamps
'''
def Key_Stats(gather="Total Debt/Equity (mrq)"):
    statspath = path+'/_KeyStats'
    print(os.walk(statspath))
    stock_list = [x[0] for x in os.walk(statspath)]
    print(stock_list)

    for each_dir in stock_list[1:]:
        each_file = os.listdir(each_dir)
        ticker = each_dir.split("/")[1]
        if len(each_file) > 0:
            for file in each_file:
                date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
                unix_time = time.mktime(date_stamp.timetuple())
                print(date_stamp, unix_time)
                # time.sleep(15)