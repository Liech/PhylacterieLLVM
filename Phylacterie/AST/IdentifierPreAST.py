from .ExprAST import ExprAST
from .Token import *

from .VarExprAST import VarExprAST
from .VariableExprAST import VariableExprAST
from .CallExprAST import CallExprAST
from .FunctionAST import FunctionAST

import llvmlite.ir as ir
import llvmlite.binding as llvm

class IdentifierPreAST(ExprAST):
  def __init__(self):
    raise Exception("Parser Error");

  def parse(parser, parent,core):
    id_name = parser.cur_tok
    parser._get_next_token()
    
    if (parser.cur_tok.kind == TokenKind.IDENTIFIER or parser.cur_tok.kind == TokenKind.BINARY or parser.cur_tok.kind == TokenKind.UNARY):
      id_name2 = parser.cur_tok
      parser._get_next_token()
      if parser._cur_tok_is_operator('=') or parser._cur_tok_is_operator(';'):
        return VarExprAST.parse(parser,parent, id_name.value,id_name2.value, core);
      else:
        return FunctionAST.parse(parser, parent, id_name,id_name2, core);
    elif parser._cur_tok_is_operator('('):
      return CallExprAST.parse(parser,parent, id_name.value, core);
    else:
      return VariableExprAST(parent, id_name.value,core)
    