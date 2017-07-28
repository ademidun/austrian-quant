import numpy as np
import scipy

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from collections import Counter

from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import SimpleMovingAverage


# https://www.quantopian.com/posts/risk-parity-slash-slash-all-weather-portfolio

def initialize(context):
    # Initialize Permanent Portfolio
    schedule_function(func=perm_portfolio, date_rule=date_rules.week_start(days_offset=0),
                      time_rule=time_rules.market_open(hours=1, minutes=1))
    schedule_function(func=perm_portfolio, date_rule=date_rules.week_start(days_offset=3),
                      time_rule=time_rules.market_open(hours=1, minutes=1))

    context.stocks = [sid(8554),  # SPY - Stocks
                      sid(23921),  # TLT - Bonds
                      sid(26807),  # GLD - Gold
                      sid(23911)]  # Shy - Cash (1-3yr treasury bonds tbh)

    # each stock should get an equal allocation in the portfolio 1/n
    context.x0 = 1.0 * np.ones_like(context.stocks) / len(context.stocks)

    # Initialize Speculations Portfolio

    # Rebalance every day, 1 hour after market open.
    schedule_function(speculate, date_rules.every_day(), time_rules.market_open(hours=1))

    schedule_function(monthly_review, date_rules.week_start(), time_rules.market_open(hours=1))

    context.speculations = symbols('XLY',  # XLY Consumer Discrectionary SPDR Fund
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


    attach_pipeline(make_pipeline(), 'pipeline_speculate')


def make_pipeline():
    pipe = Pipeline()

    _50ma = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=50)
    _200ma = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=200)

    pipe.add(_50ma, '_50ma')
    pipe.add(_200ma, '_200ma')
    pipe.add(_50ma / _200ma, 'ma_ratio')

    return pipe


def handle_data(context, data):
    if 'mx_lvrg' not in context:  # Max leverage
        context.mx_lvrg = 0  # Init this instead in initialize() for better efficiency
    if context.account.leverage > context.mx_lvrg:
        context.mx_lvrg = context.account.leverage
        record(mx_lvrg=context.mx_lvrg)  # Record maximum leverage encountered
    record(leverage=context.account.leverage)


def perm_portfolio(context, data):
    prices = data.history(context.stocks, 'price', 22, '1d').as_matrix(context.stocks)  # 22 = 1 month
    ret = np.diff(prices, axis=0)  # daily returns ret = [day1 - day 0, day2-day1,...]
    ret = np.divide(ret, np.amax(np.absolute(ret)))

    bnds = ((0, 1), (0, 1), (0, 1), (0, .1))  # bounds for weights (number of bounds  = to number of assets)
    # lambda is used here to create a concise function that returns the sum of x - 1
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})

    # calculate the efficient frontier for the portfolio using Markowitz bullet
    # How can we maximize returns, while minimizing risk (variance/std-dev)
    # https://blog.quantopian.com/markowitz-portfolio-optimization-2/
    res = scipy.optimize.minimize(fitnessERC, context.x0, args=ret, method='SLSQP', constraints=cons, bounds=bnds)

    if res.success:
        allocation = res.x  # the allocation solutions returned by
        allocation[allocation < 0] = 0
        denom = np.sum(allocation)
        if denom != 0:  # normalization process
            allocation = allocation / denom
    else:
        allocation = context.x0

    context.x0 = allocation

    total = allocation[0] + allocation[1] + allocation[2] + allocation[3]
    w1 = allocation[0] / total
    w2 = allocation[1] / total
    w3 = allocation[2] / total
    w4 = allocation[3] / total

    leverage = 1
    permanent_portfolio_allocation = 0.8
    leverage = permanent_portfolio_allocation * leverage

    order_target_percent(sid(8554), w1 * leverage)
    order_target_percent(sid(23921), w2 * leverage)
    order_target_percent(sid(26807), w3 * leverage)
    order_target_percent(sid(23911), w4 * leverage)


