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

    def __init__(self,first_line):
        self.Ticker = str(first_line[0])
        self.quantity = int(first_line[1])
        self.capital = float(first_line[2])
        self.sold = bool(int(first_line[3]))
        self.bought = bool(int(first_line[4]))
        self.bought_price = float(first_line[5])
        self.cap_log = []
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
    
    stock.capital = float(api.get_account().portfolio_value) - float(api.get_account().buying_power) # capital = money invested in stocks

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
    
    stock.capital = api.get_account().buying_power

    stock.quantity = 0
    stock.bought = False
    stock.sold = True

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

key = 'PK4KU0RNKHZFR4RLC63B'
sec = '9vwHOkN6FwDloDxoIRj0B6QtUBCWeai2MKw9dbTF'
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
                    print("Check to sell\n") #Comment this out later

            #--------------Buy Check-----------------
            if start_time + timestep <= end_time:
                start_time = time.time()

                # update stock info and check for buying conditions for each stock in stocks_list
                for i in range(stocks):
                    print(f"---------------{stocks_list[i].Ticker} Stock Start ---------------")
                    


                                        

                    print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
                counter += 1
                print(f"--------------- Finished Iteration {counter} ---------------\n")
        break

save_info(stocks_list)
#---------------------------Initialized Time/Main loop-----------------------