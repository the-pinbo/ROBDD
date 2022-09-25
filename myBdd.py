
import collections
from distutils.command.build import build
import weakref
import boolfunc
import pydot
from IPython.display import Image, display


class BDDNode:
    """Class for a node in a BDD."""
    # defining the bdd one and zero nodes key
    BDDNODEZEROKEY = (-1, id(None), id(None))
    BDDNODEONEKEY = (-2, id(None), id(None))

    def __init__(self, exp, var):
        # constructor for the BDDNode class
        self.exp = exp
        self.var = var
        self.lo = None
        self.hi = None

    @staticmethod
    def getNodeZero(numVars):
        """Returns the node corresponding to the zero function."""
        # the var for zero node is made -1
        exp = boolfunc.Expression.getEqnZero(numVars)
        return BDDNode(exp, -1)

    @staticmethod
    def getNodeOne(numVars):
        """Returns the node corresponding to the one function."""
        # the var for one node is made -2
        exp = boolfunc.Expression.getEqnOne(numVars)
        return BDDNode(exp, -2)

    def getKey(self):
        """Returns the key of the node."""
        return (self.var, self.lo, self.hi)

    def __str__(self) -> str:
        """Returns a string representation of the BDDNode."""
        rep = list()
        rep.append(f"id:{id(self)}")
        rep.append(f"var:{self.var}")
        rep.append(f"exp:{self.exp}")
        rep.append(f"lo:{id(self.lo)}")
        rep.append(f"hi:{id(self.lo)}")
        return "\n".join(rep)

    def __repr__(self) -> str:
        """Returns a string representation of the BDDNode."""
        return self.__str__()

    def getLabel(self):
        """Returns the label of the node."""
        # _label = f"var->{self.var}\nid->{id(self)}\nlo->{id(self.lo)}    hi->{id(self.hi)}"
        if self.var == -1:
            label = "0"
        elif self.var == -2:
            label = "1"
        else:
            label = f"X{self.var}"
        return label


class BDD:
    """BDD class to instantiate a BDD from an expression and an ordering."""

    def __init__(self, exp: boolfunc.Expression, ordering: list) -> None:
        # store the expression
        self.exp = exp
        # store the ordering
        self.ordering = ordering
        # node/bdd cache
        self.NODES = weakref.WeakValueDictionary()
        # build the BDD for Zero and One
        self.BDDNODEZERO = BDDNode.getNodeZero(exp.numVars)
        self.NODES[self.BDDNODEZERO.getKey()] = self.BDDNODEZERO
        self.BDDNODEONE = BDDNode.getNodeOne(exp.numVars)
        self.NODES[self.BDDNODEONE.getKey()] = self.BDDNODEONE
        # build the BDD
        self.node = self.buildBDD()

    def displayGraph(self):
        """Displays the BDD graph."""
        img = self.getPng()
        display(img)

    def getPng(self):
        """Returns the png image of the BDD."""
        self.graph = pydot.Dot(graph_type="digraph")
        visited = set()
        BDD.dfs(self.graph, self.node, visited)
        return Image(self.graph.create_png())

    @staticmethod
    def dfs(graph, node, visited):
        """Iterate through nodes in DFS post-order and build the graph using pydot."""
        # if lo is not none build the lo node
        if node.lo is not None:
            BDD.dfs(graph, node.lo, visited)
        # if hi is not none build the hi node
        if node.hi is not None:
            BDD.dfs(graph, node.hi, visited)
        # if the node is not visited
        if node not in visited:
            # add the node to the visited set
            visited.add(node)
            # add node zero to graph
            if node.var == -1:
                graph.add_node(pydot.Node(node.getLabel(),
                                          style="filled", fillcolor="orange", shape='box'))
            # add node one to graph
            elif node.var == -2:
                graph.add_node(pydot.Node(node.getLabel(),
                                          style="filled", fillcolor="lightblue", shape='box'))
            else:
                # add the normal node to the graph
                graph.add_node(pydot.Node(node.getLabel(),
                                          style="filled", fillcolor="green"))
            # add and edge from the node to the lo node
            if node.lo is not None:
                eLo = pydot.Edge(
                    node.getLabel(), node.lo.getLabel(), color='red', style='dotted')
                graph.add_edge(eLo)
            # add and edge from the node to the hi node
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
