from .ExprAST import ExprAST
from .VariableExprAST import VariableExprAST
from .UnaryExprAST import UnaryExprAST
from .CodegenError import CodegenError
from .Token import *

import llvmlite.ir as ir
import llvmlite.binding as llvm

class BinaryExprAST(ExprAST):
    def __init__(self, parent, op, lhs, rhs, core):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.parent = parent
        self.core = core
        
    def getSyntax(self):
      return ['Expression','operator','Expression']
            
    def getReturnType(self):      
      opID = self.getID();
      return self.core.typeContainer.getType(opID);

    def parse(parser, expr_prec, lhs, parent,core):
        """Parse the right-hand-side of a binary expression.

        expr_prec: minimal precedence to keep going (precedence climbing).
        lhs: AST of the left-hand-side.
        """
        while True:
            cur_prec = core.operators.getPrecedence(parser.cur_tok.value);
            # If this is a binary operator with precedence lower than the
            # currently parsed sub-expression, bail out. If it binds at least
            # as tightly, keep going.
            # Note that the precedence of non-operators is defined to be -1,
            # so this condition handles cases when the expression ended.
            if cur_prec < expr_prec:
                return lhs
            op = parser.cur_tok.value
            parser._get_next_token()  # consume the operator
            if (op == ';' and parser.cur_tok.kind == TokenKind.EOF):
              return lhs;
            rhs = UnaryExprAST.parse(parser, parent, core);

            next_prec = core.operators.getPrecedence(parser.cur_tok.value);
            # There are three options:
            # 1. next_prec > cur_prec: we need to make a recursive call
            # 2. next_prec == cur_prec: no need for a recursive call, the next
            #    iteration of this loop will handle it.
            # 3. next_prec < cur_prec: no need for a recursive call, combine
            #    lhs and the next iteration will immediately bail out.
            if cur_prec < next_prec:
                rhs = BinaryExprAST.parse(parser,  cur_prec + 1, rhs, parent, core)

            # Merge lhs/rhs
            lhs = BinaryExprAST(parent, op, lhs, rhs, core)

    def getID(self):
      return 'binary' + self.op + '_' + self.lhs.getReturnType().toString() + '_' + self.rhs.getReturnType().toString() + '_';

    def codegen(self, generator):
        # Assignment is handled specially because it doesn't follow the general
        # recipe of binary ops.
        if self.op == '=':
            if not isinstance(self.lhs, VariableExprAST):
                raise CodegenError('lhs of "=" must be a variable')
            var_addr = generator.getSymtab()[self.lhs.name]
            rhs_val = self.rhs.codegen(generator)
            generator.getBuilder().store(rhs_val, var_addr)
            return rhs_val

        lhs = self.lhs.codegen(generator)
        rhs = self.rhs.codegen(generator)
        opID = self.getID();

        if opID == 'binary+_double_double_':
            return generator.getBuilder().fadd(lhs, rhs, 'addtmp')
        elif opID == 'binary-_double_double_':
            return generator.getBuilder().fsub(lhs, rhs, 'subtmp')
        elif opID == 'binary*_double_double_':
            return generator.getBuilder().fmul(lhs, rhs, 'multmp')
        elif opID == 'binary-_int_int_':
            return generator.getBuilder().sub(lhs, rhs, 'subtmp')
        elif opID == 'binary+_int_int_':
            return generator.getBuilder().add(lhs, rhs, 'subtmp')
        elif opID == 'binary*_int_int_':
            return generator.getBuilder().mul(lhs, rhs, 'subtmp')
        elif opID == 'binary<_double_double_':
            cmp = generator.getBuilder().fcmp_unordered('<', lhs, rhs, 'cmptmp')
            return generator.getBuilder().uitofp(cmp, ir.IntType(1), 'booltmp')
        elif opID == 'binary<_int_int_':
            cmp = generator.getBuilder().cmp_unordered('<', lhs, rhs, 'cmptmp')
            return generator.getBuilder().uitofp(cmp, ir.IntType(1), 'booltmp')
        else:
            # Note one of predefined operator, so it must be a user-defined one.
            # Emit a call to it.
            func = generator.getModule().get_global(opID)
            return generator.getBuilder().call(func, [lhs, rhs], 'binop')

