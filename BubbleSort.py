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
size = int(input('Enter number of numbers: '))
array = []

for i in range(size):
    array.append(int(input('Enter a number: ')))

sorted = BubbleSort(array, size)

for i in range(size):
    print(sorted[i])