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
import matplotlib.pyplot as plt

global timestep
timestep = 300

global symbol
# symbol = ['AMZN','GOOG','TGT','MSFT','AAPL','FB','ADBE','JWN','UPWK','LUV','BA','DIS','CCL','BAC','GE','SBUX','^GSPC']
symbol = ['AMC']

global timeframe
timeframe = '2d'

global increment
increment = '5m'

global tradingbound
tradingbound = 0.07

global filelist
filelist = []

global netcapital
netcapital = 0

global netsectionval
netsectionval = 0

class stock:
    close_arr = []
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
    EMA_log =[]
    curr_EMA = 0
    prev_EMA = 0
    EMA_slope = 0
    counter = 0
    setcounter = 2
    bestsale = 0
    MACD = []
    signal = []

    def __init__(self,first_line):
        self.Ticker = str(first_line[0])
        self.quantity = int(first_line[1])
        self.capital = float(first_line[2])
        self.sold = bool(int(first_line[3]))
        self.bought = bool(int(first_line[4]))
        self.bought_price = float(first_line[5])
        self.close_arr = []
        self.profit = []
        self.limit = 0
        self.profit_per_trade = 0
        self.section_val = float(first_line[2])
        self.bestprofit = 0
        self.profitlog = []
        self.EMA_log = []
        self.curr_EMA = 0
        self.prev_EMA = 0
        self.EMA_Slope = 0
        self.counter = 0
        self.setcounter = 2
        self.bestsale = 0
        self.MACD = []
        self.signal = []

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

def MACD_update(stock, x):
    # data = yfinance.download(tickers = stock.Ticker, period ='5m', interval = '5m')
    # print(data)
    global filelist
    global timestep

    file = open(str(filelist[x]))
    # file = open('TestDataSet.csv')
    csv_reader = csv.reader(file)

    # csv_reader = reader(read_obj)

    i = 0

    for row in csv_reader:
        if(i % 2 == 0):
            if(i/2 == stock.setcounter): #Get current point's data
                stock.close_arr.append(float(row[3]))
                print(stock.close_arr[-1])
                break
        i += 1

    # stock.slopes.append((float(data.iloc[1]['Close'] - data.iloc[0]['Close'])/float(data.iloc[0]['Close'])) * 100)
    # if(stock.setcounter == 0):

    stock.limit = stock.close_arr[-1] * 1.00

    #Update the EMA; EMA = Averge Price over some interval 't0 - tf'
    stock.prev_EMA = stock.curr_EMA
    stock.curr_EMA = stock.close_arr[-1]*(2/(stock.counter+1)) + stock.curr_EMA*(1 - (2/(stock.counter + 1)))
   
    stock.EMA_log.append(stock.curr_EMA)
    
    #MACD = EMA_10min - EMA_15min 0 
    curr_EMA15 = 0
    curr_EMA10 = 0
    if(stock.counter >= 3): 
        prev_EMA = stock.close_arr[stock.counter - 3]
        curr_EMA15 = stock.close_arr[-1]*(2/(stock.counter+1)) + prev_EMA*(1 - (2/(stock.counter + 1)))
    if(stock.counter >= 2):
        prev_EMA = stock.close_arr[stock.counter - 2]
        curr_EMA10 = stock.close_arr[-1]*(2/(stock.counter+1)) + prev_EMA*(1 - (2/(stock.counter + 1)))
    if(stock.counter >= 3): 
        stock.MACD.append(curr_EMA10 - curr_EMA15)
    
    #Signal = EMA_5min
    if(stock.counter >= 4):
        stock.signal.append(stock.MACD[-1]*(2/(stock.counter + 1)) + stock.MACD[-2]*(1 - (2/(stock.counter + 1))))
    
    stock.counter += 1


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
    # MACD_update(stocks_list[i], i)

while(True):
    check_time = datetime.today() #Gets current time
    if(x < 10):
        print(f"Current Time: {check_time}\n")
        x += 1
    if check_time.hour >= 0  and check_time.hour >= 0:
        # start_time = time.time()

        print("Beginning Trades!\n")

        while(counter < iterations):
            # end_time = time.time()
            
            # if check_time.hour > 13: 
            #     break

            # if start_time + timestep <= end_time:
            #     start_time = time.time()
                
            for i in range(stocks):
                print(f"---------------{stocks_list[i].Ticker} Stock Start ---------------")
                MACD_update(stocks_list[i], i)

                # print(f"MACD: {stocks_list[i].MACD}")
                # print(f"Signal: {stocks_list[i].signal}")
                # print(f"Close: {stocks_list[i].close_arr[-1]}")

                stocks_list[i].setcounter += 1
                # Enter Checks for holding, sell, and buying
                if(len(stocks_list[i].MACD) >= 1 and len(stocks_list[i].signal) >= 1):
                    if(stocks_list[i].MACD[-1] > stocks_list[i].signal[-1]):
                        if(stocks_list[i].bought == False and stocks_list[i].sold == True):
                            buy(stocks_list[i])
                        else:
                            print("Entered buy check but already bought stocks")
                    elif(stocks_list[i].MACD[-1] <= stocks_list[i].signal[-1]):
                        if(stocks_list[i].bought == True and stocks_list[i].sold == False):
                            sell(stocks_list[i])
                        else:
                            print("Entered sell check but already sold stocks")

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

print(f"Net capital: {netcapital}")
print(f"Net section value: {netsectionval}")
print(f"Percent change: {(((netsectionval - netcapital)/netcapital)*100)}%")

t = [i for i in range(0,len(stocks_list[0].MACD))]
t1 = [i for i in range(0,len(stocks_list[0].signal))]
t2 = [i for i in range(0,len(stocks_list[0].close_arr))]
# print(t)

plt.plot(t, stocks_list[0].MACD, 'b')
plt.show()
plt.plot(t1, stocks_list[0].signal, '#ffa500')
plt.show()
    # x = int(input("Paused; Enter number to continue"))

# save_info(stocks_list)