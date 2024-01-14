import sys, secrets
sys.path.append(".")
import sc.helpers


debug = False


# ***** Lexer *****
class Token(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class InvalidCharError(Exception):
    pass


class InvalidCharSequenceError(Exception):
    pass


# Deterministic finite automaton
# M = (Q, SIGMA, DELTA, q0, F)
# Q -> finite set of states
# SIGMA -> finite set of input symbols
# DELTA -> finite set of transtions function (transition table) f(q1 of Q, s of Sigma) -> q2 of Q
# q0 -> start state
# F -> finite set of accept states (final states) (subset of Q)
# TODO: Make better errors
class DFA:
    def __init__(self, states:set, symbols:set, trasitions:dict, start:any, end_states:set):
        self.states = states,
        self.symbols = symbols
        self.trasitions = trasitions
        self.start = start
        self.end_states = end_states
        
    # run(string) -> Token and (string - Token) or raise syntax error
    def run(self, string:str) -> list[Token, str]:
        if string == '':
            return Token({'type': EOF, 'value': EOF}), string
        q = self.start
        token = ''
        while True:
            if debug:
                breakpoint() 
            char = string[0] if len(string) > 0 else ''
            if char not in self.symbols and char != '':
                raise InvalidCharError(f'Invalid character: {char}')
            q = self.trasitions.get((q, char), None)
            if not q:
                raise InvalidCharSequenceError(f'Invalid character sequence: {token+char}')
            if q in self.end_states:
                break
            token += char
            string = string[1:]
        return Token({'type': q, 'value': token.lstrip()}), string

# Get the next token out of input string
# All parameters for the DFA for the lexical analysis are defined here
# TODO: transform regex into DFAs
class Scanner:
    def __init__(self, string:str):
        self.string = string 
        self.cursor = 0
        states = {1, 2, '(', 4, ')', 6, 7, 8, 'bool', 10, 11, 'char', 13, 'fixnum', 'prim', 17, 'null', 20, 21, 'if'}
        symbols = set([*sc.helpers.CHARSET])
        start = 1
        end_states = {'fixnum', 'bool', 'null', 'char', '(', ')', 'prim', 'if'}
        transitions = sc.helpers.join_transitions(
            sc.helpers.create_transitions(1, 1, charset=' '),
            sc.helpers.create_transitions(1, 2, charset=')'),
            sc.helpers.create_transitions(1, 4, charset='('),
            sc.helpers.create_transitions(1, 14, charset='0123456789'),
            sc.helpers.create_transitions(1, 13, charset='-'),
            sc.helpers.create_transitions(1, 6, default_excluded='i0123456789-()\\.\n\t{}[];,|`\'\"# '),
            sc.helpers.create_transitions(1, 20, charset='i'),
            sc.helpers.create_transitions(14, 6, default_excluded='0123456789-()\\.\n\t{}[];,|`\'\"# '),
            sc.helpers.create_transitions(14, 14, charset='0123456789'),
            sc.helpers.create_transitions(13, 14, charset='0123456789'),
            sc.helpers.create_transitions(6, 6, default_excluded='()\\.\n\t{}[];,|`\'\"# '),
            sc.helpers.create_transitions(1, 7, charset='#'),
            sc.helpers.create_transitions(4, 17, charset=')'),
            sc.helpers.create_transitions(7, 10, charset='\\'),
            sc.helpers.create_transitions(10, 11),
            sc.helpers.create_transitions(7, 8, charset='tTfF'),
            sc.helpers.create_transitions(20, 21, charset='f'),
            sc.helpers.create_transitions(21, 6, default_excluded='()\\.\n\t{}[];,|`\'\"# '),
            sc.helpers.create_transitions(14, 'fixnum', charset=' )', add_EOF=True),
            sc.helpers.create_transitions(8, 'bool', charset=' )', add_EOF=True),
            sc.helpers.create_transitions(11, 'char', charset=' )', add_EOF=True),
            sc.helpers.create_transitions(17, 'null', charset=' )', add_EOF=True),
            sc.helpers.create_transitions(6, 'prim', charset=' )', add_EOF=True),
            sc.helpers.create_transitions(21, 'if', charset=' ', add_EOF=True),
            sc.helpers.create_transitions(2, ')', add_EOF=True),
            sc.helpers.create_transitions(4, '(', default_excluded=')', add_EOF=True))
        self.d0 = DFA(states, symbols, transitions, start, end_states)
        
    def next_token(self) -> dict:
        token, out_string = self.d0.run(self.string)
        self.string = out_string
        if debug:
            breakpoint()
        return token

# ***** Parser *****
class ParsingError(Exception):
    pass

class InvalidSyntaxError(Exception):
    pass
    

class ParseTreeNode:
    def __init__(self, label:str, value:any=None):
        self.children = []
        self.label = label
        self.value = value
        self.id = secrets.token_hex(6)

    def add_children(self, *args):
        for child in args:
            self.children.append(child)
    def __repr__(self) -> str:
        #return f'NODEID: {self.id}, {self.label}: (value: {self.value}, {[child.label for child in self.children]})'
        return f'({self.label}, {self.value})'

# Grammar # G = (V, SIGMA, R, S) # V -> finite set of non-terminals # SIGMA -> finite set of terminals # R -> production rules -> f(v of V) -> [s of Sigma/v of V]+ # R is a set of P -> P = (alpha, beta) -> alpha of V -> beta is string of terminal/non-terminals # S -> start non-terminal
class Grammar:
    def __init__(self, nonterminals:set[str], terminals:set[str], productions:dict, start:str):
        self.nonterminals = nonterminals
        self.terminals = terminals
        self.productions = productions
        self.start = start


#   TODO: add left recursion elimination process
#   FIXME: extra closing parents does not raise any error
EPSILON = '_EPSILON_'
EOF = '$'
DEFAULT_BNF = {
    '<expr>': '<atom> | <list>',
    '<list>': '( <elements> )',
    '<elements>': '<expr> <expr_tail> | <conditional>',
    '<conditional>': 'if <expr> <expr> <expr>',
    '<expr_tail>': '<expr> <expr_tail> | _EPSILON_',
    '<atom>': 'prim | <imm>',
    '<imm>': 'fixnum | bool | char | null'
#    '<P>': '<E>',
#    '<E>': '<atom> | ( <E> <Es> )',
#    '<Es>': '<E> <Es> | _EPSILON_',
}
GRAMMAR = Grammar(
    sc.helpers.non_terminals(DEFAULT_BNF),
    sc.helpers.terminals(DEFAULT_BNF),
    DEFAULT_BNF,
    '<expr>')


# LL(1) Parser
class Parser:
    def __init__(self, grammar:Grammar=GRAMMAR):
        self.grammar = grammar
        self.expanded_p = {}
        for k, v in grammar.productions.items():
            self.expanded_p[k] = sc.helpers.expand_p(v)
        self.follow_visited_set = set()
        self.table = self.parsing_table()
   
    # first(x of V or x of SIGMA) -> <set of t of SIGMA such as x can start with any of t> or <x if x of SIGMA>
    def first(self, x:str) -> list[str]:
        if not sc.helpers.is_nonterminal(x) and x in self.grammar.terminals:
            return [x]
        res = []
        for i in sc.helpers.expand_p(self.grammar.productions[x]):
            first_symbol = sc.helpers.split_p(i, list(self.grammar.terminals.union(self.grammar.nonterminals)))[0]
            res.append(self.first(first_symbol))
        return sc.helpers.flatten(res)

            
    # follow(x of V) -> <set of t of SIGMA which can directly came after x>
    # $ is EOF
    # eg. if A -> aB then follow(B) = follow(A)
    # eg. for A -> Bp, first(p) is in follow(B)
    # eg. for A -> Bq, EPSILON in first(q) -> follow(B) = first(q) - EPSILON U follow(A)
    # TODO: Add visited_set as recursive variable rather than class attribute (ATTENTION TO MUTABLE DEFAULT PROBLEM)
    def follow(self, x:str) -> list[str]:
        if x in self.follow_visited_set:
            return []
        if not sc.helpers.is_nonterminal(x) and x in self.grammar.terminals:
            return x
        res = []
        if x == self.grammar.start:
            res.append(EOF)
        for nonterminal, productions in self.expanded_p.items():
            for p in productions:
                if x in p:
                    self.follow_visited_set.add(x)
                    symbols = sc.helpers.split_p(p, self.grammar.terminals.union(self.grammar.nonterminals))
                    symbols = sorted(symbols.items())
                    for i, kv in enumerate(symbols):
                        _, v = kv
                        if v == x:
                            if symbols[-1:][0][1] == v:
                                res.append(self.follow(nonterminal))
                            else:
                                next_firsts = self.first(symbols[i+1][1])
                                if EPSILON in next_firsts:
                                    next_firsts.remove(EPSILON)
                                    res.append(self.follow(nonterminal))
                                res.append(next_firsts)
        return sc.helpers.flatten(res)

    def parsing_table(self):
       #    | a | b |
       #  c | 1 | 2 |
       #  d | 3 | 4 |
       #
       #  table = {(a,c): 1, (a,d): 3, (b,c): 2, (b,d): 4}
        table = {}
        for t in self.grammar.terminals.union({EOF}):
            for nt in self.grammar.nonterminals:
                table[(t,nt)] = None
        for nt, prods in self.expanded_p.items():
            for p in prods:
                firsts = self.first(sc.helpers.split_p(p, self.grammar.nonterminals.union(self.grammar.terminals))[0])
                for t in firsts:
                    table[(t, nt)] = p
                if EPSILON in firsts:
                    follows = self.follow(nt)
                    for t in follows:
                        table[(t, nt)] = EPSILON
                    if EOF in follows:
                        table[(EOF, nt)] = EPSILON
        return table
    
    # Produce parse tree if syntax is valid or raise syntax error
    def run(self, input_string:str) -> ParseTreeNode:
        scanner = Scanner(input_string)
        stack = [('marker', 1, 'root'), EOF]
        stack.append(self.grammar.start)
        semantic_stack = []
        next_token = scanner.next_token() 
        while(len(stack) > 0):
            if debug:
                breakpoint()
            top = stack[-1:][0]
            if top in self.grammar.terminals:
                if top == EPSILON:
                    semantic_stack.append(ParseTreeNode(stack.pop(), value=EPSILON))
                elif top == next_token.type:
                    semantic_stack.append(ParseTreeNode(stack.pop(), value=next_token.value))
                    next_token = scanner.next_token()
                else:
                    raise InvalidSyntaxError(f'Invalid syntax: expected {top} got {next_token.type}')
            elif top == EOF:
                stack.pop()

            # top == ('marker', len, <symbol>)
            elif isinstance(top, tuple):
                stack.pop()
                new_node = ParseTreeNode(top[2])
                n = top[1]
                nodes = []
                while n > 0:
                    nodes.append(semantic_stack.pop())
                    n = n-1
                new_node.add_children(*nodes[::-1])
                semantic_stack.append(new_node) 
            elif top in self.grammar.nonterminals:
                p = self.table.get((next_token.type, top), None)
                if p:
                    stack.pop()
                    symbols = sorted(sc.helpers.split_p(p, self.grammar.terminals.union(self.grammar.nonterminals)).items(), reverse=True)
                    stack.append(('marker', len(symbols), top))
                    for s in symbols:
                        stack.append(s[1])
                else:
                    raise InvalidSyntaxError(f'Invalid syntax: expected {top} got {next_token.type}')
        return semantic_stack.pop()


# ***** Testing *****
if __name__ == '__main__':
    debug = True if sys.argv[-1:][0] in ('-d', '--debug') else False
    print('***** Parser test *****')
    p = Parser()
    while True:
        input_string = input('> ').strip()
        root = p.run(input_string)
        sc.helpers.print_parse_tree(root)

