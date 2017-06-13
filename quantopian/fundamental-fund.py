"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume
from quantopian.pipeline.filters.morningstar import Q1500US

def initialize(context):
    """
    Called once at the start of the algorithm.
    """   
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_trade, date_rules.every_day(), time_rules.market_open())
    context.limit = 10
    # Create our dynamic stock selector.
    attach_pipeline(make_pipeline(), 'my_pipeline')

def make_pipeline():
    """
    A function to create our dynamic stock selector (pipeline). Documentation on
    pipeline can be found here: https://www.quantopian.com/help#pipeline-title
    """
    
    # Base universe set to the Q500US
    base_universe = Q1500US()

    # Factor of yesterday's close price.
    yesterday_close = USEquityPricing.close.latest
     
    pipe = Pipeline(
        screen = base_universe,
        columns = {
            'close': yesterday_close,
        }
    )
    return pipe

def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = pipeline_output('my_pipeline')
  
    # These are the securities that we are interested in trading each day.
    context.security_list = context.output.index
    
    context.fundamentals = get_fundamentals(
        query(
            fundamentals.valuation_ratios.pb_ratio,
            fundamentals.valuation_ratios.pe_ratio,
        )
        .filter(
            fundamentals.valuation_ratios.pe_ratio < 14
        )
        .filter(
            fundamentals.valuation_ratios.pb_ratio < 2
        )
        .order_by(
             fundamentals.valuation.market_cap.desc()
        )
        .limit(context.limit)
    )
    context.assets = context.fundamentals.columns.values

def my_trade(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    cash = context.portfolio.cash
    current_positions = context.portfolio.positions
    
    for stock in data:
        current_position = context.portfolio.positions[stock].amount
        stock_price = data[stock].price
        plausible_investment = cash / context.limit
     
        share_amount = int(plausible_investment / stock_price)
        
        try:
            if stock_price < plausible_investment:
                if current_position == 0:
                    if context.fundamentals[stock]['pe_ratio'] < 11:
                        order(stock, share_amount)
                    
                
            
        except Exception as e:
            print(str(e))

            
