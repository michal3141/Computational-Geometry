import matplotlib
matplotlib.use("TkAgg")
import commons
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import numpy as np
import pylab as pl
import random
import time
import os
from matplotlib import pyplot as plt 
from matplotlib.widgets import Button
from scipy.spatial import ConvexHull

# Matplotlib axis object.
ax = None

# Matplotlib figure object uses throughout the application.
fig = None

# If set to True then everytime while reading or writing polyhedron to file program will ask for name 
# of file to use. You can set it to False if you want defaults.
ask_for_file = True

# Global index variable controlling which color to use when rendering next polyhedron.
color_index = 0

# Default colors of faces with opacity set to 0.2
facecolors = ((1, 0, 0, 0.2), (0, 1, 0, 0.2), (0, 0, 1, 0.2), (1, 1, 0, 0.2), (1, 0, 1, 0.2), (0, 1, 1, 0.2))

# Currently plotted polyhedra
polyhedra = []

def dualize(p):
	"""Performs dualization using faces. It is my own procedure. Use with extreme caution."""

	points = []
	for face in p.faces:
		p1 = face.points[0]
		p2 = face.points[1]
		p3 = face.points[2]

		P1 = commons.Point([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
		P2 = commons.Point([p3.x - p1.x, p3.y - p1.y, p3.z - p1.z])

		p = commons.Point([P1.y*P2.z - P1.z*P2.y, P1.x*P2.z - P1.z*P2.x, P1.x*P2.y - P1.y*P2.x])
		A, B, C = p.x, p.y, p.z
		D = p1.x*p.x + p1.y*p.y + p1.z*p.z

		A /= D
		B /= D
		C /= D

		points.append(commons.Point([A, B, C]))
	return points

def sage_dual(p):
	"""Uses Sage to compute dual of polyhedron """

	with open("sagein1", "w") as f:
		for point in p.points:
			f.write("%f %f %f\n" % (point[0], point[1], point[2]))

	os.system("sage dual.sage")

	pointss = []
	with open("sageout", "r") as f:
		for line in f:
			a = line.strip().split()
			pointss.append(commons.Point([float(a[0]), float(a[1]), float(a[2])]))

	return convex_hull(pointss)	

def convex_hull(points):
	"""Computes Convex Hull of points cloud in 3D"""

	if len(points) == 0: return None
	hull = ConvexHull(points)

	pointss = []
	faces = []

	for simplex in hull.simplices:
		p0 = points[simplex[0]]
		p1 = points[simplex[1]]
		p2 = points[simplex[2]]

		if p0 not in pointss: pointss.append(p0)
		if p1 not in pointss: pointss.append(p1)
		if p2 not in pointss: pointss.append(p2)

		faces.append(commons.Face([p0, p1, p2]))
	print points

	return commons.Polyhedron(pointss, faces)

def sage_intersect(p1, p2):
	"""Uses Sage script to compute intersection of two polyhedrons. """

	with open("sagein1", "w") as f:
		for point in p1.points:
			f.write("%f %f %f\n" % (point[0], point[1], point[2]))

	with open("sagein2", "w") as f:
		for point in p2.points:
			f.write("%f %f %f\n" % (point[0], point[1], point[2]))

	os.system("sage intersect.sage")

	pointss = []
	with open("sageout", "r") as f:
		for line in f:
			a = line.strip().split()
			pointss.append(commons.Point([float(a[0]), float(a[1]), float(a[2])]))

	if len(pointss) == 0:
		print 'Intersection is empty.'
		return None 
	elif len(pointss) == 1:
		print 'Trivial intersection: (%f, %f, %f)' % (pointss[0].x, pointss[0].y, pointss[0].z) 
	else: return convex_hull(pointss)	

def intersection(p1, p2, lag=2):
	"""My own approach to intersection. Apparently there is a problem with dualization so 
		it is rather advisable to use sage_intersect instead"""

	q1 = dualize(p1)
	q2 = dualize(p2)

	d1 = convex_hull(q1)
	pl.pause(lag)
	d1.render(ax, facecolor=(0, 1, 0, 0.2))
	d2 = convex_hull(q2)
	pl.pause(lag)
	d2.render(ax, facecolor=(1, 1, 0, 0.2))

	# d3 = convex_hull(dualize(convex_hull(q1 + q2)))
	d3 = convex_hull(q1 + q2)
	pl.pause(lag)
	d3.render(ax, facecolor=(0, 1, 1, 0.2))

class ButtonHandler(object):
	""" Handling buttons used in GUI"""

	def intersect(self, event):
		"""Intersecting 2 convex polyhedra. """
		global color_index

		data = raw_input("Enter polyhedra indices to find intersection for:") 
		lst = [int(elem) for elem in data.strip().split()]

		intersection = sage_intersect(polyhedra[lst[0]], polyhedra[lst[1]])
		if intersection:
			polyhedra.append(intersection)
			polyhedra[-1].render(ax, facecolor=facecolors[color_index])
			color_index += 1
			plt.draw()		

	def dual(self, event):
		"""Dualizes and renders dualization for polyhedron. """
		global color_index

		index = int(raw_input("Enter index of polyhedron to dualize:"))
	
		# polyhedra.append(convex_hull(dualize(polyhedra[index])))
		polyhedra.append(sage_dual(polyhedra[index]))
		polyhedra[-1].render(ax, facecolor=facecolors[color_index])
		color_index += 1
		plt.draw()

	def pop(self, event):
		"""Removing last added polyhedron from graph"""
		global color_index

		print 'popping...'
		index = int(raw_input("Enter index of polyhedron to pop:"))
		if color_index > 0: 
			polyhedra.pop(index)
			ax.collections.pop(index)
			plt.draw()
			color_index -= 1

	def move(self, event):
		"""Move polyhedron from polyhedra given index, dx, dy and dz 
			Example: 0 2 4 1"""	
					
		print 'moving...'
		command = raw_input("Enter move command:")
		cmd = command.strip().split()
		index = int(cmd[0])
		dx, dy, dz = float(cmd[1]), float(cmd[2]), float(cmd[3])
		polyhedra[index].translate(dx, dy, dz)
		polyhedra[index].render(ax, facecolor=facecolors[index])
		ax.collections[index] = ax.collections[-1]
		ax.collections.pop()
		plt.draw()

	def hull(self, event):
		"""Finding convex hull for 2 or more polyhedrons."""
		global color_index

		data = raw_input("Enter polyhedra indices to find convex hull for:") 
		lst = [int(elem) for elem in data.strip().split()]

		polyhedra.append(convex_hull(polyhedra[lst[0]].points + polyhedra[lst[1]].points))
		polyhedra[-1].render(ax, facecolor=facecolors[color_index])
		color_index += 1
		plt.draw()

	def load_data(self, event):
		"""Loads polyhedron from user specifyied file"""
		global color_index

		print 'loading data...'
		if ask_for_file: filename = raw_input("Enter filename:")
		else: filename = "cube.ply"
		polyhedra.append(commons.parsePLY(os.path.join("data", filename)))
		polyhedra[-1].render(ax, facecolor=facecolors[color_index])
		color_index += 1
		plt.draw()

	def save_data(self, event):
		"""Saves polyhedron that was created as last one (from top of the stack)."""
		print 'saving data...'

		if ask_for_file: filename = raw_input("Enter filename:")
		else: filename = "example.ply"

		polyhedra[-1].save(os.path.join("data", filename))
		
	def clear(self, event):
		"""Removes everything from figure (no more polyhedra)"""
		global polyhedra, color_index

		print 'clearing...'
		ax.collections = []
		polyhedra = []
		color_index = 0
		# ax.scatter([0], [0], [0])
		plt.draw()


def rendering_test():
	"""Sets up main rendering scene. Also used for tests"""
	global ax

	pl.ion()
	pl.show()

	ax = fig.add_subplot(111, autoscale_on=False, projection="3d")
	# ax = a3.Axes3D(pl.figure())
	ax.set_xlabel("X")
	ax.set_ylabel("Y")
	ax.set_zlabel("Z")
	ax.set_xlim(-2, 2)
	ax.set_ylim(-2, 2)
	ax.set_zlim(-2, 2)

	pl.ioff()
	pl.show()

def main():
	global fig

	fig = plt.figure()
	bhandler = ButtonHandler()

	axsect = plt.axes([0.04, 0.02, 0.1, 0.075])
	axdual = plt.axes([0.15, 0.02, 0.1, 0.075])
	axpop = plt.axes([0.26, 0.02, 0.1, 0.075])
	axclear = plt.axes([0.37, 0.02, 0.1, 0.075])
	axload = plt.axes([0.48, 0.02, 0.1, 0.075])
	axsave = plt.axes([0.59, 0.02, 0.1, 0.075])
	axmove = plt.axes([0.7, 0.02, 0.1, 0.075])
	axhull = plt.axes([0.81, 0.02, 0.1, 0.075])

	bsect = Button(axsect, 'I-SECT')
	bsect.on_clicked(bhandler.intersect)

	bdual = Button(axdual, 'DUALIZE')
	bdual.on_clicked(bhandler.dual)

	bpop = Button(axpop, 'POP')
	bpop.on_clicked(bhandler.pop)

	bclear = Button(axclear, 'CLEAR')
	bclear.on_clicked(bhandler.clear)

	bload = Button(axload, 'LOAD')
	bload.on_clicked(bhandler.load_data)

	bsave = Button(axsave, 'SAVE')
	bsave.on_clicked(bhandler.save_data)

	bmove = Button(axmove, 'MOVE')
	bmove.on_clicked(bhandler.move)

	bhull = Button(axhull, 'HULL')
	bhull.on_clicked(bhandler.hull)
	
	#set_up_gui()
	rendering_test()

if __name__ == '__main__':
	main()
