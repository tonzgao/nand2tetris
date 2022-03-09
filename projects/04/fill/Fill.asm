// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(START)
@SCREEN
D = A
@CURRENT
M = D

(LOOP)
// Branch based on keyboard value
@KBD 
D = M
@color
M = D
@WRITE
D;JEQ // White
@color
M = -1 // Black

(WRITE)
// Write to screen
@color
D = M
@CURRENT
A = M
M = D

// Increment pointer
@CURRENT
M = M + 1
// Check if screen is filled
D = M
@KBD
D = D - A
@START
D;JGT

@LOOP
0;JMP

(END)
@END
0;JMP