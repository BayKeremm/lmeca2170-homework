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
    Options:
        -i        : Specify input file
        -o        : Specify output file
        -DEBUG    : {color.GREEN + color.UNDERLINE}(Optional){color.END} Visualizes the triangulation (1 to enable, 0 is default)
        -REMOVEINF: {color.GREEN + color.UNDERLINE}(Optional){color.END} Removes the points at infinity (1 to enable, 0 is default)
        -EXPORT   : {color.GREEN + color.UNDERLINE}(Optional){color.END} Exports to the specified output file (1 to enable, 0 is default)

    {color.UNDERLINE}Example usages: {color.END}
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
                in the plot.
                """)
    exit()
