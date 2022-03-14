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

global buyid
buyid = 1

global stoplossid
stoplossid = -1

key = 'PKR0Y3INLX265GC46057'
sec = 'PlGhPPRcjsQ6SCm6xoMwqVoAjfLWJolFzoCuhwoT'
url = 'https://paper-api.alpaca.markets'
api = tradeapi.REST(str(key), str(sec), url, api_version='v2')

x = ""
currbuyid = 0
currsellid = 0

while(x != 'e'):
    print(f"currbuyid: {currbuyid}")
    print(f"currsellid: {currsellid}")

    y = input("Buy or Sell?: ")

    if(y == "b"):
        api.submit_order(symbol='AMC', qty = '1', side = "buy", type = "market", time_in_force ='day', client_order_id = str(buyid))
        currbuyid = buyid
        buyid += 1
        
    elif(y == "s"):
        price = float(input("Enter Stop-Loss Limit Price: "))
        api.submit_order(symbol='AMC', qty = '1', side = "sell", type = "stop", stop_price = str(price), time_in_force = 'day', client_order_id = str(stoplossid))
        currsellid = stoplossid
        stoplossid -= 1

    elif(y == "c"):
        open_orders = api.list_orders(status = "Open", limit = 100)

        for order in open_orders:
            if(order.client_order_id == str(currsellid)):
                api.cancel_order(order.id)

                
    elif(y == 'u'):
        price = float(input("Enter new stoploss limit: "))

        open_orders = api.list_orders(status = "Open", limit = 100)

        for order in open_orders:
            if(order.client_order_id == str(currsellid)):
                api.cancel_order(order.id)

                api.submit_order(symbol='AMC', qty = '1', side = "sell", type = "stop", stop_price = str(price), time_in_force = 'day', client_order_id = str(stoplossid))
                
    
    elif(y == 'r'):
        price = float(input("Enter new stoploss limit: "))

        api.replace_order(order_id = str(currsellid), qty = '1', stop_price= str(price), time_in_force = 'day', client_order_id = str(stoplossid))
        currsellid = stoplossid
        stoplossid -= 1

    x = input("Continue? (c) ")
    # api.cancel_order(my_order.id)