A circuit description language and simulator intended for making a CPU from nand gates.

[This post](https://blog.asrpo.com/nand2cpu) describes the motivation and some internals.

Running (the default CPU with the sample preloaded into ROM)

    pip install -r requirements.txt
    python parse.py

Running your own CPU

    from parse import make_gates, rom, cpu_cycle
    program = "# Your CPU description here"
    gates = make_gates(program)
    rom[:] = [0b00, 0b10, ...] # Format this for your CPU
    while True:
        cpu_cycle(gates['CPU'])

Tests for gates used in the default CPU

    python test.py

The default CPU is based on [Nand game](https://www.nandgame.com) which itself is based on [Nand to Tetris](https://www.nand2tetris.org).
