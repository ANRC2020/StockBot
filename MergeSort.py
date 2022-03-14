def MergeSort(arr, max, min):
    if max - min == 0:
        #print(f"max: {max}")
        sorted = []
        sorted.append(arr[max])
        return sorted
    
    mid = int((max + min)/2)
    # print(f"Left: ({min},{mid})")
    Left = MergeSort(arr,mid,min)

    # print(f"Left Content:")
    # for i in range(len(Left)):
    #     print(Left[i])
    # print("--------------------")

    # print(f"right: ({mid + 1},{max})")
    Right = MergeSort(arr,max, mid + 1)

    # print(f"Right Content:")
    # for i in range(len(Right)):
    #     print(Right[i])
    # print("--------------------")

    sorted = []
    l = 0
    r = 0

    # print(f"cap_l = {len(Left)}\ncap_r = {len(Right)}")
    # print(f"(max - min) = {max - min}")

    for i in range(max - min + 1):

        if l == len(Left):
            sorted.append(Right[r])
            r += 1
            continue
        if r == len(Right):
            sorted.append(Left[l])
            l += 1
            continue
        if Left[l] <= Right[r]:
            sorted.append(Left[l])
            l += 1
        else:
            sorted.append(Right[r])
            r += 1

    return sorted
#-------------------------------------------------
size = int(input("Enter number of inputs: "))
arr = []

for i in range(size):
    arr.append(int(input("Enter a number: ")))

sorted = MergeSort(arr, size - 1, 0)

for i in range(size):
    print(sorted[i]) 