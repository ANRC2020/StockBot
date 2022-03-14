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
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import mimetypes
import json

from Save_Info import update_mass_stocks
# import ResearchTeam

global timestep
timestep = 300

global symbol
symbol = ['AAPL']
# symbol = ResearchTeam.run()
# print(symbol)
# x = input("Paused")

global timeframes
timeframes = ['52wk', '260d'] # (1 + 5) + 5 + 5 -> 3 weeks ago
# timeframe = '6d'

global increments
increments = ['1wk', '3d']
# increment = '5m'

global IP #Initilization Period = number of points over which the code remains dormant prior to trading 
IP = 0

global EP
EP = [49, 249]
# EP = -1

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

global jsonerr
jsonerr = 0

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

    AF_increment = 0.02
    AF_limit = 0.2
    PSARMatrix = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
    PSARcounter = 0
    AF_incrementlong = 0.02
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

    RSILong = []
    ut1Long = 0
    dt1Long = 0

    buy_log = []
    sell_log = []

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

    stoplosslimit = 0
    target = 0

    anchor15 = []
    anchor30 = []

    momentum = []
    momentum_EMA_log = []
    curr_momentum_EMA = 0
    prev_momentum_EMA = 0
    momentum_counter = 2
    
    momentumlong = []
    momentum_EMA_loglong = []
    curr_momentum_EMAlong = 0
    prev_momentum_EMAlong = 0
    momentum_counterlong = 2
    

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
        self.AF_increment = 0.02
        self.AF_limit = 0.2
        self.PSARMatrix = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
        self.PSARcounter = 1
        self.AF_incrementlong = 0.02
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

        self.RSILong = []
        self.ut1Long = 0.00001
        self.dt1Long = 0.00001

        self.buy_log = []
        self.sell_log = []
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

        self.stoplosslimit = 0
        self.target = 0

        self.anchor15 = []
        self.anchor30 = []

        self.momentum = []
        self.momentumlong = []
        self.momentum_EMA_log = []
        self.curr_momentum_EMA = 0
        self.prev_momentum_EMA = 0
        self.momentum_counter = 2

    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")

with open('Saved_Info_Initial.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['symbol','quantity','capital','sold','bought','bought_price']
        writer.writerow(header)
        for stock in symbol:
            row = [stock,'0','10000','1','0','0']
            writer.writerow(row)
        file.close()

def makestock(row):
    tempstock = stock(row)

    return tempstock

def email():
    host_address = 'stock.trader.report@gmail.com'
    send_to_addresses = 'siddiquiabbas22@gmail.com, ravirahul660@gmail.com'

    fileToSend = "ActivityLog.txt"

    msg = MIMEMultipart()
    msg['From'] = host_address
    fp = open(fileToSend, "rb")
    attachment = MIMEBase('txt','txt')
    attachment.set_payload(fp.read())
    fp.close()
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)

    server = smtplib.SMTP(host = 'smtp.gmail.com', port = 587)
    server.starttls()
    server.login('stock.trader.report@gmail.com', 'qwert#12345')

    # for email in send_to_addresses:
    msg['To'] = send_to_addresses
    server.send_message(msg)

    server.quit()

