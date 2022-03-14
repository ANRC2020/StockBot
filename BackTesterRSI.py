import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import PortfolioHistory
from numpy import Infinity, diff
from pandas._libs.tslibs import Timestamp
import yfinance
import time
from datetime import datetime
import pandas as pd
import csv
from csv import DictWriter, writer, reader
import matplotlib.pyplot as plt

global ut1 
ut1 = 0
    
global dt1 
dt1 = 0

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

def calculateRSI(open, close, n, i):
    global ut1
    global dt1
    
    result = 0  

    ut1 = calcSmmaUp(open,close,n,i,ut1)
    dt1 = calcSmmaDown(open,close,n,i,dt1)

    result = (100 - 100/(1+(ut1/dt1)))

    print(f"ut1: {ut1}\ndt1: {dt1}")
    print(f"result = {result}")
    x = input()
    

    return result


ticker = 'AAPL'
data = yfinance.download(tickers = ticker, period ='1w', interval = '5m')

with open('RSIDataSet.csv', 'w', newline='') as csvfile:
    fieldnames = ['Open', 'Close']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    print(f"Length of data: {len(data)}")
    writer.writeheader()

    for i in range(len(data)):
        writer.writerow({'Open':data.iloc[i]['Open'], 'Close':data.iloc[i]['Close']})

n = 14
close = []
open = []
t = []
upper = []
lower = []
RSI = []

for i in range(len(data)):
    close.append(data.iloc[i]['Close'])
    open.append(data.iloc[i]['Open'])
    
    if(len(close) >= n):
        print(f"i = {i}\nlen(close) = {len(close)}")
        t.append(i)
        upper.append(70)
        lower.append(30)
        RSI.append(calculateRSI(open, close, n, i))

plt.plot(t[14:], RSI[14:], 'g', t[14:], upper[14:], 'b', t[14:], lower[14:], 'b')
plt.title(ticker)
plt.show()