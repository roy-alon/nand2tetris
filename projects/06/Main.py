"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

MAIN ASSEMBLER MODULE
=====================
This is the main orchestrator for the Hack assembler. It coordinates the
two-pass assembly process:

Pass 1: Symbol Resolution
  - Process labels: Find all (LABEL) declarations and map them to instruction addresses
  - Process variables: Find all @symbol references and assign RAM addresses

Pass 2: Code Generation
  - Convert A-commands (@address) to 16-bit binary
  - Convert C-commands (dest=comp;jump) to 16-bit binary
  - Skip L-commands (they were removed in pass 1)

The assembly process follows this order because:
1. Labels must be processed first to know instruction addresses
2. Variables need labels resolved to avoid conflicts
3. Commands can only be converted after all symbols are resolved
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """
    Main assembly function that converts Hack assembly (.asm) to binary (.hack).
    
    This function orchestrates the two-pass assembly process:
    1. First pass: Resolve all symbols (labels and variables)
    2. Second pass: Generate binary code for each instruction
    
    Args:
        input_file (typing.TextIO): The input .asm file to assemble.
        output_file (typing.TextIO): The output .hack file where binary code is written.
    
    Returns:
        None: Writes binary output directly to output_file.
    
    Process Flow:
        1. Create parser and remove whitespace/comments
        2. Process labels: Map (LABEL) to instruction addresses
        3. Process variables: Map @symbol to RAM addresses (starting at 16)
        4. Process commands: Convert to 16-bit binary instructions
        5. Write all binary lines to output file
    """
    # Initialize parser with input file and clean up whitespace/comments
    parser = Parser(input_file)
    parser.delete_whitespaces()
    
    # Create symbol table with predefined symbols (R0-R15, SP, LCL, etc.)
    table = SymbolTable()
    
    # List to store final binary commands
    binary_commands = []
    
    # PASS 1: Process Labels
    # Labels like (LOOP) must be processed first because they reference
    # instruction addresses. We need to know where each instruction will be
    # before we can resolve jump targets.
    proccess_labels(parser, table)
    
    # PASS 1: Process Variables
    # Variables like @counter need RAM addresses assigned. We start at address 16
    # (after R0-R15) and increment for each new variable. If a symbol already
    # exists in the table (from labels or predefined), we use that address.
    proccess_variables(parser, table)
    
    # PASS 2: Process Commands
    # Now that all symbols are resolved, convert each instruction to binary:
    # - A-commands: @address -> 0 + 15-bit binary address
    # - C-commands: dest=comp;jump -> 111 + comp(7) + dest(3) + jump(3)
    binary_commands = proccess_commands(parser, table, binary_commands)

    # Write all binary commands to output file, one per line
    output_file.write("\n".join(binary_commands))

def proccess_labels(parser: Parser, table: SymbolTable) -> None:
    """
    First pass: Process label declarations and map them to instruction addresses.
    
    Labels are pseudo-commands of the form (LABEL) that mark a location in code.
    They don't generate binary code themselves, but they define a symbol that
    can be used in jump instructions (e.g., @LOOP followed by 0;JMP).
    
    Strategy:
    - Iterate through all commands
    - When we find (LABEL), extract the label name
    - Remove the label line from the code (it's not an instruction)
    - Map the label to the address of the NEXT instruction
    - This way, jumps to (LOOP) will point to the instruction after the label
    
    Args:
        parser (Parser): The parser containing the assembly code lines.
        table (SymbolTable): The symbol table to store label-to-address mappings.
    
    Returns:
        None: Modifies parser.input_lines_proccessed (removes labels) and
              table (adds label entries).
    
    Example:
        Input:  ["@5", "(LOOP)", "D=M", "@LOOP", "0;JMP"]
        After:  ["@5", "D=M", "@LOOP", "0;JMP"]
        Table:  {"LOOP": 1}  (points to "D=M" which is at index 1)
    """
    # Reset parser to start from beginning
    parser.reset_index()
    
    # Iterate through all commands
    while(parser.has_more_commands()):
        parser.advance()
        
        # Check if current command is a label declaration
        if parser.command_type() == "L_COMMAND":
            # Extract label name (e.g., "LOOP" from "(LOOP)")
            symbol = parser.symbol()
            
            # Remove the label line and get the index of the next instruction
            # This index becomes the address the label points to
            next_line_index = parser.pop_label()
            
            # Add label to symbol table with its target address
            table.add_entry(symbol, next_line_index)

