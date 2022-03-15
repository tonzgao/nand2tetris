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

class CodeBuilder:
  def __init__(self):
    self.counter = 0
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

  def _incr_stack_addr(self):
    return [
      '@SP',
      'M=M+1'
    ]
  def _decr_stack_addr(self):
    return [
      '@SP',
      'M=M-1',
    ]
  def _get_stack_addr(self):
    return [
      '@SP',
      'A=M',
    ]
  def _pop_no_set(self):
    return [
      *self._decr_stack_addr(),
      *self._get_stack_addr(),
    ]
  def _pop(self):
    return [
      *self._pop_no_set(),
      'D=M',
    ]
  def _push_stack(self):
    return [
      *self._get_stack_addr(),
      'M=D',
      *self._incr_stack_addr(),
    ]
  def _access_value(self, address, index=None):
    if not index:
      return [
        f'@{address}',
        'D=M',
      ]
    return [
      *self._get_address(address, index),
      'A=D',
      'D=M',
    ]
  def _get_address(self, base, offset='0'):
    result = self._access_value(base)
    if offset == '0':
      return result
    return [
      *result,
      f'@{offset}',
      'D=D+A',
    ]

  def push_constant(self, constant):
    return [
      f'@{constant}', 
      'D=A',
      *self._push_stack()
    ]
  def push_memory(self, address, index=None):
    return [
      *self._access_value(address, index),
      *self._push_stack(),
    ]
  def pop_to_address(self, base, offset):
    return [
      *self._get_address(base, offset),
      *self._decr_stack_addr(),
      'A=M+1',
      'M=D',
      'A=A-1',
      'D=M',
      'A=A+1',
      'A=M',
      'M=D',
    ]
  def arithmetic(self, command):   
    label = f'{command}{self.counter}'
    if command in self.operations:
      return [
        *self._pop_no_set(),
        self.operations[command],
        *self._incr_stack_addr(),
      ]
    elif command in self.jumps:
      self.counter += 1
      return [
        *self._pop(),
        *self._pop_no_set(),
        'D=M-D',
        'M=-1',
        f'@{label}',
        f'D;{self.jumps[command]}',
        *self._get_stack_addr(),
        'M=0',
        f'({label})',
        *self._incr_stack_addr(),
      ]
    return [
      *self._pop(),
      *self._pop_no_set(),
      self.operators[command],
      *self._incr_stack_addr(),
    ]
  def end(self):
    return [
      '(END)',
      '@END',
      '0;JMP',
    ]

class CodeWriter:
  def __init__(self, filename):
    self.filename = filename.split('\\')[-1].strip('.asm')
    self.f = open(filename, 'w')
    self.builder = CodeBuilder()
    self.locations = {
      'local': 'LCL',
      'argument': 'ARG',
      'this': 'THIS',
      'that': 'THAT',
    }

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

  def writePop(self, segment, index):
    address = self.getMemory(segment, index)
    if segment == 'temp' or segment == 'pointer':
      index = address
    result = self.builder.pop_to_address(address, index)
    self.write(result)

  def writeArithmetic(self, command):
    result = self.builder.arithmetic(command)
    self.write(result)

  def close(self):
    self.write(self.builder.end())
    self.f.close()

class Translator:
  def __init__(self, filename: str):
    self.parser = Parser(filename)
    self.writer = CodeWriter(filename.replace('.vm', '.asm'))

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