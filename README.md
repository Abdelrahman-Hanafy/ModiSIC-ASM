# Modi-SIC ASM
this project is assosiated with systems programming course at Arab Academy for Science and Technology. It simulates the 2 pass assembler of sic machine but with some add-ons. it add the format 1 instruction and the immdiate mode to the sic machine 

## Requirements
```
    pip install pandas
```
## File structure
```
MODISIC ASM
|   README.md
|   in.txt          //the file which includes Modi-SIC program
|   Util.py         //python script has some functions and Disct to use in assembling
|   SIC.py          //python script include All the assembling function
|   Assembler.py    //python script has the sequence of 2 pass assembler
|   RUN.bat         //bat script include the commands to run the project 
|-- OUT             //dir that includes all the output files
    |
    |-- intermediate.txt
    |-- out_pass1.txt
    |-- symbTable.txt
    |-- out_pass2.txt
    |-- HTE.txt 
```
## How to run the ASM
- Clone the project on your machine
- Run the command found in `Requirements` section on your CMD
- Put your assembly program at `in.txt` 
- Run `RUN.bat` file and it will create `OUT` if you deleted it
- Open `OUT` dir and find all the output files
