from Filter import setstocks
import csv
from csv import reader, writer
import time
from time import sleep

pass_list = []
fail_list = []

i = 1
with open('StockFilterDataBase.csv', 'r') as file:
# with open('PassStocks.csv', 'r') as file:
    reader = csv.reader(file)
    
    for row in reader:
        try:
            row = str(row[0])
        except:
            continue
        
        if(setstocks(row) == True):
            pass_list.append(str(row))
        else:
            fail_list.append(str(row))
        i += 1

        if(i % 100 == 0):
            time.sleep(5)

    file.close()

with open('PassStocks.csv', 'w', newline="") as file:
    writer = csv.writer(file)

    for i in range(len(pass_list)):
        writer.writerow([pass_list[i]])
    
    file.close()

with open('FailStocks.csv', 'w', newline='') as file:
    writer = csv.writer(file)

    for i in range(len(fail_list)):
        writer.writerow([fail_list[i]])
    
    file.close()

print(f"{len(pass_list)} pass stocks")
print(f"{len(fail_list)} fail stocks")