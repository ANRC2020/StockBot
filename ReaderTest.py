from csv import reader

setcounter = 10 # 2 gets the first two non-string values and 10 gets the last two inputs in a file containing 10 min of data in 1 min intervals 

with open('TestDataSet.csv', 'r') as read_obj:
        
#     csv_reader = reader(read_obj)
    
#     i = 0
#     close1 = ''
#     close0 = ''

#     for row in csv_reader:
#         if(i % 2 == 0):
#             if(i/2 == setcounter): #Get current point's data
#                 close1 = (row[3])
#                 break
#             elif(i/2 == setcounter - 1): #Get previous point's data
#                 close0 = (row[3])
#         i += 1

# print(close0)
# print(close1)

    csv_reader = reader(read_obj)
    
    i = 0
    arr = []
    for row in csv_reader:
        if(i % 2 == 0 and i > 1):
            if(i < 22):
                arr.append(row[3])
        i += 1
                

print(arr)
#-----------------------------------------------------
slope = []

for j in range(len(arr)-1):
    slope.append(((float(arr[j + 1]) - float(arr[j]))/float(arr[j]))*100)

print(slope)