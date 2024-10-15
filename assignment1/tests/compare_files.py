import sys

def read_triangles_from_file(file_path):
    """Reads and parses triangles from a file"""
    triangles = []
    
    with open(file_path, "r") as file:
        for line in file:
            # Split the line into vertices (x, y)
            coords = line.strip().split()
            p1 = [float(coords[0].strip("(,")),float(coords[1].strip(")"))]
            p2 = [float(coords[2].strip("(,")),float(coords[3].strip(")"))]
            p3 = [float(coords[4].strip("(,")),float(coords[5].strip(")"))]
            # Convert string coordinates to tuples of floats
            triangle = [p1,p2,p3]
            # Sort each triangle's vertices to ensure consistent ordering
            triangles.append(sorted(triangle))
    
    # Sort the list of triangles to enable comparison
    triangles.sort()
    return triangles

def compare_triangles(file1, file2):
    """Compares triangles from two files and prints the result"""
    triangles1 = read_triangles_from_file(file1)
    triangles2 = read_triangles_from_file(file2)

    # Compare the two sets of triangles
    if triangles1 == triangles2:
        print("The triangles in both files match.")
    else:
        print("The triangles in both files do not match.")
        
        # Find triangles unique to file1
        unique_to_file1 = [t for t in triangles1 if t not in triangles2]
        if unique_to_file1:
            print("\nTriangles unique to", file1, ":")
            for tri in unique_to_file1:
                print(tri)

        # Find triangles unique to file2
        unique_to_file2 = [t for t in triangles2 if t not in triangles1]
        if unique_to_file2:
            print("\nTriangles unique to", file2, ":")
            for tri in unique_to_file2:
                print(tri)

# Command-line argument handling
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_triangles.py <file1> <file2>")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    compare_triangles(file1, file2)
