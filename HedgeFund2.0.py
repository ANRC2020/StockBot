import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import PortfolioHistory
from numpy import diff
from pandas._libs.tslibs import Timestamp
import yfinance
import time
from time import sleep
import pandas as pd
import csv
from csv import DictWriter, writer, reader
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import mimetypes
from datetime import datetime
from pytz import timezone, utc
# import ResearchTeam

global timestep
timestep = 300

# global full_list
# full_list = ResearchTeam.run()

global symbol
# symbol = full_list[:5]
symbol = ['AMC','MSFT','AAPL','COST','DIS']

global timeframe
timeframe = '2d'

global increment
increment = '5m'

global IP #Initilization Period = number of points over which the code remains dormant prior to trading 
IP = 78

global IPstr
IPstr = '1d'

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

    high = []
    low = []

    MACD_check = False

    stoplosslimit = 0
    target = 0

    num_wins = 0
    num_losses = 0

    buy_counter = 0
    buy_order_time = ''
    buyorderid = ''

    stoploss_counter = 0
    stoploss_order_time = ''
    stoplossid = ''

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
        self.buy_log = []
        self.sell_log = []
        self.hard_sell_limit = -2
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

        self.num_wins = 0
        self.num_losses = 0

        self.buy_counter = 0
        self.buy_order_time = ''
        self.fbuyorderid = str(self.buy_counter) + self.buy_order_time

        self.stoploss_counter = 0
        self.stoploss_order_time = ''
        self.stoplossid = str(self.stoploss_counter) + self.stoploss_order_time

    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")

def get_pst_time():
    date_format='%m_%d_%Y_%H_%M_%S_%Z'
    date = datetime.now(tz=utc)
    date = date.astimezone(timezone('US/Pacific'))
    pstDateTime=date.strftime(date_format)
    return pstDateTime

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
        # if(stock.PSARMatrix[0][7] == 1 and stock.PSARMatrixlong[0][7] == 1):
            curr_section_val = stock.capital + (stock.quantity * stock.close[-1])
            percent_change = 0
            if(len(stock.profitlog) == 0):
                percent_change = ((curr_section_val - stock.principle)/stock.principle) * 100
            else:
                percent_change = ((curr_section_val - stock.profitlog[-1])/stock.profitlog[-1]) * 100
            # print(f"curr_section_val: {curr_section_val}")
            # print(f"percent_change: {percent_change}")
            # x = input()

            if(percent_change < stock.hard_sell_limit):
                sell(stock)
                stock.soldindicator[-1] = stock.close[-1]
                stock.hard_sell_time = curr_time
                stock.hard_sell = True
                print(f"Made a profit of: {stocks_list[i].profit[-1]}")

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
            
            if(stock.hard_sell == True):
                file.write("Hard-Sell Limit: " +  str(stock.hard_sell_limit) + "     " + "Hard-Sell Triggered: " + str(stock.hard_sell) + "       " + "Hard-Sell Time: " + str(stock.hard_sell_time) + '\n')
            else:
                file.write("Hard-Sell Limit: " +  str(stock.hard_sell_limit) + "     " + "Hard-Sell Triggered: " + str(stock.hard_sell) + '\n')

            file.write("Buys:" + "                      Prices:" + "             Sells:" + "                     Prices:\n")

            for i in range(len(stock.buy_log)):
                file.write(str(stock.buy_log[i][1]) + "  " + str(stock.buy_log[i][0]) + "  " + str(stock.sell_log[i][1]) + "  " + str(stock.sell_log[i][0]) + '\n')

        file.write(dash + 'End of File' +  dash[0: - len('End of File')] + dash[0:12]+ "\n")
        file.close()

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

