import numpy as np
import scipy

# Inspired by Georges Bilan's algorithm posted on Quantopian.
# https://www.quantopian.com/posts/risk-parity-slash-slash-all-weather-portfolio

def initialize(context):
    schedule_function(func=perm_portfolio, date_rule=date_rules.week_start(days_offset=0),
                      time_rule=time_rules.market_open(hours=1, minutes=1))
    schedule_function(func=perm_portfolio, date_rule=date_rules.week_start(days_offset=3),
                      time_rule=time_rules.market_open(hours=1, minutes=1))

    context.stocks = [sid(8554),  # SPY
                      sid(23921),  # TLT
                      sid(26807),  # GLD
                      sid(23911)]  # Shy

    # each stock should get an equal allocation in the portfolio 1/n
    context.x0 = 1.0 * np.ones_like(context.stocks) / len(context.stocks)


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
