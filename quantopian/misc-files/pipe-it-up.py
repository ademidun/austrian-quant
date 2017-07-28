"""
This is a template algorithm on Quantopian for you to adapt and fill in.
Note: This algorithm was backtested with $100k initial capital, as opposed to the
regular $1m because some of the shares were small cap stocks that were thinly traded
and thus many of their orders were only partially filled when trading with
"""


from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import SimpleMovingAverage

def initialize(context):
    """
    Called once at the start of the algorithm.
    """   


    # Rebalance every day, 1 hour after market open.
    schedule_function(execute_trade, date_rules.every_day(), time_rules.market_open(hours=1))
     
    attach_pipeline(make_pipeline(), 'pipe-it-up')
    context.stocks_sold = []

def make_pipeline():

    pipe = Pipeline()

    _50ma = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=50)
    _200ma = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=200)

    pipe.add(_50ma, '_50ma')
    pipe.add(_200ma, '_200ma')
    pipe.add(_50ma/_200ma, 'ma_ratio')
    pipe.set_screen(_50ma/_200ma > 1.0)

    return pipe

def before_trading_start(context, data):

    #turns the output from a Pipeline object to a Pandas Dataframe object

    output = pipeline_output('pipe-it-up')
    context.my_universe = output.sort('ma_ratio', ascending=False).iloc[:300]
    update_universe(context.my_universe.index)

def execute_trade(context,data):

    log.info("\n" + str(context.my_universe.head()))
    log.info("\n" + str(len(context.my_universe)))

    cash = context.portfolio.cash
    purchase_value = 1500

    for stock in context.my_universe.index:
        if stock not in context.portfolio.positions:
            if purchase_value < cash: 
                try:
                    order_target_value(stock, purchase_value) # does context.portfolio.cash not get updated?
                    # why not use that? instead of updating cash manualy
                    cash -= purchase_value
                    if stock in context.stocks_sold:
                        context.stocks_sold.remove(stock)
                except:
                    pass

    for stock in context.portfolio.positions:
        if stock not in context.my_universe.index and stock not in context.stocks_sold:
            order_target_value(stock, 0)
            context.stocks_sold.append(stock)
            record('Leverage',context.account.leverage)


