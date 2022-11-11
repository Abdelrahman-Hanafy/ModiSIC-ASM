import pandas as pd
import numpy as np
import Util
from Util import hexSum 

def loadInstruction():
    instructions = {}
    data = Util.Instructions
    for k,v in data.items():
        if('-' in v):
            t = v[1:]
            instructions[k] = f"-{int(t,16):08b}"
        else:
            instructions[k] = f"{int(v,16):08b}"
        
    return instructions

def loadProg(inst):
    '''
    Function : Make intermediate file
    Arg : instruction dict
    Resuorses : in.txt file contains the program
    output : intermediate.txt
    return: dataframe with [label, mono, oprand]
    '''
    temp = []
    with open('in.txt','r') as f:
        lines = f.readlines()
        lines = [x.split('\t') for x in lines]
        for line in lines:
            line = [x.strip() for x in line[1:] if (x != '' and x != ' ')]
            if '.' in line:
                continue
            if(len(line) == 1 and line[0] == ''):
                continue
            temp.append(line)
    
    labels = []
    mono = []
    oprnd = []
    for line in temp:
        if(line[0] in inst):
            mn = line[0]
            labels.append(np.nan)
            mono.append(mn)
            if('-' in inst[mn] or mn == "RSUB"):
                oprnd.append(np.nan)
            else:
                oprnd.append(line[1])
        else:
            lb = line[0]
            mn = line[1]
            if('START' in line):
                labels.append(lb)
                mono.append(mn)
                oprnd.append(line[2])
            elif('END' in line):
                labels.append(np.nan)
                mono.append(lb)
                oprnd.append(mn)
            elif( mn in inst):
                labels.append(lb)
                mono.append(mn)
                if('-' in inst[mn] or mn == "RSUB"):
                    oprnd.append(np.nan)
                else:
                    oprnd.append(line[2])
            else:
                labels.append(lb)
                mono.append(mn)
                oprnd.append(line[2])
        
    demo = pd.DataFrame([labels,mono,oprnd])
    demo = demo.T
    demo.columns = ["label","mono","oprnd"]
    
    demo.to_csv("OUT/intermediate.txt",sep="\t",index=False)
    return demo

def getLoc(inst,prog):
    '''
    Function : generate location counter
    Arg : dataframe with the program, instruction dict
    ouput : pass1 file
    '''
    x = prog[prog.mono == "START"].oprnd[0]
    loc = []
    for s,v in zip(prog.mono,prog.oprnd):
        loc.append(f'{x:0>4}')
        v = str(v)
        if(s == 'START'):
            continue
        if(s in inst):
            if('-' in inst[s]):
                x = hexSum(x,"1")
            else:
                x = hexSum(x,"3")
        else:
            size = "0"
            if('C' in v):
                size = hex(len(v[2:-1]))
            elif('X' in v):
                size = hex(len(v[2:-1])//2)
            elif(s == "WORD"):
                size = "3"
            elif(s == "BYTE"):
                size = "1"
            elif(s == "RESW"):
                size = hex(int(v)*3)
            elif(s == "RESB"):
                size = hex(int(v))
            x = hexSum(x,size)
        
    prog.insert(0,"LOC",loc)
    prog.to_csv("OUT/out_pass1.txt",sep="\t",index=False)

def getSymbTab(prog):
    '''
    Function : generate symble table
    Arg : dataframe with the program
    output : symbTable file
    return : symb dict
    '''
    table = {}
    for loc,lab in zip(prog.LOC,prog.label):
        if(lab is not np.nan):
            table[lab] = loc
    with open('OUT/symbTable.txt','w') as file:
        tmp = ""
        for k,v in table.items():
            tmp += f"{k}:{v}\n"
        file.write(tmp)
    return table

def getObcode(prog,inst,symb):
    '''
    Function : generate object code
    Arg : dataframe with the program, instruction dict, symbole dict
    output : pass2 file
    '''
    obcode = []
    for s,v in zip(prog.mono,prog.oprnd):
        tmp = ""
        if(s in inst):
            t = inst[s]
            if('-' in inst[s]):
                obcode.append(t)
                continue
            elif( s == "RSUB"):
                tmp = "0000"
            elif('#' in v):
                tmp = hex(int(v[1:]))
                t[8]  = '1'
                obcode.append(f"{t:x}{tmp:04x}")
                continue
            elif(',X' in v):
                tmp = symb[v[:-2]]
                tmp = hexSum(tmp,"1000")
            else:
                tmp = symb[v]
                
            tmp = int(tmp,16)
            t = int(t,2)
            obcode.append(f"{t:02x}{tmp:04x}")

        else:
            if(s == "START" or s == "END" or "RES" in s):
                obcode.append(np.nan)
            else:
                val = ""
                v = str(v)
                if('C' in v):
                    v = v[2:-1]
                    val = "".join([f"{ord(i):0x}" for i in v ])
                elif('X' in v):
                    val = v[2:-1]
                elif(s == "WORD"):
                    val = f"{int(v):06x}"
                elif(s == "BYTE"):
                    val = f"{int(v):02x}"
                obcode.append(val)

    prog["ObCode"] = obcode
    prog.to_csv("OUT/out_pass2.txt",sep="\t",index=False)

def getHErecord(prog):
    #Make H record
    name = prog[prog.mono == "START"].label[0]
    st_Addr = prog[prog.mono == "START"].oprnd[0]
    st_Addr = f"{int(st_Addr,16):06x}"
    
    l = len(prog.LOC) - 1 
    end = prog[prog.mono == "END"].LOC[l]
    ln = int(end,16) - int(st_Addr,16)
    length = f"{ln:06x}"
    
    h = f"H{name:x>6}{st_Addr}{length}\nE{st_Addr}"
    return h

def getTrecord(prog):
    #Make T records
    ln = 0
    tmp = ""
    t= ""
    for l,m,ob in zip(prog.LOC,prog.mono,prog.ObCode):
        ob = str(ob)
        if(m == "START"):
            st_Addr = l
        elif(m == "END"):
            if(len(tmp) > 0):
                t += f"T{st_Addr:0>6}{ln//2:02x}{tmp}\n"
        elif("RES" in m):
            if(len(tmp) > 0):
                t += f"T{st_Addr:0>6}{ln//2:02x}{tmp}\n"
            tmp = ""
            ln = 0
            st_Addr = l
        
        elif(ln + len(ob) <= 60):
            tmp += ob
            ln += len(ob)
        
        else:
            t += f"T{st_Addr:0>6}{ln//2:02x}{tmp}\n"
            st_Addr = l
            tmp = ob
            ln = len(ob)
    return t
