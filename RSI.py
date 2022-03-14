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

def calcSmmaUp(data,n,i,avgUt1):
    if (avgUt1==0):
        sumUpChanges = 0
        for j in range(n):
            change = data.iloc[i-j]['Close'] - data.iloc[i-j]['Open']

            if change < 0:
                sumUpChanges += change
        return sumUpChanges/n
    else:
        change = data.iloc[i]['Close'] - data.iloc[i]['Open']
        if change < 0:
            change = 0
        return ((avgUt1*(n-1))+change)/n

def calcSmmaDown(data,n,i,avgDt1):
    if avgDt1 == 0:
        sumDownChanges = 0

        for j in range(n):
            change = data.iloc[i-j]['Close'] - data.iloc[i-j]['Open']

            if change < 0:
                sumDownChanges -= change
        return sumDownChanges/n
    else:
        change = data.iloc[i]['Close'] - data.iloc[i]['Open']
        if change > 0:
            change = 0
        return ((avgDt1 * (n-1)) - change)/n

def calculateRSI(data,n):
    results = []
    t = []
    upper = []
    lower = []

    ut1 = 0
    dt1 = 0
    for i in range(len(data)):
        if i < n:
            continue

        ut1 = calcSmmaUp(data,n,i,ut1)
        dt1 = calcSmmaDown(data,n,i,dt1)

        results.append(100 - 100/(1+(ut1/dt1)))
        t.append(i)
        upper.append(70)
        lower.append(30)


    plt.plot(t[14:], results[14:], 'g',t,upper,'p',t,lower,'p')
    plt.title(ticker)
    plt.show()


ticker = 'TGT'
data = yfinance.download(tickers = ticker, period ='1y', interval = '1d')

with open('RSIDataSet.csv', 'w', newline='') as csvfile:
    fieldnames = ['Open', 'Close']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    print(f"Length of data: {len(data)}")
    writer.writeheader()

    for i in range(len(data)):
        writer.writerow({'Open':data.iloc[i]['Open'], 'Close':data.iloc[i]['Close']})

numrow = 1
n = 14
calculateRSI(data,n)




    






