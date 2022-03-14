import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import PortfolioHistory
from pandas._libs.tslibs import Timestamp
import yfinance
import time
from datetime import datetime
import pandas as pd
import csv
from csv import DictWriter, writer

#--------------------Import Statements----------------------

# Update Idea: Save information in CSV file and load in information from that file the next time 
# this code is run to initialize the variables to what they were at the end of the prior cycle

with open("DataLog.csv") as file:
    reader = csv.reader(file)
    file_name = ""
    for row in reader:
        file_name = str(row)
    file.close()

file_name = file_name.strip("'[]")

with open(file_name) as file:
    reader = csv.reader(file)
    data =[]
    csv_headings = next(reader)
    first_line = next(reader)

global Ticker
Ticker = str(first_line[0])

global stocks
stocks = int(first_line[1])

global capital
capital = float(first_line[2])

global sold
sold = bool(int(first_line[3]))

global bought
bought = bool(int(first_line[4]))

global bought_price
bought_price = float(first_line[5])

global cap_log
cap_log = []

global SMA_5arr
SMA_5arr = []

global SMA_8arr
SMA_8arr = []

global SMA_13arr
SMA_13arr = []

global SMA_5arrSlope
SMA_5arrSlope = []

global SMA_8arrSlope
SMA_8arrSlope = []

global SMA_13arrSlope
SMA_13arrSlope = []

global timestep
timestep = 300

global polarity
polarity = False

#-------------------Load Values-----------------------------
#-------------------Global Var Declaration------------------

class stick:
    high = 0
    low = 0
    open_price = 0
    close = 0

    def __init__(self, high, low, open_price, close):
        self.high = high
        self.low = low
        self.open_price = open_price
        self.close = close

# class record:
#     operation = ""
#     quantity = 0
#     netprice = 0

#     def __init__(self, operation, qty, netchange):
#         self.operation = operation
#         self.quantity = qty
#         self.netprice = netchange


#--------------------Class Construction---------------------

def save_info():
    # initialize list of lists
    print("Entered Save_Info\n")

    load = [Ticker, stocks, capital, sold, bought, bought_price]
    
    # Create the pandas DataFrame
    df = pd.DataFrame(load, columns = ['symbol', 'quantity', "capital", "sold", "bought", "bought_price"])
    
    stamp = datetime.today()
    title = f"Saved_Info_{stamp}.csv"

    field_names = ["FileName"]
    dict = {"FileName":title}
    with open("datalog.csv", "a") as file:
        writter =  DictWriter(file, fieldnames=field_names)
        writter.writerow(dict)
        file.close()

    df.to_csv(title)

def moving_avg(arr):
    # Use an interpolating method to create an approximation of the function given several closing points
    # and use Euler's Method w/ PC Method to predict values
    global SMA_5arr
    global SMA_8arr
    global SMA_13arr
    global SMA_5arrSlope
    global SMA_8arrSlope
    global SMA_13arrSlope
    global timestep
    global polarity

    print("Entered Moving_Avg\n")

    SMA_5 = 0
    SMA_8 = 0
    SMA_13 = 0

    data = yfinance.download(tickers = Ticker, period ='2h', interval = '5m')

    for i in range(13):
        SMA_13 += data.iloc[-1*i]['Close']
        if(i < 8):
            SMA_8 += data.iloc[-1*i]['Close']
            if(i < 5):
                SMA_5 += data.iloc[-1*i]['Close']
        

    SMA_13 = float(SMA_13/13)
    SMA_8 = float(SMA_8/8)
    SMA_5 = float(SMA_5/5)

    print(f"\nSMA_13 = {SMA_13}")
    print(f"SMA_8 = {SMA_8}")
    print(f"SMA_5 = {SMA_5}")

    SMA_13arr.append(SMA_13)
    SMA_8arr.append(SMA_8)
    SMA_5arr.append(SMA_5)

    if(len(SMA_13arr) >= 2):
        SMA_13arrSlope.append(float(SMA_13arr[-1] - SMA_13arr[-2])/float(timestep/60))
        SMA_8arrSlope.append(float(SMA_8arr[-1] - SMA_8arr[-2])/float(timestep/60))
        SMA_5arrSlope.append(float(SMA_5arr[-1] - SMA_5arr[-2])/float(timestep/60))
        print(f"\nSMA_13arr.[latest] = {SMA_13arr[-1]}")
        print(f"SMA_8arr.[latest] = {SMA_8arr[-1]}")
        print(f"SMA_5arr.[latest] = {SMA_5arr[-1]}")

    # Currently set to execute market orders 

    if(SMA_5 > SMA_8 and SMA_5 > SMA_13 and bought == True and sold == False):
        print("Called Sell_Check from Moving_Avg; Rebound_Sell\n")
        
        limit_price = float(bought_price) * 1.015
        make_sell_order(Ticker, limit_price, "market")

    if(len(SMA_5arrSlope) >= 1):
        if(SMA_5arrSlope[-1] < 0 and SMA_8arrSlope[-1] > 0 and polarity == True and bought == True and sold == False):
            print("Called Sell_Check from Moving_Avg; Polarity Switch Off\n")
            polarity = False
            
            limit_price = float(bought_price) * 1.015
            make_sell_order(Ticker, limit_price, "market")

    if(len(SMA_13arr) >= 2):
        if(SMA_5arr[-2] < SMA_8arr[-2] and SMA_5arr[-1] > SMA_13arr[-1] and bought == False and sold == True):
            print("Called Buy_Check from Moving_Avg; Rebound_Buy\n")
            limit_price = (float(arr[-1].close) * 1.01)
            make_buy_order(Ticker,limit_price, "market")

    if(len(SMA_5arrSlope) >= 2):
        if(SMA_5arrSlope[-2] < 0 and SMA_5arrSlope[-1] >= 0):
            if(SMA_8arrSlope[-2] < 0 and SMA_8arrSlope[-1] < 0 and SMA_13arrSlope[-2] < 0 and SMA_13arrSlope[-1] < 0 and bought == False and sold == True):
                polarity = True
                print("Called Buy_Check from Moving_Avg; Polarity Switch On\n")
                limit_price = (float(arr[-1].close) * 1.01)
                make_buy_order(Ticker,limit_price, "market")

