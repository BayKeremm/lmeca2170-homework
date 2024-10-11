import sys
import math
import gmsh
import numpy as np 

class TriangularMesh:
    def __init__(self, vertices, halfedges, triangules):
        self.vertices = vertices
        self.faces = []
        self.halfedges = halfedges

        j = 0
        for t in triangules:
            self.faces.append(Face(j,t[0]))
            j +=1
    def __str__(self):
        return f"TriangularMesh(\n\tvertices={[str(v) for v in self.vertices]},\n\n \tfaces={[str(face) for face in self.faces]},\n\n \thalfedges={[str(he) for he in self.halfedges]})"


            
class Vertex:
    def __init__(self, x=0, y=0, z=0, index=None, halfedge=None):
        self.x = x
        self.y = y
        self.z = z
        self.index = index
        self.halfedge = halfedge
    def __str__(self):
        return f"Vertex({self.index}, x={self.x}, y={self.y})"

class Face:
    def __init__(self, index=None, halfedge=None):
        self.index = index
        # halfedge going ccw around this face.
        self.halfedge = halfedge
    def __str__(self):
        return f"Face({self.index}, halfedge={self.halfedge})"

class Halfedge:
    def __init__(self, next=None, opposite=None, prev=None, vertex=None,
                 face=None, index=None):
        self.opposite = opposite
        self.next = next
        self.prev = prev
        self.vertex = vertex
        self.face = face
        self.index = index
    def __str__(self):
        next_idx = self.next.index if self.next else None
        prev_idx = self.prev.index if self.prev else None
        opp_idx = self.opposite.index if self.opposite else None
        vert_idx = self.vertex.index if self.vertex else None
        return (f"Halfedge({self.index}): vertex={vert_idx}, "
                f"next={next_idx}, prev={prev_idx}, opposite={opp_idx}")


if __name__ == '__main__':
    print(len(sys.argv))
    if len(sys.argv) == 2 :
        gmsh.initialize()
        gmsh.open (sys.argv[1])
        gmsh.model.mesh.renumber_nodes()
        tags, x, _ = gmsh.model.mesh.get_nodes()
        order = np.argsort(tags)
        verts = x.reshape([-1,3])[order]
        
        _,el = gmsh.model.mesh.get_elements_by_type(2)
        tris = el.reshape((-1,3))-1
    else  :   
        verts = [[0.,0.,0.], [1.,0.,0.], [1.,1.,0.], [0.,1.,0.]]
        tris  = [[0,1,2], [2,3,0]]
    T  = TriangularMesh(verts, tris)
    for he in T.halfedges:
        print (he.index,he.prev,he.next,he.opposite)
        