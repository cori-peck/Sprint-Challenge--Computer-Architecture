"""CPU functionality."""

import sys

SP = 7   #Stack pointer is register R7
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
HLT = 0b00000001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.fl = 0
        self.reg[SP] = 244
        self.running = False
        self.branchtable = {
            LDI: self.handleLDI,
            PRN: self.handlePRN,
            MUL: self.handleMUL,
            PUSH: self.handlePUSH,
            POP: self.handlePOP,
            HLT: self.handleHLT,
            CMP: self.handleCMP,
            JMP: self.handleJMP,
            JEQ: self.handleJEQ,
            JNE: self.handleJNE
        }

    def handleLDI(self, ir, reg, val):
        bit_operands = (ir & 0b11000000) >> 6
        self.reg[reg] = val
        self.pc += bit_operands + 1

    def handlePRN(self, ir, regloc, operand):
        bit_operands = (ir & 0b11000000) >> 6
        print(self.reg[regloc])
        self.pc += bit_operands + 1

    def handleMUL(self, ir, reg1, reg2):
        bit_operands = (ir & 0b11000000) >> 6
        self.alu("MUL", reg1, reg2)
        self.pc += bit_operands + 1

    def handlePUSH(self, ir, regloc, operand):
        bit_operands = (ir & 0b11000000) >> 6  #right shift operator - shift to right and append 1 at the end
        self.reg[SP] -=1
        self.ram[self.reg[SP]] = self.reg[regloc]
        self.pc += bit_operands + 1

    def handlePOP(self, ir, regloc, operand):
        bit_operands = (ir & 0b11000000) >> 6
        self.reg[regloc] = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        self.pc += bit_operands + 1

    def handleHLT(self):
        self.running = False

    def handleCMP(self, ir, reg1, reg2):
        #instruction handles by the ALU
        self.alu("CMP", reg1, reg2)
        self.pc += ((ir & 0b11000000) >> 6) + 1
        
    def handleJMP(self, ir, regloc, op2):
        #Set the PC to the address stored in the given register
        self.pc = self.reg[regloc]

    def handleJEQ(self, ir, regloc, op2):
        #If equal flag is set (true), jump to the address stored in the given register
        if (self.fl & 0b00000001) == 1:
            self.pc = self.reg[regloc]
        else:
            self.pc += ((ir & 0b11000000) >> 6) + 1

    def handleJNE(self, ir, regloc, op2):
        #If E flag is clear (false, 0), jump to the address stored in the given register
        if (self.fl & 0b00000001) == 0:
            self.pc = self.reg[regloc]
        else:
            self.pc += ((ir & 0b11000000) >> 6) + 1

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
        elif op == "MUL":
            product = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] = product
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                #if they are equal, set the Equal E flag to 1 otherwise set it to 0
                self.fl = (self.fl | 0b00000001)
            else:
                self.fl = (self.fl & 0b11111110)

            if self.reg[reg_a] < self.reg[reg_b]:
                #if registerA is < registerB, set the less-than L flag to 1 otherwise set to 0
                self.fl = (self.fl | 0b00000100)
            else:
                self.fl(self.fl & 0b11111011)

            if self.reg[reg_a] > self.reg[reg_b]:
                #if registerA is > registerB, set the greater-than G flag to 1 otherwise set it to 0
                self.fl = (self.fl | 0b00000010)
            else:
                self.fl = (self.fl & 0b11111101)

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
        self.running = True
        #read the memory address that's stored in register `PC`
        #store that result in `IR`(Instruction Register), can be a local variable
        while self.running:
            ir = self.ram[self.pc]
            #Using `ram_read()`,read the bytes at `PC+1` and `PC+2` from RAM into variables
            #`operand_a` and`operand_b` in case the instruction needs them.
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            try:
                self.branchtable[ir](ir, operand_a, operand_b)
                
            except:
                print(f"Unknown instruction: {ir}")
                sys.exit(1)
