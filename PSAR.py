def short_term_PSAR(stock, IL):
    #PSAR Implementation (Short Term)
    if(IL == 1):
        # print("Entered PSAR initialization\n")
        # print(f"High Value: {stock.PSARMatrix[1][0]}")
        # print(f"Low Value: {stock.PSARMatrix[1][1]}")
        stock.PSARMatrix[1][2] = stock.PSARMatrix[1][1] #set PSAR
        # print(f"PSAR Value: {stock.PSARMatrix[1][2]}")
        stock.PSARMatrix[1][3] = stock.PSARMatrix[1][0] #set EP
        # print(f"EP Value: {stock.PSARMatrix[1][3]}")
        stock.PSARMatrix[1][4] = stock.PSARMatrix[1][3] - stock.PSARMatrix[1][2] #set EP - PSAR
        # print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        stock.PSARMatrix[1][5] = stock.AF_increment #set AF
        # print(f"AF Value: {stock.PSARMatrix[1][5]}")
        stock.PSARMatrix[1][6] = stock.PSARMatrix[1][4] * stock.PSARMatrix[1][5] #set (EP - PSAR)*AF
        # print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")
        stock.PSARMatrix[1][7] = 1 #set BULLBEAR
        # print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")
    else:
    
        # print("Entered PSAR Solve")
        # print(f"High Value: {stock.PSARMatrix[1][0]}")
        # print(f"Low Value: {stock.PSARMatrix[1][1]}")

        #PSAR Update START
        if(stock.PSARMatrix[0][7] == 1 and stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6] > stock.PSARMatrix[1][1]):
            stock.PSARMatrix[1][2] = stock.PSARMatrix[0][3]
        else:
            if(stock.PSARMatrix[0][7] == 0 and stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6] < stock.PSARMatrix[1][0]):
                stock.PSARMatrix[1][2] = stock.PSARMatrix[0][3]
            else:
                stock.PSARMatrix[1][2] = stock.PSARMatrix[0][2] + stock.PSARMatrix[0][6]
        #PSAR Update END

        # print(f"PSAR Value: {stock.PSARMatrix[1][2]}")

        #BULLBEAR Update START
        if(stock.PSARMatrix[1][2] < stock.PSARMatrix[1][0]):
            stock.PSARMatrix[1][7] = 1
        else:
            if(stock.PSARMatrix[1][2] > stock.PSARMatrix[1][1]):
                stock.PSARMatrix[1][7] = 0
        #BULLBEAR Update END

        # print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")

        #EP Update START
        if(stock.PSARMatrix[1][7] == 1 and stock.PSARMatrix[1][0] > stock.PSARMatrix[0][3]):
            stock.PSARMatrix[1][3] = stock.PSARMatrix[1][0]
        else:
            if(stock.PSARMatrix[1][7] == 1 and stock.PSARMatrix[1][0] <= stock.PSARMatrix[0][3]):
                stock.PSARMatrix[1][3] = stock.PSARMatrix[0][3]
            else:
                if(stock.PSARMatrix[1][7] == 0 and stock.PSARMatrix[1][1] < stock.PSARMatrix[0][3]):
                    stock.PSARMatrix[1][3] = stock.PSARMatrix[1][1]
                else:
                    if(stock.PSARMatrix[1][7] == 0 and stock.PSARMatrix[1][1] >= stock.PSARMatrix[0][3]):
                        stock.PSARMatrix[1][3] = stock.PSARMatrix[0][3]

        #EP Update END

        # print(f"EP Value: {stock.PSARMatrix[1][3]}")

        #AF Update START
        if(stock.PSARMatrix[0][7] == stock.PSARMatrix[1][7]):
            stock.PSARMatrix[1][5] = stock.PSARMatrix[0][5]
            if(stock.PSARMatrix[1][7] == 1 and stock.PSARMatrix[1][3] > stock.PSARMatrix[0][3]):
                if(stock.PSARMatrix[1][5] < stock.AF_limit):
                    stock.PSARMatrix[1][5] = stock.PSARMatrix[1][5] + stock.AF_increment
            if(stock.PSARMatrix[1][7] == 0 and stock.PSARMatrix[1][3] < stock.PSARMatrix[0][3]):
                if(stock.PSARMatrix[1][5] < stock.AF_limit):
                    stock.PSARMatrix[1][5] = stock.PSARMatrix[1][5] + stock.AF_increment
        else:
            stock.PSARMatrix[1][5] = stock.AF_increment
        #AF Update END

        # print(f"AF Value: {stock.PSARMatrix[1][5]}")

        stock.PSARMatrix[1][4] = stock.PSARMatrix[1][3] - stock.PSARMatrix[1][2] #set EP - PSAR
        stock.PSARMatrix[1][6] = stock.PSARMatrix[1][4] * stock.PSARMatrix[1][5] #set (EP - PSAR)*AF

        # print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        # print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")

    #Setup for next iteration
    stock.PSARMatrix[0] = stock.PSARMatrix[1]
    stock.PSARMatrix[1] = [0,0,0,0,0,0,0,0]

