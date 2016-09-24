
def calcReg(regVal):
    reg0=4
    reg1=1
    reg7=regVal
    prgStack=[99999]
    if reg0==3:
        prgStack.append(3)
    elif reg0==4:
        prgStack.append(4)
        for i in range(0,reg7):
            prgStack.append(3)
    reg1=(((reg7+1)*reg7)+ (2*reg7) +1) %32768        

    while True:
        poppedNum=prgStack.pop()
        if poppedNum == 99999:
            break;
        elif poppedNum==3:
            reg1= (((reg7+1)*reg1) + ((2*reg7)+1)) % 32768
        elif poppedNum==4:
            for i in range(0,reg1):
                prgStack.append(3)
            reg1=(((reg7+1)*reg7)+ (2*reg7) +1) %32768
    if reg1==5:
        print("reg1: ", reg1 , ", reg7: ",reg7, "\n")



for regVal in range (0,32767):
    calcReg(regVal)
    if regVal %100 ==0:
        print("passed reg7 of ",regVal)
calcReg(29127)