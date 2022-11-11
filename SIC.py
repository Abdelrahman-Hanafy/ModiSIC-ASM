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