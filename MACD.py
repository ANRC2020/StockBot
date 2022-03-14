import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import PortfolioHistory
from numpy import diff
from numpy.lib.function_base import average
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
# import ResearchTeam

global timestep
timestep = 300

global symbol
# symbol = ['GOED', 'ZIVO', 'TYHT', 'PRVB', 'IMVT', 'TIRX', 'ETON', 'DAWN']
# symbol = ['WPG', 'VTNR', 'LEDS', 'GTT', 'MOSY', 'AMC', 'CNST', 'UONE']
# symbol = ['TGT', 'LOW', 'HD', 'NKE', 'TSLA', 'AAPL','NIO', 'Z', 'MSFT', 'WPG', 'VTNR', 'LEDS', 'GTT', 'MOSY', 'AMC', 'CNST', 'UONE']
# symbol = ['EXFO', 'KBSF', 'LEDS', 'NEXT', 'LMNL']
# symbol = ['AAPL','AMC','XP']
# symbol = ['PFMT','LODE','CPSH','SCKT','PRT','CTHR','EMKR','CHCI','EGY','BW',
#           'EXK','USDP','HBIO','III','PMBC','MHLD','OVID','AETUF','HL','KDOZF','CLNY',
#           'ICL','SOL','WIT','EVC','SCGLY','PNNT','NL','ASX','WRTBY','BGCP','OXBR','MMMB']
# symbol = ['PFMT','LODE','CPSH','SCKT','PRT']
# symbol = ['CLOV','IHT','NEXT','AEHL']
# symbol = ['ATOS','MCF','RMED','HOOK','ACRS']
# symbol = ['LOTZ','EVK','ASTS']
# symbol = ['F','TGT','AAPL','T','MSFT','IBM','IRM','AMC']
# symbol = ['JZXN','AAPL','RIDE']
# symbol = ['AMC']
# symbol = ['AAPL','TGT','CLOV','TSLA','MSFT','WPG']
# symbol = ['EURUSD=X']
# symbol = ['TSLA','FCX','NUE','EXPD','AMAT']
# symbol = ['AMC','CLOV','ALF','CLSD','TRCH','OBLN','CLSD']
symbol = ['AMC']
# symbol = ['STEM']
# symbol = ResearchTeam.run()
# print(symbol)
# x = input("Paused")

global timeframe
timeframe = '20d'

global increment
increment = '5m'

global IP #Initilization Period = number of points over which the code remains dormant prior to trading 
IP = 78

global IPstr
IPstr = '1d'

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

global curr_time
curr_time = ""

with open('Saved_Info_Initial.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    header = ['symbol','quantity','capital','sold','bought','bought_price']
    writer.writerow(header)
    for stock in symbol:
        row = [stock,'0','10000','1','0','0']
        writer.writerow(row)
    file.close()

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


    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")  


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

    for row in csv_reader:
        if(i == stock.PSARcounter):
            stock.PSARMatrix[1][0] = float(row[1]) #set High
            stock.PSARMatrix[1][1] = float(row[2]) #set Low
            stock.PSARMatrixlong[1][0] = float(row[1]) #set High
            stock.PSARMatrixlong[1][1] = float(row[2]) #set Low
            stock.t.append(stock.PSARcounter) #Save times
            stock.close.append(float(row[3])) #Save close prices
            stock.open.append(float(row[0])) #Save open prices
            stock.buyindicator.append(None)
            stock.soldindicator.append(None)
            curr_time = str(row[6])

                    
        if(i == stock.setcounter): #Get current point's data
            close1 = float(row[3])
            print(close1)
            break
        elif(i == stock.setcounter - 1): #Get previous point's data
            close0 = float(row[3])
            print(close0)

        i += 1

    stock.PSARcounter += 1

    # stock.slopes.append((float(data.iloc[1]['Close'] - data.iloc[0]['Close'])/float(data.iloc[0]['Close'])) * 100)
    # if(stock.setcounter == 0):

    #Change Between Consecutive Close Values
    
    stock.changes.append(((close1 - close0)/close0)*100)
    
    stock.limit = close1 * 1.00
    
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

        stock.curr_EMA12 = close1*(2/(10+1)) + stock.curr_EMA12*(1 - (2/(10 + 1)))
        stock.EMA_12_arr.append(stock.curr_EMA12)
    else:
        stock.EMA_12_arr.append(close1)
    
    if(len(stock.close) >= 0):
        # avg_close = 0
        # for i in range(26):
        #     avg_close += stock.close[-i - 1]
        # avg_close /= 26

        stock.curr_EMA26 = close1*(2/(20+1)) + stock.curr_EMA26*(1 - (2/(20+ 1)))
        stock.EMA_26_arr.append(stock.curr_EMA26)
    else:
        stock.EMA_26_arr.append(close1)

    if(len(stock.close) >= 20):
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

#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

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
                percent_change_update(stocks_list[i], i, 0)
                stocks_list[i].setcounter += 1

            counter += 1

        break

for stock in stocks_list:
    if(x != ''):
        figure, axis = plt.subplots(1, 2)
        figure.set_figwidth(17)

        axis[0].plot(stock.t[20:], stock.close[20:], 'k', stock.t[20:],stock.EMA_12_arr[20:], 'r', stock.t[20:], stock.EMA_26_arr[20:], 'b')
        axis[0].set_title(stock.Ticker + ' EMA_12 and EMA_26')

        axis[1].plot(stock.t[20:], stock.MACD_val[20:], 'm',stock.t[20:], stock.MACD9_arr[20:], 'g')
        axis[1].set_title(stock.Ticker + ' MACD and Signal')
        plt.show()