import alpaca_trade_api as tradeapi
import yfinance
import time
from datetime import datetime
#--------------------Import Statements----------------------
# Update Idea: Save information in CSV file and load in information from that file the next time 
# this code is run to initialize the variables to what they were at the end of the prior cycle
global stocks
stocks = 0

global capital
capital = 1000

global sold
sold = True

global bought
bought = False

global bought_price
bought_price = 0
#--------------------Global Var Declaration------------------
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
#--------------------Sticks Construction---------------------
def buy_check(arr):
    High = input("Enter High Value: ")
    Low = input("Enter Low Value: ")
    Open_val = input("Enter Open Value: ")
    Close = input("Enter Close Value: ")
    arr.append(stick(High,Low,Open_val,Close))
    # arr.append(stick(data['High'], data['Low'], data['Open'], data['Close']))
    if(len(arr) > 4):
        arr.pop(0)

    print(f"Length of arr: {len(arr)}\n")

    if(len(arr) == 4):
        print("Entered == 4 check")
        tof = True
        for i in range(2):
            if(arr[i].high <= arr[i + 1].high and arr[i].low <= arr[i + 1].low):
                tof = False
        #Make sure the open of the fourth is lower than the low of the third and close of
        #the fourth is higher than the high of the first
        if(arr[3].open_price < arr[2].low and arr[3].close > arr[0].high and tof == True):
            limit_price = (float(arr[3].close) * 1.01)
            make_buy_order(Ticker,limit_price)
#----------------------------------Buy/Sell Check Functions------------------------------------
def make_buy_order(Ticker, limit):
    global stocks
    global capital
    num_of_stocks = str(int(capital/limit)) #Buys the greatest whole number of stocks
    # Update stocks and capital for later use
    stocks = num_of_stocks
    capital -= float(num_of_stocks) * limit
    print(f"Executed a Buy Order!\nBought {stocks} stocks of {Ticker}")
    # order = api.submit_order(symbol=Ticker,
    #                         qty = num_of_stocks,
    #                         side ="buy",
    #                         type ='limit',
    #                         time_in_force ='day',
    #                         limit_price = limit)
    #if order executed, set bought = True


def make_sell_order(limit_price):
    print("Exectuted Sell Order\n")

    #if order executed, set sold = True


#---------------------Execute Buy and Sell Functions-------------------------

#---------------------------Beginning of the Code----------------------------
arr = []
counter = 0
Ticker = "FB"
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
while(True):
    check_time = datetime.utcnow().time() #Gets current time
    if check_time.hour >= 0 and check_time.minute >= 0:
        start_time = time.time()

        while(counter < 5): #Determines runtime
            end_time = time.time()
            #--------------Sell Check----------------
            # if bought == True:
                #Check to see if profitable to sell
            # if bought == True:
                #Data = api.
            #--------------Buy Check-----------------
            if start_time + 10 <= end_time:
                start_time = time.time()

                buy_check(arr)

                print(f"In the main loop, capital = {capital}\n")
                print(f"In the main loop, stocks = {stocks}\n")

                counter += 1
        
        break

#---------------------------Initialized Time/Main loop-----------------------  

# Test Run:
# High | Low | Open | Close
# 10     6     9      7
# 15     8     10     13
# 10     6     9      7
# 5      3     4      3
# 20     2     2      18 
