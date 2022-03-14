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
symbol = ['ANVS']

global timeframe
timeframe = '1d'

global TFN
TFN = '6d'

global increment
increment = '5m'

global delay
delay = 300

global delaycounter # 1,2 work best
delaycounter = 2

global tradingbound #0.05 for uptrends
tradingbound = 0.05

global filelist
filelist = []

global netcapital
netcapital = 0

global netsectionval
netsectionval = 0

global bestsectionval
bestsectionval = 0

global EMAPrimer #Number of data points used to prime EMA prior to trading
EMAPrimer = 390

class stock:
    changes = []
    profit = []
    profit_per_trade = 0
    limit = 0
    Ticker = ''
    quantity = 0
    capital = 0
    sold = True
    bought = False
    bought_price = 0
    section_val = 0
    bestprofit = 0
    profitlog = []
    EMA_log =[]
    curr_EMA = 0
    prev_EMA = 0
    EMA_slope = 0
    EMA_slope5 = 0
    EMA_slope10 = 0
    counter = 0
    slopecounter = 0
    setcounter = 2
    bestsale = 0
    delayed = False
    delaycounter = 0
    delaySlopearr = []
    delaySlope = 0
    AF_increment = 0.08
    AF_limit = 0.2
    PSARMatrix = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
    PSARcounter = 0

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
        self.EMA_log = []
        self.curr_EMA = -5
        self.prev_EMA = 0
        self.EMA_Slope = 0
        self.EMA_Slope10 = 0
        self.EMA_Slope30 = 0
        self.counter = 2
        self.slopecounter = 0
        self.setcounter = 2
        self.bestsale = 0
        self.delayed = False
        self.delaycounter = 0
        self.delaySlopearr = []
        self.delaySlope = 0
        self.AF_increment = 0.02
        self.AF_limit = 0.2
        self.PSARMatrix = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
        self.PSARcounter = 1

    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")

def EMAInitialize(stock):
    
    global TFN

    data = yfinance.download(tickers = stock.Ticker, period = TFN, interval = increment)
    print(data.iloc[1]['Close'])
    counter = 2

    for i in range(len(data)):       
        if(i == counter): #Get current point's data
            close1 = float(data.iloc[1]['Close'])
            stock.prev_EMA = stock.curr_EMA
            stock.curr_EMA = close1*(2/(stock.counter+1)) + stock.curr_EMA*(1 - (2/(stock.counter + 1)))
            stock.EMA_Slope = (stock.curr_EMA - stock.prev_EMA)/(timestep/60)
            stock.EMA_log.append(stock.curr_EMA)
            stock.counter += 1
    
    

