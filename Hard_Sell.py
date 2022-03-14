from Sell import sell

def hard_sell(stock, curr_time):

    if(stock.bought == True and stock.sold == False):
        itt = 3

        if(len(stock.close) >= 2):
            if(stock.low[-1] < stock.low[-2]):    
                high_pred = []
                low_ped = []
                curr_high = stock.high[-1]
                curr_low = stock.low[-1]
                low_change = stock.low[-1] - stock.low[-2]
                high_change = stock.high[-1] - stock.high[-2]

                for i in range(itt):
                    high_pred.append(curr_high + high_change)
                    low_ped.append(curr_low + low_change)

                    curr_high = curr_high + high_change
                    curr_low = curr_low + low_change

                localPSARMatrix = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
                localPSARMatrix[0] = stock.PSARMatrix[0]

                arr = []

                for i in range(itt):
                    arr.append(localPSARMatrix[0][2])

                    localPSARMatrix[1][0] = high_pred[i]
                    localPSARMatrix[1][1] = low_ped[i]

                    if(localPSARMatrix[0][7] == 1 and localPSARMatrix[0][2] + localPSARMatrix[0][6] > localPSARMatrix[1][1]):
                        localPSARMatrix[1][2] = localPSARMatrix[0][3]
                    else:
                        if(localPSARMatrix[0][7] == 0 and localPSARMatrix[0][2] + localPSARMatrix[0][6] < localPSARMatrix[1][0]):
                            localPSARMatrix[1][2] = localPSARMatrix[0][3]
                        else:
                            localPSARMatrix[1][2] = localPSARMatrix[0][2] + localPSARMatrix[0][6]
                    #PSAR Update END

                    # print(f"PSAR Value: {localPSARMatrix[1][2]}")

                    #BULLBEAR Update START
                    if(localPSARMatrix[1][2] < localPSARMatrix[1][0]):
                        localPSARMatrix[1][7] = 1
                    else:
                        if(localPSARMatrix[1][2] > localPSARMatrix[1][1]):
                            localPSARMatrix[1][7] = 0
                    #BULLBEAR Update END

                    # print(f"BULLBEAR Value: {localPSARMatrix[1][7]}")

                    #EP Update START
                    if(localPSARMatrix[1][7] == 1 and localPSARMatrix[1][0] > localPSARMatrix[0][3]):
                        localPSARMatrix[1][3] = localPSARMatrix[1][0]
                    else:
                        if(localPSARMatrix[1][7] == 1 and localPSARMatrix[1][0] <= localPSARMatrix[0][3]):
                            localPSARMatrix[1][3] = localPSARMatrix[0][3]
                        else:
                            if(localPSARMatrix[1][7] == 0 and localPSARMatrix[1][1] < localPSARMatrix[0][3]):
                                localPSARMatrix[1][3] = localPSARMatrix[1][1]
                            else:
                                if(localPSARMatrix[1][7] == 0 and localPSARMatrix[1][1] >= localPSARMatrix[0][3]):
                                    localPSARMatrix[1][3] = localPSARMatrix[0][3]

                    #EP Update END

                    # print(f"EP Value: {localPSARMatrix[1][3]}")

                    #AF Update START
                    if(localPSARMatrix[0][7] == localPSARMatrix[1][7]):
                        localPSARMatrix[1][5] = localPSARMatrix[0][5]
                        if(localPSARMatrix[1][7] == 1 and localPSARMatrix[1][3] > localPSARMatrix[0][3]):
                            if(localPSARMatrix[1][5] < stock.AF_limit):
                                localPSARMatrix[1][5] = localPSARMatrix[1][5] + stock.AF_increment
                        if(localPSARMatrix[1][7] == 0 and localPSARMatrix[1][3] < localPSARMatrix[0][3]):
                            if(localPSARMatrix[1][5] < stock.AF_limit):
                                localPSARMatrix[1][5] = localPSARMatrix[1][5] + stock.AF_increment
                    else:
                        localPSARMatrix[1][5] = stock.AF_increment
                    #AF Update END

                    # print(f"AF Value: {localPSARMatrix[1][5]}")

                    localPSARMatrix[1][4] = localPSARMatrix[1][3] - localPSARMatrix[1][2] #set EP - PSAR
                    localPSARMatrix[1][6] = localPSARMatrix[1][4] * localPSARMatrix[1][5] #set (EP - PSAR)*AF

                    # print(f"EP - PSAR Value: {localPSARMatrix[1][4]}")
                    # print(f"(EP - PSAR)*AF Value: {localPSARMatrix[1][6]}")

                    #Setup for next iteration
                    localPSARMatrix[0] = localPSARMatrix[1]
                    localPSARMatrix[1] = [0,0,0,0,0,0,0,0]
                
                if(localPSARMatrix[0][7] == 0):
                    
                    sell(stock,curr_time)

                # plt.plot(stock.t[-5:], arr, 'kx', stock.t[26:], stock.histLongPSAR[26:], 'xc', stock.t[26:], stock.histShortPSAR[26:], 'xm')
                # plt.title("4 point PSAR Prediction")
                # plt.show()

                    stock.hard_sell = True
                else:
                    stock.hard_sell = False    