def update(stocks_list,i):    
    global api

    data = yfinance.download(tickers = stocks_list[i].Ticker, period ='5m', interval = '5m')
    IL = 0

    stock = stocks_list[i]

    global timestep
    global curr_time

    close1 = 0
    close0 = 0

    stock.PSARMatrix[1][0] = float(data.iloc[0][1]) #set High
    stock.PSARMatrix[1][1] = float(data.iloc[0][2]) #set Low
    stock.PSARMatrixlong[1][0] = float(data.iloc[0][1]) #set High
    stock.PSARMatrixlong[1][1] = float(data.iloc[0][2]) #set Low
    stock.t.append(stock.PSARcounter) #Save times
    stock.close.append(float(data.iloc[0][3])) #Save close prices
    stock.open.append(float(data.iloc[0][0])) #Save open prices
    stock.high.append(float(data.iloc[0][1])) #Save high prices
    stock.low.append(float(data.iloc[0][2])) #Save low prices
    stock.buyindicator.append(None)
    stock.soldindicator.append(None)
    
    out = str(data.iloc[:,0:0].iloc[0])
    curr_time = out[17:42] 
                    
    close1 = stock.close[-1]
    close0 = stock.close[-2]
    
    stock.PSARcounter += 1

    #Change Between Consecutive Close Values
    
    stock.changes.append(((close1 - close0)/close0)*100)
    
    stock.limit = close1 * 1.00
    
    #Check if Stop-Loss was tiggered in past interval

    if(stock.low[-1] < stock.stoplosslimit):
        stoplosssell(stock)

    #Update Stop-Loss Limit if holding stocks

    if(stock.bought == True and stock.sold == False):
        if(stock.close[-1] > stock.close[-2]):
            stock.stoplosslimit = stock.close[-1]
            open_orders = api.list_orders(status = "open")

            for order in open_orders:
                if(order.client_order_id == stock.stoplossid):
                    #cancel old order
                    api.cancel_order(order.client_order_id)

                    time.sleep(10)

                    stock.stoploss_counter -= 1
                    stock.stoploss_order_time = get_pst_time()
                    stock.stoplossid = str(stock.stoploss_counter) + ' ' + stock.stoploss_order_time
                    #create a new order
                    api.submit_order(symbol=stock.Ticker, qty = str(stock.quantity), side = "sell", type = "stop", stop_price = str(stock.close[-2]), time_in_force = 'day', client_order_id = str(stock.stoplossid))
                    break

    
    #Update the EMA; EMA = Averge Price over some interval 't0 - tf'
    stock.prev_EMA = stock.curr_EMA
    stock.curr_EMA = close1*(2/(stock.counter+1)) + stock.curr_EMA*(1 - (2/(stock.counter + 1)))
    stock.EMA_Slope = (stock.curr_EMA - stock.prev_EMA)/(timestep/60)
    stock.EMA_log.append(stock.curr_EMA)

    #MACD Implementation
    for j in range(1):
        if(len(stock.close) >= 0):
            stock.curr_EMA12 = close1*(2/(12+1)) + stock.curr_EMA12*(1 - (2/(12 + 1)))
            stock.EMA_12_arr.append(stock.curr_EMA12)

        else:
            stock.EMA_12_arr.append(close1)
        
        if(len(stock.close) >= 0):
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

