import collections
import random
import weakref
import boolfunc
# existing BDDVariable references
# todo think about this dict
_VARS = dict()

# node/bdd cache
_NODES = weakref.WeakValueDictionary()
_BDDS = weakref.WeakValueDictionary()


class BDDNode:
    def __init__(self, root, lo, hi):
        self.root = root
        self.lo = lo
        self.hi = hi


"""The ``root`` of the zero node is -1,
and the ``root`` of the one node is -2.
Both zero/one nodes have ``lo=None`` and ``hi=None``.
"""
BDDNODEZERO = _NODES[(-1, None, None)] = BDDNode(-1, None, None)
BDDNODEONE = _NODES[(-2, None, None)] = BDDNode(-2, None, None)


class BinaryDecisionDiagram(boolfunc.Function):
    """Boolean function represented by a binary decision diagram

    .. seealso::
       This is a subclass of :class:`pyeda.boolalg.boolfunc.Function`

    BDDs have a single attribute, ``node``,
    that points to a node in the managed unique table.

    There are two ways to construct a BDD:

    * Convert an expression using the ``expr2bdd`` function.
    * Use operators on existing BDDs.

    Use the ``bddvar`` function to create BDD variables,
    and use the Python ``~|&^`` operators for NOT, OR, AND, XOR.

    For example::

       >>> a, b, c, d = map(bddvar, 'abcd')
       >>> f = ~a | b & c ^ d

    """

    def __init__(self, node):
        self.node = node

    # Operators
    def __invert__(self):
        return _bdd(_neg(self.node))

    def __or__(self, other):
        other_node = self.box(other).node
        # f | g <=> ITE(f, 1, g)
        return _bdd(_ite(self.node, BDDNODEONE, other_node))

    def __and__(self, other):
        other_node = self.box(other).node
        # f & g <=> ITE(f, g, 0)
        return _bdd(_ite(self.node, other_node, BDDNODEZERO))

    def __xor__(self, other):
        other_node = self.box(other).node
        # f ^ g <=> ITE(f, g', g)
        return _bdd(_ite(self.node, _neg(other_node), other_node))

    def __rshift__(self, other):
        other_node = self.box(other).node
        # f => g <=> ITE(f', 1, g)
        return _bdd(_ite(_neg(self.node), BDDNODEONE, other_node))

    def __rrshift__(self, other):
        other_node = self.box(other).node
        # f => g <=> ITE(f', 1, g)
        return _bdd(_ite(_neg(other_node), BDDNODEONE, self.node))

    # From Function
    @cached_property
    def support(self):
        return frozenset(self.inputs)

    @cached_property
    def inputs(self):
        _inputs = list()
        for node in self.dfs_postorder():
            if node.root > 0:
                v = _VARS[node.root]
                if v not in _inputs:
                    _inputs.append(v)
        return tuple(reversed(_inputs))

    def restrict(self, point):
        npoint = {v.node.root: self.box(val).node for v, val in point.items()}
        return _bdd(_restrict(self.node, npoint))

    def compose(self, mapping):
        node = self.node
        for v, g in mapping.items():
            fv0, fv1 = _bdd(node).cofactors(v)
            node = _ite(g.node, fv1.node, fv0.node)
        return _bdd(node)

    def satisfy_one(self):
        path = _find_path(self.node, BDDNODEONE)
        if path is None:
            return None
        else:
            return _path2point(path)

    def satisfy_all(self):
        for path in _iter_all_paths(self.node, BDDNODEONE):
            yield _path2point(path)

    def is_zero(self):
        return self.node is BDDNODEZERO

    def is_one(self):
        return self.node is BDDNODEONE

    @staticmethod
    def box(obj):
        if isinstance(obj, BinaryDecisionDiagram):
            return obj
        elif obj == 0 or obj == '0':
            return BDDZERO
        elif obj == 1 or obj == '1':
            return BDDONE
        else:
            return BDDONE if bool(obj) else BDDZERO

    # Specific to BinaryDecisionDiagram
    def dfs_preorder(self):
        """Iterate through nodes in depth first search (DFS) pre-order."""
        yield from _dfs_preorder(self.node, set())

    def dfs_postorder(self):
        """Iterate through nodes in depth first search (DFS) post-order."""
        yield from _dfs_postorder(self.node, set())

    def bfs(self):
        """Iterate through nodes in breadth first search (BFS) order."""
        yield from _bfs(self.node, set())

    def equivalent(self, other):
        """Return whether this BDD is equivalent to *other*.

        You can also use Python's ``is`` operator for BDD equivalency testing.

        For example::

           >>> a, b, c = map(bddvar, 'abc')
           >>> f1 = a ^ b ^ c
           >>> f2 = a & ~b & ~c | ~a & b & ~c | ~a & ~b & c | a & b & c
           >>> f1 is f2
           True
        """
        other = self.box(other)
        return self.node is other.node

    def to_dot(self, name='BDD'):  # pragma: no cover
        """Convert to DOT language representation.

        See the
        `DOT language reference <http://www.graphviz.org/content/dot-language>`_
        for details.
        """
        parts = ['graph', name, '{']
        for node in self.dfs_postorder():
            if node is BDDNODEZERO:
                parts += ['n' + str(id(node)), '[label=0,shape=box];']
            elif node is BDDNODEONE:
                parts += ['n' + str(id(node)), '[label=1,shape=box];']
            else:
                v = _VARS[node.root]
                parts.append('n' + str(id(node)))
                parts.append('[label="{}",shape=circle];'.format(v))
        for node in self.dfs_postorder():
            if node is not BDDNODEZERO and node is not BDDNODEONE:
                parts += ['n' + str(id(node)), '--',
                          'n' + str(id(node.lo)),
                          '[label=0,style=dashed];']
                parts += ['n' + str(id(node)), '--',
                          'n' + str(id(node.hi)),
                          '[label=1];']
        parts.append('}')
        return " ".join(parts)


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):
    """Binary decision diagram variable

    The ``BDDVariable`` class is useful for type checking,
    e.g. ``isinstance(f, BDDVariable)``.

    Do **NOT** create a BDD using the ``BDDVariable`` constructor.
    Use the :func:`bddvar` function instead.
    """

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.names, bvar.indices)
        node = _bddnode(bvar.uniqid, BDDNODEZERO, BDDNODEONE)
        BinaryDecisionDiagram.__init__(self, node)


