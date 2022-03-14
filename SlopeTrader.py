import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import PortfolioHistory
from pandas._libs.tslibs import Timestamp
import yfinance
import time
from datetime import datetime
import pandas as pd
import csv
from csv import DictWriter, writer
import threading

global timestep
timestep = 300

class stock:
    slopes = []
    profit = []
    profit_per_trade = 0
    limit = 0
    Ticker = ""
    quantity = 0
    initial = 0
    capital = 0
    remainder = 0
    sold = True
    bought = False
    bought_price = 0

    def __init__(self,first_line):
        self.Ticker = str(first_line[0])
        self.quantity = int(first_line[1])
        self.capital = float(first_line[2])
        self.remainder = 0
        self.sold = bool(int(first_line[3]))
        self.bought = bool(int(first_line[4]))
        self.bought_price = float(first_line[5])
        self.slopes = []
        self.profit = []
        self.limit = 0
        self.initial = float(first_line[2])
        self.profit_per_trade = 0

    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")

def save_info(stocks_list):
    # initialize list of lists
    print("Entered Save_Info\n")

    # Create the pandas DataFrame
    df = pd.DataFrame([], columns = ['symbol', 'quantity', "capital", "sold", "bought", "bought_price"])

    for i in range(len(stocks_list)):
        load = [stocks_list[i].Ticker, stocks_list[i].quantity, stocks_list[i].capital, stocks_list[i].sold, stocks_list[i].bought, stocks_list[i].bought_price]
        df.append(load,ignore_index=True)
    
    stamp = datetime.today()
    title = f"Saved_Info_{stamp}.csv"

    field_names = ["FileName"]
    dict = {"FileName":title}
    with open("datalog.csv", "a") as file:
        writter =  DictWriter(file, fieldnames=field_names)
        writter.writerow(dict)
        writter.writerow(dict)
        file.close()

    df.to_csv(title)

def slope_update(stock):
    
    data = yfinance.download(tickers = stock.Ticker, period ='5m', interval = '5m') #May need to change period to '10m'
    #[1] = current, [2] = prev
    print(data)

    stock.slopes.append((float(data.iloc[1]['Close'] - data.iloc[0]['Close'])/float(data.iloc[0]['Close'])) * 100)

    stock.limit = data.iloc[1]['Close'] * 1.00

    print(f"Slope for {stock.Ticker} was {stock.slopes[-1]}")
    print(f"Length of slopes: {len(stock.slopes)}\n\n")

def buy(stock):

    print("Triggered Buy Command\n")

    stock.quantity = int(stock.capital/stock.limit)# Buys the greatest whole number of stocks and update stocks and capital for later use
    #Note: subtract quantity by 1 to prevent buying more than you can/set limit to limit * 1.02 or another value
    
    order = api.submit_order(symbol=stock.Ticker,
                            qty = str(stock.quantity),
                            side ="buy",
                            type = "market",
                            time_in_force ='day')
    
    # money_invested = float(api.get_account().portfolio_value) - float(api.get_account().buying_power)
    stock.remainder = stock.capital - float(stock.quantity * stock.limit)
    stock.bought_price = stock.limit
    stock.profit_per_trade = stock.bought_price

    stock.bought = True
    stock.sold = False

def sell(stock):
    print("Triggered Sell Command\n")
    difference = float(api.get_account().buying_power)
    order = api.submit_order(symbol=stock.Ticker,
                            qty = str(stock.quantity),
                            side ="sell",
                            type = "market",
                            time_in_force ='day')
    
    difference = float(api.get_account().buying_power) - difference
    sold_price = difference/stock.quantity
    stock.capital = stock.remainder + (sold_price * stock.quantity)

    stock.profit_per_trade = sold_price - stock.profit_per_trade
    stock.profit.append(stock.profit_per_trade)
    stock.profit_per_trade = 0
    print(f"Sold {stock.Ticker} and make a profit of {stock.profit[-1]} per each of {stock.quantity} stocks")

    stock.quantity = 0
    stock.bought_price = 0

    stock.bought = False
    stock.sold = True
#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

counter = 0
x = 0

key = 'PKRXHTL201XCUN550DCP'
sec = 'kVgrGMxDO08kEvVkacPgRX2DBDq5YJW97EUFn4lf'
url = 'https://paper-api.alpaca.markets'
api = tradeapi.REST(key, sec, url, api_version='v2')
#Init our account var
account = api.get_account()
#Should print 'ACTIVE'
print(account.status)

with open("DataLog.csv") as file:
    reader = csv.reader(file)
    file_name = ""
    for row in reader:
        file_name = str(row)
    file.close()

file_name = file_name.strip("'[]")

print(file_name)

stocks_list = []

with open(file_name, 'r') as file:
    reader = csv.reader(file)
    csv_headings = next(reader)

    if csv_headings != None:
        i = 0
        for row in reader:
            # print(row)
            stocks_list.append(stock(row))
            stocks_list[i].print()
            i += 1

stocks = len(stocks_list)

for i in range(stocks):
    slope_update(stocks_list[i])

while(True):
    check_time = datetime.today() #Gets current time
    if(x < 10):
        print(f"Current Time: {check_time}\n")
        x += 1
    if check_time.hour >= 6  and check_time.hour <= 13:
        start_time = time.time()

        print("Beginning Trades!\n")

        while(counter < 12):
            end_time = time.time()
            
            if check_time.hour > 13:
                break

            if start_time + timestep <= end_time:
                start_time = time.time()

                for i in range(stocks):
                    print(f"---------------{stocks_list[i].Ticker} Stock Start ---------------")
                    # Update Slopes; 
                    slope_update(stocks_list[i])
                    # Enter Checks for holding, sell, and buying
                    if(-0.06 <= stocks_list[i].slopes[-1] and stocks_list[i].slopes[-1] <= 0.06):
                        print("Held the position")
                    elif(stocks_list[i].slopes[-1] < -0.06):
                        if(stocks_list[i].bought == True and stocks_list[i].sold == False):
                            if(stocks_list[i].bought_price <= stocks_list[i].limit):
                                sell(stocks_list[i])
                        else:
                            print("Entered selling check but did not meet requirements")
                    elif(stocks_list[i].slopes[-1] > 0.06):  
                        if(stocks_list[i].bought == False and stocks_list[i].sold == True):                                  
                            buy(stocks_list[i]) 
                        else:
                            print("Entered buying check but did not meet requirements")

                    print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
                counter += 1
                print(f"--------------- Finished Iteration {counter} ---------------\n")
        break

# save_info(stocks_list)
#---------------------------Initialized Time/Main loop-----------------------

# prev = 350, current = 351.35, ((current - prev)/prev) * 100 = .3857%
# prev = 30, current = 26, ((current - prev)/prev) * 100 = -13.333%
# prev = 30, current = 41.57, ((current - prev)/prev) * 100 = 38.567%

# Note: The slope values looked really wierd. They didn't match up with the data 
# on google stocks and I'm guessing it hass to do with the fact that they are displaying
# non-closing price data (i.e local high, avg, etc)