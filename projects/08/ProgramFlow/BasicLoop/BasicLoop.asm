// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 0
@LCL
D=M
@SP
M=M-1
A=M+1
M=D
A=A-1
D=M
A=A+1
A=M
M=D
// label LOOP_START
(LOOP_START)
// push argument 0
@ARG
D=M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push local 0
@LCL
D=M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
M=D+M
@SP
M=M+1
// pop local 0
@LCL
D=M
@SP
M=M-1
A=M+1
M=D
A=A-1
D=M
A=A+1
A=M
M=D
// push argument 0
@ARG
D=M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
M=M-D
@SP
M=M+1
// pop argument 0
@ARG
D=M
@SP
M=M-1
A=M+1
M=D
A=A-1
D=M
A=A+1
A=M
M=D
// push argument 0
@ARG
D=M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
// if-goto LOOP_START
@SP
M=M-1
@SP
A=M
D=M
@LOOP_START
D;JNE
// push local 0
@LCL
D=M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
(END)
@END
0;JMP
