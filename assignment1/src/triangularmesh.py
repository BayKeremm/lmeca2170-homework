from proj_utils import color
from halfedge import *
from geompreds import incircle
import matplotlib.pyplot as plt
import numpy as np
class TriangularMesh:
    def __init__(self, vertices, halfedges, triangles,debug):
        self.vertices = vertices
        self.faces = []
        self.halfedges = halfedges
        self.convexhullvertices = []
        self.debug = debug

        j = 0
        for t in triangles:
            f = Face(j,t[0])
            self.faces.append(f)
            t[0].face = f
            t[1].face = f
            t[2].face = f
            j +=1
    def export(self,file):
        tris = []
        for face in self.faces:
            v1,v2,v3 = face.halfedge.vertex, face.halfedge.next.vertex, face.halfedge.next.next.vertex
            tris.append([v1.as_tuple(),v2.as_tuple(), v3.as_tuple()])
        for tri in tris:
            triangle = [f"({pt[0]}, {pt[1]})" for pt in tri]
            # Write the triangle to the output file
            file.write(" ".join(triangle) + "\n")

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

        self.convexhullvertices = L_upper + L_lower
    def handle_boundaries(self, boundary_hes, boundary_vs):
        for he in boundary_hes:
            self.faces.remove(he.face)
            self.halfedges.remove(he)
            self.halfedges.remove(he.next)
            if he.next.opposite is not None:
                he.next.opposite.opposite = None
            self.halfedges.remove(he.next.next)
            if he.next.next.opposite is not None:
                he.next.next.opposite.opposite = None
        
        to_remove = []
        for he in self.halfedges:
            if he.vertex in boundary_vs:
                to_remove.append(he)

        for he in to_remove:
            if he.opposite is not None:
                self.special_flip(he, boundary_vs)

        if self.debug:
            self.print_mesh("After special flip")


        to_remove = []
        for he in self.halfedges:
            if he.vertex in boundary_vs:
                to_remove.append(he)
                to_remove.append(he.next)
                to_remove.append(he.next.next)
                self.faces.remove(he.face)

        # Now remove them
        for he in to_remove:
            if he in self.halfedges:
                self.halfedges.remove(he)

        for v in boundary_vs:
            self.vertices.remove(v)

    def special_flip(self, he, boundary_vertices):
        """
            We are actually not flipping anything!!!!!!!!
            were we fooled ? 
        """
        v_1 = he.vertex  
        v_2 = he.next.vertex  
        v_3 = he.next.next.vertex 

        v_4 = he.opposite.vertex 
        v_5 = he.opposite.next.vertex 
        v_6 = he.opposite.next.next.vertex 

        assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for special_flip"
        
        assert v_1 in boundary_vertices, "v_1 not correct"

        # If v_3 v_2 v_6 make a left hand turn flip
        res = orient2d(v_3.as_tuple(), v_2.as_tuple(), v_6.as_tuple())

        if res > 0:
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

    def edge_flip(self, he, pr):
        v_1 = he.vertex  # This is the starting vertex of he
        v_2 = he.next.vertex  # The next vertex in he's triangle
        v_3 = he.next.next.vertex  # The last vertex in he's triangle

        v_4 = he.opposite.vertex  # The starting vertex of he.opposite
        v_5 = he.opposite.next.vertex  # The next vertex in he.opposite's triangle
        v_6 = he.opposite.next.next.vertex  # The last vertex in he.opposite's triangle

        # Ensure this is a valid edge for flipping: v2 == v4 and v1 == v5
        assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for edge_flip"

        assert pr != v_6, "WARNING: pr =! v_6"
        res = incircle(v_1.as_tuple(), v_2.as_tuple(), v_6.as_tuple(), v_3.as_tuple())

        if res >= 0 :
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
        if he.opposite == None:
            return
        he_next = he.next
        he_next_next = he.next.next
        op = he.opposite
        op_n = he.opposite.next
        op_nn = he.opposite.next.next
        if self.edge_flip(he, pr):
            self.legalize_edge(pr, he_next) 
            self.legalize_edge(pr, he_next_next) 
            self.legalize_edge(pr, op) 
            self.legalize_edge(pr, op_n) 
            self.legalize_edge(pr, op_nn) 

    def print_tris(self):
        for face in self.faces:
            v1,v2,v3 = face.halfedge.vertex, face.halfedge.next.vertex, face.halfedge.next.next.vertex
            print([v1.index,v2.index, v3.index])
    def triangulate(self):
        to_triangulate = self.vertices[:-4]
        # Since last 4 we have manually triangulated
        for vertex in to_triangulate:
            for face in self.faces:
                res = face.inside(vertex)
                if res == True:
                    #print("Inside triangle")
                    # inside the triangle
                    #STEP 1: draw edges from 3 corners to the new point

                    he = face.halfedge
                    init_he_next = he.next
                    init_he_next_next = init_he_next.next
                    assert init_he_next_next.next == he, print("Not a triangle homie")
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

                    #self.print_mesh("Before legalizing he")
                    self.legalize_edge(vertex, he)
                    #self.print_mesh("Before legalizing init_he_next", highlight=init_he_next)
                    self.legalize_edge(vertex,init_he_next)
                    #self.print_mesh("Before legalizing he next next ", highlight=init_he_next_next)
                    self.legalize_edge(vertex,init_he_next_next)
                    #self.print_mesh("After legalizing")
                    #print("Len faces after in triangle: ", len(self.faces))
                    #self.print_tris()
                    break


                elif res == -1:
                    # on the triangle
                    print("AAAAAAAAAAAAAAAAAAAAAAA")
                    he1 = face.halfedge
                    he2 = he1.next 
                    he3 = he2.next 

                    v1 = he1.vertex
                    v2 = he2.vertex
                    v3 = he3.vertex


                    r1 = orient2d((v1.x,v1.y),(v2.x,v2.y),(vertex.x,vertex.y))
                    r2 = orient2d((v2.x,v2.y),(v3.x,v3.y),(vertex.x,vertex.y))
                    r3 = orient2d((v3.x,v3.y),(v1.x,v1.y),(vertex.x,vertex.y))
                    #print("r1: ", v1.index, v2.index , r1)
                    #print("r2: ", v2.index, v3.index, r2)
                    #print("r3: ", v3.index, v1.index, r3)
                    edge = None
                    if r1 == 0:
                        edge = he1
                    elif r2 == 0:
                        edge = he2
                    elif r3 == 0:
                        edge = he3
                    
                    #print("point is on edge: ", edge.vertex.index, edge.opposite.vertex.index)

                    # store initials
                    edge_opp = edge.opposite
                    edge_opp_n = edge.opposite.next
                    edge_opp_nn = edge.opposite.next.next

                    edge_n = edge.next
                    edge_nn = edge.next.next

                    # remove 2 triangles which are going to turn into 4 triangles
                    self.faces.remove(face)
                    self.faces.remove(edge_opp.face)

                    # check triangles and get diagonal points we are going to connect 

                    p_1 = edge.next.next.vertex 
                    p_2 = edge_opp.next.next.vertex 

                    assert edge.next.next.next == edge and edge_opp.next.next.next == edge_opp, print("Not a triangle, kendine gel")

                    # create the new halfedges for the new triangles
                    
                    v_to_p1 = Halfedge(len(self.halfedges), vertex=vertex)
                    v_to_p2 = Halfedge(len(self.halfedges) + 1, vertex=vertex)

                    p1_to_v = Halfedge(len(self.halfedges) + 2, vertex=p_1)
                    p2_to_v = Halfedge(len(self.halfedges) + 3, vertex=p_2)

                    v_to_ver_edge = Halfedge(len(self.halfedges) + 4, vertex=vertex)
                    v_to_ver_edge_opp = Halfedge(len(self.halfedges) + 5, vertex=vertex)

                    
                    self.halfedges.extend([v_to_ver_edge_opp, v_to_ver_edge, p2_to_v, p1_to_v, v_to_p1, v_to_p2])

                     
                    # set up faces
                    # face 1
                    face_1 = Face(index=len(self.faces), halfedge=edge)
                    edge.next = v_to_p1
                    edge.next.next = edge_nn
                    edge.next.next.next = edge

                    edge.opposite = v_to_ver_edge
                    v_to_ver_edge.opposite = edge

                    v_to_p1.opposite = p1_to_v
                    p1_to_v.opposite = v_to_p1

                    edge.face = face_1
                    edge.next.face = face_1
                    edge.next.next.face = face_1

                    # face 2
                    face_2 = Face(index=len(self.faces)+1, halfedge=v_to_ver_edge_opp)
                    v_to_ver_edge_opp.next = edge_n
                    v_to_ver_edge_opp.next.next = p1_to_v
                    v_to_ver_edge_opp.next.next.next = v_to_ver_edge_opp

                    v_to_ver_edge_opp.opposite = edge_opp
                    edge_opp.opposite = v_to_ver_edge_opp

                    v_to_ver_edge_opp.face = face_2
                    v_to_ver_edge_opp.next.face = face_2
                    v_to_ver_edge_opp.next.next.face = face_2

                    # face 3
                    face_3 = Face(index=len(self.faces)+2, halfedge=edge_opp)
                    edge_opp.next = v_to_p2
                    edge_opp.next.next = edge_opp_nn
                    edge_opp.next.next.next = edge_opp

                    v_to_p2.opposite = p2_to_v
                    p2_to_v.opposite = v_to_p2

                    
                    edge_opp.face = face_3
                    edge_opp.next.face = face_3
                    edge_opp.next.next.face = face_3

                    # face 4
                    face_4 = Face(index=len(self.faces)+3, halfedge=v_to_ver_edge)
                    v_to_ver_edge.next = edge_opp_n
                    v_to_ver_edge.next.next = p2_to_v
                    v_to_ver_edge.next.next.next = v_to_ver_edge

                    v_to_ver_edge.face = face_4
                    v_to_ver_edge.next.face = face_4
                    v_to_ver_edge.next.next.face = face_4

                    self.faces.extend([face_1, face_2, face_3, face_4])

                    
                    #print("------------------")
                    #print("before legalize")
                    #self.print_tris()
                    self.legalize_edge(vertex, edge_n)
                    self.legalize_edge(vertex, edge_nn)
                    self.legalize_edge(vertex, edge_opp_n)
                    self.legalize_edge(vertex, edge_opp_nn)
                    #print("after legalize")
                    #self.print_tris()
                    #print("------------------")
                    #self.print_mesh("Hmm")
                    
                    break
    def resethalfedges(self):
        for he in self.halfedges:
            he.visited = False
    def plot_convexhull(self):
        if len(self.convexhullvertices) == 0:
            return 
        # Plotting the original points and the convex hull
        plt.figure()
        # Original points
        plt.plot([v.x for v in self.vertices], [v.y for v in self.vertices], 'o', label='Points')

        # Convex hull
        hull_x = [v.x for v in self.convexhullvertices] + [self.convexhullvertices[0].x]  # closing the polygon
        hull_y = [v.y for v in self.convexhullvertices] + [self.convexhullvertices[0].y]  # closing the polygon
        plt.plot(hull_x, hull_y, 'r-', label='Convex Hull')

        plt.title("Convex Hull")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.gca().set_aspect('equal', adjustable='box')
        plt.legend()
        plt.show()

    def print_mesh(self, title="Fig", highlight=None):
        x = [v.x for v in self.vertices]
        y = [v.y for v in self.vertices]
        
        # Plot vertices
        plt.scatter(x, y, color='blue')
        for v in self.vertices:
            plt.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')

        # Plot faces and halfedges
        for face in self.faces:
            he = face.halfedge
            triangle_x = []
            triangle_y = []
            start_he = he

            while True:
                vertex = he.vertex
                next_vertex = he.next.vertex
                triangle_x.append(vertex.x)
                triangle_y.append(vertex.y)

                midpoint_x = (vertex.x + next_vertex.x) / 2
                midpoint_y = (vertex.y + next_vertex.y) / 2

                if he.visited:
                    he = he.next
                    if he == start_he:
                        break
                    continue

                if he.opposite is None:
                    pass
                    #plt.text(midpoint_x, midpoint_y, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='orange', ha='center')
                else:
                    he.opposite.visited = True
                    #plt.text(midpoint_x -0.2, midpoint_y -0.2, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='purple', ha='center')
                    #plt.text(midpoint_x , midpoint_y, f"he{he.opposite.index}\n→he{he.opposite.next.index}",
                            #fontsize=8, color='purple', ha='center')

                he.visited = True



                he = he.next
                if he == start_he:
                    break

            # Close the triangle by adding the first point again
            triangle_x.append(triangle_x[0])
            triangle_y.append(triangle_y[0])
            plt.plot(triangle_x, triangle_y, color='black')

        # Plot configuration
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(title)
        plt.grid(True)
        plt.show()
        self.resethalfedges()
    def print_boundary(self):
        x = [v.x for v in self.vertices]
        y = [v.y for v in self.vertices]
        
        # Plot vertices
        plt.scatter(x, y, color='blue')
        for v in self.vertices:
            plt.text(v.x, v.y, str(v.index), fontsize=12, color='red', ha='center', va='center')

        # Plot faces and halfedges
        for face in self.faces:
            he = face.halfedge
            triangle_x = []
            triangle_y = []
            start_he = he

            while True:
                vertex = he.vertex
                next_vertex = he.next.vertex
                triangle_x.append(vertex.x)
                triangle_y.append(vertex.y)

                midpoint_x = (vertex.x + next_vertex.x) / 2
                midpoint_y = (vertex.y + next_vertex.y) / 2

                if he.visited:
                    he = he.next
                    if he == start_he:
                        break
                    continue

                if he.opposite is None:
                    pass
                    #plt.text(midpoint_x, midpoint_y, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='orange', ha='center')
                else:
                    he.opposite.visited = True
                    #plt.text(midpoint_x -0.2, midpoint_y -0.2, f"he{he.index}\n→he{he.next.index}",
                            #fontsize=8, color='purple', ha='center')
                    #plt.text(midpoint_x , midpoint_y, f"he{he.opposite.index}\n→he{he.opposite.next.index}",
                            #fontsize=8, color='purple', ha='center')

                he.visited = True



                he = he.next
                if he == start_he:
                    break

            # Close the triangle by adding the first point again
            triangle_x.append(triangle_x[0])
            triangle_y.append(triangle_y[0])
            plt.plot(triangle_x, triangle_y, color='black')

        to_plot = []
        for he in self.halfedges:
            if he.opposite is None:
                to_plot.append(he)
        
        xs = [h.vertex.x for h in to_plot]
        ys = [h.vertex.y for h in to_plot]

        plt.scatter(xs, ys, color='orange')

        plt.title("Boundary")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()





    #def mandatory_edge_flip(self, he):
        #if he.opposite == None:
            #he_up = he.next
        #else:
            #he_up = he
        #v_1 = he_up.vertex  # This is the_up starting vertex of he_up
        #v_2 = he_up.next.vertex  # The_up next vertex in he_up's triangle
        #v_3 = he_up.next.next.vertex  # The_up last vertex in he_up's triangle

        #v_4 = he_up.opposite.vertex  # The_up starting vertex of he_up.opposite
        #v_5 = he_up.opposite.next.vertex  # The_up next vertex in he_up.opposite's triangle
        #v_6 = he_up.opposite.next.next.vertex  # The_up last vertex in he_up.opposite's triangle

        ## Ensure this is a valid edge for flipping: v2 == v4 and v1 == v5
        #assert (v_2 == v_4 and v_1 == v_5), "WARNING: Not a valid edge for edge_flip"

        ## Che_upck Delaunay condition using incircle test (commented res1 as it was unused)
        ##res1 = incircle(v_1.as_tuple(), v_2.as_tuple(), v_3.as_tuple(), v_6.as_tuple())

        ## Step 1: Cache_up the_up `next` pointers before modifying the_upm
        #he_up_next = he_up.next
        #he_up_next_next = he_up.next.next
        #op_he_up_next = he_up.opposite.next
        #op_he_up_next_next = he_up.opposite.next.next

        ## Step 2: Reassign vertices for the_up halfedges
        #he_up.vertex = v_6
        #he_up.opposite.vertex = v_3

        ## Step 3: Update the_up `next` pointers to reflect the_up new edge structure
        ## Triangle 1 (around he_up)
        #he_up.next = he_up_next_next  
        #he_up.next.next = op_he_up_next  
        #he_up.next.next.next = he_up

        ## Triangle 2 (around he_up.opposite)
        #he_up.opposite.next = op_he_up_next_next  
        #he_up.opposite.next.next = he_up_next  
        #he_up.opposite.next.next.next = he_up.opposite

        ## Step 4: Update faces
        #if he_up.face in self.faces:
            #self.faces.remove(he_up.face)
        #if he_up.opposite.face in self.faces:
            #self.faces.remove(he_up.opposite.face)
        #f1 = Face(len(self.faces),he_up)
        #self.faces.append(f1)
        #he_up.face = f1
        #f2 = Face(len(self.faces),he_up.opposite)
        #self.faces.append(f2)
        #he_up.opposite.face = f2
        #he_up.next.face = he_up.face
        #he_up.next.next.face = he_up.face
        #he_up.opposite.next.face = he_up.opposite.face
        #he_up.opposite.next.next.face = he_up.opposite.face
        """
        
                    # Add edges from vertex to opposites v_i v_j
                    v = edge.next.next.vertex
                    v_opp = edge.opposite.next.next.vertex

                    new_he1 = Halfedge(vertex=v )
                    new_he1_opp = Halfedge(vertex=vertex )

                    new_he2 = Halfedge(vertex=vertex )
                    new_he2_opp = Halfedge(vertex=v_opp)

                    edge_new = Halfedge(vertex=vertex)
                    edge_opp_new = Halfedge(vertex=vertex)

                    self.halfedges.extend([new_he1, new_he1_opp, new_he2, new_he2_opp, edge_new, edge_opp_new])

                    # split current 2 triangles into 4
                    # remove old faces
                    self.faces.remove(face)
                    self.faces.remove(edge.opposite.face)

                    # Store originals
                    edge_opp = edge.opposite
                    edge_next = edge.next
                    edge_next_next = edge.next.next

                    edge_opp_next = edge.opposite.next
                    edge_opp_next_next = edge.opposite.next.next
                    

                    # new faces
                    nf1 = Face(halfedge=edge)
                    nf2 = Face(halfedge=edge_new)

                    nf3 = Face(halfedge=edge_opp)
                    nf4 = Face(halfedge=edge_opp_new)

                    self.faces.extend([nf1,nf2,nf3,nf4])
                    # adjust halfedges
                    # f1
                    new_he1_opp.next = edge_next_next
                    new_he1_opp.next.next = edge
                    new_he1_opp.next.next.next = new_he1_opp

                    # f2
                    edge_new.next = edge_next
                    edge_new.next.next = new_he1
                    edge_new.next.next.next = edge_new

                    edge_new.next.next.opposite=new_he1_opp
                    new_he1_opp.opposite = edge_new.next.next


                    # f3
                    edge_opp.next = new_he2
                    edge_opp.next.next = edge_opp_next_next
                    edge_opp.next.next.next = edge_opp

                    edge_opp.next.opposite = new_he2_opp 
                    new_he2_opp.opposite = edge_opp.next

                    edge_new.opposite = edge_opp
                    edge_opp.opposite = edge_new
                    
                    # f4
                    edge_opp_new.next = edge_opp_next
                    edge_opp_new.next.next = new_he2_opp
                    edge_opp_new.next.next.next = edge_opp_new

                    edge_opp_new.opposite = edge
                    edge.opposite = edge_opp_new

                    # setup faces
                    edge.face = nf1
                    edge.next.face = nf1
                    edge.next.next.face = nf1

                    edge_new.face = nf2
                    edge_new.next.face = nf2
                    edge_new.next.next.face = nf2

                    edge_opp.face = nf3
                    edge_opp.next.face = nf3
                    edge_opp.next.next.face = nf3

                    edge_opp_new.face = nf4
                    edge_opp_new.next.face = nf4
                    edge_opp_new.next.next.face = nf4
                    
                    print("------------------")
                    print("before legalize")
                    self.print_tris()
                    self.legalize_edge(vertex, edge_opp_new.next)
                    self.legalize_edge(vertex,new_he2.next)
                    self.legalize_edge(vertex,edge_new.next)
                    self.legalize_edge(vertex,new_he1_opp.next)
                    print("after legalize")
                    self.print_tris()
                    print("------------------")
                    self.print_mesh("Hmm")
        
        
        """