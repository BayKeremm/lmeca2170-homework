import sys
from proj_utils import * 
from halfedge import *
from triangularmesh import *
from gui import Delaunay_GUI
def compute_convex_hull(inside_vertices):
    x_sorted = sorted(inside_vertices, key=lambda v: v.x)

    L_upper = []
    L_upper.append(x_sorted[0])
    L_upper.append(x_sorted[1])

    for i in range(2,len(inside_vertices)):
        L_upper.append(x_sorted[i])
        while len(L_upper) > 2 and orient2d(L_upper[-3].as_tuple(),
                                            L_upper[-2].as_tuple(),
                                            L_upper[-1].as_tuple()) >0:
            L_upper.remove(L_upper[-2])
    L_lower = []
    L_lower.append(x_sorted[-1])
    L_lower.append(x_sorted[-2])

    for j in reversed(range(0,len(inside_vertices)-2)):
        L_lower.append(x_sorted[j])
        while len(L_lower) > 2 and orient2d(L_lower[-3].as_tuple(),
                                            L_lower[-2].as_tuple(),
                                            L_lower[-1].as_tuple()) >0:
            L_lower.remove(L_lower[-2])
        
    L_lower.remove(L_lower[0])
    L_lower.remove(L_lower[-1])

    return L_upper + L_lower

if __name__== "__main__":
    DEBUG = False 
    REMOVEINF = False
    EXP = False

    INTERACTIVE = False
    try:
        idx_int = sys.argv.index("-INTER")
        interactive_flag = sys.argv[idx_int + 1]
        if int(interactive_flag) == 1:
            INTERACTIVE = True
    except:
        pass

    #print(INTERACTIVE)

    if not INTERACTIVE:
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
        except:
            print("DAFUQ")
        try:
            idx_inf = sys.argv.index("-REMOVEINF")
            inf = sys.argv[idx_inf+1]
            if int(inf)==1:
                REMOVEINF = True
        except:
            print("DAFUQ")
        try:
            idx_exp = sys.argv.index("-EXPORT")
            exp = sys.argv[idx_exp+1]
            if int(exp)==1:
                EXP = True
        except:
            print("DAFUQ")

        #print("------------")
        #print(DEBUG)
        #print(EXP)
        #print(REMOVEINF)
        #print(INTERACTIVE)
        #print("------------")

        fi = open(input_file,"r")
        fo = open(output_file,"w")

        lines = [i.strip("\n") for i in fi.readlines()]
        num_pts = lines[0]
        pts = lines[1:]

        assert len(pts) == int(num_pts) , print_num_pts_error()

        
        points = []
        for pt in pts:
            l = pt.split()
            p = [float(l[0]),float(l[1])]
            if p not in points:
                points.append(p)

        vertices = []
        j = 0
        for pt in points:
            vertices.append(Vertex(pt[0],pt[1],j,None))
            j +=1

        points_at_inf, inital_hes, initial_faces = create_initial_triangulation(vertices, REMOVEINF)
        vertices.extend(points_at_inf)

        T = TriangularMesh(vertices,inital_hes,initial_faces,DEBUG)

        T.triangulate()

        if DEBUG and not REMOVEINF:
            T.print_mesh("Triangulation with points at infinity")

        boundary_hes = [inital_hes[1],inital_hes[2],inital_hes[4],inital_hes[5]]
        boundary_vs = points_at_inf

        if REMOVEINF:
            print("Removing points at infinity")
            T.handle_boundaries(boundary_hes, boundary_vs)
    
        if EXP:
            # For homework's desired output
            T.export_homework(fo)
    
        if DEBUG and REMOVEINF:
            T.print_mesh("RESULT after removal of points at infinity")
    

        fi.close()
        fo.close()
    else:
        gui = Delaunay_GUI()
        gui.show()


    