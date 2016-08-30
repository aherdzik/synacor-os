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
curInput = []
handlingInput= False
inputText = []
master = []
maxSize = []
registerInputs = []
e1=[]
UIUpdate= []

def handleCommand(currentCommand):
    global cursor, inputText
    cursor= cursor+1
    if currentCommand == 0: # stop program
        printToScreen("program halted at command " ,cursor-1)
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
        register[targetReg]=ord(curInput[0])
        curInput = curInput[1:]
        
    elif currentCommand == 21: #no command
        cursor= cursor-1
    else:
        cursor= cursor-1
        printToScreen("unhandled command:" ,currentProgram[cursor], " at command " ,cursor)

def saveState():
    global cursor
    f = open('output.bin', 'wb')
    for i  in range(0, len(currentProgram)):
        f.write(struct.pack("<H", currentProgram[i]))
    f.close()

def loadState():
    global cursor

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
    global handlingInput
    while False ==handlingInput:
        master.update()

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

def updateUI():
    global curInput,register,registerInputs,UIUpdate
    if 1== UIUpdate.get():
        for i in range(0,8):
            registerInputs[i].delete(0,END)
            registerInputs[i].insert(0,str(register[i]))

def printToScreen(line):
    inputText.insert(END, str(line))

def initGUI():
    global inputText, master, e1, registerInputs,register,UIUpdate
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
        if(len(lines[2])>1):
             splitStk= lines[2].split(',')
             for regStk in splitStk:
                prgStack.append(int(regStk))


def mainEvent():
    global cursor,maxSize, currentProgram, root
    while cursor <= maxSize/2:
        master.update()
        handleCommand(currentProgram[cursor])
        cursor= cursor +1
        updateUI()


try:
    loadFiles('challenge')
except:
    printToScreen(("Unexpected error:", sys.exc_info()[0]))
    printToScreen(("Unexpected error:", sys.exc_info()[1]))

finally:
    initGUI()
  