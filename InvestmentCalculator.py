initial = 5000
percent_change = 1.20
profit = initial
#--------------------------------------------------
print(profit)
for i in range(1,53):
    profit = (profit * percent_change)
    # percent_change += percent_change*(1.00000000001)
    print(profit)
#--------------------------------------------------
print(f"After 1 year, the net profit is: {profit}")
print(f"Percent Increase: {((profit - initial)/(initial))*100}")
#--------------------------------------------------