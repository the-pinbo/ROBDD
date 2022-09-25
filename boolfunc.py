"""Module which contains the BooleanFunction class."""
import pcn
import urp


class Expression:
    """Class which represents a Boolean expression."""

    def __init__(self, filePath=None, cubes=None, numVars=None) -> None:
        """Constructor for the BooleanFunction class from a file or from an existing cubes list."""
        if filePath is not None:
            self.expFromFile(filePath)
        elif cubes is not None and numVars is not None:
            self.expFromCubes(cubes, numVars)
        else:
            raise TypeError("expected file path or cubes/numVars")

    @staticmethod
    def getEqnZero(numVars):
        """Returns the equation of the zero function."""
        return Expression(cubes=(), numVars=numVars)

    @staticmethod
    def getEqnOne(numVars):
        """Returns the equation of the one function."""
        return Expression(cubes=((),), numVars=numVars)

    def isPresent(self, x):
        """Returns true if the cube x is present in the expression."""
        for c in self.cubes:
            for l in c:
                if abs(l) == x:
                    return True
        return False

    def isTrue(self):
        """Returns true if there is all dont care cube."""
        return any(len(c) == 0 for c in self.cubes)

    def isFalse(self):
        """Returns true if there is a zero cube."""
        return len(self.cubes) == 0

    def expFromCubes(self, cubes, numVars):
        """Constructor for the BooleanFunction class from a list of cubes."""
        self.cubes, self.numVars, = tuple(set(cubes)), numVars

    def expFromFile(self, filePath):
        """Constructor for the BooleanFunction class from a file."""
        self.numVars, self.cubes = pcn.parse(filePath)

    def __str__(self) -> str:
        """Returns a string representation of the BooleanFunction."""
        return pcn.pcn_to_str(self.cubes, self.numVars)

    def __repr__(self) -> str:
        """Returns a string representation of the BooleanFunction."""
        return self.__str__()

    def complement(self):
        """Returns the complement of the BooleanFunction."""
        complementedCubes = urp.complement(self.cubes)
        return Expression(cubes=complementedCubes, numVars=self.numVars)

    def andExp(self, f):
        """Returns the conjunction of the BooleanFunction with another one."""
        andCubes = urp.cubes_and(self.cubes, f)
        return Expression(cubes=andCubes, numVars=self.numVars)

    def orExp(self, f):
        """Returns the union of the BooleanFunction with another one."""
        orCubes = urp.cubes_or(self.cubes, f)
        return Expression(cubes=orCubes, numVars=self.numVars)

    def xorExp(self, f):
        """Returns the exclusive or of the BooleanFunction with another one."""
        xorCubes = urp.cubes_xor(self.cubes, f)
        return Expression(cubes=xorCubes, numVars=self.numVars)

    def positiveCofactor(self, x):
        """Returns the positive cofactor of the BooleanFunction with respect to the variable x."""
        assert(x > 0 and x <= self.numVars)
        positiveCofactorCubes = urp.positiveCofactor(self.cubes, x)
        return Expression(cubes=positiveCofactorCubes, numVars=self.numVars)

    def negativeCofactor(self, x):
        """Returns the negative cofactor of the BooleanFunction with respect to the variable x."""
        assert(x > 0 and x <= self.numVars)
        negativeCofactorCubes = urp.negativeCofactor(self.cubes, x)
        return Expression(cubes=negativeCofactorCubes, numVars=self.numVars)

    def boolDiffWith(self, x):
        """Returns the boolean difference of the BooleanFunction with respect to the variable x."""
        assert(x > 0 and x <= self.numVars)
        boolDiffCubes = urp.boolDiff(self.cubes, x)
        return Expression(cubes=boolDiffCubes, numVars=self.numVars)

    def consensusWith(self, x):
        """Returns the consensus of the BooleanFunction with respect to the variable x."""
        assert(x > 0 and x <= self.numVars)
        consensusCubes = urp.consensus(self.cubes, x)
        return Expression(cubes=consensusCubes, numVars=self.numVars)

    def smoothingWith(self, x):
        """Returns the smoothing of the BooleanFunction with respect to the variable x."""
        assert(x > 0 and x <= self.numVars)
        smoothingCubes = urp.smoothing(self.cubes, x)
        return Expression(cubes=smoothingCubes, numVars=self.numVars)
