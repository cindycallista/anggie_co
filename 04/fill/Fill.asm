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

(POLL)
@KBD
D=M
@WHITE
D;JEQ
@color
M=-1
@PAINT
0;JMP

(WHITE)
@color
M=0

(PAINT)
@SCREEN
D=A
@cursor
M=D
@8192
D=A
@remaining
M=D

(PAINT_LOOP)
@color
D=M
@cursor
A=M
M=D
@cursor
M=M+1
@remaining
MD=M-1
@PAINT_LOOP
D;JGT
@POLL
0;JMP
