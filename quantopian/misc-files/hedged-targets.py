def initialize(context):
    context.stocks = symbols('XLY',  # XLY Consumer Discrectionary SPDR Fund   
                           'XLF',  # XLF Financial SPDR Fund  
                           'XLK',  # XLK Technology SPDR Fund  
                           'XLE',  # XLE Energy SPDR Fund  
                           'XLV',  # XLV Health Care SPRD Fund  
                           'XLI',  # XLI Industrial SPDR Fund  
                           'XLP',  # XLP Consumer Staples SPDR Fund
                           'XLB',  # XLB Materials SPDR Fund  
                           'XLU')  # XLU Utilities SPRD Fund
    
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_trade, date_rules.every_day(), time_rules.market_open(hours=1))
    
def my_trade(context, data):
    for stock in context.stocks:
        MA1 = data.history(
        stock,
        fields='price',
        bar_count=50,
        frequency='1d'
        )
    
        MA2 = data.history(
        stock,
        fields='price',
        bar_count=200,
        frequency='1d'
        )
        MA1 = MA1.mean()
        MA2 = MA2.mean()
        
        price = data.current(stock,'price')
        
        if MA1 > MA2:
            order_target_percent(stock, 0.11)
            
        elif MA1 < MA2:
            order_target_percent(stock, -0.11)