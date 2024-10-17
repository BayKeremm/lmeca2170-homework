import sys
from proj_utils import * 
from halfedge import *
from triangularmesh import *
import sys
import math
import gmsh
import numpy as np 


if __name__== "__main__":
    DEBUG = False 
    INF = False
    if len(sys.argv) < 5:
        print_help()
    else:
        try:
            idx_input = sys.argv.index("-i")
            idx_output = sys.argv.index("-o")
        except:
            print_help()

        input_file = sys.argv[idx_input+1]
        output_file = sys.argv[idx_output+1]
    
    try:
        idx_deb = sys.argv.index("-DEBUG")
        deb = sys.argv[idx_deb+1]
        if int(deb)==1:
            DEBUG = True
        idx_inf = sys.argv.index("-INF")
        inf = sys.argv[idx_inf+1]
        if int(inf)==1:
            INF = True
    except:
        pass

    fi = open(input_file,"r")
    fo = open(output_file,"w")

    lines = [i.strip("\n") for i in fi.readlines()]
    num_pts = lines[0]
    pts = lines[1:]

    assert len(pts) == int(num_pts) , print_num_pts_error()


    vertices = []
    j = 0
    for pt in pts:
        l = pt.split()
        vertices.append(Vertex(float(l[0]),float(l[1]),j,None))
        j +=1

    x_min = y_min = float('inf')
    x_max = y_max = float('-inf')

    for vertex in vertices:
        x_min = min(x_min, vertex.x)
        y_min = min(y_min, vertex.y)
        x_max = max(x_max, vertex.x)
        y_max = max(y_max, vertex.y)

    dx = (x_max - x_min)
    dy = (y_max - y_min)

    scale_factor = 1000

    x_n = Vertex(x_min - dx * scale_factor, y_min - dy * scale_factor, j, None)
    x_n1 = Vertex(x_max + dx * scale_factor, y_min - dy * scale_factor, j+1, None)
    x_n2 = Vertex(x_max + dx * scale_factor, y_max + dy * scale_factor, j+2, None)
    x_n3 = Vertex(x_min - dx * scale_factor, y_max + dy * scale_factor, j+3, None)

    vertices.extend([x_n, x_n1, x_n2, x_n3])


    # Manual creation of the two triangles that covers all the points in P

    he1 = Halfedge(vertex=x_n, index=1)
    he2 = Halfedge(vertex=x_n2, index=2)
    he3 = Halfedge(vertex=x_n1, index=3)
    he4 = Halfedge(vertex=x_n2, index=4)
    he5 = Halfedge(vertex=x_n, index=5)
    he6 = Halfedge(vertex=x_n3, index=6)

    he1.opposite = he4
    he4.opposite = he1
    he1.next = he2
    he2.next = he3
    he3.next = he1
    he4.next = he5 
    he5.next = he6
    he6.next = he4

    halfedges = []
    halfedges.extend([he1, he2, he3, he4, he5, he6])

    faces = [[he1,he2,he3],[he4,he5,he6]]



    T = TriangularMesh(vertices,halfedges,faces,DEBUG)
    

    T.triangulate()

    if INF:
        T.export(fo)

    if DEBUG:
        T.print_mesh("Triangulation with added points")

    boundary_hes = [he2,he3,he5,he6]
    boundary_vs = [x_n, x_n1, x_n2, x_n3]

    T.handle_boundaries(boundary_hes, boundary_vs)
    
    if not INF and not DEBUG:
        T.export(fo)
    
    if DEBUG:
        T.print_mesh("RESULT")
    

    fi.close()
    fo.close()

    