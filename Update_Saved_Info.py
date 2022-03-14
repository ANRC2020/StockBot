import csv
from csv import DictWriter, writer, reader

def update(symbol):
    with open('Saved_Info_Initial.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['symbol','quantity','capital','sold','bought','bought_price']
        writer.writerow(header)
        for stock in symbol:
            row = [stock,'0','10000','1','0','0']
            writer.writerow(row)
        file.close()