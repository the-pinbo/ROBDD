from itertools import islice
from itertools import chain


def parse(filePath):
    """generates the pcn data structure from a text file 
    Text file format: 

    The *first line* of the file is a single positive `int` n: the number of variables.
    We number the variables starting with index 1, so if this number was 6, 
    the variables in your problem are x1, x2, x2, x4, x5, x6.

    The second line of the file is a single positive `int` m: number of cubes in this cube list.
    If there are 10 cubes in this file, this is a “10”.

    Each of the subsequent m lines of the file describes one cube : you have the same number of 
    lines as the second line of your file. The first number on the line says how many variables 
    are not don't cares in this cube. If this number is, e.g., 5, then the next 5 numbers on 
    the line specify the true or complemented form of each variable in this cube. We use a 
    simple convention: if variable xk appears in true form, then put integer “k” on the line; 
    if variable xk appears in complement form (~xk) then put integer “-k” on the line


    Args:
        filePath (`str`): file path of the input .pcn file 

    Raises:
        AssertionError: bad pcn file 

    Returns:
        `tuple(int,list())`: number of variables and the cube list 
    """
    with open(filePath, "rb") as f:
        try:
            lines = iter(f)

            numVars = int(next(lines))
            cubeCount = int(next(lines))
            cubes = [None]*cubeCount

            for i in range(cubeCount):
                line = next(lines)
                cubes[i] = tuple(islice(map(int, line.split()), 1, None))

            return (numVars, tuple(cubes))

        except Exception as error:
            raise AssertionError("Bad pcn file {}".format(filePath)) from error


def findNumVars(cubes):
    """returns the number of variables in a cube-list

    Args:
        cubes (`cube-list`): pcn cube-list data structure 

    Returns:
        `int`: the number of variables in the cube-list
    """
    if len(cubes) == 0:
        return 0
    return max(max(map(abs, cube)) for cube in cubes)


def pcn_to_str(cubes, numVars):
    """converts a pcn data structure to a string 

    Args:
        cubes (`cube-list`): pcn cube-list data structure 

    Returns:
        `str`:  string representation of the pcn cube-list data structure 
    """
    repr = list()
    numVars = str(numVars)
    repr.append(numVars)
    numCubes = str(len(cubes))
    repr.append(numCubes)
    cubes = tuple(set(tuple(sorted(cube, key=abs)) for cube in cubes))
    for cube in cubes:
        repr.append(' '.join(map(str, chain((len(cube),), cube))))
    return "\n".join(repr)


def write_pcn(filePath, cubes):
    """write the pcn cube-list data structure 

    Args:
        filePath (`str`): out dir path
        cubes (`pcn cube-list`): pcn cube-list data structure 
    """
    with open(filePath, "w") as f:
        f.write(pcn_to_str(cubes))
