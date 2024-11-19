from geompreds import orient2d
class Vertex:
    def __init__(self, x=0, y=0, index=None, halfedge=None):
        self.x = x
        self.y = y
        self.index = index
        self.halfedge = halfedge
        self.done = False
    def __str__(self):
        return f"Vertex({self.index}, x={self.x}, y={self.y})"
    def as_tuple(self):
        return (self.x,self.y)

class Face:
    def __init__(self, index=None, halfedge=None):
        self.index = index
        # halfedge going ccw around this face.
        self.halfedge = halfedge
    def inside(self, vertex):
        def on_segment(v1,v2,v3):
            c1 = min(v1.x, v2.x) <= v3.x
            c2 = max(v1.x, v2.x) >= v3.x

            c3 = min(v1.y, v2.y) <= v3.y
            c4 = max(v1.y, v2.y) >= v3.y
            return c1 and c2 and c3 and c4
        # Since a face is a triangle we can get 3 halfedges that cover it
        he1 = self.halfedge
        he2 = he1.next
        he3 = he1.next.next

        v1 = he1.vertex
        v2 = he2.vertex
        v3 = he3.vertex

        r1 = orient2d((v1.x,v1.y),(v2.x,v2.y),(vertex.x,vertex.y))
        r2 = orient2d((v2.x,v2.y),(v3.x,v3.y),(vertex.x,vertex.y))
        r3 = orient2d((v3.x,v3.y),(v1.x,v1.y),(vertex.x,vertex.y))
        #if r1 < 1e-12 and r1 > -1e-12:
            #print(r1,r2,r3)
        #if r2 < 1e-12 and r2 > -1e-12:
            #print(r1,r2,r3)
        #if r3 < 1e-12 and r3 > -1e-12:
            #print(r1,r2,r3)

        # If all are the same sign, we are in the triangle
        if (r1 > 0 and r2 > 0 and r3 > 0) or (r1 < 0 and r2 < 0 and r3 < 0):
            return True
        elif ((r1 == 0 and on_segment(v1,v2,vertex)) 
              or (r2 == 0 and on_segment(v2,v3,vertex)) 
              or (r3 == 0 and on_segment(v3,v1,vertex))):
            return -1
        else:
            return False
    def __str__(self):
        return f"Face({self.index}, halfedge={self.halfedge})"

class Halfedge:
    def __init__(self, next=None, opposite=None, vertex=None,
                 face=None, index=None):
        self.opposite = opposite
        self.next = next
        self.vertex = vertex
        self.face = face
        self.index = index
        self.visited = False
    
    def __str__(self):
        next_idx = self.next.index if self.next else None
        opp_idx = self.opposite.index if self.opposite else None
        vert_idx = self.vertex.index if self.vertex else None
        return (f"Halfedge({self.index}): vertex={vert_idx}, "
                f"next={next_idx}, opposite={opp_idx}")

