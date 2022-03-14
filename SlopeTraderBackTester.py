import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import PortfolioHistory
from pandas._libs.tslibs import Timestamp
import yfinance
import time
from datetime import datetime
import pandas as pd
import csv
from csv import DictWriter, writer, reader
import threading

global timestep
timestep = 300

global symbol
symbol = 'ANVS'

global timeframe
timeframe = '1d'

global increment
increment = '2m'


class stock:
    netcapital = 0
    netsectionval = 0
    changes = []
    profit = []
    profit_per_trade = 0
    limit = 0
    Ticker = ""
    quantity = 0
    capital = 0
    sold = True
    bought = False
    bought_price = 0
    section_val = 0
    bestprofit = 0
    profitlog = []
    high_EMA = 0
    curr_EMA = 0
    prev_EMA = 0
    counter = 0
    setcounter = 2

    def __init__(self,first_line):
        self.Ticker = str(first_line[0])
        self.quantity = int(first_line[1])
        self.capital = float(first_line[2])
        self.sold = bool(int(first_line[3]))
        self.bought = bool(int(first_line[4]))
        self.bought_price = float(first_line[5])
        self.changes = []
        self.profit = []
        self.limit = 0
        self.profit_per_trade = 0
        self.section_val = float(first_line[2])
        self.bestprofit = 0
        self.profitlog = []
        self.high_EMA = 0
        self.curr_EMA = 0
        self.prev_EMA = 0
        self.counter = 0
        self.setcounter = 2

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

def percent_change_update(stock):
    # data = yfinance.download(tickers = stock.Ticker, period ='5m', interval = '5m')
    # print(data)

    # with open('TestDataSet.csv', 'r') as read_obj:
    file = open('TestDataSet.csv')
    csv_reader = csv.reader(file)

    # csv_reader = reader(read_obj)

    i = 0
    close1 = 0
    close0 = 0

    for row in csv_reader:
        if(i % 2 == 0):
            if(i/2 == stock.setcounter): #Get current point's data
                close1 = float(row[3])
                break
            elif(i/2 == stock.setcounter - 1): #Get previous point's data
                close0 = float(row[3])
        i += 1

    # stock.slopes.append((float(data.iloc[1]['Close'] - data.iloc[0]['Close'])/float(data.iloc[0]['Close'])) * 100)
    stock.changes.append(((close1 - close0)/close0)*100) #Difference between closing values over time difference
    # setcounter += 1
    stock.limit = close1 * 1.00
    
    #Update the EMA
    stock.prev_EMA = stock.curr_EMA
    stock.curr_EMA = close1*(2/(counter+1)) + stock.curr_EMA*(1 - (2/(counter + 1)))
    if(stock.curr_EMA >= stock.high_EMA):
        stock.high_EMA = stock.curr_EMA
    stock.counter += 1

    print(f"Slope for {stock.Ticker} was {stock.changes[-1]}")
    print(f"Length of slopes: {len(stock.changes)}\n\n")

def buy(stock):

    print("Triggered Buy Command\n")

    stock.quantity = int(stock.capital/stock.limit)# Buys the greatest whole number of stocks and update stocks and capital for later use
    #Note: subtract quantity by 1 to prevent buying more than you can/set limit to limit * 1.02 or another value
    
    # order = api.submit_order(symbol=stock.Ticker,
    #                         qty = str(stock.quantity),
    #                         side ="buy",
    #                         type = "market",
    #                         time_in_force ='day')
    
    # money_invested = float(api.get_account().portfolio_value) - float(api.get_account().buying_power)
    stock.capital = stock.capital - float(stock.quantity * stock.limit)

    stock.bought_price = stock.limit
    stock.profit_per_trade = stock.bought_price

    stock.bought = True
    stock.sold = False

def sell(stock):
    print("Triggered Sell Command\n")
    # order = api.submit_order(symbol=stock.Ticker,
    #                         qty = str(stock.quantity),
    #                         side ="sell",
    #                         type = "market",
    #                         time_in_force ='day')
    
    stock.capital = stock.capital + (stock.limit * stock.quantity)
    # difference = stock.capital - difference

    # sold_price = difference/stock.quantity
    # stock.capital = stock.remainder + (sold_price * stock.quantity)

    stock.profit_per_trade = stock.limit - stock.profit_per_trade
    stock.profit.append(stock.profit_per_trade * stock.quantity)
    stock.profit_per_trade = 0
    print(f"Sold {stock.Ticker} and made a profit of {stock.profit[-1]}")

    stock.section_val += stock.profit[-1]
    stock.profitlog.append(stock.section_val)
    
    if(stock.section_val > stock.bestprofit):
        stock.bestprofit = stock.section_val

    stock.quantity = 0
    stock.bought_price = 0

    stock.bought = False
    stock.sold = True
