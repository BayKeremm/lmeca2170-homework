from halfedge import *
class TriangularMesh:
    def __init__(self, vertices, halfedges, triangles):
        self.vertices = vertices
        self.faces = []
        self.halfedges = halfedges

        j = 0
        for t in triangles:
            self.faces.append(Face(j,t[0]))
            j +=1
    def __str__(self):
        return f"TriangularMesh(\n\tvertices={[str(v) for v in self.vertices]},\n\n \tfaces={[str(face) for face in self.faces]},\n\n \thalfedges={[str(he) for he in self.halfedges]})"
    
    def triangulate(self):
        to_triangulate = self.vertices[:-4]
        # Since last 4 we have manually triangulated
        for vertex in to_triangulate:
            # Now this vertex we need to find which triangle it is in
            for face in self.faces:
                res = face.inside(vertex)
                if res:
                    print(vertex.index ," is inside face: ", face)
                    # Once you find which triangle it is in, we need to recursively check 3 neighbors of this triangle
                    # More concretely, now we need to start with this triangle, call incircle2d and if it is in, mark it 
                    #   as invalid delaunay triangle
                    # then we need to go recursively to 3 neighbors and check them as well, and if they are invalid we need to
                    #   do it for their 3 neighbors and so on.
                    # Note: Do not visit the same triangles! => Use a dictionary to keep track of who's visited

