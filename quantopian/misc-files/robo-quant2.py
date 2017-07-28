from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import SimpleMovingAverage
from quantopian.pipeline.filters.morningstar import Q1500US


def initialize(context):
    # Schedule our rebalance function to run at the start of each week.
    schedule_function(my_rebalance, date_rules.week_start(), time_rules.market_open(hours=1))

    # Record variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())

    
    my_pipe = make_pipeline()
    attach_pipeline(my_pipe, 'my_pipeline')
    
def make_pipeline():
    """
    Create our pipeline.
    """

    # Base universe set to the Q1500US.
    base_universe = Q1500US()

    # 10-day close price average.
    mean_10 = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=10, mask=base_universe)

    # 30-day close price average.
    mean_30 = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=30, mask=base_universe)

    percent_difference = (mean_10 - mean_30) / mean_30

    # Filter to select securities to short.
    shorts = percent_difference.top(25)

    # Filter to select securities to long.
    longs = percent_difference.bottom(25)

    # Filter for all securities that we want to trade.
    securities_to_trade = (shorts | longs)

    return Pipeline(
        columns={
            'longs': longs,
            'shorts': shorts
        },
        screen=(securities_to_trade),
    )


def my_compute_weights(context):
    """
    Compute ordering weights.
    """
    # Compute even target weights for our long positions and short positions.
    long_weight = 0.5 / len(context.longs)
    short_weight = -0.5 / len(context.shorts)

    return long_weight, short_weight

def before_trading_start(context, data):
    # Gets our pipeline output every day.
    context.output = pipeline_output('my_pipeline')

    # Go long in securities for which the 'longs' value is True.
    # Select rows where the 'longs' column is true
    context.longs = context.output[context.output['longs']].index.tolist()

    # Go short in securities for which the 'shorts' value is True.
    context.shorts = context.output[context.output['shorts']].index.tolist()
    
    context.long_weight, context.short_weight = my_compute_weights(context)
    
    print ('context.output.head()', context.output.head())
    print ('context.longs', context.longs)
        
        
def my_rebalance(context, data):
    """
    Rebalance weekly.
    """
    for security in context.portfolio.positions:
        if security not in context.longs and security not in context.shorts and data.can_trade(security):
            order_target_percent(security, 0)

    for security in context.longs:
        if data.can_trade(security):
            order_target_percent(security, context.long_weight)

    for security in context.shorts:
        if data.can_trade(security):
            order_target_percent(security, context.short_weight)
    
    
def my_record_vars(context, data):
    """
    Record variables at the end of each day.
    """
    longs = shorts = 0
    for position in context.portfolio.positions.itervalues():
        if position.amount > 0:
            longs += 1
        elif position.amount < 0:
            shorts += 1

    # Record our variables.
    record(leverage=context.account.leverage, long_count=longs, short_count=shorts)        
        