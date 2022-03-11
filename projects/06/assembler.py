import argparse
from collections import defaultdict

def to_binary(string):
    return bin(int(string, 16))[2:].zfill(15)



class Assembler:
  def __init__(self):
    self.symbols = {}
    self.dests = defaultdict(lambda: '000', {
      'M': '001',
      'D': '010',
      'DM': '011',
      'A': '100',
      'AM': '101',
      'AD': '110',
      'ADM': '111',
    })
    self.comps = {
      '0': '0101010',
      '1': '0111111',
      '-1': '0111010',
      'D': '0001100',
      'A': '0110000',
      '!D': '0001101',
      '!A': '0110001',
      '-D': '0001111',
      '-A': '0110011',
      'D+1': '0011111',
      'A+1': '0110111',
      'D-1': '0001110',
      'A-1': '0110010',
      'D+A': '0000010',
      'D-A': '0010011',
      'A-D': '0000111',
      'D&A': '0000000',
      'D|A': '0010101',
      'M': '1110000',
      '!M': '1110001',
      '-M': '1110011',
      'M+1': '1110111',
      'M-1': '1110010',
      'D+M': '1000010',
      'D-M': '1010011',
      'M-D': '1000111',
      'D&M': '1000000',
      'D|M': '1010101',
    }
    self.jumps = defaultdict(lambda: '000', {
      'JGT': '001',
      'JEQ': '010',
      'JGE': '011',
      'JLT': '100',
      'JNE': '101',
      'JLE': '110',
      'JMP': '111',
    })

  def parse(self, filename: str):
    with open(filename, 'r') as f:
      for result in self.parse_file(f):
        print(result)

  def parse_file(self, f):
    for line in f:
      if line.isspace() or line.startswith('//'):
        continue
      if line.startswith('@'):
        yield self.parse_A(line.strip())
      else:
        yield self.parse_C(line.strip())

  def parse_A(self, line):
    symbol = line[1:]
    if symbol.isdigit():
      return f'0{to_binary(symbol)}'
    # TODO

  def parse_C(self, line):
    dest, comp, jump = '', line, ''
    if '=' in comp:
      dest, comp = comp.split('=')
    if ';' in comp:
      comp, jump = comp.split(';')
    return f'111{self.comps[comp]}{self.dests[dest]}{self.jumps[jump]}'

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assembler')
  parser.add_argument('filename', help='input file')
  args = parser.parse_args()
  assembler = Assembler()
  assembler.parse(args.filename)