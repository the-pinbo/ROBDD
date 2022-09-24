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

        self.node = self._buildBDD()

    def _buildBDD(self):
        return buildBDD(self.exp,self.ordering,self.NODES)


def buildBDD(exp, ordering, cache):
    if exp.isFalse():
        return cache[BDDNode.BDDNODEZEROKEY]
    if exp.isTrue():
        return cache[BDDNode.BDDNODEONEKEY]
    for idx, var in enumerate(ordering):
        if exp.isPresent(var):
            return bddNode(exp, ordering[idx:])

    raise ValueError("invalid ordering list")


def bddNode(exp, ordering, cache):
    var = ordering[0]
    lo = exp.negativeCofactor(var)
    hi = exp.positiveCofactor(var)
    if lo is hi:
        node = lo
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