#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

data = yfinance.download(tickers = symbol, period = timeframe, interval = increment)
# print(data.iloc[0])

with open('TestDataSet.csv', 'w') as csvfile:
    fieldnames = ['Open', "High", "Low", "Close", "Adj Close", "Volume"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    iterations = len(data) - 2
    writer.writeheader()

    for i in range(len(data)):
        writer.writerow({'Open': data.iloc[i]['Open'], 'High': data.iloc[i]['High'], 'Low': data.iloc[i]['Low'], 'Close':data.iloc[i]['Close'], 'Adj Close':data.iloc[i]['Adj Close'], 'Volume':data.iloc[i]['Volume']})

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
    percent_change_update(stocks_list[i])

while(True):
    check_time = datetime.today() #Gets current time
    if(x < 10):
        print(f"Current Time: {check_time}\n")
        x += 1
    if check_time.hour >= 0  and check_time.hour >= 0:
        # start_time = time.time()

        print("Beginning Trades!\n")

        while(counter < iterations): # set to # of data entires - 2
            # end_time = time.time()
            
            # if check_time.hour > 13:
            #     break

            # if start_time + timestep <= end_time:
            #     start_time = time.time()
                
            for i in range(stocks):
                print(f"---------------{stocks_list[i].Ticker} Stock Start ---------------")
                # Update Slopes; 
                percent_change_update(stocks_list[i])
                stocks_list[i].setcounter += 1
                # Enter Checks for holding, sell, and buying
                if(-0.07 <= stocks_list[i].changes[-1] and stocks_list[i].changes[-1] <= 0.07):
                    print("Held the position")
                elif(stocks_list[i].changes[-1] < -0.07):
                    if(stocks_list[i].bought == True and stocks_list[i].sold == False):
                        if(stocks_list[i].bought_price <= stocks_list[i].limit):
                            sell(stocks_list[i])
                            print(f"Made a profit of: {stocks_list[i].profit[-1]}")
                            continue
                        # if(stocks_list[i].prev_EMA > stocks_list[i].curr_EMA):
                        #     sell(stocks_list[i])
                        #     print(f"Made a profit of: {stocks_list[i].profit[-1]}")
                        #     continue
                        #Hard-sell if slope drops too quickly
                        if(stocks_list[i].changes[-1] <= -0.15):
                            sell(stocks_list[i])
                            print(f"Made a profit of: {stocks_list[i].profit[-1]}")
                    else:
                        print("Entered selling check but did not meet requirements")
                elif(stocks_list[i].changes[-1] > 0.07):
                    if(stocks_list[i].bought == False and stocks_list[i].sold == True):
                        # if(stocks_list[i].curr_EMA >= stocks_list[i].high_EMA):
                        buy(stocks_list[i]) 
                    else:
                        print("Entered buying check but did not meet requirements")

                print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
            counter += 1
            print(f"--------------- Finished Iteration {counter} ---------------\n")

        break

for i in range(stocks):
    if(stocks_list[i].bought == False and stocks_list[i].sold == True):
        print("Not holding any stocks")
        print(f"Ending capital for {stocks_list[i].Ticker} is {stocks_list[i].capital}")
        print(f"Ending section value for {stocks_list[i].Ticker} is {stocks_list[i].section_val}")
        print(f"Best profit for {stocks_list[i].Ticker} is {stocks_list[i].bestprofit}")
    else:
        print(f"Holding {stocks_list[i].quantity} stocks")
        print(f"Ending capital for {stocks_list[i].Ticker} is {stocks_list[i].capital}")
        sell(stocks_list[i])
        print(f"Ending section value for {stocks_list[i].Ticker} is {stocks_list[i].section_val}")
        print(f"Best profit for {stocks_list[i].Ticker} is {stocks_list[i].bestprofit}")
    print(stocks_list[i].profitlog)

# save_info(stocks_list)