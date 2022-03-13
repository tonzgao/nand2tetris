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
    self.filename = filename
  
  def writeArithmetic(self, command):
    print(command)

  def writePushPop(self, command, segment, index):
    print(command, segment, index)

  def close(self):
    pass

class Translator:
  def __init__(self, filename: str):
    self.parser = Parser(filename)
    self.writer = CodewWriter(filename.replace('.vm', '.asm'))

  def translate(self):
    while self.parser.hasMoreLines():
      self.parser.advance()
      if self.parser.commandType() == C_ARITHMETIC:
        self.writer.writeArithmetic(self.parser.arg1())
      elif self.parser.commandType() == C_PUSH:
        self.writer.writePushPop(C_PUSH, self.parser.arg1(), self.parser.arg2())
      elif self.parser.commandType() == C_POP:
        self.writer.writePushPop(C_POP, self.parser.arg1(), self.parser.arg2())

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Translator')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  translator = Translator(args.filename)
  translator.translate()