def data_primer(stock, j, row):

    global timestep

    stock.PSARMatrix[1][0] = float(row[1]) #set High
    stock.PSARMatrix[1][1] = float(row[2]) #set Low
    stock.PSARMatrixlong[1][0] = float(row[1]) #set High
    stock.PSARMatrixlong[1][1] = float(row[2]) #set Low
    stock.t.append(stock.PSARcounter) #Save times
    stock.close.append(float(row[3])) #Save close prices
    stock.open.append(float(row[0])) #Save open prices
    stock.buyindicator.append(None)
    stock.soldindicator.append(None)
                    
    stock.PSARcounter += 1
    
    close1 = stock.close[-1]

    if(len(stock.close) > 1):
        close0 = stock.close[-2]

    if(len(stock.close) >= 0):
        stock.curr_EMA12 = close1*(2/(12+1)) + stock.curr_EMA12*(1 - (2/(12 + 1)))
        stock.EMA_12_arr.append(stock.curr_EMA12)

    else:
        stock.EMA_12_arr.append(close1)
    
    if(len(stock.close) >= 0):
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

    if(len(stock.close) > 1):
        close0 = stock.close[-2]
        stock.changes.append(((close1 - close0)/close0)*100)
    
    stock.limit = close1 * 1.00
    
    #Update the EMA; EMA = Averge Price over some interval 't0 - tf'
    stock.prev_EMA = stock.curr_EMA
    stock.curr_EMA = close1*(2/(stock.counter+1)) + stock.curr_EMA*(1 - (2/(stock.counter + 1)))
    stock.EMA_Slope = (stock.curr_EMA - stock.prev_EMA)/(timestep/60)
    stock.EMA_log.append(stock.curr_EMA)
    
    #PSAR Implementation (Short Term)
    if(j == 0):
        stock.PSARMatrix[1][2] = stock.PSARMatrix[1][1] #set PSAR
        stock.PSARMatrix[1][3] = stock.PSARMatrix[1][0] #set EP
        stock.PSARMatrix[1][4] = stock.PSARMatrix[1][3] - stock.PSARMatrix[1][2] #set EP - PSAR
        stock.PSARMatrix[1][5] = stock.AF_increment #set AF
        stock.PSARMatrix[1][6] = stock.PSARMatrix[1][4] * stock.PSARMatrix[1][5] #set (EP - PSAR)*AF
        stock.PSARMatrix[1][7] = 1 #set BULLBEAR
    else:
        if(stock.PSARMatrix[0][7] == 1 and stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6] > stock.PSARMatrix[1][1]):
            stock.PSARMatrix[1][2] = stock.PSARMatrix[0][3]
        else:
            if(stock.PSARMatrix[0][7] == 0 and stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6] < stock.PSARMatrix[1][0]):
                stock.PSARMatrix[1][2] = stock.PSARMatrix[0][3]
            else:
                stock.PSARMatrix[1][2] = stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6]
        #PSAR Update END

        #BULLBEAR Update START
        if(stock.PSARMatrix[1][2] < stock.PSARMatrix[1][0]):
            stock.PSARMatrix[1][7] = 1
        else:
            if(stock.PSARMatrix[1][2] > stock.PSARMatrix[1][1]):
                stock.PSARMatrix[1][7] = 0
        #BULLBEAR Update END

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

        stock.PSARMatrix[1][4] = stock.PSARMatrix[1][3] - stock.PSARMatrix[1][2] #set EP - PSAR
        stock.PSARMatrix[1][6] = stock.PSARMatrix[1][4] * stock.PSARMatrix[1][5] #set (EP - PSAR)*AF

    #Setup for next iteration
    stock.PSARMatrix[0] = stock.PSARMatrix[1]
    stock.PSARMatrix[1] = [0,0,0,0,0,0,0,0]

    stock.counter += 1

    #PSAR Implementation (Long Term)
    if(j == 0):
        stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[1][1] #set PSAR
        stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[1][0] #set EP
        stock.PSARMatrixlong[1][4] = stock.PSARMatrixlong[1][3] - stock.PSARMatrixlong[1][2] #set EP - PSAR
        stock.PSARMatrixlong[1][5] = stock.AF_incrementlong #set AF
        stock.PSARMatrixlong[1][6] = stock.PSARMatrixlong[1][4] * stock.PSARMatrixlong[1][5] #set (EP - PSAR)*AF
        stock.PSARMatrixlong[1][7] = 1 #set BULLBEAR

    if(j != 0 and stock.counter % 2 == 0):

        #PSAR Update START
        if(stock.PSARMatrixlong[0][7] == 1 and stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6] > stock.PSARMatrixlong[1][1]):
            stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][3]
        else:
            if(stock.PSARMatrixlong[0][7] == 0 and stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6] < stock.PSARMatrixlong[1][0]):
                stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][3]
            else:
                stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6]
        #PSAR Update END

        #BULLBEAR Update START
        if(stock.PSARMatrixlong[1][2] < stock.PSARMatrixlong[1][0]):
            stock.PSARMatrixlong[1][7] = 1
        else:
            if(stock.PSARMatrixlong[1][2] > stock.PSARMatrixlong[1][1]):
                stock.PSARMatrixlong[1][7] = 0
        #BULLBEAR Update END

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

        stock.PSARMatrixlong[1][4] = stock.PSARMatrixlong[1][3] - stock.PSARMatrixlong[1][2] #set EP - PSAR
        stock.PSARMatrixlong[1][6] = stock.PSARMatrixlong[1][4] * stock.PSARMatrixlong[1][5] #set (EP - PSAR)*AF

    if(j == 0 or stock.counter % 2 == 0):
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

