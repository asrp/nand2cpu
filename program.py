def unpack_str(prefix, array=None):
    if array is None:
        array = prefix + 's'
    return '    ' + ', '.join("{}{}".format(prefix, i)
                              for i in range(15, -1, -1)) +\
            ' = unpack({})\n'.format(array)

def pack_str(prefix, array=None):
    if array is None:
        array = prefix + 's'
    return '    {} = pack('.format(array) +\
        ', '.join("{}{}".format(prefix, i)
                  for i in range(15, -1, -1)) + ')\n'

def bin_list(num, length=16):
    return map(int, list(bin(num)[2:].zfill(length)))

program = """
not(a) = nand(a, a)
and(a, b) = not(nand(a, b))
or(a, b) = nand(not(a), not(b))
xor(a, b) = or(and(a, not(b)), and(not(a), b))
add1(a, b) = and(a, b), xor(a, b)
or3(a, b, c) = or(a, or(b, c))
xor3(a, b, c) = xor(a, xor(b, c))
add(a, b, c) = or3(and(a, b), and(b, c), and(a, c)), xor3(a, b, c)
def add2bits(a1, a0, b1, b0, c) -> twos_high, twos_low, unit_low:
    unit_high, unit_low = add(a0, b0, c)
    twos_high, twos_low = add(a1, b1, unit_high)

select(sel, d1, d0) = or(and(sel, d1), and(not(sel), d0))
def latch(store_mode, value) -> out:
    out = select(store_mode, value, out)

flip_flop(store_mode, value, clock) =
  latch(clock, latch(and(store_mode, not(clock)), value))

def register16(store_mode, bits, clock) -> out:
""" +\
unpack_str('bit') + pack_str('out', 'out') +\
''.join("    out{0} = flip_flop(store_mode, bit{0}, clock)\n".format(i)
          for i in range(16)) +\
"""
def not16(bits) -> out:
""" +\
unpack_str('bit') + pack_str('out', 'out') +\
''.join("    out{0} = not(bit{0})\n".format(i) for i in range(16)) +\
"""
def and16(as, bs) -> out:
""" +\
unpack_str('a') + unpack_str('b') + pack_str('out', 'out') +\
''.join("    out{0} = and(a{0}, b{0})\n".format(i) for i in range(16)) +\
"""
def or16(bits) -> out15:
""" +\
unpack_str('bit') +\
'    out1 = or(bit1, bit0)\n' +\
''.join("    out{1} = or(out{0}, bit{1})\n".format(i, i+1)
          for i in range(1, 16)) +\
"""
def add16(as, bs) -> out:
""" +\
unpack_str('a') + unpack_str('b') + pack_str('out', 'out') +\
'    carry1, out0 = add1(a0, b0)\n' +\
''.join("    carry{1}, out{0} = add(carry{0}, a{0}, b{0})\n".format(i, i+1)
          for i in range(1, 16)) +\
"""
def select16(sel, ones, zeros) -> out:
""" +\
unpack_str('one') + unpack_str('zero') + pack_str('out', 'out') +\
'\n'.join("    out{0} = select(sel, one{0}, zero{0})".format(i)
          for i in range(16)) +\
"""
def is_negative(bits) -> bit15:
""" +\
unpack_str('bit') +\
"""
def increment(x16) -> out:
    minus1 = add16(x16, not16(x16))
    out = add16(x16, not16(add16(minus1, minus1)))

def counter(store_mode, bits, clock) -> out:
    stored_new_value = register16(not(clock), new_value, clock)
    new_value = select16(store_mode, bits, increment(old_value))
    old_value = register16(clock, stored_new_value, not(clock))
    out = select16(clock, stored_new_value, old_value)

switch(sel, value) = and(sel, value), and(not(sel), value)

def RAM(address, store_mode, bits, clock) -> out:
    reg1mode, reg0mode = switch(address, store_mode)
    reg1 = register16(reg1mode, bits, clock)
    reg0 = register16(reg0mode, bits, clock)
    out = select16(address, reg1, reg0)

def sign_modifier(zero, neg, value) -> out:
    zeroed = select16(zero, zero_16(zero), value)
    out = select16(neg, not16(zeroed), zeroed)

is_zero16(bits) = not(or16(bits))

def ALU(opers, raw_x, raw_y) -> out:
    zero_x, neg_x, zero_y, neg_y, oper, neg = unpack(opers)
    x = sign_modifier(zero_x, neg_x, raw_x)
    y = sign_modifier(zero_y, neg_y, raw_y)
    result = select16(oper, add16(x, y), and16(x, y))
    out = select16(neg, not16(result), result)

def compare_to_zero(comparator, x) -> out:
    lt, eq, gt = unpack3(comparator)
    x_zero = is_zero16(x)
    x_neg = is_negative(x)
    x_pos = and(not(x_zero), not(x_neg))
    out = or3(and(lt, x_neg), and(eq, x_zero), and(gt, x_pos))

def storage(write_destination, value, clock) -> address_reg, data_reg, ram:
    write_address, write_data, write_ram = unpack(write_destination)
    address_reg = register16(write_address, value, clock)
    data_reg = register16(write_data, value, clock)
""" +\
unpack_str('address_reg', 'address_reg') +\
"""    ram = RAM(write_ram, address_reg0, value, clock)

def instruction_decoder(instr) -> out:
""" +\
unpack_str('aux', 'aux') +\
unpack_str('instr', 'instr') +\
"""    is_comp = id(instr15)
    aux = select16(is_comp, instr, zero_16(is_comp))
    data = select16(is_comp, zero_16(is_comp), instr)
    out = pack6(is_comp, aux12, pack6(aux11, aux10, aux9, aux8, aux7, aux6),
          pack3(aux5, or(not(is_comp), aux4), aux3),
          pack3(aux2, aux1, aux0),
          data)

def control_unit(instr, clock) -> need_to_jump, address_reg:
    is_comp, alu_operand, ALU_opers, write_destination, comparator, value = unpack6(instruction_decoder(instr))
    need_to_jump = compare_to_zero(comparator, alu_output)
    y = select16(alu_operand, address_reg, ram_at_addr)
    alu_output = ALU(ALU_opers, data_reg, y)
    ram_input = select16(is_comp, alu_output, value)
    address_reg, data_reg, ram_at_addr = storage(write_destination, ram_input, clock)

rom(address) = RAM(address, zero_1(address), zero_16(address), zero_1(address))
program_engine(need_to_jump, address_reg, clock) = 
  manual_rom(counter(need_to_jump, address_reg, clock))

# Don't need any output actually
def CPU(clock) -> instr:
    instr = program_engine(need_to_jump, address_reg, clock)
    need_to_jump, address_reg = control_unit(instr, clock)
"""
