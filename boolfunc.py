# Class for boolean functions which can be used to generate expressions
import pcn
import urp


class Expression:
    def __init__(self, filePath=None, cubes=None, numVars=None) -> None:
        """Initializes the expression from a file or from cubes and numVars

        Args:
            filePath (str, optional): Path to the file. Defaults to None.
            cubes (list, optional): List of cubes. Defaults to None.
            numVars (int, optional): Number of variables. Defaults to None.
        Raises:
            TypeError: If both filePath and cubes are None
        """
        if filePath is not None:
            self.expFromFile(filePath)
        elif cubes is not None and numVars is not None:
            self.expFromCubes(cubes, numVars)
        else:
            raise TypeError("expected file path or cubes/numVars")

    @staticmethod
    def getEqnZero(numVars):
        return Expression(cubes=(), numVars=numVars)

    @staticmethod
    def getEqnOne(numVars):
        return Expression(cubes=((),), numVars=numVars)

    def isPresent(self, x):
        for c in self.cubes:
            for l in c:
                if abs(l) == x:
                    return True
        return False

    def isTrue(self):
        return any(len(c) == 0 for c in self.cubes)

    def isFalse(self):
        # print(self.cubes)
        return len(self.cubes) == 0

    def expFromCubes(self, cubes, numVars):
        self.cubes, self.numVars, = tuple(set(cubes)), numVars

    def expFromFile(self, filePath):
        self.numVars, self.cubes = pcn.parse(filePath)

    def __str__(self) -> str:
        return pcn.pcn_to_str(self.cubes, self.numVars)

    def __repr__(self) -> str:
        return self.__str__()

    def complement(self):
        complementedCubes = urp.complement(self.cubes)
        return Expression(cubes=complementedCubes, numVars=self.numVars)

    def andExp(self, f):
        andCubes = urp.cubes_and(self.cubes, f)
        return Expression(cubes=andCubes, numVars=self.numVars)

    def orExp(self, f):
        orCubes = urp.cubes_or(self.cubes, f)
        return Expression(cubes=orCubes, numVars=self.numVars)

    def xorExp(self, f):
        xorCubes = urp.cubes_xor(self.cubes, f)
        return Expression(cubes=xorCubes, numVars=self.numVars)

    def positiveCofactor(self, x):
        assert(x > 0 and x <= self.numVars)
        positiveCofactorCubes = urp.positiveCofactor(self.cubes, x)
        return Expression(cubes=positiveCofactorCubes, numVars=self.numVars)

    def negativeCofactor(self, x):
        assert(x > 0 and x <= self.numVars)
        negativeCofactorCubes = urp.negativeCofactor(self.cubes, x)
        return Expression(cubes=negativeCofactorCubes, numVars=self.numVars)

    def boolDiffWith(self, x):
        assert(x > 0 and x <= self.numVars)
        boolDiffCubes = urp.boolDiff(self.cubes, x)
        return Expression(cubes=boolDiffCubes, numVars=self.numVars)

    def consensusWith(self, x):
        assert(x > 0 and x <= self.numVars)
        consensusCubes = urp.consensus(self.cubes, x)
        return Expression(cubes=consensusCubes, numVars=self.numVars)

    def smoothingWith(self, x):
        assert(x > 0 and x <= self.numVars)
        smoothingCubes = urp.smoothing(self.cubes, x)
        return Expression(cubes=smoothingCubes, numVars=self.numVars)
