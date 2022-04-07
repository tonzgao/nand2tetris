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

  def write(self, text):
    self.f.write(f'{text}\n')

  def writePush(self, segment, index):
    self.write(f'push {segment} {index}')

  def writePop(self, segment, index):
    self.write(f'pop {segment} {index}')

  def writeArithmetic(self, command):
    self.write(command)

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

class CompilationEngine:
  def __init__(self, filename):
    self.tokenizer = JackTokenizer(filename)
    self.writer = VMWriter(filename.replace('.jack', '.vm'))
    self.tokenizer.removeComments()

  def compileClass(self):
    declaration = self.tokenizer.next()
    className = self.tokenizer.next()
    opening = self.tokenizer.next()
    result = [
      declaration,
      className,
      opening,
    ]
    while (peek := self.tokenizer.peek()) != '}':
      if peek in ['field', 'static']:
        result.append(self.compileClassVarDec())
      elif peek in ['constructor', 'function', 'method']:
        result.append(self.compileSubroutine())
      else:
        raise Exception('Unexpected token: ', self.tokenizer.current(), result, peek)
    result.append(self.tokenizer.current())
    return {
      'class': result
    }

  def compileClassVarDec(self):
    declaration = self.tokenizer.next()
    type = self.tokenizer.next()
    name = self.tokenizer.next()
    symbol = self.tokenizer.next()
    result = [
      declaration,
      type,
      name,
      symbol,
    ]
    while self.tokenizer.token == ',':
      name = self.tokenizer.next()
      symbol = self.tokenizer.next()
      result += [
        name,
        symbol,
      ]
    return {
      'classVarDec': result
    }
    
  def compileSubroutine(self):
    declaration = self.tokenizer.next()
    returnType = self.tokenizer.next()
    name = self.tokenizer.next()
    popening = self.tokenizer.next()
    parameters = self.compileParameterList()
    result = [
      declaration,
      returnType,
      name,
      popening,
      parameters,
    ]
    subroutine = [self.tokenizer.next()]
    while self.tokenizer.peek() == 'var':
      subroutine.append(self.compileVarDec())
    statements = self.compileStatements()
    sclosing = self.tokenizer.next()
    subroutine += [statements, sclosing]
    result.append({
      'subroutineBody': subroutine
    })
    return {
      'subroutineDec': result
    }

  def compileParameterList(self):
    result = []
    while self.tokenizer.peek() != ')':
      result.append(self.tokenizer.next())
      result.append(self.tokenizer.next())
      symbol = self.tokenizer.next()
      if self.tokenizer.token != ',':
        return [
          {'parameterList': result},
          symbol
        ]
      result.append(symbol)
    return [
       {'parameterList': result},
      self.tokenizer.next()
    ]

  def compileVarDec(self):
    declaration = self.tokenizer.next()
    type = self.tokenizer.next()
    name = self.tokenizer.next()
    symbol = self.tokenizer.next()
    result = [
      declaration,
      type,
      name,
      symbol,
    ]
    while self.tokenizer.token == ',':
      name = self.tokenizer.next()
      symbol = self.tokenizer.next()
      result += [
        name,
        symbol,
      ]
    return {
      'varDec': result
    }
    
  def compileStatements(self):
    result = []
    while (peek := self.tokenizer.peek()) != '}':
      if peek == 'do':
        result.append(self.compileDo())
      elif peek == 'let':
        result.append(self.compileLet())
      elif peek == 'while':
        result.append(self.compileWhile())
      elif peek == 'if':
        result.append(self.compileIf())
      elif peek == 'return':
        result.append(self.compileReturn())
      else:
        raise Exception('Unexpected statement token: ', self.tokenizer.current(), peek)
    return {
      'statements': result
    }

  def compileExpressionListHelper(self):
    eopen = self.tokenizer.next()
    expressionList = self.compileExpressionList()
    eclose = self.tokenizer.next()
    return [eopen, expressionList, eclose]

  def compileSubroutineCallHelper(self, result):
    if self.tokenizer.peek() == '.':
      dot = self.tokenizer.next()
      call = self.tokenizer.next()
      result += [dot, call]
    result += self.compileExpressionListHelper()
    return result

  def compileSubroutineCall(self):
    name = self.tokenizer.next()
    result = [name]
    self.compileSubroutineCallHelper(result)
    return result


  def compileDo(self):
    do = self.tokenizer.next()
    subcall = self.compileSubroutineCall()
    semi = self.tokenizer.next()
    return {
      'doStatement': [
        do,
        subcall,
        semi,
      ]
    }


  def compileLet(self):
    let = self.tokenizer.next()
    name = self.tokenizer.next()
    result = [let, name]
    if self.tokenizer.peek() == '[':
      opening = self.tokenizer.next()
      expression = self.compileExpression()
      closing = self.tokenizer.next()
      result += [
        opening, expression, closing
      ]
    equals = self.tokenizer.next()
    expression = self.compileExpression()
    semi = self.tokenizer.next()
    result += [equals, expression, semi]
    return {
      'letStatement': result
    }


  def compileWhile(self):
    wdeclare = self.tokenizer.next()
    eopen = self.tokenizer.next()
    expression = self.compileExpression()
    eclose = self.tokenizer.next()
    sopen = self.tokenizer.next()
    statements = self.compileStatements()
    sclose = self.tokenizer.next()
    return {
      'whileStatement': [
        wdeclare,
        eopen,
        expression,
        eclose,
        sopen,
        statements,
        sclose
      ]
    }

  def compileReturn(self):
    result = [self.tokenizer.next()]
    if self.tokenizer.peek() != ';':
      expression = self.compileExpression()
      result.append(expression)
    return {
      'returnStatement': result + [self.tokenizer.next()] # Semi
    }
    

  def compileIf(self):
    ifdeclare = self.tokenizer.next()
    ifopen = self.tokenizer.next()
    ifexpr = self.compileExpression()
    ifclose = self.tokenizer.next()
    sopen = self.tokenizer.next()
    ifstatements = self.compileStatements()
    sclose = self.tokenizer.next()
    result = [
      ifdeclare,
      ifopen,
      ifexpr,
      ifclose,
      sopen,
      ifstatements,
      sclose
    ]
    if self.tokenizer.peek() == 'else':
      elsedeclare = self.tokenizer.next()
      elseopen = self.tokenizer.next()
      elsestatements = self.compileStatements()
      elseclose = self.tokenizer.next()
      result += [
        elsedeclare,
        elseopen,
        elsestatements,
        elseclose
      ]
    return {
      'ifStatement': result
    }

  def compileExpression(self):
    term = self.compileTerm()
    result = [term]
    while self.tokenizer.peek() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
      op = self.tokenizer.next()
      result += [op, self.compileTerm()]
    print('here', result)
    return {
      'expression': result
    }

  def compileTerm(self):
    term = self.tokenizer.next()
    if self.tokenizer.token == '(': # Expression
      expression = self.compileExpression()
      closing = self.tokenizer.next()
      return {
        'term': [
          term,
          expression,
          closing
        ]
      }
    elif self.tokenizer.token in ['-', '~']: # Unary operator
      actualTerm = self.compileTerm()
      return {
        'term': [term, actualTerm]
      }
    elif self.tokenizer.peek() == '[': 
      opening = self.tokenizer.next()
      expression = self.compileExpression()
      closing = self.tokenizer.next()
      return {
        'term': [
          term,
          opening,
          expression,
          closing
        ]
      }
    elif self.tokenizer.peek() in ['(', '.']:
      subcall = self.compileSubroutineCallHelper([])
      return {
        'term': [
          term,
          subcall,
        ]
      }
    return {
      'term': term
    }

  def compileExpressionList(self):
    if self.tokenizer.peek() == ')':
      return {'expressionList': []}
    result = [self.compileExpression()]
    while self.tokenizer.peek() == ',':
      result += [self.tokenizer.next(), self.compileExpression()]
    return {
      'expressionList': result
    }


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Compiler')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  compiler = CompilationEngine(args.filename)
  result = compiler.compileClass()
  # print(result)

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