def initialize(context):
    context.investment_size = (context.portfolio.cash / 10.0)
    context.stop_loss_pct = 0.995
    set_symbol_lookup_date('2012-10-01')
    fetch_csv('http://sentdex.com/api/finance/sentiment-signals/sample/', pre_func = preview)
    context.stocks = symbols('AAPL', 'MCD', 'FB', 'GME', 'INTC', 'SBUX', 'T', 'MGM', 'SHLD', 'NKE', 'NFLX', 'PFE', 'GS', 'TGT', 'NOK', 'SNE', 'TXN', 'JNJ', 'KO', 'VZ', 'XOM', 'WMT', 'MCO', 'TWTR', 'URBN', 'MCP', 'MSFT', 'HD', 'KSS', 'AMZN', 'S', 'BA', 'F', 'JPM', 'QCOM', 'TSLA', 'YHOO', 'GM', 'IBM')
    
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_trade, date_rules.every_day(), time_rules.market_open(hours=1))
    
def preview(df):
    log.info(df.head())
    return df

# Will be called on every trade event for the securities you specify. 
def my_trade(context, data):
    cash = context.portfolio.cash
    try:
        for s in data:
            if 'sentiment_signal' in data[s]:
                sentiment = data[s]['sentiment_signal']
                current_position = context.portfolio.positions[s].amount
                current_price = data[s].price
                if (sentiment > 5) and (current_position == 0):
                    if cash > context.investment_size:
                        order_value(s, context.investment_size, style=StopOrder(current_price * context.stop_loss_pct))
                        cash -= context.investment_size
                elif (sentiment <= -1) and (current_position > 0):
                    order_target(s,0)

                if context.shorting:
                    ma1 = data[s].mavg(100)
                    ma2 = data[s].mavg(300)
                    if (sentiment <= -3) and (current_position) == 0:
                        if ma2 > ma1:
                            if cash > context.investment_size:
                                order_value(s, -context.investment_size)
                                context.shorts.append(s)
                                
                    elif (sentiment >= -1) and (current_position > 0) and s in context.shorts:
                        order_target(s, 0)
                        context.shorts.remove(s)
    except Exception as e:
        print(str(e))