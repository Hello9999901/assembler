"""
MIT License

Copyright (c) 2023 Byran H

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys

table = {
    # jump instructions
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
    # comp instructions
    # these include the "a" bit (the fourth msb)
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101",
}

# main symbol table, with predefined symbols. other symbols are appended
symbol_table = {
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "R6": 6,
    "R7": 7,
    "R8": 8,
    "R9": 9,
    "R10": 10,
    "R11": 11,
    "R12": 12,
    "R13": 13,
    "R14": 14,
    "R15": 15,
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}

file = open(sys.argv[1], "r")
input = file.readlines()
asm = []
output = []

"""
Parsing to remove comments, removing whitespace
"""

for line in input:
    temp_string = line.replace(" ", "").strip()
    if (temp_string != ""):
        # the entire line is a comment
        if (temp_string.find("//") == 0):
            pass
        # there are no comments in the line
        elif (temp_string.find("//") == -1):
            asm.append(temp_string)
        # take substring until the in-line comment begins
        else:
            asm.append(temp_string[:temp_string.find("//")])

"""
Handing symbols, first pass...
Each time a label declaration (xxx) is encountered, the assembler adds a new entry to the symbol table, associating
the symbol xxx with the current line number plus 1 (this will be the ROM address of the next instruction in the program).
"""

cnt = 16
line_cnt = 0

for line in asm:
    # label symbol processing
    if (line.startswith("(") and line.endswith(")")):
        symbol_table.update({line[1:len(line)-1] : line_cnt})
    else:
        line_cnt += 1

for line in asm:
    # variable symbol processing
    if line.startswith("@"):
        if (not line[1:].isdigit() and not line[1:] in symbol_table.keys()):
            symbol_table.update({line[1:] : cnt})
            cnt += 1

for line in asm:
    if line.startswith("@"):
        # a instruction
        # get variable/label from symbol table if available
        if (not line[1:].isdigit() and line[1:] in symbol_table.keys()):
            num = symbol_table.get(line[1:])
        # define as line number
        else:
            num = int(line[1:])
        # convert to binary and take substring after "0b"
        binary = bin(num)[2:]
        # dynamic pad for 16 zeroes
        output.append((16 - len(binary)) * "0" + binary)

    elif not line.startswith("(") and not line.endswith(")"):
        # c instruction

        """
        3 cases for c instruction structure:
        1. dest=comp
        2. dest=comp;jump
        3. comp;jump
        """

        dest_in = comp_in = jump_in = dest_out = comp_out = jump_out = ""

        # case 1, dest=comp
        if "=" in line:
            [dest_in, comp_in] = line.split("=")

        # case 2, dest=comp;jump
        if ";" in line and "=" in line:
            [dest_in, comp_in, jump_in] = line.replace(";", " ").replace("=", " ").split(" ")
            jump_out = table.get(jump_in)

        # case 3, comp;jump
        elif ";" in line:
            [comp_in, jump_in] = line.split(";")
            jump_out = table.get(jump_in)

        else:
            jump_out = "000"

        comp_out = table.get(comp_in)
        dest_out += "1" if "A" in dest_in else "0"
        dest_out += "1" if "D" in dest_in else "0"
        dest_out += "1" if "M" in dest_in else "0"

        output.append("111" + comp_out + dest_out + jump_out)

f = open("out.hack", "w")

for line in output:
    f.write(line + "\n")

f.close()