def buy_check(arr):
    #wait until new candelstick becomes accessible (5 min)
    print("Entered Buy_Check\n")

    data = yfinance.download(tickers = Ticker, period ='5m', interval = '5m')

    arr.append(stick(data.iloc[0]['High'], data.iloc[0]['Low'], data.iloc[0]['Open'], data.iloc[0]['Close']))

    print(f"Stick.High = {arr[-1].high}")
    print(f"Stick.Low = {arr[-1].low}")
    print(f"Stick.Open = {arr[-1].open_price}")
    print(f"Stick.Close = {arr[-1].close}")

    # title = "DataTest.csv"
    # field_names = ["Price"]
    # dict = {"Price":data.iloc[0]['High']}

    # with open(title, "a") as file:
    #     writter = DictWriter(file, fieldnames=field_names)
    #     writter.writerow(dict)
    #     file.close()

    if(len(arr) > 4):
        arr.pop(0)

    print(f"Length of arr: {len(arr)}\n")

    if(len(arr) == 4 and bought == False and sold == True):
        print("Entered == 4 check")
        tof = True
        for i in range(2):
            if(arr[i].high <= arr[i + 1].high and arr[i].low <= arr[i + 1].low):
                tof = False
        #Make sure the open of the fourth is lower than the low of the third and close of the fourth is higher than the high of the first
        if(arr[3].open_price < arr[2].low and arr[3].close > arr[0].high and tof == True):
            limit_price = (float(arr[3].close) * 1.01)
            make_buy_order(Ticker,limit_price, "limit")

def sell_check():
    print("Entered Sell_Check\n")
    data = yfinance.download(tickers = Ticker, period ='1m', interval = '1m')

    if(data['Close'] >= (float(bought_price) * 1.015) and bought == True and sold == False):
        limit_price = float(bought_price) * 1.015
        make_sell_order(Ticker, limit_price, "limit")

#----------------------------------Buy/Sell Check Functions------------------

def make_buy_order(Ticker,limit,type):
    global stocks
    global capital
    global bought
    global bought_price
    global sold

    #----------------------Specify Global Variables--------------------------
    print("Triggered Buy Command\n")

    num_of_stocks = str(int(capital/limit))# Buys the greatest whole number of stocks
    # Update stocks and capital for later use
    stocks = num_of_stocks
    
    if(type == "limit"):
        order = api.submit_order(symbol=Ticker,
                                qty = num_of_stocks,
                                side ="buy",
                                type = type,
                                time_in_force ='day',
                                limit_price = limit)
    elif(type == "market"):
        order = api.submit_order(symbol=Ticker,
                                qty = num_of_stocks,
                                side ="buy",
                                type = type,
                                time_in_force ='day')
    # if order executed, set bought = True
    # capital -= float(num_of_stocks) * limit
    
    capital = api.get_account().portfolio_value - api.get_account().buying_power # capital = money invested in stocks

    bought_price = capital/stocks

    bought = True
    sold = False

def make_sell_order(Ticker,limit, type):
    print("Triggered Sell Command\n")
    global stocks
    global capital
    global bought
    global sold

    #----------------------Specify Global Variables---------------------------
    if(type == "limit"):
        order = api.submit_order(symbol=Ticker,
                                qty = stocks,
                                side ="sell",
                                type = type,
                                time_in_force ='day',
                                limit_price = limit)
    elif(type == "market"):
        order = api.submit_order(symbol=Ticker,
                                qty = stocks,
                                side ="sell",
                                type = type,
                                time_in_force ='day')
    # capital += float(stocks) * limit
    
    capital = api.get_account().buying_power

    stocks = 0
    #if order executed, set sold = True
    bought = False
    sold = True

#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

arr = []
counter = 0
x = 0
# cap_log.append(record("Principle", 0, 1000))

#---------------------------Declared Variables-------------------------------

key = 'PKGMTSNST26BQKLH9DPC'
sec = 'z6jSpVcdmDbYXyRXqnrnhdX6rgDCQUAuIkOzgHBk'
url = 'https://paper-api.alpaca.markets'
api = tradeapi.REST(key, sec, url, api_version='v2')
#Init our account var
account = api.get_account()
#Should print 'ACTIVE'
print(account.status)

#---------------------Initialized Order Placing API Info---------------------

print(f"\nbought: {bought}")
print(f"sold: {sold}\n")

while(True):
    check_time = datetime.today() #Gets current time
    if(x < 10):
        print(f"Current Time: {check_time}\n")
        x += 1
    if check_time.hour >= 6  and check_time.hour <= 13:
        start_time = time.time()

        print("Beginning Trades!\n")

        while(counter < 12): #Determines runtime
            end_time = time.time()

            # Prevents Infinite Loops caused by market ending
            if check_time.hour > 13:
                break

            #--------------Sell Check----------------
            if bought == True and sold == False:
                sell_check()
            #--------------Buy Check-----------------
            if start_time + timestep <= end_time:
                start_time = time.time()

                buy_check(arr)

                moving_avg(arr)

                counter += 1
                print(f"\n--------------- Finished Iteration {counter} ---------------\n")
        break

save_info()
#---------------------------Initialized Time/Main loop-----------------------
# api.get_account().portfolio_value - buying power + value of stocks we own  
# api.get_account().buying_power - buying power