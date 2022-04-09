import argparse
from collections import Counter, defaultdict

from analyzer import JackTokenizer, CompilationEngine as XMLEngine

class SymbolTable:
  def __init__(self):
    self.reset()

  def reset(self):
    self.table = defaultdict(lambda: ('', 'NONE', -1))
    self.indices = Counter()

  def define(self, name, type, kind):
    self.table[name] = (type, kind, self.indices[kind])
    self.indices[kind] += 1

  def varCount(self, kind):
    return self.indices[kind]

  def kindOf(self, name):
    return self.table[name][1]

  def typeOf(self, name):
    return self.table[name][0]

  def indexOf(self, name):
    return self.table[name][2]

class VMWriter:
  def __init__(self, filename):
    self.f = open(filename, 'w')
    self.arithmetic = {
      '+': 'add',
      '-': 'sub',
      '*': 'call Math.multiply 2',
      '/': 'call Math.divide 2',
      '&': 'and',
      '|': 'or',
      '<': 'lt',
      '>': 'gt',
      '=': 'eq'
    }

  def write(self, text):
    self.f.write(f'{text}\n')

  def writePush(self, segment, index):
    self.write(f'push {segment} {index}')

  def writePop(self, segment, index):
    self.write(f'pop {segment} {index}')

  def writeArithmetic(self, command):
    self.write(self.arithmetic[command])

  def writeLabel(self, label):
    self.write(f'label {label}')

  def writeGoto(self, label):
    self.write(f'goto {label}')

  def writeIf(self, label):
    self.write(f'if-goto {label}')

  def writeCall(self, name, nArgs):
    self.write(f'call {name} {nArgs}')

  def writeFunction(self, name, nVars):
    self.write(f'function {name} {nVars}')

  def writeReturn(self):
    self.write('return')

  def close(self):
    self.f.close()

# Really should not be in python
class CompilationEngine:
  def __init__(self, filename):
    self.classSymbols = SymbolTable()
    self.subSymbols = SymbolTable()
    self.writer = VMWriter(filename.replace('.jack', '.vm'))
    self.analyzer = XMLEngine(filename)

  def compileClass(self):
    self.classSymbols.reset()
    json = self.analyzer.compileClass()
    className = json['class'][1]['identifier']
    for i in json['class']:
      print('class', i)
      if 'subroutineDec' in i:
        self.compileSubroutine(i['subroutineDec'], className)
      elif 'classVarDec' in i:
        self.compileClassVarDec(i['classVarDec'])

  def compileClassVarDec(self, varDec):
    # Attach to symbol table - field, static
    pass
    
  def compileSubroutine(self, subroutine, className):
    self.subSymbols.reset()
    subType = subroutine[0]['keyword']
    returnType = subroutine[1]['keyword']
    if subType == 'method':
      self.subSymbols.define('this', subroutine[2]['keyword'], 'argument')
    self.compileParameterList(subroutine[4]['parameterList'])
    for i in subroutine[6:]:
      if 'varDec' in i:
        self.compileVarDec(i['varDec'])
      if 'subroutineBody' in i:
        locals = self.subSymbols.varCount('local')
        self.writer.writeFunction(f'{className}.{subroutine[2]["identifier"]}', locals)
        if subType == 'method':
          self.writer.writePush('argument', 0)
          self.writer.writePop('pointer', 0)
        elif subType == 'constructor':
          'TODO'
        self.compileSubroutineBody(i['subroutineBody'])
        if returnType == 'void':
          'TODO'

  
  def compileParameterList(self, parameterList):
    # method int distance(Point other) {
    # this, Point, argument, 0
    # other, Point, argument, 1
    # Attach to symbol table - kind local
    pass

  def compileSubroutineBody(self, body):
    for i in body:
      # print('subbody', i)
      if 'statements' in i:
        self.compileStatements(i['statements'])
      elif 'varDec' in i:
        self.compileVarDec(i['varDec'])

  def compileVarDec(self, varDec):
    # Attach to symbol table
    pass
    
  def compileStatements(self, statements):
    for i in statements:
      # print('statements', i)
      if 'letStatement' in i:
        self.compileLet(i['letStatement'])
      elif 'ifStatement' in i:
        self.compileIf(i['ifStatement'])
      elif 'whileStatement' in i:
        self.compileWhile(i['whileStatement'])
      elif 'doStatement' in i:
        self.compileDo(i['doStatement'])
      elif 'returnStatement' in i:
        self.compileReturn(i['returnStatement'])

  def compileLet(self, let):
    for i in let:
      print('let', i)

  def compileIf(self, ifStatement):
    for i in ifStatement:
      print('if', i)

  def compileWhile(self, whileStatement):
    for i in whileStatement:
      print('while', i)

  def compileDo(self, do):
    call = do[1]
    method = f'{call[0]["identifier"]}.{call[2]["identifier"]}' if call[1].get('symbol') == '.' else call[0]['identifier']
    exprs = [x for x in call if 'expressionList' in x][0]
    size = self.compileExpressionList(exprs)
    self.writer.writeCall(method, size)

  def compileReturn(self, returnStatement):
    expression = returnStatement[1]
    if 'expression' in expression:
      self.compileExpression(expression['expression'])
    self.writer.writeReturn()

  def compileExpression(self, expr):
    symbol = None
    print('expr', expr)
    for i in expr:
      if 'symbol' in i:
        symbol = i['symbol']
      elif symbol:
        self.compileTerm(i['term'])
        self.writer.writeArithmetic(symbol)
        symbol = None
      else:
        self.compileTerm(i['term'])

  def compileTerm(self, term):
    print('term', term)
    if not isinstance(term, list):
      # TODO: handle variables
      self.push(term)
    elif term[0].get('symbol') == '(':
      self.compileExpression(term[1]['expression'])
    elif term[0].get('symbol'):
      self.compileTerm(term[1])
      self.writer.writeArithmetic(term[0]['symbol'])
    # TODO: function call
    # TODO: array
    
  def push(self, item):
    if 'varName' in item:
      variable = item['varName']
      if self.subSymbols.kindOf(variable):
        self.writer.writePush(self.subSymbols.kindOf(variable), self.subSymbols.indexOf(variable))
      else:
        self.writer.writePush(self.classSymbols.kindOf(variable), self.classSymbols.indexOf(variable))
    elif 'integerConstant' in item:
      self.writer.writePush('constant', item['integerConstant'])
    elif 'stringConstant' in item:
      'TODO: handle strings'
    # TODO: handle keyword constant?
    

  def compileExpressionList(self, exprs):
    for exp in exprs['expressionList']:
      self.compileExpression(exp['expression'])
    return len(exprs)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Compiler')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  compiler = CompilationEngine(args.filename)
  compiler.compileClass()

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