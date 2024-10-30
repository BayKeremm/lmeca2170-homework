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
            triangles.append(sorted(triangle))
    
    triangles.sort()
    return triangles, count

def compare_triangles(file1, file2):
    triangles1, count1 = read_triangles_from_file(file1)
    triangles2, count2 = read_triangles_from_file(file2)

    for t in triangles1:
        if t not in triangles2:
            print(t)
    print("--------------")
    for t in triangles2:
        if t not in triangles1:
            print(t)
    assert count1 == count2, "Different number of triangles start of the file"
    assert count1 == len(triangles1), "file 1 is okay"
    assert count2 == len(triangles2), "file 2 is okay"
    assert len(triangles1) == len(triangles2), "Do not match, different number of triangulations"
    assert triangles1 == triangles2,  "Do not match, different triangles present"
    print("The same triangulation. Good! ")
if len(sys.argv) != 3:
    print("Usage: python compare_triangles.py <file1> <file2>")
    sys.exit(1)

file1 = sys.argv[1]
file2 = sys.argv[2]

compare_triangles(file1, file2)
