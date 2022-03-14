def slope(stock,close1,close0):
    stock.changes.append(((close1 - close0)/close0)*100)
