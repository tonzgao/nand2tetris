import argparse
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString

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

  def peek(self):
    counter, token = self.counter, self.token
    self.advance()
    result = self.token
    self.counter, self.token = counter, token
    return result

  def advance(self):
    current = self.text[self.counter]
    self.counter += 1
    if current in symbols:
      self.token = current
      return
    if current.isspace():
      return self.advance()
    result = current
    if current == '"':
      while (current := self.text[self.counter]) != '"':
        result += current
        self.counter += 1
      self.counter += 1
    else:
      while (current := self.text[self.counter]) not in symbols and not current.isspace():
        result += current
        self.counter += 1
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
    return {'keyword': self.token}

  def symbol(self):
    return {'symbol': self.token}

  def identifier(self):
    return {'identifier': self.token}

  def intVal(self):
    return {'integerConstant': int(self.token)}

  def stringVal(self):
    return {'stringConstant': self.token[1:]}

  def current(self):
    case = self.tokenType()
    if case == 'symbol':
      return self.symbol()
    if case == 'keyword':
      return self.keyWord()
    if case == 'integerConstant':
      return self.intVal()
    if case == 'stringConstant':
      return self.stringVal()
    return self.identifier()

  def next(self):
    self.advance()
    return self.current()

class CompilationEngine:
  def __init__(self, filename, outfile):
    self.tokenizer = JackTokenizer(filename)
    self.tokenizer.removeComments()
    # self.file = open(outfile, 'w')

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
    while symbol == ',':
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
    sopen = self.tokenizer.next()
    result = [
      declaration,
      returnType,
      name,
      popening,
      parameters,
      sopen
    ]
    while self.tokenizer.peek() == 'var':
      result.append(self.compileVarDec())
    print('here', result)
    statements = self.compileStatements()
    sclosing = self.tokenizer.next()
    result += [statements, sclosing]
    return {
      'subroutineDec': result
    }

  def compileParameterList(self):
    result = []
    while self.tokenizer.peek() != ')':
      result.append(self.tokenizer.next())
      symbol = self.tokenizer.next()
      if symbol != ',':
        return [
          {'parameterList': result},
          symbol
        ]
      result.append(symbol)
    if not len(result):
      return [self.tokenizer.next()]

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
    while symbol == ',':
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
      if peek == 'let':
        result.append(self.compileLet())
      if peek == 'while':
        result.append(self.compileWhile())
      if peek == 'if':
        result.append(self.compileIf())
      if peek == 'return':
        result.append(self.compileReturn())
    return {
      'statements': result
    }

  def compileDo(self):
    pass

  def compileLet(self):
    let = self.tokenizer.next()
    name = self.tokenizer.next()
    opening = self.tokenizer.next()
    

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
    self.engine = CompilationEngine(filename, filename.replace('.jack', '.xml'))

  def analyze(self):
    result = self.engine.compileClass()
    xml = dicttoxml(result, attr_type = False, root=False)
    dom = parseString(xml)
    test = dom.toprettyxml()
    print(test.replace('<item>', '').replace('</item>', '').replace('<item/>', ''))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Compiler')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  analyzer = JackAnalyzer(args.filename)
  analyzer.analyze()