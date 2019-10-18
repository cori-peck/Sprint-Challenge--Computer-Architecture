"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0

    def load(self):
        """Load a program into memory."""
        if len(sys.argv) !=2:
            print(f"usage: {sys.argv[0]} filename", file=sys.stderr)
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                address = 0
            
                for line in f:
                    #process comments, ignore anything after # symbol
                    num = line.split("#", 1)[0]

                    if num.strip() == '':
                        continue

                    #convert numbers from binary strings to integers
                    self.ram_write(int(num, 2), address)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

        #address = 0

        # For now, we've just hardcoded a program:

        #program = [
            # From print8.ls8
            #0b10000010, # LDI R0,8
            #0b00000000,
            #0b00001000,
            #0b01000111, # PRN R0
            #0b00000000,
            #0b00000001, # HLT
        #]

        #for instruction in program:
            #self.ram[address] = instruction
            #address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        if op == "MUL":
            product = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] = product
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, mar):  ## MAR(Memory Address Register - address being read or written to)
        #get address to read - mar
        #return the value stored there
        return self.ram[mar]

    def ram_write(self, mdr, mar):  ## MDR(Memory Data Register - data that was read or data to write)
        #should accept a value to write (MDR), and the address to write it to(MAR)
        self.ram[mar] = mdr

    def run(self):
        """Run the CPU."""
        running = True
        #read the memory address that's stored in register `PC`
        #store that result in `IR`(Instruction Register), can be a local variable
        while running:
            ir = self.ram[self.pc]
            #Using `ram_read()`,read the bytes at `PC+1` and `PC+2` from RAM into variables
            #`operand_a` and`operand_b` in case the instruction needs them.
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            #depending on the value of the opcode, perform the actions needed for the instruction per the LS-8 spec
            #exit the loop if a `HLT` instruction is encountered
            if ir == 0b00000001:
                self.pc += 1
                running = False
            #LDI
            elif ir == 0b10000010:
                self.reg[operand_a] = operand_b
                self.pc += 3
            #PRN Print numeric value stored in the given register (operand_a)
            elif ir == 0b01000111:
                print(self.reg[operand_a])
                self.pc += 2
            #MUL send to self.alu and multiply th evalues in the two registers
            elif ir == 0b10100010:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            else:
                print(f"Unknown instruction: {ir}")
                sys.exit(1)
