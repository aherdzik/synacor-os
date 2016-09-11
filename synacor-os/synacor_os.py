import os
import sys
import struct
try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter 
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
import time

cursor=0
currentProgram = []
register = [-1,-1,-1,-1,-1,-1,-1,-1]
prgStack = []
stringVal= ["halt", "set", "push", "pop", "eq", "gt", "jmp", "jt", "jf", "add", "mult", "mod", "and", "or", "not", "rmem", "wmem", "call", "ret", "out", "in", "noop"]
cmdLengths=[1,3,2,2,4,4,2,3,3,4,4,4,4,4,3,3,3,2,2,2,2,1]
curInput = []
handlingInput= False
inputText = []
master = []
maxSize = []
registerInputs = []
e1=[]
stateName=[]
stackText=[]
cursorText=[]
stepUIUpdate= []
UIUpdate= []
stepUpdateChecked =[]
waitingForStep=False
stepCheckBox= []
loadStateFlag= False
saveStateFlag= False

def handleCommand(currentCommand):
    global cursor, inputText,saveStateFlag, loadStateFlag
    cursor= cursor+1
    if currentCommand == 0: # stop program
        printToScreen("program halted at command " + str(cursor-1))
        input()
        sys.exit()
    elif currentCommand == 1: # set a to value of b
        regNum= currentProgram[cursor]-32768
        cursor=cursor+1
        register[regNum]=getValue(cursor)

    elif currentCommand == 2: # push a onto stack
        prgStack.append(getValue(cursor))

    elif currentCommand == 3: # remove element on stack and write to a, otherwise error
        if len(prgStack) ==0 :
            printToScreen( "ERROR STACK POPPED WHILE EMPTY")
        else:
            register[currentProgram[cursor]-32768] = prgStack.pop()

    elif currentCommand == 4: #set a to 1 if b is equal to c, otherwise 0
        regNum= currentProgram[cursor]-32768
        cursor= cursor+1
        val1= getValue(cursor)
        cursor=cursor+1
        val2= getValue(cursor)
        if val1 == val2:
            register[regNum]=1
        else:
            register[regNum]=0
            
    elif currentCommand ==5:#set a to 1 if b is greater than c, otherwise 0
        regNum= currentProgram[cursor]-32768
        cursor= cursor+1
        val1= getValue(cursor)
        cursor=cursor+1
        val2= getValue(cursor)
        if val1 > val2:
            register[regNum]=1
        else:
            register[regNum]=0

    elif currentCommand == 6: #jump to <a>
        cursor= getValue(cursor)-1

    elif currentCommand == 7: #7 a b, if <a> is nonzero jump to b
        jumpIfNonZero = getValue(cursor)
        cursor= cursor+1
        if jumpIfNonZero !=0:
            cursor=getValue(cursor)-1

    elif currentCommand == 8: #8 a b, if <a> is zero jump to b
        jumpIfZero = getValue(cursor)
        cursor= cursor+1
        if jumpIfZero ==0:
            cursor=getValue(cursor)-1

    elif currentCommand == 9: #assign to a the sum of b and c, mod 32768
        targetReg= currentProgram[cursor]-32768
        cursor=cursor+1
        val1= getValue(cursor)
        cursor=cursor+1
        val2= getValue(cursor)
        register[targetReg]=(val1 + val2) % 32768

    elif currentCommand == 10: #assign to a the product of b and c, mod 32768
        targetReg= currentProgram[cursor]-32768
        cursor=cursor+1
        val1= getValue(cursor)
        cursor=cursor+1
        val2= getValue(cursor)
        register[targetReg]=(val1 * val2) % 32768

    elif currentCommand == 11:#assign to a themod of b and c, mod 32768
        targetReg= currentProgram[cursor]-32768
        cursor=cursor+1
        val1= getValue(cursor)
        cursor=cursor+1
        val2= getValue(cursor)
        register[targetReg]=(val1 % val2) % 32768

    elif currentCommand ==12: # store into a the bitwise 'and' of b and c
        targetReg= currentProgram[cursor]-32768
        cursor=cursor+1
        val1= getValue(cursor)
        cursor=cursor+1
        val2= getValue(cursor)
        register[targetReg]=(val1 & val2) % 32768

    elif currentCommand ==13: # store into a the bitwise 'or' of b and c
        targetReg= currentProgram[cursor]-32768
        cursor=cursor+1
        val1= getValue(cursor)
        cursor=cursor+1
        val2= getValue(cursor)
        register[targetReg]=(val1 | val2) % 32768

    elif currentCommand ==14: # stores bitwise inverse of <b> in <a>
        targetReg= currentProgram[cursor]-32768
        cursor=cursor+1
        val1= getValue(cursor)
        register[targetReg]=32767-val1

    elif currentCommand ==15: # read memory at b, write to a
        targetReg= currentProgram[cursor]-32768
        cursor=cursor+1
        val1= getValue(cursor)
        register[targetReg]=currentProgram[val1]

    elif currentCommand == 16: #write memory from address b into address a
        targetReg= getValue(cursor)
        cursor=cursor+1
        writeVal = getValue(cursor)
        currentProgram[targetReg]=writeVal

    elif currentCommand ==17: #write value of next instruction to stack, jump to a
        goto= getValue(cursor)
        prgStack.append(cursor+1)
        cursor= goto-1

    elif currentCommand == 18:
        if len(prgStack) ==0 :
            printToScreen( "ERROR STACK POPPED WHILE EMPTY")
        else:
            popVal= prgStack.pop()
            cursor= popVal-1

    elif currentCommand == 19: # print character
        if getValue(cursor) <= 255:
            #sys.stdout.write(chr(getValue(cursor)))
            inputText.insert(END, chr(getValue(cursor)))
            inputText.see(END)
        else:
            printToScreen("CHAR READER ERROR")

    elif currentCommand == 20: # read a character from the terminal and write its ascii code to <a>; it can be assumed that once input starts, it will continue until a newline is encountered; this means that you can safely read whole lines from the keyboard and trust that they will be fully read
        targetReg= currentProgram[cursor] - 32768
        global curInput, handlingInput
        if handlingInput == False:
            wait()
            #curInput= sys.stdin.readline()
            #handlingInput=True
        if len(curInput) == 1:
            handlingInput=False
        if not saveStateFlag and not loadStateFlag:
            register[targetReg]=ord(curInput[0])
            curInput = curInput[1:]
        
    elif currentCommand == 21: #no command
        cursor= cursor-1
    else:
        cursor= cursor-1
        printToScreen(("unhandled command:" ,currentProgram[cursor], " at command " ,cursor))