def percent_change_update(stock, x, IL):
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
            if(i/2 == stock.PSARcounter):
                stock.PSARMatrix[1][0] = float(row[1]) #set High
                stock.PSARMatrix[1][1] = float(row[2]) #set Low

        if(i % 2 == 0):                
            if(i/2 == stock.setcounter): #Get current point's data
                close1 = float(row[3])
                print(close1)
                break
            elif(i/2 == stock.setcounter - 1): #Get previous point's data
                close0 = float(row[3])
                print(close0)
        i += 1

    stock.PSARcounter += 1

    # stock.slopes.append((float(data.iloc[1]['Close'] - data.iloc[0]['Close'])/float(data.iloc[0]['Close'])) * 100)
    # if(stock.setcounter == 0):

    #Change Between Consecutive Close Values

    # print(f"close1: {close1}, close0: {close0}")
    
    stock.changes.append(((close1 - close0)/close0)*100)
    
    stock.limit = close1 * 1.00
    
    #Update the EMA; EMA = Averge Price over some interval 't0 - tf'
    stock.prev_EMA = stock.curr_EMA
    stock.curr_EMA = close1*(2/(stock.counter+1)) + stock.curr_EMA*(1 - (2/(stock.counter + 1)))
    stock.EMA_Slope = (stock.curr_EMA - stock.prev_EMA)/(timestep/60)
    stock.EMA_log.append(stock.curr_EMA)
    stock.counter += 1
    
    #PSAR Implementation
    if(IL == 1):
        print("Entered PSAR initialization\n")
        print(f"High Value: {stock.PSARMatrix[1][0]}")
        print(f"Low Value: {stock.PSARMatrix[1][1]}")
        stock.PSARMatrix[1][2] = stock.PSARMatrix[1][1] #set PSAR
        print(f"PSAR Value: {stock.PSARMatrix[1][2]}")
        stock.PSARMatrix[1][3] = stock.PSARMatrix[1][0] #set EP
        print(f"EP Value: {stock.PSARMatrix[1][3]}")
        stock.PSARMatrix[1][4] = stock.PSARMatrix[1][3] - stock.PSARMatrix[1][2] #set EP - PSAR
        print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        stock.PSARMatrix[1][5] = stock.AF_increment #set AF
        print(f"AF Value: {stock.PSARMatrix[1][5]}")
        stock.PSARMatrix[1][6] = stock.PSARMatrix[1][4] * stock.PSARMatrix[1][5] #set (EP - PSAR)*AF
        print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")
        stock.PSARMatrix[1][7] = 1 #set BULLBEAR
        print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")
    else:
    
        print("Entered PSAR Solve")
        print(f"High Value: {stock.PSARMatrix[1][0]}")
        print(f"Low Value: {stock.PSARMatrix[1][1]}")

        #PSAR Update START
        if(stock.PSARMatrix[0][7] == 1 and stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6] > stock.PSARMatrix[1][1]):
            stock.PSARMatrix[1][2] = stock.PSARMatrix[0][3]
        else:
            if(stock.PSARMatrix[0][7] == 0 and stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6] < stock.PSARMatrix[1][0]):
                stock.PSARMatrix[1][2] = stock.PSARMatrix[0][3]
            else:
                stock.PSARMatrix[1][2] = stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6]
        #PSAR Update END

        print(f"PSAR Value: {stock.PSARMatrix[1][2]}")

        #BULLBEAR Update START
        if(stock.PSARMatrix[1][2] < stock.PSARMatrix[1][0]):
            stock.PSARMatrix[1][7] = 1
        else:
            if(stock.PSARMatrix[1][2] > stock.PSARMatrix[1][1]):
                stock.PSARMatrix[1][7] = 0
        #BULLBEAR Update END

        print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")

        #EP Update START
        if(stock.PSARMatrix[1][7] == 1 and stock.PSARMatrix[1][0] > stock.PSARMatrix[0][3]):
            stock.PSARMatrix[1][3] = stock.PSARMatrix[1][0]
        else:
            if(stock.PSARMatrix[1][7] == 1 and stock.PSARMatrix[1][0] <= stock.PSARMatrix[0][3]):
                stock.PSARMatrix[1][3] = stock.PSARMatrix[0][3]
            else:
                if(stock.PSARMatrix[1][7] == 0 and stock.PSARMatrix[1][1] < stock.PSARMatrix[0][3]):
                    stock.PSARMatrix[1][3] = stock.PSARMatrix[1][1]
                else:
                    if(stock.PSARMatrix[1][7] == 0 and stock.PSARMatrix[1][1] >= stock.PSARMatrix[0][3]):
                        stock.PSARMatrix[1][3] = stock.PSARMatrix[0][3]

        #EP Update END

        print(f"EP Value: {stock.PSARMatrix[1][3]}")

        #AF Update START
        if(stock.PSARMatrix[0][7] == stock.PSARMatrix[1][7]):
            stock.PSARMatrix[1][5] = stock.PSARMatrix[0][5]
            if(stock.PSARMatrix[1][7] == 1 and stock.PSARMatrix[1][3] > stock.PSARMatrix[0][3]):
                if(stock.PSARMatrix[1][5] < stock.AF_limit):
                    stock.PSARMatrix[1][5] = stock.PSARMatrix[1][5] + stock.AF_increment
            if(stock.PSARMatrix[1][7] == 0 and stock.PSARMatrix[1][3] < stock.PSARMatrix[0][3]):
                if(stock.PSARMatrix[1][5] < stock.AF_limit):
                    stock.PSARMatrix[1][5] = stock.PSARMatrix[1][5] + stock.AF_increment
        else:
            stock.PSARMatrix[1][5] = stock.AF_increment
        #AF Update END

        print(f"AF Value: {stock.PSARMatrix[1][5]}")

        stock.PSARMatrix[1][4] = stock.PSARMatrix[1][3] - stock.PSARMatrix[1][2] #set EP - PSAR
        stock.PSARMatrix[1][6] = stock.PSARMatrix[1][4] * stock.PSARMatrix[1][5] #set (EP - PSAR)*AF

        print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")

    #Setup for next iteration
    stock.PSARMatrix[0] = stock.PSARMatrix[1]
    stock.PSARMatrix[1] = [0,0,0,0,0,0,0,0]

    #Delay SMA Update
    if(stock.delayed == True):
        stock.delaySlopearr.append(close1)

    stock.slopecounter += 1

    print(f"Slope for {stock.Ticker} was {stock.changes[-1]}")
    print(f"EMA_Slope for {stock.Ticker} was {stock.EMA_Slope}")
    # print(f"Length of slopes: {len(stock.changes)}\n\n")

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
    # rand = input("Paused the code")
    stock.quantity = 0
    stock.bought_price = 0

    # print(f"Original curr_EMA: {stock.curr_EMA}")
    # stock.curr_EMA = 0
    # print(f"Updated curr_EMA: {stock.curr_EMA}")

    # if(stock.PSARMatrix[0][7] == 0):
    # stock.delayed = True

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
    # EMAInitialize(stocks_list[i])
    percent_change_update(stocks_list[i], i, 1)

    

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
                percent_change_update(stocks_list[i], i, 0)
                stocks_list[i].setcounter += 1

                if(stocks_list[i].delayed == False):
                    # Enter Checks for holding, sell, and buying
                    if(-1*tradingbound <= stocks_list[i].changes[-1] and stocks_list[i].changes[-1] <= tradingbound):
                        print("Held the position")
                    elif(stocks_list[i].changes[-1] < -1*tradingbound):
                    # if(stocks_list[i].PSARMatrix[0][7] == 0):
                        if(stocks_list[i].PSARMatrix[0][7] == 0):
                            if(stocks_list[i].bought == True and stocks_list[i].sold == False):

                                if(stocks_list[i].bought_price <= stocks_list[i].limit):
                                    sell(stocks_list[i])
                                    print(f"Made a profit of: {stocks_list[i].profit[-1]}")
                                    continue

                                print("Entered selling check and had stocks but sell price < bought price")

                                if(stocks_list[i].bought_price <= stocks_list[i].limit):
                                    if(stocks_list[i].EMA_Slope < 0):
                                        sell(stocks_list[i])
                                        print(f"Made a profit of: {stocks_list[i].profit[-1]}")
                                        continue

                                print("Entered selling check and had stocks but EMA_Slope >= 0")
                                
                            else:
                                print("Entered selling check but had no stocks")
                    elif(stocks_list[i].changes[-1] > tradingbound):
                    # elif(stocks_list[i].PSARMatrix[0][7] == 1):
                        # if(stocks_list[i].PSARMatrix[0][7] == 1):
                            if(stocks_list[i].bought == False and stocks_list[i].sold == True):
                                if(stocks_list[i].EMA_Slope >= 0):
                                    buy(stocks_list[i])
                            else:
                                print("Entered buying check but did not meet requirements")

                else:
                    print("Skipped current iteration to get better info")
                    stocks_list[i].delaycounter += 1

                    if(stocks_list[i].delaycounter == delaycounter):
                        stocks_list[i].delaySlope = (stocks_list[i].delaySlopearr[-1] - stocks_list[i].delaySlopearr[0])/(timestep/60)

                        if(stocks_list[i].delaySlope > 0):
                            stocks_list[i].delayed = False
                            stocks_list[i].delaycounter = 0
                            stocks_list[i].delaySlopearr = []
                            stocks_list[i].delaySlope = 0
                        else:
                            # stocks_list[i].delaySlopearr = []
                            stocks_list[i].delaySlope = 0
                            stocks_list[i].delaycounter = 0

                print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
                # x = input("")
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

for i in range(1):
    print(f"Net capital: {netcapital}\n")
    print(f"Net section value: {netsectionval}")
    print(f"Percent change: {(((netsectionval - netcapital)/netcapital)*100)}%\n")
    print(f"Best section value: {bestsectionval}")
    print(f"Best percent change: {(((bestsectionval - netcapital)/netcapital)*100)}%\n")
