import pandas as pd #Reading/writting files
import matplotlib.pyplot as mpl #Graphing data
import numpy #calculations in general
import seaborn #
import fxcmpy #Forex
import yfinance #yahoo Finance
import plotly.graph_objs as go #plotting data
import csv
#------------------------------------
#x = [0,1,2,3,4,5,7,9,11,13]
#y = [i*3 for i in range(0,10)]

#mpl.plot(x,y)
#mpl.show()
#------------------------------------
#a = (10, 15)
#inputs = numpy.random.rand(10,15)

#hm = seaborn.heatmap(inputs)

#mpl.show()
#------------------------------------
#Yahoo Finance API Stock bot
#Tickers: S&P500 -> ^GSPC
#Start + End Date or Period: 
#Interval: 
ticker = '^GSPC'

data = yfinance.download(tickers=ticker,period='2m', interval = '1m')
#print(data)

#fig = go.Figure()
#fig.add_trace(go.Candlestick(x=data.index,open=data['Open'],high=data['High'],low=data['Low'],close=data['Close'],name = 'market data'))
#fig.update_layout(title = 'S&P500', yaxis_title='Stock Price (USD per Shares)')
#fig.update_xaxes(
#    rangeslider_visible=True,
#    rangeselector=dict(
#        buttons=list([
#            dict(count=15, label="15m", step="minute", stepmode="backward"),
#            dict(count=45, label="45m", step="minute", stepmode="backward"),
#            dict(count=1, label="HTD", step="hour", stepmode="todate"),
#            dict(count=3, label="3h", step="hour", stepmode="backward"),
#            dict(step="all")
#        ])
#    )
#)
#fig.show()

data.to_csv('SNP500_data.csv')

floorPrice = 0
t = 0
action = 0; #NULL = 0, buy = 1, sell = 2, hold = 3
movingInterval = []
column_headers = []
data = []

with open('SNP500_data.csv') as csv_file:
    csv_reader = csv.reader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            column_headers = row
            line_count += 1
        else:
            data.append(row)
            line_count += 1











































































