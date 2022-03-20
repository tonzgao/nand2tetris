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
  def _create_constant(self, constant):
    return [
      f'@{constant}', 
      'D=A',
    ]
  def _set_value(self, address):
    return [
      f'@{address}',
      'M=D',
    ]
  def _set_pointer(self):
    return self._set_value('SP')
  def _partial_return(self, address):
    return [
      '@R13',
      'M=M-1',
      'A=M',
      'D=M',
      f'@{address}',
      'M=D',
    ]

  def push_constant(self, constant):
    return [
      *self._create_constant(constant),
      *self._push_stack()
    ]
  def push_memory(self, address, index=None):
    return [
      *self._access_value(address, index),
      *self._push_stack(),
    ]
  def pop_memory(self, address):
    return [
      *self._pop(),
      f'@{address}',
      'M=D',
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
  def create_label(self, name):
    return [
      f'({name})',
    ]
  def goto(self, label):
    return [
      f'@{label}',
      '0;JMP',
    ]
  def if_goto(self, label):
    return [
      *self._pop(),
      f'@{label}',
      'D;JNE',
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
        *self.create_label(label),
        *self._incr_stack_addr(),
      ]
    return [
      *self._pop(),
      *self._pop_no_set(),
      self.operators[command],
      *self._incr_stack_addr(),
    ]
  def function(self, name, n_args):
    result = [
      *self.create_label(name)
    ]
    for _ in range(int(n_args)):
      result += self.push_constant(0)
    return result
  def call(self, name, n_args):
    label = f'f_{name}_{n_args}'
    result = [
        *self._get_stack_addr(),
        *self._set_value('R13'),
        f'@{label}',
        'D=A',
        *self._push_stack(),
        *self.push_memory('LCL'),
        *self.push_memory('ARG'),
        *self.push_memory('THIS'),
        *self.push_memory('THAT'),
        *self._access_value('SP'),
        *self._set_value('LCL'),
    ]
    for _ in range(int(n_args)):
      result += [
        '@R13',
        'M=M-1',
      ]
    result += [
      *self._access_value('R13'),
      *self._set_value('ARG'),
      *self.goto(name),
      *self.create_label(label),
    ]
    return result
  def build_return(self):
    return [
      *self._access_value('LCL'),
      '@R13',
      'M=D',
      *self.pop_to_address('ARG', '0'),
      *self._get_address('ARG'),
      'D=M+1',
      *self._set_pointer(),
      *self._partial_return('THAT'),
      *self._partial_return('THIS'),
      *self._partial_return('ARG'),
      *self._partial_return('LCL'),
      '@R13',
      'M=M-1',
      'A=M',
    ]
  def bootstrap(self):
    return [
      *self._create_constant(256),
      *self._set_pointer(),
      *self.call('Sys.init', 0),
    ]
  def end(self):
    return [
      '(END)',
      '@END',
      '0;JMP',
    ]
