import argparse
import os
from collections import defaultdict

from builder import CodeBuilder

# OP CODES
C_ARITHMETIC = 'C_ARITHMETIC'
C_PUSH = 'C_PUSH'
C_POP = 'C_POP'
C_LABEL = 'C_LABEL'
C_GOTO = 'C_GOTO'
C_IF = 'C_IF'
C_FUNCTION = 'C_FUNCTION'
C_CALL = 'C_CALL'
C_RETURN = 'C_RETURN'

class Reader:
  def __init__(self, filename):
    self.filename = filename

  def read(self):
    with open(self.filename, 'r') as f:
      for line in f:
        if '//' in line:
          line = line.split('//')[0]
        line = line.strip()
        if not line:
          continue
        yield line

  def readlines(self):
    return list(self.read())

class Parser:
  def __init__(self, filename):
    self.line_number = 0
    self.reader = Reader(filename)
    self.lines = self.reader.readlines()
    self.symbols = defaultdict(lambda: C_ARITHMETIC, {
      'push': C_PUSH,
      'pop': C_POP,
      'label': C_LABEL,
      'goto': C_GOTO,
      'if-goto': C_IF,
      'function': C_FUNCTION,
      'call': C_CALL,
      'return': C_RETURN,
    })

  def hasMoreLines(self):
    return self.line_number < len(self.lines)

  def advance(self):
    self.line_number += 1

  @property
  def comment(self):
    return f'// {self.lines[self.line_number-1]}'

  @property
  def current_line(self):
    return self.lines[self.line_number-1].split(' ')

  def commandType(self):
    return self.symbols[self.current_line[0]]

  def arg1(self):
    if len(self.current_line) == 1:
      return self.current_line[0]
    return self.current_line[1]

  def arg2(self):
    return self.current_line[2]

class CodeWriter:
  def __init__(self, filename):
    self.setFileName(filename)
    self.builder = CodeBuilder()
    self.locations = {
      'local': 'LCL',
      'argument': 'ARG',
      'this': 'THIS',
      'that': 'THAT',
    }

  def bootstrap(self):
    result = self.builder.bootstrap()
    self.write(result)

  def getMemory(self, segment, index):
    if segment in self.locations:
      return self.locations[segment]
    if segment == 'pointer':
      return 'THIS' if index == '0' else 'THAT'
    if segment == 'temp':
      return f'{int(index)+5}'
    if segment == 'static':
      return f'{self.filename}.{index}'
    return index

  def write(self, commands):
    self.f.write('\n'.join(commands))
    self.f.write('\n')

  def writePushPop(self, command, segment, index):
    if command == C_PUSH:
      self.writePush(segment, index)
    else:
      self.writePop(segment, index)

  def push(self, segment, index):
    address = self.getMemory(segment, index)
    if segment == 'constant':
      return self.builder.push_constant(address)
    elif segment == 'temp' or segment == 'pointer':
      return self.builder.push_memory(address)
    return self.builder.push_memory(address, index)

  def writePush(self, segment, index):
    result = self.push(segment, index)
    self.write(result)

  def pop(self, segment, index):
    address = self.getMemory(segment, index)
    if segment == 'temp' or segment == 'pointer':
      return self.builder.pop_memory(address)
    return self.builder.pop_to_address(address, index)

  def writePop(self, segment, index):
    result = self.pop(segment, index)
    self.write(result)

  def writeArithmetic(self, command):
    result = self.builder.arithmetic(command)
    self.write(result)

  def setFileName(self, filename):
    filename = filename.replace('.vm', '.asm')
    if '.asm' not in filename:
      filename += '\\' + filename.split('\\')[-1] + '.asm'
    self.filename = filename
    self.f = open(self.filename, 'w')

  def writeLabel(self, label):
    result = self.builder.create_label(label)
    self.write(result)

  def writeGoto(self, label):
    result = self.builder.goto(label)
    self.write(result)

  def writeIf(self, label):
    result = self.builder.if_goto(label)
    self.write(result)

  def writeFunction(self, functionName, nVars):
    result = self.builder.function(functionName, nVars)
    self.write(result)

  def writeCall(self, functionName, nArgs):
    result = self.builder.call(functionName, nArgs)
    self.write(result)

  def writeReturn(self):
    result = self.builder.build_return()
    self.write(result)

  def close(self):
    self.write(self.builder.end())
    self.f.close()

class Translator:
  def __init__(self, filename: str):
    self.filename = filename
    self.parser = None
    self.writer = CodeWriter(filename)

  def translate(self):
    if self.filename.endswith('vm'):
      return self._translate(self.filename)

    self.writer.bootstrap()
    self.writer.close()

    files = [f for f in os.listdir(self.filename) if f.endswith('.vm')]
    for file in files:
      filename = os.path.join(self.filename, file)
      self._translate(filename)

  def _translate(self, filename: str):
    self.parser = Parser(filename)
    self.writer.setFileName(filename)
    while self.parser.hasMoreLines():
      self.parser.advance()
      self.writer.write([self.parser.comment])
      if self.parser.commandType() == C_ARITHMETIC:
        self.writer.writeArithmetic(self.parser.arg1())
      elif self.parser.commandType() == C_PUSH:
        self.writer.writePushPop(C_PUSH, self.parser.arg1(), self.parser.arg2())
      elif self.parser.commandType() == C_POP:
        self.writer.writePushPop(C_POP, self.parser.arg1(), self.parser.arg2())
      elif self.parser.commandType() == C_LABEL:
        self.writer.writeLabel(self.parser.arg1())
      elif self.parser.commandType() == C_GOTO:
        self.writer.writeGoto(self.parser.arg1())
      elif self.parser.commandType() == C_IF:
        self.writer.writeIf(self.parser.arg1())
      elif self.parser.commandType() == C_FUNCTION:
        self.writer.writeFunction(self.parser.arg1(), self.parser.arg2())
      elif self.parser.commandType() == C_CALL:
        self.writer.writeCall(self.parser.arg1(), self.parser.arg2())
      elif self.parser.commandType() == C_RETURN:
        self.writer.writeReturn()
    self.writer.close()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Translator')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  translator = Translator(args.filename)
  translator.translate()