import argparse

keywords = set([
  'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'
])
symbols = set([
  '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
])

class JackTokenizer:
  def __init__(self, filename):
    with open(filename, 'r') as f:
      self.text = f.read()
    self.counter = 0
    self.token = ''

  def removeComments(self):
    single_lines = self.text.split('//')
    single_lines_removed = ''.join([
      line.split('\n', 1)[-1] for line in single_lines
    ])
    all_comments = single_lines_removed.split('/**')
    self.text = ''.join([
      line.split('*/', 1)[-1] for line in all_comments
    ])

  def hasMoreTokens(self):
    return self.counter < len(self.text) - 1

  def advance(self):
    current = self.text[self.counter]
    self.counter += 1
    if current in symbols:
      self.token = current
    if current.isspace():
      return self.advance()
    result = current
    while not current.isspace() and current not in symbols:
      current = self.text[self.counter]
      if current in symbols:
        break
      result += current
      self.counter += 1
      if not self.hasMoreTokens():
        break
    self.token = result

  def tokenType(self):
    if self.token in symbols:
      return 'symbol'
    if self.token in keywords:
      return 'keyword'
    if self.token.isdigit():
      return 'integerConstant'
    if self.token[0] == '"':
      return 'stringConstant'
    return 'identifier'

  def keyWord(self):
    if self.token in keywords:
      return self.token

  def symbol(self):
    return self.token

  def identifier(self):
    return self.token

  def intVal(self):
    return int(self.token)

  def stringVal(self):
    return self.token

class CompilationEngine:
  def __init__(self, filename, outfile):
    self.tokenizer = JackTokenizer(filename)
    self.file = outfile

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

  def compileDo(self):
    pass

  def compileLet(self):
    pass

  def compileWhile(self):
    pass

  def compileReturn(self):
    pass

  def compileIf(self):
    pass

  def compileExpression(self):
    pass

  def compileTerm(self):
    pass

  def compileExpressionList(self):
    pass

class JackAnalyzer:
  def __init__(self, filename: str):
    self.filename = filename
    self.tokenizer = JackTokenizer(filename)

  def analyze(self):
    self.tokenizer.removeComments()
    while self.tokenizer.hasMoreTokens():
      self.tokenizer.advance()
      print(self.tokenizer.tokenType(), self.tokenizer.token)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Compiler')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  analyzer = JackAnalyzer(args.filename)
  analyzer.analyze()