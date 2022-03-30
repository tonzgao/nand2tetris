from .analyzer import JackTokenizer

class SymbolTable:
  def __init__(self):
    self.table = {}

  def reset(self):
    self.table = {}

  def define(self, name, type, kind):
    pass

  def varCount(self, kind):
    pass

  def kindOf(self, name):
    return

  def typeOf(self, name):
    return

  def indexOf(self, name):
    return

class VMWriter:
  def __init__(self, filename):
    pass

  def writePush(self, segment, index):
    pass

  def writePop(self, segment, index):
    pass

  def writeArithmetic(self, command):
    pass

  def writeLabel(self, label):
    pass

  def writeGoto(self, label):
    pass

  def writeIf(self, label):
    pass

  def writeCall(self, name, nArgs):
    pass

  def writeFunction(self, name, nVars):
    pass

  def writeReturn(self):
    pass

  def close(self):
    pass

class CompilationEngine:
  def __init__(self, filename):
    pass

  def compileClass(self):
    pass

  def compileClassVarDec(self):
    pass

  def compileSubroutine(self):
    pass

  def compileParameterList(self):
    pass

  def compileVarDec(self): 
    pass

  def compileStatements(self):
    pass

  def compileLet(self):
    pass

  def compileIf(self):
    pass

  def compileWhile(self):
    pass

  def compileDo(self):
    pass

  def compileReturn(self):
    pass

  def compileExpression(self):
    pass

  def compileTerm(self):
    pass  

  def compileExpressionList(self):
    pass


# Seven : Tests how the compiler handles a simple program containing an
# arithmetic e?pression with integer constants, a do statement, and a return
# statement. Specifically, the program computes the e?pression and
# prints its value at the top left of the screen. To test whether your compiler
# has translated the program correctly, run the translated code in the VM
# emulator, and verify that it displays 7 correctly.
# ConvertToBin : Tests how the compiler handles all the procedural elements of
# the Jack language: e?pressions (without arrays or method calls), functions,
# and the statements if , while , do , let , and return . The program does not test the
# handling of methods, constructors, arrays, strings, static variables, and field
# variables. Specifically, the program gets a 16-bit decimal value from
# RAM[8000] , converts it to binary, and stores the individual bits in RAM[8001 …
# 8016] (each location will contain 0 or 1 ). Before the conversion starts, the
# program initiali?es RAM[8001 … 8016] to . To test whether your compiler has
# translated the program correctly, load the translated code into the VM
# emulator, and proceed as follows:
# Put (interactively, using the emulator’s GUI) some decimal value in
# RAM[8000] .
# Run the program for a few seconds, then stop its e?ecution.
# Check (by visual inspection) that memory locations RAM[8001 … 8016]
# contain the correct bits and that none of them contains .
# Square : Tests how the compiler handles the object-based features of the Jack
# language: constructors, methods, fields, and e?pressions that include
# method calls. Does not test the handling of static variables. Specifically, this
# multiclass program stages a simple interactive game that enables moving a
# black square around the screen using the keyboard’s four arrow keys.
# While moving, the si?e of the square can be increased and decreased by
# pressing the z and x keys, respectively. To quit the game, press the q key. To
# test whether your compiler has translated the program correctly, run the
# translated code in the VM emulator, and verify that the game works as
# e?pected.
# Average : Tests how the compiler handles arrays and strings. This is done by
# computing the average of a user-supplied sequence of integers. To test
# whether your compiler has translated the program correctly, run the
# translated code in the VM emulator, and follow the instructions displayed
# on the screen.
# Pong : A complete test of how the compiler handles an object-based
# application, including the handling of objects and static variables. In the
# classical Pong game, a ball is moving randomly, bouncing off the edges of
# the screen. The user tries to hit the ball with a small paddle that can be
# moved by pressing the keyboard’s left and right arrow keys. Each time the
# paddle hits the ball, the user scores a point and the paddle shrinks a little,
# making the game increasingly more challenging. If the user misses and the
# ball hits the bottom the game is over. To test whether your compiler has
# translated this program correctly, run the translated code in the VM
# emulator and play the game. Make sure to score some points to test the part
# of the program that displays the score on the screen.
# ComplexArrays : Tests how the compiler handles comple? array references
# and e?pressions. To that end, the program performs five comple?
# calculations using arrays. For each such calculation, the program prints on
# the screen the e?pected result along with the result computed by the
# compiled program. To test whether your compiler has translated the
# program correctly, run the translated code in the VM emulator, and make
# sure that the e?pected and actual results are identical.