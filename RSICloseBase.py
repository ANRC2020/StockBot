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

n = 14
ticker = 'AAPL'
data = yfinance.download(tickers = ticker, period ='1d', interval = '1m')

with open('RSIDataSet.csv', 'w', newline='') as csvfile:
    fieldnames = ['Close']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    print(f"Length of data: {len(data)}")
    writer.writeheader()

    for i in range(len(data)):
        writer.writerow({'Close':data.iloc[i]['Close']})

counter = 0
# print(len(data))
# print(data.iloc[0]['Close'])
close = []
UPMove = []
DOWNMove = []
diff = []
RSI = []
t = []
upper = []
lower = []

for i in range(len(data)):
    close.append(data.iloc[i]['Close'])

    if(i >= 1):
        diff.append(close[i] - close[i - 1])

        if(diff[-1] > 0):
            UPMove.append(diff[-1])
            DOWNMove.append(0)
        if(diff[-1] < 0):
            UPMove.append(0)
            DOWNMove.append(abs(diff[-1]))

    if(len(UPMove) < n):
        continue
    
    avgup = 0
    avgdown = 0

    for j in range(1,n + 1):
        avgup += UPMove[-j]
        avgdown += DOWNMove[-j]

    avgup /= n
    avgdown /= n

    RS = avgup/avgdown

    RSI.append(100 - (100/(1 + RS)))
    t.append(i)
    upper.append(70)
    lower.append(30)

for i in range(n):
    close.pop(0)

plt.plot(t, RSI, 'g', t, upper, 'p', t, lower, 'p')
plt.title(ticker)
plt.show()