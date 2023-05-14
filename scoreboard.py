import os
import sys
import pandas as pd
from rich.console import Console
from rich.table import Table

from src.funct_unit import FunctionalUnit, FORMAT_HEADER
from src.parser_inst import instructions as inst_funcs
from src.parser_inst import unit_for_instruction as unit_inst
from src.parser_inst import proc_for_instruction as proc_inst
from src.parser_inst import clock_for_instruction as clock_inst


"""A classe ScoreboardParser é responsável por receber uma
arquivo de montagem como entrada e criando seu respectivo objeto Scoreboard
que pode então ser usado para simular o algoritmo de scoreboard."""
class ScoreboardParser:

  def __init__(self, s_file):
    self.sb = Scoreboard()
    self.s = s_file
    self.flag = []


  """Analisa uma unidade funcional no arquivo"""
  def __parse_fu(self, s_tokens):
    f_unit = s_tokens[0][1:]
    num_units = int(s_tokens[1])
    clocks = int(s_tokens[2])
    for unit in range(0, num_units):
      self.sb.units.append(FunctionalUnit(f_unit, clocks))


  """Analisa uma unidade funcional no arquivo DEFAULT"""
  def __parse_fu_deault(self, s_tokens):
    if s_tokens[0].lower() in unit_inst:
      if self.sb.units == []:
        f_unit = 'integer'
        num_units = int(proc_inst[f_unit])
        clocks = int(clock_inst[f_unit])
        for unit in range(0, num_units):
          self.sb.units.append(FunctionalUnit(f_unit, clocks))
        self.flag.append(unit_inst[s_tokens[0].lower()])
        if s_tokens[0].lower() in unit_inst:
            f_unit = unit_inst[s_tokens[0].lower()]#[1:]
            num_units = int(proc_inst[f_unit])
            clocks = int(clock_inst[f_unit])
            for unit in range(0, num_units):
                self.sb.units.append(FunctionalUnit(f_unit, clocks))
            self.flag.append(unit_inst[s_tokens[0].lower()])
      else:
        if s_tokens[0].lower() in unit_inst:
            f_unit = unit_inst[s_tokens[0].lower()]#[1:]
            num_units = int(proc_inst[f_unit])
            clocks = int(clock_inst[f_unit])
            if f_unit in self.flag:
              pass
            else:
              for unit in range(0, num_units):
                self.sb.units.append(FunctionalUnit(f_unit, clocks))
              self.flag.append(unit_inst[s_tokens[0].lower()])
    else:
      pass


  """Analisa uma instrução no arquivo"""
  def __parse_inst(self, inst_tokens):
    key = inst_tokens[0].lower()
    inst_func = inst_funcs[key]
    instruction = inst_func(' '.join(inst_tokens))
    self.sb.instructions.append(instruction)
    


  """Analisa uma linha do arquivo"""
  def __parse_line(self, line):
    tokens = line.split()
    # se a linha começa com '.' é uma unidade funcional
    # em vez de uma instrução
    if tokens[0][0] == '.':
        f_units = self.__parse_fu(tokens)
    else:
        inst = self.__parse_inst(tokens)


  """Analisa uma linha do arquivo DEFAULT"""
  def __parse_line_default(self, line):
    tokens = line.split()
    f_units = self.__parse_fu_deault(tokens)
    inst = self.__parse_inst(tokens)


  """Cria um objeto Scoreboard com base em um determinado arquivo"""
  def scoreboard_for(s_file):
    parser = ScoreboardParser(s_file)
    with open(parser.s, 'r') as f:
      assembly = [line.strip() for line in f]
    if assembly[0][0] == '.':
        for instruction in assembly:
            parser.__parse_line(instruction)
    else:
        for instruction in assembly:
            parser.__parse_line_default(instruction)
    return parser.sb


