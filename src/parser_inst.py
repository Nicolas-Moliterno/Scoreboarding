# cria instruções a partir do texto decodificado
# cada função recebe uma string de instrução tokenizada
# e retorna uma instrução
import re

"""A classe de instrução define uma instrução no placar.
Cada instrução não é apenas capaz de manter seus operandos, destino,
e operação. Ele também contém a representação de string da instrução
como foi lido no arquivo de montagem assim como os ciclos que finaliza
certas fases"""
class Instruction:

  def __init__(self, repr, op, dst, src1, src2):
    self.issue = self.read_ops = self.ex_cmplt = self.write_res = -1
    self.op = op          # instruction operation
    self.fi = dst         # destination register
    self.fj = src1        # source register
    self.fk = src2        # source register
    self.repr = repr      # the string representation

  def __str__(self):
    return "%-24s%-7d%-10d%-10d%-8d" % \
        (self.repr, self.issue, self.read_ops, self.ex_cmplt, self.write_res)


"""Método utilitário para tokenizar uma string de instrução"""
def tokenize_instruction(instruction):
  tokens = re.split(',| ', instruction)
  return list(filter(None, tokens))   # remove empty strings if any

"""Carregar instrução imediata"""
def __li(inst):
  inst_toks = tokenize_instruction(inst)
  op = 'integer'
  fi = inst_toks[1]
  return Instruction(inst, op, fi, None, None)

"""Carga genérica ou instrução de armazenamento"""
def __load_store(inst):
  inst_toks = tokenize_instruction(inst)
  op = 'integer'
  fi = inst_toks[1]
  fk = re.search('\((.*)\)', inst_toks[2]).group(1)    # extract register
  return Instruction(inst, op, fi, None, fk)

"""Instrução genérica de adição, subtração, multiplicação ou divisão"""
def __arithmetic(inst):
  inst_toks = tokenize_instruction(inst)
  op = unit_for_instruction[inst_toks[0].lower()]
  fi = inst_toks[1]
  fj = inst_toks[2]
  fk = inst_toks[3]
  return Instruction(inst, op, fi, fj, fk)

"""Operação aritmética genérica com imediato"""
def __arithmetici(inst):
  inst_toks = tokenize_instruction(inst)
  op = unit_for_instruction[inst_toks[0].lower()]
  fi = inst_toks[1]
  fj = inst_toks[2]
  return Instruction(inst, op, fi, fj, None)

"""Este dicionário tem operações como chaves e tem valores de funções
que correspondem a essas operações. As funções irão analisar e instruir
de uma determinada operação e retornar uma representação que pode ser usada dentro
o próprio scoreboard"""
instructions = {
    'li':     __li,               # INTEGER unit
    'lw':     __load_store,
    'sw':     __load_store,
    'ld':     __load_store,
    'sd':     __load_store,
    'fld':     __load_store,
    'fsd':     __load_store,
    'fadd':    __arithmetic,     # ADD unit
    'addi':   __arithmetici,
    'subi':   __arithmetici,
    'fsub':   __arithmetic,
    'fmul':  __arithmetic,       # MULT unit
    'fdiv':   __arithmetic,       # DIV unit
}


unit_for_instruction = {
    'fadd':    'integer',   # ADD unit
    'addi':   'integer',
    'fsub':    'integer',
    'subi':   'integer',
    'fsub':   'add',
    'fmul':  'mult',       # MULT unit
    'fdiv':   'div',       # DIV unit
}

proc_for_instruction = {
    'integer': '1',
    'add': '1',
    'mult': '2',
    'div': '1',
}

clock_for_instruction = {
    'integer': '1',
    'add': '2',
    'mult': '4',
    'div': '16',
}