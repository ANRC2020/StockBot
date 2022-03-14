# C6H6 Benzene, H20 Water

C = 0
H = 0
O = 0
search = 1

while search == 1:

    C = int(input('# of C: '))
    H = int(input('# of H: '))
    O = int(input('# of O: '))

    if C == 6 and H == 6 and O == 0:
        print("Molecule Found: BENZENE")
    elif C == 0 and H == 2 and O == 1:
        print("Molecule Found: WATER")
    else:
        print("Molecule Not Found")

    search = int(input("Continue? "))

    