from sage.geometry.polyhedron.base import Polyhedron

vertices1 = []
with open("sagein1", "r") as f:
    for line in f:
        a = line.strip().split()
        vertices1.append((float(a[0]), float(a[1]), float(a[2])))

p1 = Polyhedron(vertices=vertices1)
dual = p1.Hrepresentation()

with open("sageout", "w") as f:
    for ineq in dual:
        div = ineq[0]
        A = ineq[1] / float(div)
        B = ineq[2] / float(div)
        C = ineq[3] / float(div)
        f.write("%f %f %f\n" % (A, B, C))

