import alpaca_trade_api as tradeapi
import yfinance
import time
from datetime import datetime

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

def make_buy_order(Ticker,limit):
    print("Triggered Buy Command")
    # order = api.submit_order(symbol=Ticker,
    #                         qty="10",
    #                         side="buy",
    #                         type='limit',
    #                         time_in_force='day',
    #                         limit_price=limit)

arr = []
counter = 0
Ticker = "FB"
x = 0

while(True):
    check_time = datetime.utcnow().time() #Gets current time
    if(x < 10):
        print(f"Current Time: {check_time}\n")
        x += 1

    if check_time.hour >= 0 and check_time.minute >= 0:
        start_time = time.time()

        print("Beginning Trades!\n")

        while(counter < 12):
            end_time = time.time()
            # print(f"if check; {datetime.utcnow().time()}\n")
            if start_time + 10 <= end_time:
                start_time = time.time()

                #wait until new candelstick becomes accessible (5 min)
                # data = yfinance.download(tickers = Ticker, period ='5m', interval = '5m')
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
                    #Make sure the open of the fourth is lower than the low of the third and close of the fourth is higher than the high of the first
                    if(arr[3].open_price < arr[2].low and arr[3].close > arr[0].high and tof == True):
                        limit_price = (float(arr[3].close) * 1.01)
                        make_buy_order(Ticker,limit_price)

                counter += 1
                print("\n")

        break

#---------------------------Initialized Time/Main loop-----------------------

# Test Run:
# High | Low | Open | Close
# 10     6     9      7
# 15     8     10     13
# 10     6     9      7
# 5      3     4      3
# 20     2     2      18 
