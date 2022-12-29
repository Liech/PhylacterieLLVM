from .ExprAST import ExprAST

import llvmlite.ir as ir
import llvmlite.binding as llvm

class UnaryExprAST(ExprAST):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def dump(self, indent=0):
        s = '{0}{1}[{2}]\n'.format(
            ' ' * indent, self.__class__.__name__, self.op)
        s += self.operand.dump(indent + 2)
        return s

    def codegen(self, generator):
        operand = generator._codegen(self.operand)
        func = generator.module.get_global('unary{0}'.format(self.op))
        return generator.builder.call(func, [operand], 'unop')