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
        self.current_function_name = ""  # Track the current function name for label scoping
        self.return_counter = 0  # Counter for unique return address labels
        self.bootstrap_written = False  # Track if bootstrap code has been written
    
    def write_bootstrap(self) -> None:
        """Writes bootstrap code that initializes the stack pointer to 256
        and calls Sys.init. This should be called once at the beginning of
        the output file for programs that require it (like FibonacciElement, StaticsTest).
        """
        if self.bootstrap_written:
            return
        
        # Bootstrap must set up the call frame for Sys.init
        # Push 5 values: return address (0, since Sys.init never returns), LCL, ARG, THIS, THAT
        # This sets up SP=261, LCL=261, ARG=256 as expected by the VM calling convention
        self.output_stream.write(
            "// Bootstrap code\n"
            "@256\n"
            "D=A\n"
            "@SP\n"
            "M=D\n"
            # Push return address (0, since Sys.init never returns)
            "@0\n"
            "D=A\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
            # Push LCL (save caller's LCL - will be 0 or undefined at bootstrap)
            "@LCL\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
            # Push ARG (save caller's ARG)
            "@ARG\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
            # Push THIS (save caller's THIS)
            "@THIS\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
            # Push THAT (save caller's THAT)
            "@THAT\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
            # ARG = SP - 5 - nArgs (nArgs = 0 for Sys.init)
            "@SP\n"
            "D=M\n"
            "@5\n"
            "D=D-A\n"
            "@ARG\n"
            "M=D\n"
            # LCL = SP (reposition LCL for callee)
            "@SP\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
            # goto Sys.init
            "@Sys.init\n"
            "0;JMP\n"
        )
        
        self.bootstrap_written = True
    
    def _get_label_scope(self) -> str:
        """Returns the scope prefix for labels. Uses function name if available, 
        otherwise falls back to filename (for early tests like BasicLoop).
        
        Returns:
            str: The scope prefix for labels (function_name or filename).
        """
        return self.current_function_name if self.current_function_name else self.filename

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
        # Reset current_function_name when starting a new file
        # (each file is independent, and labels without functions use filename)
        self.current_function_name = ""
        self.return_counter = 0

    

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
                "M=M<<1\n"
            )
        
        def shiftright_():
            self.output_stream.write(
                "// shiftright\n"
                "@SP\n"
                "A=M-1\n"
                "M=M>>1\n"
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
        scope = self._get_label_scope()
        self.output_stream.write(
            "// label %s\n" % label +
            "(%s$%s)\n" % (scope, label)
        )

    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # Labels are scoped to the current function: function_name$label
        scope = self._get_label_scope()
        self.output_stream.write(
            "// goto %s\n" % label +
            "@%s$%s\n" % (scope, label) +
            "0;JMP\n"
        )
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # if-goto: pop the top of stack, if it's not zero (true), jump to label
        # Labels are scoped to the current function: function_name$label
        scope = self._get_label_scope()
        self.output_stream.write(
            "// if-goto %s\n" % label +
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            "@%s$%s\n" % (scope, label) +
            "D;JNE\n"  # Jump if D != 0 (i.e., if condition is true)
        )
    
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
        # Update the current function name for label scoping
        self.current_function_name = function_name
        # Reset return address counter for this function
        self.return_counter = 0
        
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.output_stream.write(
            "// function %s %s\n" % (function_name, n_vars) +
            "(%s)\n" % function_name
        )
        
        # Initialize local variables to 0
        for i in range(n_vars):
            self.output_stream.write(
                "@SP\n"
                "A=M\n"
                "M=0\n"
                "@SP\n"
                "M=M+1\n"
            )
    
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
        # Generate unique return address label
        # If current_function_name is empty (shouldn't happen in valid VM code, but handle gracefully)
        if not self.current_function_name:
            # Use filename as fallback for return address scope
            scope = self.filename if self.filename else "global"
        else:
            scope = self.current_function_name
        return_label = "%s$ret.%d" % (scope, self.return_counter)
        self.return_counter += 1
        
        # push return_address
        self.output_stream.write(
            "// call %s %s\n" % (function_name, n_args) +
            "@%s\n" % return_label +
            "D=A\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )
        
        # push LCL (save caller's LCL)
        self.output_stream.write(
            "@LCL\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )
        
        # push ARG (save caller's ARG)
        self.output_stream.write(
            "@ARG\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )
        
        # push THIS (save caller's THIS)
        self.output_stream.write(
            "@THIS\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )
        
        # push THAT (save caller's THAT)
        self.output_stream.write(
            "@THAT\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )
        
        # ARG = SP - 5 - n_args (reposition ARG for callee)
        self.output_stream.write(
            "@SP\n"
            "D=M\n"
            "@%d\n" % (5 + n_args) +
            "D=D-A\n"
            "@ARG\n"
            "M=D\n"
        )
        
        # LCL = SP (reposition LCL for callee)
        self.output_stream.write(
            "@SP\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
        )
        
        # goto function_name
        self.output_stream.write(
            "@%s\n" % function_name +
            "0;JMP\n"
        )
        
        # (return_address) - inject return address label
        self.output_stream.write(
            "(%s)\n" % return_label
        )

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        self.output_stream.write("// return\n")

        # 1. FRAME = LCL (save LCL in R13)
        self.output_stream.write(
            "@LCL\n"
            "D=M\n"
            "@R13\n"  
            "M=D\n"
        )
        
        # 2. RET = *(FRAME-5) (save return address in R14)
        self.output_stream.write(
            "@R13\n"
            "D=M\n"
            "@5\n"
            "A=D-A\n"  
            "D=M\n"
            "@R14\n" 
            "M=D\n"
        )
        
        # 3. *ARG = pop() (put return value at ARG[0])
        self.output_stream.write(
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"  
            "@ARG\n"
            "A=M\n"
            "M=D\n" 
        )
        
        # 4. SP = ARG + 1 (restore SP for caller)
        self.output_stream.write(
            "@ARG\n"
            "D=M+1\n"
            "@SP\n"
            "M=D\n" 
        )
        
        # 5. THAT = *(FRAME-1) (Restore THAT, THIS, ARG, LCL)
        # THAT = *(FRAME-1)
        self.output_stream.write(
            "@R13\n"
            "D=M\n"
            "@1\n"
            "A=D-A\n"
            "D=M\n"
            "@THAT\n"
            "M=D\n"
        )
        
        # THIS = *(FRAME-2)
        self.output_stream.write(
            "@R13\n"
            "D=M\n"
            "@2\n"
            "A=D-A\n"
            "D=M\n"
            "@THIS\n"
            "M=D\n"
        )
        
        # ARG = *(FRAME-3)
        self.output_stream.write(
            "@R13\n"
            "D=M\n"
            "@3\n"
            "A=D-A\n"
            "D=M\n"
            "@ARG\n"
            "M=D\n"
        )
        
        # LCL = *(FRAME-4)
        self.output_stream.write(
            "@R13\n"
            "D=M\n"
            "@4\n"
            "A=D-A\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
        )
        
        # 6. goto RET (Jump to return address)
        self.output_stream.write(
            "@R14\n"
            "A=M\n"
            "0;JMP\n"
        )
