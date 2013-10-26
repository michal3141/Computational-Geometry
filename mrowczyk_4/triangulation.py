import json
import sys
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt 
from matplotlib.widgets import Button
from math import pi
import pylab
import time
import numpy as np

ask_for_file = False
filename = 'tmp'
polygons = []
segments = []

# Global empty list of points to have fun with
points = []

# Global axis to have fun with
ax = None

class Point(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __sub__(self, other):
		return Point(self.x - other.x, self.y - other.y)

	def __cmp__(self, other):
		if self.y < other.y: return -1
		if self.y > other.y: return 1
		if self.x < other.x: return -1
		if self.x > other.x: return 1
		return 0

	def __str__(self):
		return '(%f, %f)' % (self.x , self.y)

class Segment(object):
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2

class Polygon(object):
	def __init__(self, points):
		self.points = points

	def draw(self):
		points_len = len(self.points)
		for i in xrange(points_len):
			ax.scatter([self.points[i].x], [self.points[i].y], c='g', s=40)
			if i > 0:
				ax.plot([self.points[i-1].x, self.points[i].x], [self.points[i-1].y, self.points[i].y], c='k')
		ax.plot([self.points[-1].x, self.points[0].x], [self.points[-1].y, self.points[0].y], c='k')
		plt.draw()

	def segmentify(self):
		""" Calculates segment representation for polygon and adds it to polygon object """

		self.segments = []
		points_len = len(self.points)
		for i in xrange(points_len):
			self.segments.append(Segment(self.points[i-1], self.points[i]))
		self.segments.append(Segment(self.points[-1], self.points[0]))

def to_dict(polygons):
	""" Serializes polygons to proper nested list """
	
	d = []
	for polygon in polygons:
		d.append(['polygon', [[p.x, p.y] for p in polygon.points]])
	return d

class ButtonHandler(object):
	def create_polygon(self, event):
		global polygons, points
		polygon = Polygon(points)
		polygon.draw()
		polygons.append(polygon)
		points = []

	def run_triangulation(self, event):
		print 'run_triangulation was clicked'
		triangulate()

	def load_data(self, event):
		global polygons, points, filename

		if ask_for_file: filename = raw_input("Enter filename:")
		print 'loading data...'

		polygons = []
		d = json.loads(open(filename, 'r').read())
		for polygon in d:
			poly = Polygon([])
			pointlist = polygon[1]
			for point in pointlist:
				poly.points.append(Point(point[0], point[1]))
			polygons.append(poly)
		points = []
		ax.collections = []
		ax.lines = []
		for polygon in polygons:
			polygon.draw()

	def save_data(self, event):
		global filename

		if ask_for_file: filename = raw_input("Enter filename:")
		print 'saving data...'
		
		open(filename, 'w').write(json.dumps(to_dict(polygons)))

	def clear(self, event):
		global points, polygons
		points = []
		polygons = []
		ax.collections = []
		ax.lines = []
		plt.draw()


class MouseHandler(object):
	def onclick(self, event):
		if event.dblclick:
			x = event.xdata
			y = event.ydata
			points.append(Point(x, y))
			ax.scatter([x], [y], c='g', s=40)
			plt.draw()

def angle(vec):
	"""
	Returns an angle created by right X axis and vector vec
	"""
	x = vec.x
	y = vec.y
	theta = np.angle(complex(x, y))
	if y < 0:
		theta = 2 * pi - abs(theta)
 	return theta

def check_y_monotonicity(polygon, lag=0.1):
	points_len = len(polygon.points)
	points = polygon.points

	# Hash map sending point to dictionary indicating it's previous point
	# next point and color or type which is to be found.
	polygon.dict = {}

	polygon.dict[points[0]] = {'prev': points[-1], 'next': points[1], 'color': 'N/A'}
	polygon.dict[points[-1]] = {'prev': points[-2], 'next': points[0], 'color': 'N/A'}

	for i in xrange(1, points_len - 1):
		polygon.dict[points[i]] = {'prev': points[i-1], 'next': points[i+1], 'color': 'N/A'}

	y_monotonic = True 

	for k, v in polygon.dict.iteritems():
		time.sleep(lag)
		prev = polygon.dict[k]['prev']
		next = polygon.dict[k]['next']
		alpha = angle(k - prev)
		beta = angle(next - k)
		theta = (pi + alpha - beta) % (2*pi)
		if prev.y < k.y and next.y < k.y and theta < pi:
			polygon.dict[k]['color'] = 'green'
			ax.scatter([k.x], [k.y], c = 'lime', s=40)
		elif prev.y > k.y and next.y > k.y and theta < pi:
			polygon.dict[k]['color'] = 'red'
			ax.scatter([k.x], [k.y], c = 'r', s=40)
		elif prev.y > k.y and next.y > k.y and theta > pi:
			polygon.dict[k]['color'] = 'darkblue'
			ax.scatter([k.x], [k.y], c = 'b', s=40)
			y_monotonic = False
		elif prev.y < k.y and next.y < k.y and theta > pi:
			polygon.dict[k]['color'] = 'cyan'
			ax.scatter([k.x], [k.y], c = 'c', s=40)
			y_monotonic = False
		else:
			polygon.dict[k]['color'] = 'brown'
			ax.scatter([k.x], [k.y], c = 'brown', s=40)
		plt.draw()

	return y_monotonic

def det(p, q, r):
	""" >0 if p-q-r are clockwise, <0 if counterclockwise, 0 if colinear """
	return (q.y - p.y)*(r.x - p.x) - (q.x - p.x)*(r.y - p.y)

def debug_stack(stack):
	print '-------------'
	for point in reversed(stack):
		print point 
	print '-------------'

def triangulate(lag=1):
	""" Main algorithm """
	polygon = polygons[0]
	ps = polygon.points
	pylab.ion()

	y_monotonic = check_y_monotonicity(polygon)

	if y_monotonic:
		print 'Polygon is y monotonic'

		# Calculating and right chains
		max_ind = ps.index(max(ps))
		min_ind = ps.index(min(ps))
		ps_len = len(ps)
		right = True
		for i in xrange(ps_len):
			index = (min_ind + i) % ps_len
			if right == True:
				polygon.dict[ps[index]]['side'] = 'right'
			else:
				polygon.dict[ps[index]]['side'] = 'left'
			if index == max_ind: right = False

		for p in polygon.dict.keys():
			if polygon.dict[p]['side'] == 'right':
				ax.scatter([p.x], [p.y], c='lime', s=40)
			else:
				ax.scatter([p.x], [p.y], c='brown', s=40)
		plt.draw()
		time.sleep(2 * lag)

		# Sorting points with respect to monotonicity direction
		points = sorted(ps) # It's that simple !!

		# Pushing first two vertices onto stack.
		stack = [points[0], points[1]]
		for s in stack:
			ax.scatter([s.x], [s.y], c='r', s=40)

		for i in xrange(2, len(points)):
			# raw_input('Enter key to continue...')
			if polygon.dict[points[i]]['side'] != polygon.dict[stack[-1]]['side']:
				print 'Different sides.'
				for s in stack:
					time.sleep(lag)
					ax.plot([points[i].x, s.x], [points[i].y, s.y], c='k')
					plt.draw()
				for s in stack:
					ax.scatter([s.x], [s.y], c='darkblue', s=40)
				stack = [stack[-1]]
				ax.scatter([stack[0].x], [stack[0].y], c='r', s=40)
				plt.draw()
			else:
				print 'Same sides'
				size = len(stack) - 1
				j = size
				while j >= 1:
					time.sleep(lag)
					d = det(points[i], stack[j], stack[j-1])
					if (d < 0 and polygon.dict[points[i]]['side'] == 'left') or (d > 0 and polygon.dict[points[i]]['side'] == 'right'):
						print 'Go inside'
						if True:
							time.sleep(lag)
							ax.plot([points[i].x, stack[j-1].x], [points[i].y, stack[j-1].y], c='k')
							plt.draw()
						for s in stack[j:]:
							ax.scatter([s.x], [s.y], c='darkblue', s=40)
						stack.pop()
						for s in stack:
							ax.scatter([s.x], [s.y], c='r', s=40)
						plt.draw()
					j -= 1
			stack.append(points[i])
			ax.scatter([points[i].x], [points[i].y], c='r', s=40)
			plt.draw()
			debug_stack(stack)

		print 'Polygon successfuly triangulated!'

	else:
		print 'Polygon is NOT y monotonic'


	pylab.ioff()


def main():
	global ax
	fig = plt.figure()

	bhandler = ButtonHandler()
	mhandler = MouseHandler()

	axclear = plt.axes([0.37, 0.02, 0.1, 0.075])
	axload = plt.axes([0.48, 0.02, 0.1, 0.075])
	axsave = plt.axes([0.59, 0.02, 0.1, 0.075])
	axcreate = plt.axes([0.7, 0.02, 0.1, 0.075])
	axrun = plt.axes([0.81, 0.02, 0.1, 0.075])

	bclear = Button(axclear, 'CLEAR')
	bclear.on_clicked(bhandler.clear)

	bload = Button(axload, 'LOAD')
	bload.on_clicked(bhandler.load_data)

	bsave = Button(axsave, 'SAVE')
	bsave.on_clicked(bhandler.save_data)

	bcreate = Button(axcreate, 'CREATE')
	bcreate.on_clicked(bhandler.create_polygon)

	brun = Button(axrun, 'RUN')
	brun.on_clicked(bhandler.run_triangulation)

	ax = fig.add_subplot(111, autoscale_on=False)
	cid = fig.canvas.mpl_connect('button_press_event', mhandler.onclick)

	plt.show()

if __name__ == '__main__':
	main()