def speculate(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    prices = data.history(assets=context.speculations, bar_count=context.historical_bars, frequency='1d',
                          fields='price')

    for stock in context.speculations:

        try:

            price_hist = data.history(stock, 'price', 50, '1d')
            ma1 = price_hist.mean()  # 50 day moving average
            price_hist = data.history(stock, 'price', 200, '1d')
            ma2 = price_hist.mean()  # 200 day moving average

            start_bar = context.feature_window
            price_list = prices[stock].tolist()

            X = []  # list of feature sets
            y = []  # list of labels, one for each feature set

            bar = start_bar

            # feature creation
            """
            Summary: Get the daily % return as a feature set, if tomorrow's price increased, label
            that feature set as a 1 (strong outlook/buy).
            
            Once we have generated a feature set for the last 100 days, in 10 day windows, we can train our model 
            to identify (fit) % returns (feature set) to a buy or sell (short) recommendation  (labels).
            """
            while bar < len(price_list) - 1:
                try:

                    end_price = price_list[bar + 1]  # "tomorrow"'s price'
                    begin_price = price_list[bar]  # today's price

                    pricing_list = []
                    xx = 0
                    for _ in range(context.feature_window):
                        price = price_list[bar - (context.feature_window - xx)] # 10-(10-i) i++, get the trailing 10 day prices
                        pricing_list.append(price)
                        xx += 1

                    # get the % change in daily prices of last 10 days, this will be our feature set
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
                    print(('feature creation', str(e)))

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
            clf1.fit(X, y)
            clf2.fit(X, y)
            clf3.fit(X, y)
            clf4.fit(X, y)

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
            # if there is no consensus, we do nothing

            if Counter([p1, p2, p3, p4]).most_common(1)[0][1] >= 4:
                p = Counter([p1, p2, p3, p4]).most_common(1)[0][0]

            else:
                p = 0

            print(('ma1_d: ', ma1))
            print(('ma2_d :', ma2))
            print(('p1 :',p1))
            print(('p2 :',p2))
            print(('p3 :',p3))
            print(('p4 :',p4))
            print(('Prediction', p))


            speculations_allocation = 0.2
            # Based on the voted prediction and the momentum of the moving averages,
            # We will either buy or short the stock (or do nothing).

            if p == 1 and ma1 > ma2:
                order_target_percent(stock, 0.11 * speculations_allocation)
            elif p == -1 and ma1 < ma2:
                order_target_percent(stock, -0.11 * speculations_allocation)

                # alternatively we could just do:
                # order_target_percent(stock,(p*0.11))

        except Exception as e:
            print(str(e))

    record('ma1', ma1)
    record('ma2', ma2)
    record('Leverage_Spec', context.account.leverage)


def monthly_review(context, data):
    price_hist = data.history(context.speculations, 'price', 50, '1d')
    ma1 = price_hist.mean()
    price_hist = data.history(context.speculations, 'price', 200, '1d')
    ma2 = price_hist.mean()
    print(('ma1',str(ma1)))
    print(('ma2',str(ma2)))


def variance(x, *args):
    # x = weights
    p = np.squeeze(np.asarray(args))
    Acov = np.cov(p.T)
    return np.dot(x, np.dot(Acov, x))


# Markowitz portfolio optimization. Best possible return, at a given risk level (std)

# https://blog.quantopian.com/markowitz-portfolio-optimization-2/
def fitnessERC(x, *args):
    N = x.shape[0]
    p = np.squeeze(np.asarray(args))
    Acov = np.cov(p.T)
    Acov = np.matrix(Acov)
    x = np.matrix(x)
    y = np.array(x) * (np.array(Acov * x.T).T)
    var = x * Acov * x.T
    b = var / N
    fval = 0
    y = np.squeeze(np.asarray(y))
    for i in range(0, N):
        xij = (y[i] / var - b) * (y[i] / var - b)
        fval = fval + xij * xij
    return fval