def hard_sell(stock):

    global curr_time

    if(stock.bought == True and stock.sold == False):
        itt = 3

        if(len(stock.close) >= 2):
            if(stock.low[-1] < stock.low[-2]):    
                high_pred = []
                low_ped = []
                curr_high = stock.high[-1]
                curr_low = stock.low[-1]
                low_change = stock.low[-1] - stock.low[-2]
                high_change = stock.high[-1] - stock.high[-2]

                for i in range(itt):
                    high_pred.append(curr_high + high_change)
                    low_ped.append(curr_low + low_change)

                    curr_high = curr_high + high_change
                    curr_low = curr_low + low_change

                localPSARMatrix = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
                localPSARMatrix[0] = stock.PSARMatrix[0]

                arr = []

                for i in range(itt):
                    arr.append(localPSARMatrix[0][2])

                    localPSARMatrix[1][0] = high_pred[i]
                    localPSARMatrix[1][1] = low_ped[i]

                    if(localPSARMatrix[0][7] == 1 and localPSARMatrix[0][2] + localPSARMatrix[0][6] > localPSARMatrix[1][1]):
                        localPSARMatrix[1][2] = localPSARMatrix[0][3]
                    else:
                        if(localPSARMatrix[0][7] == 0 and localPSARMatrix[0][2] + localPSARMatrix[0][6] < localPSARMatrix[1][0]):
                            localPSARMatrix[1][2] = localPSARMatrix[0][3]
                        else:
                            localPSARMatrix[1][2] = localPSARMatrix[0][2] + localPSARMatrix[0][6]
                    #PSAR Update END

                    # print(f"PSAR Value: {localPSARMatrix[1][2]}")

                    #BULLBEAR Update START
                    if(localPSARMatrix[1][2] < localPSARMatrix[1][0]):
                        localPSARMatrix[1][7] = 1
                    else:
                        if(localPSARMatrix[1][2] > localPSARMatrix[1][1]):
                            localPSARMatrix[1][7] = 0
                    #BULLBEAR Update END

                    # print(f"BULLBEAR Value: {localPSARMatrix[1][7]}")

                    #EP Update START
                    if(localPSARMatrix[1][7] == 1 and localPSARMatrix[1][0] > localPSARMatrix[0][3]):
                        localPSARMatrix[1][3] = localPSARMatrix[1][0]
                    else:
                        if(localPSARMatrix[1][7] == 1 and localPSARMatrix[1][0] <= localPSARMatrix[0][3]):
                            localPSARMatrix[1][3] = localPSARMatrix[0][3]
                        else:
                            if(localPSARMatrix[1][7] == 0 and localPSARMatrix[1][1] < localPSARMatrix[0][3]):
                                localPSARMatrix[1][3] = localPSARMatrix[1][1]
                            else:
                                if(localPSARMatrix[1][7] == 0 and localPSARMatrix[1][1] >= localPSARMatrix[0][3]):
                                    localPSARMatrix[1][3] = localPSARMatrix[0][3]

                    #EP Update END

                    # print(f"EP Value: {localPSARMatrix[1][3]}")

                    #AF Update START
                    if(localPSARMatrix[0][7] == localPSARMatrix[1][7]):
                        localPSARMatrix[1][5] = localPSARMatrix[0][5]
                        if(localPSARMatrix[1][7] == 1 and localPSARMatrix[1][3] > localPSARMatrix[0][3]):
                            if(localPSARMatrix[1][5] < stock.AF_limit):
                                localPSARMatrix[1][5] = localPSARMatrix[1][5] + stock.AF_increment
                        if(localPSARMatrix[1][7] == 0 and localPSARMatrix[1][3] < localPSARMatrix[0][3]):
                            if(localPSARMatrix[1][5] < stock.AF_limit):
                                localPSARMatrix[1][5] = localPSARMatrix[1][5] + stock.AF_increment
                    else:
                        localPSARMatrix[1][5] = stock.AF_increment
                    #AF Update END

                    # print(f"AF Value: {localPSARMatrix[1][5]}")

                    localPSARMatrix[1][4] = localPSARMatrix[1][3] - localPSARMatrix[1][2] #set EP - PSAR
                    localPSARMatrix[1][6] = localPSARMatrix[1][4] * localPSARMatrix[1][5] #set (EP - PSAR)*AF

                    # print(f"EP - PSAR Value: {localPSARMatrix[1][4]}")
                    # print(f"(EP - PSAR)*AF Value: {localPSARMatrix[1][6]}")

                    #Setup for next iteration
                    localPSARMatrix[0] = localPSARMatrix[1]
                    localPSARMatrix[1] = [0,0,0,0,0,0,0,0]
                
                if(localPSARMatrix[0][7] == 0):
                    
                    sell(stock)

                # plt.plot(stock.t[-5:], arr, 'kx', stock.t[26:], stock.histLongPSAR[26:], 'xc', stock.t[26:], stock.histShortPSAR[26:], 'xm')
                # plt.title("4 point PSAR Prediction")
                # plt.show()

                    stock.hard_sell = True
                else:
                    stock.hard_sell = False    

