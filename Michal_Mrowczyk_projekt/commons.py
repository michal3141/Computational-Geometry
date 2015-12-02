## This is a file contatining neccessary data structures used to hold polyhedra.
## It also provides parsing mechanism for .ply files
import matplotlib
matplotlib.use("TkAgg")
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import pylab as pl

class Point(list):
 	"""Point in 3D space"""

 	def __init__(self, *args):
 		super(Point, self).__init__(*args)
 		self.x = args[0][0]
 		self.y = args[0][1]
 		self.z = args[0][2]

class Face(list):
	"""Face which is a list of points in 3D"""

	def __init__(self, *args):
		super(Face, self).__init__(*args)
		self.points = args[0]
		
class Polyhedron(object):
	"""Polyhedron represented as a list of points and faces"""

	def __init__(self, points, faces):
		super(Polyhedron, self).__init__()
		self.points = points
		self.faces = faces

	def render(self, ax, facecolor=(0,1,0,0.2), edgecolor="k", alpha=0.2):
		""" Renders polyhedron using matplotlib library 
			ax - axis used when rendering polyhedron
		"""

		self.fig = a3.art3d.Poly3DCollection(self.faces)
		self.fig.set_facecolor(facecolor)
		self.fig.set_edgecolor(edgecolor)
		self.fig.set_alpha(alpha)

		ax.add_collection3d(self.fig)

	def translate(self, x, y, z):
		""" Translates polyhedron """

		for p in self.points:
			p[0] += x
			p.x += x
			p[1] += y
			p.y += y
			p[2] += z
			p.z += z

	def save(self, filepath):
		""" Saves polyhedron using PLY file format """

		ply_header = """ply
format ascii 1.0
comment created by owner
element vertex %d
property float32 x
property float32 y
property float32 z
element face %d
property list uint8 int32 vertex_indices
end_header\n""" % (len(self.points), len(self.faces))

		with open(filepath, "w") as f:
			f.write(ply_header)
			for point in self.points:
				f.write("%f %f %f\n" % (point[0], point[1], point[2]))
			for face in self.faces:
				f.write("%d " % (len(face.points), ))
				for point in face.points:
					f.write("%d " % (self.points.index(point), ))
				f.write("\n")	

		print 'Polyhedron sucessfuly saved'

def parsePLY(filepath):
	""" Parses PLY file given as filepath
		Returns Polyhedron object
	"""

	points = []
	faces = []
	points_len, faces_len, counter = 0, 0, 0
	end_header = False

	with open(filepath, "r") as f:
		for line in f:
			value = line.strip().split()
			if not end_header:
				if value[0] == "element" and value[1] == "vertex":
					points_len = int(value[2])
				elif value[0] == "element" and value[1] == "face":
					faces_len = int(value[2])
				elif value[0] == "end_header":
					end_header = True
			else:
				if counter < points_len:
					points.append(Point([float(value[0]), float(value[1]), float(value[2])]))
				else:
					face_points = []
					for index in value[1:]:
						face_points.append(points[int(index)])
					faces.append(Face(face_points))
				counter += 1
	return Polyhedron(points, faces)	
 		 