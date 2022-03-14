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

#--------------------Import Statements----------------------

# Update Idea: Save information in CSV file and load in information from that file the next time 
# this code is run to initialize the variables to what they were at the end of the prior cycle

global timestep
timestep = 300

#--------------------Global Variables-----------------------
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

class stock:
    arr = []
    Ticker = ""
    quantity = 0
    capital = 0
    sold = True
    bought = False
    bought_price = 0
    cap_log = []
    SMA_5arr = []
    SMA_8arr = []
    SMA_13arr = []
    SMA_5arrSlope = []
    SMA_8arrSlope = []
    SMA_13arrSlope = []
    polarity = False

    def __init__(self,first_line):
        self.Ticker = str(first_line[0])
        self.quantity = int(first_line[1])
        self.capital = float(first_line[2])
        self.sold = bool(int(first_line[3]))
        self.bought = bool(int(first_line[4]))
        self.bought_price = float(first_line[5])
        self.cap_log = []
        self.SMA_5arr = []
        self.SMA_8arr = []
        self.SMA_13arr = []
        self.SMA_5arrSlope = []
        self.SMA_8arrSlope = []
        self.SMA_13arrSlope = []
        self.arr = []

    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")
#--------------------Class Construction---------------------

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

def moving_avg_update(stock):
    print(f"{stock.Ticker} Entered Moving_Avg_Update\n")

    stock.SMA_5 = 0
    stock.SMA_8 = 0
    stock.SMA_13 = 0

    data = yfinance.download(tickers = stock.Ticker, period ='2h', interval = '5m')

    for i in range(13):
        stock.SMA_13 += data.iloc[-1*i]['Close']
        if(i < 8):
            stock.SMA_8 += data.iloc[-1*i]['Close']
            if(i < 5):
                stock.SMA_5 += data.iloc[-1*i]['Close']
        

    stock.SMA_13 = float(stock.SMA_13/13)
    stock.SMA_8 = float(stock.SMA_8/8)
    stock.SMA_5 = float(stock.SMA_5/5)

    print(f"\nStock Symbol = {stock.Ticker}")
    print(f"SMA_13 = {stock.SMA_13}")
    print(f"SMA_8 = {stock.SMA_8}")
    print(f"SMA_5 = {stock.SMA_5}")

    stock.SMA_13arr.append(stock.SMA_13)
    stock.SMA_8arr.append(stock.SMA_8)
    stock.SMA_5arr.append(stock.SMA_5)

    if(len(stock.SMA_13arr) >= 2):
        stock.SMA_13arrSlope.append(float(stock.SMA_13arr[-1] - stock.SMA_13arr[-2])/float(timestep/60))
        stock.SMA_8arrSlope.append(float(stock.SMA_8arr[-1] - stock.SMA_8arr[-2])/float(timestep/60))
        stock.SMA_5arrSlope.append(float(stock.SMA_5arr[-1] - stock.SMA_5arr[-2])/float(timestep/60))
        print(f"\nStock Symbol = {stock.Ticker}")
        print(f"SMA_13arr.[latest] = {stock.SMA_13arr[-1]}")
        print(f"SMA_8arr.[latest] = {stock.SMA_8arr[-1]}")
        print(f"SMA_5arr.[latest] = {stock.SMA_5arr[-1]}")

    print("\n")

