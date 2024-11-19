import sys
from proj_utils import * 
from halfedge import *
from triangularmesh import *
from gui import Delaunay_GUI
def compute_convex_hull(inside_vertices):
    # Sort the vertices based on their x-coordinates
    x_sorted = sorted(inside_vertices, key=lambda v: v.x)
    # Initialize the upper hull
    # upper hull is the part of the convex hull running from the leftmost point p1 to the rightmost point
    # pn when the vertices are listed in clockwise order
    L_upper = []
    L_upper.append(x_sorted[0]) #leftmost point
    L_upper.append(x_sorted[1])
    # Build the upper hull
    for i in range(2,len(inside_vertices)):
        L_upper.append(x_sorted[i])
        # check if the last three points make a left turn
        # if they do, we have to remove the second vertex of the triangle 
        # we iterate until every last three points in the upper hull make a right turn
        while len(L_upper) > 2 and orient2d(L_upper[-3].as_tuple(),
                                            L_upper[-2].as_tuple(),
                                            L_upper[-1].as_tuple()) >0:
            L_upper.remove(L_upper[-2])
    # Initialize the lower hull
    L_lower = []
    L_lower.append(x_sorted[-1])
    L_lower.append(x_sorted[-2])
    # Iterate over the remaining vertices in reverse order to construct the lower hull
    for j in reversed(range(0,len(inside_vertices)-2)):
        L_lower.append(x_sorted[j])
        while len(L_lower) > 2 and orient2d(L_lower[-3].as_tuple(),
                                            L_lower[-2].as_tuple(),
                                            L_lower[-1].as_tuple()) >0:
            L_lower.remove(L_lower[-2])
    # Remove the first and last points from the lower hull, as they are duplicates of the upper hull
    # they're the points where the upper and lower hull meet  
    L_lower.remove(L_lower[0])
    L_lower.remove(L_lower[-1])
    # Combine upper and lower hull
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
                # Find indices of input and output arguments
                idx_input = sys.argv.index("-i")
                idx_output = sys.argv.index("-o")
            except:
                print_help()
            # Get input and output file names from command-line arguments
            input_file = sys.argv[idx_input+1]
            output_file = sys.argv[idx_output+1]
        # optional
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

        #open in/output files
        fi = open(input_file,"r")
        fo = open(output_file,"w")
        # analyze input file to read points
        lines = [i.strip("\n") for i in fi.readlines()]
        num_pts = lines[0] #first line has the number of the points
        pts = lines[1:] #remaining lines have points' coordinates 

        # Check number of points in the file matches the expected count
        assert len(pts) == int(num_pts) , print_num_pts_error()

        #vertx objects
        points = []
        for pt in pts:
            l = pt.split() # split the point string into coordinates
            p = [float(l[0]),float(l[1])]
            if p not in points:
                points.append(p)

        vertices = []
        j = 0
        for pt in points:
            #create a vertex object for each point and append it to the vertices list
            vertices.append(Vertex(pt[0],pt[1],j,None))
            j +=1
        # Create initial triangulation with the points  
        points_at_inf, inital_hes, initial_faces = create_initial_triangulation(vertices, REMOVEINF)
        vertices.extend(points_at_inf)

        # Initialize the mesh and triangulate
        T = TriangularMesh(vertices,inital_hes,initial_faces,DEBUG)
        T.triangulate()

        if DEBUG and not REMOVEINF:
            T.print_mesh("Triangulation with points at infinity")

        #Define the boundary half-edges and vertices for points at infinity for boundary handling
        boundary_hes = [inital_hes[1],inital_hes[2],inital_hes[4],inital_hes[5]]
        boundary_vs = points_at_inf
        # If requested, remove points at infinity and handle boundaries
        if REMOVEINF:
            print("Removing points at infinity")
            T.handle_boundaries(boundary_hes, boundary_vs)
        # Export the triangulation 
        if EXP:
            # For homework's desired output
            T.export_homework(fo)
        # Print the resulting mesh after removing points at infinity (if debug is enabled)
        if DEBUG and REMOVEINF:
            T.print_mesh("RESULT after removal of points at infinity")
    

        fi.close()
        fo.close()
    else:
        gui = Delaunay_GUI()
        gui.show()


    