def printInRange(min, max):
    for i in range (min, max):
        printToScreen("currentProgram[",i,"] = ", currentProgram[i])

def getValue(val):
    currentVal= currentProgram[val]
    if currentVal in range(0,32768):
        return currentVal
    elif currentVal in range(32768,32776):
        return register[currentVal-32768]
    else:
        printToScreen("ERROR INVALID GET VALUE")
        return -1

def wait():
    global handlingInput,loadStateFlag, saveStateFlag,cursor
    while False ==handlingInput and False==loadStateFlag and False==saveStateFlag:
        master.update()
    if True==saveStateFlag: #we have to move the cursor back a command if you save state while the program is waiting for text input, so that when the state is loaded it will start on waiting for input text
        cursor = cursor-2

def waitForStep():
    global stepUpdateChecked, waitingForStep
    if 1 == stepUpdateChecked.get():
        waitingForStep=True
        while waitingForStep ==True:
            master.update()

def stepPressed():
    global waitingForStep
    waitingForStep=False
    
def inputReceived():
    global handlingInput, curInput, e1
    if False == handlingInput:
        curInput= e1.get()
        printToScreen(curInput)
        curInput = curInput + '\n'
        e1.delete(0,END)
        handlingInput=True;

def setRegisters():
    global register,registerInputs
    for i in range(0,8):
        register[i]=int(registerInputs[i].get())



def setCursor():
    global cursorText,cursor
    cursor= int(cursorText.get())

def setStack():
    global prgStack,stackText
    prgStack= []
    stackList= stackText.get().split(',')
    for s in stackList:
        prgStack.append(int(s))

def updateUI():
    global curInput,register,registerInputs,UIUpdate, prgStack,stackText, cursorText, cursor
    if 1== UIUpdate.get():
        for i in range(0,8):
            registerInputs[i].delete(0,END)
            registerInputs[i].insert(0,str(register[i]))
        stackText.delete(0,END)

        curStack=0
        while curStack<len(prgStack):
            stackText.insert(len(stackText.get()),str(prgStack[curStack]))
            if not curStack == len(prgStack)-1:
                stackText.insert(len(stackText.get()),",")
            curStack= curStack+1

        cursorText.delete(0,END)
        cursorText.insert(0,str(cursor))


