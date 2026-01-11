"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

PARSER MODULE
=============
The Parser class is responsible for:
1. Reading and cleaning assembly code (removing whitespace/comments)
2. Identifying command types (A-command, C-command, L-command)
3. Extracting command components (dest, comp, jump, symbol)
4. Managing the current position in the code during parsing

Command Types:
- A-command: @address or @symbol (load address into A register)
- C-command: dest=comp;jump (compute, store, and/or jump)
- L-command: (LABEL) (pseudo-command, defines a label)

The parser maintains state about the current command being processed,
allowing the assembler to iterate through commands and extract information.
"""
import typing
from SymbolTable import SymbolTable
from Code import Code


class Parser:
    """
    Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """
    def __init__(self, input_file: typing.TextIO) -> None:
        """
        Initialize the parser with an input file.
        
        Reads all lines from the input file and stores them. The parser
        maintains state about the current position and current command
        being processed.
        
        Args:
            input_file (typing.TextIO): The input .asm file to parse.
        
        Instance Variables:
            input_lines: Raw lines from file (with whitespace/comments)
            c_index: Current command index (-1 means not started)
            c_command: Current command being processed (None initially)
            input_lines_proccessed: Cleaned lines (after delete_whitespaces)
            open_variables: Next available RAM address for variables (starts at 15,
                           so first variable gets 16)
        """
        # Read all lines from input file
        self.input_lines = input_file.read().splitlines()
        
        # Current command index (-1 means we haven't started parsing yet)
        self.c_index = -1

        # Current command being processed (set by advance())
        self.c_command = None
        
        # Cleaned lines (populated by delete_whitespaces())
        self.input_lines_proccessed = []
        
        # Next available RAM address for variables (starts at 15, so first is 16)
        # Addresses 0-15 are reserved for R0-R15 and predefined symbols
        self.open_variables = 15
    
    def reset_index(self) -> None:
        """
        Reset the parser to the beginning of the code.
        
        Sets c_index back to -1, allowing the parser to iterate through
        the code again from the start. This is useful for multiple passes
        over the same code (e.g., pass 1 for labels, pass 2 for variables).
        
        Returns:
            None: Modifies self.c_index.
        """
        self.c_index = -1

    def replace_symbol(self, address: str) -> None:
        """
        Replace the current A-command's symbol with a numeric address.
        
        Used during variable processing to replace @symbol with @address.
        For example, @counter might become @16.
        
        Args:
            address (str): The numeric address to replace the symbol with.
        
        Returns:
            None: Modifies self.input_lines_proccessed and self.c_command.
        """
        # Replace the line with @address
        self.input_lines_proccessed[self.c_index] = "@" + str(address)
        # Update current command to reflect the change
        self.c_command = self.input_lines_proccessed[self.c_index]

    def add_variable(self) -> int:
        """
        Allocate the next available RAM address for a new variable.
        
        Variables are assigned addresses starting at 16 (after R0-R15).
        Each call increments the counter and returns the new address.
        
        Returns:
            int: The next available RAM address for a variable.
        
        Example:
            First call: returns 16
            Second call: returns 17
            etc.
        """
        self.open_variables += 1
        return self.open_variables

    def delete_whitespaces(self) -> None:
        """
        Clean the input lines by removing whitespace and comments.
        
        This is the first step in processing. It:
        - Removes lines that are only comments (start with //)
        - Removes empty lines
        - Removes all spaces from remaining lines
        - Removes inline comments (everything after //)
        
        The cleaned lines are stored in self.input_lines_proccessed.
        
        Returns:
            None: Populates self.input_lines_proccessed with cleaned lines.
        
        Example:
            Input:  ["  @5  // comment", "  D=M  ", "// full comment", ""]
            Output: ["@5", "D=M"]
        """
        for i in range(len(self.input_lines)):
            line = self.input_lines[i]
            
            # Skip lines that are only comments or empty
            if line.startswith('//') or line == '':
                continue
            
            # Remove all spaces
            new_line = line.replace(" ", "")
            
            # Remove inline comments (everything after //)
            if "//" in new_line:
                new_line = new_line.split('//')[0]
            
            # Add cleaned line to processed list
            self.input_lines_proccessed += [new_line]
    
    def has_more_commands(self) -> bool:
        """
        Check if there are more commands to process.
        
        Returns:
            bool: True if there are more commands (c_index hasn't reached the end),
                  False otherwise.
        
        Note:
            Uses < len - 1 because c_index is 0-based and we check before
            incrementing. When c_index == len - 1, we're at the last command.
        """
        return self.c_index < len(self.input_lines_proccessed) - 1
    
    def advance(self) -> None:
        """
        Move to the next command and make it the current command.
        
        Should only be called if has_more_commands() returns True.
        Increments c_index and sets c_command to the next line.
        
        Returns:
            None: Modifies self.c_index and self.c_command.
        
        Side Effects:
            - If more commands exist: increments c_index and sets c_command
            - If no more commands: sets c_command to None
        """
        if self.has_more_commands():
            self.c_index += 1
            self.c_command = self.input_lines_proccessed[self.c_index]
        else:
            self.c_command = None
    
    def command_type(self) -> str:
        """
        Identify the type of the current command.
        
        Command types are determined by the first character:
        - '@' -> A-command (address/symbol reference)
        - '(' -> L-command (label declaration)
        - Otherwise -> C-command (computation/jump)
        
        Returns:
            str: One of "A_COMMAND", "C_COMMAND", or "L_COMMAND".
        
        Example:
            "@5" -> "A_COMMAND"
            "D=M" -> "C_COMMAND"
            "(LOOP)" -> "L_COMMAND"
        """
        if self.c_command.startswith('@'):
            return "A_COMMAND"
        elif self.c_command.startswith('('):
            return "L_COMMAND"
        else:
            return "C_COMMAND"
    
    def symbol(self) -> str:
        """
        Extract the symbol from an A-command or L-command.
        
        For A-commands: Returns the part after '@' (e.g., "@5" -> "5", "@LOOP" -> "LOOP")
        For L-commands: Returns the label name (e.g., "(LOOP)" -> "LOOP")
        
        Should only be called when command_type() is "A_COMMAND" or "L_COMMAND".
        
        Returns:
            str: The symbol/label name, or None if called on wrong command type.
        
        Example:
            "@counter" -> "counter"
            "(LOOP)" -> "LOOP"
            "@5" -> "5"
        """
        if self.command_type() == "A_COMMAND":
            # Extract everything after '@'
            return self.c_command.split('@')[1]
        elif self.command_type() == "L_COMMAND":
            # Extract label name between parentheses
            return self.c_command.split('(')[1].split(')')[0]
        return None
    
    def pop_label(self) -> int:
        """
        Remove the current L-command (label) from the code and return next instruction index.
        
        Labels are pseudo-commands that don't generate binary code. They mark
        a location that other instructions can jump to. This function:
        1. Removes the label line from input_lines_proccessed
        2. Decrements c_index (since we removed a line)
        3. Returns the index of the next instruction (which becomes the label's address)
        
        Returns:
            int: The index of the next instruction after the removed label.
                 This is the address that jumps to this label should use.
        
        Example:
            If label is at index 2, removing it makes next instruction at index 2.
            Returns 2 (the address for jumps to this label).
        """
        # Remove the label line
        self.input_lines_proccessed.pop(self.c_index)
        # Decrement index since we removed a line
        self.c_index -= 1
        # Clear current command (we just removed it)
        self.c_command = None
        # Return the index of the next instruction (label's target address)
        return self.c_index + 1

    def dest(self) -> str:
        """
        Extract the destination field from a C-command.
        
        C-commands have the format: dest=comp or dest=comp;jump
        The dest field specifies where to store the computation result.
        If there's no '=' sign, there's no destination (dest="null").
        
        Should only be called when command_type() is "C_COMMAND".
        
        Returns:
            str: The destination mnemonic (M, D, A, MD, AM, AD, AMD, or "null").
        
        Example:
            "D=M" -> "D"
            "MD=D+1" -> "MD"
            "D;JGT" -> "null" (no destination, just jump)
        """
        if '=' in self.c_command:
            # Everything before '=' is the destination
            return self.c_command.split('=')[0]
        return "null"

    def comp(self) -> tuple[bool, str]:
        """
        Extract the computation field from a C-command and detect extended operations.
        
        C-commands have the format: dest=comp or comp;jump or dest=comp;jump
        The comp field specifies what computation to perform.
        
        Extended operations are shift operations (A<<, D>>, etc.) that use
        a different binary encoding than standard operations.
        
        Should only be called when command_type() is "C_COMMAND".
        
        Returns:
            tuple[bool, str]: 
                - bool: True if this is an extended operation (contains >> or <<)
                - str: The computation mnemonic (e.g., "M", "D+1", "A<<", "null")
        
        Example:
            "D=M" -> (False, "M")
            "D=D+1" -> (False, "D+1")
            "M=A<<" -> (True, "A<<")
            "D;JGT" -> (False, "D")
        """
        # Check if this is an extended operation (shift)
        is_extended = False
        if ">>" in self.c_command or "<<" in self.c_command:
            is_extended = True

        # Extract comp field based on command format
        if '=' in self.c_command and ';' in self.c_command:
            # Format: dest=comp;jump
            # comp is between '=' and ';'
            return (is_extended, self.c_command.split('=')[1].split(';')[0])
        elif '=' in self.c_command:
            # Format: dest=comp
            # comp is everything after '='
            return (is_extended, self.c_command.split('=')[1])
        elif ';' in self.c_command:
            # Format: comp;jump
            # comp is everything before ';'
            return (is_extended, self.c_command.split(';')[0])
        # No = or ; (shouldn't happen for valid C-commands, but handle gracefully)
        return (is_extended, "null")
    

    def jump(self) -> str:
        """
        Extract the jump field from a C-command.
        
        C-commands can have the format: comp;jump or dest=comp;jump
        The jump field specifies a conditional jump based on the computation result.
        If there's no ';' sign, there's no jump (jump="null").
        
        Should only be called when command_type() is "C_COMMAND".
        
        Returns:
            str: The jump mnemonic (JGT, JEQ, JGE, JLT, JNE, JLE, JMP, or "null").
        
        Example:
            "D;JGT" -> "JGT"
            "M=D;JMP" -> "JMP"
            "D=M" -> "null" (no jump)
        """
        if ';' in self.c_command:
            # Everything after ';' is the jump condition
            return self.c_command.split(';')[1]
        return "null"
    
    
