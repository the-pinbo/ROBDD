import os
import pcn
import urp


class BCE(object):
    def __init__(self, inPath, outPath):
        self.inPath = inPath
        self.outPath = outPath
        self.eqs = {}
        self.operations = {
            "r": self.read_pcn,
            "!": self.do_not,
            "+": self.do_or,
            "&": self.do_and,
            "p": self.write_pcn,
            "xor": self.do_xor,
            "dx": self.do_dx,
            "cx": self.do_cx,
            "sx": self.do_sx,
            "q": self.quit
        }
        self.done = False

    def process(self, commandFilePath):
        with open(commandFilePath, "r") as f:
            for line in f:
                command, *args = line.split()
                self.operations[command](*args)

                if self.done:
                    return

    def read_pcn(self, fNum):
        _, self.eqs[fNum] = pcn.parse(os.path.join(self.inPath, fNum + ".pcn"))

    def write_pcn(self, fNum):
        pcn.write_pcn(os.path.join(
            self.outPath, fNum + ".pcn"), self.eqs[fNum])

    def do_not(self, resultNum, inNum):
        self.eqs[resultNum] = urp.complement(self.eqs[inNum])

    def do_or(self, resultNum, leftNum, rightNum):
        self.eqs[resultNum] = urp.cubes_or(
            self.eqs[leftNum], self.eqs[rightNum])

    def do_and(self, resultNum, leftNum, rightNum):
        self.eqs[resultNum] = urp.cubes_and(
            self.eqs[leftNum], self.eqs[rightNum])

    def do_xor(self, resultNum, leftNum, rightNum):
        self.eqs[resultNum] = urp.cubes_xor(
            self.eqs[leftNum], self.eqs[rightNum])

    def do_dx(self, resultNum, inNum, x):
        self.eqs[resultNum] = urp.boolDiff(self.eqs[inNum], int(x))

    def do_cx(self, resultNum, inNum, x):
        self.eqs[resultNum] = urp.consensus(self.eqs[inNum], int(x))

    def do_sx(self, resultNum, inNum, x):
        self.eqs[resultNum] = urp.smoothing(self.eqs[inNum], int(x))

    def quit(self):
        self.done = True
