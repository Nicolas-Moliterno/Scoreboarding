.integer 1 1
.mult 2 4
.add 1 2
.div 1 16
fld  f1, 100(R1)
FADD f2, f1, f3
FMUL f2, f2, f4
FADD R1, R2, R3
FDIV f2, f1, f2
FMUL f4, f4, f2
FADD f4, f5, f3
FSD  f1, 200(R1)