import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

fi = open("./pts.dat","r")

lines = [i.strip("\n") for i in fi.readlines()]
num_pts = lines[0]
pts = lines[1:]
fi.close()
points = []
#points.append([-1,-1])
#points.append([-1,2])
#points.append([2,-1])
#points.append([2,2])
for pt in pts:
    l = pt.split()
    points.append([float(l[0]),float(l[1])])
# Perform Delaunay triangulation
points = np.array(points)
tri = Delaunay(points)

# Plotting the points and the triangulation
plt.triplot(points[:,0], points[:,1], tri.simplices, color='blue')
plt.scatter(points[:,0], points[:,1], color='red')
plt.title("Delaunay Triangulation")
plt.xlabel("x")
plt.ylabel("y")
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
