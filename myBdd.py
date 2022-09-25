import collections
from distutils.command.build import build
from functools import cache
from math import exp
import random
import weakref
import boolfunc
import pydot
from IPython.display import Image, display


class BDDNode:
    BDDNODEZEROKEY = (-1, id(None), id(None))
    BDDNODEONEKEY = (-2, id(None), id(None))

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
        return (self.var, id(self.lo), id(self.hi))

    def __str__(self) -> str:
        rep = list()
        rep.append(f"id:{id(self)}")
        rep.append(f"var:{self.var}")
        rep.append(f"exp:{self.exp}")
        rep.append(f"lo:{id(self.lo)}")
        rep.append(f"hi:{id(self.lo)}")
        return "\n".join(rep)

    def __repr__(self) -> str:
        return self.__str__()

    def getLabel(self):
        label = f"var->{self.var}\nid->{id(self)}\nlo->{id(self.lo)}    hi->{id(self.hi)}"
        return label


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

    def displayGraph(self):
        img = self.getPng()
        display(img)

    def getPng(self):
        self.graph = pydot.Dot(graph_type="digraph")
        visited = set()
        BDD.dfs(self.graph, self.node, visited)
        return Image(self.graph.create_png())

    @staticmethod
    def dfs(graph, node, visited):
        """Iterate through nodes in DFS post-order."""
        if node.lo is not None:
            BDD.dfs(graph, node.lo, visited)
        if node.hi is not None:
            BDD.dfs(graph, node.hi, visited)
        if node not in visited:
            visited.add(node)
            if node.var == -1:
                graph.add_node(pydot.Node(node.getLabel(),
                                          style="filled", fillcolor="orange", shape='box'))
            elif node.var == -2:
                graph.add_node(pydot.Node(node.getLabel(),
                                          style="filled", fillcolor="lightblue", shape='box'))
            else:
                graph.add_node(pydot.Node(node.getLabel(),
                                          style="filled", fillcolor="green"))
            if node.lo is not None:
                eLo = pydot.Edge(
                    node.getLabel(), node.lo.getLabel(), color='red', style='dotted')
                graph.add_edge(eLo)
            if node.hi is not None:
                eHi = pydot.Edge(
                    node.getLabel(), node.hi.getLabel(), color='blue')
                graph.add_edge(eHi)

    def buildBDD(self):
        return buildBDD(self.exp, self.ordering, self.NODES)

    def dfsPreorder(self):
        visited = set()
        return _dfsPre(self.node, visited)

    def dfsPostorder(self):
        visited = set()
        return _dfsPost(self.node, visited)

    def bfs(self):
        visited = set()
        return _bfs(self.node, visited)


def buildBDD(exp, ordering, cache):
    if exp.isFalse():
        return cache[BDDNode.BDDNODEZEROKEY]
    if exp.isTrue():
        return cache[BDDNode.BDDNODEONEKEY]
    for idx, var in enumerate(ordering):
        if exp.isPresent(var):
            return bddNode(exp, ordering, cache, idx)

    raise ValueError("invalid ordering list")

# todo change key to ids


def bddNode(exp, ordering, cache, idx):
    var = ordering[idx]
    nodeLo = buildBDD(exp.negativeCofactor(var), ordering, cache)
    nodeHi = buildBDD(exp.positiveCofactor(var), ordering, cache)
    if nodeLo is nodeHi:
        exp = nodeLo.exp
        node = nodeLo
    else:
        key = (var, id(nodeLo), id(nodeHi))
        try:
            node = cache[key]
        except KeyError:
            node = BDDNode(exp, var)
            node.lo = nodeLo
            node.hi = nodeHi
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


def test():
    exp = boolfunc.Expression("A & B | C & D")
    ordering = ["A", "B", "C", "D"]
    bdd = BDD(exp, ordering)
    bdd.displayGraph()
    print(bdd.dfsPreorder())
    print(bdd.dfsPostorder())
    print(bdd.bfs())


if __name__ == "__main__":
    test()
