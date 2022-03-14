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
symbol = []
# symbol = ResearchTeam.run()
# print(symbol)
# x = input("Paused")

global timeframe
timeframe = '6d' # (1 + 5) + 5 + 5 -> 3 weeks ago

global increment
increment = '5m'

global IP #Initilization Period = number of points over which the code remains dormant prior to trading 
IP = 0

global EP
# EP = 52
EP = -1

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
    momentumlong = []
    momentum_EMA_log = []
    curr_momentum_EMA = 0
    prev_momentum_EMA = 0
    momentum_counter = 2

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

def setstocks(arr):
    global symbol

    global IP
    IP = 0

    global EP
    EP = -1
    # EP = -1

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

    symbol = []
    symbol.append(arr)

    with open('Saved_Info_Initial.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['symbol','quantity','capital','sold','bought','bought_price']
        writer.writerow(header)
        for stock in symbol:
            row = [stock,'0','10000','1','0','0']
            writer.writerow(row)
        file.close()
    
    try:
        stock = main()
    except Exception as ex:
        print(f"Ran into {ex} on {symbol[-1]}")
        # input()
        return []

    # y = input("Enter 'y' for graphs: ")
    # if(y == 'y' or y == 'Y'):
    #     y = input()
    #     if(y != ''):
    #         figure, axis = plt.subplots(1, 4)
    #         figure.set_figwidth(17)

    #         axis[0].plot(stock.t, stock.close, 'k', stock.t,stock.EMA_12_arr, 'r', stock.t, stock.EMA_26_arr, 'b', stock.t, stock.histLongPSAR, 'xc', stock.t, stock.histShortPSAR, 'xm')
    #         axis[0].set_title(stock.Ticker + ' EMA_12 and EMA_26')

    #         axis[1].plot(stock.t, stock.MACD_val, 'm',stock.t, stock.MACD9_arr, 'g')
    #         axis[1].set_title(stock.Ticker + ' MACD and Signal')

    #         axis[2].plot(stock.t, stock.RSI, 'm', stock.t, [70]*len(stock.t), 'b', stock.t, [30]*len(stock.t), 'b')
    #         axis[2].set_title(stock.Ticker + ' RSI')

    #         # axis[3].plot(stock.t, stock.momentum[25:], 'r')
    #         axis[3].plot(stock.t, stock.momentum_EMA_log, 'g')
    #         axis[3].set_title(stock.Ticker + ' Short and Long Momentum + Momentum EMA')
    #         plt.show()
    
    return ((stock.EMA_log[-2] - stock.EMA_log[-1])/2) 

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

def save_info(stocks_list, netcapital, netsectionval, bestsectionval):

    global timeframe
    global increment
    global IPstr

    with open('ActivityLog.txt', 'w', newline='') as file:
        # writer = csv.writer(file)

        dash = '----------------------------------------' # 40 dashes

        file.write(dash + "Section Stats" + dash[0:- len('Section Stats')] + dash[0:12] +"\n")
        file.write('Period: ' + timeframe + '                             Interval: ' + increment + '                        Delay Period: ' + IPstr + '\n')
        file.write("Net Capital: " + str(netcapital) + '\n')
        file.write("Net Section Value: " + str(netsectionval) + '\n')
        file.write("Net Percent Change: " + str(((netsectionval - netcapital)/netcapital)*100) + '\n')
        file.write("Best Section Value: " + str(bestsectionval) + '\n')
        file.write("Best Percent Value: " + str(((bestsectionval - netcapital)/netcapital)*100) + '\n')

        for stock in stocks_list:
            file.write(dash + stock.Ticker + dash[0:- len(stock.Ticker)] + dash[0:12] + "\n")
            file.write('Ticker: ' + stock.Ticker + '              Period: ' + timeframe + '              Interval: ' + increment + '              Delay Period: ' + IPstr + '\n')
            file.write('Principle: ' + str(stock.principle) + '                                Ending Capital: ' + str(stock.capital) + '\n')
            if(stock.section_val >= stock.principle):
                file.write('Final Percent Profit: ' + str( ((stock.section_val - stock.principle)/(stock.principle)) * 100  ) + '\n')
            else:
                file.write('Final Percent Loss: ' + str( ((stock.section_val - stock.principle)/(stock.principle)) * 100  ) + '\n')


            file.write('Profit Log: ' + str(stock.profitlog) + '\n')

            file.write('Best Percent Profit: ' + str(((stock.bestprofit - stock.principle)/stock.principle) * 100) + '\n')    
            
            if(len(stock.sell_log) > 0):
                file.write('Number of Trades Closed: ' + str(len(stock.sell_log)) + '  Average Profit Per Trade: ' + str((stock.section_val - stock.principle)/len(stock.sell_log)) + '\n')        
            else:
                file.write('Number of Trades Closed: ' + str(len(stock.sell_log)) + '  Average Profit Per Trade: ' + 'N/A\n') 

            num_win = 0
            amount_won = 0
            num_loss = 0
            amount_lost = 0
            avg_win = 0
            avg_loss = 0

            for i in range(len(stock.sell_log)):
                if(stock.buy_log[i][0] <= stock.sell_log[i][0]):
                    num_win += 1
                    amount_won += (stock.sell_log[i][0] - stock.buy_log[i][0])
                else:
                    num_loss += 1 
                    amount_lost += (stock.buy_log[i][0] - stock.sell_log[i][0])

            if(num_win > 0):
                avg_win = amount_won/num_win
                file.write('# of Winning Trades: ' + str(num_win) + '      Average Profit Per Winning Trade Per Stock: ' + str(avg_win) + '\n')
            else:
                file.write('# of Winning Trades: ' + str(num_win) + '      Average Profit Per Winning Trade Per Stock: ' + 'N/A\n')

            if(num_loss > 0):
                avg_loss = amount_lost/num_loss
                file.write('# of Losing Trades: ' + str(num_loss) + '       Average Profit Per Losing Trade Per Stock: ' + str(avg_loss) + '\n')
            else:
                file.write('# of Losing Trades: ' + str(num_loss) + '       Average Profit Per Losing Trade Per Stock: ' + 'N/A\n')

            if(avg_win > 0 and avg_loss > 0):
                file.write('Profit-Loss Trade Ratio: ' + str(avg_win/avg_loss) + '\n')
            else:
                file.write('Profit-Loss Trade Ratio: ' + 'N/A\n')
            
            # if(stock.hard_sell == True):
            #     file.write("Hard-Sell Limit: " +  str(stock.hard_sell_limit) + "     " + "Hard-Sell Triggered: " + str(stock.hard_sell) + "       " + "Hard-Sell Time: " + str(stock.hard_sell_time) + '\n')
            # else:
            #     file.write("Hard-Sell Limit: " +  str(stock.hard_sell_limit) + "     " + "Hard-Sell Triggered: " + str(stock.hard_sell) + '\n')

            file.write("Buys:" + "                      Prices:" + "             Sells:" + "                     Prices:\n")

            for i in range(len(stock.buy_log)):
                file.write(str(stock.buy_log[i][1]) + "  " + str(stock.buy_log[i][0]) + "  " + str(stock.sell_log[i][1]) + "  " + str(stock.sell_log[i][0]) + '\n')

        file.write(dash + 'End of File' +  dash[0: - len('End of File')] + dash[0:12]+ "\n")
        file.close()

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

    #Update Short Term Momentum EMA (9 periods)
    if(len(stock.momentum) >= 1):
        stock.prev_momentum_EMA = stock.curr_momentum_EMA
        stock.curr_momentum_EMA = stock.momentum[-1]*(2/(stock.momentum_counter+1)) + stock.curr_momentum_EMA*(1 - (2/(stock.momentum_counter + 1)))
        stock.momentum_EMA_log.append(stock.curr_momentum_EMA)
        stock.momentum_counter += 1
    else:
        stock.momentum_EMA_log.append(0)

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

#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

def main():
    
    global IP
    global EP
    global netcapital
    global netsectionval
    global bestsectionval
    global jsonerr
    
    iterations = 0
    for i in range(len(symbol)):
        try:
            data = yfinance.download(tickers = symbol[i], period = timeframe, interval = increment)
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

    key = 'PKRXHTL201XCUN550DCP'
    sec = 'kVgrGMxDO08kEvVkacPgRX2DBDq5YJW97EUFn4lf'
    url = 'https://paper-api.alpaca.markets'
    api = tradeapi.REST(key, sec, url, api_version='v2')
    #Init our account var
    account = api.get_account()
    #Should print 'ACTIVE'
    # print(account.status)

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

    while(True):
        check_time = datetime.today() #Gets current time
        if(x < 10):
            # print(f"Current Time: {check_time}\n")
            x += 1
        if check_time.hour >= 0  and check_time.hour >= 0:
            # start_time = time.time()

            # print("Beginning Trades!\n")

            while(counter < iterations): # set to # of data entires - 2
                # end_time = time.time()
                
                # if check_time.hour > 13:
                #     break

                # if start_time + timestep <= end_time:
                #     start_time = time.time()
                    
                for i in range(stocks):
                    # print(f"---------------{stocks_list[i].Ticker} Stock Start ---------------")
                    # Update Slopes; 
                    percent_change_update(stocks_list[i], i, 0)
                    # hard_sell(stocks_list[i])
                    stocks_list[i].setcounter += 1

                
                #     if(IP == 0):

                #         if(stocks_list[i].hard_sell == False):

                #             if(stocks_list[i].changes[-1] < 0):

                #                 # if(stocks_list[i].RSI[-1] > 30):
                #                 if((stocks_list[i].PSARMatrix[0][7] == 0 and stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1]) or (stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1] and stocks_list[i].EMA_Slope < 0) or (stocks_list[i].close[-1] < stocks_list[i].stoplosslimit)):
                #                     print("Entered Sell Check")
                #                     if(stocks_list[i].bought == True and stocks_list[i].sold == False):

                #                         # if(stocks_list[i].bought_price <= stocks_list[i].limit):

                #                             sell(stocks_list[i])

                #                             print(f"Made a profit of: {stocks_list[i].profit[-1]}")

                #                             continue

                #             elif(stocks_list[i].changes[-1] > 0):
                #                 if((stocks_list[i].MACD_val[-1] > stocks_list[i].MACD9_arr[-1] and stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1)  or (stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1) or (stocks_list[i].RSI[-2] < 30 and stocks_list[i].RSI[-2] < stocks_list[i].RSI[-1])):#or stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1
                #                     # if(stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1):
                #                         if(stocks_list[i].bought == False and stocks_list[i].sold == True):
                #                             if(stocks_list[i].EMA_Slope > 0):
                #                                 # if(stocks_list[i].anchor15[-1] > stocks_list[i].anchor15[-2] and stocks_list[i].anchor30[-1] > stocks_list[i].anchor30[-2]):
                #                                 # if(stocks_list[i].high[-1] > stocks_list[i].high[-2] and stocks_list[i].low[-1] > stocks_list[i].low[-2]):
                #                                 #     if(stocks_list[i].high[-1] > stocks_list[i].high[-3]):
                #                                         buy(stocks_list[i])
                                                        
                #                         else:
                #                             print("Entered buying check but did not meet requirements")
                                        
                                    
                #             print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
                        
                #         else:
                #             if(stocks_list[i].MACD_val[-2] > stocks_list[i].MACD9_arr[-2] and stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1]):
                #                 stocks_list[i].hard_sell = False
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