def _bdd(node):
    """Return a unique BDD."""
    try:
        bdd = _BDDS[node]
    except KeyError:
        bdd = _BDDS[node] = BinaryDecisionDiagram(node)
    return bdd


def bddVar(var, index=None):

    bvar = boolfunc.var(var, index)
    try:
        var = _VARS[bvar.uniqid]
    except KeyError:
        var = _VARS[bvar.uniqid] = BDDVariable(bvar)
        _BDDS[var.node] = var
    return var


def _restrict(node, npoint, cache=None):
    """Restrict a subset of support variables to {0, 1}."""
    if node is BDDNODEZERO or node is BDDNODEONE:
        return node

    if cache is None:
        cache = dict()

    try:
        ret = cache[node]
    except KeyError:
        try:
            val = npoint[node.root]
        except KeyError:
            lo = _restrict(node.lo, npoint, cache)
            hi = _restrict(node.hi, npoint, cache)
            ret = _bddnode(node.root, lo, hi)
        else:
            child = {BDDNODEZERO: node.lo, BDDNODEONE: node.hi}[val]
            ret = _restrict(child, npoint, cache)
        cache[node] = ret
    return ret


def _ite(f, g, h):
    """Return node that results from recursively applying ITE(f, g, h)."""
    # ITE(f, 1, 0) = f
    if g is BDDNODEONE and h is BDDNODEZERO:
        return f
    # ITE(f, 0, 1) = f'
    elif g is BDDNODEZERO and h is BDDNODEONE:
        return _neg(f)
    # ITE(1, g, h) = g
    elif f is BDDNODEONE:
        return g
    # ITE(0, g, h) = h
    elif f is BDDNODEZERO:
        return h
    # ITE(f, g, g) = g
    elif g is h:
        return g
    else:
        # ITE(f, g, h) = ITE(x, ITE(fx', gx', hx'), ITE(fx, gx, hx))
        root = min(node.root for node in (f, g, h) if node.root > 0)
        npoint0 = {root: BDDNODEZERO}
        npoint1 = {root: BDDNODEONE}
        fv0, gv0, hv0 = [_restrict(node, npoint0) for node in (f, g, h)]
        fv1, gv1, hv1 = [_restrict(node, npoint1) for node in (f, g, h)]
        return _bddnode(root, _ite(fv0, gv0, hv0), _ite(fv1, gv1, hv1))


def _bddnode(root, lo, hi):
    """Return a unique BDD node."""
    if lo is hi:
        node = lo
    else:
        key = (root, lo, hi)
        try:
            node = _NODES[key]
        except KeyError:
            node = _NODES[key] = BDDNode(*key)
    return node


def _neg(node):
    if node is BDDNODEZERO:
        return BDDNODEONE
    elif node is BDDNODEONE:
        return BDDNODEZERO
    else:
        return _bddnode(node.root, _neg(node.lo), _neg(node.hi))


def ite(f: boolfunc.Expression, g: boolfunc.Expression, h: boolfunc.Expression) -> BDDNode:
    """Return node that results from recursively applying ITE(f, g, h)."""
    # ITE(f, 1, 0) = f
    if g.isTrue() and h.isFalse():
        return f
    # ITE(f, 0, 1) = f'
    elif g.isFalse() and h.isTrue():
        return f.complement()
    # ITE(1, g, h) = g
    elif f.isTrue():
        return g
    # ITE(0, g, h) = h
    elif f.isFalse():
        return h
    # ITE(f, g, g) = g
    elif g is h:
        return g
    else:
        # ITE(f, g, h) = ITE(x, ITE(fx, gx, hx), ITE(fx', gx', hx'))
        root = min(node.root for node in (f, g, h) if node.root > 0)
        npoint0 = {root: BDDNODEZERO}
        npoint1 = {root: BDDNODEONE}
        fv0, gv0, hv0 = [_restrict(node, npoint0) for node in (f, g, h)]
        fv1, gv1, hv1 = [_restrict(node, npoint1) for node in (f, g, h)]
        return _bddnode(root, ite(fv0, gv0, hv0), ite(fv1, gv1, hv1))
