import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import PortfolioHistory
from numpy import diff
from pandas._libs.tslibs import Timestamp
import yfinance
import time
from datetime import datetime
import pandas as pd
import csv
from csv import DictWriter, writer, reader


from Graph import graph
from Alpaca_config import KEY, SEC, URL
from Percent_Change import percent_change_update
from Save_Info import save_info
from Hard_Sell import hard_sell
from Buy import buy
from Sell import sell
from Email import email
from Symbols import *
from Update_Saved_Info import update
# import ResearchTeam

global timestep
timestep = 300

global symbol
symbol = symbol13

# symbol = ResearchTeam.run()
# print(symbol)
# x = input("Paused")

global timeframe
timeframe = '2d'

global increment
increment = '5m'

global IP #Initilization Period = number of points over which the code remains dormant prior to trading 
IP = 78

global IPstr
IPstr = '1d'

global filelist
filelist = []

global netcapital
netcapital = 0

global netsectionval
netsectionval = 0

global bestsectionval
bestsectionval = 0

global curr_time
curr_time = ""

update(symbol)      #Updates Saved Info


class stock:
    changes = []
    profit = []
    profit_per_trade = 0
    limit = 0
    Ticker = ""
    quantity = 0
    capital = 0
    principle = 0
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
    slopecounter = 0
    setcounter = 2
    bestsale = 0

    AF_increment = 0.08
    AF_limit = 0.2
    PSARMatrix = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
    PSARcounter = 0
    AF_incrementlong = 0.08
    AF_limitlong = 0.2
    PSARMatrixlong = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]

    t = []
    close = []
    open = []
    buyindicator = []
    soldindicator = []

    histShortPSAR = []
    histLongPSAR = []

    RSI = []
    ut1 = 0
    dt1 = 0

    buy_log = []
    sell_log = []

    hard_sell_limit = 0
    hard_sell = False
    hard_sell_time = ""

    curr_EMA12 = 0
    EMA_12_arr = []
    curr_EMA26 = 0
    EMA_26_arr = []
    MACD_val = []
    MACD_EMA9 = 0
    MACD9_arr = []

    high = []
    low = []

    MACD_check = False

    def __init__(self,first_line):
        self.Ticker = str(first_line[0])
        self.quantity = int(first_line[1])
        self.capital = float(first_line[2])
        self.principle = float(first_line[2])
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
        self.curr_EMA = 0
        self.prev_EMA = 0
        self.EMA_Slope = 0
        self.counter = 2
        self.slopecounter = 0
        self.setcounter = 2
        self.bestsale = 0
        self.AF_increment = 0.01#0.005
        self.AF_limit = 0.2
        self.PSARMatrix = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
        self.PSARcounter = 1
        self.AF_incrementlong = 0.01#0.005
        self.AF_limitlong = 0.2
        self.PSARMatrixlong = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
        self.t = []
        self.close = []
        self.open = []
        self.buyindicator = []
        self.soldindicator = []
        self.histShortPSAR = []
        self.histLongPSAR = [] 
        self.RSI = []
        self.ut1 = 0.00001
        self.dt1 = 0.00001
        self.buy_log = []
        self.sell_log = []
        self.hard_sell_limit = -0.2
        self.hard_sell = False
        self.hard_sell_time = ""
        
        self.curr_EMA12 = 0
        self.EMA_12_arr = []
        self.curr_EMA26 = 0
        self.EMA_26_arr = []
        self.MACD_val = []
        self.MACD_EMA9 = 0
        self.MACD9_arr = []

        self.high = []
        self.low = []

        self.MACD_check = False

    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")

#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

