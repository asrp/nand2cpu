from parse import *

print "and"
print gates['and'](True, True)
print gates['and'](True, False)
print gates['and'](True, True)

print "or"
print gates['or'](False, False)
print gates['or'](True, False)
print gates['or'](False, False)

print "xor"
print gates['xor'](True, True)
print gates['xor'](True, False)
print gates['xor'](True, True)

print "add1"
print gates['add1'](True, True)
print gates['add1'](True, False)
print gates['add1'](True, True)

print "add"
print gates['add'](True, True, True)
print gates['add'](True, False, True)
print gates['add'](False, False, False)

print "add2bits"
print map(int, gates['add2bits'](1, 0, 1, 0, 0))
print map(int, gates['add2bits'](1, 0, 1, 1, 0))
print map(int, gates['add2bits'](1, 0, 1, 1, 1))

print "select"
print gates['select'](1, 1, 0)
print gates['select'](0, 1, 0)

print "latch"
for input_ in [[1, 1], [0, 1], [0, 0], [1, 0], [0, 1]]:
    print gates['latch'](input_)

val1 = [1] * 8 + [0] * 8
val2 = [0] * 8 + [1] * 8

def rec_int(x):
    if isinstance(x, list):
        return map(rec_int, x)
    return int(x)

print "register16"
print map(rec_int, gates['register16'](1, val1, 1))
print map(rec_int, gates['register16'](1, val1, 0))
print map(rec_int, gates['register16'](0, val2, 1))
print map(rec_int, gates['register16'](1, val2, 0))
print map(rec_int, gates['register16'](1, val2, 1))
print map(rec_int, gates['register16'](1, val1, 0))

print "not16"
print map(rec_int, gates['not16'](bin_list(17432)))

print "add16"
print map(rec_int, gates['add16'](bin_list(4328), bin_list(17432)))
print map(rec_int, bin_list(4328 + 17432))

print "increment"
print map(rec_int, gates['increment'](bin_list(17432)))
print map(rec_int, bin_list(17432 + 1))
print map(rec_int, gates['increment'](bin_list(17433)))

print "counter"
print map(rec_int, gates['counter'](1, bin_list(17432), 0))
print map(rec_int, gates['counter'](0, bin_list(17432), 1))
print map(rec_int, gates['counter'](0, bin_list(17432), 0))
print map(rec_int, gates['counter'](0, bin_list(17432), 1))
print map(rec_int, gates['counter'](0, bin_list(17432), 0))
print map(rec_int, gates['counter'](0, bin_list(17432), 1))
print map(rec_int, gates['counter'](0, bin_list(17432), 0))

print "RAM"
print map(rec_int, gates['RAM'](0, 1, bin_list(17432), 0))
print map(rec_int, gates['RAM'](0, 1, bin_list(17432), 1))
print map(rec_int, gates['RAM'](1, 1, bin_list(4328), 0))
print map(rec_int, gates['RAM'](1, 1, bin_list(4328), 1))
print map(rec_int, gates['RAM'](0, 0, bin_list(1234), 0))
print map(rec_int, gates['RAM'](0, 0, bin_list(1234), 1))
print map(rec_int, gates['RAM'](1, 0, bin_list(1234), 0))
print map(rec_int, gates['RAM'](1, 0, bin_list(1234), 1))

print "sign_modifier"
print map(rec_int, gates['sign_modifier'](1, 0, bin_list(4328)))
print map(rec_int, gates['sign_modifier'](0, 0, bin_list(4328)))
print map(rec_int, gates['sign_modifier'](1, 1, bin_list(4328)))
print map(rec_int, gates['sign_modifier'](0, 1, bin_list(4328)))

# zero_x, neg_x, zero_y, neg_y, oper, neg
# oper = 1:"add", 0:"and"
print "ALU"
opers = [0, 0, 0, 0, 1, 0]
print map(rec_int, gates['ALU'](opers, bin_list(4328), bin_list(17432)))
opers = [0, 0, 0, 0, 1, 1]
print map(rec_int, gates['ALU'](opers, bin_list(4328), bin_list(17432)))

print "is_zero16"
print map(rec_int, gates['is_zero16'](bin_list(0)))
print map(rec_int, gates['is_zero16'](bin_list(1234)))
print "compare_to_zero"
print map(rec_int, gates['compare_to_zero']([0, 1, 0], bin_list(0)))
print map(rec_int, gates['compare_to_zero']([0, 1, 0], bin_list(1)))
print map(rec_int, gates['compare_to_zero']([0, 1, 1], bin_list(1)))
print map(rec_int, gates['compare_to_zero']([1, 1, 0], bin_list(1)))

print "instruction_decoder"
#print gates['instruction_decoder'](bin_list(4328))
print map(rec_int, gates['instruction_decoder'](bin_list(4328)))

print "control_unit"
#print gates['control_unit'](bin_list(4328))
print map(rec_int, gates['control_unit'](bin_list(4328)))

print "program_engine"
# Should print 1,2,3,1
#print gates['control_unit'](bin_list(4328))
print map(rec_int, gates['program_engine'](0, bin_list(0), 1))
print map(rec_int, gates['program_engine'](0, bin_list(0), 0))
print map(rec_int, gates['program_engine'](0, bin_list(0), 1))
print map(rec_int, gates['program_engine'](0, bin_list(0), 0))
print map(rec_int, gates['program_engine'](0, bin_list(0), 1))
print map(rec_int, gates['program_engine'](1, bin_list(0), 0))
print map(rec_int, gates['program_engine'](0, bin_list(0), 1))
