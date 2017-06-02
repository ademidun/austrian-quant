"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""

 
def initialize(context):
    """
    Called once at the start of the algorithm.
    """   
    context.security = sid(8554)
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_trade, date_rules.every_day(), time_rules.market_open())
    

 
def my_trade(context,data):
    """
    Called every minute.
    """
    print data
    
    MA1 = data.history(
        context.security,
        fields='price',
        bar_count=50,
        frequency='1d'
    )
    
    MA2 = data.history(
        context.security,
        fields='price',
        bar_count=200,
        frequency='1d'
    )
    MA1 = MA1.mean()
    MA2 = MA2.mean()
    
    current_price = data.current(context.security,'price')
    current_positions = context.portfolio.positions[sid(8554)].amount
    cash = context.portfolio.cash
    
    if (MA1 > MA2) and current_positions == 0:
        number_shares = int(cash/current_price)
        order(context.security,number_shares)
        log.info("Buying %s" % (context.security.symbol))   
        
    elif (MA1 < MA2) and current_positions != 0:
        order_target(context.security,0)
        log.info("Buying %s" % (context.security.symbol))
        
    record(MA1 = MA1, MA2 = MA2, Price= current_price)
    
