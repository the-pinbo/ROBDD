from myBdd import *
f = boolfunc.Expression(
    r"input\1.pcn")
print(f)
ordering = [1, 2, 3, 4]
print(ordering)
a = BDD(f, ordering)
