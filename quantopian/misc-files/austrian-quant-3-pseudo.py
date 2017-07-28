PSEUDOCODE

run this function once a year:

def value_find():

	for stock in sp500[1:500]:
		""" Turn each stock in the SP 500 into a feature set using financial metrics from Morning star"""
		X = X.append(get_features(stock))
		y = y.append(get_performance(stock))

	# todo use ensemble method add more classifiers, 4 classifiers in total should be used.
	clf = RandomForestClassifier()
	clf.learn(X,y)

	stock_dict = {stock_ticker : 'probability',} # a dictionary of stock tickers and their corresponding buy probabilities

	for stock in sp500[1:500]: # Top 250 stocks by Market Cap, why top 250?
		performance = clf.predict(get_features(stock))
		prob = clf.predict_proba(get_features(stock))

		if performance == 1: # algorithm thinks it is a buy
			stock_dict['ticker'] = prob

	# https://docs.python.org/dev/library/collections.html#ordereddict-examples-and-recipes
	stock_dict_ordered = OrderedDict(sorted(stock_dict.items(), key=lambda t: t[0]))

    allocation = 0.1 # Set how much of the full portfolio we will allocate to the value fund

    sum_prob = sum(stock_dict_ordered.items()) # todo how to get sum of values in a dictionary

    for stock in context.value_stocks:# if it is not a top ten stock, sell our position
    	if stock not in stock_dict_ordered[1:10]:
    		order_target_percent(sid(stock, 0) 

	for stock in stock_dict_ordered[1:10]: #todo how to access keys and value of dictionary when iterating
		sum_prob = stock.value/sum_prob # the stronger the probability, the more money allocated to that stock
		
		if stock not in context.value_stocks:
	    	order_target_percent(sid(stock.key), sum_prob * allocation)









def get_features(stock = 'SPY'):
	""" Use Morningstart metrics to generate a feature set for the given stock"""

def get_performance((stock = 'SPY'):
	""" Compare the annual % change in stock price to annual % change of sp500, if >sp500, return 1 (buy)"""

