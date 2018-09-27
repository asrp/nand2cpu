import pdb
bp = pdb.set_trace

from pymetaterp.util import simple_wrap_tree
from pymetaterp import boot_grammar, boot_tree, boot_stackless as boot, python, python_grammar
from collections import defaultdict
from sim import nand, Vertex, FuncVertex
import itertools

_grammar = boot_grammar.bootstrap + boot_grammar.extra
i1 = boot.Interpreter(simple_wrap_tree(boot_tree.tree))
match_tree = i1.match(i1.rules['grammar'][-1], _grammar)
i2 = boot.Interpreter(match_tree)
match_tree2 = i2.match(i2.rules['grammar'][-1], _grammar + boot_grammar.diff)
i3 = boot.Interpreter(match_tree2)

# Assume no nested defs for now
grammar = r"""
grammar = single*
single = NEWLINE | SAME_INDENT {def | inline} ('\n' | '\r')

inline = {NAME=func_name} "(" {names=inputs} ")" "=" spaces {func_calls}
func_calls! = func_call ("," spaces {func_call})*
func_call = {NAME=func_name} "(" {(argument ("," spaces {argument})* | void)=arguments} ")"
argument = hspaces {func_call | NAME=variable}

def = "def" hspacesp {NAME=func_name} "(" {names=inputs} ")" 
      "->" {names=outputs} ":" {body}
body! = INDENT {statement*} DEDENT
statement! = NEWLINE SAME_INDENT {names=outputs} "=" {func_call}
names! = NAME=NAME ("," {NAME=NAME})*

NEWLINE = (hspaces comment? ('\n' | '\r'))=NEWLINE
NAME = hspaces {(letter | '_') (letter | digit | '_')*}
hspaces = (' ' | '\t' | escaped_linebreak)*
hspacesp = (' ' | '\t' | escaped_linebreak)+
escaped_linebreak = '\\' {'\n'}
comment! = '#' (~'\n' {anything})*
"""

grammar += r"""
SAME_INDENT = hspaces:s ?(self.indentation[-1] == (len(s) if s != None else 0))
INDENT = ~~(NEWLINE hspaces:s) !(self.indentation.append(len(s) if s != None else 0))
DEDENT = !(self.indentation.pop())
NEWLINE = hspaces ('\n' | '\r') {} | COMMENT_LINE
COMMENT_LINE = hspaces {comment} hspaces ('\n' | '\r')
"""

grammar += boot_grammar.extra
match_tree3 = i3.match(i3.rules['grammar'][-1], grammar)
matcher = python.Interpreter(match_tree3)
matcher.source = grammar

count = -1
def gen_name(prefix):
    global count
    count += 1
    return '%s-%s' % (prefix, count)

def circuit_from_statement(statement, from_=None, to_=None, equivs=None,
                           vertices=None):
    names, root = statement
    if to_ is None:
        to_ = defaultdict(list)
    if from_ is None:
        from_ = defaultdict(list)
    for node in itertools.chain(root.descendants, [root]):
        if not isinstance(node, str):
            if node.name == "variable":
                node.vertex = str(node[0])
            elif node.name == "func_call":
                node.vertex = gen_name(node[0][0])
                vertices[node.vertex] = node
    for i, name in enumerate(names[0]):
        from_[name[0]] = (root.vertex, "out", i)
    for parent in itertools.chain(root.descendants, [root]):
        # print parent
        if isinstance(parent, str) or parent.name not in ["func_call"]:
            continue
        for i, node in enumerate(parent[1]):
            # print "Adding", node[0]
            if node.name == "variable":
                to_[node.vertex].append((parent.vertex, "in", i))
            else:
                equivs[(node.vertex, "out", 0)].append((parent.vertex, "in", i))

def circuit_from_def(def_):
    func_name, inputs, outputs, body = def_
    to_ = defaultdict(list)
    from_ = defaultdict(list)
    equivs = defaultdict(list)
    vertices = {}
    for i, name in enumerate(inputs[0]):
        from_[name[0]] = (None, "in", i)
    for i, name in enumerate(outputs[0]):
        to_[name[0]].append((None, "out", i))
    for statement in body:
        circuit_from_statement(statement, from_, to_, equivs, vertices)
    for key in from_:
        equivs[from_[key]] = to_[key]
    return func_name, len(inputs[0]), len(outputs[0]), equivs, vertices

