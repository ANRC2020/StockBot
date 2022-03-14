#from PSAR_MACD_RSI import curr_time

def sell(stock,curr_time):
    print("Triggered Sell Command\n")
    # order = api.submit_order(symbol=stock.Ticker,
    #                         qty = str(stock.quantity),
    #                         side ="sell",
    #                         type = "market",
    #                         time_in_force ='day')
    
    stock.capital = stock.capital + (stock.limit * stock.quantity)

    stock.profit_per_trade = stock.limit - stock.profit_per_trade
    stock.profit.append(stock.profit_per_trade * stock.quantity)
    stock.profit_per_trade = 0
    print(f"Sold {stock.Ticker} and made a profit of {stock.profit[-1]}")

    stock.section_val += stock.profit[-1]
    stock.profitlog.append(stock.section_val)
    
    if(stock.section_val > stock.bestprofit):
        stock.bestprofit = stock.section_val
        stock.bestsale = stock.setcounter

    print(f"Current bestsale = {stock.bestprofit}")
    # rand = input("Paused the code")
    stock.quantity = 0
    stock.bought_price = 0

    stock.bought = False
    stock.sold = True

    stock.soldindicator[-1] = stock.close[-1]

    stock.sell_log.append([stock.limit, curr_time])