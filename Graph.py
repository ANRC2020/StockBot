import matplotlib.pyplot as plt

def graph(stock, stocks_list):
    y = input("Enter 'y' for graphs: ")
    if(y == 'y' or y =='Y'):
        y = input()
        if(y):
            for stock in stocks_list:
                mng = plt.get_current_fig_manager()
                mng.frame.Maximize(True)
                figure, axis = plt.subplots(1, 3)
                figure.set_figwidth(17)

                axis[0].plot(stock.t[50:], stock.close[50:], 'k', stock.t[50:],stock.EMA_12_arr[50:], 'r', stock.t[50:], stock.EMA_26_arr[50:], 'b', stock.t[50:], stock.buyindicator[50:], 'og', stock.t[50:], stock.soldindicator[50:], 'or', stock.t[50:], stock.histLongPSAR[50:], 'xc', stock.t[50:], stock.histShortPSAR[50:], 'xm')
                axis[0].set_title(stock.Ticker + ' EMA_12 and EMA_26')

                axis[1].plot(stock.t[50:], stock.MACD_val[50:], 'm',stock.t[50:], stock.MACD9_arr[50:], 'g')
                axis[1].set_title(stock.Ticker + ' MACD and Signal')

                axis[2].plot(stock.t, stock.RSI, 'm', stock.t, [70]*len(stock.t), 'b', stock.t, [30]*len(stock.t), 'b')
                axis[2].set_title(stock.Ticker + ' RSI')
                plt.show()