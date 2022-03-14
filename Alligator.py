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
symbol = ['AAPL']

global timeframe
timeframe = '1mo'

global increment
increment = '5m'

global delay
delay = 300

global delaycounter # 1,2 work best
delaycounter = 1

global tradingbound
tradingbound = 0.07

global filelist
filelist = []

global netcapital
netcapital = 0

global netsectionval
netsectionval = 0

global bestsectionval
bestsectionval = 0

class stock:
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
    SMA5 = 0
    SMA8 = 0
    SMA13 = 0
    counter = 0
    setcounter = 2
    bestsale = 0
    delayed = False
    delaycounter = 0
    delaySlopearr = []
    delaySlope = 0
    closearr = []

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
        self.counter = 0
        self.setcounter = 2
        self.bestsale = 0
        self.delayed = False
        self.delaycounter = 0
        self.delaySlopearr = []
        self.delaySlope = 0
        self.SMA5 = 0
        self.SMA8 = 0
        self.SMA13 = 0
        self.closearr = []

    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")

def percent_change_update(stock, x):
    # data = yfinance.download(tickers = stock.Ticker, period ='5m', interval = '5m')
    # print(data)
    global filelist
    global timestep

    file = open(str(filelist[x]))
    # file = open('TestDataSet.csv')
    csv_reader = csv.reader(file)

    # csv_reader = reader(read_obj)

    i = 0
    close1 = 0
    close0 = 0

    for row in csv_reader:
        if(i % 2 == 0):
            if(i/2 == stock.setcounter): #Get current point's data
                close1 = float(row[3])
                print(close1)
                break
            elif(i/2 == stock.setcounter - 1): #Get previous point's data
                close0 = float(row[3])
                print(close0)
        i += 1

    # stock.slopes.append((float(data.iloc[1]['Close'] - data.iloc[0]['Close'])/float(data.iloc[0]['Close'])) * 100)
    # if(stock.setcounter == 0):

    #Change Between Consecutive Close Values
    
    stock.changes.append(((close1 - close0)/close0)*100)
    stock.limit = close1 * 1.00
    
    stock.closearr.append(close1)
    stock.counter += 1
    
    if(stock.counter >= 5):
        stock.SMA5 = (stock.closearr[-1] + stock.closearr[-2] + stock.closearr[-3] + stock.closearr[-4] + stock.closearr[-5])/5
    else:
        stock.SMA5 = stock.closearr[-1]
    
    if(stock.counter >= 8):
        stock.SMA8 = (stock.closearr[-1] + stock.closearr[-2] + stock.closearr[-3] + stock.closearr[-4] + stock.closearr[-5] + stock.closearr[-6] + stock.closearr[-7] + stock.closearr[-8])/8
    else:
        stock.SMA8 = stock.closearr[-1]


    if(stock.counter >= 13):
        stock.SMA13 = (stock.closearr[-1] + stock.closearr[-2] + stock.closearr[-3] + stock.closearr[-4] + stock.closearr[-5] + stock.closearr[-6] + stock.closearr[-7] + stock.closearr[-8] + stock.closearr[-9] + stock.closearr[-10] + stock.closearr[-11] + stock.closearr[-12] + stock.closearr[-13])/13
    else:
        stock.SMA13 = stock.closearr[-1]


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
    # rand = int(input("Paused the code: Enter a number to continue"))
    stock.quantity = 0
    stock.bought_price = 0

    stock.delayed = True

    stock.bought = False
    stock.sold = True
#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------
iterations = 0
for i in range(len(symbol)):
    data = yfinance.download(tickers = symbol[i], period = timeframe, interval = increment)

    title = f"TestDataSet{i}.csv"
    filelist.append(title)

    with open(title, 'w') as csvfile:
        fieldnames = ['Open', "High", "Low", "Close", "Adj Close", "Volume"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        temp = len(data) - 2
        if(i == 0):
            iterations = temp
        if(iterations > temp):
            iterations = temp

        writer.writeheader()

        for j in range(len(data)):
            writer.writerow({'Open': data.iloc[j]['Open'], 'High': data.iloc[j]['High'], 'Low': data.iloc[j]['Low'], 'Close':data.iloc[j]['Close'], 'Adj Close':data.iloc[j]['Adj Close'], 'Volume':data.iloc[j]['Volume']})
        csvfile.close()

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
    netcapital += stocks_list[i].capital
    percent_change_update(stocks_list[i], i)

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
                percent_change_update(stocks_list[i], i)
                stocks_list[i].setcounter += 1

                if(stocks_list[i].SMA5 < stocks_list[i].SMA13 and stocks_list[i].SMA8 < stocks_list[i].SMA13):
                    if(stocks_list[i].bought == True and stocks_list[i].sold == False):

                        if(stocks_list[i].bought_price <= stocks_list[i].limit):
                            sell(stocks_list[i])
                            print(f"Made a profit of: {stocks_list[i].profit[-1]}")
                            continue

                        print("Entered selling check and had stocks but sell price < bought price")

                        # if(stocks_list[i].EMA_Slope < 0):
                        #     sell(stocks_list[i])
                        #     print(f"Made a profit of: {stocks_list[i].profit[-1]}")
                        #     continue

                        # print("Entered selling check and had stocks but EMA_Slope >= 0")
                        
                    else:
                        print("Entered selling check but had no stocks")

                elif(stocks_list[i].SMA5 > stocks_list[i].SMA8 and stocks_list[i].SMA8 > stocks_list[i].SMA13):
                    if(stocks_list[i].bought == False and stocks_list[i].sold == True):
                        # if(stocks_list[i].EMA_Slope >= 0):
                            buy(stocks_list[i])
                    else:
                            print("Entered buying check but did not meet requirements")

                else:
                    print("Sated; Doesn't match a buy or sell condition")
                    if(stocks_list[i].bought == True and stocks_list[i].sold == False):

                        if(stocks_list[i].bought_price <= stocks_list[i].limit):
                            sell(stocks_list[i])
                            print(f"Made a profit of: {stocks_list[i].profit[-1]}")
                            continue

                print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
            counter += 1
            print(f"--------------- Finished Iteration {counter} ---------------\n")

        break

for i in range(stocks):
    if(stocks_list[i].bought == False and stocks_list[i].sold == True):
        print("Not holding any stocks")
        print(f"Ending capital for {stocks_list[i].Ticker} is {stocks_list[i].capital}")
        print(f"Ending section value for {stocks_list[i].Ticker} is {stocks_list[i].section_val}")
        print(f"Best profit for {stocks_list[i].Ticker} is {stocks_list[i].bestprofit} at {stocks_list[i].bestsale}")
    else:
        print(f"Holding {stocks_list[i].quantity} stocks")
        print(f"Ending capital for {stocks_list[i].Ticker} is {stocks_list[i].capital}")
        sell(stocks_list[i])
        print(f"Ending section value for {stocks_list[i].Ticker} is {stocks_list[i].section_val}")
        print(f"Best profit for {stocks_list[i].Ticker} is {stocks_list[i].bestprofit} at {stocks_list[i].bestsale}")
    print(f"{stocks_list[i].profitlog}\n")
    netsectionval += stocks_list[i].section_val
    bestsectionval += stocks_list[i].bestprofit

print(f"Net capital: {netcapital}\n")
print(f"Net section value: {netsectionval}")
print(f"Percent change: {(((netsectionval - netcapital)/netcapital)*100)}%\n")
print(f"Best section value: {bestsectionval}")
print(f"Best percent change: {(((bestsectionval - netcapital)/netcapital)*100)}%\n")