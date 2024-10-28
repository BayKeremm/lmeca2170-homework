import numpy as np
from scipy.spatial import Delaunay
import sys
import matplotlib.pyplot as plt

# Get input and output file paths from command line arguments
idx_input = sys.argv.index("-i")
input_file = sys.argv[idx_input+1]
idx_output = sys.argv.index("-o")
output_file = sys.argv[idx_output+1]

idx_deb = sys.argv.index("-DEBUG")
DEBUG = int(sys.argv[idx_deb+1])

idx_inf = sys.argv.index("-REMOVEINF")
REMOVEINF = int(sys.argv[idx_inf+1])

idx_exp = sys.argv.index("-EXPORT")
EXPORT = int(sys.argv[idx_exp+1])

# Read points from input file
with open(input_file, "r") as fi:
    lines = [i.strip("\n") for i in fi.readlines()]
    num_pts = lines[0]
    pts = lines[1:]

# Define boundary points and append the additional points
if not REMOVEINF:
    x_min = y_min = float('inf')
    x_max = y_max = float('-inf')

    for pt in pts:
        l = pt.split()
        x_min = min(x_min, float(l[0]))
        y_min = min(y_min, float(l[1]))
        x_max = max(x_max, float(l[0]))
        y_max = max(y_max, float(l[1]))

    dx = (x_max - x_min)
    dy = (y_max - y_min)

    scale_factor = 2000

    x_n = [x_min - dx * scale_factor, y_min - dy * scale_factor]
    x_n1 =[x_max + dx * scale_factor, y_min - dy * scale_factor]
    x_n2 =[x_max + dx * scale_factor, y_max + dy * scale_factor]
    x_n3 =[x_min - dx * scale_factor, y_max + dy * scale_factor]
    points = [x_n, x_n1, x_n2, x_n3]
else:
    points = []

for pt in pts:
    l = pt.split()
    points.append([float(l[0]), float(l[1])])

# Perform Delaunay triangulation
points = np.array(points)
tri = Delaunay(points)


if DEBUG:
    plt.triplot(points[:,0], points[:,1], tri.simplices, color='blue')
    plt.scatter(points[:,0], points[:,1], color='red')
    plt.title("Delaunay Triangulation")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
elif EXPORT:
    # Open output file for writing triangles
    with open(output_file, "w") as fo:
        for simplex in tri.simplices:
            # Retrieve the coordinates of each vertex of the triangle
            triangle = [f"({points[vertex][0]}, {points[vertex][1]})" for vertex in simplex]
            # Write the triangle to the output file
            fo.write(" ".join(triangle) + "\n")
    fo.close()