if __name__ == "__main__":
    
    iterations = 0
    for i in range(len(symbol)):
        data = yfinance.download(tickers = symbol[i], period = timeframe, interval = increment)

        title = f"TestDataSet{i}.csv"
        filelist.append(title)

        data.to_csv('ALLData.csv')

        date = []

        with open('ALLData.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)

            for row in reader:
                date.append(row[0])

        with open(title, 'w', newline = '') as csvfile:
            fieldnames = ['Open', "High", "Low", "Close", "Adj Close", "Volume", 'Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            temp = len(data) - 2
            if(i == 0):
                iterations = temp
            if(iterations > temp):
                iterations = temp

            writer.writeheader()

            for j in range(len(data)):
                writer.writerow({'Open': data.iloc[j]['Open'], 'High': data.iloc[j]['High'], 'Low': data.iloc[j]['Low'], 'Close':data.iloc[j]['Close'], 'Adj Close':data.iloc[j]['Adj Close'], 'Volume':data.iloc[j]['Volume'], 'Date':date[j]})
            csvfile.close()

    counter = 0
    x = 0

    key = KEY
    sec = SEC
    url = URL
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
        percent_change_update(stocks_list[i], i, 1, filelist, timestep)

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
                    percent_change_update(stocks_list[i], i, 0, filelist, timestep)
                    hard_sell(stocks_list[i],curr_time)
                    stocks_list[i].setcounter += 1

                
                    if(IP == 0):

                        if(stocks_list[i].hard_sell == False):
                            
                            # if(stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1]):
                            if(stocks_list[i].changes[-1] < 0):

                                # if(stocks_list[i].RSI[-1] > 30):
                                if((stocks_list[i].PSARMatrix[0][7] == 0) or (stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1]  and stocks_list[i].EMA_Slope < 0)):
                                    print("Entered Sell Check")
                                    if(stocks_list[i].bought == True and stocks_list[i].sold == False):

                                        # if(stocks_list[i].bought_price <= stocks_list[i].limit):

                                            sell(stocks_list[i])
                                                
                                            # stocks_list[i].soldindicator[-1] = stocks_list[i].close[-1]

                                            print(f"Made a profit of: {stocks_list[i].profit[-1]}")

                                            continue
                                
                                # if(len(stocks_list[i].RSI) >= 2):
                                #     if(stocks_list[i].RSI[-1] > 70 or stocks_list[i].RSI[-2] > 70 and stocks_list[i].RSI[-1] < stocks_list[i].RSI[-2]):
                                #         if(stocks_list[i].bought == True and stocks_list[i].sold == False):

                                #             # if(stocks_list[i].bought_price <= stocks_list[i].limit):
                                #                 sell(stocks_list[i])
                                                
                                #                 stocks_list[i].soldindicator[-1] = stocks_list[i].close[-1]

                                #                 print(f"Made a profit of: {stocks_list[i].profit[-1]}")

                                #                 continue

                            elif(stocks_list[i].changes[-1] > 0):
                                if((stocks_list[i].MACD_val[-1] > stocks_list[i].MACD9_arr[-1] and stocks_list[i].PSARMatrixlong[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1)  or (stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1) or (stocks_list[i].RSI[-2] < 30 and stocks_list[i].RSI[-2] < stocks_list[i].RSI[-1])):#or stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1
                                    if(stocks_list[i].RSI[-1] < 70):
                                        # if(stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1):
                                            if(stocks_list[i].bought == False and stocks_list[i].sold == True):
                                                if(stocks_list[i].EMA_Slope > 0):
                                                    buy(stocks_list[i],curr_time)
                                                    stocks_list[i].buyindicator[-1] = stocks_list[i].close[-1]
                                            else:
                                                print("Entered buying check but did not meet requirements")
                                        
                                    
                            print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
                        
                        else:
                            if(stocks_list[i].MACD_val[-2] > stocks_list[i].MACD9_arr[-2] and stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1]):
                                stocks_list[i].hard_sell = False
                if(IP > 0):
                    IP -= 1
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
            stocks_list[i].soldindicator[-1] = stocks_list[i].close[-1]
            print(f"Ending capital for {stocks_list[i].Ticker} is {stocks_list[i].capital}")
            sell(stocks_list[i],curr_time)
            print(f"Ending section value for {stocks_list[i].Ticker} is {stocks_list[i].section_val}")
            print(f"Best profit for {stocks_list[i].Ticker} is {stocks_list[i].bestprofit} at {stocks_list[i].bestsale}")
        print(f"{stocks_list[i].profitlog}\n")
        netsectionval += stocks_list[i].section_val
        if(len(stocks_list[i].profitlog) != 0):
            bestsectionval += stocks_list[i].bestprofit
        else:
            bestsectionval += stocks_list[i].capital

    for i in range(1):
        print(f"Net capital: {netcapital}\n")
        print(f"Net section value: {netsectionval}")
        print(f"Percent change: {(((netsectionval - netcapital)/netcapital)*100)}%\n")
        print(f"Best section value: {bestsectionval}")
        print(f"Best percent change: {(((bestsectionval - netcapital)/netcapital)*100)}%\n")

    graph(stock, stocks_list)

    save_info(stocks_list, netcapital, netsectionval, bestsectionval,timeframe,increment,IPstr)

    # email()
    #Use Double and Triple EMA instead of EMA
    #Implement a hardsell check