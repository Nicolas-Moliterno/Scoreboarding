FORMAT_HEADER = \
    "UNIT     Clocks  Busy    Fi   Fj    Fk   Qj         Qk         Rj    Rk\
\n-------------------------------------------------------------------------------"

class FunctionalUnit:

  def __init__(self, type, clocks):
    self.type = type                      # type of functional unit
    self.clocks = clocks                  # clocks remaining
    self.default_clock = clocks           # max num of clocks for FU
    self.busy = False                     # busy status
    self.fi = self.fj = self.fk = None    # instruction registers
    self.qj = self.qk = None              # FUs producing source registers Fj, Fk
    self.rj = self.rk = True              # Flags for Fj, Fk ready status
    self.lock = False                     # mutex
    self.inst_pc = -1                     # pc for the instruction using the FU


  def __str__(self):
    qj_type = self.qj.type if self.qj is not None else None
    qk_type = self.qk.type if self.qk is not None else None

    return "%-7s%8d%6s%6s%6s%6s  %-9s  %-9s%6s%6s" % \
        (self.type, self.clocks, self.busy,
            self.fi, self.fj, self.fk,
            repr(self.qj), repr(self.qk), self.rj, self.rk)

  def __repr__(self):
    return '%s' % (self.type)


  """Redefine a unidade funcional para que ela possa ser usada por outra instrução"""
  def clear(self):
    self.clocks = self.default_clock
    self.busy = False
    self.fi = self.fj = self.fk = None
    self.qj = self.qk = None
    self.rj = self.rk = True
    self.inst_pc = -1


  """Determina se uma unidade funcional foi emitida"""
  def issued(self):
    return self.busy and self.clocks > 0


  """Encapsula a funcionalidade de emitir uma instrução"""
  def issue(self, inst, reg_status):
    self.busy = True
    self.fi = inst.fi
    self.fj = inst.fj
    self.fk = inst.fk

    if inst.fj in reg_status:
      self.qj = reg_status[inst.fj]
    if inst.fk in reg_status:
      self.qk = reg_status[inst.fk]

    self.rj = not self.qj
    self.rk = not self.qk


  """Encapsula a funcionalidade de read_operands"""
  def read_operands(self):
    self.rj = False
    self.rk = False


  """A função de atualização encapsula o clock em uma unidade funcional"""
  def execute(self):
    self.clocks -= 1


  """Encapsula a funcionalidade de escrever de volta uma instrução
  Requer como entrada todas as unidades funcionais no scoreboard"""
  def write_back(self, f_units):
    for f in f_units:
      if f.qj == self:
        f.rj = True
        f.qj = None
      if f.qk == self:
        f.rk = True
        f.qk = None
