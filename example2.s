.integer 1 1
.mult 2 4
.add 1 2
.div 1 16
FLD  f1, 100(x7)
FMUL f2, f2, f4
FADD f2, f1, f3
FLD  f9, 0(x3)
FDIV f3, f1, f7
FSUB f6, f3, f4
FMUL f7, f1, f2
FADD f4, f5, f2
FSD  f1, 50(x11)