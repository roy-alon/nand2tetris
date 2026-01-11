// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE0
D;JEQ
// False case
@SP
A=M-1
M=0
@END0
0;JMP
(PUSH_TRUE0)
@SP
A=M-1
M=-1
(END0)
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE1
D;JEQ
// False case
@SP
A=M-1
M=0
@END1
0;JMP
(PUSH_TRUE1)
@SP
A=M-1
M=-1
(END1)
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE2
D;JEQ
// False case
@SP
A=M-1
M=0
@END2
0;JMP
(PUSH_TRUE2)
@SP
A=M-1
M=-1
(END2)
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE3
D;JLT
// False case
@SP
A=M-1
M=0
@END3
0;JMP
(PUSH_TRUE3)
@SP
A=M-1
M=-1
(END3)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE4
D;JLT
// False case
@SP
A=M-1
M=0
@END4
0;JMP
(PUSH_TRUE4)
@SP
A=M-1
M=-1
(END4)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE5
D;JLT
// False case
@SP
A=M-1
M=0
@END5
0;JMP
(PUSH_TRUE5)
@SP
A=M-1
M=-1
(END5)
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE6
D;JGT
// False case
@SP
A=M-1
M=0
@END6
0;JMP
(PUSH_TRUE6)
@SP
A=M-1
M=-1
(END6)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE7
D;JGT
// False case
@SP
A=M-1
M=0
@END7
0;JMP
(PUSH_TRUE7)
@SP
A=M-1
M=-1
(END7)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE8
D;JGT
// False case
@SP
A=M-1
M=0
@END8
0;JMP
(PUSH_TRUE8)
@SP
A=M-1
M=-1
(END8)
// push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
// push constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// neg
@SP
A=M-1
M=-M
// and
@SP
AM=M-1
D=M
A=A-1
M=M&D
// push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
// or
@SP
AM=M-1
D=M
A=A-1
M=M|D
// not
@SP
A=M-1
M=!M
