# ***** Lexical utilities *****
CHARSET = '0123456789#\()ABCDEFGHJKILMNOPQRSTUVWXYZabcdefghjkilmnopqrstuvwxyz/!@#$%^&*+-=_?\'\"~><,.;{}[]|`\n\t '

def create_transitions(start_state:str|int, end_state:str|int, charset:str=CHARSET, default_excluded:str=None, add_EOF:bool=False) -> dict:
    transitions = {}
    if default_excluded:
        for c in default_excluded:
            charset = charset.replace(c, '')
    for symbol in charset:
        transitions[(start_state, symbol)] = end_state
    if add_EOF:
        transitions[(start_state, '')] = end_state
    return transitions


def join_transitions(*args) -> dict:
    transition_table = {} 
    for transition in args:
        transition_table.update(transition)
    return transition_table
        
    
# ***** Grammar utilities *****        
#   P = {'<expr>': '<imm> | (prim <expr>)'}
#   expand(p of P) -> <set string of terminal/non-terminals>
#   expand(p['<expr>']) -> ['<imm>', '(prim <expr>)']
def expand_p(p:str) -> list[str]:
    opts = list(map(lambda x: x.strip(), p.split('|')))
    return opts


#   split(p of P) -> <set of terminal/non-terminals>
#   split('(prim <expr>)') -> {0: '(', 1: 'prim', 2: '<expr>', 3: ')'}
#   FIXME: {'le', 'let', 'i'}, 'let i' -> {0: le, 0: let, 2: i}
def split_p(p:str, symbols:list[str]) -> dict:
    res = {}
    for i in symbols:
        idx = -1
        count = p.count(i)
        while count:
            idx = p.index(i, idx+1)
            res[idx] = i
            count -= 1
    return res 


def is_nonterminal(symbol: str) -> True|False:
    return bool(symbol[0] == '<' and symbol[len(symbol)-1] == '>')


#   non_terminals(bnf) -> <set of non-terminals>
def non_terminals(bnf:dict) -> set:
    return set(bnf)


#   terminals(bnf) -> <set of terminals>
def terminals(bnf:dict) -> set:
    symbols = []
    for kv in bnf.items():
        _,v = kv
        symbols.extend(v.split()) 
    res = []
    for i in symbols:
        if not is_nonterminal(i) and i != '|':
           res.append(i)
    return {s for s in res} 

# ***** Parser utilities *****
def print_parse_tree(node, indent:int=0):
    print(f"{indent*' '}{node.label}: {node.value}")
    for child in node.children:
        print_parse_tree(child, indent+4)


# ***** General utilities *****
def flatten(lst):
	return sum( ([x] if not isinstance(x, list) else flatten(x) for x in lst), [] )
