import sys, copy
sys.path.append(".")
import sc.helpers
import sc.parser


debug = False

# Increase limit for extremly long nested expression
# NOTE: Be careful when increasing it above default 1000
# TODO: Add automatic increase based on Parse Tree maximum depth
sys.setrecursionlimit(5000)

# ***** Code Generation *****
class CompilerError(Exception):
    pass

#   Grammar
#   <expr> ::= <atom> | <list>
#   <list> ::= ( <elements> )
#   <elements> ::= <expr> <expr_tail> | <conditional>
#   <conditional> ::= if <expr> <expr> <expr>
#   <expr_tail> ::= <expr> <expr_tail> | _EPSILON_
#   <atom> ::= if | prim | <imm>
#   <imm> ::= fixnum | bool | char | null

def compile_to_asm(node:sc.parser.ParseTreeNode) -> str:
    code = ''
    if node.label == 'root':
        for child in node.children:
            if child.label == '<expr>':
                code += emit_expr(child)
    else:
        raise CompilerError
    template = f'.section __TEXT,__text\n.globl _scheme_entry\n_scheme_entry:\n{code}\tret'
    return template.strip()



expr = {
'<atom>': lambda x: atom[x.children[0].label](x.children[0]),
'<list>': lambda x: list_[x.children[1].label](x.children[1]),
}


list_ = {
'(': lambda x: '',
'<elements>': lambda x: emit_elements(x),
')': lambda x: ''
}


elements = {
'<expr>': lambda x: emit_expr(x),
'<expr_tail>': lambda x: emit_expr_tail(x),
'<conditional>': lambda x: emit_conditional(x),
}


expr_tail = {
'<expr>': lambda x: emit_expr(x),
'<expr_tail>': lambda x: emit_expr_tail(x),
sc.parser.EPSILON: lambda x: '',
}


atom = {
'<imm>': lambda x: f'\tmovl ${immediate_repr(x)}, %eax\n',
'if': lambda x: emit_if(x),
'prim': lambda x: emit_prim(x)
}


conditionals = {
'if': lambda x: f''
}


# TODO: type encoding should be defined in one place and every related ops should dinamically adapt
primitives = {
'fxadd1': lambda x: f'\tadd ${immediates.get("fixnum")(1)}, %eax\n',
'fxsub1': lambda x: f'\tsub ${immediates.get("fixnum")(1)}, %eax\n',
'char->fixnum': lambda x: '\tshr $6, %eax\n',
'fixnum->char':lambda x: '\tshl $6, %eax\n\txor $15, %eax\n',
'fxzero?': lambda x: '\tcmp $0, %eax\n\tsete %al\n\tmovzx %al, %eax\n\tshl $6, %eax\n\txor $47, %eax\n',
'null?': lambda x: '\tcmp $63, %eax\n\tsete %al\n\tmovzx %al, %eax\n\tshl $6, %eax\n\txor $47, %eax\n',
'not': lambda x: '\tcmp $47, %eax\n\tsete %al\n\tmovzx %al, %eax\n\tshl $6, %eax\n\txor $47, %eax\n',
'fixnum?': lambda x: '\tand $3, %eax\n\tcmp $0, %eax\n\tsete %al\n\tmovzx %al, %eax\n\tshl $6, %eax\n\txor $47, %eax\n',
'boolean?': lambda x: '\tand $191, %eax\n\tcmp $47, %eax\n\tsete %al\n\tmovzx %al, %eax\n\tshl $6, %eax\n\txor $47, %eax\n',
'char?': lambda x: '\tand $255, %eax\n\tcmp $15, %eax\n\tsete %al\n\tmovzx %al, %eax\n\tshl $6, %eax\n\txor $47, %eax\n',
'fxlognot': lambda x: '\txor $4294967292, %eax\n'
}


# Describe how types are encoded
#
# FIXNUM: 30-bit value - 2-bit tag: 00
# BOOL: 2-bit value - 6-bit tag: 101111
# CHAR: 8-bit value - 8-bit tag: 00001111
# NULL: 00111111

immediates = {
'fixnum': lambda x: int(x) << 2,
'char': lambda x: (ord(x.replace('#\\', '')) << 8) ^ 0b00001111,
'bool': lambda x: (int(bool(x in {'#t', '#T'})) << 6) ^ 0b101111,
'null': lambda x: 0b00111111,
}


# <expr> node
def emit_expr(node:sc.parser.ParseTreeNode) -> str:
    code = ''
    for child in node.children:
        if debug: 
            breakpoint()
        res = expr[child.label](child)
        code = res + code
    return code


# <expr_tail> node
def emit_expr_tail(node:sc.parser.ParseTreeNode) -> str:
    code = ''
    for child in node.children:
        if debug:
            breakpoint()
        res = expr_tail[child.label](child)
        code = code + res
    return code


# <elements> node
def emit_elements(node:sc.parser.ParseTreeNode) -> str:
    code = ''
    for child in node.children:
        if debug:
            breakpoint()
        res = elements[child.label](child)
        code = res + code
    return code


# <conditional> node
def emit_conditional(node:sc.parser.ParseTreeNode) -> str:
    code = ''
    end_label = unique_label()
    alt_label = unique_label()
    test_cond = node.children[1]
    true_cond = node.children[2]
    false_cond = node.children[3]
    code += emit_expr(test_cond)
    code += f'\tcmp ${immediates.get("bool")("#f")}, %eax\n'
    code += f'\tje {alt_label}\n'
    code += emit_expr(true_cond)
    code += f'\tjmp {end_label}\n'
    code += f'{alt_label}:\n'
    code += emit_expr(false_cond)
    code += f'{end_label}:\n'
    return code


# Generate unique labels for jmp instructions -> L_0, L_1, L_2 ...
def unique_label(counter:list[int]=[0]) -> str:
    label = f'L_{counter[0]}'
    counter[0] += 1
    return label


# prim node
def emit_prim(node:sc.parser.ParseTreeNode) -> str:
    code = ''
    code += primitives[node.value]([])
    return code


# <imm> node
def immediate_repr(node:sc.parser.ParseTreeNode) -> int:
    if len(node.children) != 1:
        raise CompilerError
    return immediates[node.children[0].label](node.children[0].value)


# ***** Testing *****
if __name__ == '__main__':
    debug = True if '-d' in sys.argv else False
    tree = True if '-t' in sys.argv else False
    print('***** CodeGen test *****')
    p = sc.parser.Parser()
    while True:
        input_string = input('> ').strip()
        root = p.run(input_string)
        print(compile_to_asm(root))
        if tree:
            sc.helpers.print_parse_tree(root)
 
