"""
This program uses PLY (Python Lex-Yacc). Documentation for PLY is
available at
    http://www.dabeaz.com/ply/ply.html

PLY can be installed on your own system using pip, which comes
preinstalled on recent versions of Python (>= 3.4). Using pip the PLY
package can be installed with the following command:
    pip3 install ply
This requires Internet access to download the package.
"""

import ply.lex as lex
import ply.yacc as yacc
import sys

"""
PLY's scanner works by matching regular expressions to the tokens.
Regular expressions were used in the superquiz, but if anyone needs
a reminder of the syntax check the following link:
    https://docs.python.org/3/library/re.html

All tokens that the lexer can find must be decleared in a list of
strings called tokens, which contains the names of the tokens, but
not the regular expressions matching them.
"""

# reserved words
reserved = {
    'do': 'DO',
    'else': 'ELSE',
    'end': 'END',
    'if': 'IF',
    'then': 'THEN',
    'while': 'WHILE',
    'read': 'READ',
    'write': 'WRITE'
    
}

# all token types
tokens = [
    'SEM', 'BEC', 'LESS', 'EQ', 'GRTR', 'LEQ', 'NEQ', 'GEQ',
    'ADD', 'SUB', 'MUL', 'DIV', 'LPAR', 'RPAR', 'NUM', 'ID'
] + list(reserved.values())

"""
A regular expression is associated to a token as in the following
example:

    t_EXAMPLE1 = r'\+'

The declared name must start with 't_' and end with the name of a
token (an element of tokens). It is assigned a string denoting a
regular expression. The prefix 'r' of the string is not related to
regular expressions but specifies raw strings in Python. In raw
strings, Python does not treat backslashes as escape sequences.

By declaring a function instead of a string, an action can be
performed after a token has been matched:

    def t_EXAMPLE2(t):
        r'\+'
        t.type = 'ADD' # must be the name of a token
        t.value = 'ADD' # can be any value associated with the token
        return t

In this case, the regular expression is the docstring of the
function. The function has a single input 't', a token object with
attributes type and value, both of which are already set. The
attribute t.type is set to the function's name without 't_' and
t.value is set to the string that the regular expression matched.
These attributes can be modified if necessary, as shown above.
"""

# rules specifying regular expressions and actions

t_SEM = r';'
t_BEC = r':='
t_LESS = r'<'
t_EQ = r'='
t_GRTR = r'>'
t_LEQ = r'<='
t_GEQ = r'>='
t_NEQ = r'!='
t_MUL = r'\*'
t_DIV = r'/'
t_ADD = r'\+'
t_SUB = r'-'
t_LPAR = r'\('
t_RPAR = r'\)'

### add code for inequality, multiplication, division and numbers ###

def t_ID(t):
    r'[a-z]+'
    t.type = reserved.get(t.value, 'ID')
    ### add code for reserved words using the dictionary above ###
    return t

def t_NUM(t):
    r'[0-9]+'
    return t

# rule to track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# rule to ignore whitespace
t_ignore = ' \t'

