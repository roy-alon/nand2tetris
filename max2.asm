@R1
D=M        // D = R1
@R2
D=D-M      // D = R1 - R2
@R1_GREATER
D;JGT      // אם R1 > R2, קפוץ ל-R1_GREATER

// אחרת (R2 >= R1)
@R2
D=M
@R0
M=D
@END
0;JMP

(R1_GREATER)
// כאן R1 > R2
@R1
D=M
@R0
M=D

(END)
@END
0;JMP