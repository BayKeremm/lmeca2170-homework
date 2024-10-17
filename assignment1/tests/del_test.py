import numpy as np
from scipy.spatial import Delaunay
import sys
import matplotlib.pyplot as plt

# Get input and output file paths from command line arguments
idx_input = sys.argv.index("-i")
input_file = sys.argv[idx_input+1]
idx_output = sys.argv.index("-o")
output_file = sys.argv[idx_output+1]

# Read points from input file
with open(input_file, "r") as fi:
    lines = [i.strip("\n") for i in fi.readlines()]
    num_pts = lines[0]
    pts = lines[1:]

# Define boundary points and append the additional points
points = [[-1, -1], [-1, 2], [2, -1], [2, 2]]
#points = []

for pt in pts:
    l = pt.split()
    points.append([float(l[0]), float(l[1])])

# Perform Delaunay triangulation
points = np.array(points)
tri = Delaunay(points)

# Open output file for writing triangles
with open(output_file, "w") as fo:
    for simplex in tri.simplices:
        # Retrieve the coordinates of each vertex of the triangle
        triangle = [f"({points[vertex][0]}, {points[vertex][1]})" for vertex in simplex]
        # Write the triangle to the output file
        fo.write(" ".join(triangle) + "\n")
fo.close()


#plt.triplot(points[:,0], points[:,1], tri.simplices, color='blue')
#plt.scatter(points[:,0], points[:,1], color='red')
#plt.title("Delaunay Triangulation")
#plt.xlabel("x")
#plt.ylabel("y")
#plt.gca().set_aspect('equal', adjustable='box')
#plt.show()