def long_term_PSAR(stock, IL):
    #PSAR Implementation (Long Term)
    if(IL == 1):
        # print("Entered PSAR initialization\n")
        # print(f"High Value: {stock.PSARMatrix[1][0]}")
        # print(f"Low Value: {stock.PSARMatrix[1][1]}")
        stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[1][1] #set PSAR
        # print(f"PSAR Value: {stock.PSARMatrix[1][2]}")
        stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[1][0] #set EP
        # print(f"EP Value: {stock.PSARMatrix[1][3]}")
        stock.PSARMatrixlong[1][4] = stock.PSARMatrixlong[1][3] - stock.PSARMatrixlong[1][2] #set EP - PSAR
        # print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        stock.PSARMatrixlong[1][5] = stock.AF_incrementlong #set AF
        # print(f"AF Value: {stock.PSARMatrix[1][5]}")
        stock.PSARMatrixlong[1][6] = stock.PSARMatrixlong[1][4] * stock.PSARMatrixlong[1][5] #set (EP - PSAR)*AF
        # print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")
        stock.PSARMatrixlong[1][7] = 1 #set BULLBEAR
        # print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")

    if(IL != 1 and stock.counter % 2 == 0):
        # print("Entered PSAR Solve")
        # print(f"High Value: {stock.PSARMatrix[1][0]}")
        # print(f"Low Value: {stock.PSARMatrix[1][1]}")

        #PSAR Update START
        if(stock.PSARMatrixlong[0][7] == 1 and stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6] > stock.PSARMatrixlong[1][1]):
            stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][3]
        else:
            if(stock.PSARMatrixlong[0][7] == 0 and stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6] < stock.PSARMatrixlong[1][0]):
                stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][3]
            else:
                stock.PSARMatrixlong[1][2] = stock.PSARMatrixlong[0][2] + stock.PSARMatrixlong[0][6]
        #PSAR Update END

        # print(f"PSAR Value: {stock.PSARMatrix[1][2]}")

        #BULLBEAR Update START
        if(stock.PSARMatrixlong[1][2] < stock.PSARMatrixlong[1][0]):
            stock.PSARMatrixlong[1][7] = 1
        else:
            if(stock.PSARMatrixlong[1][2] > stock.PSARMatrixlong[1][1]):
                stock.PSARMatrixlong[1][7] = 0
        #BULLBEAR Update END

        # print(f"BULLBEAR Value: {stock.PSARMatrix[1][7]}")

        #EP Update START
        if(stock.PSARMatrixlong[1][7] == 1 and stock.PSARMatrixlong[1][0] > stock.PSARMatrixlong[0][3]):
            stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[1][0]
        else:
            if(stock.PSARMatrixlong[1][7] == 1 and stock.PSARMatrixlong[1][0] <= stock.PSARMatrixlong[0][3]):
                stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[0][3]
            else:
                if(stock.PSARMatrixlong[1][7] == 0 and stock.PSARMatrixlong[1][1] < stock.PSARMatrixlong[0][3]):
                    stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[1][1]
                else:
                    if(stock.PSARMatrixlong[1][7] == 0 and stock.PSARMatrixlong[1][1] >= stock.PSARMatrixlong[0][3]):
                        stock.PSARMatrixlong[1][3] = stock.PSARMatrixlong[0][3]

        #EP Update END

        # print(f"EP Value: {stock.PSARMatrix[1][3]}")

        #AF Update START
        if(stock.PSARMatrixlong[0][7] == stock.PSARMatrixlong[1][7]):
            stock.PSARMatrixlong[1][5] = stock.PSARMatrixlong[0][5]
            if(stock.PSARMatrixlong[1][7] == 1 and stock.PSARMatrixlong[1][3] > stock.PSARMatrixlong[0][3]):
                if(stock.PSARMatrixlong[1][5] < stock.AF_limitlong):
                    stock.PSARMatrixlong[1][5] = stock.PSARMatrixlong[1][5] + stock.AF_incrementlong
            if(stock.PSARMatrixlong[1][7] == 0 and stock.PSARMatrixlong[1][3] < stock.PSARMatrixlong[0][3]):
                if(stock.PSARMatrixlong[1][5] < stock.AF_limitlong):
                    stock.PSARMatrixlong[1][5] = stock.PSARMatrixlong[1][5] + stock.AF_incrementlong
        else:
            stock.PSARMatrixlong[1][5] = stock.AF_incrementlong
        #AF Update END

        # print(f"AF Value: {stock.PSARMatrix[1][5]}")

        stock.PSARMatrixlong[1][4] = stock.PSARMatrixlong[1][3] - stock.PSARMatrixlong[1][2] #set EP - PSAR
        stock.PSARMatrixlong[1][6] = stock.PSARMatrixlong[1][4] * stock.PSARMatrixlong[1][5] #set (EP - PSAR)*AF

        # print(f"EP - PSAR Value: {stock.PSARMatrix[1][4]}")
        # print(f"(EP - PSAR)*AF Value: {stock.PSARMatrix[1][6]}")

    if(IL == 1 or stock.counter % 2 == 0):
        #Setup for next iteration
        stock.PSARMatrixlong[0] = stock.PSARMatrixlong[1]
        stock.PSARMatrixlong[1] = [0,0,0,0,0,0,0,0]

    #Update Historical PSAR Arrays
    stock.histShortPSAR.append(stock.PSARMatrix[0][2])
    stock.histLongPSAR.append(stock.PSARMatrixlong[0][2])