def calcSmmaUpLong(open,close,n,i,avgUt1):
    if (avgUt1==0):
        sumUpChanges = 0
        for j in range(n):
            # change = data.iloc[i-j]['Close'] - data.iloc[i-j]['Open']
            change = close[i-j] - open[i-j]

            if change < 0:
                sumUpChanges += change
        return sumUpChanges/n
    else:
        # change = data.iloc[i]['Close'] - data.iloc[i]['Open']
        change = close[i] - open[i]
        if change < 0:
            change = 0
        return ((avgUt1*(n-1))+change)/n

def calcSmmaDownLong(open,close,n,i,avgDt1):
    if avgDt1 == 0:
        sumDownChanges = 0

        for j in range(n):
            # change = data.iloc[i-j]['Close'] - data.iloc[i-j]['Open']
            change = close[i - j] - open[i - j]

            if change < 0:
                sumDownChanges -= change
        return sumDownChanges/n
    else:
        # change = data.iloc[i]['Close'] - data.iloc[i]['Open']
        change = close[i] - open[i]
        if change > 0:
            change = 0
        return ((avgDt1 * (n-1)) - change)/n

def calculateRSILong(stock, n, i):
    result = 0

    stock.ut1Long = calcSmmaUp(stock.open,stock.close,n,i,stock.ut1Long)
    stock.dt1Long = calcSmmaDown(stock.open,stock.close,n,i,stock.dt1Long)

    result = (100 - 100/(1+(stock.ut1Long/stock.dt1Long)))

    return result

def calcSmmaUp(open,close,n,i,avgUt1):
    if (avgUt1==0):
        sumUpChanges = 0
        for j in range(n):
            # change = data.iloc[i-j]['Close'] - data.iloc[i-j]['Open']
            change = close[i-j] - open[i-j]

            if change < 0:
                sumUpChanges += change
        return sumUpChanges/n
    else:
        # change = data.iloc[i]['Close'] - data.iloc[i]['Open']
        change = close[i] - open[i]
        if change < 0:
            change = 0
        return ((avgUt1*(n-1))+change)/n

def calcSmmaDown(open,close,n,i,avgDt1):
    if avgDt1 == 0:
        sumDownChanges = 0

        for j in range(n):
            # change = data.iloc[i-j]['Close'] - data.iloc[i-j]['Open']
            change = close[i - j] - open[i - j]

            if change < 0:
                sumDownChanges -= change
        return sumDownChanges/n
    else:
        # change = data.iloc[i]['Close'] - data.iloc[i]['Open']
        change = close[i] - open[i]
        if change > 0:
            change = 0
        return ((avgDt1 * (n-1)) - change)/n

def calculateRSI(stock, n, i):
    result = 0

    stock.ut1 = calcSmmaUp(stock.open,stock.close,n,i,stock.ut1)
    stock.dt1 = calcSmmaDown(stock.open,stock.close,n,i,stock.dt1)

    # print(f"stock.ut1 = {stock.ut1}\nstock.dt1 = {stock.dt1}")
    # print(f"result = {(100 - 100/(1+(stock.ut1/stock.dt1)))}")

    result = (100 - 100/(1+(stock.ut1/stock.dt1)))

    return result

