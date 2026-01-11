// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

//Finding the Maximum of an array
D=0
@16383
D=D-A 
@max
M=D //setting max with minimum value
@0
D=A
@MaxIndex
M=D //setting MaxIndex to a default 0 value
@i
M=0
(FindMaxLoop)
@i
D=M //Grabbing the index to D
@R15 //arr.length
D=M-D // D is arr.length - i
@BreakMaxLoop
D;JLE // Breaks if arr.length - i <= 0 <=> arr.length <=i
@i
D=M //Grabbing the index to D
@R14
A=M+D //Grabbing the index to arr[i]
D=M // Grabbing arr[i] to D
@max
D=M-D // D holding max-arr[i]
@IndexIsBigger
D;JLT
@IncreaseIAndReiterate
0;JMP //No change needs to be made to max index and max
(IndexIsBigger)
@i
D=M //Grabbing the index to D
@R14
A=M+D //Grabbing the index to arr[i]
D=M // Grabbing arr[i] to D
@max
M=D //Setting max to the new index
@i
D=M
@MaxIndex
M=D //Setting the new index of the max item to i*/
(IncreaseIAndReiterate)
@i
M=M+1 //Increasing the index i to check the next one
@FindMaxLoop
0;JMP // Found that max>arr[i] nothing to do, running loop for i+1
(BreakMaxLoop)

//Finding the Minimum of an array
@16383
D=A
@min
M=D //setting min to it's maximum value
@0
D=A
@MinIndex
M=D //setting MaxIndex to a default 0 value
@i
M=0
(FindMinLoop)
@i
D=M //Grabbing the index to D
@R15 //arr.length
D=M-D // D is arr.length - i
@BreakMinLoop
D;JLE // Breaks if arr.length - i <= 0 <=> arr.length <=i
@i
D=M //Grabbing the index to D
@R14
A=M+D //Grabbing the index to arr[i]
D=M // Grabbing arr[i] to D
@min
D=M-D // D holding min-arr[i]
@IndexIsSmaller
D;JGT
@IncreaseIAndReiterateMin
0;JMP //No change needs to be made to max index and max
(IndexIsSmaller)
@i
D=M //Grabbing the index to D
@R14
A=M+D //Grabbing the index to arr[i]
D=M // Grabbing arr[i] to D
@min
M=D //Setting min to the new index
@i
D=M
@MinIndex
M=D //Setting the new index of the max item to i*/
(IncreaseIAndReiterateMin)
@i
M=M+1 //Increasing the index i to check the next one
@FindMinLoop
0;JMP // Found that max>arr[i] nothing to do, running loop for i+1
(BreakMinLoop)

//Swap MinIndex with MaxIndex
//Putting the minimun value in the arr[MaxIndex]
@R14
D=M
@MaxIndex
M=M+D //Max Index now points to arr[MaxIndex] and not only holding the Index
@min
D=M
@MaxIndex
A=M
M=D

//Putting the maximum value in the arr[MinIndex]
@R14
D=M
@MinIndex
M=M+D //Max Index now points to arr[MinIndex] and not only holding the Index
@max
D=M
@MinIndex
A=M
M=D
(End)
@End
0;JMP
