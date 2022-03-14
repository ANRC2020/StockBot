arr = []

while(True):
    arr.append(int(input("Enter a number: ")))

    if(len(arr) > 4):
        arr.pop(0)

    print("Content of the list:")

    for i in range(len(arr)):
        print(arr[i])

    yon = input("Continue? ")

    if yon == 'n' or yon == 'N':
        break
    