import sys
from proj_utils import * 
from halfedge import *
from triangularmesh import *
import sys
import math
import gmsh
import numpy as np 



if __name__== "__main__":
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

    #print(input_file,output_file)


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

    x_min = vertices[0].x
    y_min = vertices[0].y
    x_max = vertices[0].x
    y_max = vertices[0].y

    for vertex in vertices:
        if vertex.x < x_min:
            x_min = vertex.x
        if vertex.x > x_max:
            x_max = vertex.x
        if vertex.y < y_min:
            y_min = vertex.y
        if vertex.y > y_max:
            y_max = vertex.y

    #print(f"x_min: {x_min}, y_min: {y_min}, x_max: {x_max}, y_max: {y_max}") 

    #x_min -= x_max
    #y_min -= y_max

    #y_max += y_max
    #x_max += x_max

    x_min = -1
    y_min = -1

    y_max = 2
    x_max = 2

    # these 4 new points make sure the convex hull contains 4 vertices
    # So we would end up with 2*n+2 traingles (n is the number of points)
    x_n = Vertex(x_min, y_min, j, None)
    x_n1 = Vertex(x_max, y_min, j+1, None)
    x_n2 = Vertex(x_max, y_max, j+2, None)
    x_n3 = Vertex(x_min, y_max, j+3, None)

    vertices.append(x_n)
    vertices.append(x_n1)
    vertices.append(x_n2)
    vertices.append(x_n3)

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
    halfedges.append(he1)
    halfedges.append(he2)
    halfedges.append(he3)
    halfedges.append(he4)
    halfedges.append(he5)
    halfedges.append(he6)

    T = TriangularMesh(vertices,halfedges,[[he1,he2,he3],[he4,he5,he6]])
    # Since we know the convex hull
    T.set_convex_hull_edges([he2,he3,he5,he6])

    p = Printer(T)
    T.set_printer(p)

    #p.print_mesh()

    T.triangulate()

    # Remove initial triangulation, with 4 edges, we need to remove 4 triangles

    T.faces.remove(he2.face)
    T.halfedges.remove(he2)
    T.halfedges.remove(he2.next)
    T.halfedges.remove(he2.next.next)

    T.faces.remove(he3.face)
    T.halfedges.remove(he3)
    T.halfedges.remove(he3.next)
    T.halfedges.remove(he3.next.next)

    T.faces.remove(he5.face)
    T.halfedges.remove(he5)
    T.halfedges.remove(he5.next)
    T.halfedges.remove(he5.next.next)

    T.faces.remove(he6.face)
    T.halfedges.remove(he6)
    T.halfedges.remove(he6.next)
    T.halfedges.remove(he6.next.next)

    to_remove = []
    vs = [x_n,x_n1,x_n2,x_n3]
    for h in T.halfedges:
        if h.vertex in vs:
            to_remove.append(h)
    
    for h in to_remove:
        T.faces.remove(h.face)
        T.halfedges.remove(h)
        T.halfedges.remove(h.next)
        T.halfedges.remove(h.next.next)
    
    T.vertices.remove(x_n)
    T.vertices.remove(x_n1)
    T.vertices.remove(x_n2)
    T.vertices.remove(x_n3)


    T.compute_convex_hull()
    p.plot_convexhull()
    #p.print_mesh("Result of triangulation")




    fi.close()
    fo.close()

    