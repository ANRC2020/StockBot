import csv
from Slope import slope
from RSI import calculateRSI
from EMA import EMA
from MACD import MACD
from PSAR import short_term_PSAR, long_term_PSAR
from Get_Close import get_close

def percent_change_update(stock, x, IL, filelist, timestep):
    # data = yfinance.download(tickers = stock.Ticker, period ='5m', interval = '5m')
    # print(data)

    file = open(str(filelist[x]))
    # file = open('TestDataSet.csv')
    csv_reader = csv.reader(file)

    # csv_reader = reader(read_obj)

    
    close1 = 0
    close0 = 0

    close0, close1 = get_close(stock,csv_reader)

    stock.PSARcounter += 1

    # stock.slopes.append((float(data.iloc[1]['Close'] - data.iloc[0]['Close'])/float(data.iloc[0]['Close'])) * 100)
    # if(stock.setcounter == 0):

    #Change Between Consecutive Close Values
    
    slope(stock,close1,close0)    

    stock.limit = close1 * 1.00

    EMA(stock,close1,timestep)

    MACD(stock, close1)

    short_term_PSAR(stock, IL)
    stock.counter += 1
    long_term_PSAR(stock, IL)
    stock.slopecounter += 1

    #Update RSI Array
    if(len(stock.close) >= 14):
        stock.RSI.append(calculateRSI(stock, 14, len(stock.close) - 1))
    else:
        stock.RSI.append(0)

    # print(f"Slope for {stock.Ticker} was {stock.changes[-1]}")
    # print(f"EMA_Slope for {stock.Ticker} was {stock.EMA_Slope}")
    # print(f"Length of slopes: {len(stock.changes)}\n\n")
