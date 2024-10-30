import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

# Open the points file and read the points
fi = open("./pts.dat","r")

lines = [i.strip("\n") for i in fi.readlines()]
num_pts = lines[0]
pts = lines[1:]
fi.close()
points = []
for pt in pts:
    l = pt.split()
    points.append([float(l[0]),float(l[1])])
points = np.array(points)
# Calculate the convex hull
hull = ConvexHull(points)

# Plotting the convex hull
plt.plot(points[:,0], points[:,1], 'o')
for simplex in hull.simplices:
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')

plt.title("Convex Hull")
plt.xlabel("x")
plt.ylabel("y")
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
