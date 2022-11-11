from SIC import *

print("Getting started")
#get Ready
inst = loadInstruction()
prog = loadProg(inst,'in.txt')

print("Pass1 Begin")
#Pass1
getLoc(inst,prog)
symb = getSymbTab(prog)

print("Pass2 Begin")
#Pass2
getObcode(prog,inst,symb)
writeHTE(prog)

print("Check for the output files")