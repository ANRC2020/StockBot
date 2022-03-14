import csv

def get_close(stock, csv_reader):
    #Get current and previous close data
    i = 0
    for row in csv_reader:
        if(i == stock.PSARcounter):
            stock.PSARMatrix[1][0] = float(row[1]) #set High
            stock.PSARMatrix[1][1] = float(row[2]) #set Low
            stock.PSARMatrixlong[1][0] = float(row[1]) #set High
            stock.PSARMatrixlong[1][1] = float(row[2]) #set Low
            stock.t.append(stock.PSARcounter) #Save times
            stock.close.append(float(row[3])) #Save close prices
            stock.open.append(float(row[0])) #Save open prices
            stock.high.append(float(row[1])) #Save high prices
            stock.low.append(float(row[2])) #Save low prices
            stock.buyindicator.append(None)
            stock.soldindicator.append(None)
            curr_time = str(row[6])

                    
        if(i == stock.setcounter): #Get current point's data
            close1 = float(row[3])
            print(close1)
            break
        elif(i == stock.setcounter - 1): #Get previous point's data
            close0 = float(row[3])
            print(close0)

        i += 1
        
    return close0, close1