# error handling rule
def t_error(t):
    print("lexical error: illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)

def indent(s, level):
    return '    '*level + s + '\n'

class Symbol_Table:
    '''A symbol table maps identifiers to locations.'''
    def __init__(self):
        self.symbol_table = {}
    def size(self):
        '''Returns the number of entries in the symbol table.'''
        return len(self.symbol_table)
    def location(self, identifier):
        '''Returns the location of an identifier. If the identifier is not in
           the symbol table, it is entered with a new location. Locations are
           numbered sequentially starting with 0.'''
        if identifier in self.symbol_table:
            return self.symbol_table[identifier]
        index = len(self.symbol_table)
        self.symbol_table[identifier] = index
        return index

class Label:
    def __init__(self):
        self.current_label = 0
    def next(self):
        '''Returns a new, unique label.'''
        self.current_label += 1
        return 'l' + str(self.current_label)

def indent(s, level):
    return '    '*level + s + '\n'

# Each of the following classes is a kind of node in the abstract syntax tree.
# indented(level) returns a string that shows the tree levels by indentation.
# code() returns a string with JVM bytecode implementing the tree fragment.
# true_code/false_code(label) jumps to label if the condition is/is not true.
# Execution of the generated code leaves the value of expressions on the stack.

class Program_AST:
    def __init__(self, program):
        self.program = program
    def __repr__(self):
        return repr(self.program)
    def indented(self, level):
        return self.program.indented(level)
    def code(self):
        program = self.program.code()
        local = symbol_table.size()
        java_scanner = symbol_table.location('Java Scanner')
        return '.class public Program\n' + \
               '.super java/lang/Object\n' + \
               '.method public <init>()V\n' + \
               'aload_0\n' + \
               'invokenonvirtual java/lang/Object/<init>()V\n' + \
               'return\n' + \
               '.end method\n' + \
               '.method public static main([Ljava/lang/String;)V\n' + \
               '.limit locals ' + str(local) + '\n' + \
               '.limit stack 1024\n' + \
               'new java/util/Scanner\n' + \
               'dup\n' + \
               'getstatic java/lang/System.in Ljava/io/InputStream;\n' + \
               'invokespecial java/util/Scanner.<init>(Ljava/io/InputStream;)V\n' + \
               'astore ' + str(java_scanner) + '\n' + \
               program + \
               'return\n' + \
               '.end method\n'

class Statements_AST:
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        result = repr(self.statements[0])
        for st in self.statements[1:]:
            result += '; ' + repr(st)
        return result
    def indented(self, level):
        result = indent('Statements', level)
        for st in self.statements:
            result += st.indented(level+1)
        return result
    def code(self):
        result = ''
        for st in self.statements:
            result += st.code()
        return result

class If_AST:
    def __init__(self, condition, then):
        self.condition = condition
        self.then = then
    def __repr__(self):
        return 'if ' + repr(self.condition) + ' then ' + \
                       repr(self.then) + ' end'
    def indented(self, level):
        return indent('If', level) + \
               self.condition.indented(level+1) + \
               self.then.indented(level+1)
    def code(self):
        l1 = label_generator.next()
        return self.condition.false_code(l1) + \
               self.then.code() + \
               l1 + ':\n'

class If_Else_AST:
    def __init__(self, condition, then, next_condition):
        self.condition = condition
        self.then = then
        self.next_condition = next_condition
    def __repr__(self):
        return 'if ' + repr(self.condition) + ' then ' + \
                       repr(self.then) + ' else ' + repr(next_condition) + ' end'
    def indented(self, level):
        return indent('If-Else', level) + \
               self.condition.indented(level+1) + \
               self.then.indented(level+1) + \
               self.next_condition.indented(level+1)    
    def code(self):
        l1 = label_generator.next()
        l2 = label_generator.next()
        return self.condition.false_code(l1) + \
               self.then.code() + \
               l1 + ':\n' + \
               self.next_condition.code() + \
               l2 + ':\n'

class While_AST:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return 'while ' + repr(self.condition) + ' do ' + \
                          repr(self.body) + ' end'
    def indented(self, level):
        return indent('While', level) + \
               self.condition.indented(level+1) + \
               self.body.indented(level+1)
    def code(self):
        l1 = label_generator.next()
        l2 = label_generator.next()
        return l1 + ':\n' + \
               self.condition.false_code(l2) + \
               self.body.code() + \
               'goto ' + l1 + '\n' + \
               l2 + ':\n'

class Assign_AST:
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression
    def __repr__(self):
        return repr(self.identifier) + ':=' + repr(self.expression)
    def indented(self, level):
        return indent('Assign', level) + \
               self.identifier.indented(level+1) + \
               self.expression.indented(level+1)
    def code(self):
        loc = symbol_table.location(self.identifier.identifier)
        return self.expression.code() + \
               'istore ' + str(loc) + '\n'

class Write_AST:
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return 'write ' + repr(self.expression)
    def indented(self, level):
        return indent('Write', level) + self.expression.indented(level+1)
    def code(self):
        return 'getstatic java/lang/System/out Ljava/io/PrintStream;\n' + \
               self.expression.code() + \
               'invokestatic java/lang/String/valueOf(I)Ljava/lang/String;\n' + \
               'invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V\n'

class Read_AST:
    def __init__(self, identifier):
        self.identifier = identifier
    def __repr__(self):
        return 'read ' + repr(self.identifier)
    def indented(self, level):
        return indent('Read', level) + self.identifier.indented(level+1)
    def code(self):
        java_scanner = symbol_table.location('Java Scanner')
        loc = symbol_table.location(self.identifier.identifier)
        return 'aload ' + str(java_scanner) + '\n' + \
               'invokevirtual java/util/Scanner.nextInt()I\n' + \
               'istore ' + str(loc) + '\n'

class Comparison_AST:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return repr(self.left) + self.op + repr(self.right)
    def indented(self, level):
        return indent(self.op, level) + \
               self.left.indented(level+1) + \
               self.right.indented(level+1)
    def true_code(self, label):
        op = { '<':'if_icmplt', '=':'if_icmpeq', '>':'if_icmpgt',
               '<=':'if_icmple', '!=':'if_icmpne', '>=':'if_icmpge' }
        return self.left.code() + \
               self.right.code() + \
               op[self.op] + ' ' + label + '\n'
    def false_code(self, label):
        # Negate each comparison because of jump to "false" label.
        op = { '<':'if_icmpge', '=':'if_icmpne', '>':'if_icmple',
               '<=':'if_icmpgt', '!=':'if_icmpeq', '>=':'if_icmplt' }
        return self.left.code() + \
               self.right.code() + \
               op[self.op] + ' ' + label + '\n'

class Expression_AST:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return '(' + repr(self.left) + self.op + repr(self.right) + ')'
    def indented(self, level):
        return indent(self.op, level) + \
               self.left.indented(level+1) + \
               self.right.indented(level+1)
    def code(self):
        op = { '+':'iadd', '-':'isub', '*':'imul', '/':'idiv' }
        return self.left.code() + \
               self.right.code() + \
               op[self.op] + '\n'

class Number_AST:
    def __init__(self, number):
        self.number = number
    def __repr__(self):
        return self.number
    def indented(self, level):
        return indent(self.number, level)
    def code(self): # works only for short numbers
        return 'sipush ' + self.number + '\n'

class Identifier_AST:
    def __init__(self, identifier):
        self.identifier = identifier
    def __repr__(self):
        return self.identifier
    def indented(self, level):
        return indent(self.identifier, level)
    def code(self):
        loc = symbol_table.location(self.identifier)
        return 'iload ' + str(loc) + '\n'

# --------------------------------------------------------------------
#  Parser - Productions defined using the yacc library of PLY
# --------------------------------------------------------------------
"""
PLYs grammars are written in BNF. Each rule has a non-terminal on the
left-hand side and can have a mixture of non-terminals and terminals on
the right-hand side. Terminals are the tokens produced by the scanner.

PLY allows an action to be performed after a rule is reduced, as in
the following example:

    def p_rule_name(p):
        'A : B C D'
        p[0] = p[1] + p[2] + p[3]

The function's name must start with 'p_'. The BNF rule is the docstring
of the function. Separate the items of the BNF rule including the colon
by a space.

The parameter p of the function is a list containing the values of a
synthesised attribute for each item in the BNF rule. In the above
example, the attribute value of A is p[0], that of B is p[1], and so on.
When the function is called, p[1:] will have values for the attribute
of each item on the right-hand side of the BNF rule. The function must
set p[0] to the attribute value of the left-hand side non-terminal.
Values in p[1:] are determined by the parser if the corresponding item
is a non-terminal, and are set to t.value from the scanner if the item
is a terminal token t.
"""


precedence = (
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV'),
    ('left', 'ELSE', 'IF')
)

def p_program(p):
    'Program : Statements'
    p[0] = Program_AST(p[1])

def p_statements_statement(p):
    'Statements : Statement'
    p[0] = Statements_AST([p[1]])

def p_statements_statements(p):
    'Statements : Statements SEM Statement'
    sts = p[1].statements
    sts.append(p[3])
    p[0] = Statements_AST(sts)

def p_statement(p):
    '''Statement : If
                 | While
                 | Read
                 | Write
                 | Assignment'''
    p[0] = p[1]

def p_if(p):
    '''If : IF Comparison THEN Statements END
          | IF Comparison THEN Statements ELSE Statements END'''
    if p[5] == 'end':
        p[0] = If_AST(p[2], p[4])
    elif p[5] == 'else':
        p[0] = If_Else_AST(p[2], p[4], p[6])


def p_while(p):
    'While : WHILE Comparison DO Statements END'
    p[0] = While_AST(p[2], p[4])

def p_assignment(p):
    'Assignment : Id BEC Expression'
    p[0] = Assign_AST(p[1], p[3])

def p_comparison(p):
    'Comparison : Expression Relation Expression'
    p[0] = Comparison_AST(p[1], p[2], p[3])

def p_relation(p):
    '''Relation : EQ
                | NEQ
                | LESS
                | LEQ
                | GRTR
                | GEQ'''
    p[0] = p[1]

def p_expression_binary(p):
    '''Expression : Expression ADD Expression
                  | Expression SUB Expression
                  | Expression MUL Expression
                  | Expression DIV Expression'''
    p[0] = Expression_AST(p[1], p[2], p[3])

def p_expression_parenthesis(p):
    'Expression : LPAR Expression RPAR'
    p[0] = p[2]

def p_expression_num(p):
    'Expression : NUM'
    p[0] = Number_AST(p[1])

def p_expression_id(p):
    'Expression : Id'
    p[0] = p[1]

def p_id(p):
    'Id : ID'
    p[0] = Identifier_AST(p[1])
    
def p_read(p):
    'Read : READ Id'
    p[0] = Read_AST(p[2])
    
def p_write(p):
    'Write : WRITE Expression'
    p[0] = Write_AST(p[2])    

def p_error(p):
    print("syntax error")
    sys.exit()
    
scanner = lex.lex()
symbol_table = Symbol_Table()
symbol_table.location('Java Scanner') # fix a location for the Java Scanner
label_generator = Label()

# Uncomment the following to test the scanner without the parser.
# Show all tokens in the input.
#
# scanner.input(sys.stdin.read())
#
# for token in scanner:
#     if token.type in ['NUM', 'ID']:
#         print(token.type, token.value)
#     else:
#         print(token.type)
# sys.exit()

# Call the parser.

prgm = """
n := 5;
if n < 6 then
 n := 6
else
  if n < 7 then
   n := 7
  end
end
"""

parser = yacc.yacc()
#ast = parser.parse(sys.stdin.read(), lexer=scanner)
ast = parser.parse(prgm, lexer=scanner)

# Uncomment the following to test the parser without the code generator.
# Show the syntax tree with levels indicated by indentation.
#
# print(ast.indented(0), end='')
# sys.exit()

# Call the code generator.

# Translate the abstract syntax tree to JVM bytecode.
# It can be assembled to a class file by Jasmin: http://jasmin.sourceforge.net/

print(ast.code(), end='')
