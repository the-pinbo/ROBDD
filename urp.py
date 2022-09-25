# implementation of the URP algorithms to perform boolean operations
import operator
from collections import defaultdict
from itertools import chain


def compose(func_1, func_2):
    """
    compose(func_1, func_2, unpack=False) -> function

    The function returned by compose is a com 
    position of func_1 and func_2.
    That is, compose(func_1, func_2)(5) == func_1(func_2(5))
    """
    if not callable(func_1):
        raise TypeError("First argument to compose must be callable")
    if not callable(func_2):
        raise TypeError("Second argument to compose must be callable")

    def composition(*args, **kwargs):
        return func_1(func_2(*args, **kwargs))

    return composition


def complement_cube(cube: tuple[list]) -> tuple[list]:
    """returns the complement of a cube
    """
    return tuple((-v,) for v in cube)


def _all_max(values, key=None):
    maxTotal = max(values, key=key)
    return (v for v in values if key(v) == key(maxTotal))


def _all_min(values, key=None):
    minTotal = min(values, key=key)
    return (v for v in values if key(v) == key(minTotal))


def _most_binate(cubes):
    """Returns the variable that appears in the most cubes
    """
    # Find the variable that occurs in the most cubes
    counts = defaultdict(lambda: [0, 0, 0])
    # counts = {var: [positive, negative, total]}
    for cube in cubes:
        for v in cube:
            counts[abs(v)][v > 0] += 1
            counts[abs(v)][2] += 1
    # Find the variable that occurs in the most cubes
    binate = tuple((v, c) for v, c in counts.items() if c[0] > 0 and c[1] > 0)
    if len(binate) > 0:
        # Pick smallest index if there is a tie
        mostBinate = tuple(_all_max(binate, key=lambda arg: arg[1][2]))
        # Pick smallest index if there is a tie
        ties = _all_min(mostBinate, key=lambda arg: abs(arg[1][1] - arg[1][0]))
    else:
        # Again, pick smallest index if there is a tie
        ties = _all_max(counts.items(), key=lambda arg: arg[1][2])
    # Return the variable with the smallest index
    choice = min(map(operator.itemgetter(0), ties))
    return choice


def generalCofactor(cubes: tuple[list], x: int):
    """Returns the positive cofactor of cubes with respect to x"""
    return tuple(sorted(tuple(c for c in cube if c != x)
                        for cube in cubes if -x not in cube))


def positiveCofactor(cubes: tuple[list], position: int):
    """Returns the positive cofactor of cubes with respect to x"""
    assert(position > 0)
    return generalCofactor(cubes, position)


def negativeCofactor(cubes: tuple[list], position: int):
    """Returns the negative cofactor of cubes with respect to x"""
    assert(position > 0)
    return generalCofactor(cubes, -position)


def cubes_var_and(cubes, var):
    """Returns the boolean AND of a cube list with a variable"""
    return tuple(tuple(chain(cube, (var,))) for cube in cubes)


def cubes_or(left, right):
    """Returns the boolean OR of two cube lists"""
    return tuple(set(chain(left, right)))


def cubes_and(left, right):
    """Returns the boolean AND of two cube lists"""
    return complement(cubes_or(complement(left), complement(right)))


def cubes_xor(left, right):
    """Returns the boolean XOR of two cube lists"""
    return cubes_or(cubes_and(left, complement(right)), cubes_and(complement(left), right))


def boolDiff(cubes, x):
    """Returns the boolean difference of a cube list with respect to variable X"""
    pCf = positiveCofactor(cubes, x)
    nCf = negativeCofactor(cubes, x)
    return cubes_xor(pCf, nCf)


def consensus(cubes, x):
    """Returns the consensus of a cube list with respect to variable X"""
    pCf = positiveCofactor(cubes, x)
    nCf = negativeCofactor(cubes, x)
    return cubes_and(pCf, nCf)


def smoothing(cubes, x):
    """Returns the smoothing of a cube list with respect to variable X"""
    pCf = positiveCofactor(cubes, x)
    nCf = negativeCofactor(cubes, x)
    return cubes_or(pCf, nCf)


def complement(cubes):
    """Returns the complement of a cube list using URP"""
    # check if F is simple enough to complement it directly and quit
    if len(cubes) == 0:
        # Boolean equation "0"
        # Return a single don't care cube
        result = ((),)
    elif len(cubes) == 1:
        # One cube list, use demorgan's law
        result = complement_cube(cubes[0])
    elif any(len(c) == 0 for c in cubes):
        # Boolean F = stuff + 1
        # Return empty cube list, or "1"
        result = ()
    else:
        # Find the variable that occurs in the most cubes
        x = _most_binate(cubes)
        # Find the positive and negative cofactors
        pCubes = complement(positiveCofactor(cubes, x))
        nCubes = complement(negativeCofactor(cubes, x))
        p = cubes_var_and(pCubes, x)
        n = cubes_var_and(nCubes, -x)
        result = cubes_or(p, n)

    return result
