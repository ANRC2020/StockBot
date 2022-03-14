import alpaca_trade_api as tradeapi
from alpaca_trade_api.entity import PortfolioHistory
from pandas._libs.tslibs import Timestamp
import yfinance
import time
from datetime import datetime
import pandas as pd
import csv
from csv import DictWriter, writer, reader
import threading


files = [] #all the titles of each stock's file of info
symbol = ['ANVS','AAPL']
stocks = 2
timeframe = '1d'
increment = '2m'

for i in range(stocks):
    data = yfinance.download(tickers = symbol[i], period = timeframe, interval = increment)

    title = f"TestDataSet{i}.csv"
    files.append(title)

    with open(title, 'w') as csvfile:
        fieldnames = ['Open', "High", "Low", "Close", "Adj Close", "Volume"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print(f"{len(data)}")

        for j in range(len(data)):
            writer.writerow({'Open': data.iloc[j]['Open'], 'High': data.iloc[j]['High'], 'Low': data.iloc[j]['Low'], 'Close':data.iloc[j]['Close'], 'Adj Close':data.iloc[j]['Adj Close'], 'Volume':data.iloc[j]['Volume']})
        csvfile.close()

with open("MultiDataLog.csv", 'w') as csvfile:
    fieldnames = ["Filename"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for file in files:
        writer.writerow({'Filename':file})
    csvfile.close()