def circuit_from_inline(inline):
    func_name, inputs, body = inline
    to_ = defaultdict(list)
    from_ = defaultdict(list)
    equivs = defaultdict(list)
    vertices = {}
    for i, name in enumerate(inputs[0]):
        from_[name[0]] = (None, "in", i)
    for i, root in enumerate(body):
        to_[(func_name[0], i)].append((None, "out", i))
        circuit_from_statement(([[[(func_name[0], i)]]], root), from_, to_, equivs, vertices)
    for key in from_:
        equivs[from_[key]] = to_[key]
    return func_name, len(inputs[0]), len(body), equivs, vertices

def unpack(args):
    return args[0]

def pack(bits):
    return [bits]

def id_(values):
    return values

def parse_bin(bitlist):
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out

rom = []

def manual_rom(args):
    (address,) = args
    print "Reading rom[%s]" % parse_bin(address)
    return [rom[parse_bin(address)]]

start_gates = {'nand': FuncVertex(nand),
               'pack': FuncVertex(pack, 16, 1, default=[[0] * 16]),
               'pack6': FuncVertex(pack, 6, 1, default=[[0] * 6]),
               'pack3': FuncVertex(pack, 3, 1, default=[[0] * 3]),
               'unpack': FuncVertex(unpack, 1, 16, default=[[[0] * 16]]),
               'unpack3': FuncVertex(unpack, 1, 3, default=[[[0] * 3]]),
               'unpack6': FuncVertex(unpack, 1, 6, default=[[[0] * 6]]),
               'id': FuncVertex(id_, 1, 1),
               'zero_1': FuncVertex(lambda args: [0], 0, 1),
               'zero_16': FuncVertex(lambda args: [[0] * 16], 1, 1, default=[0]),
               'manual_rom': FuncVertex(manual_rom, 1, 1, default=[0])}

def add_vertex(root, gates):
    global count
    count = -1
    if root.name == "inline":
        func = circuit_from_inline
    elif root.name == "def":
        func = circuit_from_def
    elif root.name == "comment":
        return
    else:
        raise Exception("Don't know how to make a vertex from %s type" % root.name)
    name, num_inputs, num_outputs, equivs, vertices = func(root)
    inner = {k: gates[v[0][0]].copy() for k, v in vertices.items()}
    gates[name[0]] = Vertex(inner, num_inputs, num_outputs, equiv=equivs)
    return gates[name[0]]

def make_gates(program, start=start_gates, debug=False):
    prog_tree = matcher.match(matcher.rules['grammar'][-1], program, debug=debug)
    gates = start.copy()
    for root in prog_tree:
        add_vertex(root, gates)
    return gates

def rec_int(x):
    if isinstance(x, list):
        return map(rec_int, x)
    return int(x)

def cpu_cycle(cpu):
    cpu(1)
    cpu(0)
    print "Program counter at", map(rec_int, cpu.vertices['program_engine-0'].vertices['counter-0'].output_values)
    print "Register a is", map(rec_int, cpu.vertices['control_unit-1'].vertices['storage-6'].vertices['register16-1'].output_values)
    print "Register d is", map(rec_int, cpu.vertices['control_unit-1'].vertices['storage-6'].vertices['register16-2'].output_values)
    print "Storage instructions", map(rec_int, cpu.vertices['control_unit-1'].vertices['storage-6'].input_values)
    print "Compare to zero input", map(rec_int, cpu.vertices['control_unit-1'].vertices['compare_to_zero-2'].input_values)
    print "Comparison result", map(rec_int, cpu.vertices['control_unit-1'].vertices['compare_to_zero-2'].output_values)
    print "Control output", map(rec_int, cpu.vertices['control_unit-1'].output_values)

if __name__ == '__main__':
    from program import program, bin_list
    gates = make_gates(program)

    # d = 3; a = d; d = 12;
    # (3) d = d - 1; if d != 0: goto a;
    rom = [0b0000000000000011, 0b1110001010100000, 0b0000000000001100,
           0b1110001110010000, 0b1110001100000101]
    rom = map(bin_list, rom)
    cpu = gates['CPU'].copy()
    for i in range(3 + 2*12):
        cpu_cycle(cpu)

    # Should give a list out of index error
    # cpu_cycle(cpu)