def buy(stock):
    global api
    global curr_time
    print("Triggered Buy Command\n")

    stock.quantity = int(stock.capital/stock.limit)# Buys the greatest whole number of stocks and update stocks and capital for later use
    #Note: subtract quantity by 1 to prevent buying more than you can/set limit to limit * 1.02 or another value
    stock.buy_counter += 1
    stock.buy_order_time = get_pst_time()
    stock.buyorderid = str(stock.buy_counter) + " " + stock.buy_order_time
    api.submit_order(symbol=stock.Ticker, qty = str(stock.quantity), side = "buy", type = "market", client_order_id = stock.buyorderid, time_in_force ='day')

    time.sleep(10)

    closed_orders = api.list_orders(status="closed")
    for order in closed_orders:
        if order.client_order_id == stock.buyorderid:
            stock.stoploss_counter -= 1
            stock.stoploss_order_time = get_pst_time()
            stock.stoplossid = str(stock.stoploss_counter) + ' ' + stock.stoploss_order_time
            api.submit_order(symbol=stock.Ticker, qty = str(stock.quantity), side = "sell", type = "stop", stop_price = str(stock.close[-2]), time_in_force = 'day', client_order_id = str(stock.stoplossid))

    # money_invested = float(api.get_account().portfolio_value) - float(api.get_account().buying_power)
    stock.capital = stock.capital - float(stock.quantity * stock.limit)

    stock.bought_price = stock.limit
    stock.stoplosslimit = stock.close[-2]
    stock.profit_per_trade = stock.bought_price

    stock.bought = True
    stock.sold = False

    stock.buy_log.append([stock.limit, curr_time])

    stocks_list[i].buyindicator[-1] = stocks_list[i].close[-1]
    # x = input("Paused Code")

def sell(stock):
    global api

    print("Triggered Sell Command\n")

    orders = api.list_orders(status = 'all')

    for order in orders:
        if(order.client_order_id == stock.stoplossid):
            if order.status == 'open':
                api.cancel_order(order.client_order_id)
                order = api.submit_order(symbol=stock.Ticker, qty = str(stock.quantity), side ="sell", type = "market", time_in_force ='day')
                
                if(stock.stoplosslimit != 0):
                        stock.capital = stock.capital + (stock.stoplosslimit * stock.quantity)
                        stock.profit_per_trade = stock.stoplosslimit - stock.profit_per_trade

                        if(stock.stoplosslimit >= stock.bought_price):
                            stock.num_wins += 1
                        else:
                            stock.num_losses += 1

                else:
                    stock.capital = stock.capital + (stock.limit * stock.quantity)
                    stock.profit_per_trade = stock.limit - stock.profit_per_trade

                    if(stock.limit >= stock.bought_price):
                        stock.num_wins += 1
                    else:
                        stock.num_losses += 1

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

                stocks_list[i].soldindicator[-1] = stocks_list[i].close[-1]

                stock.sell_log.append([stock.limit, curr_time])
                break
            else:
                stock.stoplosslimit = order.filled_avg_price
                if(stock.stoplosslimit != 0):
                        stock.capital = stock.capital + (stock.stoplosslimit * stock.quantity)
                        stock.profit_per_trade = stock.stoplosslimit - stock.profit_per_trade

                        if(stock.stoplosslimit >= stock.bought_price):
                            stock.num_wins += 1
                        else:
                            stock.num_losses += 1

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

                stocks_list[i].soldindicator[-1] = stocks_list[i].close[-1]

                stock.sell_log.append([stock.limit, curr_time])
                break

def stoplosssell(stock):

    if(stock.stoplosslimit != 0):
        stock.capital = stock.capital + (stock.stoplosslimit * stock.quantity)
        stock.profit_per_trade = stock.stoplosslimit - stock.profit_per_trade

        if(stock.stoplosslimit >= stock.bought_price):
            stock.num_wins += 1
        else:
            stock.num_losses += 1

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

    stocks_list[i].soldindicator[-1] = stocks_list[i].close[-1]

    stock.sell_log.append([stock.limit, curr_time])

#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

iterations = 0
stocks_list = []

with open('Saved_Info_Initial.csv', 'r') as file:
    reader = csv.reader(file)
    csv_headings = next(reader)

    if csv_headings != None:
        i = 0
        for row in reader:
            # print(row)
            stocks_list.append(stock(row))
            stocks_list[i].print()
            i += 1

# Stored stock objects in stocks_list and intialized each object with info from Saved_Info_Initial.csv

stocks = len(stocks_list)

