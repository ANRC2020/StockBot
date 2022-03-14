class stick:
    high = 0
    low = 0
    open_price = 0
    close = 0

    def __init__(self, high, low, open_price, close):
        self.high = high
        self.low = low
        self.open_price = open_price
        self.close = close
#------------------------------------------------------
# High = input("Enter High Value: ")
# Low = input("Enter Low Value: ")
# Open_val = input("Enter Open Value: ")
# Close = input("Enter Close Vlaue: ")
arr = []

arr.append(stick(10, 6, 9, 1.27))
print(f"High: {arr[0].high}, Low: {arr[0].low}, Open: {arr[0].open_price}, Close: {arr[0].close}\n")

limit_price = float(arr[0].close) * 1.01
print(f"Limit Price: {limit_price}\n")