def percent_change_update(stock, x, IL):
    # data = yfinance.download(tickers = stock.Ticker, period ='5m', interval = '5m')
    # print(data)
    global filelist
    global timestep
    global curr_time

    file = open(str(filelist[x]))
    # file = open('TestDataSet.csv')
    csv_reader = csv.reader(file)

    # csv_reader = reader(read_obj)

    i = 0
    close1 = 0
    close0 = 0

    # while():
    for row in csv_reader:
        if(i == stock.PSARcounter):
            stock.PSARMatrix[1][0] = float(row[1]) #set High
            stock.PSARMatrix[1][1] = float(row[2]) #set Low
            stock.PSARMatrixlong[1][0] = float(row[1]) #set High
            stock.PSARMatrixlong[1][1] = float(row[2]) #set Low
            stock.t.append(stock.PSARcounter) #Save times
            stock.close.append(float(row[3])) #Save close prices
            stock.open.append(float(row[0])) #Save open prices
            stock.high.append(float(row[1])) #Save high prices
            stock.low.append(float(row[2])) #Save low prices
            stock.buyindicator.append(None)
            stock.soldindicator.append(None)
            curr_time = str(row[6])

                    
        if(i == stock.setcounter): #Get current point's data
            close1 = float(row[3])
            # print(close1)
            break
        elif(i == stock.setcounter - 1): #Get previous point's data
            close0 = float(row[3])
            # print(close0)

        i += 1

    stock.PSARcounter += 1

    # stock.slopes.append((float(data.iloc[1]['Close'] - data.iloc[0]['Close'])/float(data.iloc[0]['Close'])) * 100)
    # if(stock.setcounter == 0):

    #Update Short Term and Long Term Momentum
    for i in range(1):
        if(len(stock.close) >= 9):
            stock.momentum.append(stock.close[-1] - stock.close[-9])
        else:
            stock.momentum.append(0)

        if(len(stock.close) >= 26):
            stock.momentumlong.append(stock.close[-1] - stock.close[-26])
        else:
            stock.momentum.append(0)

    #Update Short Term Momentum EMA (9 periods) and Long Term EMA (26 periods)
    if(len(stock.momentum) >= 1):
        stock.prev_momentum_EMA = stock.curr_momentum_EMA
        stock.curr_momentum_EMA = stock.momentum[-1]*(2/(stock.momentum_counter+1)) + stock.curr_momentum_EMA*(1 - (2/(stock.momentum_counter + 1)))
        stock.momentum_EMA_log.append(stock.curr_momentum_EMA)
        stock.momentum_counter += 1
    else:
        stock.momentum_EMA_log.append(0)
    
    if(len(stock.momentumlong) >= 1):
        stock.prev_momentum_EMAlong = stock.curr_momentum_EMAlong
        stock.curr_momentum_EMAlong = stock.momentumlong[-1]*(2/(stock.momentum_counterlong+1)) + stock.curr_momentum_EMAlong*(1 - (2/(stock.momentum_counterlong + 1)))
        stock.momentum_EMA_loglong.append(stock.curr_momentum_EMAlong)
        stock.momentum_counterlong += 1
    else:
        stock.momentum_EMA_loglong.append(0)

    #Change Between Consecutive Close Values
    if(len(stock.close) >= 3 and len(stock.close) % 3 == 0):
        stock.anchor15.append(stock.close[-1])

    if(len(stock.close) >= 6 and len(stock.close) % 6 == 0):
        stock.anchor30.append(stock.close[-1])
    
    stock.changes.append(((close1 - close0)/close0)*100)
    
    stock.limit = close1 * 1.00

    if(stock.bought == True and stock.sold == False):
        if(stock.close[-1] > stock.close[-2]):
            stock.stoplosslimit = stock.close[-1]
    
    #Update the EMA; EMA = Averge Price over some interval 't0 - tf'
    stock.prev_EMA = stock.curr_EMA
    stock.curr_EMA = close1*(2/(stock.counter+1)) + stock.curr_EMA*(1 - (2/(stock.counter + 1)))
    stock.EMA_Slope = (stock.curr_EMA - stock.prev_EMA)/(timestep/60)
    stock.EMA_log.append(stock.curr_EMA)


    if(len(stock.close) >= 0):
        # avg_close = 0
        # for i in range(12):
        #     avg_close += stock.close[-i - 1]
        # avg_close /= 12

        stock.curr_EMA12 = close1*(2/(12+1)) + stock.curr_EMA12*(1 - (2/(12 + 1)))
        stock.EMA_12_arr.append(stock.curr_EMA12)
    else:
        stock.EMA_12_arr.append(close1)
    
    if(len(stock.close) >= 0):
        # avg_close = 0
        # for i in range(26):
        #     avg_close += stock.close[-i - 1]
        # avg_close /= 26

        stock.curr_EMA26 = close1*(2/(26+1)) + stock.curr_EMA26*(1 - (2/(26+ 1)))
        stock.EMA_26_arr.append(stock.curr_EMA26)
    else:
        stock.EMA_26_arr.append(close1)

    if(len(stock.close) >= 26):
        stock.MACD_val.append(stock.curr_EMA12 - stock.curr_EMA26)
    else:
        stock.MACD_val.append(0)
    
    if(len(stock.MACD_val) >= 9):
        avg_MACD = 0
        for i in range(9):
            avg_MACD += stock.MACD_val[-i - 1]
        avg_MACD /= 9

        stock.MACD9_arr.append(avg_MACD)
    else:
        stock.MACD9_arr.append(0)
    
    #PSAR Implementation (Short Term)
    if(IL == 1):
        # print("Entered PSAR initialization\n")
        # print(f"High Value: {stock.PSARMatrix[1][0]}")
        # print(f"Low Value: {stock.PSARMatrix[1][1]}")
        stock.PSARMatrix[1][2] = stock.PSARMatrix[1][1] #set PSAR
        # print(f"PSAR Value: {stock.PSARMatrix[1][2]}")
        stock.PSARMatrix[1][3] = stock.PSARMatrix[1][0] #set EP
        # print(f"EP Value: {stock.PSARMatrix[1][3]}")
        stock.PSARMatrix[1][4] = stock.PSARMatrix[1][3] - stock.PSARMatrix[1][2] #set EP - PSAR
        # print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        stock.PSARMatrix[1][5] = stock.AF_increment #set AF
        # print(f"AF Value: {stock.PSARMatrix[1][5]}")
        stock.PSARMatrix[1][6] = stock.PSARMatrix[1][4] * stock.PSARMatrix[1][5] #set (EP - PSAR)*AF
        # print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")
        stock.PSARMatrix[1][7] = 1 #set BULLBEAR
        # print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")
    else:
    
        # print("Entered PSAR Solve")
        # print(f"High Value: {stock.PSARMatrix[1][0]}")
        # print(f"Low Value: {stock.PSARMatrix[1][1]}")

        #PSAR Update START
        if(stock.PSARMatrix[0][7] == 1 and stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6] > stock.PSARMatrix[1][1]):
            stock.PSARMatrix[1][2] = stock.PSARMatrix[0][3]
        else:
            if(stock.PSARMatrix[0][7] == 0 and stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6] < stock.PSARMatrix[1][0]):
                stock.PSARMatrix[1][2] = stock.PSARMatrix[0][3]
            else:
                stock.PSARMatrix[1][2] = stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6]
        #PSAR Update END

        # print(f"PSAR Value: {stock.PSARMatrix[1][2]}")

        #BULLBEAR Update START
        if(stock.PSARMatrix[1][2] < stock.PSARMatrix[1][0]):
            stock.PSARMatrix[1][7] = 1
        else:
            if(stock.PSARMatrix[1][2] > stock.PSARMatrix[1][1]):
                stock.PSARMatrix[1][7] = 0
        #BULLBEAR Update END

        # print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")

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

        # print(f"EP Value: {stock.PSARMatrix[1][3]}")

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

        # print(f"AF Value: {stock.PSARMatrix[1][5]}")

        stock.PSARMatrix[1][4] = stock.PSARMatrix[1][3] - stock.PSARMatrix[1][2] #set EP - PSAR
        stock.PSARMatrix[1][6] = stock.PSARMatrix[1][4] * stock.PSARMatrix[1][5] #set (EP - PSAR)*AF

        # print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        # print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")

    #Setup for next iteration
    stock.PSARMatrix[0] = stock.PSARMatrix[1]
    stock.PSARMatrix[1] = [0,0,0,0,0,0,0,0]

    stock.counter += 1

    #PSAR Implementation (Long Term)
    if(IL == 1):
        # print("Entered PSAR initialization\n")
        # print(f"High Value: {stock.PSARMatrix[1][0]}")
        # print(f"Low Value: {stock.PSARMatrix[1][1]}")
        stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[1][1] #set PSAR
        # print(f"PSAR Value: {stock.PSARMatrix[1][2]}")
        stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[1][0] #set EP
        # print(f"EP Value: {stock.PSARMatrix[1][3]}")
        stock.PSARMatrixlong[1][4] = stock.PSARMatrixlong[1][3] - stock.PSARMatrixlong[1][2] #set EP - PSAR
        # print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        stock.PSARMatrixlong[1][5] = stock.AF_incrementlong #set AF
        # print(f"AF Value: {stock.PSARMatrix[1][5]}")
        stock.PSARMatrixlong[1][6] = stock.PSARMatrixlong[1][4] * stock.PSARMatrixlong[1][5] #set (EP - PSAR)*AF
        # print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")
        stock.PSARMatrixlong[1][7] = 1 #set BULLBEAR
        # print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")

    if(IL != 1 and stock.counter % 2 == 0):
        # print("Entered PSAR Solve")
        # print(f"High Value: {stock.PSARMatrix[1][0]}")
        # print(f"Low Value: {stock.PSARMatrix[1][1]}")

        #PSAR Update START
        if(stock.PSARMatrixlong[0][7] == 1 and stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6] > stock.PSARMatrixlong[1][1]):
            stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][3]
        else:
            if(stock.PSARMatrixlong[0][7] == 0 and stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6] < stock.PSARMatrixlong[1][0]):
                stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][3]
            else:
                stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6]
        #PSAR Update END

        # print(f"PSAR Value: {stock.PSARMatrix[1][2]}")

        #BULLBEAR Update START
        if(stock.PSARMatrixlong[1][2] < stock.PSARMatrixlong[1][0]):
            stock.PSARMatrixlong[1][7] = 1
        else:
            if(stock.PSARMatrixlong[1][2] > stock.PSARMatrixlong[1][1]):
                stock.PSARMatrixlong[1][7] = 0
        #BULLBEAR Update END

        # print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")

        #EP Update START
        if(stock.PSARMatrixlong[1][7] == 1 and stock.PSARMatrixlong[1][0] > stock.PSARMatrixlong[0][3]):
            stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[1][0]
        else:
            if(stock.PSARMatrixlong[1][7] == 1 and stock.PSARMatrixlong[1][0] <= stock.PSARMatrixlong[0][3]):
                stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[0][3]
            else:
                if(stock.PSARMatrixlong[1][7] == 0 and stock.PSARMatrixlong[1][1] < stock.PSARMatrixlong[0][3]):
                    stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[1][1]
                else:
                    if(stock.PSARMatrixlong[1][7] == 0 and stock.PSARMatrixlong[1][1] >= stock.PSARMatrixlong[0][3]):
                        stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[0][3]

        #EP Update END

        # print(f"EP Value: {stock.PSARMatrix[1][3]}")

        #AF Update START
        if(stock.PSARMatrixlong[0][7] == stock.PSARMatrixlong[1][7]):
            stock.PSARMatrixlong[1][5] = stock.PSARMatrixlong[0][5]
            if(stock.PSARMatrixlong[1][7] == 1 and stock.PSARMatrixlong[1][3] > stock.PSARMatrixlong[0][3]):
                if(stock.PSARMatrixlong[1][5] < stock.AF_limitlong):
                    stock.PSARMatrixlong[1][5] = stock.PSARMatrixlong[1][5] + stock.AF_incrementlong
            if(stock.PSARMatrixlong[1][7] == 0 and stock.PSARMatrixlong[1][3] < stock.PSARMatrixlong[0][3]):
                if(stock.PSARMatrixlong[1][5] < stock.AF_limitlong):
                    stock.PSARMatrixlong[1][5] = stock.PSARMatrixlong[1][5] + stock.AF_incrementlong
        else:
            stock.PSARMatrixlong[1][5] = stock.AF_incrementlong
        #AF Update END

        # print(f"AF Value: {stock.PSARMatrix[1][5]}")

        stock.PSARMatrixlong[1][4] = stock.PSARMatrixlong[1][3] - stock.PSARMatrixlong[1][2] #set EP - PSAR
        stock.PSARMatrixlong[1][6] = stock.PSARMatrixlong[1][4] * stock.PSARMatrixlong[1][5] #set (EP - PSAR)*AF

        # print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        # print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")

    if(IL == 1 or stock.counter % 2 == 0):
        #Setup for next iteration
        stock.PSARMatrixlong[0] = stock.PSARMatrixlong[1]
        stock.PSARMatrixlong[1] = [0,0,0,0,0,0,0,0]

    #Update Historical PSAR Arrays
    stock.histShortPSAR.append(stock.PSARMatrix[0][2])
    stock.histLongPSAR.append(stock.PSARMatrixlong[0][2])

    stock.slopecounter += 1

    #Update RSI Array
    if(len(stock.close) >= 14):
        stock.RSI.append(calculateRSI(stock, 14, len(stock.close) - 1))
    else:
        stock.RSI.append(0)

    if(len(stock.close) >= 250):
        stock.RSILong.append(calculateRSILong(stock, 250, len(stock.close) - 1))
    else:
        stock.RSILong.append(0)

    # print(f"Slope for {stock.Ticker} was {stock.changes[-1]}")
    # print(f"EMA_Slope for {stock.Ticker} was {stock.EMA_Slope}")
    # print(f"Length of slopes: {len(stock.changes)}\n\n")

