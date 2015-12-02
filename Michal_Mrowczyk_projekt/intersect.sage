from sage.geometry.polyhedron.base import Polyhedron

vertices1 = []
with open("sagein1", "r") as f:
    for line in f:
        a = line.strip().split()
        vertices1.append((float(a[0]), float(a[1]), float(a[2])))
vertices2 = []
with open("sagein2", "r") as f:
    for line in f:
        a = line.strip().split()
        vertices2.append((float(a[0]), float(a[1]), float(a[2])))
        
p1 = Polyhedron(vertices=vertices1)
p2 = Polyhedron(vertices=vertices2)

common = p1.intersection(p2)

with open("sageout", "w") as f:
    for vertex in common.vertices():
        f.write("%f %f %f\n" % (vertex[0], vertex[1], vertex[2]))


