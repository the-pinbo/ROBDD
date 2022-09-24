import collections
from distutils.command.build import build
from functools import cache
import random
import weakref
import boolfunc


class BDDNode:
    BDDNODEZEROKEY = (-1, None, None)
    BDDNODEONEKEY = (-2, None, None)

    def __init__(self, exp, var):
        self.exp = exp
        self.var = var
        self.lo = None
        self.hi = None

    @staticmethod
    def getNodeZero(numVars):
        # the var for zero node is made -1
        exp = boolfunc.Expression.getEqnZero(numVars)
        return BDDNode(exp, -1)

    @staticmethod
    def getNodeOne(numVars):
        # the var for one node is made -2
        exp = boolfunc.Expression.getEqnOne(numVars)
        return BDDNode(exp, -2)

    def getKey(self):
        return (self.var, self.lo, self.hi)


class BDD:
    def __init__(self, exp: boolfunc.Expression, ordering: list) -> None:
        self.exp = exp
        self.ordering = ordering
        # node/bdd cache
        self.NODES = weakref.WeakValueDictionary()

        self.BDDNODEZERO = BDDNode.getNodeZero(exp.numVars)
        self.NODES[self.BDDNODEZERO.getKey()] = self.BDDNODEZERO

        self.BDDNODEONE = BDDNode.getNodeOne(exp.numVars)
        self.NODES[self.BDDNODEONE.getKey()] = self.BDDNODEONE

        self.node = self.buildBDD()

    def buildBDD(self):
        return buildBDD(self.exp, self.ordering, self.NODES)

    def dfsPreorder(self):
        visited = list()
        _dfsPre(self.node, visited)
        return visited

    def dfsPostorder(self):
        visited = list()
        _dfsPost(self.node, visited)
        return visited

    def bfs(self):
        visited = list()
        _bfs(self.node, visited)
        return visited


def buildBDD(exp, ordering, cache):
    if exp.isFalse():
        return cache[BDDNode.BDDNODEZEROKEY]
    if exp.isTrue():
        return cache[BDDNode.BDDNODEONEKEY]
    for idx, var in enumerate(ordering):
        if exp.isPresent(var):
            return bddNode(exp, ordering, cache, idx)

    raise ValueError("invalid ordering list")


def bddNode(exp, ordering, cache, idx):
    var = ordering[idx]
    lo = exp.negativeCofactor(var)
    hi = exp.positiveCofactor(var)
    if lo.cubes == hi.cubes:
        exp = lo
        node = buildBDD(exp, ordering, cache)
    else:
        key = (var, lo, hi)
        try:
            node = cache[key]
        except KeyError:
            node = BDDNode(exp, var)
            node.lo = buildBDD(lo, ordering, cache)
            node.hi = buildBDD(hi, ordering, cache)
            cache[key] = node
    return node


def _dfsPre(node, visited):
    """Iterate through nodes in DFS pre-order."""
    if node not in visited:
        visited.add(node)
        yield node
    if node.lo is not None:
        yield from _dfsPre(node.lo, visited)
    if node.hi is not None:
        yield from _dfsPre(node.hi, visited)


def _dfsPost(node, visited):
    """Iterate through nodes in DFS post-order."""
    if node.lo is not None:
        yield from _dfsPost(node.lo, visited)
    if node.hi is not None:
        yield from _dfsPost(node.hi, visited)
    if node not in visited:
        visited.add(node)
        yield node


def _bfs(node, visited):
    """Iterate through nodes in BFS order."""
    queue = collections.deque()
    queue.appendleft(node)
    while queue:
        node = queue.pop()
        if node not in visited:
            if node.lo is not None:
                queue.appendleft(node.lo)
            if node.hi is not None:
                queue.appendleft(node.hi)
            visited.add(node)
            yield node