def buy(stock):
    global curr_time
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
    stock.stoplosslimit = stock.close[-2]
    stock.profit_per_trade = stock.bought_price

    stock.bought = True
    stock.sold = False

    stock.buy_log.append([stock.limit, curr_time])

    stock.buyindicator[-1] = stock.close[-1]

    # x = input("Paused Code")

def sell(stock):
    print("Triggered Sell Command\n")
    # order = api.submit_order(symbol=stock.Ticker,
    #                         qty = str(stock.quantity),
    #                         side ="sell",
    #                         type = "market",
    #                         time_in_force ='day')
    
    stock.capital = stock.capital + (stock.limit * stock.quantity)

    if(stock.stoplosslimit != 0):
        stock.profit_per_trade = stock.stoplosslimit - stock.profit_per_trade
    else:
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
    stock.stoplosslimit = 0

    stock.bought = False
    stock.sold = True

    stock.soldindicator[-1] = stock.close[-1]

    stock.sell_log.append([stock.limit, curr_time])

def mainloop(stocks, stocks_list, i, counter, iterations, timeframe, increment, EP):
    
    while(True):

        while(counter < iterations): 
                
            for i in range(stocks):
                percent_change_update(stocks_list[i], i, 0)
                stocks_list[i].setcounter += 1

            if(EP > 0):
                EP -= 1
            elif(EP == 0):
                break           
                        
            # if(IP > 0):
            #     IP -= 1
            counter += 1
            # print(f"--------------- Finished Iteration {counter} ---------------\n")

        break

    return stocks_list[0]