def moving_avg_buy(stock, arr):
    # Use an interpolating method to create an approximation of the function given several closing points
    # and use Euler's Method w/ PC Method to predict values
    print(f"{stock.Ticker} Entered Moving_Avg_Buy\n")

    # Currently set to execute market orders 

    if(len(stock.SMA_13arr) >= 2):
        if(stock.SMA_5arr[-2] < stock.SMA_8arr[-2] and stock.SMA_5arr[-1] > stock.SMA_13arr[-1] and stock.bought == False and stock.sold == True):
            print("Called Buy_Check from Moving_Avg; Rebound_Buy\n")
            limit_price = (float(arr[-1].close) * 1.01)
            make_buy_order(stock.Ticker,limit_price, "market", stock)

    if(len(stock.SMA_5arrSlope) >= 2):
        if(stock.SMA_5arrSlope[-2] < 0 and stock.SMA_5arrSlope[-1] >= 0):
            if(stock.SMA_8arrSlope[-2] < 0 and stock.SMA_8arrSlope[-1] < 0 and stock.SMA_13arrSlope[-2] < 0 and stock.SMA_13arrSlope[-1] < 0 and stock.bought == False and stock.sold == True):
                stock.polarity = True
                print("Called Buy_Check from Moving_Avg; Polarity Switch On\n")
                limit_price = (float(arr[-1].close) * 1.01)
                make_buy_order(stock.Ticker,limit_price, "market", stock)
    
    print("\n")

def moving_avg_sell(stock):
    print(f"{stock.Ticker} Entered Moving_Avg_Sell\n")
    
    if(stock.SMA_5 > stock.SMA_8 and stock.SMA_5 > stock.SMA_13 and stock.bought == True and stock.sold == False):
        print("Called Sell_Check from Moving_Avg; Rebound_Sell\n")
        
        limit_price = float(stock.bought_price) * 1.015
        make_sell_order(stock.Ticker, limit_price, "market", stock)

    if(len(stock.SMA_5arrSlope) >= 1):
        if(stock.SMA_5arrSlope[-1] < 0 and stock.SMA_8arrSlope[-1] > 0 and stock.polarity == True and stock.bought == True and stock.sold == False):
            print("Called Sell_Check from Moving_Avg; Polarity Switch Off\n")
            stock.polarity = False
            
            limit_price = float(stock.bought_price) * 1.015
            make_sell_order(stock.Ticker, limit_price, "market", stock)
    
    print("\n")

def arr_update(stock, arr):
    
    data = yfinance.download(tickers = stock.Ticker, period ='5m', interval = '5m')

    arr.append(stick(data.iloc[0]['High'], data.iloc[0]['Low'], data.iloc[0]['Open'], data.iloc[0]['Close']))

    print(f"Stick.High = {arr[-1].high}")
    print(f"Stick.Low = {arr[-1].low}")
    print(f"Stick.Open = {arr[-1].open_price}")
    print(f"Stick.Close = {arr[-1].close}")

    if(len(arr) > 4):
        arr.pop(0)

    print(f"Length of arr: {len(arr)}\n\n")

def three_line_buy(stock, arr):
    #wait until new candelstick becomes accessible (5 min)
    print(f"{stock.Ticker} Entered Buy_Check\n")

    if(len(arr) == 4 and stock.bought == False and stock.sold == True):
        print("Entered == 4 check")
        tof = True
        for i in range(2):
            if(arr[i].high <= arr[i + 1].high and arr[i].low <= arr[i + 1].low):
                tof = False
        #Make sure the open of the fourth is lower than the low of the third and close of the fourth is higher than the high of the first
        if(arr[3].open_price < arr[2].low and arr[3].close > arr[0].high and tof == True):
            limit_price = (float(arr[3].close) * 1.01)
            make_buy_order(stock.Ticker,limit_price,"limit", stock)

#----------------------------------Buy/Sell Check Functions------------------

def make_buy_order(Ticker,limit,type,stock):

    print("Triggered Buy Command\n")

    stock.quantity = str(int(stock.capital/limit))# Buys the greatest whole number of stocks and update stocks and capital for later use

    if(type == "limit"):
        order = api.submit_order(symbol=Ticker,
                                qty = stock.quantity,
                                side ="buy",
                                type = type,
                                time_in_force ='day',
                                limit_price = limit)
    elif(type == "market"):
        order = api.submit_order(symbol=Ticker,
                                qty = stock.quantity,
                                side ="buy",
                                type = type,
                                time_in_force ='day')
    
    # time.sleep(30)
    open_order = api.list_orders(
        status='open',
        limit=1,
        nested=True  # show nested multi-leg orders
    )
    if not(open_order.status=="filled") :
        cancel_thread = threading.Thread(target="cancel_order", args=(open_order,))
        cancel_thread.start()

    
    stock.capital = api.get_account().portfolio_value - api.get_account().buying_power # capital = money invested in stocks

    stock.bought_price = stock.capital/stock.quantity

    stock.bought = True
    stock.sold = False

