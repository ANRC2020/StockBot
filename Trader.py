import alpaca_trade_api as tradeapi
import yfinance as yf
import time

key = 'PKVFHHHH0AY7H08R27DJ'
sec = 'glrKIjgy1haexGNZdiKLwWd67WN6qZEVUorrNkA9'

url = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(key, sec, url, api_version='v2')

#Init our account var
account = api.get_account()

#Should print 'ACTIVE'
print(account.status)



order = api.submit_order(symbol="FB",
                            qty="10",
                            side="buy",
                            type="market",
                            time_in_force="day")

buy_price = order.price
print(order)


current_price = yf.download(tickers='FB',period='1m', interval = '1m')['Open'][1]
print(current_price)

if current_price > buy_price:
    order = api.submit_order(symbol="FB",
                            qty="10",
                            side="sell",
                            type="market",
                            time_in_force="day")

print(order)