#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------
arr = int([0,0,0,0,0,0])

stockv1 = makestock(arr)
stockv2 = makestock(arr)

for timeframe in timeframes:

    for increment in increments:

        if(timeframe == '52w' and increment == '1w'):

            iterations = 0
            for i in range(len(symbol)):
                try:
                    data = yfinance.download(tickers = symbol[i], thread = False, period = timeframe, interval = increment)
                    data = data.dropna()
                except Exception as ex:
                    jsonerr += 1
                    error = 1/0
                    

                # print(data.Close)
                # x = input()
                # if(len(data.close) == 0):
                #     return (1/0) #Instigate error

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
                        stocks_list.append(makestock(row))
                        stocks_list[i].print()
                        i += 1

            stocks = len(stocks_list)

            for i in range(stocks):
                netcapital += stocks_list[i].capital
                percent_change_update(stocks_list[i], i, 1)

            stockv1 = mainloop(stocks, stocks_list, i, counter, iterations, timeframe, increment, EP[0])
            

        elif(timeframe == '260d' and increment == '3d'):

            iterations = 0
            for i in range(len(symbol)):
                try:
                    data = yfinance.download(tickers = symbol[i], thread = False, period = timeframe, interval = increment)
                    data = data.dropna()
                except Exception as ex:
                    jsonerr += 1
                    error = 1/0
                    

                # print(data.Close)
                # x = input()
                # if(len(data.close) == 0):
                #     return (1/0) #Instigate error

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
                        stocks_list.append(makestock(row))
                        stocks_list[i].print()
                        i += 1

            stocks = len(stocks_list)

            for i in range(stocks):
                netcapital += stocks_list[i].capital
                percent_change_update(stocks_list[i], i, 1)
            
            mainloop(stocks, stocks_list, i, counter, iterations, timeframe, increment, EP[1])

