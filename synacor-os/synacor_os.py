import os
import sys
import struct
from Tkinter import *
import time

cursor=0
f = open("challenge.bin", "rb")
maxSize= int(os.path.getsize("challenge.bin"))
currentProgram = []
register = [0,0,0,0,0,0,0,0]
prgStack = []
stringVal= ["halt", "set", "push", "pop", "eq", "gt", "jmp", "jt", "jf", "add", "mult", "mod", "and", "or", "not", "rmem", "wmem", "call", "ret", "out", "in", "noop"]
curInput = []
handlingInput= False
inputText = []
master = []

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
        else:
            printToScreen("CHAR READER ERROR")

    elif currentCommand == 20: # read a character from the terminal and write its ascii code to <a>; it can be assumed that once input starts, it will continue until a newline is encountered; this means that you can safely read whole lines from the keyboard and trust that they will be fully read
        targetReg= currentProgram[cursor] - 32768
        global curInput, handlingInput
        if handlingInput == False:
            curInput= sys.stdin.readline()
            handlingInput=True
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

def printToScreen(line):
    inputText.insert(END, line)

def initGUI():
    global inputText, master
    master = Tk()
    inputText= Text(master)
    inputText.grid(row=0, column=1,pady=20)
    x1 =Label(master, text="First").grid(row=1, pady=0)
    e1 = Entry(master)
    e1.grid(row=1, column=1)
    master.after(10, mainEvent)
    master.mainloop()


def mainEvent():
    global cursor,maxSize, currentProgram, root
    while cursor <= maxSize/2:
        master.update()
        handleCommand(currentProgram[cursor])
        cursor= cursor +1


try:
    x= 2
    byte = f.read(2)
    currentProgram = []
    
    while x<=maxSize:
        #curByte= int.from_bytes(byte, byteorder='little')

        newbyte= byte[1]+byte[0]
        curByte = int(newbyte.encode('hex'), 16)

        currentProgram.append(curByte)
        byte=f.read(2)
        x+=2
except:
    printToScreen("Unexpected error:", sys.exc_info()[0])
    printToScreen("Unexpected error:", sys.exc_info()[1])

finally:
    f.close()
    cursor=0
    initGUI()

    