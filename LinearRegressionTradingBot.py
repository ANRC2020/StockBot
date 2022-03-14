import quandl
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
import yfinance
import matplotlib.pyplot as plt

t = [0,1,2,3,4,5,6]
prices = [0,0,0,0,0,0,0]

for i in range(100):
    confidence = 0
    lr_prediction = 0

    df = yfinance.download(tickers = "AAPL", period ='1y', interval = '1h')
    #df = quandl.get("WIKI/AMZN")
    df.to_csv('MLData.csv')
    # Take a look at the data
    #print(df.head())

    # Get the Adjusted Close Price
    df = df[['Close']]

    # print(f"Type df = {type(df)}")
    df = df[:-7]

    # A variable for predicting 'n' days out into the future
    forecast_out = 7 #'n=30' days
    #Create another column (the target ) shifted 'n' units up 
    df['Prediction'] = df[['Close']].shift(-forecast_out)

    X = np.array(df.drop(['Prediction'],1))
    X = X[:-forecast_out]
    y = np.array(df['Prediction'])
    # Get all of the y values except the last '30' rows
    y = y[:-forecast_out]
    # print(y)

    # Split the data into 80% training and 20% testing
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Create and train the Support Vector Machine (Regressor)
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_rbf.fit(x_train, y_train)
    # Testing Model: Score returns the coefficient of determination R^2 of the prediction.
    # The best possible score is 1.0
    svm_confidence = svr_rbf.score(x_test, y_test)
    # print("svm confidence: ", svm_confidence)

    # Create and train the Linear Regression Model
    lr = LinearRegression()
    # Train the model
    lr.fit(x_train, y_train)

    # Testing Model: Score returns the coefficient of determination R^2 of the prediction.
    # The best possible score is 1.0
    lr_confidence = lr.score(x_test, y_test)
    print("lr confidence: ", lr_confidence)
    confidence = lr_confidence

    # Set x_forecast equal to the last 30 rows of the original data set from Adj Close column
    x_forecast = np.array(df.drop(['Prediction'],1))[-forecast_out:]
    # print(x_forecast)

    # Print linear regression model predictions for the next '30' days
    lr_prediction = lr.predict(x_forecast)

    print(f"lr_prediction = {lr_prediction}")
    print(f"Type lr_prediction = {(lr_prediction[0])}")

    for j in range(forecast_out):
        prices[j] += lr_prediction[j]

    print(f"Itteration: {i}")


for i in range(forecast_out):
    prices[i] /= 100

plt.plot(t, prices, 'r')
plt.title('AAPL')
plt.show()