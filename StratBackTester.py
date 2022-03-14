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
# import ResearchTeam

global timestep
timestep = 300

global symbol
symbol = ['ROOT']
# symbol = ResearchTeam.run()
# print(symbol)
# x = input("Paused")

global timeframe
timeframe = '1d'

global increment
increment = '5m'

global IP #Initilization Period = number of points over which the code remains dormant prior to trading 
IP = 0

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
    high = []
    low = []
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

    strat_type = []
    stoplosslimit = 0
    pricetarget = 0

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
        self.high = []
        self.low = []
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
        self.strat_type = []
        self.stoplosslimit = 0
        self.pricetarget = 0

    def print(self):
        print(f"Ticker: {self.Ticker}")
        print(f"Quantity: {self.quantity}")
        print(f"Capital: {self.capital}\n")

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

    for row in csv_reader:

        if(i == stock.counter):
            stock.t.append(stock.counter) #Save times
            stock.close.append(float(row[3])) #Save close prices
            stock.open.append(float(row[0])) #Save open prices
            stock.high.append(float(row[1])) #Save High prices
            stock.low.append(float(row[2])) #Save Low Prices

            print(stock.open[-1])
            print(stock.close[-1])
            print(stock.low[-1])
            print(stock.high[-1])

            stock.buyindicator.append(None)
            stock.soldindicator.append(None)
            curr_time = str(row[6])
        
        i += 1
    
    stock.counter += 1

    if(IL == 1):
        stock.strat_type.append(float(0))
    else:

        # Type 1: curr_high < prev_high and curr_low > prev_low
        if(stock.high[-1] <= stock.high[-2] and stock.low[-1] >= stock.low[-2]):
            stock.strat_type.append(1)
        # Type 2U: curr_high > prev_high and curr_low > prev_low
        elif((stock.high[-1] > stock.high[-2] and stock.low[-1] >= stock.low[-2])):
            stock.strat_type.append(2)
        #Type 2D: curr_high < prev_high and curr_low < prev_low
        elif((stock.high[-1] <= stock.high[-2] and stock.low[-1] < stock.low[-2])):
            stock.strat_type.append(-2)
        # elif(stock.high[-1] > stock.high[-2] and stock.low[-1] < stock.low[-2]):
        else:
            stock.strat_type.append(3)
        # else:
        #     stock.strat_type.append(1)

    stock.limit = stock.close[-1]

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
    stock.profit_per_trade = stock.bought_price
    stock.stoplosslimit = stock.low[-2]

    i = -3
    while(True):
        if(stock.high[i] > stock.high[-1]):
            stock.pricetarget = stock.high[i]
            break
        else:
            i -= 1

    stock.bought = True
    stock.sold = False

    stock.buy_log.append([stock.limit, curr_time])

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
    stock.target = 0

    stock.bought = False
    stock.sold = True

    stock.sell_log.append([stock.limit, curr_time])
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
                    print(f"---------------{stocks_list[i].Ticker} Stock Start ---------------")
                    percent_change_update(stocks_list[i], i, 0)
                    # hard_sell(stocks_list[i])
                    stocks_list[i].setcounter += 1

                
                    if(IP == 0):

                        if(stocks_list[i].hard_sell == False):

                            if(stocks_list[i].bought == True and stocks_list[i].sold == False):

                                if(stocks_list[i].stoplosslimit > stocks_list[i].low[-1]):

                                    sell(stocks_list[i])
                            else:

                                if(stocks_list[i].strat_type[-1] == -2 and (stocks_list[i].open[-1] > stocks_list[i].low[-2] and stocks_list[i].high[-1] > stocks_list[i].high[-2])):                                

                                    buy(stocks_list[i])

                            

                            print(f"---------------{stocks_list[i].Ticker} Stock End ---------------\n")
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

    y = input("Enter 'y' for graphs: ")
    if(y == 'y'):
        for stock in stocks_list:
            x = input()
            if(x != ''):
                plt.plot(stock.t, stock.close, 'k', stock.t, stock.buyindicator, 'og', stock.t, stock.soldindicator, 'or')
                plt.title(stock.Ticker + 'With STRAT')
                plt.show()

    save_info(stocks_list, netcapital, netsectionval, bestsectionval)

    print(stocks_list[0].strat_type)

    # email()