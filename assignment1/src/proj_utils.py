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

    {color.YELLOW+ color.BOLD + color.UNDERLINE}Example usage: {color.END}
        {color.BOLD}
        python ./src/delaunay.py -i pts.dat -o triangles.out -DEBUG 0 -REMOVEINF 1 -EXPORT 1
        {color.END}
            - Reads points from "pts.dat" , triangulates, removes the points at infinity
                and exports to "triangles.out".
        {color.BOLD}
        python ./src/delaunay.py -i pts.dat -o triangles.out -DEBUG 1 -REMOVEINF 0 -EXPORT 0
        {color.END}
            - Reads points from "pts.dat" , triangulates, keeps the points at infinity,
                and shows the triangulation result
            {color.UNDERLINE}Note{color.END}: Adjust scale factor for points at infinity otherwise zooming in is necessary
                in the plot. This can be done in the funciton "create_initial_triangulation" in ./src/delaunay.py.
        
        {color.BOLD}sh run_test.sh <POINT_FILE> {color.END}
            - Compares the implementation with the library implemetation of Delaunay triangulation from scipy.

        {color.BOLD}sh run_debug.sh <POINT_FILE> {color.END}
            - Runs triangulation on both homework implementation and library and visualizes both. Useful for debugging.
                
        {color.BOLD}sh dragon_attack.sh {color.END}
            Stress test.
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