def printToScreen(line):
    inputText.insert(END, str(line))

def initGUI():
    global inputText, master, e1, registerInputs,register,UIUpdate,stateName,stackText, cursorText, stepCheckBox, stepUpdateChecked 
    master = Tk()
    
    #left frame area
    leftFrame= Frame(master,width=2,bd=1, relief=SUNKEN)
    leftFrame.pack(side=LEFT)
    inputText= Text(leftFrame)
    inputText.bind("<Key>", lambda e: "break")
    inputText.pack(side=TOP)
    x1 =Label(leftFrame, text="Input").pack(side=TOP)
    inputFrame= Frame(leftFrame,width=1)
    e1 = Entry(inputFrame, width=80)
    e1.bind("<Return>",(lambda event: inputReceived()))
    e1.pack(side=LEFT)
    b = Button(inputFrame, text="OK", command=inputReceived).pack(side=LEFT)
    inputFrame.pack(side=BOTTOM)

    #right frame area
    rightFrame= Frame(master,width=2, bd=1,relief=SUNKEN)
    rightFrame.pack(side=RIGHT)
    UIUpdate=IntVar()
    checkUIUpdate = Checkbutton(rightFrame, text="Update variables", onvalue = 1, offvalue = 0, variable=UIUpdate)
    checkUIUpdate.pack(side=TOP)
    Button(rightFrame, text="Print Program", command=printProgram).pack(side=TOP)

    #step manager area
    stepManagerFrame=Frame(rightFrame,bd=1,relief=SUNKEN)
    stepManagerFrame.pack(side=TOP)
    stepUpdateChecked=IntVar()
    stepCheckBox = Checkbutton(stepManagerFrame, text="Step", onvalue = 1, offvalue = 0, variable=stepUpdateChecked)
    stepCheckBox.pack(side=LEFT)
    Button(stepManagerFrame, text="Step", command=stepPressed).pack(side=LEFT)

    #state manager area
    stateManagerFrame=Frame(rightFrame,bd=1,relief=SUNKEN)
    stateManagerFrame.pack(side=TOP)
    Label(stateManagerFrame, text="State Manager").pack(side=TOP)

    stateEntryFrame=Frame(stateManagerFrame)
    stateEntryFrame.pack(side=TOP)
    stateName = Entry(stateEntryFrame, width=30)
    stateName.pack(side=LEFT)
    Button(stateEntryFrame, text="Load State", command=setLoadStateFlag).pack(side=LEFT)
    Button(stateEntryFrame, text="Save State", command=setSaveStateFlag).pack(side=LEFT)
    
    #register updating area
    registerFrame= Frame(rightFrame, bd=1,relief=SUNKEN)
    registerFrame.pack(side=TOP)
    registerInputFrame= Frame(registerFrame,width=1,relief=SUNKEN)
    Label(registerFrame, text="Registers").pack(side=TOP)
    for i in range (0,8):
        registerInputs.append(Entry(registerInputFrame))
        registerInputs[i].grid(row=int(i/2),column=int(i%2))
    registerInputFrame.pack(side=TOP)
    Button(registerFrame, text="Set Registers", command=setRegisters).pack(side=TOP)

    #stack manager area
    stackManagerFrame=Frame(rightFrame,bd=1,relief=SUNKEN)
    stackManagerFrame.pack(side=TOP)
    Label(stackManagerFrame, text="Stack Manager").pack(side=TOP)

    stackEntryFrame=Frame(stackManagerFrame)
    stackEntryFrame.pack(side=TOP)
    stackText = Entry(stackEntryFrame, width=30)
    stackText.pack(side=LEFT)
    Button(stackEntryFrame, text="Set Stack", command=setStack).pack(side=LEFT)

    #cursor manager area
    cursorManagerFrame=Frame(rightFrame,bd=1,relief=SUNKEN)
    cursorManagerFrame.pack(side=TOP)
    Label(cursorManagerFrame, text="Cursor").pack(side=TOP)

    cursorEntryFrame=Frame(cursorManagerFrame)
    cursorEntryFrame.pack(side=TOP)
    cursorText = Entry(cursorEntryFrame, width=10)
    cursorText.pack(side=LEFT)
    Button(cursorEntryFrame, text="Set Cursor", command=setCursor).pack(side=LEFT)


    master.after(10, mainEvent)
    master.mainloop()

