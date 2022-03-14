from Top15Filter import setstocks
import csv
from csv import reader, writer

results = []

with open('PreviousTopWinners.csv', 'r') as file:
    reader = csv.reader(file)
    
    for row in reader:
        try:
            row = str(row[0])
        except:
            continue
        
        results.append(setstocks(row))

    file.close()

print(results)