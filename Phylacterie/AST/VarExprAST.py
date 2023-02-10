from .ExprAST import ExprAST
from .Token import *
from string2irType import string2irType
from ParseError import ParseError

import llvmlite.ir as ir
import llvmlite.binding as llvm

class VarExprAST(ExprAST):
    def __init__(self,parent, var):
        # vars is a sequence of (name, init) pairs
        self.var = var
        self.parent = parent

    def dump(self, indent=0):
        prefix = ' ' * indent
        s = '{0}{1}\n'.format(prefix, self.__class__.__name__)
        for name, init, datatype in [self.var]:
            s += '{0} {1}'.format(prefix, name)
            if init is None:
                s += '\n'
            else:
                s += '=\n' + init.dump(indent+2) + '\n'
        return s

    def parse(parser, parent):
        parser._get_next_token()  # consume the 'var'
        vars = []

        # At least one variable name is required
        if parser.cur_tok.kind != TokenKind.IDENTIFIER:
            raise ParseError('expected datatype identifier after "var"')         
        datatype = parser.cur_tok.value
        parser._get_next_token()  # consume the identifier
        if parser.cur_tok.kind != TokenKind.IDENTIFIER:
          raise ParseError('expected name identifier after "var"')         

        name = parser.cur_tok.value
        parser._get_next_token()  # consume the identifier

        # Parse the optional initializer
        if parser._cur_tok_is_operator('='):
            parser._get_next_token()  # consume the '='
            init = parser._parse_expression(parent)
        else:
            init = None

        return VarExprAST(parent, (name, init, string2irType(datatype)))

    def codegen(self, generator):
        old_bindings = []
        names = []

        for name, init, datatype in [self.var]:
            # Emit the initializer before adding the variable to scope. This
            # prefents the initializer from referencing the variable itgenerator.
            if init is not None:
                init_val = init.codegen(generator)
            else:
                init_val = ir.Constant(datatype, 0.0)

            old = generator.defineVariable(name,init_val);
            if (not old is None):
              old_bindings.append(old);        
            names.append(name);
            lastInitValue = init_val;


        # Cleanup of variables is done by parent scope
        self.parent.addOldBindings(old_bindings);
        self.parent.addVarNames(names);
        
        return lastInitValue