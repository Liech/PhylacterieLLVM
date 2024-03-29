from ctypes.wintypes import BOOL
from xmlrpc.client import boolean
from .ExprAST import ExprAST
from .Token import *
from .DatatypeAST import DatatypeAST

import llvmlite.ir as ir
import llvmlite.binding as llvm


class BoolExprAST(ExprAST):
    def __init__(self, core, parent, val):
        self.val = val
        self.parent = parent
        self.core = core;
        
    def getSyntax(self):
      #return ['true']
      return ['false']

    def parse(parser, parent, core):
      if (parser.cur_tok.kind == TokenKind.FALSE):
        parser._get_next_token()
        return BoolExprAST(core, parent,0);
      elif (parser.cur_tok.kind == TokenKind.TRUE):
        parser._get_next_token()
        return BoolExprAST(core, parent,1);
      else:
        raise ParseError("Expected boolean true/false");

    def codegen(self, generator):
        return ir.Constant(ir.IntType(1), int(self.val))
      
    def getReturnType(self):
      return DatatypeAST(self.core, 'bool')