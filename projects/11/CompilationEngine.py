"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", symbol_table: "SymbolTable", vm_writer: "VMWriter", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output = output_stream
        self.symbol_table = symbol_table
        self.vm_writer = vm_writer
        self.current_class = None
        self.subroutine_type = None  # CONSTRUCTOR, FUNCTION, or METHOD
        self.label_counter = 0  # For generating unique labels

    def _escape_xml(self, token: str) -> str:
        """Escapes XML special characters (<, >, &, \")."""
        return token.replace("&", "&amp;") \
                    .replace("<", "&lt;") \
                    .replace(">", "&gt;") \
                    .replace('"', "&quot;")

    def compile_class(self) -> None:
        """Compiles a complete class.
        Grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        # Expect 'class' keyword
        if self.tokenizer.token_type() != "KEYWORD" or self.tokenizer.keyword() != "CLASS":
            raise ValueError(f"Expected 'class', got {self.tokenizer.current_token}")
        
        # self.output.write("<class>\n")
        # self.output.write(f"<keyword> class </keyword>\n")
        self.tokenizer.advance()
        
        # Expect className (identifier)
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected className, got {self.tokenizer.current_token}")
        # self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.current_class = self.tokenizer.identifier()
        self.tokenizer.advance()
        
        # Expect '{'
        if self.tokenizer.current_token != "{":
            raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
        #self.output.write(f"<symbol> {{ </symbol>\n")
        self.tokenizer.advance()
        
        # Parse classVarDec* (zero or more)
        while (self.tokenizer.token_type() == "KEYWORD" and 
               self.tokenizer.keyword() in ["STATIC", "FIELD"]):
            self.compile_class_var_dec()
        
        # Parse subroutineDec* (zero or more)
        while (self.tokenizer.token_type() == "KEYWORD" and 
               self.tokenizer.keyword() in ["CONSTRUCTOR", "FUNCTION", "METHOD"]):
            self.compile_subroutine()
        
        # Expect '}'
        if self.tokenizer.current_token != "}":
            raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
        #self.output.write(f"<symbol> }} </symbol>\n")
        self.tokenizer.advance()
        
        #self.output.write("</class>\n")
        

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration.
        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() in ["STATIC", "FIELD"]):
            return
        
        # Parse 'static' or 'field'
        kind = self.tokenizer.keyword()  # STATIC or FIELD
        self.tokenizer.advance()
        
        # Parse type
        var_type = self._parse_type()
        
        # Parse varName (',' varName)*
        while True:
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected identifier, got {self.tokenizer.current_token}")
            var_name = self.tokenizer.identifier()
            self.symbol_table.define(var_name, var_type, kind)
            self.tokenizer.advance()
            
            if self.tokenizer.current_token == ",":
                self.tokenizer.advance()
            else:
                break
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.tokenizer.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        Grammar: ('constructor' | 'function' | 'method') ('void' | type) 
                 subroutineName '(' parameterList ')' subroutineBody
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() in ["CONSTRUCTOR", "FUNCTION", "METHOD"]):
            return
    
        self.symbol_table.start_subroutine()
        
        # Parse 'constructor', 'function', or 'method'
        self.subroutine_type = self.tokenizer.keyword()  # CONSTRUCTOR, FUNCTION, or METHOD
        self.tokenizer.advance()
        
        # Parse return type ('void' or type)
        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "VOID":
            self.tokenizer.advance()
        else:
            self._parse_type()
        
        # Parse subroutineName (identifier)
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected subroutine name, got {self.tokenizer.current_token}")
        current_function = self.tokenizer.identifier()
        self.current_function_name = current_function  # Store for use in compile_subroutine_body
        self.tokenizer.advance()
        
        # Parse '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # For methods, add implicit 'this' as first argument
        if self.subroutine_type == "METHOD":
            self.symbol_table.define("this", self.current_class, "ARG")
        
        # Parse parameterList
        self.compile_parameter_list()
        
        # Parse ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
        self.tokenizer.advance()

        # Get local variable count (VAR) for function declaration
        # Note: must count VARs AFTER parsing var declarations in subroutine body
        # But we need to write function declaration before body
        # So we'll count VARs in the body and write function declaration there
        # Actually, we need to parse var declarations first, then write function
        # Let's do it in compile_subroutine_body instead
        
        # Parse subroutineBody (which will handle var declarations and function declaration)
        self.compile_subroutine_body()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        Grammar: ((type varName) (',' type varName)*)?
        """
        # Check if parameter list is empty
        if self.tokenizer.current_token == ")":
            return
        
        # Parse first parameter
        param_type = self._parse_type()
        
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected parameter name, got {self.tokenizer.current_token}")
        param_name = self.tokenizer.identifier()
        self.symbol_table.define(param_name, param_type, "ARG")
        self.tokenizer.advance()
        
        # Parse additional parameters
        while self.tokenizer.current_token == ",":
            self.tokenizer.advance()
            
            param_type = self._parse_type()
            
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected parameter name, got {self.tokenizer.current_token}")
            param_name = self.tokenizer.identifier()
            self.symbol_table.define(param_name, param_type, "ARG")
            self.tokenizer.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration.
        Grammar: 'var' type varName (',' varName)* ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "VAR"):
            return
        
        # Parse 'var' keyword
        self.tokenizer.advance()
        
        # Parse type
        var_type = self._parse_type()
        
        # Parse varName (',' varName)*
        while True:
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected identifier, got {self.tokenizer.current_token}")
            var_name = self.tokenizer.identifier()
            self.symbol_table.define(var_name, var_type, "VAR")
            self.tokenizer.advance()
            
            if self.tokenizer.current_token == ",":
                self.tokenizer.advance()
            else:
                break
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.tokenizer.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        Grammar: statement*
        """
        while (self.tokenizer.token_type() == "KEYWORD" and 
               self.tokenizer.keyword() in ["LET", "IF", "WHILE", "DO", "RETURN"]):
            if self.tokenizer.keyword() == "LET":
                self.compile_let()
            elif self.tokenizer.keyword() == "IF":
                self.compile_if()
            elif self.tokenizer.keyword() == "WHILE":
                self.compile_while()
            elif self.tokenizer.keyword() == "DO":
                self.compile_do()
            elif self.tokenizer.keyword() == "RETURN":
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement.
        Grammar: 'do' subroutineCall ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "DO"):
            return
        
        # 'do' keyword
        self.tokenizer.advance()
        
        # subroutineCall logic
        # Expect Identifier (className | varName | subroutineName)
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected identifier in do statement, got {self.tokenizer.current_token}")
        
        first_identifier = self.tokenizer.identifier()
        self.tokenizer.advance()
        
        # Check for '.' (method call like Game.run or obj.method)
        if self.tokenizer.current_token == ".":
            # External call: className.subroutineName or obj.subroutineName
            self.tokenizer.advance()
            
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected subroutine name after '.', got {self.tokenizer.current_token}")
            subroutine_name = self.tokenizer.identifier()
            self.tokenizer.advance()
            
            # Check if first identifier is a variable (method call on object)
            var_kind = self.symbol_table.kind_of(first_identifier)
            if var_kind is not None:
                # It's a method call: push the object (this)
                var_segment = self.symbol_table.kind_of(first_identifier)
                var_index = self.symbol_table.index_of(first_identifier)
                self.vm_writer.write_push(var_segment, var_index)
                # Get the type (class name) of the variable
                var_type = self.symbol_table.type_of(first_identifier)
                function_name = f"{var_type}.{subroutine_name}"
                n_args = 1  # We'll add 1 for the object
            else:
                # It's a class name, so it's a function call
                function_name = f"{first_identifier}.{subroutine_name}"
                n_args = 0
        else:
            # No dot: it's a method call on 'this' or a function call
            subroutine_name = first_identifier
            var_kind = self.symbol_table.kind_of(subroutine_name)
            if var_kind is not None:
                # It's a variable name, so this is invalid
                raise ValueError(f"Unexpected variable name in subroutine call: {subroutine_name}")
            # It's a method call on current class
            self.vm_writer.write_push("POINTER", 0)  # Push 'this'
            function_name = f"{self.current_class}.{subroutine_name}"
            n_args = 1
        
        # Expect '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Compile expression list
        expression_count = self.compile_expression_list()
        n_args += expression_count
        
        # Call the function/method
        self.vm_writer.write_call(function_name, n_args)
        
        # Pop return value (do statements discard return values)
        self.vm_writer.write_pop("TEMP", 0)
        
        # Expect ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
    
    def compile_let(self) -> None:
        """Compiles a let statement.
        Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "LET"):
            return
        
        self.tokenizer.advance()
        
        # Expect varName
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected variable name, got {self.tokenizer.current_token}")
        var_name = self.tokenizer.identifier()
        var_kind = self.symbol_table.kind_of(var_name)
        var_index = self.symbol_table.index_of(var_name)
        self.tokenizer.advance()
        
        is_array = False
        # Handle optional array subscript: '[' expression ']'
        if self.tokenizer.current_token == "[":
            is_array = True
            # Push array base address
            self.vm_writer.write_push(var_kind, var_index)
            self.tokenizer.advance()
            # Compile index expression
            self.compile_expression()
            if self.tokenizer.current_token != "]":
                raise ValueError(f"Expected ']', got {self.tokenizer.current_token}")
            self.tokenizer.advance()
            # Add base + index
            self.vm_writer.write_arithmetic("+")
        
        # Expect '='
        if self.tokenizer.current_token != "=":
            raise ValueError(f"Expected '=', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Compile expression
        self.compile_expression()
        
        # Store the value
        if is_array:
            # For arrays: address is on stack, value is on top
            # We need to swap: address should be below value
            # Store value in temp, pop address to THAT, then restore value
            self.vm_writer.write_pop("TEMP", 0)  # Save value
            self.vm_writer.write_pop("POINTER", 1)  # Set THAT to address
            self.vm_writer.write_push("TEMP", 0)  # Restore value
            self.vm_writer.write_pop("THAT", 0)  # Store value at THAT[0]
        else:
            # Regular variable assignment
            self.vm_writer.write_pop(var_kind, var_index)
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.tokenizer.advance()

    def compile_while(self) -> None:
        """Compiles a while statement.
        Grammar: 'while' '(' expression ')' '{' statements '}'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "WHILE"):
            return
        
        self.tokenizer.advance()
        
        # Generate unique labels
        label_start = f"WHILE_EXP{self.label_counter}"
        label_end = f"WHILE_END{self.label_counter}"
        self.label_counter += 1
        
        # Label for start of condition check
        self.vm_writer.write_label(label_start)
        
        # Expect '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Parse expression (condition)
        self.compile_expression()
        
        # Negate condition (if false, jump to end)
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(label_end)
        
        # Expect ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Expect '{'
        if self.tokenizer.current_token != "{":
            raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Parse statements
        self.compile_statements()
        
        # Jump back to condition check
        self.vm_writer.write_goto(label_start)
        
        # Expect '}'
        if self.tokenizer.current_token != "}":
            raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Label for end of while loop
        self.vm_writer.write_label(label_end)

    def compile_return(self) -> None:
        """Compiles a return statement.
        Grammar: 'return' expression? ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "RETURN"):
            return
        
        self.tokenizer.advance()
        
        # Parse optional expression
        if self.tokenizer.current_token != ";":
            # Has return value
            self.compile_expression()
        else:
            # No return value
            if self.subroutine_type == "CONSTRUCTOR":
                # Constructors must return 'this' (push pointer 0)
                self.vm_writer.write_push("POINTER", 0)
            else:
                # Void function, push 0
                self.vm_writer.write_push("CONST", 0)
        
        self.vm_writer.write_return()
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.tokenizer.advance()

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause.
        Grammar: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "IF"):
            return
        
        self.tokenizer.advance()
        
        # Generate unique labels
        label_else = f"IF_ELSE{self.label_counter}"
        label_end = f"IF_END{self.label_counter}"
        self.label_counter += 1
        
        # Expect '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Parse expression (condition)
        self.compile_expression()
        
        # Expect ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Negate condition (if false, jump to else or end)
        self.vm_writer.write_arithmetic("NOT")
        
        # Write conditional jump to else_label (we'll define it later)
        # If there's no else, else_label will be the same as end_label
        self.vm_writer.write_if(label_else)
        
        # Expect '{'
        if self.tokenizer.current_token != "{":
            raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Parse statements (if true) - only executed if condition was true
        self.compile_statements()
        
        # Expect '}'
        if self.tokenizer.current_token != "}":
            raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
        self.tokenizer.advance()
        
        # Now check if there's an else clause (AFTER parsing the if block)
        has_else = (self.tokenizer.token_type() == "KEYWORD" and 
                    self.tokenizer.keyword() == "ELSE")
        
        if has_else:
            # Jump to end after if block (to skip else block)
            self.vm_writer.write_goto(label_end)
            
            # Label for else block (jump here if condition was false)
            self.vm_writer.write_label(label_else)
            
            # Parse 'else'
            self.tokenizer.advance()
            
            # Expect '{'
            if self.tokenizer.current_token != "{":
                raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
            self.tokenizer.advance()
            
            # Parse statements (else block)
            self.compile_statements()
            
            # Expect '}'
            if self.tokenizer.current_token != "}":
                raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
            self.tokenizer.advance()
        else:
            # No else clause - else_label should point to end_label
            # So we just define else_label = end_label (same location)
            self.vm_writer.write_label(label_else)
        
        # Label for end of if statement
        self.vm_writer.write_label(label_end)
                            

    def compile_expression(self) -> None:
        """Compiles an expression.
        Grammar: term (op term)*
        """
        # Check if we have content for an expression
        if self.tokenizer.current_token in [';', ']', ')', ',']:
            return
        
        #self.output.write("<expression>\n")
        
        # Parse first term
        self.compile_term()
        
        # Parse (op term)* - zero or more operators followed by terms
        while (self.tokenizer.token_type() == "SYMBOL" and 
               self.tokenizer.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]):
            # ESCAPE XML HERE
            symbol = self.tokenizer.symbol()
            #self.output.write(f"<symbol> {self._escape_xml(self.tokenizer.symbol())} </symbol>\n")
            self.tokenizer.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(symbol)
        
        #self.output.write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term.
        Grammar: integerConstant | stringConstant | keywordConstant | varName | 
                 varName '[' expression ']' | subroutineCall | 
                 '(' expression ')' | unaryOp term
        """
        # Handle unary operators: unaryOp term
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ["-", "~"]:
            symbol = self.tokenizer.symbol()
            self.tokenizer.advance()
            # Recursively compile the term after unary operator
            self.compile_term()
            # Apply unary operator
            if symbol == "-":
                self.vm_writer.write_arithmetic("NEG")
            elif symbol == "~":
                self.vm_writer.write_arithmetic("NOT")
            return
        
        # Handle parenthesized expression: '(' expression ')'
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.tokenizer.advance()
            self.compile_expression()
            if self.tokenizer.current_token != ")":
                raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
            self.tokenizer.advance()
            return
        
        # Handle integer constant
        if self.tokenizer.token_type() == "INT_CONST":
            self.vm_writer.write_push("CONST", self.tokenizer.int_val())
            self.tokenizer.advance()
            return
        
        # Handle string constant
        if self.tokenizer.token_type() == "STRING_CONST":
            # String constants: call String.new(length) and append characters
            string_val = self.tokenizer.string_val()
            string_length = len(string_val)
            # Call String.new(length)
            self.vm_writer.write_push("CONST", string_length)
            self.vm_writer.write_call("String.new", 1)
            # Append each character
            for char in string_val:
                self.vm_writer.write_push("CONST", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)
            self.tokenizer.advance()
            return
        
        # Handle keyword constant (true, false, null, this)
        if self.tokenizer.token_type() == "KEYWORD":
            keyword = self.tokenizer.keyword().lower()
            if keyword == "true":
                self.vm_writer.write_push("CONST", 0)
                self.vm_writer.write_arithmetic("NOT")  # true = not false
            elif keyword == "false" or keyword == "null":
                self.vm_writer.write_push("CONST", 0)
            elif keyword == "this":
                self.vm_writer.write_push("POINTER", 0)  # Push 'this' pointer
            else:
                raise ValueError(f"Unexpected keyword: {keyword}")
            self.tokenizer.advance()
            return
        
        # Handle identifier: varName, varName '[' expression ']', or subroutineCall
        if self.tokenizer.token_type() == "IDENTIFIER":
            first_identifier = self.tokenizer.identifier()
            self.tokenizer.advance()
            
            # Check what comes after the identifier
            if self.tokenizer.current_token == "[":
                # Array subscript: varName '[' expression ']'
                var_kind = self.symbol_table.kind_of(first_identifier)
                var_index = self.symbol_table.index_of(first_identifier)
                # Push array base address
                self.vm_writer.write_push(var_kind, var_index)
                self.tokenizer.advance()
                # Compile index expression
                self.compile_expression()
                if self.tokenizer.current_token != "]":
                    raise ValueError(f"Expected ']', got {self.tokenizer.current_token}")
                self.tokenizer.advance()
                # Add base + index
                self.vm_writer.write_arithmetic("+")
                # Load value at address using THAT pointer
                self.vm_writer.write_pop("POINTER", 1)  # Set THAT to address
                self.vm_writer.write_push("THAT", 0)  # Push value at THAT[0]
                return
            
            elif self.tokenizer.current_token == "." or self.tokenizer.current_token == "(":
                # Subroutine call
                if self.tokenizer.current_token == ".":
                    # External call: className.subroutineName or obj.subroutineName
                    self.tokenizer.advance()
                    if self.tokenizer.token_type() != "IDENTIFIER":
                        raise ValueError(f"Expected subroutine name, got {self.tokenizer.current_token}")
                    subroutine_name = self.tokenizer.identifier()
                    self.tokenizer.advance()
                    
                    # Check if first identifier is a variable (method call on object)
                    var_kind = self.symbol_table.kind_of(first_identifier)
                    if var_kind is not None:
                        # It's a method call: push the object (this)
                        var_index = self.symbol_table.index_of(first_identifier)
                        self.vm_writer.write_push(var_kind, var_index)
                        # Get the type (class name) of the variable
                        var_type = self.symbol_table.type_of(first_identifier)
                        function_name = f"{var_type}.{subroutine_name}"
                        n_args = 1  # We'll add 1 for the object
                    else:
                        # It's a class name, so it's a function call
                        function_name = f"{first_identifier}.{subroutine_name}"
                        n_args = 0
                else:
                    # No dot: it's a method call on 'this' or a function call
                    subroutine_name = first_identifier
                    var_kind = self.symbol_table.kind_of(subroutine_name)
                    if var_kind is not None:
                        # It's a variable name, so this is invalid
                        raise ValueError(f"Unexpected variable name in subroutine call: {subroutine_name}")
                    # It's a method call on current class
                    self.vm_writer.write_push("POINTER", 0)  # Push 'this'
                    function_name = f"{self.current_class}.{subroutine_name}"
                    n_args = 1
                
                # Expect '('
                if self.tokenizer.current_token != "(":
                    raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
                self.tokenizer.advance()
                
                # Compile expression list
                expression_count = self.compile_expression_list()
                n_args += expression_count
                
                # Call the function/method
                self.vm_writer.write_call(function_name, n_args)
                
                if self.tokenizer.current_token != ")":
                    raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
                self.tokenizer.advance()
                return
            else:
                # Simple variable access
                var_kind = self.symbol_table.kind_of(first_identifier)
                var_index = self.symbol_table.index_of(first_identifier)
                if var_kind is None:
                    # Could be a function call inside current class without 'this' or parentheses
                    # But the grammar says subroutineCall always has '('
                    # So this must be a variable access
                    raise ValueError(f"Undefined variable: {first_identifier}")
                self.vm_writer.write_push(var_kind, var_index)
                return
        
        raise ValueError(f"Expected term, got {self.tokenizer.current_token}")
    
    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions.
        Grammar: (expression (',' expression)* )?
        Returns the number of expressions compiled.
        """
        # Check if empty
        if self.tokenizer.current_token == ")":
            return 0
        
        expression_count = 0
        # Parse first expression
        self.compile_expression()
        expression_count += 1
        
        # Parse additional expressions
        while self.tokenizer.current_token == ",":
            self.tokenizer.advance()
            self.compile_expression()
            expression_count += 1
        
        return expression_count

    def compile_subroutine_body(self) -> None:
        """Compiles a subroutine body.
        Grammar: '{' varDec* statements '}'
        """
        if self.tokenizer.current_token != "{":
            raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
        
        self.tokenizer.advance()
        
        # Parse varDec* (zero or more) - must be done before function declaration
        while (self.tokenizer.token_type() == "KEYWORD" and 
               self.tokenizer.keyword() == "VAR"):
            self.compile_var_dec()
        
        # Now write the function declaration with correct local count
        n_locals = self.symbol_table.var_count("VAR")
        function_name = f"{self.current_class}.{self.current_function_name}"
        self.vm_writer.write_function(function_name, n_locals)
        
        # Handle constructor: allocate memory for object
        if self.subroutine_type == "CONSTRUCTOR":
            n_fields = self.symbol_table.var_count("FIELD")
            self.vm_writer.write_push("CONST", n_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)  # Set 'this' to point to allocated memory
        
        # Handle method: set 'this' pointer
        elif self.subroutine_type == "METHOD":
            self.vm_writer.write_push("ARG", 0)  # First argument is 'this'
            self.vm_writer.write_pop("POINTER", 0)  # Set 'this' pointer
        
        # Parse statements
        self.compile_statements()
        
        # Parse '}'
        if self.tokenizer.current_token != "}":
            raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
        self.tokenizer.advance()

    def _parse_type(self) -> str:
        """Helper method to parse a type (int | char | boolean | className).
        Returns the type as a string.
        """
        if self.tokenizer.token_type() == "KEYWORD" and \
           self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"]:
            var_type = self.tokenizer.keyword().lower()
            self.tokenizer.advance()
            return var_type
        elif self.tokenizer.token_type() == "IDENTIFIER":
            var_type = self.tokenizer.identifier()
            self.tokenizer.advance()
            return var_type
        else:
            raise ValueError(f"Expected type, got {self.tokenizer.current_token}")