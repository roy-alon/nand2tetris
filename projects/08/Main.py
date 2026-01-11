"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO, 
        filename: str, code_writer: CodeWriter) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
        filename (str): the filename without extension (for static variables and label scoping).
        code_writer (CodeWriter): the CodeWriter instance to use.
    """
    # Your code goes here!
    # It might be good to start with something like:
    # parser = Parser(input_file)
    # code_writer = CodeWriter(output_file)
    parser = Parser(input_file)
    code_writer.set_file_name(filename)
    while parser.has_more_commands():
        parser.advance()
        if parser.cur_com == '':
            break
        # Command can be a valid command, or a '' indicating no command found after last command
        if parser.command_type() == 'C_ARITHMETIC':
            code_writer.write_arithmetic(parser.arg1())
        elif parser.command_type() == 'C_PUSH' or parser.command_type() == 'C_POP':
            code_writer.write_push_pop(parser.command_type(), parser.arg1(), parser.arg2())
        elif parser.command_type() == 'C_LABEL':
            code_writer.write_label(parser.arg1())
        elif parser.command_type() == 'C_GOTO':
            code_writer.write_goto(parser.arg1())
        elif parser.command_type() == 'C_IF':
            code_writer.write_if(parser.arg1())
        elif parser.command_type() == 'C_FUNCTION':
            code_writer.write_function(parser.arg1(), parser.arg2())
        elif parser.command_type() == 'C_CALL':
            code_writer.write_call(parser.arg1(), parser.arg2())
        elif parser.command_type() == 'C_RETURN':
            code_writer.write_return()



if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        # Filter for .vm files only, then sort so Sys.vm comes first (if it exists)
        all_files = [os.path.join(argument_path, filename) 
                     for filename in os.listdir(argument_path)]
        files_to_translate = [f for f in all_files 
                             if os.path.splitext(f)[1].lower() == '.vm']
        files_to_translate.sort(key=lambda x: (os.path.basename(x) != 'Sys.vm', x))
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    
    # Check if any file contains Sys.init (requires bootstrap code)
    has_sys_init = False
    for input_path in files_to_translate:
        with open(input_path, 'r') as f:
            content = f.read()
            if 'function Sys.init' in content:
                has_sys_init = True
                break
    
    with open(output_path, 'w') as output_file:
        code_writer = CodeWriter(output_file)
        
        # Write bootstrap code if Sys.init exists
        if has_sys_init:
            code_writer.write_bootstrap()
        
        for input_path in files_to_translate:
            with open(input_path, 'r') as input_file:
                filename_without_ext, _ = os.path.splitext(os.path.basename(input_path))
                translate_file(input_file, output_file, filename_without_ext, code_writer)
