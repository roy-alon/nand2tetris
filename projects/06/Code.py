"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

CODE TRANSLATION MODULE
========================
The Code class translates Hack assembly mnemonics into their binary
representations. This is the final step in converting assembly
language to machine code.

C-Command Structure (16 bits):
  1 1 1 a c1 c2 c3 c4 c5 c6 d1 d2 d3 j1 j2 j3
  | | | | |  |  |  |  |  |  |  |  |  |  |  |
  | | | | |  |  |  |  |  |  |  |  |  |  |  +-- jump (3 bits)
  | | | | |  |  |  |  |  |  |  |  |  +--+----- dest (3 bits)
  | | | | |  |  |  |  |  |  |  +--+--------- comp (7 bits)
  | | | +--+--+--+--+--+--+------------------- a-bit + computation
  +--+--+------------------------------------- always 111 for C-commands

A-Command Structure (16 bits):
  0 + 15-bit address

The Code class provides static methods to translate each field:
- dest(): 3-bit code for destination register(s)
- comp(): 7-bit code for computation operation
- jump(): 3-bit code for jump condition
- extend_c(): Special encoding for shift operations
"""


class Code:
    """
    Translates Hack assembly language mnemonics into binary codes.
    
    All methods are static because they're pure translation functions
    that don't require instance state. They map assembly mnemonics
    to their corresponding binary representations according to the
    Hack machine language specification.
    """
    
    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Translate destination mnemonic to 3-bit binary code.
        
        The destination field specifies where to store the result of
        the computation. Multiple destinations can be combined.
        
        Args:
            mnemonic (str): Destination mnemonic:
                - "null": No destination (000)
                - "M": Memory[A] (001)
                - "D": D register (010)
                - "MD": Both M and D (011)
                - "A": A register (100)
                - "AM": Both A and M (101)
                - "AD": Both A and D (110)
                - "AMD": All three (111)
        
        Returns:
            str: 3-bit binary string representing the destination.
        
        Example:
            dest("M") -> "001"
            dest("D") -> "010"
            dest("MD") -> "011"
            dest("null") -> "000"
        """
        if(mnemonic == "null"):
            return "000"
        if(mnemonic == "M"):
            return "001"
        if(mnemonic == "D"):
            return "010"
        if(mnemonic == "MD"):
            return "011"
        if(mnemonic == "A"):
            return "100"
        if(mnemonic == "AM"):
            return "101"
        if(mnemonic == "AD"):
            return "110"
        if(mnemonic == "AMD"):
            return "111"

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Translate computation mnemonic to 7-bit binary code.
        
        The computation field specifies what operation to perform.
        The 7-bit code consists of:
        - 1 a-bit: 0 for A register, 1 for M (Memory[A])
        - 6 computation bits: specific operation code
        
        Args:
            mnemonic (str): Computation mnemonic. Supported operations:
                Constants: "0", "1", "-1"
                Single operand: "D", "A", "M", "!D", "!A", "!M", "-D", "-A", "-M"
                Two operands: "D+1", "A+1", "M+1", "D-1", "A-1", "M-1",
                             "D+A", "D+M", "D-A", "D-M", "A-D", "M-D",
                             "D&A", "D&M", "D|A", "D|M"
        
        Returns:
            str: 7-bit binary string representing the computation.
                 Format: a c1 c2 c3 c4 c5 c6
        
        Example:
            comp("0") -> "0101010"
            comp("D") -> "0001100"
            comp("M") -> "1110000"  (a=1 for memory)
            comp("D+M") -> "1000010"
        """
        if(mnemonic == "0"):
            return "0101010"
        if(mnemonic == "1"):
            return "0111111"
        if(mnemonic == "-1"):
            return "0111010"
        if(mnemonic == "D"):
            return "0001100"
        if(mnemonic == "A"):
            return "0110000"
        if(mnemonic == "!D"):
            return "0001101"
        if(mnemonic == "!A"):
            return "0110001"
        if(mnemonic == "-D"):
            return "0001111"
        if(mnemonic == "-A"):
            return "0110011"
        if(mnemonic == "D+1"):
            return "0011111"
        if(mnemonic == "A+1"):
            return "0110111"
        if(mnemonic == "D-1"):
            return "0001110"
        if(mnemonic == "A-1"):
            return "0110010"
        if(mnemonic == "D+A"):
            return "0000010"
        if(mnemonic == "D-A"):
            return "0010011"
        if(mnemonic == "A-D"):
            return "0000111"
        if(mnemonic == "D&A"):
            return "0000000"
        if(mnemonic == "D|A"):
            return "0010101"
        if(mnemonic == "M"):
            return "1110000"
        if(mnemonic == "!M"):
            return "1110001"
        if(mnemonic == "-M"):
            return "1110011"
        if(mnemonic == "M+1"):
            return "1110111"
        if(mnemonic == "M-1"):
            return "1110010"
        if(mnemonic == "D+M"):
            return "1000010"
        if(mnemonic == "D-M"):
            return "1010011"
        if(mnemonic == "M-D"):
            return "1000111"
        if(mnemonic == "D&M"):
            return "1000000"
        if(mnemonic == "D|M"):
            return "1010101"

    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Translate jump condition mnemonic to 3-bit binary code.
        
        The jump field specifies a conditional jump based on the
        computation result. The jump occurs if the condition is met.
        
        Args:
            mnemonic (str): Jump condition mnemonic:
                - "null": No jump (000)
                - "JGT": Jump if comp > 0 (001)
                - "JEQ": Jump if comp == 0 (010)
                - "JGE": Jump if comp >= 0 (011)
                - "JLT": Jump if comp < 0 (100)
                - "JNE": Jump if comp != 0 (101)
                - "JLE": Jump if comp <= 0 (110)
                - "JMP": Unconditional jump (111)
        
        Returns:
            str: 3-bit binary string representing the jump condition.
        
        Example:
            jump("null") -> "000"
            jump("JGT") -> "001"
            jump("JMP") -> "111"
        """
        if(mnemonic == "null"):
            return "000"
        if(mnemonic == "JGT"):
            return "001"
        if(mnemonic == "JEQ"):
            return "010"
        if(mnemonic == "JGE"):
            return "011"
        if(mnemonic == "JLT"):
            return "100"
        if(mnemonic == "JNE"):
            return "101"
        if(mnemonic == "JLE"):
            return "110"
        if(mnemonic == "JMP"):
            return "111"

    @staticmethod
    def extend_c(mnemonic: str) -> str:
        """
        Translate extended C-instruction (shift operations) to binary prefix.
        
        Extended C-instructions support bit shift operations that aren't
        part of the standard Hack instruction set. These use a special
        encoding with prefix "101" instead of "111".
        
        The shift operations are:
        - A<<, D<<, M<<: Left shift
        - A>>, D>>, M>>: Right shift
        
        Args:
            mnemonic (str): Shift operation mnemonic:
                - "A<<": Left shift A register
                - "D<<": Left shift D register
                - "M<<": Left shift Memory[A]
                - "A>>": Right shift A register
                - "D>>": Right shift D register
                - "M>>": Right shift Memory[A]
        
        Returns:
            str: 10-bit binary string: "101" + 7-bit comp code.
                 This is the prefix for extended C-instructions.
                 Note: This does NOT include dest and jump bits - those
                 are added separately in the assembler.
        
        Example:
            extend_c("A<<") -> "1010100000"
            extend_c("D>>") -> "1010010000"
        
        Note:
            The full extended C-instruction format is:
            extend_c(comp) + dest(3 bits) + jump(3 bits) = 16 bits total
        """
        comp = ""
        # Left shift operations
        if(mnemonic=="A<<"):
            comp="0100000"
        if(mnemonic=="D<<"):
            comp="0110000"
        if(mnemonic=="M<<"):
            comp="1100000"
        # Right shift operations
        if(mnemonic=="A>>"):
            comp="0000000"
        if(mnemonic=="D>>"):
            comp="0010000"
        if(mnemonic=="M>>"):
            comp="1000000"
        # Return prefix "101" + 7-bit comp code (dest and jump added separately)
        return "101" + comp