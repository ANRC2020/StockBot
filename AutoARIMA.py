import pandas as pd
import numpy as np
from pmdarima.arima import AutoARIMA
import plotly.express as px
import plotly.graph_objects as go
from sklearn import linear_model
from tqdm.notebook import tqdm
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from datetime import date, timedelta
import yfinance as yf
# import 

def get_positions(difference, thres=3, short=True):
    """
    Compares the percentage difference between actual 
    values and the respective predictions.
    
    Returns the decision or positions to long or short 
    based on the difference.
    
    Optional: shorting in addition to buying
    """
    
    if difference > thres/100:
        
        return 1
    
    
    elif short and difference < -thres/100:
        
        return -1
    
    
    else:
        
        return 0

# Getting the date five years ago to download the current timeframe
years = (date.today() - timedelta(weeks=260)).strftime("%Y-%m-%d")
# Stocks to analyze
stocks = ['GE', 'GPRO','FB','F']
# Getting the data for multiple stocks
df = yf.download(stocks, start=years).dropna()
# Storing the dataframes in a dictionary
stock_df = {}
for col in set(df.columns.get_level_values(0)):
    
    # Assigning the data for each stock in the dictionary
    stock_df[col] = df[col]

# Finding the log returns
stock_df['LogReturns'] = stock_df['Adj Close'].apply(np.log).diff().dropna()
# Using Moving averages
stock_df['MovAvg'] = stock_df['Adj Close'].rolling(10).mean().dropna()
# Logarithmic scaling of the data and rounding the result
stock_df['Log'] = stock_df['MovAvg'].apply(np.log).apply(lambda x: round(x, 2))

# Days in the past to train on
days_to_train = 180

# Days in the future to predict
days_to_predict = 5

# Establishing a new DF for predictions
stock_df['Predictions'] = pd.DataFrame(index=stock_df['Log'].index,columns=stock_df['Log'].columns)

# Iterate through each stock
for stock in tqdm(stocks):
    print("In loop")
    
    # Current predicted value
    pred_val = 0
    
    # Training the model in a predetermined date range
    for day in tqdm(range(1000, stock_df['Log'].shape[0]-days_to_predict)):        

        # Data to use, containing a specific amount of days
        training = stock_df['Log'][stock].iloc[day-days_to_train:day+1].dropna()
        
        # Determining if the actual value crossed the predicted value
        cross = ((training[-1] >= pred_val >= training[-2]) or 
                 (training[-1] <= pred_val <= training[-2]))
        
        # Running the model when the latest training value crosses the predicted value or every other day 
        if cross or day % 2 == 0:

            # Finding the best parameters
            model    = LinearRegression(start_p=0, start_q=0,
                                 start_P=0, start_Q=0,
                                 max_p=8, max_q=8,
                                 max_P=5, max_Q=5,
                                 error_action='ignore',
                                 information_criterion='bic',
                                 suppress_warnings=True)

            # Getting predictions for the optimum parameters by fitting to the training set            
            forecast = model.fit_predict(training,
                                         n_periods=days_to_predict)

            # Getting the last predicted value from the next N days
            stock_df['Predictions'][stock].iloc[day:day+days_to_predict] = np.exp(forecast[-1])


            # Updating the current predicted value
            pred_val = forecast[-1]

# Shift ahead by 1 to compare the actual values to the predictions
pred_df = stock_df['Predictions'].shift(1).astype(float).dropna()


for stock in stocks:
    
    fig = go.Figure()
    
    # Plotting the actual values
    fig.add_trace(go.Scatter(x=pred_df.index,
                             y=stock_df['MovAvg'][stock].loc[pred_df.index],
                             name='Actual Moving Average',
                             mode='lines'))
    
    # Plotting the predicted values
    fig.add_trace(go.Scatter(x=pred_df.index,
                             y=pred_df[stock],
                             name='Predicted Moving Average',
                             mode='lines'))
    
    # Setting the labels
    fig.update_layout(title=f'Predicting the Moving Average for the Next {days_to_predict} days for {stock}',
                      xaxis_title='Date',
                      yaxis_title='Prices')
    
    fig.show()

for stock in stocks:
    
    # Finding the root mean squared error
    rmse = mean_squared_error(stock_df['MovAvg'][stock].loc[pred_df.index], pred_df[stock], squared=False)
print(f"On average, the model is off by {rmse} for {stock}\n")


# # Creating a DF dictionary for trading the model
# trade_df = {}

# # Getting the percentage difference between the predictions and the actual values
# trade_df['PercentDiff'] = (stock_df['Predictions'].dropna() / 
#                            stock_df['MovAvg'].loc[stock_df['Predictions'].dropna().index]) - 1

# # Getting positions
# trade_df['Positions'] = trade_df['PercentDiff'].applymap(lambda x: get_positions(x, 
#                                                                                  thres=1, 
#                                                                                  short=True) / len(stocks))

# # Preventing lookahead bias by shifting the positions
# trade_df['Positions'] = trade_df['Positions'].shift(2).dropna()

# # Getting Log Returns
# trade_df['LogReturns'] = stock_df['LogReturns'].loc[trade_df['Positions'].index] 

# # Calculating Returns by multiplying the 
# # positions by the log returns
# returns = trade_df['Positions'] * trade_df['LogReturns']
# # Calculating the performance as we take the cumulative 
# # sum of the returns and transform the values back to normal
# performance = returns.cumsum().apply(np.exp)
# # Plotting the performance per stock
# px.line(performance,
#         x=performance.index,
#         y=performance.columns,
#         title='Returns Per Stock Using ARIMA Forecast',
#         labels={'variable':'Stocks',
#                 'value':'Returns'})

# # Returns for the portfolio
# returns = (trade_df['Positions'] * trade_df['LogReturns']).sum(axis=1)

# # Returns for SPY
# spy = yf.download('SPY', start=returns.index[0]).loc[returns.index]

# spy = spy['Adj Close'].apply(np.log).diff().dropna().cumsum().apply(np.exp)

# # Calculating the performance as we take the cumulative sum of the returns and transform the values back to normal
# performance = returns.cumsum().apply(np.exp)

# # Plotting the comparison between SPY returns and ARIMA returns
# fig = go.Figure()

# fig.add_trace(go.Scatter(x=spy.index,
#                          y=spy,
#                          name='SPY Returns',
#                          mode='lines'))

# fig.add_trace(go.Scatter(x=performance.index,
#                          y=performance.values,
#                          name='ARIMA Returns on Portfolio',
#                          mode='lines'))

# fig.update_layout(title='SPY vs ARIMA Overall Portfolio Returns',
#                   xaxis_title='Date',
#                   yaxis_title='Returns')

# fig.show()
