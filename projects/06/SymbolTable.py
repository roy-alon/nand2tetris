"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

SYMBOL TABLE MODULE
===================
The SymbolTable class maintains a mapping between symbolic names and their
corresponding memory addresses. This is essential for the assembler because:

1. Predefined Symbols: R0-R15, SP, LCL, ARG, THIS, THAT, SCREEN, KBD
   These have fixed addresses defined by the Hack architecture.

2. Labels: User-defined labels like (LOOP) that mark locations in code.
   These are resolved to instruction addresses during pass 1.

3. Variables: User-defined variables like @counter that need RAM addresses.
   These are assigned addresses starting at 16 (after predefined symbols).

The symbol table is used during assembly to resolve all symbolic references
to their numeric addresses before generating binary code.
"""


class SymbolTable:
    """
    A symbol table that keeps a correspondence between symbolic labels and 
    numeric addresses.
    
    This table maps symbolic names (labels, variables, predefined symbols)
    to their corresponding memory addresses. It's used throughout the assembly
    process to resolve all symbolic references.
    """

    def __init__(self) -> None:
        """
        Initialize the symbol table with all predefined symbols.
        
        According to the Hack architecture specification, certain symbols
        have fixed addresses that are always available:
        
        - R0-R15: General-purpose registers (addresses 0-15)
        - SP, LCL, ARG, THIS, THAT: Virtual memory segments (addresses 0-4)
        - SCREEN: Screen memory map (address 16384)
        - KBD: Keyboard input register (address 24576)
        
        These are added to the table at initialization so they're always
        available during assembly.
        
        Returns:
            None: Populates self.__table with predefined symbols.
        """
        # Internal dictionary: symbol -> address
        self.__table = {}

        # R0 through R15 are registers at addresses 0-15
        for i in range(16):
            self.__table[f"R{i}"] = i

        # Predefined memory-mapped I/O and virtual segments
        self.__table["SCREEN"] = 16384  # Screen memory starts here
        self.__table["KBD"] = 24576     # Keyboard input register
        self.__table["SP"] = 0           # Stack pointer
        self.__table["LCL"] = 1          # Local segment pointer
        self.__table["ARG"] = 2          # Argument segment pointer
        self.__table["THIS"] = 3         # This segment pointer
        self.__table["THAT"] = 4         # That segment pointer

    def add_entry(self, symbol: str, address: int) -> None:
        """
        Add a new symbol-to-address mapping to the table.
        
        Used to add:
        - Labels: Maps label names to instruction addresses
        - Variables: Maps variable names to RAM addresses (starting at 16)
        
        If the symbol already exists, this will overwrite the previous mapping.
        This is intentional - labels should be defined before use.
        
        Args:
            symbol (str): The symbol name to add (e.g., "LOOP", "counter").
            address (int): The memory address associated with this symbol.
        
        Returns:
            None: Modifies self.__table.
        
        Example:
            add_entry("LOOP", 5)  # Label at instruction address 5
            add_entry("counter", 16)  # Variable at RAM address 16
        """
        self.__table[symbol] = address

    def contains(self, symbol: str) -> bool:
        """
        Check if a symbol exists in the symbol table.
        
        Used to determine if a symbol has already been defined (either as
        a predefined symbol, label, or variable). This helps avoid duplicate
        variable assignments and ensures labels are defined before use.
        
        Args:
            symbol (str): The symbol name to check (e.g., "LOOP", "R5").
        
        Returns:
            bool: True if the symbol exists in the table, False otherwise.
        
        Example:
            contains("R0") -> True (predefined)
            contains("LOOP") -> True if label was defined
            contains("newvar") -> False if not yet defined
        """
        if symbol in self.__table:
            return True
        return False

    def get_address(self, symbol: str) -> int:
        """
        Retrieve the address associated with a symbol.
        
        Should only be called if contains(symbol) returns True.
        Used to resolve symbolic references to their numeric addresses
        during code generation.
        
        Args:
            symbol (str): The symbol name to look up.
        
        Returns:
            int: The memory address associated with the symbol.
        
        Raises:
            KeyError: If the symbol is not in the table (should check contains() first).
        
        Example:
            get_address("R0") -> 0
            get_address("LOOP") -> 5 (if label was at instruction 5)
            get_address("counter") -> 16 (if variable was assigned address 16)
        """
        return self.__table[symbol]

    def __str__(self) -> str:
        """
        String representation of the symbol table (for debugging).
        
        Returns:
            str: A string representation of the entire symbol table dictionary.
        """
        return str(self.__table)