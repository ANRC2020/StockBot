from datetime import datetime
from pytz import timezone
from os import system
from pandas.core.indexing import IndexingError
import pytz
import quandl
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
# from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
import yfinance
import csv
import time

def partition(arr, low, high):
    i = (low-1)      
    pivot = arr[high][3]     
  
    for j in range(low, high):
  
        if arr[j][3] <= pivot:
  
            i = i+1
            arr[i], arr[j] = arr[j], arr[i]
  
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return (i+1)
   
def quickSort(arr, low, high):
    if len(arr) == 1:
        return arr
    if low < high:
        pi = partition(arr, low, high)
        quickSort(arr, low, pi-1)
        quickSort(arr, pi+1, high)

def get_Data(ticker):
    try:
        
        df = yfinance.download(tickers = ticker, period = '2y', interval = '1d')
        df = df[['Close']]
        df = df[:-1]
        return get_prediction(df)
    except (RuntimeError, TypeError, NameError, ValueError, IndexError):
        return -1, 1, 0

def get_prediction(df):

    curr_p = df['Close'].iloc[-1]
    sum_pred = 0
    sum_conf = 0
    num = 100

    forecast_out = 1 #'n=30' days
    df['Prediction'] = df[['Close']].shift(-forecast_out)

    X = np.array(df.drop(['Prediction'],1))
    X = X[:-forecast_out]

    y = np.array(df['Prediction'])
    y = y[:-forecast_out]

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    lr = LinearRegression()
    
    for i in range(num):
        # Create and train the Linear Regression Model
        
        # Train the model
        lr.fit(x_train, y_train)

        # Testing Model: Score returns the coefficient of determination R^2 of the prediction.
        # The best possible score is 1.0
        lr_confidence = lr.score(x_test, y_test)
        sum_conf = float(lr_confidence)

        # Set x_forecast equal to the last 30 rows of the original data set from Adj Close column
        x_forecast = np.array(df.drop(['Prediction'],1))[-forecast_out:]

        lr_prediction = lr.predict(x_forecast)
        sum_pred += float(lr_prediction)
    
    return float(sum_pred/num), float(curr_p), float(sum_conf/num)
    

def run():
    symbol = []
    with open('constituents_csv.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)

        for i in reader:
            if(i[0] != 'Symbol'):
                symbol.append([str(i[0]),0,0,0])
                # print(symbol)

    itt = len(symbol)

    i = 0
    while i < len(symbol):

        # if(i == 50):
        #     break

        print(i)
        Predicted_P,curr_p,symbol[i][2] = get_Data(symbol[i][0])

        if(((Predicted_P - curr_p)/curr_p) * 100 > 0):
            if(curr_p <= 1000):
                symbol[i][1] = ((Predicted_P - curr_p)/curr_p) * 100
                symbol[i][3] = (symbol[i][2] * (.75)) + (symbol[i][1] * (.25))
        i += 1

    symbol = [sym for sym in symbol if sym[3] != 0 ]

    quickSort(symbol, 0, len(symbol) - 1)

    symbol.reverse()

    arr = symbol[:5]

    now = datetime.now(tz = pytz.utc)
    now = now.astimezone(timezone('US/Pacific'))
    curr_time = now.strftime('%m-%d-%Y %H:%M:%S')


    with open('Prediction.txt','a',newline = '') as file:
        file.write("---------------------------------------------------\n")
        file.write(curr_time + '\n')

        for a in arr:
            file.write(str(a) + '\n')

        file.write("---------------------------------------------------\n")

    return [item[0] for item in symbol[:15]]

#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

symbol = []

arr = run()

print(arr)