#Graph the stock versions

y = input("Enter 'y' for graphs: ")
if(y == 'y' or y == 'Y'):
    y = input()
    if(y != ''):
        figure, axis = plt.subplots(2, 4)
        figure.set_figwidth(17)

        axis[0][0].plot(stockv1.t, stockv1.close, 'k', stockv1.t,stockv1.EMA_12_arr, 'r', stockv1.t, stockv1.EMA_26_arr, 'b', stockv1.t, stockv1.histLongPSAR, 'xc', stockv1.t, stockv1.histShortPSAR, 'xm')
        axis[0][0].set_title(stockv1.Ticker + ' EMA_12 and EMA_26')

        axis[0][1].plot(stockv1.t, stockv1.MACD_val, 'm',stockv1.t, stockv1.MACD9_arr, 'g')
        axis[0][1].set_title(stockv1.Ticker + ' MACD and Signal')

        axis[0][2].plot(stockv1.t, stockv1.RSI, 'm', stockv1.t, [70]*len(stockv1.t), 'b', stockv1.t, [30]*len(stockv1.t), 'b')
        axis[0][2].set_title(stockv1.Ticker + ' RSI')

        axis[0][3].plot(stockv1.t, stockv1.momentum_EMA_log, 'g', stockv1.t, stockv1.momentum_EMA_loglong, 'r')
        axis[0][3].set_title(stockv1.Ticker + ' Short and Long Momentum + Momentum EMA')

        axis[1][0].plot(stockv2.t, stockv2.close, 'k', stockv2.t,stockv2.EMA_12_arr, 'r', stockv2.t, stockv2.EMA_26_arr, 'b', stockv2.t, stockv2.histLongPSAR, 'xc', stockv2.t, stockv2.histShortPSAR, 'xm')
        axis[1][0].set_title(stockv2.Ticker + ' EMA_12 and EMA_26')

        axis[1][1].plot(stockv2.t, stockv2.MACD_val, 'm',stockv2.t, stockv2.MACD9_arr, 'g')
        axis[1][1].set_title(stockv2.Ticker + ' MACD and Signal')

        axis[1][2].plot(stockv2.t, stockv2.RSI, 'm', stockv2.t, [70]*len(stockv2.t), 'b', stockv2.t, [30]*len(stockv2.t), 'b')
        axis[1][2].set_title(stockv2.Ticker + ' RSI')

        axis[1][3].plot(stockv2.t, stockv2.momentum_EMA_log, 'g', stockv2.t, stockv2.momentum_EMA_loglong, 'r')
        axis[1][3].set_title(stockv2.Ticker + ' Short and Long Momentum + Momentum EMA')
        plt.show()    
