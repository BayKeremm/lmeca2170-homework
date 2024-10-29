import sys
from proj_utils import * 
from halfedge import *
from triangularmesh import *
from gui import Delaunay_GUI

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
    except ValueError:
        print("Argument '-INTER' not found.")
    except IndexError:
        print("Expected value after '-INTER' argument.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print(INTERACTIVE)

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
    else:
        gui = Delaunay_GUI()
        gui.show()


    