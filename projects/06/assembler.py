import argparse
from collections import defaultdict

def to_binary(string):
    return bin(int(string, 10))[2:].zfill(15)

class Assembler:
  def __init__(self):
    self.symbols = {
      'R0': '0',
      'R1': '1',
      'R2': '2',
      'R3': '3',
      'R4': '4',
      'R5': '5',
      'R6': '6',
      'R7': '7',
      'R8': '8',
      'R9': '9',
      'R10': '10',
      'R11': '11',
      'R12': '12',
      'R13': '13',
      'R14': '14',
      'R15': '15',
      'SP': '0',
      'LCL': '1',
      'ARG': '2',
      'THIS': '3',
      'THAT': '4',
      'SCREEN': '16384',
      'KBD': '24576',
    }
    self.ram = 16
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
    outfile = filename.replace('.asm', '.hack')
    with open(filename, 'r') as f:
      self.parse_labels(f)
    with open(filename, 'r') as f:
      with open(outfile, 'w') as out:
        for result in self.parse_file(f):
          out.write(f'{result}\n')

  def prep_line(self, line):
    if '//' in line:
      line = line.split('//')[0]
    line = line.strip()
    return line

  def parse_labels(self, f):
    number = 1
    for line in f:
      line = self.prep_line(line)
      if not line or line.startswith('//'):
        continue
      if line.startswith('('):
        self.symbols[line[1:-1]] = f'{number-1}'
      else:
        number += 1

  def parse_file(self, f):
    for line in f:
      line = self.prep_line(line)
      if not line or line.startswith('//') or line.startswith('('):
        continue
      if line.startswith('@'):
        yield self.parse_A(line)
      else:
        yield self.parse_C(line)

  def parse_A(self, line):
    symbol = line[1:]
    if symbol[0].isdigit():
      return f'0{to_binary(symbol)}'
    if symbol not in self.symbols:
      self.symbols[symbol] = f'{self.ram}'
      self.ram += 1
    return f'0{to_binary(self.symbols[symbol])}'

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