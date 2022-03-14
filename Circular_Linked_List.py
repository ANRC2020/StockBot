class link:
    value = 0

    def makelink(self, input):
        self.value = input
#----------------------------------------------------
def circularLinkedList(array, size):
    obj = []

    for i in range(size):
        obj.append(link())
        obj[i].value = array[i]

    return obj
#----------------------------------------------------
size = int(input('Enter the number of links: '))
array = []

for i in range(size):
    array.append(input("Enter number: "))

obj = circularLinkedList(array, size)

for i in range(size):
    print(obj[i].value)