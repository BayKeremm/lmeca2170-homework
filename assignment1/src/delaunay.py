import sys
from proj_utils import * 
from halfedge import *
from triangularmesh import *
import sys
import numpy as np 

def create_initial_triangulation(vertices):
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

    points_at_inf = [x_n, x_n1, x_n2, x_n3]
    initial_hes = [he1, he2, he3, he4, he5, he6]
    faces = [[he1,he2,he3],[he4,he5,he6]]
    return points_at_inf, initial_hes, faces


if __name__== "__main__":
    DEBUG = False 
    REMOVEINF = False
    EXP = False
    if len(sys.argv) < 5:
        print_usage()
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
        idx_inf = sys.argv.index("-REMOVEINF")
        inf = sys.argv[idx_inf+1]
        if int(inf)==1:
            REMOVEINF = True
        idx_exp = sys.argv.index("-EXPORT")
        exp = sys.argv[idx_inf+1]
        if int(exp)==1:
            EXP = True
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

    points_at_inf, inital_hes, initial_faces = create_initial_triangulation(vertices)
    vertices.extend(points_at_inf)

    T = TriangularMesh(vertices,inital_hes,initial_faces,DEBUG)

    T.triangulate()

    if EXP and not REMOVEINF:
        T.export(fo)

    if DEBUG and not REMOVEINF:
        T.print_mesh("Triangulation with points at infinity")

    boundary_hes = [inital_hes[1],inital_hes[2],inital_hes[4],inital_hes[5]]
    boundary_vs = points_at_inf

    if REMOVEINF:
        print("Removing points at infinity")
        T.handle_boundaries(boundary_hes, boundary_vs)
    
    if EXP and REMOVEINF:
        T.export(fo)
    
    if DEBUG and REMOVEINF:
        T.print_mesh("RESULT after removal of points at infinity")
    

    fi.close()
    fo.close()

    