def proccess_variables(parser: Parser, table: SymbolTable) -> None:
    """
    First pass: Process variable references and assign RAM addresses.
    
    Variables are symbols in A-commands that aren't numbers or predefined symbols.
    Examples: @counter, @sum, @i
    
    Strategy:
    - Iterate through all A-commands
    - If symbol is a number (e.g., @5), leave it as-is (direct address)
    - If symbol exists in table (label or predefined), replace with its address
    - If symbol is new, assign next available RAM address (starting at 16)
    - Replace @symbol with @address in the code
    
    RAM Address Allocation:
    - Addresses 0-15: Predefined (R0-R15, SP, LCL, ARG, THIS, THAT)
    - Addresses 16+: User variables (assigned sequentially)
    
    Args:
        parser (Parser): The parser containing the assembly code lines.
        table (SymbolTable): The symbol table to check/update with variable mappings.
    
    Returns:
        None: Modifies parser.input_lines_proccessed (replaces @symbol with @address).
    
    Example:
        Input:  ["@counter", "@5", "@LOOP", "@sum"]
        After:  ["@16", "@5", "@1", "@17"]  (assuming LOOP was at address 1)
        Table:  {"counter": 16, "sum": 17}
    """
    # Reset parser to start from beginning
    parser.reset_index()
    
    # Iterate through all commands
    while(parser.has_more_commands()):
        parser.advance()
        
        # Only process A-commands (they contain addresses/symbols)
        if parser.command_type() == "A_COMMAND":
            symbol = parser.symbol()
            
            # If it's already a number, it's a direct address - no processing needed
            if symbol.isdigit():
                continue
            
            # If symbol exists in table (from labels or predefined symbols),
            # replace @symbol with @address
            elif table.contains(symbol):
                address = table.get_address(symbol)
                parser.replace_symbol(address)
            
            # New variable: assign next available RAM address (starting at 16)
            else:
                new_variable = parser.add_variable()
                table.add_entry(symbol, new_variable)
                parser.replace_symbol(new_variable)

def proccess_commands(parser: Parser, table: SymbolTable, binary_commands: list) -> list:
    """
    Second pass: Convert assembly instructions to 16-bit binary machine code.
    
    At this point, all symbols have been resolved:
    - Labels have been removed and mapped to addresses
    - Variables have been replaced with numeric addresses
    - A-commands now only contain numeric addresses
    
    Conversion Rules:
    - A-command: @address -> 0 + 15-bit binary address
    - C-command: dest=comp;jump -> 111 + comp(7 bits) + dest(3 bits) + jump(3 bits)
    - L-command: Already removed in pass 1, skip if encountered
    
    Extended C-commands (shift operations):
    - Operations like A<<, D>> use special encoding
    - Detected by checking for >> or << in comp field
    
    Args:
        parser (Parser): The parser containing processed assembly code (symbols resolved).
        table (SymbolTable): Symbol table (not used here, but kept for consistency).
        binary_commands (list): List to accumulate binary output strings.
    
    Returns:
        list: List of 16-bit binary strings, one per instruction.
    
    Example:
        Input:  ["@5", "D=M", "D;JGT"]
        Output: ["0000000000000101", "1111110000010000", "1110001100000001"]
    """
    # Reset parser to start from beginning
    parser.reset_index()
    
    # At this point, parser.input_lines_proccessed contains only:
    # - A-commands with numeric addresses (e.g., "@5", "@16")
    # - C-commands (e.g., "D=M", "D;JGT")
    # - No L-commands (they were removed in pass 1)
    
    while(parser.has_more_commands()):
        parser.advance()
        
        # A-command: @address -> 0 + 15-bit binary
        if parser.command_type() == "A_COMMAND":
            # Get the numeric address (already resolved from symbol)
            address_str = parser.symbol()
            # Convert to binary: "0" prefix + 15-bit address
            binary_commands.append("0" + to_binary(address_str))
        
        # C-command: dest=comp;jump -> 111 + comp + dest + jump
        elif parser.command_type() == "C_COMMAND":
            # Parse comp field and check if it's an extended operation (shift)
            is_extended, comp = parser.comp()
            
            if is_extended:
                # Extended C-command: shift operations (A<<, D>>, etc.)
                # Format: 101 + comp(7 bits) + dest(3 bits) + jump(3 bits)
                binary_commands.append(
                    Code.extend_c(comp) + 
                    Code.dest(parser.dest()) + 
                    Code.jump(parser.jump())
                )
            else:
                # Standard C-command: arithmetic/logical operations
                # Format: 111 + comp(7 bits) + dest(3 bits) + jump(3 bits)
                binary_commands.append(
                    "111" + 
                    Code.comp(comp) + 
                    Code.dest(parser.dest()) + 
                    Code.jump(parser.jump())
                )
    
    return binary_commands


def to_binary(symbol: str) -> str:
    """
    Convert a decimal number string to 15-bit binary string with leading zeros.
    
    This is used for A-commands to convert addresses to binary.
    The result is always 15 bits (padded with zeros on the left).
    
    Args:
        symbol (str): A string representation of a decimal number (e.g., "5", "16").
    
    Returns:
        str: 15-bit binary string (e.g., "000000000000101" for "5").
    
    Example:
        to_binary("5") -> "000000000000101"
        to_binary("16") -> "000000000010000"
    """
    return bin(int(symbol))[2:].zfill(15)



if "__main__" == __name__:
    """
    Main entry point for the assembler.
    
    Usage: python Main.py <input_path>
    
    The input_path can be:
    - A single .asm file: assembles that file
    - A directory: assembles all .asm files in that directory
    
    For each .asm file, creates a corresponding .hack file with binary output.
    """
    # Validate command-line arguments
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    
    # Get absolute path of input (file or directory)
    argument_path = os.path.abspath(sys.argv[1])
    
    # If it's a directory, get all files in it
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        # Single file
        files_to_assemble = [argument_path]
    
    # Process each file
    for input_path in files_to_assemble:
        # Extract filename and extension
        filename, extension = os.path.splitext(input_path)
        
        # Only process .asm files
        if extension.lower() != ".asm":
            continue
        
        # Create output filename (same name, .hack extension)
        output_path = filename + ".hack"
        
        # Open input and output files, assemble, and close automatically
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
