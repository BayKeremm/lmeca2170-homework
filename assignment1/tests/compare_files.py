import sys

def read_triangles_from_file(file_path):
    """Reads and parses triangles from a file"""
    triangles = []
    
    with open(file_path, "r") as file:
        i = 0
        count = 0
        for line in file:
            if i == 0:
                count = int(line.strip())
                i += 1
                continue
            indexes = line.strip().split()
            triangle = [int(indexes[0]),int(indexes[1]),int(indexes[2])]
            triangles.append(sorted(triangle)) # Sort the triangle vertices and add to the list
    
    triangles.sort() # Sort the list of triangles
    return triangles, count

def compare_triangles(file1, file2):
    """
    Compares triangles listed in two files. It reads and sorts the triangles from each file,
    checks if they contain the same triangles, and prints any mismatches.    
    Arguments:
    file1 -- string, path to the first file of triangles
    file2 -- string, path to the second file of triangles
        Raises:
    AssertionError if the number of triangles or the actual triangles do not match between files.
    """
    triangles1, count1 = read_triangles_from_file(file1)
    triangles2, count2 = read_triangles_from_file(file2)

    for t in triangles1:
        if t not in triangles2:
            print(t)
    print("--------------")
    for t in triangles2:
        if t not in triangles1:
            print(t) # Print the triangle if it's not found in file1
    assert count1 == count2, "Different number of triangles start of the file"
    assert count1 == len(triangles1), "file 1 is okay"
    assert count2 == len(triangles2), "file 2 is okay"
    assert len(triangles1) == len(triangles2), "Do not match, different number of triangulations"
    assert triangles1 == triangles2,  "Do not match, different triangles present"
    # If all checks pass
    print("The same triangulation. Good! ")
# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 3:
    # Print usage instructions if the user provides incorrect arguments
    print("Usage: python compare_triangles.py <file1> <file2>")
    sys.exit(1)
# Assign input file paths from command-line arguments
file1 = sys.argv[1]
file2 = sys.argv[2]

compare_triangles(file1, file2)
