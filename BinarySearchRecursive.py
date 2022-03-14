def BubbleSort(arr, n):
    # 3,6,5,8,1
    for j in range(n - 1):
        for i in range(n - 1):
            current = arr[i]
            
            if current >= arr[i + 1]:
                temp = arr[i + 1]
                arr[i + 1] = current
                arr[i] = temp
    
    return arr
#---------------------------------------------
def binarysearch(arr, size, high, low, key, tof):
   # print(f"High: {high}, low: {low}")
    mid = int((high + low)/2)
   # print(f"Mid: {mid}")

    if key < arr[low] or key > arr[high]:
        tof = [0, 0]
        return tof
    #3,6,7,9,12 key = 9

    if high - low == 1:
        if key == arr[high]:
            mid = high
        elif key == arr[low]:
            mid = low
        else:
            tof = [0, 0]
            return tof

    if key == arr[mid]:
        tof = [1, mid]
        return tof
    elif key < arr[mid]:
        high = mid
        return binarysearch(arr, size, high, low, key, tof)
    else:
        low = mid 
        return binarysearch(arr, size, high, low, key, tof)


#---------------------------------------------
size = int(input('Enter number of inputs: '))
arr = []

for i in range(size):
    arr.append(int(input('Enter a number: ')))

key = int(input('Enter search key: '))

arr = BubbleSort(arr, size)
#tof = [true/flase, index]
tof = binarysearch(arr, size, size - 1, 0, key, [0,0])

if tof[0] == 1:
    print(f"Search key was found at index {tof[1]}")
else:
    print("Search key not found")