.integer 1 1
.mult 2 4
.add 1 2
.div 1 16
FLD f1, 0(x1)
FLD f5, 0(x1)
FDIV f2, f4, f5
FMUL f4, f8, f9
FADD f1, f2, f3 
FSD f4, 0(x2)