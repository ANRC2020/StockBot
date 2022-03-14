import csv
from csv import DictWriter, writer, reader

def AddLine():
    print("Entered AddLine")
    
    file = open("WordBank.csv")
    numlines = sum(1 for row in file)

    writer = csv.writer(file)
    reader = csv.reader(file)

    # curr_line = next(reader)

    for row in file:
        writer.writerow(curr_line)
        curr_line = next(reader)

    add = True
    while(add == True):
        EnglishWord = str(input("What word do you want to add? "))
        KoreanWord = str(input(f"What is the Korean equivalent to '{EnglishWord}'? "))
        Pronounce = str(input(f"How do you pronounce {KoreanWord}? ")) 

        print(f"You are about to add the following line:\n{EnglishWord} {KoreanWord} {Pronounce}")
        tof = input("Enter 't' to confirm, else enter 'f' to cancel")

        if(tof == 't'):
            row = [EnglishWord,KoreanWord,Pronounce]
            writer.writerow(row)
        else:
            print("Canceled add order")

        x = str(input("Do you want to add more words? (t:f) "))   

        if(x == 't'):
            add = True
        else:
            add = False

    csv.close()

def RemoveLine():
    print("Entered RemoveLine")



def DisplayContent():
    print("Entered Display Content")

def Quiz():
    print("Entered Quiz")

def Main():
    choice = int(input("[1] Jeongbo chuga [2] Jeongbo jegeo [3] Jeongbo pyosi [4] Kwijeu: "))
    Execute(choice)

def Execute(choice):
    if(choice == 1):
        AddLine()
    elif(choice == 2):
        RemoveLine()
    elif(choice == 3):
        DisplayContent()
    elif(choice == 4):
        Quiz()
    else:
        print("Jalmosdoen iblyeog")

#----------------------------------------------------------------------------
#---------------------------Beginning of the Code----------------------------
#----------------------------------------------------------------------------

print('Annyeonghaseyo!')

while(True):
    print('\nMwohago sip-eo?')
    Main()

    
    