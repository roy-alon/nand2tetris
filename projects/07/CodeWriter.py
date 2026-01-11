"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream
        self.filename = ""
        self.counter = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.filename = filename

    

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        def add_():
            self.output_stream.write(
                "// add\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=M+D\n"
            )
        
        def sub_():
            self.output_stream.write(
                "// sub\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=M-D\n"
            )

        def neg_():
            self.output_stream.write(
                "// neg\n"
                "@SP\n"
                "A=M-1\n"
                "M=-M\n"
            )

        def and_():
            self.output_stream.write(
                "// and\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=M&D\n"
            )

        def or_():
            self.output_stream.write(
                "// or\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=M|D\n"
            )

        def not_():
            self.output_stream.write(
                "// not\n"
                "@SP\n"
                "A=M-1\n"
                "M=!M\n"
            )

        def shiftleft_():
            self.output_stream.write(
                "// shiftleft\n"
                "@SP\n"
                "A=M-1\n"
                "M=<<M\n"
            )
        
        def shiftright_():
            self.output_stream.write(
                "// shiftright\n"
                "@SP\n"
                "A=M-1\n"
                "M=>>M\n"
            )

        def eq_():
            self.output_stream.write(
                "// eq\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "D=M-D\n"
                f"@PUSH_TRUE{self.counter}\n"
                "D;JEQ\n"
                "// False case\n"
                "@SP\n"
                "A=M-1\n"
                "M=0\n"
                f"@END{self.counter}\n"
                "0;JMP\n"
                f"(PUSH_TRUE{self.counter})\n"
                "@SP\n"
                "A=M-1\n"
                "M=-1\n"
                f"(END{self.counter})\n"
            )
            self.counter += 1

        def gt_():
            self.output_stream.write(
                "// gt\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "D=M-D\n"
                f"@PUSH_TRUE{self.counter}\n"
                "D;JGT\n"
                "// False case\n"
                "@SP\n"
                "A=M-1\n"
                "M=0\n"
                f"@END{self.counter}\n"
                "0;JMP\n"
                f"(PUSH_TRUE{self.counter})\n"
                "@SP\n"
                "A=M-1\n"
                "M=-1\n"
                f"(END{self.counter})\n"
            )
            self.counter += 1

        def lt_():
            self.output_stream.write(
                "// lt\n"
                "@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "D=M-D\n"
                f"@PUSH_TRUE{self.counter}\n"
                "D;JLT\n"
                "// False case\n"
                "@SP\n"
                "A=M-1\n"
                "M=0\n"
                f"@END{self.counter}\n"
                "0;JMP\n"
                f"(PUSH_TRUE{self.counter})\n"
                "@SP\n"
                "A=M-1\n"
                "M=-1\n"
                f"(END{self.counter})\n"
            )
            self.counter += 1

        if command == "add":
            add_()
        elif command == "sub":
            sub_()
        elif command == "neg":
            neg_()
        elif command == "and":
            and_()
        elif command == "or":
            or_()
        elif command == "not":
            not_()
        elif command == "shiftleft":
            shiftleft_()
        elif command == "shiftright":
            shiftright_()
        elif command == "eq":
            eq_()
        elif command == "gt":
            gt_()
        elif command == "lt":
            lt_()


    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        if command == "C_PUSH":
            if segment == "constant":
                self.output_stream.write(
                    "// push constant %s\n" % index +
                    "@%s\n" % index +
                    "D=A\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            elif segment == "local":
                self.output_stream.write(
                    "// push local %s\n" % index +
                    "@LCL\n"
                    "D=M\n"
                    "@%s\n" % index +
                    "A=D+A\n"
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            elif segment == "argument":
                self.output_stream.write(
                    "// push argument %s\n" % index +
                    "@ARG\n"
                    "D=M\n"
                    "@%s\n" % index +
                    "A=D+A\n"
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            elif segment == "this":
                self.output_stream.write(
                    "// push this %s\n" % index +
                    "@THIS\n"
                    "D=M\n"
                    "@%s\n" % index +
                    "A=D+A\n"
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            elif segment == "that":
                self.output_stream.write(
                    "// push that %s\n" % index +
                    "@THAT\n"
                    "D=M\n"
                    "@%s\n" % index +
                    "A=D+A\n"
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            elif segment == "static":
                self.output_stream.write(
                    "// push static %s\n" % index +
                    "@%s.%s\n" % (self.filename, index) +
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            elif segment == "temp":
                temp_location = 5 + index
                self.output_stream.write(
                    "// push temp %s\n" % index +
                    "@%s\n" % temp_location +
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            elif segment == "pointer":
                pointer_location = 3 + index
                self.output_stream.write(
                    "// push pointer %s\n" % index +
                    "@%s\n" % pointer_location +
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
        elif command == "C_POP":
            if segment == "local":
                self.output_stream.write(
                    "// pop local %s\n" % index +
                    "@%s\n" % index +
                    "D=A\n"
                    "@LCL\n"
                    "D=M+D\n"
                    "@R13\n"
                    "M=D\n"
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    "@R13\n"
                    "A=M\n"
                    "M=D\n"
                )
            elif segment == "argument":
                self.output_stream.write(
                    "// pop argument %s\n" % index +
                    "@%s\n" % index +
                    "D=A\n"
                    "@ARG\n"
                    "D=M+D\n"
                    "@R13\n"
                    "M=D\n"
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    "@R13\n"
                    "A=M\n"
                    "M=D\n"
                )
            elif segment == "this":
                self.output_stream.write(
                    "// pop this %s\n" % index +
                    "@%s\n" % index +
                    "D=A\n"
                    "@THIS\n"
                    "D=M+D\n"
                    "@R13\n"
                    "M=D\n"
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    "@R13\n"
                    "A=M\n"
                    "M=D\n"
                )
            elif segment == "that":
                self.output_stream.write(
                    "// pop that %s\n" % index +
                    "@%s\n" % index +
                    "D=A\n"
                    "@THAT\n"
                    "D=M+D\n"
                    "@R13\n"
                    "M=D\n"
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    "@R13\n"
                    "A=M\n"
                    "M=D\n"
                )
            elif segment == "static":
                self.output_stream.write(
                    "// pop static %s\n" % index +
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    "@%s.%s\n" % (self.filename, index) +
                    "M=D\n"
                )
            elif segment == "temp":
                temp_location = 5 + index
                self.output_stream.write(
                    "// pop temp %s\n" % index +
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    "@%s\n" % temp_location +
                    "M=D\n"
                )
            elif segment == "pointer":
                pointer_location = 3 + index
                self.output_stream.write(
                    "// pop pointer %s\n" % index +
                    "@SP\n"
                    "AM=M-1\n"
                    "D=M\n"
                    "@%s\n" % pointer_location +
                    "M=D\n"
                )
                

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass
