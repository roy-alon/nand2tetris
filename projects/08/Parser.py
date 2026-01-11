"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line's end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        self.cur_com = ''


    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        if len(self.input_lines) > 0:
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        # Your code goes here!
        self.cur_com = self.input_lines.pop(0)
        # print("Preloop: ", self.cur_com)
        while (self.cur_com.startswith('//') or self.cur_com.isspace() or self.cur_com == '') and self.has_more_commands():
            self.cur_com = self.input_lines.pop(0)
            # print("loop command: ", self.cur_com)
        # print("Postloop: ", self.cur_com)
        self.cur_com = self.cur_com.strip()
        self.cur_com = self.cur_com.split('//')[0].strip()


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Your code goes here!
        first_arg = self.cur_com.split(' ')[0]
        if first_arg == 'push':
            return 'C_PUSH'
        elif first_arg == 'pop':
            return 'C_POP'
        elif first_arg in ["add", "sub", "neg", "and", "or", "not", "shiftleft", "shiftright", "eq", "gt", "lt"]:
            return 'C_ARITHMETIC'
        elif first_arg == 'label':
            return "C_LABEL"
        elif first_arg == "goto":
            return "C_GOTO"
        elif first_arg == "if-goto":
            return "C_IF"
        elif first_arg == "function":
            return "C_FUNCTION"
        elif first_arg == "call":
            return "C_CALL"
        elif first_arg == "return":
            return "C_RETURN"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!
        if self.command_type() == 'C_ARITHMETIC':
            return self.cur_com
        elif self.command_type() == 'C_PUSH' or self.command_type() == 'C_POP':
            return self.cur_com.split(' ')[1] # In case of a push or pop we return the segment. i.e. push local 0 returns local
        elif self.command_type() == 'C_LABEL' or self.command_type() == 'C_GOTO' or self.command_type() == 'C_IF':
            return self.cur_com.split(' ')[1]
        elif self.command_type() == 'C_FUNCTION' or self.command_type() == 'C_CALL':
            return self.cur_com.split(' ')[1]  # Function name is the first argument
        else:
            return None

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        if self.command_type() == 'C_PUSH' or self.command_type() == 'C_POP':
            return int(self.cur_com.split(' ')[2])
        elif self.command_type() == 'C_FUNCTION' or self.command_type() == 'C_CALL':
            return int(self.cur_com.split(' ')[2])  # Number of vars/args is the second argument
        elif self.command_type() == 'C_LABEL' or self.command_type() == 'C_GOTO' or self.command_type() == 'C_IF':
            return None  # These commands don't have a second argument
        elif self.command_type() == 'C_RETURN':
            return None
        elif self.command_type() == 'C_ARITHMETIC':
            return None
        else:
            return None