def make_sell_order(Ticker,limit,type,stock):
    print("Triggered Sell Command\n")
    
    if(type == "limit"):
        order = api.submit_order(symbol=Ticker,
                                qty = stock.quantity,
                                side ="sell",
                                type = type,
                                time_in_force ='day',
                                limit_price = limit)
    elif(type == "market"):
        order = api.submit_order(symbol=Ticker,
                                qty = stock.quantity,
                                side ="sell",
                                type = type,
                                time_in_force ='day')
    
    # time.sleep(30)
    open_order = api.list_orders(
        status='open',
        limit=1,
        nested=True  # show nested multi-leg orders
    )
    if not(open_order.status=="filled") :
        cancel_thread = threading.Thread(target="cancel_order", args=(open_order,))
        cancel_thread.start()
    
    stock.capital = api.get_account().buying_power

    stock.quantity = 0
    #if order executed, set sold = True
    stock.bought = False
    stock.sold = True

def cancel_order(open_order):
    time.sleep(1200)
    if not(open_order.status=="filled") :
        cancel_order(open_order.id)
#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

counter = 0
x = 0

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
for i in range(stocks):
    print(f"\nStock Symbol: {stocks_list[i].Ticker}")
    print(f"bought: {stocks_list[i].bought}")
    print(f"sold: {stocks_list[i].sold}\n")
    

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

            # Prevents Infinite Loops caused by market ending; Disable for testing
            if check_time.hour > 13:
                break
                
            for i in range(stocks):
                #--------------Sell Check----------------
                if stocks_list[i].bought == True and stocks_list[i].sold == False:
                    # sell_check(stocks_list[i])
                    moving_avg_sell(stocks_list[i])
            #--------------Buy Check-----------------
            if start_time + timestep <= end_time:
                start_time = time.time()

                # update stock info and check for buying conditions for each stock in stocks_list
                for i in range(stocks):
                    print(f"---------------{stocks_list[i].Ticker} Stock Start ---------------")
                    # Update Candlestick Data and Moving Averages Data
                    arr_update(stocks_list[i],stocks_list[i].arr)
                    moving_avg_update(stocks_list[i])
                    # Check if its worth buying a stock
                    three_line_buy(stocks_list[i], stocks_list[i].arr)
                    moving_avg_buy(stocks_list[i], stocks_list[i].arr)                    

                    print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
                counter += 1
                print(f"--------------- Finished Iteration {counter} ---------------\n")
        break

save_info(stocks_list)
#---------------------------Initialized Time/Main loop-----------------------
# api.get_account().portfolio_value - buying power + value of stocks we own  
# api.get_account().buying_power - buying power

# def cancel_order(open_order):
# time.sleep(1200)
# if not(open_order.status=="filled") :
#     cancel_order(open_order.id)

# time.sleep(30)
#     open_order = api.list_orders(
#         status='open',
#         limit=1,
#         nested=True  # show nested multi-leg orders
#     )
#     if not(open_order.status=="filled") :
#         cancel_thread = threading.Thread(target=cancel_order, args=(open_order,))
#         cancel_thread.start()


#------------------------------Retired Functions-----------------------------
# def sell_check(stock):
#     print("Entered Sell_Check\n")
#     data = yfinance.download(tickers = stock.Ticker, period ='1m', interval = '1m')

#     if(data['Close'] >= (float(stock.bought_price) * 1.015) and stock.bought == True and stock.sold == False):
#         limit_price = float(stock.bought_price) * 1.015
#         make_sell_order(stock.Ticker, limit_price, "limit", stock)