def loadFiles(fileName):
    global f,currentProgram,maxSize,cursor,register,prgStack
    fileLoc=("saves/" + fileName+ "/")
    maxSize= int(os.path.getsize(fileLoc + fileName+  ".bin"))
    f = open(fileLoc + fileName+  ".bin", "rb")
    x= 2
    byte = f.read(2)
    currentProgram = []
    
    #loads the program data into memory
    while x<=maxSize:
        if sys.version_info > (3,0):
            curByte= int.from_bytes(byte, byteorder='little')
        else:
            newbyte= byte[1]+byte[0]
            curByte = int(newbyte.encode('hex'), 16)

        currentProgram.append(curByte)
        byte=f.read(2)
        x+=2
    f.close()
    
    #load the program state (cursor location, register values, stack)
    with open(fileLoc+"info.txt") as f:
        lines = f.readlines()
        cursor=int(lines[0])
        splitReg= lines[1].split(',')
        regCount= 0
        for regNum in splitReg:
            register[regCount]= int(regNum)
            regCount+=1
        prgStack=[]
        if(len(lines[2])>1):
             splitStk= lines[2].split(',')
             for regStk in splitStk:
                prgStack.append(int(regStk))

def setLoadStateFlag():
    global loadStateFlag
    loadStateFlag=True

def setSaveStateFlag():
    global saveStateFlag
    saveStateFlag=True

def saveState():
    global cursor, stateName,register,prgStack
    fileName= stateName.get()
    fileLoc=("saves/" + fileName+ "/")
    if not os.path.isdir(fileLoc):
        os.mkdir(fileLoc)
    
    f = open(fileLoc+ fileName + ".bin", 'wb')
    for i  in range(0, len(currentProgram)):
        f.write(struct.pack("<H", currentProgram[i]))
    f.close()

    f = open(fileLoc+ "info.txt", 'w')
    f.write(str(cursor)+ '\n')
    regCursor=0
    for reg in register:
        f.write(str(reg))
        if not 7==regCursor:
            f.write(',')
        regCursor=regCursor+1
    f.write('\n')
    stkCursor=0
    for stk in prgStack:
        f.write(str(stk))
        if not len(prgStack)-1==stkCursor:
            f.write(',')
        stkCursor= stkCursor +1
    f.write('\n')

def printProgram():
    global stringVal,cmdLengths,currentProgram
    f = open("currentdebug.txt", 'w')
    curCursor=0
    while curCursor < len(currentProgram):
        f.write("cmd" +str(curCursor) + " ")
        if currentProgram[curCursor]>=len(stringVal):
            returnVal=""
            if currentProgram[curCursor]>=32768:
                returnVal=("reg"+ str(currentProgram[curCursor]-32768))
            else:
                returnVal=str(currentProgram[curCursor])
            f.write("UNKNOWN COMMAND " + returnVal)
        else:
            f.write(stringVal[currentProgram[curCursor]] + "(")
            f.write(str(currentProgram[curCursor]) + ") " )
            if currentProgram[curCursor]==19:
                while currentProgram[curCursor]==19:
                    if currentProgram[curCursor+1] <=255:
                        f.write(chr(currentProgram[curCursor+1]))
                    else:
                        f.write("REG"+ str(currentProgram[curCursor+1]-32768))
                    curCursor= curCursor+2
                curCursor= curCursor-1
            else:
                varNum=2
                totalVars=cmdLengths[currentProgram[curCursor]]
                while varNum<=totalVars:
                    curCursor= curCursor+1
                    if currentProgram[curCursor]>=32768:
                        f.write("reg" + str(currentProgram[curCursor]-32768)+ " ")
                    else:
                        f.write(str(currentProgram[curCursor])+ " ")
                    varNum= varNum+1   
        f.write('\n')
        curCursor=curCursor+1
        f.flush()



def mainEvent():
    global cursor,maxSize, currentProgram, root, loadStateFlag, saveStateFlag, stateName
    while cursor <= maxSize/2:
        master.update()
        handleCommand(currentProgram[cursor])
        cursor= cursor +1
        updateUI()
        waitForStep()
        if True==loadStateFlag:
            loadFiles(stateName.get())
            loadStateFlag= False
        if True==saveStateFlag:
            saveState()
            saveStateFlag= False

try:
    loadFiles('challenge')
except:
    printToScreen(("Unexpected error:", sys.exc_info()[0]))
    printToScreen(("Unexpected error:", sys.exc_info()[1]))

finally:
    initGUI()
  