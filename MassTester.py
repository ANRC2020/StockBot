from MACDPSARBaseWithRSIMassTester import setstocks
import csv
from csv import reader, writer  

def partition(array, begin, end):
    pivot_idx = begin
    for i in range(begin+1, end+1):
        if array[i][2] <= array[begin][2]:
            pivot_idx += 1
            array[i], array[pivot_idx] = array[pivot_idx], array[i]
    array[pivot_idx], array[begin] = array[begin], array[pivot_idx]
    return pivot_idx

def quick_sort_recursion(array, begin, end):
    if begin >= end:
        return
    pivot_idx = partition(array, begin, end)
    quick_sort_recursion(array, begin, pivot_idx-1)
    quick_sort_recursion(array, pivot_idx+1, end)

def quick_sort(array, begin=0, end=None):
    if end is None:
        end = len(array) - 1
    
    return quick_sort_recursion(array, begin, end)

#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------
results = []
ideal_stock = 0
# directory = 'MassTesterDataBase.csv'
directory = 'PassStocks.csv'
# directory = 'PreviousTopWinners.csv'
with open(directory, 'r') as file:
    reader = csv.reader(file)
    
    for row in reader:
        if(len(row[0]) != 0):
            row = str(row[0])
        else:
            continue
        result = setstocks(row)

        if len(result) != 0: 
            results.append(result)
            if(result[-1] > 15):
                ideal_stock += 1

    file.close()

quick_sort(results, 0, len(results) - 1)

# print(results)

high = results[-15:]
low = results[:15]

high_load = [x[0] for x in results[-15:]]

if(directory != 'PreviousTopWinners.csv'):
    with open('PreviousTopWinners.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        for i in range(len(high_load)):
            writer.writerow([high_load[i]])
        
        file.close()
else:
    with open('NextWeekResults.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        for i in range(len(high_load)):
            writer.writerow([high_load[i]])
        
        file.close()

print(f"high = {high}\n")

print(f"low = {low}")

win_count = 0
win_sum = 0
zero_count = 0
loss_count = 0
loss_sum = 0

for i in range(len(results)):
    if(results[i][2] > 0):
        win_count += 1
        win_sum += results[i][2]
    elif(results[i][2] == 0):
        zero_count += 1
    else:
        loss_count += 1
        loss_sum += results[i][2]

if(win_count != 0 and loss_count != 0):
    print(f"Wins: {win_count}\nLosses: {loss_count}\nZeros: {zero_count}\nWin Avg: {win_sum/win_count}\nLoss Avg: {loss_sum/loss_count}")
elif(win_count != 0 and loss_count == 0):
    print(f"Wins: {win_count}\nLosses: {loss_count}\nZeros: {zero_count}\nWin Avg: {win_sum/win_count}\nLoss Avg: N/A")
else:
    print(f"Wins: {win_count}\nLosses: {loss_count}\nZeros: {zero_count}\nWin Avg: N/A\nLoss Avg: {loss_sum/loss_count}")

print(f"Number of ideal stocks: {ideal_stock}")