"""A classe Scoreboard é usada para simular o algoritmo"""
class Scoreboard:

  def __init__(self):
    self.units = []           # array of FunctionalUnit
    self.instructions = []    # array of Instruction
    self.reg_status = {}      # register status table
    self.pc = 0               # program counter
    self.clock = 1            # processor clock


  def __str__(self):
    result = 'CLOCK: %d\n' % (self.clock)
    result += FORMAT_HEADER + '\n'
    for unit in self.units:
      result += str(unit) + '\n'
    return result


  """Verifica se o scoreboard terminou de ser executado. Retorna True se sim"""
  def done(self):
    done_executing = True
    out_of_insts = not self.has_remaining_insts()
    if out_of_insts:
      for fu in self.units:
        if fu.busy:
          done_executing = False
          break
    return out_of_insts and done_executing


  """Verifica se há instruções deixadas para emitir para o
  scoreboard e retorna True em caso afirmativo"""
  def has_remaining_insts(self):
    return self.pc < len(self.instructions)


  """Determina se uma instrução pode ser emitida"""
  def can_issue(self, inst, fu):
    if inst is None:
      return False
    else:
      return inst.op == fu.type and not fu.busy and not (inst.fi in self.reg_status)


  """Determina se uma instrução é capaz de entrar na fase de leitura de operandos"""
  def can_read_operands(self, fu):
    return fu.busy and fu.rj and fu.rk


  """Determina se uma instrução é capaz de entrar na fase de execução"""
  def can_execute(self, fu):
    # verifica se lemos os operandos, a unidade funcional
    # está realmente em uso e tem relógios restantes
    return (not fu.rj and not fu.rk) and fu.issued()


  """Determina se uma instrução é capaz de entrar na fase de write-back"""
  def can_write_back(self, fu):
    can_write_back = False
    for f in self.units:
      can_write_back = (f.fj != fu.fi or not f.rj) and (f.fk != fu.fi or not f.rk)
      if not can_write_back:
        break
    return can_write_back


  """Emite uma instrução para o scoreboard"""
  def issue(self, inst, fu):
    fu.issue(inst, self.reg_status)
    self.reg_status[inst.fi] = fu
    self.instructions[self.pc].issue = self.clock
    fu.inst_pc = self.pc


  """Ler estágio de operandos do placar"""
  def read_operands(self, fu):
    fu.read_operands()
    self.instructions[fu.inst_pc].read_ops = self.clock


  """Executar etapa do placar"""
  def execute(self, fu):
    fu.execute()
    if fu.clocks == 0:
      self.instructions[fu.inst_pc].ex_cmplt = self.clock


  """Estágio de write-back do placar"""
  def write_back(self, fu):
    fu.write_back(self.units)
    self.instructions[fu.inst_pc].write_res = self.clock
    # limpa o status do registrador de resultado
    del self.reg_status[fu.fi]
    fu.clear()


  """Tick: simula um ciclo de clock no placar"""
  def tick(self):
    # desbloquear todas as unidades funcionais
    for fu in self.units:
      fu.lock = False

    # Obtenha a próxima instrução com base no PC
    next_instruction = self.instructions[self.pc] if self.has_remaining_insts() else None

    for fu in self.units:
      if self.can_issue(next_instruction, fu):
        self.issue(next_instruction, fu)
        self.pc += 1
        fu.lock = True
      elif self.can_read_operands(fu):
        self.read_operands(fu)
        fu.lock = True
      elif self.can_execute(fu):
        self.execute(fu)
        fu.lock = True
      elif fu.issued():
        # a unidade funcional está em uso, mas não pode fazer nada
        fu.lock = True
      result = 'CLOCK: %d' % (self.clock)

      # result += FORMAT_HEADER + '\n'
      print('\n', result)
      data = {
        'UNIT': [vars(fu)['type']],
        'Clocks': [vars(fu)['clocks']],
        'Busy': [vars(fu)['busy']],
        'Fi': [vars(fu)['fi']],
        'Fj': [vars(fu)['fj']],
        'Fk': [vars(fu)['fk']],
        'Qj': [vars(fu)['qj']],
        'Qk': [vars(fu)['qk']],
        'Rj': [vars(fu)['rj']],
        'Rk': [vars(fu)['rk']],
      }
      df = pd.DataFrame(data)
      table = Table(title="")
      rows = df.values.tolist()
      rows = [[str(el) for el in row] for row in rows]
      columns = df.columns.tolist()

      for column in columns:
          table.add_column(column)

      for row in rows:
          table.add_row(*row, style='bright_green')

      console = Console()
      console.print(table)

    for fu in self.units:
      if not fu.lock and self.can_write_back(fu):
        self.write_back(fu)

    self.clock += 1


if __name__ == '__main__':
  ASM_FILE = os.path.abspath(sys.argv[1])

  instruction_rows_repr = []
  instruction_rows_issue = []
  instruction_rows_read_op = []
  instruction_rows_exec = []
  instruction_rows_write = []

  # exibir os resultados finais
  print('\n=========== TABELA REGISTRADORES ==============\n')
  
  sb = ScoreboardParser.scoreboard_for(ASM_FILE)
  
  while not sb.done():
      sb.tick()

  for instruction in sb.instructions:
      instruction_rows_repr.append(vars(instruction)['repr'])
      instruction_rows_issue.append(vars(instruction)['issue'])
      instruction_rows_read_op.append(vars(instruction)['read_ops'])
      instruction_rows_exec.append(vars(instruction)['ex_cmplt'])
      instruction_rows_write.append(vars(instruction)['write_res'])  


  # create empty data frame in pandas
  df = pd.DataFrame()
  df['     ']  = instruction_rows_repr
  df['Issue']  = instruction_rows_issue
  df['Read Operands']  = instruction_rows_read_op
  df['Execute Complete']  = instruction_rows_exec
  df['Write Result']  = instruction_rows_write  

  table = Table(title="\n=========== TABELA SCOREBOARDING ==============\n")

  rows = df.values.tolist()
  rows = [[str(el) for el in row] for row in rows]
  columns = df.columns.tolist()

  for column in columns:
      table.add_column(column)

  for row in rows:
      table.add_row(*row, style='bright_green')
  console = Console()
  console.print(table)
    
    
    
