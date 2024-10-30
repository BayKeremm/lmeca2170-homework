import numpy as np
from halfedge import *
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def print_help():
    print(color.RED + "Error: Incorrect usage of arguments" + color.END)
    print("\t- Example usage: "+ color.YELLOW + "python del.py -i <INPUT_FILE> -o <OUTPUT_FILE>" + color.END)
    exit()


def print_num_pts_error():
    print(color.RED + "Error :Number of points does not correspond to number of lines retrieved from the file" + color.END)
    exit()
    
def print_usage():
    print(
        f"""{color.BLUE}
       /\\
      /  \\
     /____\\\t \t \t {color.END + color.YELLOW}LMECA Homework 1 - Delaunay Triangulation {color.END + color.BLUE}
    /\\    /\\
   /  \\  /  \\
  /____\\/____\\{color.END}""")
    print(f"""
    {color.YELLOW + color.BOLD}Options {color.END}:
        -i        : Specify input file
        -o        : Specify output file
        -DEBUG    : {color.GREEN + color.UNDERLINE}(Optional){color.END} Visualizes the triangulation (1 to enable, 0 is default)
        -REMOVEINF: {color.GREEN + color.UNDERLINE}(Optional){color.END} Removes the points at infinity (1 to enable, 0 is default)
        -EXPORT   : {color.GREEN + color.UNDERLINE}(Optional){color.END} Exports to the specified output file (1 to enable, 0 is default)

        -{color.BOLD}INTER{color.END}    : {color.PURPLE + color.BOLD}Opens up an interactive window. Default is 0 and setting this flag to 1 disregards other flags.{color.END}

    {color.YELLOW+ color.BOLD + color.UNDERLINE}Example usage: {color.END}
        {color.BOLD}python ./src/delaunay.py -INTER 1{color.END}
            - Opens up the interactive window.

        {color.BOLD}python ./src/delaunay.py -i pts.dat -o triangles.out -DEBUG 0 -REMOVEINF 1 -EXPORT 1{color.END}
            - Reads points from "pts.dat" , triangulates, removes the points at infinity
                and exports to "triangles.out".

        {color.BOLD}python ./src/delaunay.py -i pts.dat -o triangles.out -DEBUG 1 -REMOVEINF 0 -EXPORT 0{color.END}
            - Reads points from "pts.dat" , triangulates, keeps the points at infinity,
                and shows the triangulation result
            {color.UNDERLINE}Note{color.END}: Adjust scale factor for points at infinity otherwise zooming in is necessary
                in the plot. This can be done in the funciton "create_initial_triangulation" in ./src/delaunay.py.
        
        {color.BOLD}sh run_test.sh <POINT_FILE> {color.END}
            - Compares the implementation with the library implemetation of Delaunay triangulation from scipy.

        {color.BOLD}sh run_debug.sh <POINT_FILE> {color.END}
            - Runs triangulation on both homework implementation and library and visualizes both. Useful for debugging.
                
        {color.BOLD}sh dragon_attack.sh <1 or 0>{color.END}
            Stress test.
            - Argument: 1 = remove points at infinity, 0 = keep the infinity points in the test.
            - removes pts.dat file
            - generates a new 1000 points pts.dat file
            - calls "sh run_test.sh pts.dat" and gets the output.
            - continues until output is not of the form *"The same triangulation. Good!"*.
                """)
    exit()

    """
    {color.YELLOW + color.BOLD}Tests{color.END}:
        The code is tested with library function scipy.spatial.Delaunay.

        - {color.CYAN}./run_test.sh {color.END}: contains the script that runs homework implementation and library implementation and compares.
            {color.BOLD}Usage: sh run_test.sh <POINT_FILE> {color.END}
        - {color.CYAN}./run_debug.sh {color.END}: useful for visual debugging.
            {color.BOLD}Usage: sh run_debug.sh <POINT_FILE> {color.END}
        - {color.CYAN}./tests/del_test.py {color.END}: Uses the library funciton to do the triangulation.
        - {color.CYAN}./tests/compare_files.py {color.END}: The script to compare 2 files generated from triangulations to compare.
    
    {color.YELLOW + color.BOLD}Description {color.END}:
        - {color.CYAN}./src/genpts.py{color.END} : Generates points to triangulate
            {color.BOLD}Usage: python ./src/genpts.py <ENTER_NUMBER_PTS> <OUTPUT_FILE> {color.END}
        - {color.CYAN}./src/halfedge.py{color.END} : Modified halfedge data structure
        - {color.CYAN}./src/triangularmesh.py{color.END} : Triangular mesh data structure. Implements functions on a mesh.
        - {color.CYAN}./src/delaunay.py {color.END}: {color.UNDERLINE}This is the enterance point{color.END}. Calculates an inital triangulation and initializes
                                the triangular mesh data structure.
        - {color.CYAN}./src/proj_utils.py{color.END} : Contains printing functions such as this output.
    
    """

def points_to_vertices(pts):
    vertices = []
    j = 0
    for pt in pts:
        vertices.append(Vertex(float(pt[0]),float(pt[1]),j,None))
        j +=1
    return vertices



def create_initial_triangulation(vertices=None, remove_inf=False, interactive=False):
    # Initialize min and max bounds for x and y based on vertex coordinates
    if vertices is not None and not interactive:
        x_min = y_min = float('inf')
        x_max = y_max = float('-inf')
        # Determine the bounding box of the input vertices
        for vertex in vertices:
            x_min = min(x_min, vertex.x)
            y_min = min(y_min, vertex.y)
            x_max = max(x_max, vertex.x)
            y_max = max(y_max, vertex.y)
        # Calculate the width and height of the bounding box
        dx = (x_max - x_min)
        dy = (y_max - y_min)
        # Set scale factor to define the size of the bounding box extension
        if remove_inf:
            scale_factor = 30000
        else:
            scale_factor = 0.02

        j = len(vertices)
    else:
        dx = 1
        dy = 1
        scale_factor = 0
        x_min = y_min = -3000
        x_max = y_max = 3000
        j=0
    
    # Create vertices at infinity to form an initial super-rectangle covering all input points
    x_n = Vertex(x_min - dx *  scale_factor, y_min - dy * scale_factor, j, None)
    x_n1 = Vertex(x_max + dx * scale_factor, y_min - dy * scale_factor, j+1, None)
    x_n2 = Vertex(x_max + dx * scale_factor, y_max + dy * scale_factor, j+2, None)
    x_n3 = Vertex(x_min - dx * scale_factor, y_max + dy * scale_factor, j+3, None)

    # Define half-edges to connect the vertices of the initial super-rectangle (divining it in two triangles)
    he1 = Halfedge(vertex=x_n, index=1)
    he2 = Halfedge(vertex=x_n2, index=2)
    he3 = Halfedge(vertex=x_n1, index=3)
    he4 = Halfedge(vertex=x_n2, index=4)
    he5 = Halfedge(vertex=x_n, index=5)
    he6 = Halfedge(vertex=x_n3, index=6)
    # Set up half-edge relationships (opposites and next pointers)
    he1.opposite = he4 #it's the diagonal of the super-rectangle (shared between the two triangles)
    he4.opposite = he1
    he1.next = he2
    he2.next = he3
    he3.next = he1
    he4.next = he5 
    he5.next = he6
    he6.next = he4

    points_at_inf = [x_n, x_n1, x_n2, x_n3] #initial points
    initial_hes = [he1, he2, he3, he4, he5, he6] #initial half-edges
    faces = [[he1,he2,he3],[he4,he5,he6]] #initial faces
    return points_at_inf, initial_hes, faces