from halfedge import *
from geompreds import incircle
class TriangularMesh:
    def __init__(self, vertices, halfedges, triangles):
        self.vertices = vertices
        self.faces = []
        self.halfedges = halfedges

        j = 0
        for t in triangles:
            f = Face(j,t[0])
            self.faces.append(f)
            t[0].face = f
            t[1].face = f
            t[2].face = f
            j +=1
    def __str__(self):
        return f"TriangularMesh(\n\tvertices={[str(v) for v in self.vertices]},\n\n \tfaces={[str(face) for face in self.faces]},\n\n \thalfedges={[str(he) for he in self.halfedges]})"
    def set_printer(self,p):
        self.printer = p 
    
    def edge_flip(self, he):
        # Get vertices of the two triangles sharing the edge (v1v4)
        v_1 = he.vertex
        v_2 = he.next.vertex
        v_3 = he.prev.vertex

        v_4 = he.opposite.vertex
        v_5 = he.opposite.next.vertex
        v_6 = he.opposite.prev.vertex

        # Ensure this is a valid edge for flipping indicent edge for 2 triangles
        assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for edge_flip"

        # Check Delaunay condition using incircle test
        res1 = incircle(v_1.as_tuple(), v_2.as_tuple(), v_3.as_tuple(), v_6.as_tuple())
        res2 = incircle(v_1.as_tuple(), v_2.as_tuple(), v_6.as_tuple(), v_3.as_tuple())

        if res1 > 0 or res2 > 0:
            he_next = he.next
            he_prev = he.prev
            opp_next = he.opposite.next
            opp_prev = he.opposite.prev

            he.vertex = v_3
            he.opposite.vertex = v_6

            he.next = opp_prev
            he.prev = he_next
            he.opposite.next = he_prev
            he.opposite.prev = opp_next

            he.next.next = he.prev
            he.next.prev = he
            he.prev.next = he
            he.prev.prev = he.next
            he.opposite.next.next = he.opposite.prev
            he.opposite.prev.next = he.opposite
            he.opposite.next.prev = he.opposite
            he.opposite.prev.prev = he.opposite.next

            he.next.face = he.face
            he.prev.face = he.face
            he.opposite.next.face = he.opposite.face
            he.opposite.prev.face = he.opposite.face
            self.printer.print_mesh("After edge flip")

            return True
        return False

    def legalize_edge(self, pr, he):
        if he == None:
            return
        if he.opposite == None:
            return
        he2 = he.next
        he3 = he.prev
        if self.edge_flip(he):
            self.legalize_edge(pr, he2)
            self.legalize_edge(pr, he3)

    def triangulate(self):
        to_triangulate = self.vertices[:-4]
        # Since last 4 we have manually triangulated
        for vertex in to_triangulate:
            # Now this vertex we need to find which triangle it is in
            for face in self.faces:
                res = face.inside(vertex)
                if res == True:
                    # inside the triangle
                    print(vertex.index ," is inside face: ", face)
                    he1 = face.halfedge
                    he2 = he1.next
                    he3 = he1.prev

                    assert (he1.face == he2.face and he3.face == he2.face and he1.face == he3.face), print("Faces do not mach in triangulate 1")

                    # Add edges from vertex to 3 corners of the triangle
                    #   part 1
                    he4 = Halfedge(vertex=vertex,index=len(self.halfedges))
                    self.halfedges.append(he4)
                    he5 = Halfedge(vertex=he2.vertex,index=len(self.halfedges))
                    self.halfedges.append(he5)
                    f1 = Face(len(self.faces),he1)
                    self.faces.remove(he1.face)
                    self.faces.append(f1)

                    # link halfedges
                    he1.next = he5
                    he1.prev = he4
                    he1.next.next = he4
                    he1.next.prev = he1
                    he1.prev.next = he1
                    he1.prev.prev = he5
                    # link the face
                    he1.face = f1
                    he4.face = f1
                    he5.face = f1

                    #assert (he1.face == he4.face and he1.face == he5.face and he4.face == he5.face), print("Faces do not mach in triangulate 2")
                    
                    
                    #   part 2
                    he6 = Halfedge(vertex=vertex,index=len(self.halfedges))
                    self.halfedges.append(he6)
                    he7 = Halfedge(vertex=he3.vertex,index=len(self.halfedges))
                    self.halfedges.append(he7)
                    f2 = Face(len(self.faces),he2)
                    self.faces.append(f2)

                    # link halfedges
                    he2.next = he7
                    he2.prev = he6
                    he2.next.next = he6
                    he2.next.prev = he2
                    he2.prev.prev = he7
                    he2.prev.next = he2
                    # link the face
                    he2.face = f2
                    he6.face = f2
                    he7.face = f2

                    #   part 3
                    he8 = Halfedge(vertex=vertex,index=len(self.halfedges))
                    self.halfedges.append(he8)
                    he9 = Halfedge(vertex=he1.vertex,index=len(self.halfedges))
                    self.halfedges.append(he9)
                    f3 = Face(len(self.faces),he3)
                    self.faces.append(f3)

                    # link halfedges
                    he3.next = he9
                    he3.prev = he8
                    he3.next.next = he8
                    he3.next.prev = he3
                    he3.prev.prev = he9
                    he3.prev.next = he3
                    # link the face
                    he3.face = f3
                    he8.face = f3
                    he9.face = f3

                    # link the opposites
                    he4.opposite = he9
                    he9.opposite = he4
                    he5.opposite = he6
                    he6.opposite = he5
                    he8.opposite = he7
                    he7.opposite = he8


                    self.printer.print_mesh("Before legalize")
                    self.legalize_edge(vertex,he1)
                    self.legalize_edge(vertex,he2)
                    self.legalize_edge(vertex,he3)
                    self.printer.print_mesh("after legalize")



                elif res == -1:
                    # on the triangle
                    pass
                



        """
            Perform an edge flip on two triangles that share the edge incident to the given halfedge (he) if the given edge is illegal

            Note:
            The edge flip is done to restore the Delaunay condition:
                - Let edge pi-pj be incident to triangles pi-pj-pk and pi-pj-pl
                - Let C be the cirlce through pi-pj-pk
                The edge pi-pj is illegal if and only if the point pl lies in the interior of C

                Furthermore, if the points pi,pj,pk,pl form a convex quadrilateral 
                and do not lie on a common circle, then exactly one of the pi-pj and pk-pl is illegal
            
        """