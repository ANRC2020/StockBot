import yfinance
import csv
from csv import writer, reader

name = 'Open'

data = yfinance.download(tickers = "AAPL", period ='2d', interval = '5m')
# print(data.iloc[1][name])
# arr = data.iloc[0]
# arr = data.iloc[:,0:0]
# out = str(arr.iloc[0])

# print(out[17:42])
print(data.iloc[1])
data.to_csv('AllData.csv')
date = []

with open('AllData.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)

    for row in reader:
        date.append(row[0])

with open('TestDataSet.csv', 'w') as csvfile:
    # fieldnames = ['Open', "High", "Low", "Close", "Adj Close", "Volume", "Date"]
    fieldnames = [name]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    print(f"Length of data: {len(data)}")
    writer.writeheader()

    for i in range(len(data)):
        # writer.writerow({'Open': data.iloc[i]['Open'], 'High': data.iloc[i]['High'], 'Low': data.iloc[i]['Low'], 'Close':data.iloc[i]['Close'], 'Adj Close':data.iloc[i]['Adj Close'], 'Volume':data.iloc[i]['Volume'], 'Date':data.iloc[i].name})
        # if(i%2 == 0):
        writer.writerow({name:data.iloc[i][name]})