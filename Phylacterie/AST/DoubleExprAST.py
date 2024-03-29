from .ExprAST import ExprAST
from .DatatypeAST import DatatypeAST

import llvmlite.ir as ir
import llvmlite.binding as llvm


class DoubleExprAST(ExprAST):
    def __init__(self, core, parent, val):
        self.val = val
        self.parent = parent
        self.core = core
        
    def getSyntax(self):
      return ['Number','.','Number']

    def codegen(self, generator):
        return ir.Constant(ir.DoubleType(), float(self.val))
      
    def getReturnType(self):
      return DatatypeAST(self.core, 'double')