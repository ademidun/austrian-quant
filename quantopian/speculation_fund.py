"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from collections import Counter
import numpy as np

def initialize(context):
    """
    Called once at the start of the algorithm.
    """   
    

    context.stocks = symbols('XLY',  # XLY Consumer Discrectionary SPDR Fund   
                           'XLF',  # XLF Financial SPDR Fund  
                           'XLK',  # XLK Technology SPDR Fund  
                           'XLE',  # XLE Energy SPDR Fund  
                           'XLV',  # XLV Health Care SPRD Fund  
                           'XLI',  # XLI Industrial SPDR Fund  
                           'XLP',  # XLP Consumer Staples SPDR Fund   
                           'XLB',  # XLB Materials SPDR Fund  
                           'XLU')  # XLU Utilities SPRD Fund
    
    context.historical_bars = 100
    context.feature_window = 10

    # Rebalance every day, 1 hour after market open.
    schedule_function(execute_trade, date_rules.every_day(), time_rules.market_open(hours=1))
     
    schedule_function(monthly_review, date_rules.week_start(), time_rules.market_open(hours=1))

def execute_trade(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    prices = data.history(assets = context.stocks, bar_count = context.historical_bars, frequency='1d', fields='price')


    for stock in context.stocks:   
        
        try:

            price_hist = data.history(stock, 'price', 50, '1d')
            ma1 = price_hist.mean()
            price_hist = data.history(stock, 'price', 200, '1d')
            ma2 = price_hist.mean()
            
            start_bar = context.feature_window
            price_list = prices[stock].tolist()
            
            X = [] # list of feature sets
            y = [] # list of labels, one for each feature set
            
            bar = start_bar
            
            # feature creation
            while bar < len(price_list)-1:
                try:

                    end_price = price_list[bar+1] # "tomorrow"'s price'
                    begin_price = price_list[bar] # today's price
                    
                    pricing_list = []
                    xx = 0
                    for _ in range(context.feature_window):
                        price = price_list[bar-(context.feature_window-xx)]
                        pricing_list.append(price)
                        xx += 1
                    
                    # get the % change in daily prices of last 10 days
                    features = np.around(np.diff(pricing_list) / pricing_list[:-1] * 100.0, 1)
                    
                    # if tomorrow's price is more than today's price
                    # label the feature set (% change in last 10 days)
                    # a 1 (strong outlook, buy) else -1 (weak outlook, sell)
                    if end_price > begin_price:
                        label = 1
                    else:
                        label = -1

                    bar += 1
                    X.append(features)
                    y.append(label)
                    # print(features)

                except Exception as e:
                    bar += 1
                    print(('feature creation',str(e)))


            clf1 = RandomForestClassifier()
            clf2 = LinearSVC()
            clf3 = NuSVC()
            clf4 = LogisticRegression()

            # now we get the prices and features for the last 10 days
            last_prices = price_list[-context.feature_window:]
            current_features = np.around(np.diff(last_prices) / last_prices[:-1] * 100.0, 1)

            # append the last 10 days feature set
            # scale the data (mean becomes zero, SD = 0), necessary for ML algo to work
            X.append(current_features)
            X = preprocessing.scale(X)

            # the current feature will be the last SCALED feature set
            # X will be all the feature sets, excluding the most recent one,
            # this is the feature set which we will be using to predict
            current_features = X[-1]
            X = X[:-1]

            # this is where the magic happens:
                # we will be training our algorithm here to see the correlation between
                # the features and the labels (this feature set, was a buy etc.)
                # the Most CPU intensive part of the program 
                # sklearn documentation says it time complexity is quadratic to number of samples
                # this means it is difficult to scale to a large dataset > a couple 10,000 samples
                # Bonus: How the documentation describes this function: Build a forest of trees from the training set (X, y).
            # we can also provide a sample_weight, if some samples are more important than others
            clf1.fit(X,y)
            clf2.fit(X,y)
            clf3.fit(X,y)
            clf4.fit(X,y)

            # then based on the RandomForestClassifier we predict what our current
                # feature set should be labelled: (1 (buy) or 0 (sell), [0] is the index of the actual predection
                # returns an array of labels based on the  n samples
            p1 = clf1.predict(current_features)[0]
            p2 = clf2.predict(current_features)[0]
            p3 = clf3.predict(current_features)[0]
            p4 = clf4.predict(current_features)[0]

            # Counter('abracadabra').most_common(3)
            #   >>[('a', 5), ('r', 2), ('b', 2)]
            # if all the classifiers agree on the same prediction we will either buy or sell the stock
            #if there is no consensus, we do nothing

            if Counter([p1,p2,p3,p4]).most_common(1)[0][1] >= 4:
                p = Counter([p1,p2,p3,p4]).most_common(1)[0][0]
           
            else:
                p = 0

            print(('ma1_d: ',ma1))
            print(('ma2_d :',ma2))
            print(('p1 :',p1))
            print(('p2 :',p2))
            print(('p3 :',p3))
            print(('p4 :',p4))
            print(('Prediction',p))

            # Based on the voted prediction and the momentum of the moving averages
            if p == 1 and ma1 > ma2:
                    order_target_percent(stock,0.11)
            elif p == -1 and ma1 < ma2:
                order_target_percent(stock,-0.11)
            # alternatively we could just do:
            # order_target_percent(stock,(p*0.11))

        except Exception as e:
            print(str(e))
                      
    record('ma1',ma1)
    record('ma2',ma2)
    record('Leverage',context.account.leverage)

def monthly_review(context, data):
    price_hist = data.history(context.stocks, 'price', 50, '1d')
    ma1 = price_hist.mean()
    price_hist = data.history(context.stocks, 'price', 200, '1d')
    ma2 = price_hist.mean()
    print(('ma1',str(ma1)))
    print(('ma2',str(ma2)))
