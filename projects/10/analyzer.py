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
  def __init__(self, filename):
    self.tokenizer = JackTokenizer(filename)
    self.outfile = filename.replace('.jack', '_output.xml')
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

class JackAnalyzer:
  def __init__(self, filename: str):
    self.engine = CompilationEngine(filename)

  def analyze(self):
    result = self.engine.compileClass()
    xml = dicttoxml(result, attr_type = False, root=False)
    dom = parseString(xml).toprettyxml()
    formatted = '\n'.join([x.replace('\t', '  ') for x in dom.replace('<item>', '').replace('</item>', '').replace('<item/>', '').split('\n')[1:] if x.strip()])
    # TODO: replace <emptytag/> with <emptytag></emptytag>
    with open(self.engine.outfile, 'w') as f:
      f.write(formatted)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Compiler')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  analyzer = JackAnalyzer(args.filename)
  analyzer.analyze()