#USE FOR PRIMING
for i in range(stocks):
    data = yfinance.download(tickers = symbol[i], period = timeframe, interval = increment)

    for j in range(len(data)):
        data_primer(stocks_list[i], j, data.iloc[j])

    stock = stocks_list[i]

    figure, axis = plt.subplots(1, 3)
    figure.set_figwidth(17)

    axis[0].plot(stock.t, stock.close, 'k', stock.t, stock.buyindicator, 'og', stock.t, stock.soldindicator, 'or', stock.t, stock.histLongPSAR, 'xc', stock.t, stock.histShortPSAR, 'xm')
    axis[0].set_title(stock.Ticker + ' PSAR + EMAs')

    axis[1].plot(stock.t[50:], stock.MACD_val[50:], 'g', stock.t[50:], stock.MACD9_arr[50:], 'r')
    axis[1].set_title(stock.Ticker + ' MACD + Signal')

    axis[2].plot(stock.t, stock.RSI, 'm', stock.t, [70]*len(stock.t), 'b', stock.t, [30]*len(stock.t), 'b')
    axis[2].set_title(stock.Ticker + ' RSI')
    plt.show()

    # x = input("Paused Code: ")

# Got Priming Data and primed each stock object

counter = 0
x = 0

key = 'PKG4BZ9XQIDMN0NU02T4'
sec = 'oo85kzfGRdOIT9iU3fJrR13zpf1NpTCN1t5hbw3L'
url = 'https://paper-api.alpaca.markets'

global api
api = tradeapi.REST(key, sec, url, api_version='v2')
#Init our account var
account = api.get_account()
#Should print 'ACTIVE'
print(account.status)

# Connected to ALPACA

for i in range(stocks):
    netcapital += stocks_list[i].capital

while(True):
    
    check_time = datetime.today() #Gets current time

    # if(x < 10):
    #     print(f"Current Time: {check_time}\n")
    #     x += 1

    if(check_time.hour >= 6 and check_time.hour <= 11): #check_time.hour >= 0:
        start_time = time.time()

        print("Beginning Trades!\n")

        while(check_time.hour <= 11): #check_time.hour <= 13
            end_time = time.time()

            # print("Entered 2nd while")
            # input()

            if start_time + timestep <= end_time:
                start_time = time.time()
                
                for i in range(stocks):
                    print(f"---------------{stocks_list[i].Ticker} Stock Start ---------------")
                    update(stocks_list, i)
                    # hard_sell(stocks_list[i])
                    stocks_list[i].setcounter += 1

                    if(stocks_list[i].hard_sell == False):

                        if(stocks_list[i].changes[-1] < 0):

                            if((stocks_list[i].PSARMatrix[0][7] == 0 and stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1]) or (stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1] and stocks_list[i].EMA_Slope < 0) or (stocks_list[i].close[-1] < stocks_list[i].stoplosslimit)):
                                print("Entered Sell Check")
                                if(stocks_list[i].bought == True and stocks_list[i].sold == False):

                                    # if(stocks_list[i].bought_price <= stocks_list[i].limit):

                                        sell(stocks_list[i])

                                        print(f"Made a profit of: {stocks_list[i].profit[-1]}")

                                        continue

                        elif(stocks_list[i].changes[-1] > 0):

                            if((stocks_list[i].MACD_val[-1] > stocks_list[i].MACD9_arr[-1] and stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1)  or (stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1) or (stocks_list[i].RSI[-2] < 30 and stocks_list[i].RSI[-2] < stocks_list[i].RSI[-1])):#or stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1
                            #if(stocks_list[i].PSARMatrix[0][7] == 1 and stocks_list[i].PSARMatrixlong[0][7] == 1):
                                if(stocks_list[i].bought == False and stocks_list[i].sold == True):
                                    if(stocks_list[i].EMA_Slope > 0):
                                        # if(stocks_list[i].high[-1] > stocks_list[i].high[-2] and stocks_list[i].low[-1] > stocks_list[i].low[-2]):
                                        #     if(stocks_list[i].high[-1] > stocks_list[i].high[-3]):
                                                buy(stocks_list[i])
                                                
                                else:
                                    print("Entered buying check but did not meet requirements")
                                    
                                
                        print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
                    
                    else:
                        if(stocks_list[i].MACD_val[-2] > stocks_list[i].MACD9_arr[-2] and stocks_list[i].MACD_val[-1] < stocks_list[i].MACD9_arr[-1]):
                            stocks_list[i].hard_sell = False
    
                print(f"--------------- Finished Iteration {counter} ---------------\n")
                counter += 1
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
        sell(stocks_list[i])
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

save_info(stocks_list, netcapital, netsectionval, bestsectionval)

email()