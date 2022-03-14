import csv

def save_info(stocks_list, netcapital, netsectionval, bestsectionval,timeframe,increment,IPstr):

    with open('ActivityLog.txt', 'w', newline='') as file:
        # writer = csv.writer(file)

        dash = '----------------------------------------' # 40 dashes

        file.write(dash + "Section Stats" + dash[0:- len('Section Stats')] + dash[0:12] +"\n")
        file.write('Period: ' + timeframe + '                             Interval: ' + increment + '                        Delay Period: ' + IPstr + '\n')
        file.write("Net Capital: " + str(netcapital) + '\n')
        file.write("Net Section Value: " + str(netsectionval) + '\n')
        file.write("Net Percent Change: " + str(((netsectionval - netcapital)/netcapital)*100) + '\n')
        file.write("Best Section Value: " + str(bestsectionval) + '\n')
        file.write("Best Percent Value: " + str(((bestsectionval - netcapital)/netcapital)*100) + '\n')

        for stock in stocks_list:
            file.write(dash + stock.Ticker + dash[0:- len(stock.Ticker)] + dash[0:12] + "\n")
            file.write('Ticker: ' + stock.Ticker + '              Period: ' + timeframe + '              Interval: ' + increment + '              Delay Period: ' + IPstr + '\n')
            file.write('Principle: ' + str(stock.principle) + '                                Ending Capital: ' + str(stock.capital) + '\n')
            if(stock.section_val >= stock.principle):
                file.write('Final Percent Profit: ' + str( ((stock.section_val - stock.principle)/(stock.principle)) * 100  ) + '\n')
            else:
                file.write('Final Percent Loss: ' + str( ((stock.section_val - stock.principle)/(stock.principle)) * 100  ) + '\n')


            file.write('Profit Log: ' + str(stock.profitlog) + '\n')

            file.write('Best Percent Profit: ' + str(((stock.bestprofit - stock.principle)/stock.principle) * 100) + '\n')    
            
            if(len(stock.sell_log) > 0):
                file.write('Number of Trades Closed: ' + str(len(stock.sell_log)) + '  Average Profit Per Trade: ' + str((stock.section_val - stock.principle)/len(stock.sell_log)) + '\n')        
            else:
                file.write('Number of Trades Closed: ' + str(len(stock.sell_log)) + '  Average Profit Per Trade: ' + 'N/A\n') 

            num_win = 0
            amount_won = 0
            num_loss = 0
            amount_lost = 0
            avg_win = 0
            avg_loss = 0

            for i in range(len(stock.sell_log)):
                if(stock.buy_log[i][0] <= stock.sell_log[i][0]):
                    num_win += 1
                    amount_won += (stock.sell_log[i][0] - stock.buy_log[i][0])
                else:
                    num_loss += 1 
                    amount_lost += (stock.buy_log[i][0] - stock.sell_log[i][0])

            if(num_win > 0):
                avg_win = amount_won/num_win
                file.write('# of Winning Trades: ' + str(num_win) + '      Average Profit Per Winning Trade Per Stock: ' + str(avg_win) + '\n')
            else:
                file.write('# of Winning Trades: ' + str(num_win) + '      Average Profit Per Winning Trade Per Stock: ' + 'N/A\n')

            if(num_loss > 0):
                avg_loss = amount_lost/num_loss
                file.write('# of Losing Trades: ' + str(num_loss) + '       Average Profit Per Losing Trade Per Stock: ' + str(avg_loss) + '\n')
            else:
                file.write('# of Losing Trades: ' + str(num_loss) + '       Average Profit Per Losing Trade Per Stock: ' + 'N/A\n')

            if(avg_win > 0 and avg_loss > 0):
                file.write('Profit-Loss Trade Ratio: ' + str(avg_win/avg_loss) + '\n')
            else:
                file.write('Profit-Loss Trade Ratio: ' + 'N/A\n')
            
            if(stock.hard_sell == True):
                file.write("Hard-Sell Limit: " +  str(stock.hard_sell_limit) + "     " + "Hard-Sell Triggered: " + str(stock.hard_sell) + "       " + "Hard-Sell Time: " + str(stock.hard_sell_time) + '\n')
            else:
                file.write("Hard-Sell Limit: " +  str(stock.hard_sell_limit) + "     " + "Hard-Sell Triggered: " + str(stock.hard_sell) + '\n')

            file.write("Buys:" + "                      Prices:" + "             Sells:" + "                     Prices:\n")

            for i in range(len(stock.buy_log)):
                file.write(str(stock.buy_log[i][1]) + "  " + str(stock.buy_log[i][0]) + "  " + str(stock.sell_log[i][1]) + "  " + str(stock.sell_log[i][0]) + '\n')

        file.write(dash + 'End of File' +  dash[0: - len('End of File')] + dash[0:12]+ "\n")
        file.close()

def update_mass_stocks(stock, IP, netsectionval, netcapital):
    with open('MassTesterResults.txt','a') as file:
        row = [stock.Ticker,((stock.close[-1] - stock.close[IP] )/stock.close[IP])*100, (((netsectionval - netcapital)/netcapital)*100)]
        file.write(str(row))

