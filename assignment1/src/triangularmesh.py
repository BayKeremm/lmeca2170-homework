from proj_utils import color
from halfedge import *
from geompreds import incircle
class TriangularMesh:
    #def __str__(self):
        #return f"TriangularMesh(\n\tvertices={[str(v) for v in self.vertices]},\n\n \tfaces={[str(face) for face in self.faces]},\n\n \thalfedges={[str(he) for he in self.halfedges]})"
    def set_printer(self,p):
        self.printer = p 
    def set_convex_hull_edges(self, halfedges):
        self.convexhalfedges = halfedges
    def __init__(self, vertices, halfedges, triangles):
        self.vertices = vertices
        self.faces = []
        self.halfedges = halfedges
        self.convexhullvertices = []

        j = 0
        for t in triangles:
            f = Face(j,t[0])
            self.faces.append(f)
            t[0].face = f
            t[1].face = f
            t[2].face = f
            j +=1
    def compute_convex_hull(self):
        x_sorted = sorted(self.vertices, key=lambda v: v.x)

        L_upper = []
        L_upper.append(x_sorted[0])
        L_upper.append(x_sorted[1])

        for i in range(2,len(self.vertices)):
            L_upper.append(x_sorted[i])
            while len(L_upper) > 2 and orient2d(L_upper[-3].as_tuple(),L_upper[-2].as_tuple(),L_upper[-1].as_tuple()) >0:
                L_upper.remove(L_upper[-2])
        L_lower = []
        L_lower.append(x_sorted[-1])
        L_lower.append(x_sorted[-2])

        for j in reversed(range(0,len(self.vertices)-2)):
            L_lower.append(x_sorted[j])
            while len(L_lower) > 2 and orient2d(L_lower[-3].as_tuple(),L_lower[-2].as_tuple(),L_lower[-1].as_tuple()) >0:
                L_lower.remove(L_lower[-2])
        
        L_lower.remove(L_lower[0])
        L_lower.remove(L_lower[-1])
        #print(color.YELLOW)
        #print([str(v) for v in L_upper])
        #print([str(v) for v in L_lower])
        #print(color.END)

        self.convexhullvertices = L_upper + L_lower
    def edge_flip(self, he):
        v_1 = he.vertex  # This is the starting vertex of he
        v_2 = he.next.vertex  # The next vertex in he's triangle
        v_3 = he.next.next.vertex  # The last vertex in he's triangle

        v_4 = he.opposite.vertex  # The starting vertex of he.opposite
        v_5 = he.opposite.next.vertex  # The next vertex in he.opposite's triangle
        v_6 = he.opposite.next.next.vertex  # The last vertex in he.opposite's triangle

        # Ensure this is a valid edge for flipping: v2 == v4 and v1 == v5
        assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for edge_flip"

        # Check Delaunay condition using incircle test (commented res1 as it was unused)
        #res1 = incircle(v_1.as_tuple(), v_2.as_tuple(), v_3.as_tuple(), v_6.as_tuple())
        res2 = incircle(v_1.as_tuple(), v_2.as_tuple(), v_6.as_tuple(), v_3.as_tuple())

        if res2 > 0:
            # Step 1: Cache the `next` pointers before modifying them
            he_next = he.next
            he_next_next = he.next.next
            op_he_next = he.opposite.next
            op_he_next_next = he.opposite.next.next

            # Step 2: Reassign vertices for the halfedges
            he.vertex = v_6
            he.opposite.vertex = v_3

            # Step 3: Update the `next` pointers to reflect the new edge structure
            # Triangle 1 (around he)
            he.next = he_next_next  
            he.next.next = op_he_next  
            he.next.next.next = he

            # Triangle 2 (around he.opposite)
            he.opposite.next = op_he_next_next  
            he.opposite.next.next = he_next  
            he.opposite.next.next.next = he.opposite

            # Step 4: Update faces
            self.faces.remove(he.face)
            self.faces.remove(he.opposite.face)
            f1 = Face(len(self.faces),he)
            self.faces.append(f1)
            he.face = f1
            f2 = Face(len(self.faces),he.opposite)
            self.faces.append(f2)
            he.opposite.face = f2
            he.next.face = he.face
            he.next.next.face = he.face
            he.opposite.next.face = he.opposite.face
            he.opposite.next.next.face = he.opposite.face

            return True

        return False

    def legalize_edge(self, pr, he):
        if he in self.convexhalfedges:
            return 
        if he.opposite == None:
            return
        he_next = he.next
        he_next_next = he.next
        if self.edge_flip(he):
            self.legalize_edge(pr, he_next) 
            self.legalize_edge(pr, he_next_next) 

    def triangulate(self):
        to_triangulate = self.vertices[:-4]
        # Since last 4 we have manually triangulated
        for vertex in to_triangulate:
            for face in self.faces:
                res = face.inside(vertex)
                if res == True:
                    # inside the triangle
                    #STEP 1: draw edges from 3 corners to the new point

                    he = face.halfedge
                    init_he_next = he.next
                    init_he_next_next = he.next.next
                    he1 = Halfedge(vertex=(he.next.vertex),index=len(self.halfedges))
                    self.halfedges.append(he1)

                    he2 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                    self.halfedges.append(he2)

                    he3 = Halfedge(vertex=(he.vertex),index=len(self.halfedges))
                    self.halfedges.append(he3)

                    he4 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                    self.halfedges.append(he4)

                    he5 = Halfedge(vertex=(he.next.next.vertex),index=len(self.halfedges))
                    self.halfedges.append(he5)

                    he6 = Halfedge(vertex=(vertex),index=len(self.halfedges))
                    self.halfedges.append(he6)

                    # Remove the face we are going to destroy now
                    self.faces.remove(face)
                    # link the halfedges and create the triangles
                    #   1
                    he.next = he1
                    he1.next = he2
                    he2.next = he
                    # This now created a new face
                    f1 = Face(len(self.faces),he)
                    self.faces.append(f1)
                    he.face = f1
                    he1.face = f1
                    he2.face = f1

                    #   2
                    init_he_next.next = he5
                    he5.next = he6
                    he6.next = init_he_next
                    f2 = Face(len(self.faces),init_he_next)
                    self.faces.append(f2)
                    init_he_next.face = f2
                    he5.face = f2
                    he6.face = f2
                    
                    #   3
                    init_he_next_next.next = he3
                    he3.next = he4
                    he4.next = init_he_next_next
                    f3 = Face(len(self.faces),init_he_next_next)
                    self.faces.append(f3)
                    init_he_next_next.face = f3
                    he3.face = f3
                    he4.face = f3
                    
                    # set the opposites
                    he1.opposite = he6
                    he6.opposite = he1
                    he2.opposite = he3
                    he3.opposite = he2
                    he4.opposite = he5
                    he5.opposite = he4

                    #self.printer.print_mesh("After adding new edges")
                    self.legalize_edge(vertex, he)
                    self.legalize_edge(vertex,init_he_next)
                    self.legalize_edge(vertex,init_he_next_next)
                    #self.printer.print_mesh("After legalizing")


                elif res == -1:
                    # on the triangle
                    print("AAAAAAAAAAAAAAAAAAAAAAA")
                    pass
    def resethalfedges(self):
        for he in self.halfedges:
            he.visited = False
