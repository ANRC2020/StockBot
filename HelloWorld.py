#Abbas Siddiqui
#4/24/2021

#print("Hello World!")
#print("My name is Abbas Siddiqui.")

#name = input("What is your name?")
#print("Hello %s, welcome to ya mama's house boi!" %name)

#print("Yo mama's hungry, she needs you to grab some stuff from the store.")
#num_items = int(input("How many things does she need? "))

#store_list = []
#for i in range(0, num_items):
#    item = input("Enter an item: ")
#    store_list.append(item)

#print("Here's your list: ")
#print(store_list)

#27290 -> [2,7,2,9,0]

def GetIndexValue(array, index):
    print(array(index))


size = int(input("Enter Number of Inputs: "))

array  = []
for i in range(0, size):
    array.append(int(input("Enter a value: ")))

index = int(input("What index do you want to check? "))

GetIndexValue(array, index)