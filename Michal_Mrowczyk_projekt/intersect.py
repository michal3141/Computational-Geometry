# This file was *autogenerated* from the file intersect.sage.
from sage.all_cmdline import *   # import sage library
_sage_const_2 = Integer(2); _sage_const_1 = Integer(1); _sage_const_0 = Integer(0)
from sage.geometry.polyhedron.base import Polyhedron

vertices1 = []
with open("sagein1", "r") as f:
    for line in f:
        a = line.strip().split()
        vertices1.append((float(a[_sage_const_0 ]), float(a[_sage_const_1 ]), float(a[_sage_const_2 ])))
vertices2 = []
with open("sagein2", "r") as f:
    for line in f:
        a = line.strip().split()
        vertices2.append((float(a[_sage_const_0 ]), float(a[_sage_const_1 ]), float(a[_sage_const_2 ])))
        
p1 = Polyhedron(vertices=vertices1)
p2 = Polyhedron(vertices=vertices2)

common = p1.intersection(p2)

with open("sageout", "w") as f:
    for vertex in common.vertices():
        f.write("%f %f %f\n" % (vertex[_sage_const_0 ], vertex[_sage_const_1 ], vertex[_sage_const_2 ]))


