import sys

def read_triangles_from_file(file_path):
    """Reads and parses triangles from a file"""
    triangles = []
    
    with open(file_path, "r") as file:
        for line in file:
            coords = line.strip().split()
            p1 = [float(coords[0].strip("(,")),float(coords[1].strip(")"))]
            p2 = [float(coords[2].strip("(,")),float(coords[3].strip(")"))]
            p3 = [float(coords[4].strip("(,")),float(coords[5].strip(")"))]
            triangle = [p1,p2,p3]
            triangles.append(sorted(triangle))
    
    triangles.sort()
    return triangles

def compare_triangles(file1, file2):
    triangles1 = read_triangles_from_file(file1)
    triangles2 = read_triangles_from_file(file2)

    if triangles1 == triangles2:
        print("The triangles in both files match.")
    else:
        print("The triangles in both files do not match.")
        

if len(sys.argv) != 3:
    print("Usage: python compare_triangles.py <file1> <file2>")
    sys.exit(1)

file1 = sys.argv[1]
file2 = sys.argv[2]

compare_triangles(file1, file2)
