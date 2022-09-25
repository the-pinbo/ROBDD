# Implementation of ROBDD

> Implementation of ROBDD using python3 visualizing it using graphviz and pydot

## Introduction:

Binary Decision Diagrams(BDDs) are an effective data structure to represent boolean functions. BDDs are referred to as Directed Acyclic Graphs(DAGs). BDDs, however, are not canonical forms of describing boolean functions. But a certain kind of BDDs, called the Reduced Ordered BDDs(ROBDDs) are canonical for that particular ordering. ROBDDs are BDDs following a specified variable ordering and simplified/reduced using reduction rules. This is a very desirable property for determining formal equivalence.

Two reduction rules exist for converting an OBDD into a ROBDD:

1.  Merge equivalent leaves

```python
# Reduction rule 1
# is lo is hi then return lo
if nodeLo is nodeHi:
	exp = nodeLo.exp
	node = nodeLo
```

2.  Merge isomorphic nodes

```python
# Reduction rule 2
# if the node is already present in the cache then return the node
key = (var, id(nodeLo), id(nodeHi))
try:
    node = cache[key]
except KeyError:
```

> Ex: The BDD for the Boolean function $f(X_1,X_2,X_3)= X_1 . \bar X_2 . \bar X_3+ X_1.X_2 + X_2.X_3$ is shown below:
> ![bdd image]()

The ROBDD for the same function with the variable ordering $X_1<X_2<X_3$, is shown below:

![bdd image](https://upload.wikimedia.org/wikipedia/commons/1/14/BDD_simple.svg)

### How does variable ordering affect the BDD?

ROBDD of $f(X_1,X_2,X_3,X_4,X_5,X_6,X_7,X_8) = X_1.X_2 + X_3.X_4 + X_5.X_6 + X_7.X_8$

ordering : $X_1<X_2<X_3<X_4<X_5<X_6<X_7<X_8$

![ex1](https://upload.wikimedia.org/wikipedia/commons/4/4b/BDD_Variable_Ordering_Good.svg)

ordering : $X_1<X_3<X_5<X_7<X_2<X_4<X_6<X_8$

![ex2](https://upload.wikimedia.org/wikipedia/commons/2/28/BDD_Variable_Ordering_Bad.svg)

Even though the above graphs are ROBDDs of the same Boolean function, the former is the result of a bad variable ordering, while the latter is the result of optimal ordering. This indicates that just reducing the BDD to ROBDD does not give an optimal representation, but starting with a good variable ordering does. For a small number of variables, one can try various combinations of variable ordering and select the optimal ordering. This, however, is not feasible when the boolean function contains a large number of variables, say 100. One can use heuristic approaches such as Minato’s Heuristic to come up with a variable ordering which is ‘good enough, if not optimal.

## Input File Format

### PCN File Format

We are using a very simple text file format for this program. Our code will read a Boolean function specified in this format. The file format looks like this:

- The _first line_ of the file is a single positive `int` n: the number of variables. We number the variables starting with index 1, so if number was 3, the variables in your problem are $$X_1, X_2, X_3$$
- The second line of the file is a single positive `int` m: number of cubes in this cube list. If there are 10 cubes in this file, this is a “10”.
- Each of the subsequent m lines of the file describes one cube : you have the same number of lines as the second line of your file. The first number on the line says how many variables are not don't cares in this cube. If this number is, e.g., 5, then the next 5 numbers on the line specify the true or complemented form of each variable in this cube. We use a simple convention: if variable $x_k$ appears in true form, then put integer $“k”$ on the line; if variable $x_k$ appears in complement form $\bar x_k$ then put integer $“-k”$ on the line

_Example :_
Suppose we have a function $F = X_1.X_2 + X_2.X_3 + X_3.X_1$

```
3
3
2 1 2
2 2 3
2 1 3
```

## Setup

Simply clone this git hub repo and run `test.ipynb ` with appropriate pcn files an input form the `./input` directory , further instructions are given ther, also make sure to install the depandancies.

## Contact

Created by [@the-pinbo](https://github.com/the-pinbo) - feel free to contact me!
