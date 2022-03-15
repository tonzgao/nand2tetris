import argparse
from collections import defaultdict


# OP CODES
C_ARITHMETIC = 'C_ARITHMETIC'
C_PUSH = 'C_PUSH'
C_POP = 'C_POP'
C_LABEL = 'C_LABEL'
C_GOTO = 'C_GOTO'
C_IF = 'C_IF'
C_FUNCTION = 'C_FUNCTION'
C_RETURN = 'C_RETURN'
C_CALL = 'C_CALL'

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

class CodewWriter:
  def __init__(self, filename):
    self.filename = filename.strip('.asm')
    self.f = open(filename, 'w')
    self.counter = 0
    self.locations = {
      'local': 'LCL',
      'argument': 'ARG',
      'this': 'THIS',
      'that': 'THAT',
    }
    self.jumps = {
      'eq': 'JEQ',
      'gt': 'JGT',
      'lt': 'JLT',
    }
    self.operations = {
      'not': 'M=!M',
      'neg': 'M=-M',
    }
    self.operators = {
      'add': 'M=D+M',
      'sub': 'M=M-D',
      'and': 'M=D&M',
      'or': 'M=D|M',
    }
    self.increment = [
      '@SP',
      'M=M+1'
    ]
    self.access = [
      '@SP',
      'A=M',
    ]
    self.pop = [
      '@SP',
      'M=M-1',
      *self.access,
    ]

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

  def writePush(self, segment, index):
    address = self.getMemory(segment, index)
    if segment == 'constant':
      result = [
        f'@{address}', 
        'D=A',
        *self.access,
        'M=D',
        *self.increment,
      ]
    elif segment == 'temp':
      result = [
        f'@{address}', 
        'D=M',
        *self.access,
        'M=D',
        *self.increment,
      ]
    else:
      result = [
        f'@{address}',
        'D=M',
        f'@{index}',
        'D=D+A',
        'A=D',
        'D=M',
        *self.access,
        'M=D',
        *self.increment,
      ]
    self.write(result)

  def writePop(self, segment, index):
    address = self.getMemory(segment, index)
    if segment == 'temp':
      index = address
    result = [
      f'@{address}',
      'D=M',
      f'@{index}',
      'D=D+A',
      '@SP',
      'M=M-1',
      'A=M+1',
      'M=D',
      'A=A-1',
      'D=M',
      'A=A+1',
      'A=M',
      'M=D',
    ]
    self.write(result)

  def arithmetic(self, command):   
    pop_set =  [
      *self.pop,
      'D=M',
    ]
    label = f'{command}{self.counter}'
    if command in self.operations:
      return [
        *self.pop,
        self.operations[command],
        *self.increment,
      ]
    elif command in self.jumps:
      self.counter += 1
      return [
        *pop_set,
        *self.pop,
        'D=M-D',
        'M=-1',
        f'@{label}',
        f'D;{self.jumps[command]}',
        *self.access,
        'M=0',
        f'({label})',
        *self.increment,
      ]
    return [
      *pop_set,
      *self.pop,
      self.operators[command],
      *self.increment,
    ]

  def writeArithmetic(self, command):
    result = self.arithmetic(command)
    self.write(result)

  def close(self):
    self.write([
      '(END)',
      '@END',
      '0;JMP',
    ])
    self.f.close()

class Translator:
  def __init__(self, filename: str):
    self.parser = Parser(filename)
    self.writer = CodewWriter(filename.replace('.vm', '.asm'))

  def translate(self):
    while self.parser.hasMoreLines():
      self.parser.advance()
      self.writer.write([self.parser.comment])
      if self.parser.commandType() == C_ARITHMETIC:
        self.writer.writeArithmetic(self.parser.arg1())
      elif self.parser.commandType() == C_PUSH:
        self.writer.writePushPop(C_PUSH, self.parser.arg1(), self.parser.arg2())
      elif self.parser.commandType() == C_POP:
        self.writer.writePushPop(C_POP, self.parser.arg1(), self.parser.arg2())
    self.writer.close()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Translator')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  translator = Translator(args.filename)
  translator.translate()