"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.fl = 0b00000000

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""
        if len(sys.argv) != 2:
            print('Must specify a file to run.')
            print('Usage: <ls8.py> filename')
            sys.exit(1)
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for instruction in f:
                    comment_split = instruction.strip().split('#')
                    num = comment_split[0]
                    if comment_split[0] == '':
                        continue
                    val = int(num, 2)
                    self.ram[address] = val
                    address += 1

        except FileNotFoundError:
            print('File not found')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]

        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]

        elif op == 'CMP':
            if self.register[reg_a] < self.register[reg_b]:
                self.fl = 0b00000100
            elif self.register[reg_a] > self.register[reg_b]:
                self.fl = 0b00000010
            elif self.register[reg_a] == self.register[reg_b]:
                self.fl = 0b00000001

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == HLT:
                running = False

            elif ir == LDI:
                self.register[operand_a] = operand_b

            elif ir == PRN:
                print(self.register[operand_a])

            elif ir == MUL:
                self.alu('MUL', operand_a, operand_b)

            elif ir == ADD:
                self.alu('ADD', operand_a, operand_b)

            elif ir == PUSH:
                self.register[7] -= 1
                val = self.register[operand_a]
                self.ram_write(val, self.register[7])

            elif ir == POP:
                val = self.ram_read(self.register[7])
                self.register[operand_a] = val
                self.register[7] += 1

            elif ir == CALL:
                self.register[7] -= 1
                self.ram_write(self.pc + 2, self.register[7])
                self.pc = self.register[operand_a]

            elif ir == RET:
                self.pc = self.ram_read(self.register[7])
                self.register[7] += 1

            elif ir == CMP:
                self.alu('CMP', operand_a, operand_b)

            elif ir == JMP:
                self.pc = self.register[operand_a]

            elif ir == JEQ:
                if self.fl & 0b00000001 == 1:
                    self.pc = self.register[operand_a]
                else:
                    self.pc += 2

            elif ir == JNE:
                if self.fl & 0b00000001 != 1:
                    self.pc = self.register[operand_a]
                else:
                    self.pc += 2

            else:
                print(f'Invalid instruction {ir}')
                running = False

            if ir & 0b00010000 == 0:
                self.pc += (ir >> 6) + 1

cpu = CPU()