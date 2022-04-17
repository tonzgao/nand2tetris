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

  def __repr__(self):
      return dict(self.table).__repr__()

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
    self.unary = {
      '-': 'neg',
      '~': 'not'
    }
    self.label = 0

  def write(self, text):
    self.f.write(f'{text}\n')

  def getSegment(self, segment):
    if segment == 'field':
      return 'this'
    return segment

  def writePush(self, segment, index):
    self.write(f'push {self.getSegment(segment)} {index}')

  def writePop(self, segment, index):
    self.write(f'pop {self.getSegment(segment)} {index}')

  def writeUnary(self, command):
    self.write(self.unary[command])

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
    self.label_counter = 0

  def createLabel(self, name):
    self.label_counter += 1
    return f'{name}_{self.label_counter}'

  def remember(self, identifier):
    table = self.subSymbols if self.subSymbols.typeOf(identifier) else self.classSymbols
    return (table.kindOf(identifier), table.indexOf(identifier), table.typeOf(identifier))

  def compileClass(self):
    self.classSymbols.reset()
    json = self.analyzer.compileClass()
    className = json['class'][1]['identifier']
    for i in json['class']:
      if 'subroutineDec' in i:
        self.compileSubroutine(i['subroutineDec'], className)
      elif 'classVarDec' in i:
        self.compileClassVarDec(i['classVarDec'])

  def compileClassVarDec(self, varDec):
    kind = varDec[0]['keyword']
    type = varDec[1].get('keyword') or varDec[1]['identifier']
    for i in varDec[2:]:
      if 'identifier' in i:
        self.classSymbols.define(i['identifier'], type, kind)
    
  def compileSubroutine(self, subroutine, className):
    self.subSymbols.reset()
    subType = subroutine[0]['keyword']
    returnType = subroutine[1].get('keyword') or subroutine[1]['identifier']
    params = self.compileParameterList(subroutine[4]['parameterList'])

    body = subroutine[6]['subroutineBody']
    for i in body:
      if 'varDec' in i:
        self.compileVarDec(i['varDec'])
      elif 'statements' in i:
        locals = self.subSymbols.varCount('local')
        self.writer.writeFunction(f'{className}.{subroutine[2]["identifier"]}', locals)
        if subType == 'method':
          self.subSymbols.define('this', className, 'argument')
          self.writer.writePush('argument', 0)
          self.writer.writePop('pointer', 0)
        elif subType == 'constructor':
          print('constructor', className, params, subroutine[4], len(self.classSymbols.table), locals)
          self.subSymbols.define('this', className, 'pointer')
          self.writer.writePush('constant', params + len(self.classSymbols.table))
          self.writer.writeCall('Memory.alloc', 1)
          self.writer.writePop('pointer', 0)
        self.compileStatements(i['statements'])
        break

  def compileParameterList(self, parameterList):
    count = 0
    for i in range(0, len(parameterList), 3):
      self.subSymbols.define(parameterList[i+1]['identifier'], parameterList[i]['keyword'], 'argument')
      count += 1
    return count

  def compileVarDec(self, varDec):
    type = varDec[1].get('keyword') or varDec[1]['identifier']
    for i in varDec[2:]:
      if 'identifier' in i:
        self.subSymbols.define(i['identifier'], type, 'local')
        
    
  def compileStatements(self, statements):
    for i in statements:
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
    identifier = let[1]['identifier']
    expression = let[3]['expression']
    var = self.remember(identifier)
    self.compileExpression(expression)
    if let[2].get('symbol') == '[':
      self.writer.writePush(var[0], var[1])
      self.writer.writeArithmetic('+')
      self.compileExpression(let[6]['expression'])
      self.writer.writePop('temp', 0)
      self.writer.writePop('pointer', 1)
      self.writer.writePush('temp', 0)
      self.writer.writePop('that', 0)
    else:
      self.writer.writePop(var[0], var[1])

  def compileIf(self, ifStatement):
    endLabel = self.createLabel('ifend')
    elseLabel = self.createLabel('else')
    self.compileExpression(ifStatement[2]['expression'])
    self.writer.writeUnary('~')
    self.writer.writeIf(elseLabel)
    self.compileStatements(ifStatement[5]['statements'])
    self.writer.writeGoto(endLabel)
    self.writer.writeLabel(elseLabel)
    if len(ifStatement) > 7:
      self.compileStatements(ifStatement[9]['statements'])
    self.writer.writeLabel(endLabel)

  def compileWhile(self, whileStatement):
    continueLabel = self.createLabel('while')
    terminatelabel = self.createLabel('while_end')
    self.writer.writeLabel(continueLabel)
    self.compileExpression(whileStatement[2]['expression'])
    self.writer.writeUnary('~')
    self.writer.writeIf(terminatelabel)
    self.compileStatements(whileStatement[5]['statements'])
    self.writer.writeGoto(continueLabel)
    self.writer.writeLabel(terminatelabel)

  def compileCall(self, call):
    callee = call[0]["identifier"] if call[1].get('symbol') == '.' else 'this'
    method = call[2]['identifier'] if call[1].get('symbol') == '.' else call[0]['identifier']
    exprs = [x for x in call if 'expressionList' in x][0]
    size = 0
    if callee[0].islower():
      var = self.remember(callee)
      callee = var[2]
      self.writer.writePush(var[0], var[1])
      # print('call', method, var, self.subSymbols)
      size += 1
    size += self.compileExpressionList(exprs)
    self.writer.writeCall(f'{callee}.{method}', size)

  def compileDo(self, do):
    call = do[1]
    # print('call', call)
    self.compileCall(call)
    self.writer.writePop('temp', 0)

  def compileReturn(self, returnStatement):
    expression = returnStatement[1]
    # print('return', expression)
    if 'expression' in expression:
      self.compileExpression(expression['expression'])
    else:
      self.writer.writePush('constant', 0)
    self.writer.writeReturn()

  def compileExpression(self, expr):
    symbol = None
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
    if not isinstance(term, list):
      if 'identifier' in term:
        var = self.remember(term['identifier'])
        self.writer.writePush(var[0], var[1])
      elif term.get('keyword') == 'this':
        self.writer.writePush('pointer', 0)
      elif term.get('stringConstant'):
        string = term['stringConstant']
        self.writer.writePush('constant', len(string))
        self.writer.writeCall('String.new', 1)
        for c in string:
          self.writer.writePush('constant', ord(c))
          self.writer.writeCall('String.appendChar', 2)
      else:
        self.push(term)
    elif term[0].get('symbol') == '(':
      self.compileExpression(term[1]['expression'])
    elif term[0].get('symbol'):
      self.compileTerm(term[1]['term'])
      self.writer.writeUnary(term[0]['symbol'])
    elif term[1].get('symbol') == '[':
      print('array', term)
      var = self.remember(term[0]['identifier'])
      self.writer.writePush(var[0], var[1])
      self.compileExpression(term[2]['expression'])
      self.writer.writeArithmetic('+')
      self.writer.writePop('pointer', 1)
      self.writer.writePush('that', 0)
    else:
      self.compileCall(term)
    
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
    elif 'keyword' in item:
      # TODO: handle 'this'
      self.writer.writePush('constant', 0)
      if item['keyword'] == 'true':
        self.writer.writeUnary('~')

  def compileExpressionList(self, exprs):
    size = 0
    for exp in exprs['expressionList']:
      if 'expression' in exp:
        self.compileExpression(exp['expression'])
        size += 1
    return size

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Compiler')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  compiler = CompilationEngine(args.filename)
  compiler.compileClass()
