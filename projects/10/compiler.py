class JackTokenizer:
  def __init__(self, f):
    self.file = f

  def hasMoreTokens(self):
    pass

  def advance(self):
    pass

  def tokenType(self):
    pass

  def keyWord(self):
    pass

  def symbol(self):
    pass

  def identifier(self):
    pass

  def intVal(self):
    pass

  def stringVal(self):
    pass

class CompilationEngine:
  def __init__(self, infile, outfile):
    self.tokenizer = JackTokenizer(infile)
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

  def analyze(self):
    pass